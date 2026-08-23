from app.rag.intelligence.retrieval_planner import (
    RetrievalPlanner,
)
from app.rag.intelligence.retrieval_strategy import (
    RetrievalStrategy,
)
from app.rag.query.enums import (
    QueryAmbiguity,
    QueryComplexity,
    QueryIntent,
)
from app.rag.query.models import (
    QueryAnalysisResult,
)


def make_analysis(
    *,
    intent=QueryIntent.FACTUAL,
    complexity=QueryComplexity.SIMPLE,
    ambiguity=QueryAmbiguity.LOW,
    requires_rewrite=False,
    requires_multi_query=False,
):
    return QueryAnalysisResult(
        query="original query",
        intent=intent,
        complexity=complexity,
        ambiguity=ambiguity,
        requires_rewrite=requires_rewrite,
        requires_multi_query=requires_multi_query,
    )


def test_self_query_semantic_query_is_used_by_strategy():

    planner = RetrievalPlanner()

    strategy = planner.plan(
        query=(
            "machine learning "
            "filename research.pdf"
        ),
        k=5,
        analysis=make_analysis(),
    )

    assert isinstance(
        strategy,
        RetrievalStrategy,
    )

    assert strategy.query == "machine learning"

    assert strategy.filters == {
        "filename": "research.pdf",
    }

    assert strategy.self_query is True


def test_plain_query_has_empty_filters():

    planner = RetrievalPlanner()

    strategy = planner.plan(
        query="machine learning fundamentals",
        k=5,
        analysis=make_analysis(),
    )

    assert strategy.query == (
        "machine learning fundamentals"
    )

    assert strategy.filters == {}

    assert strategy.self_query is False


def test_multiple_self_query_filters_are_preserved():

    planner = RetrievalPlanner()

    strategy = planner.plan(
        query=(
            "machine learning "
            "filename research.pdf "
            "document type pdf"
        ),
        k=5,
        analysis=make_analysis(),
    )

    assert strategy.query == "machine learning"

    assert strategy.filters == {
        "filename": "research.pdf",
        "document_type": "pdf",
    }

    assert strategy.self_query is True


def test_planner_does_not_mutate_original_query():

    planner = RetrievalPlanner()

    query = (
        "machine learning "
        "filename research.pdf"
    )

    planner.plan(
        query=query,
        k=5,
        analysis=make_analysis(),
    )

    assert query == (
        "machine learning "
        "filename research.pdf"
    )


def test_existing_strategy_flags_are_preserved():

    planner = RetrievalPlanner()

    strategy = planner.plan(
        query=(
            "compare retrieval systems "
            "filename research.pdf"
        ),
        k=5,
        analysis=make_analysis(
            intent=QueryIntent.COMPARISON,
            complexity=QueryComplexity.COMPLEX,
            requires_multi_query=True,
        ),
    )

    assert strategy.query == (
        "compare retrieval systems"
    )

    assert strategy.filters == {
        "filename": "research.pdf",
    }

    assert strategy.self_query is True

    assert strategy.multi_query is True

    assert strategy.hyde is False