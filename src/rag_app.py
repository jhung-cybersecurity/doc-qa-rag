"""Day 3: Production RAG pipeline with persistent vector store."""
import chromadb
import json
from datetime import datetime
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.llms import ChatMessage

SIMILARITY_THRESHOLD = 0.50
load_dotenv()

# 1. Configure global models — set ONCE, used everywhere
Settings.llm = Anthropic(model="claude-opus-4-7")
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

# 2. Set up ChromaDB — persistent on disk
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("policy_docs")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 3. Build or load the index
if chroma_collection.count() == 0:
    print("First run — ingesting PDF...")
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    print(f"Ingested {chroma_collection.count()} chunks.\n")
else:
    print(f"Loading existing index ({chroma_collection.count()} chunks)...\n")
    index = VectorStoreIndex.from_vector_store(vector_store)




# 5. Ask a question
def ask(question: str) -> str:
    print(f"Q: {question}\n")
    
    # retrieve nodes
    retriever = index.as_retriever(similarity_top_k=3)
    nodes = retriever.retrieve(question)

    # threshold gate
    if not nodes or nodes[0].score < SIMILARITY_THRESHOLD:
        refusal = "I can only answer questions about your auto policy."
        print(f"A: {refusal}\n")

        # log the refusal
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "top_score": nodes[0].score if nodes else 0.0,
            "blocked": True,
            "answer": refusal,
        }
        with open("query_log.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return refusal

    # build context from retrieve nodes
    context = "\n\n".join(node.text for node in nodes)

    # build prompts
    system_prompt = """You answer using only the <sources>, if it's not present in the <sources>, you tell the user you do not have information on that. Do not make up premium, policy dates, and values that are not found in the source."""
    
    user_message = f"""<sources>
    {context}
    </sources>

    Question: {question}"""

    # call Claude
    response = Settings.llm.chat([
    ChatMessage(role="system", content=system_prompt),
    ChatMessage(role="user", content=user_message),
    ])
    
    answer = response.message.content
    print(f"A: {answer}\n")

    # ↓ LOG THE ANSWER
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "top_score": nodes[0].score,
        "blocked": False,
        "answer": answer,
    }
    with open("query_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Show sources
    print("--- Sources ---")
    for i, node in enumerate(nodes, start=1):
        print(f"\n[Source {i}] Score: {node.score:.4f} | Page: {node.metadata.get('page_label', 'n/a')}")
        print(f"{node.text[:200]}...")

    return answer 

print("\n=== Auto Policy Q&A ===")
print("Ask any question...")
while True:
    question = input("\nAsk a question (or 'quit'): ").strip()

    if question.lower() in {"quit", "exit", "q"}:
        print("Goodbye.")
        break
    if not question:
        continue

    ask(question)