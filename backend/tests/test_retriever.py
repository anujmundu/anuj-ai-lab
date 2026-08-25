from app.rag.retriever import retriever


def test_semantic_retriever_structure():
    results = retriever.retrieve("Python", k=2)
    assert "ids" in results
    assert "documents" in results