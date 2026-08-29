from dataclasses import dataclass


@dataclass(slots=True)
class EmbeddingSimilarityConfig:
    """
    Configuration for semantic similarity.

    This module provides a unified abstraction
    for semantic similarity calculations.

    The initial implementation uses the
    SemanticMatcher.

    Future implementations may replace it with:

    • Sentence Transformers
    • BGE
    • E5
    • OpenAI Embeddings
    """

    # --------------------------------------------------
    # Master Switches
    # --------------------------------------------------

    enabled: bool = True

    include_similarity_breakdown: bool = True

    include_diagnostics: bool = True

    include_confidence: bool = True

    # --------------------------------------------------
    # Thresholds
    # --------------------------------------------------

    minimum_similarity: float = 0.35

    high_similarity: float = 0.85

    medium_similarity: float = 0.65

    low_similarity: float = 0.45