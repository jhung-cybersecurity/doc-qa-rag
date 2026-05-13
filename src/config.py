# src/config.py
"""Centralized configuration for the RAG pipeline."""

# Retrieval
SIMILARITY_THRESHOLD = 0.5
TOP_K = 3

# Models
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
LLM_MODEL = "claude-opus-4-7"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# ChromaDB
CHROMA_PERSIST_PATH = "./chroma_db"
COLLECTION_NAME = "policy_docs"

# Log file path
LOG_FILE_PATH = "query_log.jsonl"

