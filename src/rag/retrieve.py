"""Consulta da base de conhecimento (RAG) na geração.

Recupera trechos relevantes das regras na coleção ``dnd_5e_knowledge`` do
ChromaDB para enriquecer o prompt. É best-effort: qualquer falha (Chroma fora,
coleção ausente, embed model não instalado) devolve uma lista vazia — a geração
segue sem o contexto das regras.
"""

from __future__ import annotations

import logging

import chromadb

from src.config import Settings
from src.rag.constants import COLLECTION_NAME
from src.rag.embeddings import OllamaEmbeddingFunction

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 5


class Retriever:
    """Recupera trechos de regras do ChromaDB (best-effort, conexão lazy)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._collection = None  # conectado sob demanda e cacheado

    def _get_collection(self) -> chromadb.Collection:
        if self._collection is None:
            client = chromadb.HttpClient(
                host=self._settings.chroma_host, port=self._settings.chroma_port
            )
            embedding_function = OllamaEmbeddingFunction(
                host=self._settings.ollama_host,
                model=self._settings.ollama_embed_model,
            )
            self._collection = client.get_collection(
                name=COLLECTION_NAME, embedding_function=embedding_function
            )
        return self._collection

    def retrieve(self, query: str, n_results: int = DEFAULT_TOP_K) -> list[str]:
        """Devolve até ``n_results`` trechos relevantes; ``[]`` em qualquer falha."""
        try:
            collection = self._get_collection()
            results = collection.query(query_texts=[query], n_results=n_results)
            documents = results.get("documents") or [[]]
            return list(documents[0])
        except Exception as exc:  # noqa: BLE001 — RAG é reforço, nunca quebra a geração
            logger.warning("RAG indisponível, gerando sem contexto: %s", exc)
            self._collection = None  # força reconexão na próxima tentativa
            return []
