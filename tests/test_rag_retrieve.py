"""Testes da consulta de RAG (src/rag/retrieve.py) — sem rede."""

from __future__ import annotations

from src.config import Settings
from src.rag.retrieve import DEFAULT_TOP_K, Retriever


class _FakeCollection:
    """Coleção fake: devolve documentos fixos ou levanta um erro em ``query``."""

    def __init__(self, documents=None, error=None):
        self._documents = documents
        self._error = error
        self.last_query = None

    def query(self, query_texts, n_results):
        self.last_query = {"query_texts": query_texts, "n_results": n_results}
        if self._error is not None:
            raise self._error
        return {"documents": [self._documents]}


def _retriever_with(collection) -> Retriever:
    retriever = Retriever(
        Settings(ollama_host="http://x:11434", ollama_model="mistral")
    )
    retriever._collection = collection  # injeta, evita conectar
    return retriever


def test_retrieve_returns_documents():
    retriever = _retriever_with(_FakeCollection(documents=["trecho A", "trecho B"]))
    assert retriever.retrieve("consulta") == ["trecho A", "trecho B"]


def test_retrieve_passes_query_and_n_results():
    fake = _FakeCollection(documents=[])
    retriever = _retriever_with(fake)
    retriever.retrieve("minha busca", n_results=3)
    assert fake.last_query == {"query_texts": ["minha busca"], "n_results": 3}


def test_retrieve_default_top_k():
    fake = _FakeCollection(documents=[])
    retriever = _retriever_with(fake)
    retriever.retrieve("q")
    assert fake.last_query["n_results"] == DEFAULT_TOP_K


def test_retrieve_swallows_errors_returns_empty():
    retriever = _retriever_with(_FakeCollection(error=RuntimeError("chroma fora")))
    assert retriever.retrieve("q") == []
