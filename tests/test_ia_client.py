"""Testes do cliente de IA (src/ia_client.py).

A biblioteca do Ollama é totalmente mockada — nenhum teste acessa a rede.
"""

from __future__ import annotations

import httpx
import ollama
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


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeResponse:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeClient:
    """Cliente fake cujo ``.chat(**kwargs)`` devolve (ou levanta) uma resposta."""

    def __init__(self, response):
        self._response = response
        self.last_kwargs = None

    def chat(self, **kwargs):
        self.last_kwargs = kwargs
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


def _patch_client(monkeypatch, response):
    """Faz ``ollama.Client(...)`` devolver um cliente fake com a resposta dada."""
    fake = _FakeClient(response)
    monkeypatch.setattr(ia_client.ollama, "Client", lambda **_: fake)
    return fake


class _FakeRetriever:
    """Retriever fake: registra a query e devolve trechos fixos."""

    def __init__(self, chunks=None):
        self.chunks = chunks if chunks is not None else []
        self.last_query = None

    def retrieve(self, query, n_results=5):
        self.last_query = query
        return self.chunks


def _make_client(retriever=None) -> IAClient:
    return IAClient(
        Settings(ollama_host="http://x:11434", ollama_model="mistral"),
        retriever=retriever if retriever is not None else _FakeRetriever(),
    )


def test_generate_adventure_returns_dict(monkeypatch):
    content = _fake_adventure().model_dump_json()
    fake = _patch_client(monkeypatch, _FakeResponse(content))
    client = _make_client()

    result = client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")

    assert result["title"] == "O Sino de Pedraluz"
    assert result["narrative_funnel"]["antagonist"]["doom_clock"]
    assert result["three_act_structure"]["act_3_the_climax"]
    # O prompt e o schema foram enviados corretamente ao Ollama.
    kwargs = fake.last_kwargs
    assert kwargs["model"] == "mistral"
    assert kwargs["format"] == Adventure.model_json_schema()
    roles = {m["role"]: m["content"] for m in kwargs["messages"]}
    assert "system" in roles
    assert "ideia" in roles["user"]


def test_invalid_response_becomes_ia_client_error(monkeypatch):
    _patch_client(monkeypatch, _FakeResponse("não é json"))
    client = _make_client()

    with pytest.raises(IAClientError):
        client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")


def test_sdk_error_becomes_ia_client_error(monkeypatch):
    _patch_client(monkeypatch, RuntimeError("falha inesperada"))
    client = _make_client()

    with pytest.raises(IAClientError):
        client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")


def test_connection_error_becomes_ia_client_error(monkeypatch):
    _patch_client(monkeypatch, httpx.ConnectError("connection refused"))
    client = _make_client()

    with pytest.raises(IAClientError, match="conectar ao Ollama"):
        client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")


def _server_error() -> ollama.ResponseError:
    return ollama.ResponseError("UNAVAILABLE", 503)


class _SequencedClient:
    """Devolve, a cada chamada, o próximo item de uma sequência (raise se Exception)."""

    def __init__(self, sequence):
        self._sequence = list(sequence)
        self.calls = 0

    def chat(self, **_):
        item = self._sequence[self.calls]
        self.calls += 1
        if isinstance(item, Exception):
            raise item
        return item


def _patch_sequenced(monkeypatch, sequence):
    client = _SequencedClient(sequence)
    monkeypatch.setattr(ia_client.ollama, "Client", lambda **_: client)
    monkeypatch.setattr(ia_client.time, "sleep", lambda *_: None)  # sem espera real
    return client


def test_retries_then_succeeds_on_transient_error(monkeypatch):
    content = _fake_adventure().model_dump_json()
    client_fake = _patch_sequenced(
        monkeypatch,
        [_server_error(), _FakeResponse(content)],
    )
    client = _make_client()

    result = client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")

    assert result["title"] == "O Sino de Pedraluz"
    assert client_fake.calls == 2  # falhou 1x, sucesso na 2ª


def test_persistent_transient_error_raises_overload_message(monkeypatch):
    client_fake = _patch_sequenced(
        monkeypatch,
        [_server_error(), _server_error(), _server_error()],
    )
    client = _make_client()

    with pytest.raises(IAClientError, match="sobrecarregado"):
        client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")
    assert client_fake.calls == 3  # esgotou as tentativas


def test_query_uses_idea_tom_and_nivel(monkeypatch):
    content = _fake_adventure().model_dump_json()
    _patch_client(monkeypatch, _FakeResponse(content))
    retriever = _FakeRetriever()
    client = _make_client(retriever)

    client.generate_adventure("cidade flutuante", "Sombrio", "5–10", "One-shot")

    assert "cidade flutuante" in retriever.last_query
    assert "Sombrio" in retriever.last_query
    assert "5–10" in retriever.last_query


def test_context_injected_when_chunks(monkeypatch):
    content = _fake_adventure().model_dump_json()
    fake = _patch_client(monkeypatch, _FakeResponse(content))
    client = _make_client(_FakeRetriever(chunks=["Regra do grimório"]))

    client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")

    user_msg = {m["role"]: m["content"] for m in fake.last_kwargs["messages"]}["user"]
    assert "Regra do grimório" in user_msg
    assert "<regras>" in user_msg


def test_no_context_block_when_no_chunks(monkeypatch):
    content = _fake_adventure().model_dump_json()
    fake = _patch_client(monkeypatch, _FakeResponse(content))
    client = _make_client(_FakeRetriever(chunks=[]))

    client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")

    user_msg = {m["role"]: m["content"] for m in fake.last_kwargs["messages"]}["user"]
    assert "<regras>" not in user_msg
