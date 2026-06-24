"""Estruturas de dados (schema) para saídas de Dungeons & Dragons 5e.

Define o formato estruturado que o modelo de IA deve seguir ao gerar uma
aventura, garantindo um processamento consistente da resposta (Funil Narrativo
+ 3 atos). O JSON Schema destes modelos Pydantic é passado como ``format`` na
chamada ao Ollama (ver ``src/ia_client.py``).

Os nomes dos campos ficam em inglês (estáveis para o schema); os textos gerados
e as descrições que guiam o modelo ficam em pt-BR.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Antagonist(BaseModel):
    """Força motriz do conflito + ameaça (Doom Clock)."""

    description: str = Field(
        description="Descrição do antagonista: quem é, motivações e métodos."
    )
    doom_clock: str = Field(
        description="O que acontece, de forma crescente, se os jogadores falharem."
    )


class Location(BaseModel):
    """Local-chave da aventura."""

    name: str = Field(description="Nome do local.")
    description: str = Field(
        description="Descrição breve do ambiente e sua importância na trama."
    )


class NPC(BaseModel):
    """Personagem não-jogador importante."""

    name: str = Field(description="Nome do NPC.")
    description: str = Field(
        description="Papel do NPC e as informações cruciais que ele carrega."
    )


class NarrativeFunnel(BaseModel):
    """Blocos lógicos que estruturam a história (Funil Narrativo)."""

    plot_hook: str = Field(
        description="Gancho: por que os aventureiros se envolvem na missão."
    )
    antagonist: Antagonist
    key_locations: list[Location] = Field(
        description="Locais-chave da aventura (de 2 a 4)."
    )
    key_npcs: list[NPC] = Field(
        description="NPCs importantes da aventura (de 2 a 4)."
    )


class ThreeActStructure(BaseModel):
    """Estrutura de 3 atos para apresentar a aventura."""

    act_1_the_call: str = Field(
        description="Ato 1 — O Chamado: introdução do problema e engajamento inicial."
    )
    act_2_the_development: str = Field(
        description="Ato 2 — O Desenvolvimento: exploração, investigação, conflitos."
    )
    act_3_the_climax: str = Field(
        description="Ato 3 — O Clímax: confronto final e resolução."
    )


class Adventure(BaseModel):
    """Aventura completa de D&D 5e (Funil Narrativo + 3 atos)."""

    title: str = Field(description="Título épico e evocativo da aventura.")
    narrative_funnel: NarrativeFunnel
    three_act_structure: ThreeActStructure
