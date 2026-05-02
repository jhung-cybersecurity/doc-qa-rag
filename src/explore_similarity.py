"""Day 2 exploration: do similar sentences produce similar vectors?"""
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import numpy as np

print("Loading embedding model...")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
print("Loaded.\n")


# three test sentences - two related, one unrelated
sentence_A = "How do I cancel my insurance policy?"
sentence_B = "What's the process for terminating my coverage?"
sentence_C = "What is the deductible for collision coverage?"
sentence_D = "What's the cancellation policy?"

# embed all three
vec_A = np.array(embed_model.get_text_embedding(sentence_A))
vec_B = np.array(embed_model.get_text_embedding(sentence_B))
vec_C = np.array(embed_model.get_text_embedding(sentence_C))
vec_D = np.array(embed_model.get_text_embedding(sentence_D))

# cosine similarity = dot product of normalized vectors
# range: -1 (opposite) to 1 (identical), 0 = unrelated
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

sim_AB = cosine_similarity(vec_A, vec_B)
sim_AC = cosine_similarity(vec_A, vec_C)
sim_BC = cosine_similarity(vec_B, vec_C)
sim_AD = cosine_similarity(vec_A, vec_D)


print(f"A: {sentence_A}")
print(f"B: {sentence_B}")
print(f"C: {sentence_C}")
print(f"D: {sentence_D}\n")

print(f"Similarity(A, B) = {sim_AB:.4f}   <-- both about cancellation")
print(f"Similarity(A, C) = {sim_AC:.4f}   <-- cancellation vs deductible")
print(f"Similarity(B, C) = {sim_BC:.4f}   <-- cancellation vs deductible")
print(f"Similarity(A, D) = {sim_AD:.4f}   <-- cancellation vs cancellation")

