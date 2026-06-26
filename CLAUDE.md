# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`rpg_master_assistent` — an AI co-pilot for RPG Game Masters. It accelerates
worldbuilding, narrative creation, and campaign management **without replacing**
the Game Master.

- **MVP (Phase 1):** adventure generator for **D&D 5e** — the "Narrative Funnel"
  (plot hook, antagonist/Doom Clock, key locations & NPCs) + three-act structure.
- **Phase 2 (future):** multi-system (D&D + Cyberpunk RED) via dynamic prompt
  routing, isolated RAG knowledge bases, and per-system JSON Schemas.
- Source document: `documents/RPG_MASTER_ASSISTENT_DOCUMENT.md`.

> **Status:** structure + tooling in place. AI generation is **not** yet
> implemented — `src/ia_client.py` is a skeleton and `app.py` only shows the form.

## Stack

- Python 3.10+
- Streamlit (web interface — `app.py`)
- Mistral served locally by Ollama via the `ollama` Python library — AI engine
  (no API key; structured output via the `format` JSON Schema parameter)
- `python-dotenv` (environment variables)
- Pydantic models (`src/schemas/`) whose JSON Schema structures the AI responses

## Commands

```bash
# Environment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configuration (set OLLAMA_HOST / OLLAMA_MODEL if needed — no API key required)
cp .env.example .env

# Pull the model on the Ollama host
ollama pull mistral

# Run the application
streamlit run app.py
```

> There is no test suite or linter configured yet.

## Architecture

Intended flow: `app.py` (Streamlit) collects the GM's idea → calls
`src/ia_client.py` → which builds the prompt with `src/prompts.py` and asks the
local Mistral (via Ollama) for a response in the format of `src/schemas/dnd5e.py`
→ the structured result is displayed.

- `app.py` — Streamlit entrypoint; UI and call orchestration.
- `src/config.py` — `load_settings()` reads `.env` and exposes `Settings`
  (`ollama_host` and `ollama_model`); auto-detects the Ollama host on WSL
  (`/etc/resolv.conf`) when `OLLAMA_HOST` is unset.
- `src/ia_client.py` — the **only** layer that knows the AI provider. Class
  `IAClient` with `generate_adventure(idea) -> dict`. The rest of the app talks
  only to this interface (makes it easy to swap/abstract the provider in Phase 2).
- `src/prompts.py` — `SYSTEM_PROMPT` (persona, pt-BR output) and
  `ADVENTURE_PROMPT_TEMPLATE`; comments map the Narrative Funnel and the three acts.
- `src/schemas/` — per-system output structures; `dnd5e.py` holds `ADVENTURE_SCHEMA`.

## Conventions

- **Language:** the interface and generated outputs are in **Portuguese (pt-BR)**.
- **Secrets:** never commit `.env` (already in `.gitignore`); use `.env.example`
  as the template.
- AI-provider-specific details stay isolated in `src/ia_client.py`.
