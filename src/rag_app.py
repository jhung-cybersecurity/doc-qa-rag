"""Day 3: Production RAG pipeline with persistent vector store."""
import chromadb
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.chroma import ChromaVectorStore

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

# 4. Create a query engine
query_engine = index.as_query_engine(similarity_top_k=3)

# 5. Ask a question
question = "How do I cancel my policy?"
print(f"Q: {question}\n")

response = query_engine.query(question)
print(f"A: {response}\n")

# 6. Show sources
print("--- Sources ---")
for i, node in enumerate(response.source_nodes, start=1):
    print(f"\n[Source {i}] Score: {node.score:.4f} | Page: {node.metadata.get('page_label', 'n/a')}")
    print(f"{node.text[:200]}...")
    