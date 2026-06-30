from dataclasses import dataclass


@dataclass(slots=True)
class HallucinationDetectorConfig:
    """
    Configuration for HallucinationDetector.

    Controls how hallucination risk is estimated
    without modifying or blocking model responses.
    """

    # --------------------------------------------------
    # Detection
    # --------------------------------------------------

    check_context_overlap: bool = True

    detect_unsupported_terms: bool = True

    estimate_hallucination_risk: bool = True

    # --------------------------------------------------
    # Thresholds
    # --------------------------------------------------

    overlap_threshold: float = 0.60

    risk_threshold: float = 0.50

    # --------------------------------------------------
    # Text Processing
    # --------------------------------------------------

    normalize_text: bool = True

    ignore_case: bool = True