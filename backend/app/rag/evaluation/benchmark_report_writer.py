from __future__ import annotations

import json
from pathlib import Path

from app.rag.evaluation.benchmark_report import (
    BenchmarkReport,
)


class BenchmarkReportWriter:
    """
    Writes BenchmarkReport objects to JSON.

    This component performs no benchmark execution and does
    not modify the RAG pipeline.
    """

    def write(
        self,
        report: BenchmarkReport,
        path: str | Path,
    ) -> Path:
        if not isinstance(
            report,
            BenchmarkReport,
        ):
            raise TypeError(
                "report must be a BenchmarkReport"
            )

        output_path = Path(path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            json.dumps(
                report.to_dict(),
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        return output_path


benchmark_report_writer = BenchmarkReportWriter()