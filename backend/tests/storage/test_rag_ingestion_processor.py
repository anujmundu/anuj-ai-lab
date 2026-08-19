import io

import pytest

from app.db.models import Asset
from app.storage.rag_ingestion_processor import (
    RagIngestionProcessor,
)


def create_asset(
    *,
    filename="test.txt",
):
    return Asset(
        asset_id="asset-test",
        filename=filename,
        original_filename=filename,
        mime_type="text/plain",
        size_bytes=0,
        storage_path="storage/assets/asset-test",
        status="completed",
        progress=1.0,
    )


def test_processor_bridges_stream_to_rag_service(
    monkeypatch,
):
    captured = {}

    def fake_ingest(file_path):
        captured["file_path"] = file_path

        with open(
            file_path,
            "rb",
        ) as file:
            captured["content"] = file.read()

        return {
            "filename": "test",
            "status": "indexed",
            "chunks_indexed": 2,
            "chunk_ids": [
                "chunk-1",
                "chunk-2",
            ],
        }

    import app.storage.rag_ingestion_processor as module

    monkeypatch.setattr(
        module.ingestion_service,
        "ingest",
        fake_ingest,
    )

    processor = RagIngestionProcessor(
        chunk_size=4,
    )

    result = processor.process(
        io.BytesIO(
            b"hello world"
        ),
        asset=create_asset(),
    )

    assert captured["content"] == b"hello world"

    assert result.status == "indexed"
    assert result.bytes_processed == 11

    assert result.metadata["asset_id"] == (
        "asset-test"
    )

    assert result.metadata["chunks_indexed"] == 2
    assert result.metadata["chunk_ids"] == [
        "chunk-1",
        "chunk-2",
    ]


def test_processor_uses_original_file_extension(
    monkeypatch,
):
    captured = {}

    def fake_ingest(file_path):
        captured["file_path"] = file_path

        return {
            "filename": "document",
            "status": "indexed",
            "chunks_indexed": 1,
            "chunk_ids": ["chunk-1"],
        }

    import app.storage.rag_ingestion_processor as module

    monkeypatch.setattr(
        module.ingestion_service,
        "ingest",
        fake_ingest,
    )

    processor = RagIngestionProcessor()

    processor.process(
        io.BytesIO(b"pdf content"),
        asset=create_asset(
            filename="document.pdf"
        ),
    )

    assert captured["file_path"].endswith(
        ".pdf"
    )


def test_processor_removes_temporary_file(
    monkeypatch,
):
    captured = {}

    def fake_ingest(file_path):
        captured["file_path"] = file_path

        assert __import__(
            "os"
        ).path.exists(file_path)

        return {
            "filename": "test",
            "status": "indexed",
            "chunks_indexed": 1,
            "chunk_ids": ["chunk-1"],
        }

    import app.storage.rag_ingestion_processor as module

    monkeypatch.setattr(
        module.ingestion_service,
        "ingest",
        fake_ingest,
    )

    processor = RagIngestionProcessor()

    processor.process(
        io.BytesIO(b"test"),
        asset=create_asset(),
    )

    assert not __import__(
        "os"
    ).path.exists(
        captured["file_path"]
    )


def test_processor_cleans_up_when_rag_fails(
    monkeypatch,
):
    captured = {}

    def fake_ingest(file_path):
        captured["file_path"] = file_path

        raise RuntimeError(
            "RAG ingestion failed"
        )

    import app.storage.rag_ingestion_processor as module

    monkeypatch.setattr(
        module.ingestion_service,
        "ingest",
        fake_ingest,
    )

    processor = RagIngestionProcessor()

    with pytest.raises(
        RuntimeError,
        match="RAG ingestion failed",
    ):
        processor.process(
            io.BytesIO(b"test"),
            asset=create_asset(),
        )

    assert not __import__(
        "os"
    ).path.exists(
        captured["file_path"]
    )


def test_processor_rejects_invalid_chunk_size():
    with pytest.raises(
        ValueError,
        match="chunk_size must be greater than zero",
    ):
        RagIngestionProcessor(
            chunk_size=0,
        )