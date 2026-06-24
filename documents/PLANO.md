# Plano — Integração com o Gemini (geração real de aventuras)

## Contexto

A etapa anterior entregou o frontend (página dark fantasy + testes), mas a
geração via IA era um **mock**. Esta etapa torna a geração **real**: ao submeter
o formulário, o app chama o **Google Gemini** e exibe uma aventura única (Funil
Narrativo + 3 atos) estruturada via JSON Schema (modelos Pydantic).

## Parte A — Backend (camada de IA)
- `src/schemas/dnd5e.py` — modelos Pydantic (`Adventure`, `NarrativeFunnel`,
  `Antagonist`, `Location`, `NPC`, `ThreeActStructure`) usados como
  `response_schema`.
- `src/prompts.py` — `SYSTEM_PROMPT` (persona mestre D&D 5e, pt-BR) e
  `ADVENTURE_PROMPT_TEMPLATE` com `{idea}/{tom}/{nivel}/{duracao}`.
- `src/config.py` — `load_settings()` levanta `ConfigError` sem a chave; modelo
  padrão `gemini-2.5-flash`.
- `src/ia_client.py` — `IAClient.generate_adventure(idea, tom, nivel, duracao)`
  chama o Gemini com saída JSON estruturada; erros viram `IAClientError`.

## Parte B — Frontend (`app.py`)
- `get_client()` em `@st.cache_resource`.
- `_adventure_card_html(...)` renderiza o dict real (título, Gancho, Antagonista
  + Doom Clock, Locais-chave, NPCs, 3 atos), com escape de HTML.
- Submit: `st.spinner` durante a geração; `ConfigError`/`IAClientError` → `st.error`.

## Parte C — Testes (sem rede)
- `tests/test_ia_client.py`, `tests/test_config.py`, `tests/test_prompts.py` e
  `tests/test_app.py` (atualizado). Gemini sempre mockado.

## Parte D — Docs e Git
- Substituir `documents/PLANO.md` e `documents/CHECKLIST.md`.
- Continuar na `development`; tudo no mesmo **PR #1**.

## Fora de escopo
- Multi-sistema / Cyberpunk RED (Fase 2). Só D&D 5e.

## Verificação
1. `pytest -q` → verde (sem rede).
2. `streamlit run app.py` com chave real → aventura gerada pelo Gemini no card.
3. Sem `GEMINI_API_KEY` → `st.error` claro em vez de quebrar.
