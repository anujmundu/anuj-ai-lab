from app.rag.builders.diagnostics_builder import DiagnosticsBuilder

from app.rag.query.models import QueryAnalysisResult
from app.rag.query.enums import (
    QueryIntent,
    QueryComplexity,
    QueryAmbiguity,
)

from app.rag.prompt_pipeline_models import (
    PromptPipelineResult,
)

from app.rag.prompt_optimizer_models import (
    PromptAnalysis,
    PromptOptimizationResult,
)

from app.rag.token_budget_models import (
    TokenBudget,
)

from app.rag.performance_models import (
    PerformanceProfilingResult,
)


def make_query_analysis():
    return QueryAnalysisResult(
        query="What is Python?",
        intent=QueryIntent.DEFINITION,
        complexity=QueryComplexity.SIMPLE,
        ambiguity=QueryAmbiguity.MEDIUM,
        requires_rewrite=False,
        requires_multi_query=False,
    )


def make_prompt_pipeline():
    analysis = PromptAnalysis(
        total_tokens=100,
        total_characters=400,
        instruction_ratio=0.10,
        context_ratio=0.50,
        memory_ratio=0.10,
        conversation_ratio=0.05,
        question_ratio=0.05,
        largest_component="context",
        efficiency_score=1.0,
        redundancy_score=0.0,
        balanced=True,
        recommendations=[],
    )

    optimization = PromptOptimizationResult(
        original_components=[],
        optimized_components=[],
        analysis_before=analysis,
        analysis_after=analysis,
        optimizations=[],
        tokens_saved=0,
    )

    budget = TokenBudget(
        context_window=32768,
        reserved_output_tokens=2048,
        available_input_tokens=30720,
        used_input_tokens=100,
        remaining_input_tokens=30620,
        utilization=0.003,
    )

    return PromptPipelineResult(
        prompt="What is Python?",
        analysis=analysis,
        optimization=optimization,
        budget=budget,
        quality={
            "total_tokens": 100,
            "total_characters": 400,
            "instruction_ratio": 0.10,
            "context_ratio": 0.50,
            "memory_ratio": 0.10,
            "conversation_ratio": 0.05,
            "question_ratio": 0.05,
            "largest_component": "context",
            "balanced": True,
            "efficiency_score": 1.0,
            "redundancy_score": 0.0,
            "prompt_efficiency": "Excellent",
            "recommendations": [],
            "optimization_count": 0,
            "tokens_saved": 0,
            "context_window": 32768,
            "reserved_output_tokens": 2048,
            "available_input_tokens": 30720,
            "used_input_tokens": 100,
            "remaining_input_tokens": 30620,
            "budget_utilization": 0.003,
            "overflow_detected": False,
            "overflow_tokens": 0,
            "truncated_components": 0,
        },
    )


def make_performance():
    return PerformanceProfilingResult()


def build_diagnostics(*, grounding_result):
    builder = DiagnosticsBuilder()

    return builder.build_request_diagnostics(
        query_analysis=make_query_analysis(),

        question="What is Python?",

        retrieval_seconds=0.25,

        retrieval_diagnostics={
            "strategy": "hybrid",
            "semantic_candidates": 20,
            "keyword_candidates": 3,
            "fused_candidates": 3,
            "filtered_candidates": 3,
        },

        context_build_seconds=0.001,

        prompt_build_seconds=0.001,

        generation_seconds=1.0,

        total_seconds=1.3,

        prompt_pipeline=make_prompt_pipeline(),

        prompt="What is Python?",

        context="Python is a programming language.",

        memory="",

        conversation=None,

        answer="Python is a programming language.",

        confidence=0.95,

        hallucination_result={
            "hallucination_risk": 0.07,
            "unsupported_claims": 0,
            "contradicted_claims": 0,
            "contradictions_detected": 0,
        },

        consistency_result={
            "status": "consistent",
            "consistency_score": 1.0,
            "contradicted_pairs": 0,
            "sentence_pairs": 1,
        },

        answer_quality_result={},

        pipeline_health_result={},

        scorecard_result={},

        citation_result={
            "citations": ["[1]"],
            "coverage": {
                "total_sentences": 1,
                "cited_sentences": 1,
                "uncited_sentences": 0,
                "coverage": 1.0,
                "citation_density": 1.0,
            },
        },

        grounding_result=grounding_result,

        performance=make_performance(),
    )


def test_build_request_diagnostics_includes_grounding():
    grounding = {
        "enabled": True,
        "decision": "accept",
        "grounded": True,
        "repairable": False,
        "reason": "answer_meets_grounding_criteria",
        "reasons": [],
        "metrics": {
            "evidence": {
                "total_sentences": 2,
                "grounded_sentences": 2,
                "partially_grounded_sentences": 0,
                "unsupported_sentences": 0,
                "supported_ratio": 1.0,
                "unsupported_ratio": 0.0,
                "grounding_score": 1.0,
                "average_confidence": 0.775,
            }
        },
    }

    result = build_diagnostics(
        grounding_result=grounding,
    )

    assert "grounding" in result
    assert result["grounding"]["enabled"] is True
    assert result["grounding"]["decision"] == "accept"
    assert result["grounding"]["grounded"] is True


def test_grounding_metrics_are_preserved():
    grounding = {
        "enabled": True,
        "decision": "repair",
        "grounded": False,
        "repairable": True,
        "reason": "partial_evidence_available",
        "reasons": [
            "partial evidence",
        ],
        "metrics": {
            "evidence": {
                "grounding_score": 0.5,
                "average_confidence": 0.55,
            }
        },
    }

    result = build_diagnostics(
        grounding_result=grounding,
    )

    assert result["grounding"]["decision"] == "repair"
    assert result["grounding"]["repairable"] is True

    assert (
        result["grounding"]["metrics"]["evidence"]["grounding_score"]
        == 0.5
    )

    assert (
        result["grounding"]["metrics"]["evidence"]["average_confidence"]
        == 0.55
    )


def test_grounding_rejection_is_preserved():
    grounding = {
        "enabled": True,
        "decision": "reject",
        "grounded": False,
        "repairable": False,
        "reason": "grounding_score_below_threshold",
        "reasons": [
            "insufficient evidence",
        ],
        "metrics": {},
    }

    result = build_diagnostics(
        grounding_result=grounding,
    )

    assert result["grounding"]["decision"] == "reject"
    assert result["grounding"]["grounded"] is False
    assert result["grounding"]["repairable"] is False
    assert (
        result["grounding"]["reason"]
        == "grounding_score_below_threshold"
    )