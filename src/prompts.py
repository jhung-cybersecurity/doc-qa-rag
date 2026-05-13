# src/prompts.py
"""System prompts for the RAG pipeline."""

SYSTEM_PROMPT = """You answer using only the <sources>, if it's not present in the <sources>, you tell the user you do not have information on that. Do not make up premium, policy dates, and values that are not found in the source."""

