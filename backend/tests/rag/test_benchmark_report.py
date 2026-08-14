import pytest

from app.rag.evaluation.benchmark_report import (
    BenchmarkReport,
)
from app.rag.evaluation.models import (
    BenchmarkResult,
)


def _result():
    return BenchmarkResult(
        total_samples=2,
        retrieval={
            "hit_at_1": 1.0,
            "recall_at_3": 1.0,
            "ndcg_at_5": 0.9599,
        },
        answers={
            "grounding_score": 0.8335,
            "supported_ratio": 1.0,
            "hallucination_risk": 0.215,
        },
        runtime={
            "total_seconds": 11.948789,
            "samples_per_second": 0.1674,
        },
        metadata={
            "evaluation_type": "full_rag",
            "retrieval_samples": 2,
            "answer_samples": 2,
        },
    )


def test_report_from_result():

    report = BenchmarkReport.from_result(
        _result()
    )

    assert report.total_samples == 2

    assert report.retrieval["hit_at_1"] == 1.0

    assert report.answers[
        "grounding_score"
    ] == 0.8335

    assert report.runtime[
        "samples_per_second"
    ] == 0.1674

    assert report.metadata[
        "evaluation_type"
    ] == "full_rag"


def test_report_to_dict():

    report = BenchmarkReport.from_result(
        _result()
    )

    data = report.to_dict()

    assert isinstance(data, dict)

    assert data["total_samples"] == 2

    assert data["retrieval"]["ndcg_at_5"] == 0.9599

    assert data["answers"][
        "supported_ratio"
    ] == 1.0


def test_report_does_not_modify_result():

    result = _result()

    report = BenchmarkReport.from_result(
        result
    )

    report.retrieval["hit_at_1"] = 0.0

    assert result.retrieval[
        "hit_at_1"
    ] == 1.0


def test_report_requires_benchmark_result():

    with pytest.raises(
        TypeError,
        match="BenchmarkResult",
    ):
        BenchmarkReport.from_result(
            object()
        )


def test_empty_result_is_supported():

    result = BenchmarkResult()

    report = BenchmarkReport.from_result(
        result
    )

    assert report.total_samples == 0
    assert report.retrieval == {}
    assert report.answers == {}
    assert report.runtime == {}
    assert report.metadata == {}