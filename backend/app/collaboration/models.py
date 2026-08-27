from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    CODER = "coder"
    CRITIC = "critic"
    SUMMARIZER = "summarizer"


class CollaborationStatus(str, Enum):
    INITIALIZING = "initializing"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class AgentMessage:
    sender_role: AgentRole
    recipient_role: str  # e.g. "all", "coder", "orchestrator"
    content: str
    message_type: str = "dialogue"
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "sender_role": self.sender_role.value,
            "recipient_role": self.recipient_role,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp,
        }


@dataclass(slots=True)
class BlackboardEntry:
    author_role: AgentRole
    topic: str
    content: Any
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "author_role": self.author_role.value,
            "topic": self.topic,
            "content": self.content,
            "timestamp": self.timestamp,
        }


@dataclass(slots=True)
class CollaborationSession:
    goal: str
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    status: CollaborationStatus = CollaborationStatus.INITIALIZING
    participants: list[AgentRole] = field(default_factory=lambda: [
        AgentRole.ORCHESTRATOR,
        AgentRole.RESEARCHER,
        AgentRole.CODER,
        AgentRole.CRITIC,
    ])
    messages: list[AgentMessage] = field(default_factory=list)
    blackboard: list[BlackboardEntry] = field(default_factory=list)
    final_synthesis: str | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "goal": self.goal,
            "status": self.status.value,
            "participants": [p.value for p in self.participants],
            "messages": [m.to_dict() for m in self.messages],
            "blackboard": [b.to_dict() for b in self.blackboard],
            "final_synthesis": self.final_synthesis,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
