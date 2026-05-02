"""Day 2 exploration: what does an embedding actually look like?"""
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# load the embedding model (downloads on first run, ~130MB)
print("Loading embeddings model...")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
print("Loaded.\n")

# embed a single sentence
text = "The deductible for collision coverage is $500."
vector = embed_model.get_text_embedding(text)

# inspect the vecotr
print(f"Input text: {text}")
print(f"Vector type: {type(vector)}")
print(f"Vector length (dimensions): {len(vector)}")
print(f"\nFirst 10 numbers in the vector:")
print(vector[:10])
print(f"\nMin value: {min(vector):.4f}")
print(f"Max value: {max(vector):.4f}")

