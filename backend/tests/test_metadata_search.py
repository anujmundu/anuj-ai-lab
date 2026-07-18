from app.rag.vector_store import vector_store

results = vector_store.collection.get()

print(results["ids"])
print()
print(results["metadatas"])