from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionExemplar:
    task_type: str
    input_query: str
    reasoning_steps: list[str]
    final_answer: str
    quality_score: float = 1.0
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "task_type": self.task_type,
            "input_query": self.input_query,
            "reasoning_steps": self.reasoning_steps,
            "final_answer": self.final_answer,
            "quality_score": self.quality_score,
            "metadata": self.metadata,
        }

    def format_prompt_block(self) -> str:
        steps_text = "\n".join(f"  - {s}" for s in self.reasoning_steps)
        return (
            f"Example Query: {self.input_query}\n"
            f"Reasoning:\n{steps_text}\n"
            f"Answer: {self.final_answer}"
        )


class ExemplarStore:
    """
    Stores and retrieves verified few-shot exemplars for dynamic prompt synthesis.
    """

    def __init__(self) -> None:
        self._exemplars: dict[str, ExecutionExemplar] = {}
        # Pre-seed with default verified exemplars
        self.add(
            ExecutionExemplar(
                task_type="calculation",
                input_query="Calculate the quarterly revenue for 500 units at $120 each",
                reasoning_steps=[
                    "Identified tool: calculator",
                    "Parsed expression: 500 * 120",
                    "Executed calculation to get 60000",
                ],
                final_answer="The total quarterly revenue is $60,000.",
                quality_score=1.0,
            )
        )
        self.add(
            ExecutionExemplar(
                task_type="graph_reasoning",
                input_query="How does FastAPI relate to SQLite?",
                reasoning_steps=[
                    "Queried Knowledge Graph for 'FastAPI'",
                    "Found relation: (FastAPI) -[connects_to]-> (SQLite)",
                    "Extracted context and verified architecture",
                ],
                final_answer="FastAPI connects to SQLite to persist chat messages and ingestion jobs.",
                quality_score=1.0,
            )
        )

    def add(self, exemplar: ExecutionExemplar) -> None:
        self._exemplars[exemplar.id] = exemplar

    def get(self, exemplar_id: str) -> ExecutionExemplar | None:
        return self._exemplars.get(exemplar_id)

    def list_exemplars(self) -> list[ExecutionExemplar]:
        return list(self._exemplars.values())

    def find_relevant(self, query: str, top_k: int = 2) -> list[ExecutionExemplar]:
        """Simple keyword / token overlap matching for few-shot retrieval."""
        query_words = set(query.lower().split())
        scored: list[tuple[float, ExecutionExemplar]] = []

        for ex in self._exemplars.values():
            ex_words = set(ex.input_query.lower().split()) | set(ex.task_type.lower().split())
            overlap = len(query_words & ex_words)
            score = overlap * ex.quality_score
            scored.append((score, ex))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [ex for score, ex in scored[:top_k]]

    def format_few_shot_context(self, query: str, top_k: int = 2) -> str:
        exemplars = self.find_relevant(query, top_k=top_k)
        if not exemplars:
            return ""

        blocks = ["FEW-SHOT DEMONSTRATION EXAMPLES:"]
        for idx, ex in enumerate(exemplars, start=1):
            blocks.append(f"\n[Example {idx}]\n{ex.format_prompt_block()}")

        return "\n".join(blocks)

    def clear(self) -> None:
        self._exemplars.clear()


exemplar_store = ExemplarStore()
