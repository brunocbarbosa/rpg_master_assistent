"""Testes do cliente de IA (src/ia_client.py).

O SDK do Gemini é totalmente mockado — nenhum teste acessa a rede.
"""

from __future__ import annotations

import pytest

import src.ia_client as ia_client
from src.config import Settings
from src.ia_client import IAClient, IAClientError
from src.schemas.dnd5e import (
    Adventure,
    Antagonist,
    Location,
    NarrativeFunnel,
    NPC,
    ThreeActStructure,
)


def _fake_adventure() -> Adventure:
    return Adventure(
        title="O Sino de Pedraluz",
        narrative_funnel=NarrativeFunnel(
            plot_hook="Um sino tocou sozinho.",
            antagonist=Antagonist(
                description="Um lich entediado.",
                doom_clock="A cada badalada, um morto se ergue.",
            ),
            key_locations=[Location(name="A Torre", description="Onde o sino dorme.")],
            key_npcs=[NPC(name="Mestra Vael", description="A sineira cega.")],
        ),
        three_act_structure=ThreeActStructure(
            act_1_the_call="Os heróis ouvem o sino.",
            act_2_the_development="Investigam a torre.",
            act_3_the_climax="Silenciam o sino.",
        ),
    )


class _FakeModels:
    def __init__(self, response):
        self._response = response
        self.last_kwargs = None

    def generate_content(self, **kwargs):
        self.last_kwargs = kwargs
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


class _FakeClient:
    def __init__(self, response):
        self.models = _FakeModels(response)


class _FakeResponse:
    def __init__(self, parsed=None, text=None):
        self.parsed = parsed
        self.text = text


def _patch_client(monkeypatch, response):
    """Faz ``genai.Client(...)`` devolver um cliente fake com a resposta dada."""
    fake = _FakeClient(response)
    monkeypatch.setattr(ia_client.genai, "Client", lambda **_: fake)
    return fake


def _make_client() -> IAClient:
    return IAClient(Settings(gemini_api_key="k", gemini_model="m"))


def test_generate_adventure_returns_dict(monkeypatch):
    fake = _patch_client(monkeypatch, _FakeResponse(parsed=_fake_adventure()))
    client = _make_client()

    result = client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")

    assert result["title"] == "O Sino de Pedraluz"
    assert result["narrative_funnel"]["antagonist"]["doom_clock"]
    assert result["three_act_structure"]["act_3_the_climax"]
    # O prompt foi montado com os parâmetros e o schema/ system prompt enviados.
    kwargs = fake.models.last_kwargs
    assert "ideia" in kwargs["contents"]
    assert kwargs["config"].response_schema is Adventure


def test_generate_adventure_parses_text_when_parsed_is_none(monkeypatch):
    json_text = _fake_adventure().model_dump_json()
    _patch_client(monkeypatch, _FakeResponse(parsed=None, text=json_text))
    client = _make_client()

    result = client.generate_adventure("ideia", "Épico", "5–10", "Curta")

    assert result["title"] == "O Sino de Pedraluz"


def test_sdk_error_becomes_ia_client_error(monkeypatch):
    _patch_client(monkeypatch, RuntimeError("falha de rede"))
    client = _make_client()

    with pytest.raises(IAClientError):
        client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")


def test_invalid_response_becomes_ia_client_error(monkeypatch):
    _patch_client(monkeypatch, _FakeResponse(parsed=None, text="não é json"))
    client = _make_client()

    with pytest.raises(IAClientError):
        client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")
