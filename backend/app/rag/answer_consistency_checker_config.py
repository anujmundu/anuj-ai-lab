from dataclasses import dataclass


@dataclass(slots=True)
class AnswerConsistencyCheckerConfig:
    """
    Configuration for AnswerConsistencyChecker.

    Controls how answer consistency is evaluated
    without modifying generated responses.
    """

    # --------------------------------------------------
    # Detection
    # --------------------------------------------------

    enabled: bool = True

    # --------------------------------------------------
    # Sentence Processing
    # --------------------------------------------------

    sentence_split_regex: str = r"(?<=[.!?])\s+"

    ignore_case: bool = True

    minimum_token_length: int = 3

    # --------------------------------------------------
    # Similarity Thresholds
    # --------------------------------------------------

    # Minimum lexical overlap required before two
    # sentences are considered related.
    minimum_overlap: float = 0.30

    # --------------------------------------------------
    # Consistency Thresholds
    # --------------------------------------------------

    # Score >= consistent_threshold
    # → "consistent"
    consistent_threshold: float = 0.75

    # Score >= uncertain_threshold
    # → "uncertain"
    #
    # Otherwise
    # → "needs_review"
    uncertain_threshold: float = 0.50