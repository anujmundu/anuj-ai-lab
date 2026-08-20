from app.rag.intelligence.dynamic_k import (
    DynamicKSelector,
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
) -> QueryAnalysisResult:

    return QueryAnalysisResult(
        query="test query",
        intent=intent,
        complexity=complexity,
        ambiguity=ambiguity,
        requires_rewrite=False,
        requires_multi_query=False,
    )


def test_simple_query_uses_default_k():

    selector = DynamicKSelector()

    decision = selector.select(
        analysis=make_analysis(
            intent=QueryIntent.DEFINITION,
            complexity=QueryComplexity.SIMPLE,
            ambiguity=QueryAmbiguity.LOW,
        )
    )

    assert decision.k == 5
    assert decision.reason == "simple_query"


def test_medium_query_increases_k():

    selector = DynamicKSelector()

    decision = selector.select(
        analysis=make_analysis(
            intent=QueryIntent.EXPLANATION,
            complexity=QueryComplexity.MEDIUM,
            ambiguity=QueryAmbiguity.LOW,
        )
    )

    assert decision.k == 7
    assert decision.reason == "medium_complexity_query"


def test_complex_query_increases_k():

    selector = DynamicKSelector()

    decision = selector.select(
        analysis=make_analysis(
            intent=QueryIntent.FACTUAL,
            complexity=QueryComplexity.COMPLEX,
            ambiguity=QueryAmbiguity.LOW,
        )
    )

    assert decision.k == 10
    assert decision.reason == "complex_query"


def test_high_ambiguity_increases_k():

    selector = DynamicKSelector()

    decision = selector.select(
        analysis=make_analysis(
            intent=QueryIntent.EXPLANATION,
            complexity=QueryComplexity.SIMPLE,
            ambiguity=QueryAmbiguity.HIGH,
        )
    )

    assert decision.k == 7
    assert decision.reason == "high_ambiguity_query"


def test_research_query_gets_more_results():

    selector = DynamicKSelector()

    decision = selector.select(
        analysis=make_analysis(
            intent=QueryIntent.RESEARCH,
            complexity=QueryComplexity.MEDIUM,
            ambiguity=QueryAmbiguity.LOW,
        )
    )

    assert decision.k == 9
    assert decision.reason == "broad_information_need"


def test_comparison_query_gets_more_results():

    selector = DynamicKSelector()

    decision = selector.select(
        analysis=make_analysis(
            intent=QueryIntent.COMPARISON,
            complexity=QueryComplexity.SIMPLE,
            ambiguity=QueryAmbiguity.LOW,
        )
    )

    assert decision.k == 7
    assert decision.reason == "broad_information_need"


def test_k_never_exceeds_maximum():

    selector = DynamicKSelector()

    decision = selector.select(
        analysis=make_analysis(
            intent=QueryIntent.RESEARCH,
            complexity=QueryComplexity.COMPLEX,
            ambiguity=QueryAmbiguity.HIGH,
        )
    )

    assert decision.k <= selector.MAX_K


def test_k_never_goes_below_minimum():

    selector = DynamicKSelector()

    decision = selector.select(
        analysis=make_analysis(
            intent=QueryIntent.DEFINITION,
            complexity=QueryComplexity.SIMPLE,
            ambiguity=QueryAmbiguity.LOW,
        )
    )

    assert decision.k >= selector.MIN_K