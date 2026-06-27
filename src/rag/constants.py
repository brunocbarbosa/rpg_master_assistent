"""Constantes compartilhadas entre os módulos de RAG.

Centraliza valores de configuração para evitar dependências circulares e
importações pesadas no caminho de consulta (retrieve) e de ingestão (ingest).
"""

COLLECTION_NAME = "dnd_5e_knowledge"
RPG_SYSTEM = "dnd_5e"
