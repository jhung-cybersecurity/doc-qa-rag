"""Day 3: Production RAG pipeline with persistent vector store."""
import os
import chromadb
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.chroma import ChromaVectorStore

# load API key from .env
load_dotenv()

# 1. config global models - set once, used everywhere
Settings.llm = Anthropic(model="claude-opus-4-7")
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

# 2. set up ChromaDB - persistent on disk
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("policy_docs")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 3. build or load the index
# If collection is empty, ingest the PDF. Otherwise, reuse existing embeddings.
if chroma_collection.count() == 0:
    print("First run — ingesting PDF...")
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    print(f"Ingested {chroma_collection.count()} chunks.\n")
else:
    print(f"loading existing index ({chroma_collection.count()} chunks)...\n")
    index = VectorStoreIndex.from_vector_store(vector_store)

# 4. create a query engine, the thing that does the full RAG flow
query_engine = index.as_query_engine(similarity_top_k=3)

questions = [
    "What is the deductible for collision coverage?",
    "Tell me about my pet's veterinary coverage",
    "What's my coverage limit?",
]

retriever = index.as_retriever(similarity_top_k=3)

for question in questions:
    nodes = retriever.retrieve(question)
    print(f"\nQ: {question}")
    for i, node in enumerate(nodes, start=1):
        print(f"  #{i}: {node.score:.4f}")