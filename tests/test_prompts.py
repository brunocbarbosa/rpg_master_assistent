"""Testes dos prompts (src/prompts.py)."""

from __future__ import annotations

from src.prompts import (
    ADVENTURE_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
    format_rules_context,
)


def test_system_prompt_is_ptbr_persona():
    assert "pt-BR" in SYSTEM_PROMPT
    assert "D&D 5" in SYSTEM_PROMPT or "Dungeons & Dragons" in SYSTEM_PROMPT


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
    assert "</regras>" in bloco
    assert bloco.endswith("\n\n")


def test_template_includes_context_block_when_present():
    prompt = ADVENTURE_PROMPT_TEMPLATE.format(
        idea="i", tom="t", nivel="n", duracao="d", contexto="BLOCO_DE_REGRAS\n\n"
    )
    assert "BLOCO_DE_REGRAS" in prompt
