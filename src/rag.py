# src/rag.py
"""Core RAG pipeline: setup + ask() function."""
import chromadb
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.llms import ChatMessage

from src.config import (
    SIMILARITY_THRESHOLD,
    TOP_K,
    EMBEDDING_MODEL,
    LLM_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_PERSIST_PATH,
    COLLECTION_NAME,
)
from src.prompts import SYSTEM_PROMPT
from src.logging_config import log_query

REFUSAL_PHRASES = [
    "i don't have information",
    "i do not have information",
    "not in the sources",
    "not provided in the sources",
    "i cannot answer",
    "no information available",
]

load_dotenv()

# --- Module-level setup (runs once on import) ---

Settings.llm = Anthropic(model=LLM_MODEL)
Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
Settings.node_parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)
chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

if chroma_collection.count() == 0:
    print("First run — ingesting PDF...")
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    print(f"Ingested {chroma_collection.count()} chunks.\n")
else:
    print(f"Loading existing index ({chroma_collection.count()} chunks)...\n")
    index = VectorStoreIndex.from_vector_store(vector_store)


# --- Per-query function ---
def _detect_refusal(answer: str) -> bool:
    """Heuristic: returns True if Claude's answer looks like a refusal."""
    answer_lower = answer.lower()
    return any(phrase in answer_lower for phrase in REFUSAL_PHRASES)

def ask(question, threshold=None):
    """Run one query through the RAG pipeline. Returns a structured result."""
    if threshold is None:
        threshold = SIMILARITY_THRESHOLD
    # retrieve
    retriever = index.as_retriever(similarity_top_k=TOP_K)
    nodes = retriever.retrieve(question)

    top_score = nodes[0].score if nodes else 0.0

    # Layer 1: threshold gate
    if not nodes or nodes[0].score < threshold:
        refusal = "I can only answer questions about your auto policy."
        log_query(
            question=question,
            top_score=top_score,
            blocked=True,
            answer=refusal,
        )
        return {
            "question": question,
            "answer": refusal,
            "blocked": True,
            "top_score": top_score,
            "sources": [],
            "refusal_reason": "threshold",
        }

    # build context + user message
    context = "\n\n".join(node.text for node in nodes)
    user_message = f"""<sources>
{context}
</sources>

Question: {question}"""

    # call Claude
    response = Settings.llm.chat([
        ChatMessage(role="system", content=SYSTEM_PROMPT),
        ChatMessage(role="user", content=user_message),
    ])
    answer = response.message.content
    
    # Layer 2: did Claude refuse?
    layer_2_refused = _detect_refusal(answer)

    # build sources list
    sources = [
        {
            "page": node.metadata.get("page_label", "n/a"),
            "score": node.score,
            "text": node.text,
        }
        for node in nodes
    ]

    # log
    log_query(
        question=question,
        top_score=nodes[0].score,
        blocked=False,
        answer=answer,
    )
    return {
        "question": question,
        "answer": answer,
        "blocked": layer_2_refused,
        "top_score": top_score,
        "sources": sources,
        "refusal_reason": "prompt" if layer_2_refused else None,
    }


