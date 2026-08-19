from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Iterator


class AssetReader:
    """
    Opens persisted assets as bounded streaming readers.

    This layer deliberately does not:
        - parse documents
        - run RAG
        - create embeddings
        - load the entire asset into memory
    """

    DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024

    def __init__(
        self,
        *,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero"
            )

        self.chunk_size = chunk_size

    def open(
        self,
        storage_path: str | Path,
    ) -> BinaryIO:

        path = Path(storage_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Asset storage file not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Asset storage path is not a file: {path}"
            )

        return path.open("rb")

    def iter_chunks(
        self,
        file: BinaryIO,
    ) -> Iterator[bytes]:

        while True:

            chunk = file.read(
                self.chunk_size
            )

            if not chunk:
                break

            yield chunk


asset_reader = AssetReader()