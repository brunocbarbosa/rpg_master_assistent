"""Geração do PDF da aventura — tema *dark fantasy*.

Recebe o dict estruturado (ver ``src/schemas/dnd5e.py``) e produz os bytes de um
PDF com fundo escuro, títulos dourados e texto claro, combinando com a tela.

Usa fontes Unicode (DejaVu) empacotadas em ``static/fonts/`` para renderizar
corretamente acentos do pt-BR e travessões (``–``/``—``).
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from fpdf import FPDF

_FONT_DIR = Path(__file__).resolve().parent.parent / "static" / "fonts"

# Cores do tema (RGB).
_BG = (22, 18, 14)
_GOLD = (212, 175, 55)
_GOLD_SOFT = (224, 200, 120)
_TEXT = (232, 224, 212)
_PURPLE = (167, 138, 224)  # roxo clareado para legibilidade sobre o fundo escuro

# Remove emojis / símbolos sem glifo no DejaVu (preserva acentos e travessões).
_EMOJI_RE = re.compile(
    "[\U0001f000-\U0001faff\U00002600-\U000027bf\U0001f1e6-\U0001f1ff⬀-⯿]"
)


def _clean(text: object) -> str:
    """Remove emojis/símbolos não suportados e normaliza espaços."""
    return _EMOJI_RE.sub("", str(text)).strip()


def pdf_filename(title: str) -> str:
    """Gera um nome de arquivo seguro a partir do título da aventura."""
    base = unicodedata.normalize("NFKD", title or "")
    base = base.encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    return f"{base or 'aventura'}.pdf"


class _AdventurePDF(FPDF):
    """FPDF que pinta o fundo escuro em toda página (inclusive nas quebras)."""

    def header(self) -> None:  # noqa: D401 — chamado automaticamente a cada página
        self.set_fill_color(*_BG)
        self.rect(0, 0, self.w, self.h, "F")
        self.set_xy(self.l_margin, self.t_margin)


def build_adventure_pdf(adventure: dict, tom: str, nivel: str, duracao: str) -> bytes:
    """Monta o PDF da aventura e retorna seus bytes."""
    pdf = _AdventurePDF(format="A4")
    pdf.add_font("DejaVu", "", str(_FONT_DIR / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(_FONT_DIR / "DejaVuSans-Bold.ttf"))
    pdf.set_margins(18, 18, 18)
    pdf.set_auto_page_break(True, margin=18)
    pdf.add_page()

    funnel = adventure.get("narrative_funnel", {})
    antagonist = funnel.get("antagonist", {})
    acts = adventure.get("three_act_structure", {})

    def write(text: str, *, size: int = 11, color=_TEXT, bold: bool = False) -> None:
        pdf.set_font("DejaVu", "B" if bold else "", size)
        pdf.set_text_color(*color)
        pdf.multi_cell(0, 6, _clean(text), new_x="LMARGIN", new_y="NEXT")

    def heading(text: str) -> None:
        pdf.ln(3)
        write(text, size=13, color=_GOLD_SOFT, bold=True)

    # Título + tags.
    write(adventure.get("title", "Aventura"), size=20, color=_GOLD, bold=True)
    write(
        f"Tom: {tom}   |   Nível: {nivel}   |   Duração: {duracao}",
        size=10,
        color=_GOLD_SOFT,
    )

    heading("Gancho")
    write(funnel.get("plot_hook", ""))

    heading("Antagonista & Ameaça")
    write(antagonist.get("description", ""))
    write(f"Doom Clock: {antagonist.get('doom_clock', '')}", color=_PURPLE, bold=True)

    heading("Locais-chave")
    for loc in funnel.get("key_locations", []):
        write(f"•  {loc.get('name', '')}: {loc.get('description', '')}")

    heading("NPCs")
    for npc in funnel.get("key_npcs", []):
        write(f"•  {npc.get('name', '')}: {npc.get('description', '')}")

    heading("Estrutura em 3 Atos")
    for label, key in (
        ("Ato 1 — O Chamado", "act_1_the_call"),
        ("Ato 2 — O Desenvolvimento", "act_2_the_development"),
        ("Ato 3 — O Clímax", "act_3_the_climax"),
    ):
        write(label, color=_GOLD_SOFT, bold=True)
        write(acts.get(key, ""))

    return bytes(pdf.output())
