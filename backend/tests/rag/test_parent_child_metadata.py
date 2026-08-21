from app.rag.retrieval_models import RetrievalMetadata


def test_retrieval_metadata_supports_parent_child_ids():
    metadata = RetrievalMetadata(
        filename="document.pdf",
        chunk_id="child-001",
        parent_id="parent-001",
        child_id="child-001",
        chunk_number=1,
        total_chunks=10,
    )

    assert metadata.parent_id == "parent-001"
    assert metadata.child_id == "child-001"


def test_parent_child_ids_are_optional():
    metadata = RetrievalMetadata(
        filename="document.pdf",
        chunk_id="chunk-001",
    )

    assert metadata.parent_id == ""
    assert metadata.child_id == ""


def test_existing_retrieval_metadata_remains_backward_compatible():
    metadata = RetrievalMetadata(
        filename="document.pdf",
        chunk_id="chunk-001",
        chunk_number=2,
        total_chunks=5,
    )

    assert metadata.filename == "document.pdf"
    assert metadata.chunk_id == "chunk-001"
    assert metadata.chunk_number == 2
    assert metadata.total_chunks == 5
    assert metadata.parent_id == ""
    assert metadata.child_id == ""