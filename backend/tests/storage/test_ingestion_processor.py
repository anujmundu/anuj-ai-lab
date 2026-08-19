import io

import pytest

from app.db.models import Asset
from app.storage.ingestion_processor import (
    InspectionIngestionProcessor,
)


def create_asset():

    return Asset(
        asset_id="asset-test",
        filename="test.txt",
        original_filename="test.txt",
        mime_type="text/plain",
        size_bytes=11,
        storage_path="storage/assets/test",
        status="completed",
        progress=1.0,
    )


def test_processor_consumes_stream():

    processor = InspectionIngestionProcessor(
        chunk_size=4,
    )

    result = processor.process(
        io.BytesIO(b"hello world"),
        asset=create_asset(),
    )

    assert result.status == "processed"
    assert result.bytes_processed == 11


def test_processor_returns_asset_metadata():

    processor = InspectionIngestionProcessor()

    result = processor.process(
        io.BytesIO(b"hello"),
        asset=create_asset(),
    )

    assert result.metadata == {
        "asset_id": "asset-test",
        "filename": "test.txt",
        "mime_type": "text/plain",
    }


def test_processor_rejects_invalid_chunk_size():

    with pytest.raises(
        ValueError,
        match="chunk_size",
    ):

        InspectionIngestionProcessor(
            chunk_size=0,
        )


def test_processor_handles_empty_stream():

    processor = InspectionIngestionProcessor()

    result = processor.process(
        io.BytesIO(b""),
        asset=create_asset(),
    )

    assert result.status == "processed"
    assert result.bytes_processed == 0
