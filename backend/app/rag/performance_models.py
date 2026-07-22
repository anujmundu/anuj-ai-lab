from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PerformanceStage:
    """
    Represents the execution metrics for a single pipeline stage.
    """

    name: str

    duration_seconds: float = 0.0

    percentage: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    @property
    def duration_milliseconds(self) -> float:
        """
        Duration expressed in milliseconds.
        """

        return self.duration_seconds * 1000.0


@dataclass(slots=True)
class PerformanceMetrics:
    """
    Aggregated metrics describing the overall pipeline execution.
    """

    total_duration_seconds: float = 0.0

    average_stage_duration_seconds: float = 0.0

    slowest_stage: str = ""

    fastest_stage: str = ""

    stage_count: int = 0

    @property
    def total_duration_milliseconds(self) -> float:
        """
        Total pipeline duration in milliseconds.
        """

        return self.total_duration_seconds * 1000.0

    @property
    def average_stage_duration_milliseconds(self) -> float:
        """
        Average stage duration in milliseconds.
        """

        return self.average_stage_duration_seconds * 1000.0


@dataclass(slots=True)
class PerformanceProfilingResult:
    """
    Result returned by the Performance Profiler.

    This object represents the complete performance profile
    of a single RAG pipeline execution.
    """

    metrics: PerformanceMetrics = field(
        default_factory=PerformanceMetrics,
    )

    stages: list[PerformanceStage] = field(
        default_factory=list,
    )

    @property
    def total_duration_seconds(self) -> float:
        """
        Total pipeline execution time.
        """

        return self.metrics.total_duration_seconds

    @property
    def total_duration_milliseconds(self) -> float:
        """
        Total pipeline execution time in milliseconds.
        """

        return self.metrics.total_duration_milliseconds

    @property
    def average_stage_duration_seconds(self) -> float:
        """
        Average duration of all recorded stages.
        """

        return self.metrics.average_stage_duration_seconds

    @property
    def average_stage_duration_milliseconds(self) -> float:
        """
        Average duration of all recorded stages in milliseconds.
        """

        return self.metrics.average_stage_duration_milliseconds

    @property
    def slowest_stage(self) -> str:
        """
        Name of the slowest recorded stage.
        """

        return self.metrics.slowest_stage

    @property
    def fastest_stage(self) -> str:
        """
        Name of the fastest recorded stage.
        """

        return self.metrics.fastest_stage

    @property
    def stage_count(self) -> int:
        """
        Number of recorded stages.
        """

        return self.metrics.stage_count