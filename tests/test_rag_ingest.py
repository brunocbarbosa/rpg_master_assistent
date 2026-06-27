"""Testes das partes sem rede da ingestão de RAG (src/rag/ingest.py)."""

from __future__ import annotations

import pytest

from src.rag import ingest


def test_list_books_resolves_expected_pdfs(tmp_path):
    for pdf_name in ingest.DND_5E_BOOKS:
        (tmp_path / pdf_name).write_bytes(b"%PDF-1.4")

    books = ingest.list_books(tmp_path)

    assert {b.pdf_name for b in books} == set(ingest.DND_5E_BOOKS)
    assert all(b.rpg_system == "dnd_5e" for b in books)
    assert {b.book_category for b in books} == {
        "master_guide",
        "monsters_manual",
        "player_book",
    }


def test_list_books_missing_pdf_raises(tmp_path):
    # Apenas um dos três livros presente.
    (tmp_path / "dnd_5e_master_guide.pdf").write_bytes(b"%PDF-1.4")

    with pytest.raises(FileNotFoundError):
        ingest.list_books(tmp_path)


def test_split_text_respects_size_and_overlap():
    text = "palavra " * 500  # ~4000 caracteres

    chunks = ingest.split_text(text, chunk_size=1000, chunk_overlap=200)

    assert len(chunks) > 1
    assert all(len(chunk) <= 1000 for chunk in chunks)
    assert all(chunk.strip() for chunk in chunks)


def test_split_text_drops_empty_chunks():
    assert ingest.split_text("   \n\n  ") == []


def test_chunk_id_is_deterministic_and_unique():
    assert ingest.chunk_id("a.pdf", 1) == ingest.chunk_id("a.pdf", 1)
    assert ingest.chunk_id("a.pdf", 1) != ingest.chunk_id("a.pdf", 2)
    assert ingest.chunk_id("a.pdf", 1) != ingest.chunk_id("b.pdf", 1)


def test_build_records_attaches_metadata():
    book = ingest.BookSource(
        path=None,  # type: ignore[arg-type]
        pdf_name="dnd_5e_master_guide.pdf",
        rpg_system="dnd_5e",
        book_category="master_guide",
    )
    chunks = ["trecho 1", "trecho 2"]

    ids, documents, metadatas = ingest.build_records(book, chunks)

    assert documents == chunks
    assert len(ids) == len(set(ids)) == 2
    assert all(
        m == {
            "pdf_name": "dnd_5e_master_guide.pdf",
            "rpg_system": "dnd_5e",
            "book_category": "master_guide",
        }
        for m in metadatas
    )
