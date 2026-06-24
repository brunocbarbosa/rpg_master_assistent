"""Cliente de IA — integração com a API do Google Gemini.

Responsável por enviar prompts ao modelo e devolver as aventuras geradas já
estruturadas (dicionários prontos para virar JSON). Esta é a única camada que
conhece detalhes do provedor de IA; o restante da aplicação fala apenas com a
interface pública definida aqui.

NOTA: este módulo é um ESQUELETO. As chamadas reais à API ainda não foram
implementadas (Fase 1 funcional).
"""

from __future__ import annotations

from src.config import Settings


class IAClient:
    """Encapsula a comunicação com o modelo Gemini."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        # TODO: configurar o SDK google-genai com a API key e instanciar o
        # cliente (from google import genai; genai.Client(api_key=...)).

    def generate_adventure(self, idea: str) -> dict:
        """Gera uma aventura de D&D 5e a partir da ideia central do mestre.

        Args:
            idea: Ideia central informada pelo mestre (texto livre, pt-BR).

        Returns:
            Dicionário estruturado seguindo o Funil Narrativo e os 3 atos
            (ver ``src/schemas/dnd5e.py``).

        TODO (Fase 1 funcional):
            1. Montar o prompt combinando o System Prompt (``src/prompts.py``)
               com a ideia do mestre.
            2. Chamar o modelo Gemini solicitando saída em JSON.
            3. Fazer o parse/validação da resposta e retornar o dicionário.
        """
        raise NotImplementedError("Geração de aventura ainda não implementada.")
