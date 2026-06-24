# Checklist — Integração com o Gemini (geração real)

## Parte A — Backend
- [x] `src/schemas/dnd5e.py` — modelos Pydantic
- [x] `src/prompts.py` — SYSTEM_PROMPT + ADVENTURE_PROMPT_TEMPLATE
- [x] `src/config.py` — ConfigError + modelo padrão gemini-2.5-flash
- [x] `.env.example` — modelo padrão atualizado
- [x] `src/ia_client.py` — generate_adventure real + IAClientError
- [x] `src/ia_client.py` — retry/backoff para erros transitórios (503) + msg precisa

## Parte B — Frontend
- [x] `app.py` — get_client (cache), card real, spinner e tratamento de erro

## Parte C — Testes (sem rede)
- [x] `tests/test_ia_client.py` (inclui retry)
- [x] `tests/test_config.py`
- [x] `tests/test_prompts.py`
- [x] `tests/test_app.py` atualizado
- [x] `pytest -q` passando (18 testes)

## Parte D — Docs e Git
- [x] Substituir `documents/PLANO.md` e `documents/CHECKLIST.md`
- [x] Commit + `git push origin development` (atualiza PR #1)

## Verificação
- [x] Ponta a ponta: aventura real gerada pelo Gemini renderizada no card
- [x] Erro transitório (503) tratado com mensagem clara (`st.error`)
- [x] Modelo do `.env` corrigido (gemini-1.5-flash → gemini-2.5-flash)
