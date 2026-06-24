# Checklist — Botão "Baixar em PDF" da aventura

## Implementação
- [x] `requirements.txt` — `fpdf2`
- [x] `static/fonts/` — DejaVuSans regular + bold empacotadas
- [x] `src/pdf.py` — `build_adventure_pdf` + `pdf_filename` (tema dark fantasy)
- [x] `app.py` — persistência em `session_state` + `st.download_button`

## Testes (sem rede)
- [x] `tests/test_pdf.py`
- [x] `tests/test_app.py` atualizado (session_state, persistência, erro)
- [x] `pytest -q` passando (23 testes)

## Verificação
- [x] PDF renderizado (tema escuro, dourado/roxo, acentos e travessões ok)
- [x] Botão "Baixar em PDF" aparece abaixo do card (validado no app)
- [ ] Geração ponta a ponta no app real bloqueada por pico de demanda do Gemini
      (503) no momento; o caminho do botão foi validado via preview sem IA

## Git
- [ ] Commit / push / PR — **somente quando o usuário pedir**
