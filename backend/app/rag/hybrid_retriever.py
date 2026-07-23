from contextlib import nullcontext

from app.rag.enums import PerformanceStageName
from app.rag.performance_profiler import PerformanceProfiler
from app.rag.base_retriever import BaseRetriever
from app.rag.keyword_retriever import keyword_retriever
from app.rag.result_fusion import result_fusion
from app.rag.retrieval_config import RetrievalConfig
from app.rag.retrieval_filter import retrieval_filter
from app.rag.retriever import retriever
from app.rag.semantic_reranker import semantic_reranker


class SemanticRetriever(BaseRetriever):
    """
    Adapter around the semantic vector retriever.
    """

    def retrieve(
        self,
        query: str,
        k: int = 3,
        profiler: PerformanceProfiler | None = None,
    ):
        return retriever.retrieve(
            query=query,
            k=k,
            profiler=profiler,
        )


class HybridRetriever(BaseRetriever):
    """
    Hybrid retrieval pipeline.

        Semantic Retriever
                │
        Keyword Retriever
                │
          Result Fusion
                │
        Retrieval Filter
                │
          Final Results
    """

    def __init__(
        self,
        config: RetrievalConfig | None = None,
    ):

        self.config = config or RetrievalConfig()

        self.semantic = SemanticRetriever()
        self.keyword = keyword_retriever

    @property
    def strategy(self) -> str:
        return self.config.retrieval_strategy

    def _use_semantic(self) -> bool:
        return self.strategy in (
            "semantic",
            "hybrid",
        )

    def _use_keyword(self) -> bool:
        return self.strategy in (
            "keyword",
            "hybrid",
        )

    def retrieve(
        self,
        query: str,
        k: int | None = None,
        profiler: PerformanceProfiler | None = None,
    ) -> dict:

        k = k or self.config.top_k
        
        measure = (
            profiler.measure
            if profiler is not None
            else lambda *_: nullcontext()
        )

        semantic_results = None
        keyword_results = None

        if self._use_semantic():
            candidate_k = max(
                k * semantic_reranker.config.candidate_multiplier,
                semantic_reranker.config.minimum_candidates,
            )

            candidate_k = min(
                candidate_k,
                semantic_reranker.config.maximum_candidates,
            )

            with measure(
                PerformanceStageName.SEMANTIC_RETRIEVAL
            ):
                semantic_results = self.semantic.retrieve(
                    query=query,
                    k=candidate_k,
                    profiler=profiler,
                )

            with measure(
                PerformanceStageName.SEMANTIC_RERANKER
            ):
                semantic_results = semantic_reranker.rerank(
                    query=query,
                    results=semantic_results,
                )
    
            semantic_results["requested_k"] = k

        if self._use_keyword():
            with measure(
                PerformanceStageName.BM25_SEARCH
            ):
                keyword_results = self.keyword.retrieve(
                    query=query,
                    k=k,
                )

        with measure(
            PerformanceStageName.RANK_FUSION
        ):
            fused_results = result_fusion.combine(
                semantic=semantic_results,
                keyword=keyword_results,
                k=k,
            )

        with measure(
            PerformanceStageName.RETRIEVAL_FILTERING
        ):
            filtered_results = retrieval_filter.apply(
                results=fused_results,
                k=k,
            )

        filtered_results["pipeline"] = {
            "strategy": self.strategy,
            "semantic_candidates": (
                len(semantic_results["ids"][0])
                if semantic_results
                else 0
            ),
            "keyword_candidates": (
                len(keyword_results["ids"][0])
                if keyword_results
                else 0
            ),
            "fused_candidates": len(
                fused_results["ids"][0]
            ),
            "filtered_candidates": len(
                filtered_results["ids"][0]
            ),
        }
        print(filtered_results.keys())
        return filtered_results


hybrid_retriever = HybridRetriever()