# RPG Master Assistant

Co-piloto de IA para mestres de RPG. O assistente **não substitui** o mestre —
ele acelera a criação de conteúdo (worldbuilding, narrativa e gestão de campanha),
deixando o mestre livre para improvisar e conduzir o jogo.

> **MVP (Fase 1):** gerador de aventuras para **Dungeons & Dragons 5e**, usando o
> "Funil Narrativo" (gancho, antagonista/Doom Clock, locais & NPCs) e a estrutura
> de 3 atos. Evolução futura (Fase 2): multi-sistema (D&D + Cyberpunk RED).
>
> Documento completo do projeto: [`documents/RPG_MASTER_ASSISTENT_DOCUMENT.md`](documents/RPG_MASTER_ASSISTENT_DOCUMENT.md).

## Stack

- **Python** 3.10+
- **Streamlit** — interface web
- **Mistral via Ollama** (`ollama`) — motor de IA, rodando localmente
- **python-dotenv** — variáveis de ambiente

## Pré-requisitos

- Python 3.10 ou superior
- [Ollama](https://ollama.com) instalado e com o modelo Mistral baixado:
  `ollama pull mistral` (não requer chave de API)

## Setup

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Configurar as variáveis de ambiente
cp .env.example .env
# ajuste OLLAMA_HOST/OLLAMA_MODEL se necessário (no WSL com Ollama no host
# Windows, aponte OLLAMA_HOST para o IP do host; caso contrário o app tenta
# detectar automaticamente)
```

## Como rodar

```bash
streamlit run app.py
```

> **Status atual:** estrutura e tooling do projeto. A geração de aventuras via IA
> ainda não está implementada (a interface já exibe o formulário).

## Estrutura do projeto

```text
.
├── app.py                # Entrypoint Streamlit
├── requirements.txt      # Dependências
├── .env.example          # Template das variáveis de ambiente
└── src/
    ├── config.py         # Carregamento de configuração (.env)
    ├── ia_client.py      # Cliente do Ollama (Mistral local)
    ├── prompts.py        # System Prompts e templates narrativos
    └── schemas/
        └── dnd5e.py      # Estruturas de dados (JSON) para D&D 5e
```
