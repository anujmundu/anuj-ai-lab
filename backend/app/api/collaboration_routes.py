from __future__ import annotations

import asyncio
import json
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.collaboration.hitl import hitl_gate
from app.collaboration.models import CollaborationSession, CollaborationStatus
from app.collaboration.orchestrator import multi_agent_orchestrator
from app.services.collaboration_service import collaboration_service

router = APIRouter(prefix="/collaboration", tags=["Collaboration"])


class CreateSessionRequest(BaseModel):
    goal: str = Field(..., description="High-level goal for multi-agent collaboration")


class ApprovalDecisionRequest(BaseModel):
    approved: bool = Field(..., description="Whether the sensitive action is approved by the human operator")


# Legacy backwards compatibility
@router.get("/collaborate")
def legacy_collaborate(goal: str):
    return collaboration_service.execute(goal)


@router.post("/sessions", response_model=dict)
def create_collaboration_session(
    request: CreateSessionRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """Start a new multi-agent collaboration session in background worker."""
    session = CollaborationSession(goal=request.goal)
    multi_agent_orchestrator._sessions[session.session_id] = session

    background_tasks.add_task(
        multi_agent_orchestrator.run_collaboration,
        goal=request.goal,
        session_id=session.session_id,
    )

    return {
        "session_id": session.session_id,
        "goal": session.goal,
        "status": session.status.value,
        "created_at": session.created_at,
    }


@router.get("/sessions/{session_id}", response_model=dict)
def get_collaboration_session(session_id: str) -> dict:
    """Retrieve state, participant messages, blackboard entries, and final synthesis."""
    session = multi_agent_orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Collaboration session not found")
    return session.to_dict()


@router.get("/sessions", response_model=list[dict])
def list_collaboration_sessions() -> list[dict]:
    """List all registered multi-agent collaboration sessions."""
    sessions = multi_agent_orchestrator.list_sessions()
    return [s.to_dict() for s in sessions]


@router.post("/sessions/{session_id}/approve", response_model=dict)
def submit_hitl_approval(session_id: str, request: ApprovalDecisionRequest) -> dict:
    """Submit a Human-in-the-Loop approval decision for a collaboration session."""
    try:
        req = hitl_gate.submit_decision(session_id, approved=request.approved)
        return {
            "session_id": req.session_id,
            "is_decided": req.is_decided,
            "is_approved": req.is_approved,
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="No pending approval request for session")


@router.get("/sessions/{session_id}/stream")
async def stream_collaboration_dialogue(session_id: str):
    """Real-time Server-Sent Events (SSE) stream of multi-agent dialogue and consensus."""
    session = multi_agent_orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Collaboration session not found")

    queue = multi_agent_orchestrator.subscribe(session_id)

    async def event_generator():
        try:
            # Yield initial snapshot
            yield f"data: {json.dumps({'type': 'init', 'session': session.to_dict()})}\n\n"

            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield f"data: {json.dumps(event)}\n\n"

                    if event.get("type") in {"session_completed", "session_failed"}:
                        break
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
                    current = multi_agent_orchestrator.get_session(session_id)
                    if current and current.status in {CollaborationStatus.COMPLETED, CollaborationStatus.FAILED}:
                        break
        finally:
            multi_agent_orchestrator.unsubscribe(session_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )