from unittest.mock import Mock, patch

from app.rag.intelligence.retrieval_intelligence import (
    RetrievalIntelligence,
)
from app.rag.intelligence.retrieval_strategy import (
    RetrievalStrategy,
)
from app.rag.parent_child import ParentChunk
from app.rag.parent_context_resolver import (
    ResolvedParentContext,
)
from app.rag.query.enums import (
    QueryAmbiguity,
    QueryComplexity,
    QueryIntent,
)
from app.rag.query.models import QueryAnalysisResult
from app.rag.retrieval_models import (
    RetrievalMetadata,
    RetrievalResult,
    RetrievalScores,
)


def make_analysis(
    *,
    requires_multi_query: bool = False,
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
    multi_query: bool = False,
    hyde: bool = False,
    k: int = 7,
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
        hyde=hyde,
    )


def make_result(
    *,
    child_id: str,
    parent_id: str,
) -> RetrievalResult:

    return RetrievalResult(
        doc_id=child_id,
        document=f"Content for {child_id}",
        metadata=RetrievalMetadata(
            filename="document.txt",
            chunk_id=child_id,
            parent_id=parent_id,
            child_id=child_id,
            chunk_number=1,
            total_chunks=2,
            source="test",
        ),
        scores=RetrievalScores(
            semantic_score=0.9,
            keyword_score=0.8,
            combined_score=0.85,
        ),
    )


def make_parent_context(
    *,
    parent_id: str,
    child_ids: tuple[str, ...],
) -> ResolvedParentContext:

    return ResolvedParentContext(
        parent=ParentChunk(
            parent_id=parent_id,
            text="Parent context",
            index=0,
        ),
        child_ids=child_ids,
    )


def test_strategy_controls_retriever_and_k():

    intelligence = RetrievalIntelligence()

    analysis = make_analysis(
        requires_multi_query=True,
    )

    strategy = make_strategy(
        multi_query=True,
        k=11,
    )

    with patch(
        "app.rag.intelligence.retrieval_planner.retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence.multi_query_retriever"
    ) as multi_query, patch(
        "app.rag.intelligence.retrieval_intelligence.hybrid_retriever"
    ) as hybrid, patch(
        "app.rag.intelligence.retrieval_intelligence.parent_context_resolver"
    ) as resolver:

        planner.plan.return_value = strategy

        multi_query.retrieve.return_value = {
            "results": [],
        }

        resolver.resolve.return_value = ()

        result = intelligence.retrieve(
            query="original query",
            k=3,
            analysis=analysis,
            profiler=None,
        )

    multi_query.retrieve.assert_called_once_with(
        query="planned query",
        k=11,
        analysis=analysis,
        profiler=None,
    )

    hybrid.retrieve.assert_not_called()

    assert result["strategy"] is strategy
    assert result["effective_k"] == 11


def test_hybrid_strategy_preserves_strategy_contract():

    intelligence = RetrievalIntelligence()

    analysis = make_analysis()

    strategy = make_strategy(
        multi_query=False,
        k=9,
    )

    with patch(
        "app.rag.intelligence.retrieval_planner.retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence.hybrid_retriever"
    ) as hybrid, patch(
        "app.rag.intelligence.retrieval_intelligence.multi_query_retriever"
    ) as multi_query, patch(
        "app.rag.intelligence.retrieval_intelligence.parent_context_resolver"
    ) as resolver:

        planner.plan.return_value = strategy

        hybrid.retrieve.return_value = {
            "results": [],
        }

        resolver.resolve.return_value = ()

        result = intelligence.retrieve(
            query="original query",
            k=2,
            analysis=analysis,
            profiler=None,
        )

    hybrid.retrieve.assert_called_once_with(
        query="planned query",
        k=9,
        profiler=None,
    )

    multi_query.retrieve.assert_not_called()

    assert result["strategy"] is strategy
    assert result["effective_k"] == strategy.k


def test_retrieved_children_and_parent_context_are_separate():

    intelligence = RetrievalIntelligence()

    strategy = make_strategy(
        k=8,
    )

    child = make_result(
        child_id="child-1",
        parent_id="parent-1",
    )

    parent_context = make_parent_context(
        parent_id="parent-1",
        child_ids=("child-1",),
    )

    with patch(
        "app.rag.intelligence.retrieval_planner.retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence.hybrid_retriever"
    ) as hybrid, patch(
        "app.rag.intelligence.retrieval_intelligence.parent_context_resolver"
    ) as resolver:

        planner.plan.return_value = strategy

        hybrid.retrieve.return_value = {
            "results": [child],
        }

        resolver.resolve.return_value = (
            parent_context,
        )

        result = intelligence.retrieve(
            query="original query",
            k=5,
            analysis=make_analysis(),
            profiler=None,
        )

    assert result["results"] == [child]

    assert result["parent_contexts"] == (
        parent_context,
    )

    assert result["results"][0] is child

    assert result["parent_contexts"][0] is parent_context


def test_multiple_children_are_grouped_under_one_parent():

    intelligence = RetrievalIntelligence()

    strategy = make_strategy(
        k=8,
    )

    first = make_result(
        child_id="child-1",
        parent_id="parent-1",
    )

    second = make_result(
        child_id="child-2",
        parent_id="parent-1",
    )

    context = make_parent_context(
        parent_id="parent-1",
        child_ids=(
            "child-1",
            "child-2",
        ),
    )

    with patch(
        "app.rag.intelligence.retrieval_planner.retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence.hybrid_retriever"
    ) as hybrid, patch(
        "app.rag.intelligence.retrieval_intelligence.parent_context_resolver"
    ) as resolver:

        planner.plan.return_value = strategy

        hybrid.retrieve.return_value = {
            "results": [
                first,
                second,
            ],
        }

        resolver.resolve.return_value = (
            context,
        )

        result = intelligence.retrieve(
            query="original query",
            k=5,
            analysis=make_analysis(),
            profiler=None,
        )

    resolver.resolve.assert_called_once_with(
        [
            first,
            second,
        ]
    )

    assert result["results"] == [
        first,
        second,
    ]

    assert result["parent_contexts"] == (
        context,
    )


def test_multi_query_and_parent_context_compose():

    intelligence = RetrievalIntelligence()

    analysis = make_analysis(
        requires_multi_query=True,
    )

    strategy = make_strategy(
        multi_query=True,
        k=10,
    )

    child = make_result(
        child_id="child-1",
        parent_id="parent-1",
    )

    context = make_parent_context(
        parent_id="parent-1",
        child_ids=("child-1",),
    )

    profiler = Mock()

    with patch(
        "app.rag.intelligence.retrieval_planner.retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence.multi_query_retriever"
    ) as multi_query, patch(
        "app.rag.intelligence.retrieval_intelligence.hybrid_retriever"
    ) as hybrid, patch(
        "app.rag.intelligence.retrieval_intelligence.parent_context_resolver"
    ) as resolver:

        planner.plan.return_value = strategy

        multi_query.retrieve.return_value = {
            "results": [child],
        }

        resolver.resolve.return_value = (
            context,
        )

        result = intelligence.retrieve(
            query="original query",
            k=5,
            analysis=analysis,
            profiler=profiler,
        )

    multi_query.retrieve.assert_called_once_with(
        query="planned query",
        k=10,
        analysis=analysis,
        profiler=profiler,
    )

    hybrid.retrieve.assert_not_called()

    resolver.resolve.assert_called_once_with(
        [child]
    )

    assert result["results"] == [child]
    assert result["parent_contexts"] == (context,)
    assert result["strategy"] is strategy
    assert result["effective_k"] == 10


def test_hyde_flag_is_preserved_in_strategy():

    intelligence = RetrievalIntelligence()

    strategy = make_strategy(
        hyde=True,
        k=7,
    )

    with patch(
        "app.rag.intelligence.retrieval_planner.retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence.hybrid_retriever"
    ) as hybrid, patch(
        "app.rag.intelligence.retrieval_intelligence.parent_context_resolver"
    ) as resolver:

        planner.plan.return_value = strategy

        hybrid.retrieve.return_value = {
            "results": [],
        }

        resolver.resolve.return_value = ()

        result = intelligence.retrieve(
            query="original query",
            k=5,
            analysis=make_analysis(),
            profiler=None,
        )

    assert result["strategy"].hyde is True
    assert result["effective_k"] == 7
    assert result["parent_contexts"] == ()


def test_empty_retrieval_produces_empty_parent_context():

    intelligence = RetrievalIntelligence()

    strategy = make_strategy()

    with patch(
        "app.rag.intelligence.retrieval_planner.retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence.hybrid_retriever"
    ) as hybrid, patch(
        "app.rag.intelligence.retrieval_intelligence.parent_context_resolver"
    ) as resolver:

        planner.plan.return_value = strategy

        hybrid.retrieve.return_value = {
            "results": [],
        }

        resolver.resolve.return_value = ()

        result = intelligence.retrieve(
            query="original query",
            k=5,
            analysis=make_analysis(),
            profiler=None,
        )

    assert result["results"] == []
    assert result["parent_contexts"] == ()

    resolver.resolve.assert_not_called()


def test_non_retrieval_compatible_results_are_preserved():

    intelligence = RetrievalIntelligence()

    strategy = make_strategy()

    raw_result = {
        "chunk_id": "legacy-child",
    }

    with patch(
        "app.rag.intelligence.retrieval_planner.retrieval_planner"
    ) as planner, patch(
        "app.rag.intelligence.retrieval_intelligence.hybrid_retriever"
    ) as hybrid, patch(
        "app.rag.intelligence.retrieval_intelligence.parent_context_resolver"
    ) as resolver:

        planner.plan.return_value = strategy

        hybrid.retrieve.return_value = {
            "results": [raw_result],
        }

        result = intelligence.retrieve(
            query="original query",
            k=5,
            analysis=make_analysis(),
            profiler=None,
        )

    assert result["results"] == [raw_result]
    assert result["parent_contexts"] == ()

    resolver.resolve.assert_not_called()
