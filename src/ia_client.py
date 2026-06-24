"""Cliente de IA — integração com a API do Google Gemini.

Responsável por enviar prompts ao modelo e devolver as aventuras geradas já
estruturadas (dicionários prontos para virar JSON). Esta é a única camada que
conhece detalhes do provedor de IA; o restante da aplicação fala apenas com a
interface pública definida aqui.
"""

from __future__ import annotations

import time

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from src.config import Settings
from src.prompts import ADVENTURE_PROMPT_TEMPLATE, SYSTEM_PROMPT
from src.schemas.dnd5e import Adventure

# Tentativas extras quando a API responde com erro transitório (5xx / sobrecarga).
_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = 2.0


class IAClientError(RuntimeError):
    """Falha ao gerar a aventura (erro de rede, da API ou de parse da resposta)."""


class IAClient:
    """Encapsula a comunicação com o modelo Gemini."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = genai.Client(api_key=settings.gemini_api_key)

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
            IAClientError: se a chamada à API ou o parse da resposta falhar.
        """
        prompt = ADVENTURE_PROMPT_TEMPLATE.format(
            idea=idea, tom=tom, nivel=nivel, duracao=duracao
        )
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=Adventure,
        )

        response = self._generate_with_retry(prompt, config)
        adventure = response.parsed
        if adventure is None:
            # Fallback: alguns retornos trazem só o texto JSON.
            try:
                adventure = Adventure.model_validate_json(response.text or "")
            except Exception as exc:  # noqa: BLE001
                raise IAClientError(
                    "A resposta da IA veio em um formato inesperado. Tente novamente."
                ) from exc

        return adventure.model_dump()

    def _generate_with_retry(self, prompt: str, config: types.GenerateContentConfig):
        """Chama a API com retry/backoff para erros transitórios (5xx/sobrecarga).

        Erros de cliente (4xx, ex.: chave inválida) não são repetidos.
        """
        last_exc: Exception | None = None
        for attempt in range(_MAX_ATTEMPTS):
            try:
                return self._client.models.generate_content(
                    model=self._settings.gemini_model,
                    contents=prompt,
                    config=config,
                )
            except genai_errors.ServerError as exc:
                # Transitório (ex.: 503 UNAVAILABLE): aguarda e tenta de novo.
                last_exc = exc
                if attempt < _MAX_ATTEMPTS - 1:
                    time.sleep(_BACKOFF_SECONDS * (attempt + 1))
            except Exception as exc:  # noqa: BLE001 — qualquer outro erro do SDK
                raise IAClientError(
                    "Não foi possível gerar a aventura. Verifique sua conexão e a "
                    "chave da API, e tente novamente."
                ) from exc

        raise IAClientError(
            "O serviço de IA está temporariamente sobrecarregado. "
            "Tente novamente em alguns instantes."
        ) from last_exc
