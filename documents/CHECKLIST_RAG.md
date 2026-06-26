# Checklist — Base de conhecimento (RAG) com ChromaDB

Objetivo: dar à IA acesso às **regras** dos sistemas de RPG via RAG. As regras de
um PDF são extraídas, divididas em trechos, vetorizadas (embeddings) e guardadas
no **ChromaDB**, para serem consultadas durante a geração das aventuras.

Embeddings: `nomic-embed-text` servido pelo Ollama (sem API).

## Fase 1 — Infraestrutura
- [x] `docker-compose.yml` — servidor ChromaDB (`chromadb/chroma:1.5.9`), porta
      8000, persistência em `./data/chroma`
- [x] `requirements.txt` — `chromadb==1.5.9` (casado com a imagem), `PyPDF2`,
      `langchain-text-splitters`
- [x] `.gitignore` — ignora `data/` (índices) e `documents/regras/` (PDFs)
- [x] `src/config.py` + `.env.example` — `CHROMA_HOST`, `CHROMA_PORT`,
      `OLLAMA_EMBED_MODEL`
- [x] Verificação: `docker compose up -d` + heartbeat OK + imports das libs
      (nesta máquina a 8000 está ocupada pelo portainer → usamos `CHROMA_PORT=8001`)

## Fase 2 — Ingestão do PDF (quando o PDF chegar)
- [ ] Pasta `documents/regras/` com o PDF de origem
- [ ] `ollama pull nomic-embed-text` no host
- [ ] Extração do texto (PyPDF2)
- [ ] Divisão em trechos (`langchain-text-splitters` —
      `RecursiveCharacterTextSplitter`, com overlap)
- [ ] `EmbeddingFunction` via Ollama (`ollama.Client(...).embeddings(...)`)
- [ ] Gravação na coleção do Chroma (`HttpClient`) com metadados (sistema, fonte)
- [ ] Script/CLI de ingestão idempotente (reprocessar sem duplicar)

## Fase 3 — Consulta (RAG na geração)
- [ ] Recuperar trechos relevantes a partir da ideia do GM
- [ ] Injetar o contexto recuperado no prompt (`src/prompts.py`)
- [ ] Integrar em `src/ia_client.py` (provider permanece isolado nessa camada)
- [ ] Testes da camada de RAG (sem rede / com mocks)

## Git
- [ ] Commit / push / PR — **somente quando o usuário pedir**
