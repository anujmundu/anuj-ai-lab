from app.rag.query.enums import (
    QueryComplexity,
    QueryIntent,
)
from app.rag.query.models import QueryAnalysisResult
from app.rag.query.query_decomposer import (
    query_decomposer,
)


def make_analysis(
    *,
    intent: QueryIntent,
    complexity: QueryComplexity,
) -> QueryAnalysisResult:

    return QueryAnalysisResult(
        query="test query",
        intent=intent,
        complexity=complexity,
        ambiguity="low",
        requires_rewrite=False,
        requires_multi_query=True,
    )


def test_complex_comparison_query_is_decomposed():

    analysis = make_analysis(
        intent=QueryIntent.COMPARISON,
        complexity=QueryComplexity.COMPLEX,
    )

    result = query_decomposer.decompose(
        query=(
            "Compare Python and Java for AI development "
            "including performance, libraries and deployment"
        ),
        analysis=analysis,
    )

    assert result.decomposed is True
    assert result.original_query == (
        "Compare Python and Java for AI development "
        "including performance, libraries and deployment"
    )

    assert len(result.sub_queries) >= 3


def test_simple_query_is_not_decomposed():

    analysis = make_analysis(
        intent=QueryIntent.DEFINITION,
        complexity=QueryComplexity.SIMPLE,
    )

    result = query_decomposer.decompose(
        query="What is Python?",
        analysis=analysis,
    )

    assert result.decomposed is False
    assert result.sub_queries == []


def test_medium_query_is_not_decomposed():

    analysis = make_analysis(
        intent=QueryIntent.RESEARCH,
        complexity=QueryComplexity.MEDIUM,
    )

    result = query_decomposer.decompose(
        query="Explain retrieval augmented generation",
        analysis=analysis,
    )

    assert result.decomposed is False
    assert result.sub_queries == []


def test_empty_query_returns_no_sub_queries():

    analysis = make_analysis(
        intent=QueryIntent.RESEARCH,
        complexity=QueryComplexity.COMPLEX,
    )

    result = query_decomposer.decompose(
        query="   ",
        analysis=analysis,
    )

    assert result.decomposed is False
    assert result.sub_queries == []


def test_sub_queries_are_unique():

    analysis = make_analysis(
        intent=QueryIntent.COMPARISON,
        complexity=QueryComplexity.COMPLEX,
    )

    result = query_decomposer.decompose(
        query=(
            "Compare Python and Java "
            "including performance and libraries"
        ),
        analysis=analysis,
    )

    assert len(result.sub_queries) == len(
        set(result.sub_queries)
    )