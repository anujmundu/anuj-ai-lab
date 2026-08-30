from dataclasses import dataclass


@dataclass(slots=True)
class PromptQualityConfig:
    """
    Configuration for PromptQuality.

    Evaluates the balance of prompt composition
    using token distribution.
    """

    enabled: bool = True

    balanced_ratio_difference: float = 0.25