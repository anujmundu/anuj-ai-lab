from dataclasses import dataclass


@dataclass(slots=True)
class RAGScorecardConfig:
    """
    Configuration for the end-to-end
    RAG scorecard.
    """

    enabled: bool = True