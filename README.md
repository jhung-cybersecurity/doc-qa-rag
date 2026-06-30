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

## Setup
1. Clone: `git clone https://github.com/jhung-cybersecurity/doc-qa-rag` then `cd doc-qa-rag`
2. Venv: `python -m venv venv`
3. Activate: `venv\Scripts\Activate.ps1`
4. Install: `pip install -r requirements.txt`
5. Secret: API key `ANTHROPIC_API_KEY=your-key-here` goes in `.env` and is activated in `.gitignore` to make sure it is never committed. 
6. Run: `python -m src.main`

- When running the repo for the first time, expect a small delay because the repo builds the index and downloads the embedding model.
- Go to (console.anthropic.com) to get the API key
- Activation is OS-specific. This repo is for Windows PowerShell (`venv\Scripts\Activate.ps1`). A Mac/Linux user needs `source venv/bin/activate`.

## Docker

1. Build the image: `docker build -t doc-qa-rag .`
   Reads the Dockerfile and produces a named image.

2. Run a container: `docker run -p 8000:8000 --env-file .env -v ${PWD}/chroma_db:/app/chroma_db doc-qa-rag`
   - `-p 8000:8000` exposes the API so you can reach it from a browser
   - `--env-file .env` loads the environment variables from the host's `.env` at runtime
   - `-v ${PWD}/chroma_db:/app/chroma_db` mounts a host folder so the index persists after the container stops

3. Secrets in `.env` are injected at runtime, never baked into the image, because image layers are inspectable and anyone who pulls the image could read a baked-in key.

## Evaluation
There are three categories that the repo tests for. The first one is `on-topic` which tests for questions that have a direct answer from the `<sources>`. Second one is `off-topic` which tests for questions that have nothing to do with the provided `<sources>`. Last but not least, `adversarial` tests for questions that are similar in topic but ultimately have nothing to do with it. An example of this is case #3: "policy number for life insurance". The repo is about auto insurance not life insurance. 

After thorough testing, I ended up with 10 of 11 passing. This is a deliberate, documented result, not a bug. Case #10 fails on phrase-match nondeterminism. The answer is correct but the exact string assertion is unreliable against a paraphrasing LLM. 




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