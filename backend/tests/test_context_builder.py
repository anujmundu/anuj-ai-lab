from app.rag.context_builder import context_builder


def test_context_builder_builds_context():
    documents = ["Chunk A content", "Chunk B content"]
    metadatas = [
        {"filename": "doc1", "chunk_number": 1, "total_chunks": 2},
        {"filename": "doc1", "chunk_number": 2, "total_chunks": 2},
    ]

    context = context_builder.build_context(
        documents=documents,
        metadatas=metadatas,
    )

    assert "Chunk A content" in context
    assert "Chunk B content" in context
    assert "doc1" in context