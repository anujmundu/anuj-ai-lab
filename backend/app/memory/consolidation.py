from __future__ import annotations

import re
from typing import Any
from sqlmodel import Session, select
from app.db.database import engine
from app.db.chat_models import ChatMessage, ChatSession
from app.memory.models import Memory


class MemoryConsolidationEngine:
    """
    Consolidates episodic conversation history into durable semantic memories.
    """

    FACT_PATTERNS = [
        # User preferences: "I prefer X", "I use X", "My stack is X"
        (r"(?i)\b(?:i\s+prefer|i\s+like|i\s+always\s+use|my\s+stack\s+is|we\s+use)\s+([a-zA-Z0-9_\s,\.\-]{3,60})", "preference"),
        # User facts / identity: "My name is X", "I am a X", "I work at X"
        (r"(?i)\b(?:my\s+name\s+is|i\s+am\s+(?:an?|the)|i\s+work\s+(?:at|as))\s+([a-zA-Z0-9_\s,\.\-]{3,60})", "identity"),
        # Technical constraints: "Always use X", "Never do Y", "Constraint: X"
        (r"(?i)\b(?:always\s+use|never\s+use|must\s+include|requirement:\s*)\s+([a-zA-Z0-9_\s,\.\-]{3,60})", "technical_rule"),
    ]

    def extract_facts_from_text(self, text: str) -> list[tuple[str, str]]:
        """Extracts structured (fact, category) tuples from conversation text."""
        extracted: list[tuple[str, str]] = []
        for pattern, category in self.FACT_PATTERNS:
            for match in re.finditer(pattern, text):
                fact_str = match.group(0).strip()
                if len(fact_str) > 5:
                    extracted.append((fact_str, category))
        return extracted

    def consolidate_session(self, session_id: str) -> list[Memory]:
        """
        Consolidates a specific chat session into long-term memories.
        """
        with Session(engine) as db_session:
            statement = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
            messages = db_session.exec(statement).all()

            if not messages:
                return []

            created_memories: list[Memory] = []
            existing_contents = {m.content.lower() for m in db_session.exec(select(Memory)).all()}

            for msg in messages:
                if msg.role.lower() == "user":
                    facts = self.extract_facts_from_text(msg.content)
                    for fact, cat in facts:
                        if fact.lower() not in existing_contents:
                            mem = Memory(
                                content=fact,
                                category=cat,
                                importance=2 if cat in {"technical_rule", "identity"} else 1,
                            )
                            db_session.add(mem)
                            created_memories.append(mem)
                            existing_contents.add(fact.lower())

            db_session.commit()
            for m in created_memories:
                db_session.refresh(m)

            return created_memories

    def consolidate_all(self) -> dict[str, Any]:
        """Consolidates all chat sessions in the database."""
        with Session(engine) as db_session:
            sessions = db_session.exec(select(ChatSession)).all()
            total_created = 0
            session_count = len(sessions)

            for s in sessions:
                created = self.consolidate_session(s.session_id)
                total_created += len(created)

            return {
                "sessions_processed": session_count,
                "memories_created": total_created,
                "status": "completed",
            }


memory_consolidation_engine = MemoryConsolidationEngine()
