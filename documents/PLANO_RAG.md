# Plano — Infraestrutura RAG: ChromaDB + ingestão de PDF

## Contexto

O `rpg_master_assistent` gera aventuras de D&D 5e com IA (Ollama/Mistral local).
Hoje não há base de conhecimento: a IA não consulta as regras do sistema. O
`RPG_MASTER_ASSISTENT_DOCUMENT.md` já prevê, na Fase 2, **"Isolated Knowledge
Bases (RAG)"** para separar as regras por sistema.

Este trabalho monta a **infraestrutura de RAG** (sem ainda ingerir conteúdo): um
servidor **ChromaDB** rodando via Docker Compose para guardar as regras
vetorizadas, mais as bibliotecas de leitura/divisão de PDF. O PDF de regras será
enviado depois — a ingestão propriamente dita (extrair → dividir → embeddar →
gravar) virá num passo seguinte, mas o plano já deixa a estratégia definida.

Decisões confirmadas com o usuário:
- Branch: **`feature/chromadb-rag`** (a partir de `development`)
- Adicionar o cliente Python **`chromadb`** ao `requirements.txt`
- Embeddings via **Ollama `nomic-embed-text`** (reaproveita o Ollama já usado, sem API)

## Escopo desta entrega

Infra + dependências + configuração. **Não** inclui a ingestão do PDF nem código
de consulta (RAG na geração) — isso fica para quando o PDF chegar.

## Passos

### 1. Branch
Criar `feature/chromadb-rag` a partir de `development`.

### 2. `docker-compose.yml` (novo, na raiz)
Serviço único do ChromaDB com persistência:
- imagem `chromadb/chroma` **pinada** numa versão (usada: `chromadb/chroma:1.5.9`)
- porta publicada via `${CHROMA_PORT:-8000}:8000` (configurável; default 8000)
- `environment: IS_PERSISTENT=TRUE`, `PERSIST_DIRECTORY=/data`,
  `ANONYMIZED_TELEMETRY=FALSE`
- volume `./data/chroma:/data` para persistir os índices entre `up`/`down`
- `restart: unless-stopped`

Importante: a **versão do cliente `chromadb` no `requirements.txt` deve casar com
a tag da imagem** (Chroma exige compatibilidade client/server). Hoje: `1.5.9`
nas duas pontas.

### 3. `requirements.txt`
Acrescentar (mantendo o estilo atual, porém fixando `chromadb` por causa do
casamento de versão com a imagem):
- `chromadb==1.5.9`
- `PyPDF2`
- `langchain-text-splitters`

### 4. `.gitignore`
Adicionar `data/` (dados persistidos do Chroma) e a pasta de PDFs de origem
(`documents/regras/`), para não versionar binários/índices pesados.
Atenção: comentários em `.gitignore` precisam ficar em **linha própria**
(o `#` inline não funciona).

### 5. Configuração (`src/config.py` + `.env.example`)
Estender `Settings` (dataclass) com campos do Chroma e do modelo de embeddings,
seguindo o padrão já existente de `load_settings()`:
- `chroma_host` (env `CHROMA_HOST`, default `localhost`)
- `chroma_port` (env `CHROMA_PORT`, default `8000`)
- `ollama_embed_model` (env `OLLAMA_EMBED_MODEL`, default `nomic-embed-text`)

Os novos campos têm default no dataclass para não quebrar construções existentes
de `Settings` (ex.: nos testes).

Observação: o Chroma roda como container **local** (WSL) → `localhost` é o
correto, diferente do Ollama, que aponta para o host Windows via gateway. Manter
a auto-detecção de gateway **apenas** para o Ollama.

Atualizar `.env.example` documentando `CHROMA_HOST`, `CHROMA_PORT` e
`OLLAMA_EMBED_MODEL`.

### 6. Documentação
- `CLAUDE.md`: atualizar Stack/Commands/Architecture citando ChromaDB (Docker),
  PyPDF2, langchain-text-splitters e o pipeline de RAG previsto.
- Criar `documents/CHECKLIST_RAG.md` com a checklist desta fase (infra → ingestão
  → consulta), marcando o que for concluído — conforme o fluxo de checklist do
  projeto.

## Embeddings (definido agora, implementado na ingestão)
Usar `nomic-embed-text` no Ollama. Pré-requisito operacional:
`ollama pull nomic-embed-text` no host. Na ingestão, criar uma
`EmbeddingFunction` que chame `ollama.Client(host=...).embeddings(...)` e
registrá-la na coleção do Chroma. (Fora do escopo desta entrega.)

## Arquivos
- **Novos:** `docker-compose.yml`, `documents/CHECKLIST_RAG.md`,
  `documents/PLANO_RAG.md`
- **Modificados:** `requirements.txt`, `.gitignore`, `src/config.py`,
  `.env.example`, `CLAUDE.md`

## Verificação
1. `docker compose up -d` → container do Chroma sobe sem erro.
2. `curl http://localhost:<CHROMA_PORT>/api/v2/heartbeat` retorna um nanosegundo
   (servidor no ar).
3. Em Python: `pip install -r requirements.txt`, depois
   `chromadb.HttpClient(host="localhost", port=<CHROMA_PORT>).heartbeat()`
   responde — e a versão do cliente casa com a do servidor (sem warning de
   incompatibilidade).
4. `python -c "import PyPDF2, langchain_text_splitters"` sem erro.
5. `docker compose down && up` → dados em `./data/chroma` persistem.
6. `pytest -q` continua passando (testes atuais não devem quebrar com os novos
   campos de `Settings`).

## Notas de execução (ambiente do usuário)
- A porta **8000 já estava ocupada pelo `portainer`** nesta máquina; por isso o
  Chroma local roda na **8001** (`CHROMA_PORT=8001` no `.env`). O default do
  repositório permanece 8000 para outros ambientes.
- Verificação concluída com sucesso: heartbeat, cliente↔servidor sem mismatch
  (`1.5.9`), persistência sobrevivendo a `down/up`, e `pytest` (23 passed).
