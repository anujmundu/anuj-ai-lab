from app.rag.hybrid_retriever import hybrid_retriever


results = hybrid_retriever.retrieve(
    query="What is ChromaDB?",
    k=3
)

print("Retrieved IDs:")
print(results["ids"][0])

print()

print("Retrieved Documents:")
for document in results["documents"][0]:
    print(document)
    print("-" * 40)