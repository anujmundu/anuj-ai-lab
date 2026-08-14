import pytest

from app.rag.evaluation.benchmark_comparator import (
    BenchmarkComparator,
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
    total_seconds=10.0,
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
            },
            runtime={
                "total_seconds": total_seconds,
            },
        )
    )


def test_higher_is_better_metric():

    comparator = BenchmarkComparator()

    result = comparator.compare(
        _report(hit_at_1=0.8),
        _report(hit_at_1=1.0),
    )

    metric = result.metrics[0]

    assert metric.metric == "hit_at_1"
    assert metric.baseline == 0.8
    assert metric.current == 1.0
    assert metric.delta == pytest.approx(0.2)
    assert metric.direction == "higher_is_better"
    assert metric.improved is True
    assert metric.regressed is False


def test_lower_is_better_metric():

    comparator = BenchmarkComparator()

    result = comparator.compare(
        _report(hallucination_risk=0.3),
        _report(hallucination_risk=0.1),
    )

    metric = next(
        item
        for item in result.metrics
        if item.metric == "hallucination_risk"
    )

    assert metric.direction == "lower_is_better"
    assert metric.improved is True
    assert metric.regressed is False


def test_regression_is_detected():

    comparator = BenchmarkComparator()

    result = comparator.compare(
        _report(
            hit_at_1=1.0,
            grounding_score=0.9,
        ),
        _report(
            hit_at_1=0.8,
            grounding_score=0.7,
        ),
    )

    assert result.regressed == 2
    assert result.improved == 0


def test_runtime_regression_is_detected():

    comparator = BenchmarkComparator()

    result = comparator.compare(
        _report(total_seconds=5.0),
        _report(total_seconds=8.0),
    )

    metric = next(
        item
        for item in result.metrics
        if item.metric == "total_seconds"
    )

    assert metric.regressed is True
    assert metric.improved is False


def test_tolerance_marks_small_change_unchanged():

    comparator = BenchmarkComparator(
        tolerance=0.05
    )

    result = comparator.compare(
        _report(hit_at_1=0.90),
        _report(hit_at_1=0.93),
    )

    metric = result.metrics[0]

    assert metric.improved is False
    assert metric.regressed is False
    assert result.unchanged == 4


def test_equal_values_are_unchanged():

    comparator = BenchmarkComparator()

    result = comparator.compare(
        _report(),
        _report(),
    )

    assert result.improved == 0
    assert result.regressed == 0
    assert result.unchanged == 4


def test_invalid_baseline_is_rejected():

    comparator = BenchmarkComparator()

    with pytest.raises(
        TypeError,
        match="baseline must be",
    ):
        comparator.compare(
            object(),
            _report(),
        )


def test_invalid_current_is_rejected():

    comparator = BenchmarkComparator()

    with pytest.raises(
        TypeError,
        match="current must be",
    ):
        comparator.compare(
            _report(),
            object(),
        )


def test_negative_tolerance_is_rejected():

    with pytest.raises(
        ValueError,
        match="tolerance",
    ):
        BenchmarkComparator(
            tolerance=-0.1
        )