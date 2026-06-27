# Design — RAG Fase 3: consulta das regras na geração

## Contexto

A Fase 2 ingeriu os 3 livros de D&D 5e na coleção `dnd_5e_knowledge` do ChromaDB
(`src/rag/ingest.py` + `src/rag/embeddings.py`). Falta usar essa base na geração:
recuperar trechos relevantes a partir da ideia do mestre e injetá-los no prompt,
para a IA manter coerência com as regras. O `src/ia_client.py` permanece a única
camada que conhece o provedor de IA.

## Decisões confirmadas

- **Degradação graciosa:** RAG é reforço, não bloqueio. Se a recuperação falhar
  (Chroma fora, coleção ausente/vazia, embed model não instalado), a geração
  segue **sem** contexto — o app nunca quebra por causa do RAG.
- **Texto da busca:** `ideia + tom + nível` (busca mais contextualizada).
- **Quantidade:** top‑k = **5** trechos, exposto como constante configurável.
- **Sem filtro por `book_category`** neste passo (busca em toda a coleção). O
  filtro por metadados fica como evolução futura (já há suporte de metadados).

## Componentes

### 1. `src/rag/retrieve.py` — `Retriever` (novo; isola o RAG)

- `__init__(settings: Settings)` — guarda `settings`; **não conecta** (a
  construção nunca falha). Conexão é lazy e cacheada.
- `DEFAULT_TOP_K = 5` (constante de módulo).
- `retrieve(query: str, n_results: int = DEFAULT_TOP_K) -> list[str]`:
  1. Conecta (lazy) ao Chroma via `chromadb.HttpClient(host, port)` e obtém a
     coleção `dnd_5e_knowledge` com a `OllamaEmbeddingFunction(settings)`.
  2. `collection.query(query_texts=[query], n_results=n_results)`.
  3. Devolve a lista de textos (`results["documents"][0]`).
  - **Best‑effort:** envolve tudo em `try/except` amplo → qualquer falha retorna
    `[]` (e registra um aviso via `warnings`/log leve, sem poluir a saída).
- Coleção e cliente ficam em atributos cacheados (`self._collection`), criados na
  primeira chamada bem-sucedida.

### 2. `src/prompts.py` — injeção do contexto

- `ADVENTURE_PROMPT_TEMPLATE` ganha um placeholder `{contexto}` no início.
- Nova constante/auxiliar `format_rules_context(chunks: list[str]) -> str`:
  - Se `chunks` vazio → retorna `""` (o bloco some do prompt).
  - Senão → monta um bloco instruindo o uso das regras como referência (não
    copiar literalmente), com os trechos delimitados (ex.: dentro de
    `<regras>…</regras>`, separados por `\n---\n`).

### 3. `src/ia_client.py` — orquestração

- `IAClient.__init__(self, settings, retriever: Retriever | None = None)` →
  `self._retriever = retriever or Retriever(settings)` (**injetável** p/ testes).
- Em `generate_adventure`:
  1. `query = f"{idea}\nTom: {tom}\nNível: {nivel}"`.
  2. `chunks = self._retriever.retrieve(query)`.
  3. `contexto = format_rules_context(chunks)`.
  4. `prompt = ADVENTURE_PROMPT_TEMPLATE.format(idea=…, tom=…, nivel=…,
     duracao=…, contexto=contexto)`.
  - Retry, parse e tratamento de erro da geração permanecem inalterados.

## Fluxo de dados

`app.py` → `IAClient.generate_adventure(idea, tom, nivel, duracao)`
→ `Retriever.retrieve(query)` → trechos
→ `format_rules_context` → bloco de contexto
→ `ADVENTURE_PROMPT_TEMPLATE` → Ollama `chat` → parse Pydantic → `dict`.

## Tratamento de erros

- `Retriever.retrieve` captura **todas** as exceções e retorna `[]` (degradação
  graciosa). Não propaga falha de RAG para o app.
- O fluxo de erro da geração (`IAClientError`, retry/backoff em 5xx, mensagens de
  conexão) continua exatamente como hoje.

## Testes (sem rede)

- **`tests/test_rag_retrieve.py`** (novo):
  - `retrieve()` com coleção fake injetada → devolve os textos esperados.
  - Falha ao conectar/consultar (fake levanta exceção) → retorna `[]`.
  - Respeita `n_results` repassado à `query`.
- **`tests/test_ia_client.py`** (atualizar):
  - `_make_client` injeta um `Retriever` stub (retorna `[]` ou lista fixa) para
    manter os testes **offline** (a promessa do arquivo permanece válida).
  - Novo teste: query enviada = `ideia + tom + nível`.
  - Novo teste: bloco de contexto entra no prompt quando há trechos e **some**
    quando a lista é vazia.
- **`tests/test_prompts.py`** (atualizar/novo): `format_rules_context` retorna
  `""` para lista vazia e inclui os trechos quando há conteúdo.

## Arquivos

- **Novos:** `src/rag/retrieve.py`, `tests/test_rag_retrieve.py`.
- **Modificados:** `src/prompts.py`, `src/ia_client.py`, `tests/test_ia_client.py`,
  `tests/test_prompts.py`, `documents/plans/CHECKLIST_RAG.md`, `CLAUDE.md`.

## Verificação

1. `pytest -q` — toda a suíte passa (incluindo os novos testes, sem rede).
2. Com Chroma no ar + coleção ingerida + `nomic-embed-text` instalado:
   `streamlit run app.py` → gerar uma aventura → o prompt enviado ao Ollama
   contém o bloco `<regras>` (validar via log/inspeção).
3. Com Chroma **desligado**: gerar uma aventura → funciona normalmente, sem o
   bloco de regras (degradação graciosa).

## Fora de escopo

- Filtro/roteamento por `book_category` ou `rpg_system` na consulta.
- Reranking, deduplicação semântica, citações de fonte no resultado.
- Multi-sistema (Cyberpunk RED) — Fase futura.
