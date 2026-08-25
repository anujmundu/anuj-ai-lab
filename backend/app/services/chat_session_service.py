from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.db.chat_models import ChatMessage, ChatSession
from app.rag.rag_service import rag_service
from app.services.ollama_service import ollama_service


class ChatSessionService:
    """
    Coordinates multi-session conversation persistence,
    context formatting, and rolling summarization.
    """

    def create_session(
        self,
        session: Session,
        *,
        title: str = "New Conversation",
    ) -> ChatSession:
        chat_session = ChatSession(title=title)
        session.add(chat_session)
        session.commit()
        session.refresh(chat_session)
        return chat_session

    def list_sessions(
        self,
        session: Session,
        *,
        limit: int = 50,
    ) -> list[ChatSession]:
        statement = (
            select(ChatSession)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
        )
        return list(session.exec(statement).all())

    def get_session(
        self,
        session: Session,
        *,
        session_id: str,
    ) -> ChatSession | None:
        statement = select(ChatSession).where(
            ChatSession.session_id == session_id
        )
        return session.exec(statement).first()

    def delete_session(
        self,
        session: Session,
        *,
        session_id: str,
    ) -> bool:
        chat_session = self.get_session(session, session_id=session_id)
        if not chat_session:
            return False

        # Delete all associated messages
        msg_statement = select(ChatMessage).where(
            ChatMessage.session_id == session_id
        )
        messages = session.exec(msg_statement).all()
        for msg in messages:
            session.delete(msg)

        session.delete(chat_session)
        session.commit()
        return True

    def get_messages(
        self,
        session: Session,
        *,
        session_id: str,
        limit: int = 100,
    ) -> list[ChatMessage]:
        statement = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        return list(session.exec(statement).all())

    def format_conversation_context(
        self,
        session: Session,
        *,
        session_id: str,
        max_turns: int = 6,
    ) -> str | None:
        messages = self.get_messages(
            session,
            session_id=session_id,
            limit=max_turns * 2,
        )
        if not messages:
            return None

        chat_session = self.get_session(session, session_id=session_id)
        formatted_lines = []

        if chat_session and chat_session.summary:
            formatted_lines.append(
                f"Summary of previous discussion: {chat_session.summary}\n"
            )

        for msg in messages:
            speaker = "User" if msg.role == "user" else "Assistant"
            formatted_lines.append(f"{speaker}: {msg.content}")

        return "\n".join(formatted_lines)

    def post_message(
        self,
        session: Session,
        *,
        session_id: str,
        content: str,
    ) -> dict:
        chat_session = self.get_session(session, session_id=session_id)
        if not chat_session:
            raise ValueError(f"Chat session {session_id} not found")

        # 1. Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=content,
        )
        session.add(user_msg)
        session.commit()

        # 2. Build conversation context from past messages
        conversation_context = self.format_conversation_context(
            session,
            session_id=session_id,
        )

        # 3. Call RAG service
        rag_response = rag_service.ask(
            question=content,
            conversation=conversation_context,
        )

        answer = rag_response.get("answer", "")
        sources = rag_response.get("sources", [])

        # 4. Save assistant message
        assistant_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=answer,
            sources_json=json.dumps(sources) if sources else None,
        )
        session.add(assistant_msg)

        # Update session title if first turn
        if chat_session.title == "New Conversation":
            chat_session.title = content[:40].strip() + (
                "..." if len(content) > 40 else ""
            )

        chat_session.updated_at = datetime.now(timezone.utc)
        session.add(chat_session)
        session.commit()
        session.refresh(chat_session)
        session.refresh(assistant_msg)

        return {
            "session_id": session_id,
            "user_message_id": user_msg.id,
            "assistant_message_id": assistant_msg.id,
            "answer": answer,
            "sources": sources,
            "diagnostics": rag_response.get("diagnostics", {}),
        }


chat_session_service = ChatSessionService()
