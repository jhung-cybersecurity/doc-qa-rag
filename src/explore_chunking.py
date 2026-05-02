"""Day 2 exploration: see what chunking actually does."""
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

# step 1: load the PDF (same as before)
documents = SimpleDirectoryReader("data").load_data()
print(f"Loaded {len(documents)} documents (one per page)\n")

# step 2: configure the chunker
# chunk_size = max charc. per chunk (roughly)
# chunk_overlap = how much each chunk shares with the next one 
splitter = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=50
)

# step 3: chunk all documents into "nodes"
# in LlamIndex, a chunk is called a "node"
nodes = splitter.get_nodes_from_documents(documents)

# step 4: inspect what we got
print(f"Total nodes (chunks) created: {len(nodes)}\n")
print(f"--- First chunk ---")
print(f"Length: {len(nodes[0].text)} characters")
print(f"Metadata: {nodes[0].metadata}")
print(f"Text:\n{nodes[0].text}\n")

print(f"--- Second chunk ---")
print(f"Length: {len(nodes[1].text)} characters")
print(f"Text:\n{nodes[1].text}\n")

