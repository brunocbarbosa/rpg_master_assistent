"""Ingestão dos PDFs de regras na base de conhecimento (ChromaDB).

Pipeline: para cada livro em ``documents/books/dnd_5e/`` extrai o texto (PyPDF2),
divide em trechos (`RecursiveCharacterTextSplitter`), embeda via Ollama e grava
na coleção ``dnd_5e_knowledge`` com metadados que isolam sistema e livro.

A ingestão é idempotente: cada trecho recebe um ID determinístico
(``sha1(pdf_name:índice)``) e usa ``upsert`` — reprocessar um livro sobrescreve
em vez de duplicar.

Uso:
    python -m src.rag.ingest            # ingere/atualiza os 3 livros
    python -m src.rag.ingest --rebuild  # apaga a coleção antes de ingerir
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader

from src.config import Settings, load_settings
from src.rag.constants import COLLECTION_NAME, RPG_SYSTEM
from src.rag.embeddings import OllamaEmbeddingFunction

# --- Decisões da Fase 2 (ver documents/plans/PLANO_RAG.md) -------------------

# Pasta de origem, relativa à raiz do projeto.
BOOKS_DIR = Path("documents/books") / RPG_SYSTEM

# Parâmetros de divisão definidos com o usuário.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Quantos trechos enviar por chamada de upsert (cada lote vira uma chamada de
# embeddings no Ollama). Mantém o uso de memória previsível em PDFs grandes.
BATCH_SIZE = 100

# Livros de D&D 5e → categoria. Explícito de propósito: garante erro claro se um
# arquivo esperado faltar e documenta o vínculo arquivo ↔ book_category.
DND_5E_BOOKS: dict[str, str] = {
    "dnd_5e_master_guide.pdf": "master_guide",
    "dnd_5e_monsters_manual.pdf": "monsters_manual",
    "dnd_5e_player_book.pdf": "player_book",
}


@dataclass(frozen=True)
class BookSource:
    """Um PDF de origem e seus metadados de catalogação."""

    path: Path
    pdf_name: str
    rpg_system: str
    book_category: str


# --- Funções puras (sem rede) ------------------------------------------------


def list_books(books_dir: Path = BOOKS_DIR) -> list[BookSource]:
    """Resolve os PDFs esperados em ``books_dir`` para ``BookSource``.

    Raises:
        FileNotFoundError: se algum PDF esperado não existir na pasta.
    """
    sources: list[BookSource] = []
    for pdf_name, book_category in DND_5E_BOOKS.items():
        path = books_dir / pdf_name
        if not path.is_file():
            raise FileNotFoundError(
                f"PDF de regras não encontrado: {path}. Coloque os livros de "
                f"D&D 5e em {books_dir}/."
            )
        sources.append(
            BookSource(
                path=path,
                pdf_name=pdf_name,
                rpg_system=RPG_SYSTEM,
                book_category=book_category,
            )
        )
    return sources


def extract_text(pdf_path: Path) -> str:
    """Extrai o texto de todas as páginas do PDF, separadas por quebra de linha."""
    reader = PdfReader(str(pdf_path))
    pages = (page.extract_text() or "" for page in reader.pages)
    return "\n".join(pages)


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Divide o texto em trechos com sobreposição, ignorando trechos vazios."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return [chunk for chunk in splitter.split_text(text) if chunk.strip()]


def chunk_id(pdf_name: str, index: int) -> str:
    """ID determinístico de um trecho — estável entre execuções (idempotência)."""
    return hashlib.sha1(f"{pdf_name}:{index}".encode("utf-8")).hexdigest()


def build_records(
    book: BookSource, chunks: list[str]
) -> tuple[list[str], list[str], list[dict[str, str]]]:
    """Monta ``(ids, documents, metadatas)`` de um livro para gravar no Chroma."""
    ids = [chunk_id(book.pdf_name, i) for i in range(len(chunks))]
    metadatas = [
        {
            "pdf_name": book.pdf_name,
            "rpg_system": book.rpg_system,
            "book_category": book.book_category,
        }
        for _ in chunks
    ]
    return ids, chunks, metadatas


# --- Orquestração (com rede) -------------------------------------------------


def _get_collection(settings: Settings, *, rebuild: bool) -> chromadb.Collection:
    """Conecta ao Chroma e devolve a coleção `dnd_5e_knowledge` pronta para uso."""
    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    embedding_function = OllamaEmbeddingFunction(
        host=settings.ollama_host, model=settings.ollama_embed_model
    )
    if rebuild:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:  # noqa: BLE001 — coleção pode ainda não existir
            pass
    return client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=embedding_function
    )


def ingest(settings: Settings | None = None, *, rebuild: bool = False) -> int:
    """Ingere os 3 livros de D&D 5e na coleção. Retorna o total de trechos gravados."""
    settings = settings or load_settings()
    collection = _get_collection(settings, rebuild=rebuild)

    total = 0
    for book in list_books():
        print(f"→ {book.pdf_name} ({book.book_category}): extraindo texto…")
        chunks = split_text(extract_text(book.path))
        ids, documents, metadatas = build_records(book, chunks)
        print(f"  {len(chunks)} trechos — gravando na coleção '{COLLECTION_NAME}'…")
        # Remove trechos anteriores do livro para não deixar chunks órfãos em re-ingestões menores.
        collection.delete(where={"pdf_name": book.pdf_name})
        for start in range(0, len(chunks), BATCH_SIZE):
            end = start + BATCH_SIZE
            collection.upsert(
                ids=ids[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end],
            )
        total += len(chunks)

    print(f"✓ Ingestão concluída: {total} trechos na coleção '{COLLECTION_NAME}'.")
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="apaga a coleção antes de ingerir (reprocessa tudo do zero)",
    )
    args = parser.parse_args()
    ingest(rebuild=args.rebuild)


if __name__ == "__main__":
    main()
