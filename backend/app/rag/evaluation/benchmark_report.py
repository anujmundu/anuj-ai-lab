from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.rag.evaluation.models import BenchmarkResult


@dataclass(slots=True, frozen=True)
class BenchmarkReport:
    """
    Presentation-ready representation of a benchmark run.

    The report is derived from BenchmarkResult and does not
    execute or modify the RAG pipeline.
    """

    total_samples: int

    retrieval: dict[str, Any] = field(
        default_factory=dict
    )

    answers: dict[str, Any] = field(
        default_factory=dict
    )

    runtime: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_result(
        cls,
        result: BenchmarkResult,
    ) -> "BenchmarkReport":
        """
        Convert a BenchmarkResult into a report.
        """

        if not isinstance(
            result,
            BenchmarkResult,
        ):
            raise TypeError(
                "result must be a BenchmarkResult"
            )

        return cls(
            total_samples=result.total_samples,
            retrieval=dict(result.retrieval),
            answers=dict(result.answers),
            runtime=dict(result.runtime),
            metadata=dict(result.metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Return the report as a JSON-serializable dictionary.
        """

        return asdict(self)