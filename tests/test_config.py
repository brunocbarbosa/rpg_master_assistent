"""Testes de carregamento de configuração (src/config.py)."""

from __future__ import annotations

from src.config import DEFAULT_OLLAMA_MODEL, load_settings


def test_load_settings_uses_env_host_and_model(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "http://192.168.0.10:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "mistral-nemo")

    settings = load_settings()

    assert settings.ollama_host == "http://192.168.0.10:11434"
    assert settings.ollama_model == "mistral-nemo"


def test_load_settings_defaults_when_host_absent(monkeypatch):
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    settings = load_settings()

    # Host auto-detectado (WSL/localhost) e modelo padrão.
    assert settings.ollama_host.startswith("http://")
    assert settings.ollama_host.endswith(":11434")
    assert settings.ollama_model == DEFAULT_OLLAMA_MODEL


def test_default_model_constant():
    assert DEFAULT_OLLAMA_MODEL == "mistral"
