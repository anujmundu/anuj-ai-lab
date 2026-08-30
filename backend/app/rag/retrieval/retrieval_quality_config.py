from dataclasses import dataclass


@dataclass(slots=True)
class RetrievalQualityConfig:
    """
    Configuration for RetrievalQuality.

    Controls how overall retrieval quality is
    estimated from the retrieved documents.

    This component is diagnostic-only and never
    changes retrieval results.
    """

    # --------------------------------------------------
    # Detection
    # --------------------------------------------------

    enabled: bool = True

    # --------------------------------------------------
    # Quality Thresholds
    # --------------------------------------------------

    excellent_coverage: float = 0.75

    good_coverage: float = 0.60

    fair_coverage: float = 0.40

    # --------------------------------------------------
    # Redundancy
    # --------------------------------------------------

    nearby_chunk_distance: int = 1

    # --------------------------------------------------
    # Numerical Stability
    # --------------------------------------------------

    epsilon: float = 1e-9