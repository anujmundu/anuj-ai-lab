from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO, Protocol

from app.db.models import Asset


@dataclass(frozen=True, slots=True)
class IngestionProcessorResult:
    status: str
    bytes_processed: int
    metadata: dict


class IngestionProcessor(Protocol):

    def process(
        self,
        file: BinaryIO,
        *,
        asset: Asset,
    ) -> IngestionProcessorResult:
        ...


class InspectionIngestionProcessor:
    """
    Minimal ingestion processor used as the execution boundary.

    It consumes the persisted asset as a stream and records the
    number of bytes processed.

    This is intentionally NOT the RAG ingestion implementation.
    """

    def __init__(
        self,
        *,
        chunk_size: int = 8 * 1024 * 1024,
    ) -> None:

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero"
            )

        self.chunk_size = chunk_size

    def process(
        self,
        file: BinaryIO,
        *,
        asset: Asset,
    ) -> IngestionProcessorResult:

        bytes_processed = 0

        while True:

            chunk = file.read(
                self.chunk_size
            )

            if not chunk:
                break

            bytes_processed += len(chunk)

        return IngestionProcessorResult(
            status="processed",
            bytes_processed=bytes_processed,
            metadata={
                "asset_id": asset.asset_id,
                "filename": asset.original_filename,
                "mime_type": asset.mime_type,
            },
        )


ingestion_processor = InspectionIngestionProcessor()
