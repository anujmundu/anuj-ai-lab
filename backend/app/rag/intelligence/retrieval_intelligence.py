from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.multi_query_retriever import (
    multi_query_retriever,
)
from app.rag.query.models import QueryAnalysisResult
from app.rag.parent_context_resolver import (
    parent_context_resolver,
)


class RetrievalIntelligence:
    """
    Entry point for all retrieval operations.

    Receives query analysis from the retrieval pipeline
    and delegates retrieval planning to RetrievalPlanner.

    The selected retrieval strategy determines whether
    retrieval is performed through the standard HybridRetriever
    or the MultiQueryRetriever.

    After retrieval, parent context is resolved from the
    retrieved child chunks without modifying the original
    retrieval results.

    Metadata filters are forwarded only when the planner
    actually extracted filters from the query. Empty filters
    are intentionally omitted from downstream calls.
    """

    def retrieve(
        self,
        *,
        query: str,
        k: int,
        analysis: QueryAnalysisResult,
        profiler=None,
    ):
        from app.rag.intelligence.retrieval_planner import (
            retrieval_planner,
        )

        strategy = retrieval_planner.plan(
            query=query,
            k=k,
            analysis=analysis,
        )

        retrieval_kwargs = {
            "query": strategy.query,
            "k": strategy.k,
            "profiler": profiler,
        }

        if strategy.multi_query:
            retrieval_kwargs["analysis"] = analysis

        if strategy.filters:
            retrieval_kwargs["filters"] = strategy.filters

        if strategy.multi_query:
            results = multi_query_retriever.retrieve(
                **retrieval_kwargs,
            )
        elif strategy.hyde:
            from app.rag.intelligence.hyde_retrieval import (
                hyde_retrieval,
            )
            try:
                hyde_result = hyde_retrieval.generate(
                    strategy.query,
                )
                retrieval_kwargs["dense_query"] = (
                    hyde_result.hypothetical_document
                )
            except Exception:
                # Graceful fallback to standard hybrid retrieval if LLM call fails
                pass

            results = hybrid_retriever.retrieve(
                **retrieval_kwargs,
            )
        else:
            results = hybrid_retriever.retrieve(
                **retrieval_kwargs,
            )

        retrieved_results = results.get(
            "results",
            [],
        )

        if retrieved_results and all(
            hasattr(result, "parent_id")
            and hasattr(result, "child_id")
            for result in retrieved_results
        ):
            parent_contexts = parent_context_resolver.resolve(
                retrieved_results,
            )
        else:
            parent_contexts = ()

        results["parent_contexts"] = parent_contexts
        results["strategy"] = strategy
        results["effective_k"] = strategy.k

        return results


retrieval_intelligence = RetrievalIntelligence()