import json

import pytest

from app.rag.evaluation.benchmark_report import (
    BenchmarkReport,
)
from app.rag.evaluation.benchmark_report_writer import (
    BenchmarkReportWriter,
)
from app.rag.evaluation.models import (
    BenchmarkResult,
)


def _report():
    result = BenchmarkResult(
        total_samples=2,
        retrieval={
            "hit_at_1": 1.0,
            "recall_at_3": 1.0,
        },
        answers={
            "grounding_score": 0.8335,
        },
        runtime={
            "total_seconds": 11.94,
        },
        metadata={
            "evaluation_type": "full_rag",
        },
    )

    return BenchmarkReport.from_result(
        result
    )


def test_writer_creates_json_file(tmp_path):

    writer = BenchmarkReportWriter()

    output = tmp_path / "benchmark.json"

    result = writer.write(
        _report(),
        output,
    )

    assert result == output
    assert output.exists()


def test_writer_produces_valid_json(tmp_path):

    writer = BenchmarkReportWriter()

    output = tmp_path / "benchmark.json"

    writer.write(
        _report(),
        output,
    )

    data = json.loads(
        output.read_text(
            encoding="utf-8"
        )
    )

    assert data["total_samples"] == 2

    assert data["retrieval"]["hit_at_1"] == 1.0

    assert data["answers"][
        "grounding_score"
    ] == 0.8335


def test_writer_creates_parent_directories(tmp_path):

    writer = BenchmarkReportWriter()

    output = (
        tmp_path
        / "reports"
        / "rag"
        / "benchmark.json"
    )

    writer.write(
        _report(),
        output,
    )

    assert output.exists()


def test_writer_adds_trailing_newline(tmp_path):

    writer = BenchmarkReportWriter()

    output = tmp_path / "benchmark.json"

    writer.write(
        _report(),
        output,
    )

    content = output.read_text(
        encoding="utf-8"
    )

    assert content.endswith("\n")


def test_writer_rejects_invalid_report(tmp_path):

    writer = BenchmarkReportWriter()

    with pytest.raises(
        TypeError,
        match="BenchmarkReport",
    ):
        writer.write(
            object(),
            tmp_path / "benchmark.json",
        )