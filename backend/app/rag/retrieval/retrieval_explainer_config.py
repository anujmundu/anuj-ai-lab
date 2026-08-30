from dataclasses import dataclass


@dataclass(slots=True)
class RetrievalExplainerConfig:
    """
    Configuration for RetrievalExplainer.
    """

    enabled: bool = True

    semantic_high: float = 0.70

    semantic_medium: float = 0.50

    keyword_high: float = 0.50

    combined_high: float = 0.70