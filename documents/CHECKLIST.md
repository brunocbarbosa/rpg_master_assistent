# Checklist — Troca do provedor de IA: Gemini → Mistral (Ollama local)

## Implementação
- [x] `requirements.txt` — remove `google-genai`, adiciona `ollama`
- [x] `src/config.py` — `Settings(ollama_host, ollama_model)` + auto-detecção WSL
- [x] `src/ia_client.py` — `ollama.Client().chat(..., format=schema)` + retry adaptado
- [x] `.env.example` — `OLLAMA_HOST` / `OLLAMA_MODEL=mistral`
- [x] Docstrings (`app.py`, `src/schemas/dnd5e.py`) + `CLAUDE.md` + `README.md`

## Correções pós-teste (depuração do "não foi possível gerar")
- [x] Tratamento de erro de transporte ampliado (`httpx.RequestError`/`InvalidURL`/
      `ollama.RequestError`) → URL malformada dá msg clara, não a genérica
- [x] Auto-detecção do host corrigida: usa o **gateway padrão** (`/proc/net/route`),
      não o nameserver do resolv.conf
- [x] `timeout` no `ollama.Client` (connect=5s, read=600s) → falha rápido se o
      Ollama estiver inacessível, em vez de travar o app
- [x] `.env` — typo `hhttp://` corrigido; `OLLAMA_HOST` comentado (usa auto-detecção)

## Testes (sem rede)
- [x] `tests/test_ia_client.py` reescrito para o Ollama
- [x] `tests/test_config.py` reescrito (host/modelo via env, defaults)
- [x] `tests/test_app.py` atualizado (`OLLAMA_MODEL`)
- [x] `pytest -q` passando (23 testes)

## Verificação
- [ ] `ollama pull mistral` no host Windows + `curl http://<host>:11434/api/tags` ok
- [ ] Geração ponta a ponta no app real (card estruturado em pt-BR)
- [ ] Ollama desligado → mensagem clara de erro (sem stack trace)

## Git
- [ ] Commit / push / PR — **somente quando o usuário pedir**
