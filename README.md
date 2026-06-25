## DOC-QA-RAG
This RAG ingests the insurance policy Q&A PDFs and filters irrelevant questions by thresholds followed by a second defense layer using prompts against hallucination.

When the user asks a question, the RAG uses the initial PDF ingestions which are chunked and embedded into ChromaDB. Then it uses similarity search to retrieve the top-K chunks. If the top chunk scores below 0.45 it rejects before the LLM. Claude then answers using only the retrieved chunks via a strict prompt, and declines if they do not contain the answer.

## Stack Highlights 
LlamaIndex, ChromaDB, local embeddings (BAAI/bge-small-en-v1.5, run on-device for zero embedding cost and document privacy), Claude-opus-4-8, FastAPI, Docker.

## Two-Layer Defense
The first layer is the similarity threshold. It sets a threshold where the retrieval only returns the top chunk, if it scores higher than 0.45. Initially it was 0.50 as an intuition to get the RAG working. After running sweep threshold testings, I lowered it to 0.45 to allow borderline questions through. Blocking a question that the LLM could have answered is worse than letting a borderline question through. 

The second layer is prompt. It's a strict system prompt that forces Claude to answer only from the provided `<sources>` not from its own training data. If the sources do not contain the answer, it will say so instead of guessing and making up answers.

Example: Case #5 — "How do I pay my premium?", 0.49 score
Layer 1 let the chunk pass because it's above 0.45
Layer 2 blocked it because the `<sources>` do not have any information on how to pay the insurance premium therefore it tells the user "I don't have that information" instead of making up a payment method. 




## Architecture

src/
├── config.py          # Threshold, model names, paths
├── prompts.py         # Strict system prompt with <sources> tags
├── logging_config.py  # JSONL query logger
├── rag.py             # Pipeline setup + ask() function
└── main.py            # CLI entry point

Run with: `python -m src.main`

## Run as HTTP service

In addition to the CLI (`python -m src.main`), the RAG pipeline is exposed as a FastAPI service:

```bash
fastapi dev src/api.py
```

Then open http://127.0.0.1:8000/docs for the interactive Swagger UI.

### Endpoints

| Method | Path     | Description                                  |
|--------|----------|----------------------------------------------|
| GET    | /health  | Health check, returns `{"status": "ok"}`     |
| POST   | /ask     | Submit a question, returns structured answer |

### Example request

```json
POST /ask
{"question": "what is my deductible"}
```

### Example response

```json
{
  "question": "what is my deductible",
  "answer": "Your deductible is...",
  "blocked": false,
  "top_score": 0.62,
  "sources": [...],
  "refusal_reason": null
}
```

When a query is blocked, `blocked: true` and `refusal_reason` indicates which defense layer triggered (`"threshold"` for similarity gate, `"prompt"` for Claude-driven refusal).