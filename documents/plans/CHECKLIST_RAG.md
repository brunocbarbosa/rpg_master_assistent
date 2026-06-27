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

## Fase 2 — Ingestão dos PDFs
PDFs em `documents/books/dnd_5e/` (3 livros). Coleção única `dnd_5e_knowledge`.
Código em `src/rag/` (`embeddings.py`, `ingest.py`); rodar via
`python -m src.rag.ingest` (`--rebuild` apaga a coleção antes).
- [x] Extração do texto (PyPDF2) dos 3 PDFs:
      `dnd_5e_master_guide.pdf`, `dnd_5e_monsters_manual.pdf`,
      `dnd_5e_player_book.pdf` — `src/rag/ingest.py:extract_text`
- [x] Divisão em trechos (`langchain-text-splitters` —
      `RecursiveCharacterTextSplitter`, `chunk_size=1000`, `chunk_overlap=200`)
      — `split_text`
- [x] `OllamaEmbeddingFunction` via Ollama (`client.embed(...)`) —
      `src/rag/embeddings.py`
- [x] Gravação na coleção `dnd_5e_knowledge` (`HttpClient`) com metadados por
      chunk: `pdf_name`, `rpg_system` (`dnd_5e`),
      `book_category` (`master_guide` | `monsters_manual` | `player_book`)
- [x] Script/CLI de ingestão idempotente (IDs determinísticos via
      `sha1(pdf_name:índice)` + `upsert` — reprocessar sem duplicar)
- [x] Testes sem rede (`tests/test_rag_ingest.py`, `tests/test_rag_embeddings.py`)
- [ ] **Rodar a ingestão real** (pendente do usuário): `ollama pull nomic-embed-text`
      no host + `docker compose up -d` → `python -m src.rag.ingest`

## Fase 3 — Consulta (RAG na geração)
Código em `src/rag/retrieve.py` + integração em `src/ia_client.py`.
- [x] Recuperar trechos relevantes a partir da ideia do GM (`Retriever.retrieve`,
      query = ideia + tom + nível, top-k=5)
- [x] Injetar o contexto recuperado no prompt (`format_rules_context` em
      `src/prompts.py`)
- [x] Integrar em `src/ia_client.py` (provider permanece isolado; `Retriever`
      injetável)
- [x] Testes da camada de RAG (sem rede / com mocks): `tests/test_rag_retrieve.py`,
      novos casos em `tests/test_ia_client.py` e `tests/test_prompts.py`
- [ ] Validação manual: `streamlit run app.py` com Chroma no ar + coleção ingerida

## Git
- [ ] Commit / push / PR — **somente quando o usuário pedir**
