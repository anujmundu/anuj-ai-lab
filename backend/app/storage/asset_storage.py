from __future__ import annotations

import hashlib
import os
import uuid

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


@dataclass(frozen=True, slots=True)
class StoredAsset:
    asset_id: str
    original_filename: str
    storage_path: str
    size_bytes: int
    checksum: str


class AssetStorage:
    """
    Persistent streaming storage for uploaded assets.

    The storage layer deliberately knows nothing about:
        - RAG
        - embeddings
        - videos
        - PDFs
        - databases
        - AI models

    Its only responsibility is safely persisting bytes.
    """

    DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024

    def __init__(
        self,
        root_dir: str | Path = "storage/assets",
        *,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero"
            )

        self.root_dir = Path(root_dir)
        self.chunk_size = chunk_size

        self.root_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def store(
        self,
        file: BinaryIO,
        *,
        original_filename: str,
        asset_id: str | None = None,
    ) -> StoredAsset:

        if not original_filename:
            raise ValueError(
                "original_filename must not be empty"
            )

        resolved_asset_id = (
            asset_id
            if asset_id is not None
            else uuid.uuid4().hex
        )

        temporary_path = (
            self.root_dir
            / f".{resolved_asset_id}.uploading"
        )

        final_path = (
            self.root_dir
            / resolved_asset_id
        )

        hasher = hashlib.sha256()
        size_bytes = 0

        try:

            with open(
                temporary_path,
                "wb",
            ) as output:

                while True:

                    chunk = file.read(
                        self.chunk_size
                    )

                    if not chunk:
                        break

                    output.write(chunk)

                    hasher.update(chunk)

                    size_bytes += len(chunk)

                output.flush()
                os.fsync(
                    output.fileno()
                )

            os.replace(
                temporary_path,
                final_path,
            )

        except Exception:

            try:
                temporary_path.unlink(
                    missing_ok=True
                )
            except Exception:
                pass

            raise

        checksum = hasher.hexdigest()

        return StoredAsset(
            asset_id=resolved_asset_id,
            original_filename=original_filename,
            storage_path=str(final_path),
            size_bytes=size_bytes,
            checksum=checksum,
        )


asset_storage = AssetStorage()