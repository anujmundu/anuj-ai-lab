from app.rag.hybrid_retriever import hybrid_retriever


def test_hybrid_retriever_structure():
    results = hybrid_retriever.retrieve(
        query="What is ChromaDB?",
        k=3,
    )
    assert "ids" in results
    assert "documents" in results
    assert "metadatas" in results
    assert "retrieval" in results
    assert "pipeline" in results