from unittest.mock import Mock, patch

from app.rag.intelligence.retrieval_intelligence import (
    RetrievalIntelligence,
)
from app.rag.intelligence.retrieval_strategy import (
    RetrievalStrategy,
)
from app.rag.query.enums import (
    QueryAmbiguity,
    QueryComplexity,
    QueryIntent,
)
from app.rag.query.models import QueryAnalysisResult


def make_analysis(
    *,
    requires_multi_query: bool,
) -> QueryAnalysisResult:

    return QueryAnalysisResult(
        query="test query",
        intent=QueryIntent.RESEARCH,
        complexity=QueryComplexity.MEDIUM,
        ambiguity=QueryAmbiguity.LOW,
        requires_rewrite=False,
        requires_multi_query=requires_multi_query,
    )


def make_strategy(
    *,
    multi_query: bool,
    k: int,
) -> RetrievalStrategy:

    return RetrievalStrategy(
        query="planned query",
        k=k,
        analysis=make_analysis(
            requires_multi_query=multi_query,
        ),
        rewrite=False,
        expand=False,
        multi_query=multi_query,
    )


def test_multi_query_true_dispatches_to_multi_query_retriever():

    intelligence = RetrievalIntelligence()

    analysis = make_analysis(
        requires_multi_query=True,
    )

    strategy = make_strategy(
        multi_query=True,
        k=8,
    )

    multi_query_results = {
        "results": [
            {"chunk_id": "chunk-1"},
        ],
    }

    with patch(
        "app.rag.intelligence.retrieval_planner."
        "retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence."
        "multi_query_retriever"
    ) as multi_query, patch(
        "app.rag.intelligence.retrieval_intelligence."
        "hybrid_retriever"
    ) as hybrid:

        planner.plan.return_value = strategy

        multi_query.retrieve.return_value = (
            multi_query_results
        )

        result = intelligence.retrieve(
            query="original query",
            k=5,
            analysis=analysis,
            profiler=None,
        )

    planner.plan.assert_called_once_with(
        query="original query",
        k=5,
        analysis=analysis,
    )

    multi_query.retrieve.assert_called_once_with(
        query="planned query",
        k=8,
        analysis=analysis,
        profiler=None,
    )

    hybrid.retrieve.assert_not_called()

    assert result["results"] == [
        {"chunk_id": "chunk-1"},
    ]


def test_multi_query_false_dispatches_to_hybrid_retriever():

    intelligence = RetrievalIntelligence()

    analysis = make_analysis(
        requires_multi_query=False,
    )

    strategy = make_strategy(
        multi_query=False,
        k=6,
    )

    hybrid_results = {
        "results": [
            {"chunk_id": "chunk-2"},
        ],
    }

    with patch(
        "app.rag.intelligence.retrieval_planner."
        "retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence."
        "multi_query_retriever"
    ) as multi_query, patch(
        "app.rag.intelligence.retrieval_intelligence."
        "hybrid_retriever"
    ) as hybrid:

        planner.plan.return_value = strategy

        hybrid.retrieve.return_value = (
            hybrid_results
        )

        result = intelligence.retrieve(
            query="original query",
            k=5,
            analysis=analysis,
            profiler=None,
        )

    planner.plan.assert_called_once_with(
        query="original query",
        k=5,
        analysis=analysis,
    )

    hybrid.retrieve.assert_called_once_with(
        query="planned query",
        k=6,
        profiler=None,
    )

    multi_query.retrieve.assert_not_called()

    assert result["results"] == [
        {"chunk_id": "chunk-2"},
    ]


def test_planner_selected_k_is_passed_downstream():

    intelligence = RetrievalIntelligence()

    analysis = make_analysis(
        requires_multi_query=True,
    )

    strategy = make_strategy(
        multi_query=True,
        k=11,
    )

    with patch(
        "app.rag.intelligence.retrieval_planner."
        "retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence."
        "multi_query_retriever"
    ) as multi_query:

        planner.plan.return_value = strategy

        multi_query.retrieve.return_value = {
            "results": [],
        }

        intelligence.retrieve(
            query="original query",
            k=3,
            analysis=analysis,
            profiler=None,
        )

    call = multi_query.retrieve.call_args

    assert call.kwargs["k"] == 11


def test_returned_effective_k_equals_strategy_k():

    intelligence = RetrievalIntelligence()

    analysis = make_analysis(
        requires_multi_query=False,
    )

    strategy = make_strategy(
        multi_query=False,
        k=9,
    )

    with patch(
        "app.rag.intelligence.retrieval_planner."
        "retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence."
        "hybrid_retriever"
    ) as hybrid:

        planner.plan.return_value = strategy

        hybrid.retrieve.return_value = {
            "results": [],
        }

        result = intelligence.retrieve(
            query="original query",
            k=4,
            analysis=analysis,
            profiler=None,
        )

    assert result["effective_k"] == strategy.k


def test_returned_strategy_is_planners_strategy():

    intelligence = RetrievalIntelligence()

    analysis = make_analysis(
        requires_multi_query=True,
    )

    strategy = make_strategy(
        multi_query=True,
        k=7,
    )

    with patch(
        "app.rag.intelligence.retrieval_planner."
        "retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence."
        "multi_query_retriever"
    ) as multi_query:

        planner.plan.return_value = strategy

        multi_query.retrieve.return_value = {
            "results": [],
        }

        result = intelligence.retrieve(
            query="original query",
            k=5,
            analysis=analysis,
            profiler=None,
        )

    assert result["strategy"] is strategy


def test_profiler_is_forwarded_to_selected_retriever():

    intelligence = RetrievalIntelligence()

    analysis = make_analysis(
        requires_multi_query=True,
    )

    strategy = make_strategy(
        multi_query=True,
        k=8,
    )

    profiler = Mock()

    with patch(
        "app.rag.intelligence.retrieval_planner."
        "retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence."
        "multi_query_retriever"
    ) as multi_query:

        planner.plan.return_value = strategy

        multi_query.retrieve.return_value = {
            "results": [],
        }

        intelligence.retrieve(
            query="original query",
            k=5,
            analysis=analysis,
            profiler=profiler,
        )

    call = multi_query.retrieve.call_args

    assert call.kwargs["profiler"] is profiler