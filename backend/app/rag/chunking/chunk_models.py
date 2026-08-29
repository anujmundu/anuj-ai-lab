from dataclasses import dataclass


@dataclass(slots=True)
class Chunk:
    """
    Internal representation of a chunk.

    The ingestion pipeline still receives
    plain strings.

    This object exists so we can compute
    statistics and diagnostics without
    changing the rest of the codebase.
    """

    text: str

    characters: int

    words: int