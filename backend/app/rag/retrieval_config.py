from dataclasses import dataclass


@dataclass(slots=True)
class RetrievalConfig:
    """
    Configuration for retrieval engines.

    These settings control how multiple retrieval
    strategies are combined.

    The defaults are intentionally conservative and
    can be tuned later without modifying the retrieval
    implementations.
    """

    top_k: int = 5

    semantic_weight: float = 0.70

    keyword_weight: float = 0.30

    enable_semantic: bool = True

    enable_keyword: bool = True

    normalize_scores: bool = True