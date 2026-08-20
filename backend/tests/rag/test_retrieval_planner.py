from app.rag.intelligence.retrieval_planner import (
    retrieval_planner,
)
from app.rag.query.enums import (
    QueryAmbiguity,
    QueryComplexity,
    QueryIntent,
)
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


def test_simple_definition_uses_dynamic_k():

    analysis = make_analysis(
        intent=QueryIntent.DEFINITION,
        complexity=QueryComplexity.SIMPLE,
        ambiguity=QueryAmbiguity.MEDIUM,
    )

    strategy = retrieval_planner.plan(
        query="What is Python?",
        k=5,
        analysis=analysis,
    )

    assert strategy.query == "What is Python?"
    assert strategy.k == 5
    assert strategy.rewrite is False
    assert strategy.expand is False
    assert strategy.multi_query is False


def test_requested_k_caps_dynamic_k():

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

    # Dynamic selector recommends 10 for this query,
    # but the caller requested only 5.
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
    assert strategy.k == 5


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
        k=7,
        analysis=analysis,
    )

    assert strategy.rewrite is True
    assert strategy.query == "Explain this"

    # Medium complexity = 7,
    # high ambiguity adds 2 => 9.
    # Caller requested 7, therefore effective k = 7.
    assert strategy.k == 7


def test_complex_query_uses_dynamic_k_when_requested_k_is_high():

    analysis = make_analysis(
        intent=QueryIntent.FACTUAL,
        complexity=QueryComplexity.COMPLEX,
        ambiguity=QueryAmbiguity.LOW,
    )

    strategy = retrieval_planner.plan(
        query="Analyze this complex question",
        k=20,
        analysis=analysis,
    )

    assert strategy.k == 10


def test_multi_query_requirement_is_preserved():

    analysis = make_analysis(
        intent=QueryIntent.RESEARCH,
        complexity=QueryComplexity.COMPLEX,
        ambiguity=QueryAmbiguity.MEDIUM,
        requires_multi_query=True,
    )

    strategy = retrieval_planner.plan(
        query="Analyze retrieval augmented generation systems",
        k=20,
        analysis=analysis,
    )

    assert strategy.multi_query is True

    # Complex = 10
    # Medium ambiguity = +1
    # Research = +2
    # Capped by DynamicKSelector.MAX_K = 12.
    assert strategy.k == 12


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

def test_research_query_enables_hyde():

    analysis = make_analysis(
        intent=QueryIntent.RESEARCH,
        complexity=QueryComplexity.MEDIUM,
        ambiguity=QueryAmbiguity.LOW,
    )

    strategy = retrieval_planner.plan(
        query="Research retrieval augmented generation",
        k=5,
        analysis=analysis,
    )

    assert strategy.hyde is True


def test_complex_explanation_query_enables_hyde():

    analysis = make_analysis(
        intent=QueryIntent.EXPLANATION,
        complexity=QueryComplexity.COMPLEX,
        ambiguity=QueryAmbiguity.MEDIUM,
    )

    strategy = retrieval_planner.plan(
        query="Explain advanced retrieval architectures",
        k=5,
        analysis=analysis,
    )

    assert strategy.hyde is True


def test_simple_definition_does_not_enable_hyde():

    analysis = make_analysis(
        intent=QueryIntent.DEFINITION,
        complexity=QueryComplexity.SIMPLE,
        ambiguity=QueryAmbiguity.LOW,
    )

    strategy = retrieval_planner.plan(
        query="What is Python?",
        k=3,
        analysis=analysis,
    )

    assert strategy.hyde is False


def test_multi_query_takes_precedence_over_hyde():

    analysis = make_analysis(
        intent=QueryIntent.RESEARCH,
        complexity=QueryComplexity.COMPLEX,
        ambiguity=QueryAmbiguity.LOW,
        requires_multi_query=True,
    )

    strategy = retrieval_planner.plan(
        query="Research retrieval augmented generation",
        k=5,
        analysis=analysis,
    )

    assert strategy.multi_query is True
    assert strategy.hyde is False


def test_comparison_query_does_not_enable_hyde():

    analysis = make_analysis(
        intent=QueryIntent.COMPARISON,
        complexity=QueryComplexity.COMPLEX,
        ambiguity=QueryAmbiguity.MEDIUM,
    )

    strategy = retrieval_planner.plan(
        query="Compare Python and Java",
        k=5,
        analysis=analysis,
    )

    assert strategy.hyde is False


def test_strategy_preserves_existing_planner_decisions():

    analysis = make_analysis(
        intent=QueryIntent.EXPLANATION,
        complexity=QueryComplexity.COMPLEX,
        ambiguity=QueryAmbiguity.HIGH,
        requires_rewrite=True,
        requires_multi_query=False,
    )

    strategy = retrieval_planner.plan(
        query="Explain this architecture",
        k=4,
        analysis=analysis,
    )

    assert strategy.rewrite is True
    assert strategy.multi_query is False
    assert strategy.hyde is True