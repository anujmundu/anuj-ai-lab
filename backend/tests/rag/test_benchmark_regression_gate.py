import pytest

from app.rag.evaluation.benchmark_comparator import (
    BenchmarkComparator,
)
from app.rag.evaluation.benchmark_regression_gate import (
    BenchmarkRegressionGate,
)
from app.rag.evaluation.benchmark_report import (
    BenchmarkReport,
)
from app.rag.evaluation.models import (
    BenchmarkResult,
)


def _report(
    *,
    hit_at_1=1.0,
    grounding_score=0.8,
    hallucination_risk=0.2,
    citation_coverage=0.8,
):
    return BenchmarkReport.from_result(
        BenchmarkResult(
            total_samples=2,
            retrieval={
                "hit_at_1": hit_at_1,
            },
            answers={
                "grounding_score": grounding_score,
                "hallucination_risk": hallucination_risk,
                "citation_coverage": citation_coverage,
            },
        )
    )


def _comparison(
    *,
    baseline,
    current,
    tolerance=0.0,
):
    comparator = BenchmarkComparator(
        tolerance=tolerance,
    )

    return comparator.compare(
        baseline,
        current,
    )


def test_gate_passes_when_no_regression():

    comparison = _comparison(
        baseline=_report(),
        current=_report(),
    )

    gate = BenchmarkRegressionGate()

    result = gate.evaluate(
        comparison
    )

    assert result.passed is True
    assert result.regressed_metrics == ()
    assert result.critical_regressions == ()


def test_gate_fails_on_critical_regression():

    comparison = _comparison(
        baseline=_report(
            hit_at_1=1.0,
        ),
        current=_report(
            hit_at_1=0.8,
        ),
    )

    gate = BenchmarkRegressionGate()

    result = gate.evaluate(
        comparison
    )

    assert result.passed is False
    assert "hit_at_1" in result.regressed_metrics
    assert "hit_at_1" in result.critical_regressions


def test_gate_detects_lower_is_better_regression():

    comparison = _comparison(
        baseline=_report(
            hallucination_risk=0.1,
        ),
        current=_report(
            hallucination_risk=0.3,
        ),
    )

    gate = BenchmarkRegressionGate()

    result = gate.evaluate(
        comparison
    )

    assert result.passed is False
    assert (
        "hallucination_risk"
        in result.critical_regressions
    )


def test_non_critical_regression_does_not_fail_gate():

    comparison = _comparison(
        baseline=_report(
            grounding_score=0.8,
        ),
        current=_report(
            grounding_score=0.8,
            citation_coverage=0.5,
        ),
    )

    gate = BenchmarkRegressionGate(
        critical_metrics={
            "grounding_score",
        }
    )

    result = gate.evaluate(
        comparison
    )

    assert result.passed is True
    assert (
        "citation_coverage"
        in result.regressed_metrics
    )
    assert result.critical_regressions == ()


def test_multiple_regressions_are_preserved():

    comparison = _comparison(
        baseline=_report(
            hit_at_1=1.0,
            grounding_score=0.9,
            citation_coverage=0.9,
        ),
        current=_report(
            hit_at_1=0.8,
            grounding_score=0.7,
            citation_coverage=0.6,
        ),
    )

    gate = BenchmarkRegressionGate()

    result = gate.evaluate(
        comparison
    )

    assert result.passed is False

    assert set(
        result.regressed_metrics
    ) == {
        "hit_at_1",
        "grounding_score",
        "citation_coverage",
    }

    assert set(
        result.critical_regressions
    ) == {
        "hit_at_1",
        "grounding_score",
        "citation_coverage",
    }


def test_gate_rejects_invalid_comparison():

    gate = BenchmarkRegressionGate()

    with pytest.raises(
        TypeError,
        match="BenchmarkComparison",
    ):
        gate.evaluate(
            object()
        )