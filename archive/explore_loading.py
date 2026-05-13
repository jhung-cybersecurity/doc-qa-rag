"""Day 2 exploration: what does SimpleDirectoryReader actually give us?"""
from llama_index.core import SimpleDirectoryReader

# load all files from the data/ folder
documents = SimpleDirectoryReader("data").load_data()

# inspect what we got back 
print(f"Number of documents: {len(documents)}")
print(f"Type: {type(documents[0])}")
print(f"\n--- First document attributes ---")
print(f"Text length: {len(documents[0].text)} characters")
print(f"Metadata: {documents[0].metadata}")
print(f"\n--- First 500 characters of text ---")
print(documents[0].text[:500])

