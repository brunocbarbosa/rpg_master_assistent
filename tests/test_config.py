"""Testes de carregamento de configuração (src/config.py)."""

from __future__ import annotations

import pytest

from src.config import ConfigError, DEFAULT_GEMINI_MODEL, load_settings


def test_load_settings_raises_without_key(monkeypatch):
    # Var presente porém vazia: load_dotenv (override=False) não sobrescreve.
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(ConfigError):
        load_settings()


def test_load_settings_returns_settings_with_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "abc123")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    settings = load_settings()

    assert settings.gemini_api_key == "abc123"
    # Sem GEMINI_MODEL no ambiente, usa o padrão (a menos que o .env defina um).
    assert settings.gemini_model


def test_default_model_constant():
    assert DEFAULT_GEMINI_MODEL.startswith("gemini-")
