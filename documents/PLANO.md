# Plano — Página principal (frontend) + fluxo Git + testes

## Contexto

O projeto é um esqueleto Streamlit (MVP D&D 5e). Hoje `app.py` mostrava apenas um
`text_area` cru + botão, com a aparência genérica padrão do Streamlit, e a geração
via IA ainda não está implementada. Esta etapa entrega três coisas:

1. **Página principal — só a UI, bonita e temática** — onde o mestre informa a
   ideia da aventura. A integração com a IA (Gemini) fica para depois; aqui o
   botão "Gerar Aventura" demonstra o fluxo com um resultado de exemplo (mock).
2. **Fluxo de Git:** branch `development` a partir da `main`, e a `main` protegida
   para só receber atualizações via Pull Request.
3. **Testes automatizados** da página (primeira suíte de testes do projeto).

Decisões validadas com o usuário:
- **Stack:** Streamlit + CSS customizado (mantém o stack do CLAUDE.md).
- **Campos do formulário:** ideia central + tom + nível dos personagens + duração.
- **Estilo visual:** *dark fantasy* — fundo escuro, acentos dourado/âmbar e roxo,
  títulos com tipografia medieval (Cinzel).
- **Proteção da `main`:** branch protection exigindo PR, com 0 aprovações (projeto
  solo), `enforce_admins: true`. O GitHub não restringe de qual branch o PR vem;
  "a partir da `development`" é convenção do fluxo.

## Parte A — Frontend

1. **`.streamlit/config.toml`** — tema base dark do Streamlit (cores
   primária/fundo/superfície/texto) coerente com o dark fantasy.
2. **`static/style.css`** — CSS customizado: fontes Cinzel (títulos) + EB Garamond
   (corpo), hero dourado com brilho, botão com gradiente dourado e hover, inputs e
   selects com bordas âmbar, card de resultado, esconder menu/rodapé do Streamlit.
3. **`app.py`** (reescrito) — `load_css()`, constantes de formulário
   (`TONS`, `NIVEIS`, `DURACOES`), hero, formulário (`st.form`) com ideia + 3
   selects + botão, e ao submeter: aviso se vazio, ou card de aventura de exemplo
   (mock) seguindo a forma de `src/schemas/dnd5e.py`.

## Parte B — Testes automatizados

`streamlit.testing.v1.AppTest` + `pytest`.

- `requirements-dev.txt` — `pytest`.
- `tests/__init__.py` (vazio) e `tests/test_app.py`:
  - `test_form_options_nonempty`
  - `test_load_css`
  - `test_page_renders`
  - `test_empty_idea_shows_warning`
  - `test_valid_idea_renders_result`

## Parte C — Fluxo de Git

1. Criar branch `development` a partir da `main`.
2. Criar `documents/PLANO.md` e `documents/CHECKLIST.md`.
3. Implementar Partes A e B; commits em pt-BR (`feat:`/`chore:`/`test:`),
   atualizando a CHECKLIST a cada tarefa.
4. `git push -u origin development`.
5. Branch protection na `main` via `gh api` (PR obrigatório, 0 aprovações,
   `enforce_admins: true`).
6. Abrir PR `development → main`.

## Fora de escopo
- Nenhuma chamada real à Gemini / `IAClient`.
- Sem alterações em `src/ia_client.py`, `src/prompts.py`, `src/config.py`,
  `src/schemas/dnd5e.py`.

## Verificação
1. `pip install -r requirements-dev.txt` e `pytest -q` → verde.
2. `streamlit run app.py` → tema aplicado, formulário e card de exemplo funcionando.
3. `git branch` (development ativa), branch protection ativa, PR aberto.
