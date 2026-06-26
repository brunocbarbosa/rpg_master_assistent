"""Testes dos prompts (src/prompts.py)."""

from __future__ import annotations

from src.prompts import ADVENTURE_PROMPT_TEMPLATE, SYSTEM_PROMPT


def test_system_prompt_is_ptbr_persona():
    assert "pt-BR" in SYSTEM_PROMPT
    assert "D&D 5" in SYSTEM_PROMPT or "Dungeons & Dragons" in SYSTEM_PROMPT


def test_adventure_template_injects_all_params():
    prompt = ADVENTURE_PROMPT_TEMPLATE.format(
        idea="Um sino amaldiçoado",
        tom="Sombrio",
        nivel="1–4",
        duracao="One-shot",
    )
    assert "Um sino amaldiçoado" in prompt
    assert "Sombrio" in prompt
    assert "1–4" in prompt
    assert "One-shot" in prompt
