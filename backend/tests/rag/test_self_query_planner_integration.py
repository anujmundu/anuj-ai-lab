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


def test_planner_preserves_plain_query_without_filters():

    planner = RetrievalPlanner()

    strategy = planner.plan(
        query="machine learning fundamentals",
        k=5,
        analysis=make_analysis(),
    )

    assert isinstance(
        strategy,
        RetrievalStrategy,
    )

    assert strategy.query == (
        "machine learning fundamentals"
    )

    assert strategy.filters == {}

    assert strategy.self_query is False


def test_planner_extracts_filename_filter():

    planner = RetrievalPlanner()

    strategy = planner.plan(
        query=(
            "machine learning "
            "filename research.pdf"
        ),
        k=5,
        analysis=make_analysis(),
    )

    assert strategy.query == (
        "machine learning"
    )

    assert strategy.filters == {
        "filename": "research.pdf",
    }

    assert strategy.self_query is True


def test_planner_extracts_multiple_filters():

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

    assert strategy.query == (
        "machine learning"
    )

    assert strategy.filters == {
        "filename": "research.pdf",
        "document_type": "pdf",
    }

    assert strategy.self_query is True


def test_planner_keeps_original_analysis():

    planner = RetrievalPlanner()

    analysis = make_analysis(
        intent=QueryIntent.RESEARCH,
        complexity=QueryComplexity.COMPLEX,
        ambiguity=QueryAmbiguity.MEDIUM,
        requires_rewrite=True,
        requires_multi_query=False,
    )

    strategy = planner.plan(
        query=(
            "retrieval systems "
            "filename research.pdf"
        ),
        k=5,
        analysis=analysis,
    )

    assert strategy.analysis is analysis


def test_self_query_does_not_change_dynamic_k():

    planner = RetrievalPlanner()

    plain = planner.plan(
        query="retrieval systems",
        k=5,
        analysis=make_analysis(
            complexity=QueryComplexity.COMPLEX,
        ),
    )

    filtered = planner.plan(
        query=(
            "retrieval systems "
            "filename research.pdf"
        ),
        k=5,
        analysis=make_analysis(
            complexity=QueryComplexity.COMPLEX,
        ),
    )

    assert filtered.k == plain.k


def test_self_query_does_not_change_multi_query_decision():

    planner = RetrievalPlanner()

    strategy = planner.plan(
        query=(
            "compare retrieval systems "
            "filename research.pdf"
        ),
        k=5,
        analysis=make_analysis(
            intent=QueryIntent.COMPARISON,
            requires_multi_query=True,
        ),
    )

    assert strategy.multi_query is True

    assert strategy.filters == {
        "filename": "research.pdf",
    }

    assert strategy.self_query is True


def test_self_query_does_not_change_hyde_decision():

    planner = RetrievalPlanner()

    strategy = planner.plan(
        query=(
            "explain retrieval augmented "
            "generation filename research.pdf"
        ),
        k=5,
        analysis=make_analysis(
            intent=QueryIntent.EXPLANATION,
            complexity=QueryComplexity.COMPLEX,
        ),
    )

    assert strategy.hyde is True

    assert strategy.filters == {
        "filename": "research.pdf",
    }

    assert strategy.self_query is True


def test_strategy_is_deterministic():

    planner = RetrievalPlanner()

    query = (
        "machine learning "
        "filename research.pdf "
        "document type pdf"
    )

    analysis = make_analysis()

    first = planner.plan(
        query=query,
        k=5,
        analysis=analysis,
    )

    second = planner.plan(
        query=query,
        k=5,
        analysis=analysis,
    )

    assert first == second


def test_strategy_filters_are_independent_between_calls():

    planner = RetrievalPlanner()

    first = planner.plan(
        query=(
            "python filename first.pdf"
        ),
        k=5,
        analysis=make_analysis(),
    )

    second = planner.plan(
        query=(
            "python filename second.pdf"
        ),
        k=5,
        analysis=make_analysis(),
    )

    assert first.filters == {
        "filename": "first.pdf",
    }

    assert second.filters == {
        "filename": "second.pdf",
    }

    assert first.filters is not second.filters