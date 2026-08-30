from datetime import datetime, timezone
import uuid

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.utcnow()


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    session_id: str = Field(
        default_factory=lambda: uuid.uuid4().hex,
        primary_key=True,
        index=True,
    )
    title: str = Field(
        default="New Conversation",
    )
    summary: str | None = Field(
        default=None,
    )
    created_at: datetime = Field(
        default_factory=utc_now,
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
    )


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    session_id: str = Field(
        index=True,
    )
    role: str = Field(
        default="user",
        index=True,
    )
    content: str
    sources_json: str | None = Field(
        default=None,
    )
    created_at: datetime = Field(
        default_factory=utc_now,
    )
