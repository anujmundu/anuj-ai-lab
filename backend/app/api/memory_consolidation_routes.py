from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any

from app.memory.consolidation import memory_consolidation_engine
from app.memory.exemplar_store import exemplar_store
from app.memory.feedback_service import feedback_service
from app.rag.graph.graph_optimizer import graph_optimizer

router = APIRouter(tags=["Memory & Evolution"])


class FeedbackSubmission(BaseModel):
    target_type: str = Field(..., description="'chat_message', 'agent_task', or 'rag_answer'")
    target_id: str = Field(..., description="ID of the message or task being evaluated")
    vote: int = Field(..., ge=-1, le=1, description="+1 (positive) or -1 (negative)")
    rating: int | None = Field(default=None, ge=1, le=5, description="Optional 1-5 star rating")
    comment: str = Field(default="", description="Optional feedback comment")
    query_text: str = Field(default="", description="Optional query text to promote to exemplars")
    answer_text: str = Field(default="", description="Optional answer text to promote to exemplars")


@router.post("/memory/consolidate", response_model=dict)
def trigger_memory_consolidation() -> dict:
    """Consolidate episodic chat history into long-term semantic memory."""
    return memory_consolidation_engine.consolidate_all()


@router.post("/memory/feedback", response_model=dict)
def submit_feedback(data: FeedbackSubmission) -> dict:
    """Record user feedback and promote high-quality answers to few-shot exemplars."""
    rec = feedback_service.record_feedback(
        target_type=data.target_type,
        target_id=data.target_id,
        vote=data.vote,
        rating=data.rating,
        comment=data.comment,
        query_text=data.query_text,
        answer_text=data.answer_text,
    )
    return rec.to_dict()


@router.get("/memory/feedback/metrics", response_model=dict)
def get_feedback_metrics() -> dict:
    """Get system-wide satisfaction metrics and feedback counts."""
    return feedback_service.get_metrics()


@router.get("/memory/exemplars", response_model=list[dict])
def list_exemplars() -> list[dict]:
    """List verified few-shot exemplars for dynamic prompt injection."""
    return [ex.to_dict() for ex in exemplar_store.list_exemplars()]


@router.post("/rag/graph/optimize", response_model=dict)
def trigger_graph_optimization() -> dict:
    """Deduplicate entity aliases and prune redundant relations in the Knowledge Graph."""
    return graph_optimizer.optimize()
