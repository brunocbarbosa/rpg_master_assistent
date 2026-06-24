# Checklist — Página principal (frontend) + fluxo Git + testes

## Parte C — Fluxo de Git
- [x] Criar branch `development` a partir da `main`
- [x] Criar `documents/PLANO.md`
- [x] Criar `documents/CHECKLIST.md`

## Parte A — Frontend
- [x] `.streamlit/config.toml` (tema base dark)
- [x] `static/style.css` (tema dark fantasy customizado)
- [x] `app.py` reescrito (load_css, constantes, hero, formulário, card de exemplo)

## Parte B — Testes automatizados
- [x] `requirements-dev.txt` (pytest)
- [x] `tests/__init__.py` + `tests/test_app.py`
- [x] `pytest -q` passando (5 testes)

## Verificação
- [ ] Revisão visual do app (`streamlit run app.py`)

## Fechamento
- [x] `git push -u origin development`
- [~] Branch protection na `main` — **adiada por decisão**: repo privado no plano
      free não suporta (exige GitHub Pro ou repo público). Por ora vale só a
      convenção de fluxo (trabalhar na `development`, levar à `main` via PR).
- [x] Abrir PR `development → main` (#1)
