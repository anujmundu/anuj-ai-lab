from app.rag.retriever import retriever

results = retriever.retrieve(
    "Python"
)

print(results)