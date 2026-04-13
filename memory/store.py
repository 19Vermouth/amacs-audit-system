import chromadb

client = chromadb.Client()

collection = client.create_collection("audit_memory")

def save_memory(text):
    collection.add(
        documents=[text],
        ids=[str(hash(text))]
    )

def query_memory(query):
    return collection.query(query_texts=[query], n_results=2)