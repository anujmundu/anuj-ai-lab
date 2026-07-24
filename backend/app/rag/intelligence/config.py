from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalIntelligenceConfig:
    """
    Global configuration for Retrieval Intelligence.

    Initially all advanced capabilities are disabled.
    """

    enable_query_rewriting: bool = False

    enable_query_expansion: bool = False

    enable_multi_query: bool = False

    enable_adaptive_retrieval: bool = False


retrieval_intelligence_config = RetrievalIntelligenceConfig()