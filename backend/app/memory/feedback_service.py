from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any
from app.memory.exemplar_store import ExecutionExemplar, exemplar_store


@dataclass(slots=True)
class FeedbackRecord:
    target_type: str  # "chat_message", "agent_task", "rag_answer"
    target_id: str
    vote: int  # +1 (positive) or -1 (negative)
    rating: int | None = None  # 1 to 5
    comment: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "vote": self.vote,
            "rating": self.rating,
            "comment": self.comment,
            "timestamp": self.timestamp,
        }


class FeedbackService:
    """
    Collects user feedback, tracks system quality analytics, and promotes high-rated traces to exemplars.
    """

    def __init__(self) -> None:
        self._records: list[FeedbackRecord] = []

    def record_feedback(
        self,
        target_type: str,
        target_id: str,
        vote: int,
        rating: int | None = None,
        comment: str = "",
        query_text: str = "",
        answer_text: str = "",
    ) -> FeedbackRecord:
        record = FeedbackRecord(
            target_type=target_type,
            target_id=target_id,
            vote=vote,
            rating=rating,
            comment=comment,
        )
        self._records.append(record)

        # If user gave a high rating and provided question/answer, promote to ExemplarStore
        if vote > 0 and query_text and answer_text:
            exemplar = ExecutionExemplar(
                task_type="user_promoted",
                input_query=query_text,
                reasoning_steps=["Verified by positive user feedback"],
                final_answer=answer_text,
                quality_score=1.5,
            )
            exemplar_store.add(exemplar)

        return record

    def get_metrics(self) -> dict[str, Any]:
        if not self._records:
            return {"total_feedback": 0, "positive_rate": 1.0, "total_positive": 0, "total_negative": 0}

        positive = sum(1 for r in self._records if r.vote > 0)
        negative = sum(1 for r in self._records if r.vote < 0)
        total = len(self._records)

        return {
            "total_feedback": total,
            "total_positive": positive,
            "total_negative": negative,
            "positive_rate": round(positive / total if total > 0 else 1.0, 2),
        }

    def clear(self) -> None:
        self._records.clear()


feedback_service = FeedbackService()
