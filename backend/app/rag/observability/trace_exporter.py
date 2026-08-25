from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from app.rag.performance_profiler import PerformanceProfiler


@dataclass(slots=True)
class OpenTelemetrySpan:
    trace_id: str
    span_id: str
    parent_span_id: str | None
    name: str
    start_time_ns: int
    duration_ms: float
    attributes: dict = field(default_factory=dict)
    status: str = "OK"

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "start_time_ns": self.start_time_ns,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "status": self.status,
        }


class TraceExporter:
    """
    Exports RAG performance metrics into OpenTelemetry trace spans.
    """

    def export(
        self,
        profiler: PerformanceProfiler | None,
        *,
        trace_id: str | None = None,
        root_name: str = "rag_request",
    ) -> dict:
        trace_id = trace_id or uuid.uuid4().hex
        root_span_id = uuid.uuid4().hex[:16]
        now_ns = int(time.time() * 1e9)

        if profiler is None:
            return {
                "trace_id": trace_id,
                "spans": [],
            }

        spans: list[dict] = []

        # Read completed stages from PerformanceProfiler
        completed_stages = getattr(profiler, "_completed_stages", [])
        for stage in completed_stages:
            stage_name = stage.name.value if hasattr(stage.name, "value") else str(stage.name)
            duration_ms = round(stage.duration_seconds * 1000.0, 2)
            span = OpenTelemetrySpan(
                trace_id=trace_id,
                span_id=uuid.uuid4().hex[:16],
                parent_span_id=root_span_id,
                name=f"rag.{stage_name}",
                start_time_ns=now_ns,
                duration_ms=duration_ms,
                attributes=stage.metadata or {},
            )
            spans.append(span.to_dict())

        return {
            "trace_id": trace_id,
            "root_span_id": root_span_id,
            "spans": spans,
        }



trace_exporter = TraceExporter()
