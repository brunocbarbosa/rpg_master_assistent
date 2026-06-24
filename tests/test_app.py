"""Testes da página principal (app.py).

Usa o framework oficial ``streamlit.testing.v1.AppTest`` para executar a app de
forma headless. A chamada ao Ollama é sempre mockada — nenhum teste acessa a rede.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import app

APP_PATH = str(Path(app.__file__).resolve())

# Aventura fixa usada como retorno mockado do IAClient.
FAKE_ADVENTURE = {
    "title": "O Sino de Pedraluz",
    "narrative_funnel": {
        "plot_hook": "Um sino tocou sozinho à meia-noite.",
        "antagonist": {
            "description": "Um lich entediado.",
            "doom_clock": "A cada badalada, um morto se ergue.",
        },
        "key_locations": [{"name": "A Torre", "description": "Onde o sino dorme."}],
        "key_npcs": [{"name": "Mestra Vael", "description": "A sineira cega."}],
    },
    "three_act_structure": {
        "act_1_the_call": "Os heróis ouvem o sino.",
        "act_2_the_development": "Investigam a torre.",
        "act_3_the_climax": "Silenciam o sino para sempre.",
    },
}


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
    markdown_text = " ".join(md.value for md in at.markdown)
    assert "RPG Master Assistant" in markdown_text
    assert len(at.text_area) == 1
    assert len(at.selectbox) == 3


def test_empty_idea_shows_warning():
    at = _run()
    at.button[0].click().run()
    assert len(at.warning) == 1
    assert "ideia" in at.warning[0].value.lower()


def test_card_html_has_no_indented_lines():
    # Regressão: linhas com 4+ espaços fariam o Streamlit renderizar o HTML como
    # bloco de código em vez de HTML.
    html = app._adventure_card_html(FAKE_ADVENTURE, "Sombrio", "1–4", "One-shot")
    for line in html.splitlines():
        assert not line.startswith("    "), f"linha indentada: {line!r}"
    assert 'class="rpg-card"' in html
    assert "O Sino de Pedraluz" in html


def test_valid_idea_renders_generated_card(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "mistral")
    with patch.object(
        app.IAClient, "generate_adventure", return_value=FAKE_ADVENTURE
    ):
        at = AppTest.from_file(APP_PATH)
        at.run()
        at.text_area[0].set_value("Um sino amaldiçoado.")
        at.button[0].click().run()

        assert not at.exception
        assert len(at.warning) == 0
        markdown_text = " ".join(md.value for md in at.markdown)
        assert "rpg-card" in markdown_text
        assert "O Sino de Pedraluz" in markdown_text
        # A aventura fica no session_state para sobreviver ao rerun do download.
        assert at.session_state["adventure"]["title"] == "O Sino de Pedraluz"

        # Rerun sem submeter (simula o clique no download): o card persiste.
        at.run()
        assert "O Sino de Pedraluz" in " ".join(md.value for md in at.markdown)


def test_error_clears_previous_adventure(monkeypatch):
    from src.ia_client import IAClientError

    monkeypatch.setenv("OLLAMA_MODEL", "mistral")
    at = AppTest.from_file(APP_PATH)
    at.session_state["adventure"] = FAKE_ADVENTURE
    at.session_state["params"] = ("Sombrio", "1–4", "One-shot")
    with patch.object(
        app.IAClient, "generate_adventure", side_effect=IAClientError("Falhou.")
    ):
        at.run()
        at.text_area[0].set_value("Nova ideia.")
        at.button[0].click().run()

    assert len(at.error) == 1
    assert "adventure" not in at.session_state


def test_config_error_shows_friendly_message(monkeypatch):
    from src.config import ConfigError

    monkeypatch.setenv("OLLAMA_MODEL", "mistral")
    with patch.object(
        app.IAClient,
        "generate_adventure",
        side_effect=ConfigError("Falha de configuração."),
    ):
        at = AppTest.from_file(APP_PATH)
        at.run()
        at.text_area[0].set_value("Qualquer ideia.")
        at.button[0].click().run()

    assert not at.exception
    assert len(at.error) == 1
    assert "Falha de configuração." in at.error[0].value
