"""Carregamento de configuração e variáveis de ambiente.

Lê o arquivo `.env` (via python-dotenv) e expõe as configurações da aplicação.
Mantém os segredos (chaves de API) fora do código-fonte.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


class ConfigError(RuntimeError):
    """Erro de configuração (ex.: variável de ambiente obrigatória ausente)."""


@dataclass(frozen=True)
class Settings:
    """Configurações da aplicação carregadas do ambiente."""

    gemini_api_key: str
    gemini_model: str


def load_settings() -> Settings:
    """Carrega as variáveis do `.env` e retorna um objeto ``Settings``.

    Raises:
        ConfigError: se ``GEMINI_API_KEY`` não estiver definida.
    """
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ConfigError(
            "GEMINI_API_KEY não encontrada. Copie .env.example para .env e "
            "preencha a sua chave da API do Google Gemini."
        )

    return Settings(
        gemini_api_key=api_key,
        gemini_model=os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL),
    )
