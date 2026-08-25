from app.rag.vector_store import vector_store


def test_vector_store_get_structure():
    results = vector_store.collection.get()
    assert "ids" in results
    assert "metadatas" in results