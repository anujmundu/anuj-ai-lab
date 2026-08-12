from app.rag.query.enums import QueryIntent
from app.rag.query.models import QueryAnalysisResult
from app.rag.query.query_generator import query_generator


def make_analysis(
    *,
    intent: QueryIntent,
    requires_multi_query: bool = True,
) -> QueryAnalysisResult:
    return QueryAnalysisResult(
        query="test query",
        intent=intent,
        complexity="medium",
        ambiguity="low",
        requires_rewrite=False,
        requires_multi_query=requires_multi_query,
    )


def test_comparison_query_generates_three_queries():
    analysis = make_analysis(
        intent=QueryIntent.COMPARISON,
    )

    queries = query_generator.generate(
        query="Compare Python and Java",
        analysis=analysis,
    )

    assert len(queries) == 3

    assert queries[0] == "Compare Python and Java"
    assert queries[1] == "Compare Python and Java comparison"
    assert queries[2] == "differences between Compare Python and Java"


def test_research_query_generates_three_queries():
    analysis = make_analysis(
        intent=QueryIntent.RESEARCH,
    )

    queries = query_generator.generate(
        query="Retrieval augmented generation",
        analysis=analysis,
    )

    assert len(queries) == 3

    assert queries[0] == "Retrieval augmented generation"
    assert queries[1] == (
        "Retrieval augmented generation overview"
    )
    assert queries[2] == (
        "Retrieval augmented generation key concepts"
    )


def test_explanation_query_generates_three_queries():
    analysis = make_analysis(
        intent=QueryIntent.EXPLANATION,
    )

    queries = query_generator.generate(
        query="Explain Python decorators",
        analysis=analysis,
    )

    assert len(queries) == 3

    assert queries[0] == "Explain Python decorators"
    assert queries[1] == (
        "Explain Python decorators explanation"
    )
    assert queries[2] == (
        "Explain Python decorators fundamentals"
    )


def test_default_query_generates_three_queries():
    analysis = make_analysis(
        intent=QueryIntent.DEFINITION,
    )

    queries = query_generator.generate(
        query="What is Python?",
        analysis=analysis,
    )

    assert len(queries) == 3

    assert queries[0] == "What is Python?"
    assert queries[1] == "What is Python? overview"
    assert queries[2] == "What is Python? details"


def test_empty_query_returns_empty_list():
    analysis = make_analysis(
        intent=QueryIntent.RESEARCH,
    )

    queries = query_generator.generate(
        query="   ",
        analysis=analysis,
    )

    assert queries == []


def test_duplicate_queries_are_removed():
    analysis = make_analysis(
        intent=QueryIntent.COMPARISON,
    )

    queries = query_generator.generate(
        query="Compare Python and Java",
        analysis=analysis,
    )

    assert len(queries) == len(set(queries))