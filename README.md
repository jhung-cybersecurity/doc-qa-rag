## Architecture

src/
├── config.py          # Threshold, model names, paths
├── prompts.py         # Strict system prompt with <sources> tags
├── logging_config.py  # JSONL query logger
├── rag.py             # Pipeline setup + ask() function
└── main.py            # CLI entry point

Run with: `python -m src.main`

