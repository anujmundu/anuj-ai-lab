from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class RetrievalConfig:
    """
    Configuration for retrieval.

    This configuration controls:

    • which retrieval engines are enabled
    • how scores are fused
    • how many results are returned

    Future commits will extend this with:

    • similarity thresholds
    • diversification
    • maximum chunks per document
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