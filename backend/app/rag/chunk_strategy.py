from enum import Enum


class ChunkStrategy(str, Enum):
    """
    Supported chunking strategies.

    Additional strategies can be added in future
    phases without changing the public API.
    """

    SENTENCE = "sentence"

    PARAGRAPH = "paragraph"

    FIXED = "fixed"

    RECURSIVE = "recursive"