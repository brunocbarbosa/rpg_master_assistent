# Plano — Troca do provedor de IA: Gemini → Mistral (Ollama local)

## Contexto

A geração de aventuras passava pelo **Google Gemini** (`google-genai`, com chave de
API). Esta etapa troca o motor de IA para o **Mistral rodando localmente no Ollama**,
via a biblioteca oficial `ollama`. Ganhos: sem chave de API, sem custo, dados na
máquina.

Ambiente: o Ollama roda **no host Windows** e o app no **WSL2** — `localhost:11434`
não responde a partir do WSL, então o host precisa apontar para o IP do Windows.

O provedor já estava isolado em `src/ia_client.py`, então a troca é localizada. O
Ollama suporta saída estruturada via `format` (JSON Schema), então o schema Pydantic
`Adventure` e o parsing estruturado foram **mantidos**.

## Mudanças
- `requirements.txt` — remove `google-genai`, adiciona `ollama`.
- `src/config.py` — `Settings(ollama_host, ollama_model)`; sem chave de API.
  `_default_ollama_host()` detecta o IP do host Windows via `/etc/resolv.conf` (WSL),
  com fallback para `localhost`. `OLLAMA_HOST` do `.env` tem prioridade.
- `src/ia_client.py` — `ollama.Client(host=...).chat(model, messages, format=schema)`;
  parsing com `Adventure.model_validate_json(...)`. Retry em `ollama.ResponseError`
  5xx; erro de conexão → mensagem clara imediata.
- `.env.example` — `OLLAMA_HOST` (comentado) e `OLLAMA_MODEL=mistral`.
- Docstrings de `app.py` e `src/schemas/dnd5e.py`; `CLAUDE.md` e `README.md`.

## Testes (sem rede)
- `tests/test_ia_client.py` — mocks reescritos para o Ollama (`.chat` → `.message.content`),
  cobrindo sucesso, JSON inválido, erro genérico, erro de conexão, retry 5xx e overload.
- `tests/test_config.py` — host via env, defaults (auto-detecção), constante do modelo.
- `tests/test_app.py` — `setenv` atualizado para `OLLAMA_MODEL`.

## Fora de escopo
- Multi-sistema (Fase 2). Parametrizar temperatura/opções do modelo.

## Verificação
1. `pytest -q` → verde (sem rede).
2. `ollama pull mistral` no host; `curl http://<host>:11434/api/tags` responde.
3. App: gerar aventura → card estruturado (título, funil, 3 atos) em pt-BR.
4. Ollama desligado → mensagem clara orientando a verificar o serviço/`OLLAMA_HOST`.
