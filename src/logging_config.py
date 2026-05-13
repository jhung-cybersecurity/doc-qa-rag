# src/logging_config.py
"""JSONL query logger setup."""
import json
import logging
from datetime import datetime, timezone

from src.config import LOG_FILE_PATH

def get_query_logger() -> logging.Logger:
    """Return a configured logger that writes JSONL entries to disk."""
    logger = logging.getLogger("query_logger")

    # Avoid adding duplicate handlers if called multi times
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s")) # raw JSON, no prefix
    logger.addHandler(handler)
    return logger

def log_query(question: str, top_score: float, blocked: bool, answer: str) -> None:
    """Write a single query event as a JSON line."""
    logger = get_query_logger()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "top_score": round(top_score, 4),
        "blocked": blocked,
        "answer": answer,
    }
    logger.info(json.dumps(entry))


