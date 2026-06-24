"""RPG Master Assistant — aplicação Streamlit (entrypoint).

Página principal do gerador de aventuras de D&D 5e (MVP / Fase 1). A interface
coleta a ideia central do mestre e alguns ajustes (tom, nível, duração), chama o
modelo Gemini (via src/ia_client.py) e exibe a aventura gerada seguindo o Funil
Narrativo + estrutura de 3 atos.

Para executar:
    streamlit run app.py
"""

from __future__ import annotations

import html as html_lib
from pathlib import Path

import streamlit as st

from src.config import ConfigError, load_settings
from src.ia_client import IAClient, IAClientError
from src.pdf import build_adventure_pdf, pdf_filename

BASE_DIR = Path(__file__).resolve().parent
CSS_PATH = BASE_DIR / "static" / "style.css"

# Opções do formulário — centralizadas aqui e reutilizadas no prompt da IA.
TONS = ["Sombrio", "Heroico", "Misterioso", "Épico", "Cômico"]
NIVEIS = ["1–4", "5–10", "11–16", "17–20"]
DURACOES = [
    "One-shot (1 sessão)",
    "Curta (2–4 sessões)",
    "Campanha (5+ sessões)",
]


def load_css(path: Path) -> None:
    """Lê o arquivo CSS e injeta na página via ``st.markdown``.

    Mantém o estilo fora do código Python e permite o tema "dark fantasy".
    """
    css = Path(path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def get_client() -> IAClient:
    """Instancia o ``IAClient`` uma única vez (cache entre reruns do Streamlit)."""
    return IAClient(load_settings())


def _render_hero() -> None:
    """Renderiza o cabeçalho (hero) com título e subtítulo."""
    st.markdown(
        """
        <div class="rpg-hero">
            <h1>🎲 RPG Master Assistant</h1>
            <p>Co-piloto de IA para mestres de RPG — Gerador de aventuras de D&amp;D 5e</p>
        </div>
        <hr class="rpg-divider" />
        """,
        unsafe_allow_html=True,
    )


def _esc(value: str) -> str:
    """Escapa texto vindo da IA para inserção segura no HTML do card."""
    return html_lib.escape(str(value))


def _adventure_card_html(
    adventure: dict, tom: str, nivel: str, duracao: str
) -> str:
    """Monta o HTML do card a partir do dict estruturado da aventura.

    Segue a forma de ``src/schemas/dnd5e.py`` (Funil Narrativo + 3 atos).
    """
    funnel = adventure.get("narrative_funnel", {})
    antagonist = funnel.get("antagonist", {})
    acts = adventure.get("three_act_structure", {})

    locations = "".join(
        f"<li><strong>{_esc(loc.get('name', ''))}:</strong> "
        f"{_esc(loc.get('description', ''))}</li>"
        for loc in funnel.get("key_locations", [])
    )
    npcs = "".join(
        f"<li><strong>{_esc(npc.get('name', ''))}:</strong> "
        f"{_esc(npc.get('description', ''))}</li>"
        for npc in funnel.get("key_npcs", [])
    )

    html = f"""
    <div class="rpg-card">
        <h2>⚔️ {_esc(adventure.get('title', 'Aventura'))}</h2>
        <div>
            <span class="rpg-tag">Tom: {_esc(tom)}</span>
            <span class="rpg-tag">Nível: {_esc(nivel)}</span>
            <span class="rpg-tag">Duração: {_esc(duracao)}</span>
        </div>

        <h3>🪝 Gancho</h3>
        <p>{_esc(funnel.get('plot_hook', ''))}</p>

        <h3>👁️ Antagonista &amp; Ameaça</h3>
        <p>{_esc(antagonist.get('description', ''))}</p>
        <p><span class="rpg-doom">Doom Clock:</span> {_esc(antagonist.get('doom_clock', ''))}</p>

        <h3>🗺️ Locais-chave</h3>
        <ul>{locations}</ul>

        <h3>🎭 NPCs</h3>
        <ul>{npcs}</ul>

        <h3>📜 Estrutura em 3 Atos</h3>
        <p><strong>Ato 1 — O Chamado:</strong> {_esc(acts.get('act_1_the_call', ''))}</p>
        <p><strong>Ato 2 — O Desenvolvimento:</strong> {_esc(acts.get('act_2_the_development', ''))}</p>
        <p><strong>Ato 3 — O Clímax:</strong> {_esc(acts.get('act_3_the_climax', ''))}</p>
    </div>
    """
    # Remove a indentação de cada linha: o markdown do Streamlit interpreta
    # linhas com 4+ espaços como bloco de código, o que renderizaria o HTML cru.
    return "\n".join(line.strip() for line in html.splitlines() if line.strip())


def main() -> None:
    st.set_page_config(
        page_title="RPG Master Assistant",
        page_icon="🎲",
        layout="centered",
    )
    load_css(CSS_PATH)

    _render_hero()

    with st.form("adventure_form"):
        idea = st.text_area(
            "Ideia central da aventura",
            placeholder="Ex.: Um vilarejo isolado nas montanhas onde crianças estão "
            "desaparecendo durante a lua cheia...",
            height=150,
        )

        col_tom, col_nivel, col_duracao = st.columns(3)
        with col_tom:
            tom = st.selectbox("Tom", TONS)
        with col_nivel:
            nivel = st.selectbox("Nível dos personagens", NIVEIS)
        with col_duracao:
            duracao = st.selectbox("Duração", DURACOES)

        submitted = st.form_submit_button("⚔️ Gerar Aventura", type="primary")

    if submitted:
        if not idea.strip():
            st.warning("Descreva uma ideia central antes de gerar a aventura.")
        else:
            _handle_generation(idea.strip(), tom, nivel, duracao)

    # Exibido a partir do session_state para sobreviver ao rerun do download.
    if "adventure" in st.session_state:
        _render_result(
            st.session_state["adventure"], st.session_state["params"]
        )


def _handle_generation(idea: str, tom: str, nivel: str, duracao: str) -> None:
    """Gera a aventura e guarda no session_state; em erro, mostra e limpa o estado."""
    try:
        client = get_client()
        with st.spinner("Convocando o oráculo... a aventura está sendo forjada."):
            adventure = client.generate_adventure(idea, tom, nivel, duracao)
    except (ConfigError, IAClientError) as exc:
        st.session_state.pop("adventure", None)
        st.session_state.pop("params", None)
        st.error(str(exc))
        return

    st.session_state["adventure"] = adventure
    st.session_state["params"] = (tom, nivel, duracao)


def _render_result(adventure: dict, params: tuple[str, str, str]) -> None:
    """Renderiza o card e o botão de download em PDF."""
    tom, nivel, duracao = params
    st.markdown(
        _adventure_card_html(adventure, tom, nivel, duracao),
        unsafe_allow_html=True,
    )

    try:
        pdf_bytes = build_adventure_pdf(adventure, tom, nivel, duracao)
    except Exception:  # noqa: BLE001 — o PDF nunca deve esconder a aventura
        st.warning("Não foi possível gerar o PDF desta aventura.")
        return

    st.download_button(
        "📜 Baixar em PDF",
        data=pdf_bytes,
        file_name=pdf_filename(adventure.get("title", "aventura")),
        mime="application/pdf",
    )


if __name__ == "__main__":
    main()
