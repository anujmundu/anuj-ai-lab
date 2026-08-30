from app.rag.embedding_service import embedding_service


def test_embedding_vector_generation():
    vector = embedding_service.embed(
        "Python is a programming language."
    )
    assert isinstance(vector, list)
    assert len(vector) > 0