"""RPG Master Assistant — aplicação Streamlit (entrypoint).

Esqueleto da interface do gerador de aventuras de D&D 5e (MVP / Fase 1).
A geração via IA ainda NÃO está implementada — esta tela apenas estrutura o
formulário e o local de exibição do resultado.

Para executar:
    streamlit run app.py
"""

import streamlit as st


def main() -> None:
    st.set_page_config(page_title="RPG Master Assistant", page_icon="🎲")

    st.title("🎲 RPG Master Assistant")
    st.caption("Co-piloto de IA para mestres de RPG — Gerador de aventuras de D&D 5e")

    idea = st.text_area(
        "Ideia central da aventura",
        placeholder="Ex.: Um vilarejo isolado nas montanhas onde crianças estão "
        "desaparecendo durante a lua cheia...",
        height=150,
    )

    if st.button("Gerar Aventura", type="primary"):
        if not idea.strip():
            st.warning("Descreva uma ideia central antes de gerar a aventura.")
        else:
            # TODO (Fase 1 funcional): chamar src.ia_client.IAClient.generate_adventure
            # e exibir a aventura estruturada (Funil Narrativo + 3 atos).
            st.info("Geração de aventura ainda não implementada.")


if __name__ == "__main__":
    main()
