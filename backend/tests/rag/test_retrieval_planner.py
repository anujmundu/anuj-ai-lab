from app.rag.intelligence.retrieval_planner import retrieval_planner
from app.rag.query.enums import QueryAmbiguity, QueryComplexity, QueryIntent
from app.rag.query.models import QueryAnalysisResult


def make_analysis(
    *,
    intent: QueryIntent,
    complexity: QueryComplexity,
    ambiguity: QueryAmbiguity,
    requires_rewrite: bool = False,
    requires_multi_query: bool = False,
) -> QueryAnalysisResult:
    return QueryAnalysisResult(
        query="test query",
        intent=intent,
        complexity=complexity,
        ambiguity=ambiguity,
        requires_rewrite=requires_rewrite,
        requires_multi_query=requires_multi_query,
    )


def test_simple_definition_uses_standard_retrieval():
    analysis = make_analysis(
        intent=QueryIntent.DEFINITION,
        complexity=QueryComplexity.SIMPLE,
        ambiguity=QueryAmbiguity.MEDIUM,
    )

    strategy = retrieval_planner.plan(
        query="What is Python?",
        k=3,
        analysis=analysis,
    )

    assert strategy.query == "What is Python?"
    assert strategy.k == 3
    assert strategy.rewrite is False
    assert strategy.expand is False
    assert strategy.multi_query is False


def test_comparison_query_enables_multi_query():
    analysis = make_analysis(
        intent=QueryIntent.COMPARISON,
        complexity=QueryComplexity.MEDIUM,
        ambiguity=QueryAmbiguity.MEDIUM,
        requires_multi_query=True,
    )

    strategy = retrieval_planner.plan(
        query="Compare Python and Java",
        k=5,
        analysis=analysis,
    )

    assert strategy.query == "Compare Python and Java"
    assert strategy.k == 5
    assert strategy.multi_query is True


def test_research_query_enables_multi_query():
    analysis = make_analysis(
        intent=QueryIntent.RESEARCH,
        complexity=QueryComplexity.MEDIUM,
        ambiguity=QueryAmbiguity.LOW,
        requires_multi_query=True,
    )

    strategy = retrieval_planner.plan(
        query="Research retrieval augmented generation",
        k=5,
        analysis=analysis,
    )

    assert strategy.multi_query is True


def test_rewrite_requirement_is_preserved():
    analysis = make_analysis(
        intent=QueryIntent.EXPLANATION,
        complexity=QueryComplexity.MEDIUM,
        ambiguity=QueryAmbiguity.HIGH,
        requires_rewrite=True,
        requires_multi_query=False,
    )

    strategy = retrieval_planner.plan(
        query="Explain this",
        k=4,
        analysis=analysis,
    )

    assert strategy.rewrite is True
    assert strategy.query == "Explain this"
    assert strategy.k == 5


def test_multi_query_requirement_is_preserved():
    analysis = make_analysis(
        intent=QueryIntent.RESEARCH,
        complexity=QueryComplexity.COMPLEX,
        ambiguity=QueryAmbiguity.MEDIUM,
        requires_multi_query=True,
    )

    strategy = retrieval_planner.plan(
        query="Analyze retrieval augmented generation systems",
        k=10,
        analysis=analysis,
    )

    assert strategy.multi_query is True
    assert strategy.k == 10


def test_planner_does_not_modify_query():
    query = "  Compare Python and Java  "

    analysis = make_analysis(
        intent=QueryIntent.COMPARISON,
        complexity=QueryComplexity.MEDIUM,
        ambiguity=QueryAmbiguity.MEDIUM,
        requires_multi_query=True,
    )

    strategy = retrieval_planner.plan(
        query=query,
        k=5,
        analysis=analysis,
    )

    assert strategy.query == query