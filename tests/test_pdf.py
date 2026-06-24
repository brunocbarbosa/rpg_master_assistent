"""Testes da geração de PDF (src/pdf.py)."""

from __future__ import annotations

from src.pdf import build_adventure_pdf, pdf_filename

ADVENTURE = {
    "title": "O Lamento da Garganta Gélida",
    "narrative_funnel": {
        "plot_hook": "Uma caravana some numa passagem de montanha — ninguém volta.",
        "antagonist": {
            "description": "Um espírito ancestral preso ao desfiladeiro.",
            "doom_clock": "A cada noite, a névoa avança 1–2 km vilarejo adentro.",
        },
        "key_locations": [
            {"name": "As Gargantas", "description": "Ravinas onde o vento uiva."},
            {"name": "O Altar", "description": "Pedra rachada coberta de runas."},
        ],
        "key_npcs": [
            {"name": "Mestra Elara", "description": "Sábia cega que ouve os mortos."},
        ],
    },
    "three_act_structure": {
        "act_1_the_call": "Os heróis encontram a caravana abandonada.",
        "act_2_the_development": "Investigam as gargantas e o altar.",
        "act_3_the_climax": "Confrontam o espírito antes do amanhecer.",
    },
}


def test_build_pdf_returns_pdf_bytes():
    data = build_adventure_pdf(ADVENTURE, "Sombrio", "1–4", "One-shot (1 sessão)")
    assert isinstance(data, (bytes, bytearray))
    assert bytes(data).startswith(b"%PDF")
    assert len(data) > 1000


def test_build_pdf_handles_dashes_and_accents():
    # Travessões (–/—) e acentos não devem quebrar a geração.
    data = build_adventure_pdf(ADVENTURE, "Épico", "11–16", "Campanha (5+ sessões)")
    assert bytes(data).startswith(b"%PDF")


def test_build_pdf_long_text_multiple_pages():
    big = dict(ADVENTURE)
    big["three_act_structure"] = {
        "act_1_the_call": "Lorem ipsão " * 400,
        "act_2_the_development": "Dolor sit " * 400,
        "act_3_the_climax": "Amet consectetur " * 400,
    }
    data = build_adventure_pdf(big, "Sombrio", "1–4", "Campanha")
    assert bytes(data).startswith(b"%PDF")


def test_pdf_filename_is_safe():
    assert pdf_filename("O Lamento da Garganta Gélida!") == "o-lamento-da-garganta-gelida.pdf"
    assert pdf_filename("") == "aventura.pdf"
    assert pdf_filename("###").endswith(".pdf")
