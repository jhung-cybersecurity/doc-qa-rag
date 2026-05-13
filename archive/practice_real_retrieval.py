"""Real practice challenge: rank actual policy chunks by similarity to a question."""
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import numpy as np


# 1. load + chunk 
documents = SimpleDirectoryReader("data").load_data()
splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = splitter.get_nodes_from_documents(documents)

# 2. load embedding model
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# 3. define your question
question = "How do I cancel my policy?"
# a) Embed the question
question_vector = np.array(embed_model.get_text_embedding(question))
# Cosine similarity helper
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
# b) Loop through every node, embed its .text, compute similarity to question
results = []
for node in nodes:
    chunk_vector = np.array(embed_model.get_text_embedding(node.text))
    similarity = cosine_similarity(question_vector, chunk_vector)
    results.append((similarity, node.text))

# d) Sort by similarity, highest first
results.sort(reverse=True)

# e) Print the top 3 ranked chunks with their scores
print(f"Question: {question}\n")
print(f"--- Top 3 most relevant chunks ---\n")
for i, (score, text) in enumerate(results[:3], start=1):
    print(f"#{i} | Similarity: {score:.4f}")
    print(f"{text[:200]}...\n")

