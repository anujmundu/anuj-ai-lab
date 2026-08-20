from app.rag.intelligence.adaptive_retrieval import (
    AdaptiveRetrieval,
)
from app.rag.intelligence.enums import RetrievalMode
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
    requires_multi_query: bool = False,
) -> QueryAnalysisResult:

    return QueryAnalysisResult(
        query="test query",
        intent=intent,
        complexity=complexity,
        ambiguity=ambiguity,
        requires_rewrite=False,
        requires_multi_query=requires_multi_query,
    )


def test_simple_definition_uses_standard_retrieval():

    adaptive = AdaptiveRetrieval()

    decision = adaptive.decide(
        analysis=make_analysis(
            intent=QueryIntent.DEFINITION,
            complexity=QueryComplexity.SIMPLE,
            ambiguity=QueryAmbiguity.LOW,
        )
    )

    assert decision.mode == RetrievalMode.STANDARD
    assert decision.reason == "standard_query"


def test_multi_query_requirement_selects_multi_query():

    adaptive = AdaptiveRetrieval()

    decision = adaptive.decide(
        analysis=make_analysis(
            intent=QueryIntent.COMPARISON,
            complexity=QueryComplexity.MEDIUM,
            ambiguity=QueryAmbiguity.LOW,
            requires_multi_query=True,
        )
    )

    assert decision.mode == RetrievalMode.MULTI_QUERY
    assert (
        decision.reason
        == "query_analysis_requires_multi_query"
    )


def test_research_query_can_select_multi_query():

    adaptive = AdaptiveRetrieval()

    decision = adaptive.decide(
        analysis=make_analysis(
            intent=QueryIntent.RESEARCH,
            complexity=QueryComplexity.COMPLEX,
            ambiguity=QueryAmbiguity.MEDIUM,
        )
    )

    assert decision.mode == RetrievalMode.MULTI_QUERY
    assert decision.reason == "complex_research_query"


def test_high_ambiguity_remains_standard():

    adaptive = AdaptiveRetrieval()

    decision = adaptive.decide(
        analysis=make_analysis(
            intent=QueryIntent.EXPLANATION,
            complexity=QueryComplexity.MEDIUM,
            ambiguity=QueryAmbiguity.HIGH,
        )
    )

    assert decision.mode == RetrievalMode.STANDARD
    assert (
        decision.reason
        == "high_ambiguity_requires_rewrite_or_analysis"
    )


def test_adaptive_decision_does_not_execute_retrieval():

    adaptive = AdaptiveRetrieval()

    decision = adaptive.decide(
        analysis=make_analysis(
            intent=QueryIntent.DEFINITION,
            complexity=QueryComplexity.SIMPLE,
            ambiguity=QueryAmbiguity.LOW,
        )
    )

    assert isinstance(
        decision.mode,
        RetrievalMode,
    )