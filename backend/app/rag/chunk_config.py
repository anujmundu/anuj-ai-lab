from dataclasses import dataclass


@dataclass(slots=True)
class ChunkingConfig:
    """
    Configuration for the text chunker.

    These defaults work well for most
    English technical documents.
    """

    chunk_size: int = 500

    overlap_sentences: int = 1

    strategy: str = "sentence"

    paragraph_separator: str = "\n\n"

    sentence_regex: str = r"(?<=[.!?])\s+"