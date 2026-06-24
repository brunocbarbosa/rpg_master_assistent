"""Testes da página principal (app.py).

Usa o framework oficial ``streamlit.testing.v1.AppTest`` para executar a app
de forma headless e inspecionar os elementos renderizados.
"""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

import app

APP_PATH = str(Path(app.__file__).resolve())


def _run():
    """Instancia e executa a app a partir do arquivo, retornando o AppTest."""
    at = AppTest.from_file(APP_PATH)
    at.run()
    return at


def test_form_options_nonempty():
    assert app.TONS, "TONS não deve ser vazio"
    assert app.NIVEIS, "NIVEIS não deve ser vazio"
    assert app.DURACOES, "DURACOES não deve ser vazio"


def test_load_css_file_exists_and_has_style():
    css = app.CSS_PATH.read_text(encoding="utf-8")
    assert ".rpg-hero" in css
    assert ".rpg-card" in css


def test_page_renders_without_exception():
    at = _run()
    assert not at.exception
    # Título presente em algum bloco markdown do hero.
    markdown_text = " ".join(md.value for md in at.markdown)
    assert "RPG Master Assistant" in markdown_text
    # Formulário: 1 text_area + 3 selectbox.
    assert len(at.text_area) == 1
    assert len(at.selectbox) == 3


def test_empty_idea_shows_warning():
    at = _run()
    at.button[0].click().run()
    assert len(at.warning) == 1
    assert "ideia" in at.warning[0].value.lower()


def test_valid_idea_renders_example_card():
    at = _run()
    at.text_area[0].set_value("Um vilarejo amaldiçoado sob a lua cheia.")
    at.button[0].click().run()
    assert not at.exception
    assert len(at.warning) == 0
    markdown_text = " ".join(md.value for md in at.markdown)
    # O card de exemplo e a ideia informada aparecem no resultado.
    assert "rpg-card" in markdown_text
    assert "Um vilarejo amaldiçoado" in markdown_text
