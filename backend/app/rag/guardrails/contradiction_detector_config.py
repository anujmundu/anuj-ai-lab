from dataclasses import dataclass


@dataclass(slots=True)
class ContradictionDetectorConfig:
    """
    Configuration for contradiction detection.

    This component estimates whether a claim is
    supported, contradicted, or neutral relative
    to retrieved context.

    Current implementation uses heuristic scoring.

    Future implementations may use:

    • DeBERTa NLI
    • RoBERTa MNLI
    • Modern NLI models
    """

    # --------------------------------------------------
    # Master Switches
    # --------------------------------------------------

    enabled: bool = True

    include_similarity: bool = True

    include_explanation: bool = True

    include_diagnostics: bool = True

    # --------------------------------------------------
    # Thresholds
    # --------------------------------------------------

    support_threshold: float = 0.75

    neutral_threshold: float = 0.45