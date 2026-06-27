from app.rag.base_retriever import BaseRetriever
from app.rag.keyword_retriever import keyword_retriever
from app.rag.result_fusion import result_fusion
from app.rag.retrieval_config import RetrievalConfig
from app.rag.retrieval_filter import retrieval_filter
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
    Hybrid retrieval pipeline.

    Pipeline:

        Semantic Retriever
                │
        Keyword Retriever
                │
          Result Fusion
                │
        Retrieval Filter
                │
          Final Results

    This class intentionally contains no ranking or
    filtering logic. It only orchestrates the retrieval
    pipeline.
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
    ) -> dict:

        k = k or self.config.top_k

        semantic_results = None
        keyword_results = None

        #
        # Semantic Retrieval
        #

        if self.config.enable_semantic:

            semantic_results = self.semantic.retrieve(
                query=query,
                k=k
            )

        #
        # Keyword Retrieval
        #

        if self.config.enable_keyword:

            keyword_results = self.keyword.retrieve(
                query=query,
                k=k
            )

        #
        # Merge retrieval engines
        #

        fused_results = result_fusion.combine(
            semantic=semantic_results,
            keyword=keyword_results,
            k=k
        )

        #
        # Improve retrieval quality
        #

        filtered_results = retrieval_filter.apply(
            results=fused_results,
            k=k
        )

        return filtered_results


hybrid_retriever = HybridRetriever()