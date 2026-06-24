# Plano — Botão "Baixar em PDF" da aventura gerada

## Contexto

Após gerar uma aventura, o app mostrava só o card HTML, sem exportação. Esta etapa
adiciona um **botão para baixar o resultado em PDF** (tema *dark fantasy*),
exibido logo abaixo do card.

Pontos técnicos:
- **Persistência:** `st.download_button` dispara rerun; a aventura passou a ser
  guardada em `st.session_state` para o resultado não sumir ao baixar.
- **Unicode pt-BR:** PDF usa `fpdf2` + fonte **DejaVu** empacotada em
  `static/fonts/` (acentos e travessões corretos).

## Mudanças
- `requirements.txt` — adiciona `fpdf2`.
- `static/fonts/DejaVuSans.ttf` e `DejaVuSans-Bold.ttf` — fontes Unicode.
- `src/pdf.py` — `build_adventure_pdf(adventure, tom, nivel, duracao) -> bytes`
  (fundo escuro, título dourado, Doom Clock em roxo) e `pdf_filename(title)`.
- `app.py` — gera/persiste a aventura em `session_state`; `_render_result`
  renderiza o card + `st.download_button`; em erro limpa o estado.

## Testes (sem rede)
- `tests/test_pdf.py` — bytes `%PDF`, travessões/acentos, múltiplas páginas, slug.
- `tests/test_app.py` — `session_state` após geração, persistência no rerun, erro
  limpa o estado.

## Fora de escopo
- Multi-sistema (Fase 2). Outros formatos de exportação.

## Verificação
1. `pytest -q` → verde (sem rede).
2. App: gerar aventura → card + botão "Baixar em PDF"; baixar mantém o resultado.
3. PDF: tema escuro, título dourado, acentos/travessões corretos.
