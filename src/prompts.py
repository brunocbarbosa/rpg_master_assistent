"""System Prompts e templates de geração narrativa.

Centraliza a "personalidade" do assistente e a estrutura que guia o modelo a
produzir aventuras coerentes, seguindo o **Funil Narrativo** e a **estrutura de
3 atos** descritos no documento do projeto.

NOTA: conteúdo abaixo é PLACEHOLDER. O prompt engineering definitivo será feito
na Fase 1 funcional.
"""

# System Prompt mestre — define o tom e o papel do assistente (saída em pt-BR).
# TODO: refinar a persona (mestre experiente de D&D 5e, tom épico) e as regras
# de formatação da resposta.
SYSTEM_PROMPT = """
Você é um assistente especialista em mestrar Dungeons & Dragons 5ª edição.
Seu papel é apoiar o Mestre na criação de aventuras, sem substituí-lo.
Responda sempre em português (pt-BR).
""".strip()

# Funil Narrativo — blocos lógicos que estruturam a história gerada.
# Referência: documento do projeto, seção "The Narrative Funnel".
#   - Plot Hook (Gancho): por que os aventureiros se envolvem na missão.
#   - Antagonista & Ameaça: força motriz do conflito + "Doom Clock"
#     (o que acontece se os jogadores falharem).
#   - Locais-chave & NPCs: descrições breves de ambientes e personagens
#     importantes com as informações cruciais.
#
# Estrutura de 3 atos — formato de apresentação da aventura:
#   - Ato 1: O Chamado (introdução do problema e engajamento inicial).
#   - Ato 2: O Desenvolvimento (exploração, investigação, combates menores).
#   - Ato 3: O Clímax (confronto final e resolução).

# TODO: template de prompt do usuário que injeta a ideia central do mestre e
# instrui o modelo a responder no schema de `src/schemas/dnd5e.py`.
ADVENTURE_PROMPT_TEMPLATE = """
Ideia central do mestre:
{idea}

Gere uma aventura seguindo o Funil Narrativo e a estrutura de 3 atos.
""".strip()
