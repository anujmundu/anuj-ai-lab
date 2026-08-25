import json
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.database import get_session
from app.services.chat_session_service import chat_session_service


router = APIRouter(prefix="/chat", tags=["Chat Sessions"])


class SessionCreateRequest(BaseModel):
    title: str = "New Conversation"


class MessagePostRequest(BaseModel):
    content: str


@router.post("/sessions")
def create_session(
    payload: SessionCreateRequest | None = None,
    session: Session = Depends(get_session),
):
    title = payload.title if payload else "New Conversation"
    chat_session = chat_session_service.create_session(session, title=title)
    return {
        "session_id": chat_session.session_id,
        "title": chat_session.title,
        "created_at": chat_session.created_at.isoformat(),
        "updated_at": chat_session.updated_at.isoformat(),
    }


@router.get("/sessions")
def list_sessions(
    limit: int = 50,
    session: Session = Depends(get_session),
):
    sessions = chat_session_service.list_sessions(session, limit=limit)
    return [
        {
            "session_id": s.session_id,
            "title": s.title,
            "summary": s.summary,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
def get_session_details(
    session_id: str,
    session: Session = Depends(get_session),
):
    chat_session = chat_session_service.get_session(session, session_id=session_id)
    if not chat_session:
        raise HTTPException(
            status_code=404,
            detail=f"Chat session {session_id} not found",
        )

    messages = chat_session_service.get_messages(session, session_id=session_id)
    return {
        "session_id": chat_session.session_id,
        "title": chat_session.title,
        "summary": chat_session.summary,
        "created_at": chat_session.created_at.isoformat(),
        "updated_at": chat_session.updated_at.isoformat(),
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "sources": json.loads(m.sources_json) if m.sources_json else [],
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    session: Session = Depends(get_session),
):
    deleted = chat_session_service.delete_session(session, session_id=session_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Chat session {session_id} not found",
        )
    return {"message": "Session deleted successfully"}


@router.post("/sessions/{session_id}/messages")
def send_session_message(
    session_id: str,
    payload: MessagePostRequest,
    session: Session = Depends(get_session),
):
    if not payload.content.strip():
        raise HTTPException(
            status_code=400,
            detail="Message content cannot be empty",
        )

    try:
        result = chat_session_service.post_message(
            session,
            session_id=session_id,
            content=payload.content,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
