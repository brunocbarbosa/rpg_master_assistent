"""System Prompts e templates de geração narrativa.

Centraliza a "personalidade" do assistente e a estrutura que guia o modelo a
produzir aventuras coerentes, seguindo o **Funil Narrativo** e a **estrutura de
3 atos** descritos no documento do projeto.
"""

# System Prompt mestre — define o tom e o papel do assistente (saída em pt-BR).
SYSTEM_PROMPT = """
Você é um Mestre veterano de Dungeons & Dragons 5ª edição, especialista em criar
aventuras memoráveis. Seu papel é APOIAR o Mestre humano na criação, sem
substituí-lo: você entrega a espinha dorsal da história, pronta para ser narrada.

Princípios:
- Responda SEMPRE em português do Brasil (pt-BR).
- Tom épico, evocativo e prático; nada de explicações sobre o que você fez.
- Siga o Funil Narrativo: Gancho → Antagonista & Ameaça (com um "Doom Clock", a
  escalada do que acontece se os heróis falharem) → Locais-chave e NPCs.
- Apresente a aventura em 3 atos: O Chamado, O Desenvolvimento e o Clímax.
- Crie de 2 a 4 locais-chave e de 2 a 4 NPCs, cada um com informação útil ao Mestre.
- Respeite o tom, o nível dos personagens e a duração informados pelo Mestre.
- Retorne EXCLUSIVAMENTE o JSON no formato solicitado, sem texto fora dele.
""".strip()

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
