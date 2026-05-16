from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from src.rag import ask

# 1. App instance with a real title for the /docs page 
app = FastAPI(
    title="Insurance Policy Q&A API",
    description="RAG-powered Q&A over an auto insurance policy PDF",
    version="0.1.0",
)

# 2. Request schema - what callers send in 
class AskRequest(BaseModel):
    question: str

# 3. Response schema - mirrors the dict ask() returns
class AskResponse(BaseModel):
    question: str
    answer: str
    blocked: bool
    top_score: float
    sources: list
    refusal_reason: Optional[str] = None


# 4. Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# 5. The real endpoint - wraps your existing ask()
@app.post("/ask", response_model=AskResponse)
def ask_endpoint(request: AskRequest):
    result = ask(request.question)
    return result

