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


def make_analysis() -> QueryAnalysisResult:
    return QueryAnalysisResult(
        query="test query",
        intent=QueryIntent.RESEARCH,
        complexity=QueryComplexity.MEDIUM,
        ambiguity=QueryAmbiguity.LOW,
        requires_rewrite=False,
        requires_multi_query=False,
    )


def make_strategy(
    *,
    k: int = 5,
) -> RetrievalStrategy:
    return RetrievalStrategy(
        query="planned query",
        k=k,
        analysis=make_analysis(),
        rewrite=False,
        expand=False,
        multi_query=False,
    )


def make_retrieval_result(
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


def test_retrieval_intelligence_can_attach_resolved_parent_context():
    intelligence = RetrievalIntelligence()

    strategy = make_strategy(k=7)

    retrieval_result = make_retrieval_result(
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
            "results": [retrieval_result],
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

    assert result["results"] == [retrieval_result]
    assert result["strategy"] is strategy
    assert result["effective_k"] == 7
    assert result["parent_contexts"] == (
        parent_context,
    )


def test_parent_context_resolver_receives_retrieved_results():
    intelligence = RetrievalIntelligence()

    strategy = make_strategy()

    retrieval_result = make_retrieval_result(
        child_id="child-1",
        parent_id="parent-1",
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
            "results": [retrieval_result],
        }

        resolver.resolve.return_value = ()

        intelligence.retrieve(
            query="original query",
            k=5,
            analysis=make_analysis(),
            profiler=None,
        )

    resolver.resolve.assert_called_once_with(
        [retrieval_result],
    )


def test_parent_context_resolution_preserves_retrieval_results():
    intelligence = RetrievalIntelligence()

    strategy = make_strategy(k=8)

    first = make_retrieval_result(
        child_id="child-1",
        parent_id="parent-1",
    )

    second = make_retrieval_result(
        child_id="child-2",
        parent_id="parent-1",
    )

    resolved_context = make_parent_context(
        parent_id="parent-1",
        child_ids=("child-1", "child-2"),
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
            "results": [first, second],
        }

        resolver.resolve.return_value = (
            resolved_context,
        )

        result = intelligence.retrieve(
            query="original query",
            k=3,
            analysis=make_analysis(),
            profiler=None,
        )

    assert result["results"] == [
        first,
        second,
    ]

    assert result["parent_contexts"] == (
        resolved_context,
    )


def test_empty_retrieval_results_produce_empty_parent_context():
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


def test_missing_parent_context_does_not_remove_retrieved_children():
    intelligence = RetrievalIntelligence()

    strategy = make_strategy()

    retrieval_result = make_retrieval_result(
        child_id="child-1",
        parent_id="unknown-parent",
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
            "results": [retrieval_result],
        }

        resolver.resolve.return_value = ()

        result = intelligence.retrieve(
            query="original query",
            k=5,
            analysis=make_analysis(),
            profiler=None,
        )

    assert result["results"] == [
        retrieval_result,
    ]

    assert result["parent_contexts"] == ()


def test_profiler_remains_forwarded_to_selected_retriever():
    intelligence = RetrievalIntelligence()

    strategy = make_strategy()

    profiler = Mock()

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

        intelligence.retrieve(
            query="original query",
            k=5,
            analysis=make_analysis(),
            profiler=profiler,
        )

    hybrid.retrieve.assert_called_once_with(
        query="planned query",
        k=strategy.k,
        profiler=profiler,
    )