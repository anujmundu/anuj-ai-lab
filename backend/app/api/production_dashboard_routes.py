from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any

from app.rag.evaluation.synthetic_eval_generator import synthetic_eval_generator
from app.rag.observability.telemetry_dashboard import telemetry_dashboard_service
from app.rag.production.system_health import system_health_monitor

router = APIRouter(tags=["Production & Telemetry Dashboard"])


class GenerateEvalRequest(BaseModel):
    chunks: list[str] = Field(..., description="List of document chunk texts from which to derive synthetic questions")


@router.get("/health/detailed", response_model=dict)
def get_detailed_system_health() -> dict:
    """Detailed health checks and latency diagnostics for SQLite, ChromaDB, and Cache."""
    return system_health_monitor.get_full_diagnostics()


@router.post("/eval/synthetic/generate", response_model=list[dict])
def generate_synthetic_evaluation_dataset(request: GenerateEvalRequest) -> list[dict]:
    """Generate synthetic ground-truth Q&A test cases from ingested text chunks."""
    items = synthetic_eval_generator.generate_dataset(request.chunks)
    return [i.to_dict() for i in items]


@router.get("/telemetry/dashboard", response_model=dict)
def get_telemetry_dashboard() -> dict:
    """Consolidated enterprise observability dashboard with real-time metrics across all layers."""
    return telemetry_dashboard_service.get_dashboard_summary()
