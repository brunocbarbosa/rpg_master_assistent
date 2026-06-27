"""Pacote de RAG (Retrieval-Augmented Generation).

Reúne a base de conhecimento das regras de RPG: ingestão dos PDFs (extrair →
dividir → embeddar → gravar no ChromaDB) e, futuramente, a consulta usada na
geração das aventuras. Os embeddings vêm do Ollama (`nomic-embed-text`).
"""
