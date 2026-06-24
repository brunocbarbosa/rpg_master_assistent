"""Carregamento de configuração e variáveis de ambiente.

Lê o arquivo `.env` (via python-dotenv) e expõe as configurações da aplicação.
Mantém os segredos (chaves de API) fora do código-fonte.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Configurações da aplicação carregadas do ambiente."""

    gemini_api_key: str
    gemini_model: str


def load_settings() -> Settings:
    """Carrega as variáveis do `.env` e retorna um objeto ``Settings``.

    TODO (Fase 1 funcional): validar a presença de ``GEMINI_API_KEY`` e
    levantar um erro claro quando ausente, antes de qualquer chamada à IA.
    """
    load_dotenv()

    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
    )
