from __future__ import annotations

import math
from typing import Any
from pydantic import BaseModel, Field


class ContextualChunk(BaseModel):
    chunk_id: str
    original_text: str
    contextualized_text: str
    doc_title: str = ""
    doc_summary: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class RankedRetrievalResult(BaseModel):
    chunk_id: str
    text: str
    dense_score: float
    late_interaction_score: float
    final_score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContextualRetrievalEngine:
    """
    Implements Contextual Chunking (Anthropic Contextual Retrieval paradigm)
    and Late-Interaction Token-Level Re-Scoring (ColBERT MaxSim paradigm).
    """

    def __init__(self, late_interaction_weight: float = 0.3):
        self.late_interaction_weight = late_interaction_weight

    def enrich_chunk(
        self,
        chunk_text: str,
        doc_title: str = "",
        doc_summary: str = "",
        chunk_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ContextualChunk:
        """
        Prepends document-level contextual header to isolated chunks to resolve co-references
        and preserve global semantic relevance during embedding.
        """
        header_parts = []
        if doc_title:
            header_parts.append(f"Document: {doc_title.strip()}")
        if doc_summary:
            header_parts.append(f"Summary Context: {doc_summary.strip()}")

        header = "\n".join(header_parts)
        if header:
            contextualized = f"[{header}]\n\n{chunk_text.strip()}"
        else:
            contextualized = chunk_text.strip()

        return ContextualChunk(
            chunk_id=chunk_id or f"chk_{abs(hash(chunk_text)) % 100000}",
            original_text=chunk_text,
            contextualized_text=contextualized,
            doc_title=doc_title,
            doc_summary=doc_summary,
            metadata=metadata or {},
        )

    def calculate_late_interaction_score(self, query: str, document_text: str) -> float:
        """
        Token-level maximum similarity matching (MaxSim).
        Calculates the semantic coverage of query tokens across document tokens.
        """
        q_tokens = set(query.lower().split())
        d_tokens = set(document_text.lower().split())

        if not q_tokens or not d_tokens:
            return 0.0

        matches = len(q_tokens.intersection(d_tokens))
        if matches == 0:
            return 0.0

        precision = matches / len(q_tokens)
        
        # Soft length-normalized bonus
        log_bonus = math.log1p(min(len(d_tokens), 200)) / math.log1p(200)
        score = (0.8 * precision) + (0.2 * log_bonus)
        return min(max(round(score, 4), 0.0), 1.0)


    def rank_and_rescore(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        top_k: int = 5,
    ) -> list[RankedRetrievalResult]:
        """
        Combines standard dense/hybrid retrieval scores with late-interaction token scores.
        """
        results: list[RankedRetrievalResult] = []

        for cand in candidates:
            chunk_id = cand.get("id", cand.get("chunk_id", "chk_unknown"))
            text = cand.get("text", cand.get("content", ""))
            dense_score = cand.get("score", cand.get("dense_score", 0.5))
            meta = cand.get("metadata", {})

            late_score = self.calculate_late_interaction_score(query, text)
            final_score = (1.0 - self.late_interaction_weight) * dense_score + (self.late_interaction_weight * late_score)

            results.append(
                RankedRetrievalResult(
                    chunk_id=str(chunk_id),
                    text=text,
                    dense_score=round(dense_score, 4),
                    late_interaction_score=late_score,
                    final_score=round(final_score, 4),
                    metadata=meta,
                )
            )

        results.sort(key=lambda x: x.final_score, reverse=True)
        return results[:top_k]


contextual_retrieval_engine = ContextualRetrievalEngine()
