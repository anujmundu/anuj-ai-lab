from app.rag.vector_store import vector_store


vector_store.add_document(
    "1",
    "Python is a programming language."
)

vector_store.add_document(
    "2",
    "Cats are wonderful pets."
)

vector_store.add_document(
    "3",
    "FastAPI is a modern Python framework."
)

results = vector_store.search(
    "Python"
)

print(results)