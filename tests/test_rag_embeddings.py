"""Testes da função de embeddings do RAG (src/rag/embeddings.py)."""

from __future__ import annotations

from src.rag.embeddings import OllamaEmbeddingFunction


class _FakeEmbedResponse:
    def __init__(self, embeddings):
        self.embeddings = embeddings


class _FakeOllamaClient:
    def __init__(self):
        self.calls = []

    def embed(self, model, input):  # noqa: A002 — assina igual ao SDK do ollama
        self.calls.append((model, list(input)))
        return _FakeEmbedResponse([[0.1, 0.2, 0.3] for _ in input])


def test_embedding_function_delegates_to_ollama(monkeypatch):
    ef = OllamaEmbeddingFunction(host="http://localhost:11434", model="nomic-embed-text")
    fake = _FakeOllamaClient()
    monkeypatch.setattr(ef, "_client", fake)

    vectors = ef(["texto a", "texto b"])

    assert len(vectors) == 2
    assert fake.calls == [("nomic-embed-text", ["texto a", "texto b"])]


def test_embedding_function_config_roundtrip():
    ef = OllamaEmbeddingFunction(host="http://h:1", model="m")
    rebuilt = OllamaEmbeddingFunction.build_from_config(ef.get_config())

    assert rebuilt.get_config() == {"host": "http://h:1", "model": "m"}
    assert OllamaEmbeddingFunction.name() == "ollama_embed"
