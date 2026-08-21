from pathlib import Path

from app.rag import ingestion_service as ingestion_module


def test_ingestion_adds_parent_child_metadata(
    monkeypatch,
    tmp_path,
):
    captured = []

    monkeypatch.setattr(
        ingestion_module.document_loader,
        "load",
        lambda _: "First sentence. Second sentence. Third sentence.",
    )

    monkeypatch.setattr(
        ingestion_module.text_chunker,
        "chunk",
        lambda _: [
            "First sentence.",
            "Second sentence.",
            "Third sentence.",
        ],
    )

    monkeypatch.setattr(
        ingestion_module.duplicate_detector,
        "exists",
        lambda _: False,
    )

    monkeypatch.setattr(
        ingestion_module.vector_store,
        "add",
        lambda doc_id, text, metadata: captured.append(
            (
                doc_id,
                text,
                metadata.copy(),
            )
        ),
    )

    monkeypatch.setattr(
        ingestion_module.vector_store,
        "sync_bm25_index",
        lambda: {},
    )

    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "First sentence. Second sentence. Third sentence.",
        encoding="utf-8",
    )

    result = ingestion_module.ingestion_service.ingest(
        str(file_path),
    )

    assert result["chunks_indexed"] == 3

    assert len(captured) == 3

    for index, (
        doc_id,
        text,
        metadata,
    ) in enumerate(captured, start=1):

        assert doc_id == f"document_chunk_{index:03d}"

        assert metadata["filename"] == "document"

        assert metadata["chunk_id"] == (
            f"document_chunk_{index:03d}"
        )

        assert metadata["chunk_number"] == index

        assert metadata["total_chunks"] == 3

        assert metadata["chunk_type"] == "child"

        assert metadata["child_id"] == (
            f"document:child:{index - 1}"
        )

        assert metadata["parent_id"] == (
            f"document:parent:{(index - 1) // 3}"
        )


def test_ingestion_preserves_existing_chunk_ids(
    monkeypatch,
    tmp_path,
):
    captured_ids = []

    monkeypatch.setattr(
        ingestion_module.document_loader,
        "load",
        lambda _: "A. B. C.",
    )

    monkeypatch.setattr(
        ingestion_module.text_chunker,
        "chunk",
        lambda _: [
            "A.",
            "B.",
            "C.",
        ],
    )

    monkeypatch.setattr(
        ingestion_module.duplicate_detector,
        "exists",
        lambda _: False,
    )

    monkeypatch.setattr(
        ingestion_module.vector_store,
        "add",
        lambda doc_id, text, metadata: captured_ids.append(
            doc_id,
        ),
    )

    monkeypatch.setattr(
        ingestion_module.vector_store,
        "sync_bm25_index",
        lambda: {},
    )

    file_path = tmp_path / "stable.txt"
    file_path.write_text(
        "A. B. C.",
        encoding="utf-8",
    )

    ingestion_module.ingestion_service.ingest(
        str(file_path),
    )

    assert captured_ids == [
        "stable_chunk_001",
        "stable_chunk_002",
        "stable_chunk_003",
    ]


def test_ingestion_preserves_existing_metadata(
    monkeypatch,
    tmp_path,
):
    captured_metadata = []

    monkeypatch.setattr(
        ingestion_module.document_loader,
        "load",
        lambda _: "A. B.",
    )

    monkeypatch.setattr(
        ingestion_module.text_chunker,
        "chunk",
        lambda _: [
            "A.",
            "B.",
        ],
    )

    monkeypatch.setattr(
        ingestion_module.duplicate_detector,
        "exists",
        lambda _: False,
    )

    monkeypatch.setattr(
        ingestion_module.vector_store,
        "add",
        lambda doc_id, text, metadata: captured_metadata.append(
            metadata.copy(),
        ),
    )

    monkeypatch.setattr(
        ingestion_module.vector_store,
        "sync_bm25_index",
        lambda: {},
    )

    file_path = tmp_path / "metadata.txt"
    file_path.write_text(
        "A. B.",
        encoding="utf-8",
    )

    ingestion_module.ingestion_service.ingest(
        str(file_path),
    )

    assert len(captured_metadata) == 2

    for metadata in captured_metadata:

        assert "indexed_at" in metadata

        assert metadata["filename"] == "metadata"

        assert metadata["chunk_id"].startswith(
            "metadata_chunk_"
        )

        assert metadata["chunk_type"] == "child"

        assert metadata["parent_id"]

        assert metadata["child_id"]