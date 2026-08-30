from dataclasses import dataclass


@dataclass(slots=True)
class RankerConfig:
    """
    Configuration for the retrieval ranking stage.

    Controls lightweight filtering before
    context construction.

    Future versions will also configure
    reranking and diversification.
    """

    # -----------------------------------------
    # Filtering
    # -----------------------------------------

    minimum_combined_score: float = 0.25

    remove_duplicate_chunks: bool = True

    maximum_chunks: int = 3

    # -----------------------------------------
    # Future
    # -----------------------------------------

    enable_cross_encoder: bool = False

    enable_diversification: bool = False