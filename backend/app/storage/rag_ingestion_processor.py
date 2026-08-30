from __future__ import annotations

import os
import tempfile

from pathlib import Path
from typing import BinaryIO

from app.db.models import Asset
from app.rag.ingestion_service import ingestion_service
from app.storage.ingestion_processor import (
    IngestionProcessorResult,
)


class RagIngestionProcessor:
    """
    Adapter between the streaming ingestion architecture
    and the existing path-based RAG ingestion service.

    The existing RAG pipeline remains the source of truth for:

        - document loading
        - chunking
        - duplicate detection
        - vector storage
        - BM25 synchronization

    This adapter only bridges:

        BinaryIO -> temporary filesystem path
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

        suffix = Path(
            asset.original_filename
        ).suffix

        temporary_path: str | None = None
        bytes_processed = 0

        try:

            with tempfile.NamedTemporaryFile(
                mode="wb",
                suffix=suffix,
                delete=False,
            ) as temporary_file:

                temporary_path = temporary_file.name

                while True:

                    chunk = file.read(
                        self.chunk_size
                    )

                    if not chunk:
                        break

                    temporary_file.write(chunk)
                    bytes_processed += len(chunk)

                temporary_file.flush()
                os.fsync(
                    temporary_file.fileno()
                )

            try:
                result = ingestion_service.ingest(
                    temporary_path,
                    original_filename=asset.original_filename,
                )
            except TypeError:
                result = ingestion_service.ingest(
                    temporary_path
                )

            return IngestionProcessorResult(
                status=result["status"],
                bytes_processed=bytes_processed,
                metadata={
                    "asset_id": asset.asset_id,
                    "filename": asset.original_filename,
                    "mime_type": asset.mime_type,
                    "chunks_indexed": result[
                        "chunks_indexed"
                    ],
                    "chunk_ids": result[
                        "chunk_ids"
                    ],
                },
            )

        finally:

            if temporary_path is not None:

                try:
                    os.unlink(temporary_path)
                except FileNotFoundError:
                    pass


rag_ingestion_processor = RagIngestionProcessor()