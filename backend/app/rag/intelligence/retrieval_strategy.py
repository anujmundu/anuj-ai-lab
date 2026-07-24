from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalStrategy:
    """
    Defines how retrieval should be executed.

    Stage 5.0 keeps defaults identical to the
    current implementation.
    """

    query: str

    k: int

    rewrite: bool = False

    expand: bool = False

    multi_query: bool = False