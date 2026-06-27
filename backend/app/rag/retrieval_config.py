from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class RetrievalConfig:
    """
    Configuration for retrieval.

    This configuration controls:

    • Retrieval engines
    • Result fusion
    • Retrieval quality
    • Future retrieval strategies

    The goal is to keep the retrieval pipeline
    configurable without modifying the implementation.
    """

    # --------------------------------------------------
    # Retrieval
    # --------------------------------------------------

    top_k: int = 5

    enable_semantic: bool = True

    enable_keyword: bool = True

    # --------------------------------------------------
    # Score Fusion
    # --------------------------------------------------

    fusion_strategy: Literal[
        "weighted",
        "rrf"
    ] = "weighted"

    semantic_weight: float = 0.70

    keyword_weight: float = 0.30

    normalize_scores: bool = True

    # --------------------------------------------------
    # Reciprocal Rank Fusion
    # --------------------------------------------------

    rrf_k: int = 60

    # --------------------------------------------------
    # Retrieval Quality
    # --------------------------------------------------

    # Minimum acceptable semantic similarity.
    # Results below this threshold are discarded.
    min_semantic_score: float = 0.35

    # Prevent one document from dominating
    # the retrieved context.
    max_chunks_per_document: int = 2

    # Try to spread retrieved chunks across
    # multiple documents.
    diversify_documents: bool = False

    # Remove chunks that are nearly identical.
    remove_near_duplicates: bool = True

    # Lexical similarity threshold used by
    # the duplicate filter.
    duplicate_similarity_threshold: float = 0.85