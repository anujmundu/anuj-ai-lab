from __future__ import annotations

from typing import Any
from app.collaboration.models import AgentRole, BlackboardEntry


class AgentBlackboard:
    """
    Central shared workspace for multi-agent collaboration sessions.
    """

    def __init__(self) -> None:
        self._entries: list[BlackboardEntry] = []

    def post(
        self,
        author: AgentRole,
        topic: str,
        content: Any,
    ) -> BlackboardEntry:
        entry = BlackboardEntry(
            author_role=author,
            topic=topic,
            content=content,
        )
        self._entries.append(entry)
        return entry

    def get_by_topic(self, topic: str) -> list[BlackboardEntry]:
        return [e for e in self._entries if e.topic.lower() == topic.lower()]

    def get_by_author(self, author: AgentRole) -> list[BlackboardEntry]:
        return [e for e in self._entries if e.author_role == author]

    def list_entries(self) -> list[BlackboardEntry]:
        return list(self._entries)

    def summarize(self) -> str:
        """Produce a formatted markdown summary of the entire blackboard state."""
        if not self._entries:
            return "Blackboard is currently empty."

        lines = ["=== SHARED COLLABORATION BLACKBOARD ==="]
        for e in self._entries:
            lines.append(f"\n[{e.topic.upper()}] by {e.author_role.value}:")
            lines.append(str(e.content))

        return "\n".join(lines)

    def clear(self) -> None:
        self._entries.clear()


agent_blackboard = AgentBlackboard()
