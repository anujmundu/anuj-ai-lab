from app.rag.base_retriever import BaseRetriever
from app.rag.keyword_retriever import keyword_retriever
from app.rag.result_fusion import result_fusion
from app.rag.retrieval_config import RetrievalConfig
from app.rag.retriever import retriever


class SemanticRetriever(BaseRetriever):
    """
    Adapter around the semantic vector retriever.
    """

    def retrieve(
        self,
        query: str,
        k: int = 3
    ):

        return retriever.retrieve(
            query=query,
            k=k
        )


class HybridRetriever(BaseRetriever):
    """
    Hybrid retrieval engine.

    Current retrieval engines:

    • Semantic Search
    • Keyword Search

    Future retrieval engines:

    • BM25
    • Elasticsearch
    • OpenSearch
    • SQLite FTS5
    """

    def __init__(
        self,
        config: RetrievalConfig | None = None
    ):

        self.config = config or RetrievalConfig()

        self.semantic = SemanticRetriever()

        self.keyword = keyword_retriever

    def retrieve(
        self,
        query: str,
        k: int | None = None
    ):

        k = k or self.config.top_k

        semantic_results = None
        keyword_results = None

        if self.config.enable_semantic:

            semantic_results = self.semantic.retrieve(
                query=query,
                k=k
            )

        if self.config.enable_keyword:

            keyword_results = self.keyword.retrieve(
                query=query,
                k=k
            )

        return result_fusion.combine(
            semantic=semantic_results,
            keyword=keyword_results,
            k=k
        )


hybrid_retriever = HybridRetriever()