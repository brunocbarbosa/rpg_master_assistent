"""Estruturas de dados (JSON Schemas) para saídas de Dungeons & Dragons 5e.

Define o formato estruturado que o modelo deve seguir ao gerar uma aventura,
garantindo um processamento consistente da resposta (Funil Narrativo + 3 atos).

NOTA: PLACEHOLDER. Os schemas definitivos serão definidos na Fase 1 funcional.
"""

# Esboço da estrutura de uma aventura de D&D 5e.
# TODO: converter em JSON Schema completo (ou modelo Pydantic) e usar para
# validar a resposta do modelo em `src/ia_client.py`.
ADVENTURE_SCHEMA: dict = {
    "title": "",
    "narrative_funnel": {
        "plot_hook": "",
        "antagonist": {
            "description": "",
            "doom_clock": "",
        },
        "key_locations": [],
        "key_npcs": [],
    },
    "three_act_structure": {
        "act_1_the_call": "",
        "act_2_the_development": "",
        "act_3_the_climax": "",
    },
}
