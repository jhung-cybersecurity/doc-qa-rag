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

def ask(question: str) -> str:
    print(f"Q: {question}\n")

    # retrieve
    retriever = index.as_retriever(similarity_top_k=TOP_K)
    nodes = retriever.retrieve(question)

    # threshold gate
    if not nodes or nodes[0].score < SIMILARITY_THRESHOLD:
        refusal = "I can only answer questions about your auto policy."
        print(f"A: {refusal}\n")
        log_query(
            question=question,
            top_score=nodes[0].score if nodes else 0.0,
            blocked=True,
            answer=refusal,
        )
        return refusal

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
    print(f"A: {answer}\n")

    # log
    log_query(
        question=question,
        top_score=nodes[0].score,
        blocked=False,
        answer=answer,
    )

    # show sources
    print("--- Sources ---")
    for i, node in enumerate(nodes, start=1):
        page = node.metadata.get("page_label", "n/a")
        print(f"\n[Source {i}] Score: {node.score:.4f} | Page: {page}")
        print(f"{node.text[:200]}...")

    return answer

