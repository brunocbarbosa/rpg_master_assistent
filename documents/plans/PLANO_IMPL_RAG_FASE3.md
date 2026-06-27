# RAG Fase 3 (consulta na geração) — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recuperar trechos das regras de D&D 5e do ChromaDB a partir da ideia do mestre e injetá-los no prompt de geração, de forma best-effort.

**Architecture:** Novo `Retriever` (`src/rag/retrieve.py`) consulta a coleção `dnd_5e_knowledge`; `src/prompts.py` ganha um bloco de contexto opcional; `src/ia_client.py` orquestra (monta a query, recupera, injeta) e segue como única camada de provider. Falha de RAG → gera sem contexto.

**Tech Stack:** Python 3.10+, chromadb 1.5.9 (`HttpClient`), Ollama embeddings (`nomic-embed-text`), pytest.

## Global Constraints

- Idioma do código/comentários/saída: **pt-BR**.
- Nenhum teste acessa a rede — Ollama/Chroma sempre mockados/injetados.
- RAG é **reforço**: qualquer falha de recuperação retorna `[]` e a geração segue.
- `src/ia_client.py` continua a **única** camada que conhece o provider de IA.
- Coleção: `dnd_5e_knowledge` (constante já definida em `src/rag/ingest.py`).
- top-k padrão: `DEFAULT_TOP_K = 5`.
- **Git:** este projeto **não comita sem pedido explícito do usuário**. Os passos
  "Commit" abaixo só devem ser executados quando o usuário autorizar; caso
  contrário, agrupe as mudanças e peça antes.

---

### Task 1: Bloco de contexto no prompt (`src/prompts.py`)

**Files:**
- Modify: `src/prompts.py`
- Test: `tests/test_prompts.py`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `format_rules_context(chunks: list[str]) -> str` — `""` se vazio; senão um
    bloco terminado em `"\n\n"` contendo `<regras>…</regras>`.
  - `ADVENTURE_PROMPT_TEMPLATE` passa a exigir o parâmetro de formatação
    `contexto` (placeholder `{contexto}` no início).

- [ ] **Step 1: Escrever os testes que falham**

Em `tests/test_prompts.py`, ajustar o import e o teste existente e adicionar os novos:

```python
from src.prompts import (
    ADVENTURE_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
    format_rules_context,
)


def test_adventure_template_injects_all_params():
    prompt = ADVENTURE_PROMPT_TEMPLATE.format(
        idea="Um sino amaldiçoado",
        tom="Sombrio",
        nivel="1–4",
        duracao="One-shot",
        contexto="",
    )
    assert "Um sino amaldiçoado" in prompt
    assert "Sombrio" in prompt
    assert "1–4" in prompt
    assert "One-shot" in prompt


def test_format_rules_context_empty_returns_empty():
    assert format_rules_context([]) == ""


def test_format_rules_context_includes_chunks():
    bloco = format_rules_context(["Regra A", "Regra B"])
    assert "Regra A" in bloco
    assert "Regra B" in bloco
    assert "<regras>" in bloco
    assert bloco.endswith("\n\n")


def test_template_includes_context_block_when_present():
    prompt = ADVENTURE_PROMPT_TEMPLATE.format(
        idea="i", tom="t", nivel="n", duracao="d", contexto="BLOCO_DE_REGRAS\n\n"
    )
    assert "BLOCO_DE_REGRAS" in prompt
```

- [ ] **Step 2: Rodar para ver falhar**

Run: `pytest tests/test_prompts.py -q`
Expected: FAIL — `ImportError: cannot import name 'format_rules_context'`.

- [ ] **Step 3: Implementar em `src/prompts.py`**

Adicionar o placeholder `{contexto}` no início do template e a função. O template fica:

```python
# Template do prompt do usuário — injeta a ideia central e os ajustes do Mestre.
# `{contexto}` recebe (opcionalmente) o bloco de regras recuperado via RAG.
ADVENTURE_PROMPT_TEMPLATE = """
{contexto}Crie uma aventura de D&D 5e com base nestes parâmetros:

- Ideia central: {idea}
- Tom: {tom}
- Nível dos personagens: {nivel}
- Duração pretendida: {duracao}

Gere a aventura seguindo o Funil Narrativo e a estrutura de 3 atos, calibrando a
escala e a complexidade para o nível e a duração indicados.
""".strip()


def format_rules_context(chunks: list[str]) -> str:
    """Formata os trechos de regras recuperados (RAG) em um bloco para o prompt.

    Retorna ``""`` quando não há trechos — assim o bloco simplesmente desaparece
    do prompt (degradação graciosa). Quando há, devolve um bloco terminado em
    ``"\\n\\n"`` para separar do restante do template.
    """
    if not chunks:
        return ""
    regras = "\n---\n".join(chunk.strip() for chunk in chunks)
    return (
        "Use as REGRAS OFICIAIS de D&D 5e abaixo como REFERÊNCIA para manter "
        "coerência mecânica (não as copie literalmente):\n"
        f"<regras>\n{regras}\n</regras>\n\n"
    )
```

- [ ] **Step 4: Rodar para ver passar**

Run: `pytest tests/test_prompts.py -q`
Expected: PASS (4 testes).

- [ ] **Step 5: Commit** (somente se o usuário autorizar)

```bash
git add src/prompts.py tests/test_prompts.py
git commit -m "feat(rag): bloco de contexto de regras no prompt de geração"
```

---

### Task 2: `Retriever` (`src/rag/retrieve.py`)

**Files:**
- Create: `src/rag/retrieve.py`
- Test: `tests/test_rag_retrieve.py`

**Interfaces:**
- Consumes: `COLLECTION_NAME` de `src/rag/ingest.py`; `OllamaEmbeddingFunction`
  de `src/rag/embeddings.py`; `Settings` de `src/config.py`.
- Produces:
  - `DEFAULT_TOP_K = 5`
  - `class Retriever`: `__init__(self, settings: Settings)` (não conecta);
    `retrieve(self, query: str, n_results: int = DEFAULT_TOP_K) -> list[str]`.

- [ ] **Step 1: Escrever os testes que falham**

Criar `tests/test_rag_retrieve.py`:

```python
"""Testes da consulta de RAG (src/rag/retrieve.py) — sem rede."""

from __future__ import annotations

from src.config import Settings
from src.rag.retrieve import DEFAULT_TOP_K, Retriever


class _FakeCollection:
    """Coleção fake: devolve documentos fixos ou levanta um erro em ``query``."""

    def __init__(self, documents=None, error=None):
        self._documents = documents
        self._error = error
        self.last_query = None

    def query(self, query_texts, n_results):
        self.last_query = {"query_texts": query_texts, "n_results": n_results}
        if self._error is not None:
            raise self._error
        return {"documents": [self._documents]}


def _retriever_with(collection) -> Retriever:
    retriever = Retriever(
        Settings(ollama_host="http://x:11434", ollama_model="mistral")
    )
    retriever._collection = collection  # injeta, evita conectar
    return retriever


def test_retrieve_returns_documents():
    retriever = _retriever_with(_FakeCollection(documents=["trecho A", "trecho B"]))
    assert retriever.retrieve("consulta") == ["trecho A", "trecho B"]


def test_retrieve_passes_query_and_n_results():
    fake = _FakeCollection(documents=[])
    retriever = _retriever_with(fake)
    retriever.retrieve("minha busca", n_results=3)
    assert fake.last_query == {"query_texts": ["minha busca"], "n_results": 3}


def test_retrieve_default_top_k():
    fake = _FakeCollection(documents=[])
    retriever = _retriever_with(fake)
    retriever.retrieve("q")
    assert fake.last_query["n_results"] == DEFAULT_TOP_K


def test_retrieve_swallows_errors_returns_empty():
    retriever = _retriever_with(_FakeCollection(error=RuntimeError("chroma fora")))
    assert retriever.retrieve("q") == []
```

- [ ] **Step 2: Rodar para ver falhar**

Run: `pytest tests/test_rag_retrieve.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.rag.retrieve'`.

- [ ] **Step 3: Implementar `src/rag/retrieve.py`**

```python
"""Consulta da base de conhecimento (RAG) na geração.

Recupera trechos relevantes das regras na coleção ``dnd_5e_knowledge`` do
ChromaDB para enriquecer o prompt. É best-effort: qualquer falha (Chroma fora,
coleção ausente, embed model não instalado) devolve uma lista vazia — a geração
segue sem o contexto das regras.
"""

from __future__ import annotations

import warnings

import chromadb

from src.config import Settings
from src.rag.embeddings import OllamaEmbeddingFunction
from src.rag.ingest import COLLECTION_NAME

DEFAULT_TOP_K = 5


class Retriever:
    """Recupera trechos de regras do ChromaDB (best-effort, conexão lazy)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._collection = None  # conectado sob demanda e cacheado

    def _get_collection(self):
        if self._collection is None:
            client = chromadb.HttpClient(
                host=self._settings.chroma_host, port=self._settings.chroma_port
            )
            embedding_function = OllamaEmbeddingFunction(
                host=self._settings.ollama_host,
                model=self._settings.ollama_embed_model,
            )
            self._collection = client.get_collection(
                name=COLLECTION_NAME, embedding_function=embedding_function
            )
        return self._collection

    def retrieve(self, query: str, n_results: int = DEFAULT_TOP_K) -> list[str]:
        """Devolve até ``n_results`` trechos relevantes; ``[]`` em qualquer falha."""
        try:
            collection = self._get_collection()
            results = collection.query(query_texts=[query], n_results=n_results)
            documents = results.get("documents") or [[]]
            return list(documents[0])
        except Exception as exc:  # noqa: BLE001 — RAG é reforço, nunca quebra a geração
            warnings.warn(f"RAG indisponível, gerando sem contexto: {exc}")
            self._collection = None  # força reconexão na próxima tentativa
            return []
```

- [ ] **Step 4: Rodar para ver passar**

Run: `pytest tests/test_rag_retrieve.py -q`
Expected: PASS (4 testes).

- [ ] **Step 5: Commit** (somente se o usuário autorizar)

```bash
git add src/rag/retrieve.py tests/test_rag_retrieve.py
git commit -m "feat(rag): Retriever best-effort da coleção dnd_5e_knowledge"
```

---

### Task 3: Integração na geração (`src/ia_client.py`)

**Files:**
- Modify: `src/ia_client.py`
- Test: `tests/test_ia_client.py`

**Interfaces:**
- Consumes: `Retriever` (Task 2); `format_rules_context` e
  `ADVENTURE_PROMPT_TEMPLATE` (Task 1).
- Produces: `IAClient.__init__(self, settings, retriever: Retriever | None = None)`;
  `generate_adventure` monta `query = f"{idea}\nTom: {tom}\nNível: {nivel}"` e
  injeta o contexto no prompt.

- [ ] **Step 1: Atualizar/escrever os testes que falham**

Em `tests/test_ia_client.py`, adicionar o fake de retriever, atualizar
`_make_client` e adicionar os novos testes:

```python
class _FakeRetriever:
    """Retriever fake: registra a query e devolve trechos fixos."""

    def __init__(self, chunks=None):
        self.chunks = chunks if chunks is not None else []
        self.last_query = None

    def retrieve(self, query, n_results=5):
        self.last_query = query
        return self.chunks


def _make_client(retriever=None) -> IAClient:
    return IAClient(
        Settings(ollama_host="http://x:11434", ollama_model="mistral"),
        retriever=retriever if retriever is not None else _FakeRetriever(),
    )


def test_query_uses_idea_tom_and_nivel(monkeypatch):
    content = _fake_adventure().model_dump_json()
    _patch_client(monkeypatch, _FakeResponse(content))
    retriever = _FakeRetriever()
    client = _make_client(retriever)

    client.generate_adventure("cidade flutuante", "Sombrio", "5–10", "One-shot")

    assert "cidade flutuante" in retriever.last_query
    assert "Sombrio" in retriever.last_query
    assert "5–10" in retriever.last_query


def test_context_injected_when_chunks(monkeypatch):
    content = _fake_adventure().model_dump_json()
    fake = _patch_client(monkeypatch, _FakeResponse(content))
    client = _make_client(_FakeRetriever(chunks=["Regra do grimório"]))

    client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")

    user_msg = {m["role"]: m["content"] for m in fake.last_kwargs["messages"]}["user"]
    assert "Regra do grimório" in user_msg
    assert "<regras>" in user_msg


def test_no_context_block_when_no_chunks(monkeypatch):
    content = _fake_adventure().model_dump_json()
    fake = _patch_client(monkeypatch, _FakeResponse(content))
    client = _make_client(_FakeRetriever(chunks=[]))

    client.generate_adventure("ideia", "Sombrio", "1–4", "One-shot")

    user_msg = {m["role"]: m["content"] for m in fake.last_kwargs["messages"]}["user"]
    assert "<regras>" not in user_msg
```

Nota: os testes existentes que chamam `_make_client()` sem argumento continuam
válidos — recebem um `_FakeRetriever()` vazio (offline).

- [ ] **Step 2: Rodar para ver falhar**

Run: `pytest tests/test_ia_client.py -q`
Expected: FAIL — `IAClient.__init__` não aceita `retriever` (TypeError).

- [ ] **Step 3: Implementar em `src/ia_client.py`**

Atualizar os imports no topo:

```python
from src.config import Settings
from src.prompts import (
    ADVENTURE_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
    format_rules_context,
)
from src.rag.retrieve import Retriever
from src.schemas.dnd5e import Adventure
```

Atualizar o `__init__`:

```python
    def __init__(self, settings: Settings, retriever: Retriever | None = None) -> None:
        self._settings = settings
        self._client = ollama.Client(host=settings.ollama_host, timeout=_TIMEOUT)
        self._retriever = retriever or Retriever(settings)
```

No `generate_adventure`, substituir a montagem do prompt por:

```python
        # RAG (best-effort): recupera regras relevantes e injeta como contexto.
        query = f"{idea}\nTom: {tom}\nNível: {nivel}"
        contexto = format_rules_context(self._retriever.retrieve(query))
        prompt = ADVENTURE_PROMPT_TEMPLATE.format(
            idea=idea, tom=tom, nivel=nivel, duracao=duracao, contexto=contexto
        )
```

- [ ] **Step 4: Rodar para ver passar**

Run: `pytest tests/test_ia_client.py -q`
Expected: PASS (todos, incluindo os 3 novos).

- [ ] **Step 5: Commit** (somente se o usuário autorizar)

```bash
git add src/ia_client.py tests/test_ia_client.py
git commit -m "feat(rag): injeta contexto recuperado no prompt da geração"
```

---

### Task 4: Documentação + verificação final

**Files:**
- Modify: `documents/plans/CHECKLIST_RAG.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: tudo das Tasks 1–3. Produces: nada (docs).

- [ ] **Step 1: Marcar a Fase 3 no checklist**

Em `documents/plans/CHECKLIST_RAG.md`, na seção `## Fase 3 — Consulta (RAG na geração)`, marcar:

```markdown
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
```

- [ ] **Step 2: Atualizar `CLAUDE.md`**

Na seção Stack, trocar a frase sobre RAG para indicar que a consulta foi
implementada:

```markdown
  (`nomic-embed-text`). **Ingestion** (`python -m src.rag.ingest`) and **query**
  (RAG on generation, `src/rag/retrieve.py`) are implemented — see
  `documents/plans/CHECKLIST_RAG.md`.
```

Na seção Architecture, no item `src/rag/`, acrescentar a frase final:

```markdown
  `retrieve.py` (`Retriever`) consulta a coleção e devolve trechos para o
  `IAClient` injetar no prompt (best-effort: falha de RAG → gera sem contexto).
```

- [ ] **Step 3: Rodar a suíte completa**

Run: `pytest -q`
Expected: PASS — todos os testes (antigos + novos), sem rede.

- [ ] **Step 4: Commit** (somente se o usuário autorizar)

```bash
git add documents/plans/CHECKLIST_RAG.md CLAUDE.md
git commit -m "docs(rag): marca Fase 3 (consulta) e atualiza CLAUDE.md"
```

---

## Self-Review (preenchido)

- **Cobertura do spec:** degradação graciosa (Task 2 retrieve → `[]`); query
  ideia+tom+nível (Task 3); top-k=5 (Task 2 `DEFAULT_TOP_K`); injeção no prompt
  (Tasks 1+3); testes sem rede (Tasks 1–3); docs (Task 4). Tudo coberto.
- **Sem placeholders:** todo passo tem código/comando concreto.
- **Consistência de tipos:** `format_rules_context(list[str]) -> str`,
  `Retriever.retrieve(str, int) -> list[str]`, `IAClient.__init__(settings,
  retriever=None)` — usados de forma idêntica entre tasks.
