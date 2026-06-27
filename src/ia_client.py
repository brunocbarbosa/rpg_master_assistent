"""Cliente de IA — integração com o Mistral via Ollama (local).

Responsável por enviar prompts ao modelo e devolver as aventuras geradas já
estruturadas (dicionários prontos para virar JSON). Esta é a única camada que
conhece detalhes do provedor de IA; o restante da aplicação fala apenas com a
interface pública definida aqui.
"""

from __future__ import annotations

import time

import httpx
import ollama

from src.config import Settings
from src.prompts import (
    ADVENTURE_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
    format_rules_context,
)
from src.rag.retrieve import Retriever
from src.schemas.dnd5e import Adventure

# Tentativas extras quando o servidor responde com erro transitório
# (5xx / modelo ainda carregando).
_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = 2.0

# Timeouts (segundos): conexão curta para falhar rápido se o Ollama estiver
# inacessível; leitura longa porque a geração do LLM pode demorar (CPU/modelo
# grande). Sem isso, um host inacessível trava o app indefinidamente.
_TIMEOUT = httpx.Timeout(connect=5.0, read=600.0, write=10.0, pool=5.0)

# Erros de transporte: servidor inacessível (desligado, host/porta errados, sem
# rota, timeout) ou URL malformada (ex.: esquema inválido no OLLAMA_HOST).
# Não adianta repetir — falha imediata com orientação. ``httpx.RequestError``
# cobre ConnectError/ConnectTimeout/ReadTimeout/UnsupportedProtocol etc.
_CONNECTION_ERRORS = (
    ConnectionError,
    httpx.RequestError,
    httpx.InvalidURL,
    ollama.RequestError,
)


class IAClientError(RuntimeError):
    """Falha ao gerar a aventura (erro de rede, do servidor ou de parse da resposta)."""


class IAClient:
    """Encapsula a comunicação com o modelo Mistral servido pelo Ollama."""

    def __init__(self, settings: Settings, retriever: Retriever | None = None) -> None:
        self._settings = settings
        self._client = ollama.Client(host=settings.ollama_host, timeout=_TIMEOUT)
        self._retriever = retriever or Retriever(settings)

    def generate_adventure(
        self, idea: str, tom: str, nivel: str, duracao: str
    ) -> dict:
        """Gera uma aventura de D&D 5e a partir dos parâmetros do mestre.

        Args:
            idea: Ideia central informada pelo mestre (texto livre, pt-BR).
            tom: Tom desejado (ex.: "Sombrio").
            nivel: Faixa de nível dos personagens (ex.: "1–4").
            duracao: Duração pretendida (ex.: "One-shot (1 sessão)").

        Returns:
            Dicionário estruturado seguindo o Funil Narrativo e os 3 atos
            (ver ``src/schemas/dnd5e.py``).

        Raises:
            IAClientError: se a chamada ao Ollama ou o parse da resposta falhar.
        """
        # RAG (best-effort): recupera regras relevantes e injeta como contexto.
        query = f"{idea}\nTom: {tom}\nNível: {nivel}"
        contexto = format_rules_context(self._retriever.retrieve(query))
        prompt = ADVENTURE_PROMPT_TEMPLATE.format(
            idea=idea, tom=tom, nivel=nivel, duracao=duracao, contexto=contexto
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        response = self._chat_with_retry(messages)

        content = response.message.content or ""
        try:
            adventure = Adventure.model_validate_json(content)
        except Exception as exc:  # noqa: BLE001
            raise IAClientError(
                "A resposta da IA veio em um formato inesperado. Tente novamente."
            ) from exc

        return adventure.model_dump()

    def _chat_with_retry(self, messages: list[dict]):
        """Chama o Ollama com retry/backoff para erros transitórios (5xx/sobrecarga).

        Erros de conexão (servidor desligado / host errado) falham de imediato.
        """
        last_exc: Exception | None = None
        for attempt in range(_MAX_ATTEMPTS):
            try:
                return self._client.chat(
                    model=self._settings.ollama_model,
                    messages=messages,
                    format=Adventure.model_json_schema(),
                )
            except ollama.ResponseError as exc:
                status = getattr(exc, "status_code", None)
                # Transitório (5xx, ex.: modelo carregando): aguarda e tenta de novo.
                if status is not None and status >= 500:
                    last_exc = exc
                    if attempt < _MAX_ATTEMPTS - 1:
                        time.sleep(_BACKOFF_SECONDS * (attempt + 1))
                    continue
                # Erros de cliente (4xx, ex.: modelo inexistente) não são repetidos.
                raise IAClientError(
                    "Não foi possível gerar a aventura. Verifique se o modelo "
                    f"'{self._settings.ollama_model}' está instalado no Ollama "
                    "(ollama pull) e tente novamente."
                ) from exc
            except _CONNECTION_ERRORS as exc:
                raise IAClientError(
                    "Não foi possível conectar ao Ollama. Verifique se ele está "
                    f"rodando e se OLLAMA_HOST ('{self._settings.ollama_host}') "
                    "aponta para o servidor correto."
                ) from exc
            except Exception as exc:  # noqa: BLE001 — qualquer outro erro do SDK
                raise IAClientError(
                    "Não foi possível gerar a aventura. Tente novamente."
                ) from exc

        raise IAClientError(
            "O serviço de IA está temporariamente sobrecarregado. "
            "Tente novamente em alguns instantes."
        ) from last_exc
