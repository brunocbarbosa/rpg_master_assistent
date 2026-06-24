"""RPG Master Assistant — aplicação Streamlit (entrypoint).

Página principal do gerador de aventuras de D&D 5e (MVP / Fase 1). A interface
coleta a ideia central do mestre e alguns ajustes (tom, nível, duração) e exibe
o resultado seguindo o Funil Narrativo + estrutura de 3 atos.

NOTA: a geração via IA ainda NÃO está implementada. Ao submeter, a página exibe
uma **aventura de exemplo (mock)** para demonstrar o layout do resultado; a
chamada real ao modelo Gemini (src/ia_client.py) entra em uma etapa posterior.

Para executar:
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
CSS_PATH = BASE_DIR / "static" / "style.css"

# Opções do formulário — centralizadas aqui para reuso futuro pelo prompt da IA.
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


def _example_adventure_html(idea: str, tom: str, nivel: str, duracao: str) -> str:
    """Monta o HTML de uma aventura de EXEMPLO (mock) com base nos campos.

    Demonstra o layout do resultado (Funil Narrativo + 3 atos) seguindo a forma
    de ``src/schemas/dnd5e.py``, sem chamar a IA.
    """
    html = f"""
    <div class="rpg-card">
        <h2>⚔️ A Sombra sobre o Vilarejo</h2>
        <div>
            <span class="rpg-tag">Tom: {tom}</span>
            <span class="rpg-tag">Nível: {nivel}</span>
            <span class="rpg-tag">Duração: {duracao}</span>
        </div>

        <h3>🪝 Gancho</h3>
        <p>{idea}</p>

        <h3>👁️ Antagonista &amp; Ameaça</h3>
        <p>Um culto esquecido invoca uma entidade que se alimenta de memórias.
        <span class="rpg-doom">Doom Clock:</span> a cada lua cheia, mais um
        habitante desaparece sem deixar rastro — em três luas, o vilarejo inteiro
        terá sido esquecido pelo mundo.</p>

        <h3>📜 Estrutura em 3 Atos</h3>
        <p><strong>Ato 1 — O Chamado:</strong> os heróis chegam ao vilarejo e
        descobrem os desaparecimentos e o medo que paralisa os moradores.</p>
        <p><strong>Ato 2 — O Desenvolvimento:</strong> investigação das ruínas,
        pistas do culto e confrontos com servos da entidade.</p>
        <p><strong>Ato 3 — O Clímax:</strong> confronto final no santuário antes
        que a última lua cheia complete o ritual.</p>

        <p style="margin-top:1rem;color:#a89c8a;font-style:italic;">
        ✨ Exemplo ilustrativo — a geração real via IA (Gemini) será adicionada na
        próxima etapa.</p>
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
            # TODO (Fase 1 funcional): substituir o exemplo abaixo pela chamada a
            # src.ia_client.IAClient.generate_adventure(idea, tom, nivel, duracao).
            st.markdown(
                _example_adventure_html(idea.strip(), tom, nivel, duracao),
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
