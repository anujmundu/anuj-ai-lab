from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SyntheticEvalItem:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    question: str = ""
    ground_truth_context: str = ""
    expected_answer: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "ground_truth_context": self.ground_truth_context,
            "expected_answer": self.expected_answer,
        }


class SyntheticEvalGenerator:
    """
    Automatically generates evaluation test cases from text chunks to measure retrieval accuracy.
    """

    def generate_from_chunk(self, chunk_text: str) -> list[SyntheticEvalItem]:
        """Derives synthetic questions and expected answers from text chunks."""
        items: list[SyntheticEvalItem] = []
        sentences = [s.strip() for s in re.split(r"[.\n]", chunk_text) if len(s.strip()) > 15]

        for sentence in sentences:
            # Pattern: "X is Y" or "X provides Y"
            match = re.match(r"^([A-Z][a-zA-Z0-9_\s]{2,25})\s+(?:is|provides|implements|manages)\s+(.+)$", sentence)
            if match:
                subject = match.group(1).strip()
                predicate = match.group(2).strip()
                question = f"What is {subject} and what does it do?"
                items.append(
                    SyntheticEvalItem(
                        question=question,
                        ground_truth_context=chunk_text,
                        expected_answer=sentence,
                    )
                )

        # Fallback if no specific regex matched
        if not items and len(chunk_text.strip()) > 20:
            first_sentence = sentences[0] if sentences else chunk_text[:80]
            items.append(
                SyntheticEvalItem(
                    question=f"Explain the primary concept described in: '{first_sentence[:40]}...'",
                    ground_truth_context=chunk_text,
                    expected_answer=first_sentence,
                )
            )

        return items

    def generate_dataset(self, chunks: list[str]) -> list[SyntheticEvalItem]:
        dataset: list[SyntheticEvalItem] = []
        for chunk in chunks:
            dataset.extend(self.generate_from_chunk(chunk))
        return dataset


synthetic_eval_generator = SyntheticEvalGenerator()
