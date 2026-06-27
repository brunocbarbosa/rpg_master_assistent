"""Função de embeddings do ChromaDB apoiada no Ollama.

O ChromaDB chama uma ``EmbeddingFunction`` para transformar textos em vetores.
Aqui ela delega ao Ollama (modelo `nomic-embed-text` por padrão), reaproveitando
o mesmo servidor já usado para a geração — sem chave de API.
"""

from __future__ import annotations

from typing import Any

import ollama
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings


class OllamaEmbeddingFunction(EmbeddingFunction[Documents]):
    """Gera embeddings via Ollama para uso nas coleções do ChromaDB.

    Args:
        host: Endereço do servidor Ollama (ex.: ``http://localhost:11434``).
        model: Nome do modelo de embeddings (ex.: ``nomic-embed-text``).
    """

    def __init__(self, host: str, model: str) -> None:
        self._host = host
        self._model = model
        self._client = ollama.Client(host=host)

    def __call__(self, input: Documents) -> Embeddings:
        """Embeda um lote de textos e devolve a lista de vetores correspondente."""
        response = self._client.embed(model=self._model, input=list(input))
        return [list(vector) for vector in response.embeddings]

    @staticmethod
    def name() -> str:
        return "ollama_embed"

    def get_config(self) -> dict[str, Any]:
        return {"host": self._host, "model": self._model}

    @classmethod
    def build_from_config(cls, config: dict[str, Any]) -> "OllamaEmbeddingFunction":
        return cls(host=config["host"], model=config["model"])
