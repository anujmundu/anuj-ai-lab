from dataclasses import dataclass


@dataclass(slots=True)
class AnswerQualityConfig:
    """
    Configuration for AnswerQuality.

    Computes descriptive quality metrics for
    generated answers.
    """

    enabled: bool = True

    minimum_sentence_length: int = 3

    readability_good: float = 20.0

    readability_fair: float = 35.0

    repetition_threshold: float = 0.15

    redundancy_threshold: float = 0.10