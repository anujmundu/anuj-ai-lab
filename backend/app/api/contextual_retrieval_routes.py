from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any

from app.rag.contextual_retriever import (
    contextual_retrieval_engine,
    ContextualChunk,
    RankedRetrievalResult,
)

router = APIRouter(prefix="/retrieval", tags=["Advanced Contextual Retrieval"])


class EnrichChunkRequest(BaseModel):
    chunk_text: str = Field(..., description="The raw chunk text")
    doc_title: str = Field(default="", description="Document title")
    doc_summary: str = Field(default="", description="Document global summary or context")
    chunk_id: str = Field(default="", description="Unique identifier for chunk")
    metadata: dict[str, Any] = Field(default_factory=dict)


class LateInteractionRankRequest(BaseModel):
    query: str = Field(..., description="The user search query")
    candidates: list[dict[str, Any]] = Field(..., description="List of candidate chunks with 'id', 'text', and 'score'")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")


@router.post("/enrich-chunk", response_model=ContextualChunk)
def enrich_chunk(req: EnrichChunkRequest) -> ContextualChunk:
    """Prepends document-level summary context to individual text chunk."""
    return contextual_retrieval_engine.enrich_chunk(
        chunk_text=req.chunk_text,
        doc_title=req.doc_title,
        doc_summary=req.doc_summary,
        chunk_id=req.chunk_id,
        metadata=req.metadata,
    )


@router.post("/late-interaction-rank", response_model=list[RankedRetrievalResult])
def late_interaction_rank(req: LateInteractionRankRequest) -> list[RankedRetrievalResult]:
    """Re-ranks candidate document chunks using token-level late-interaction matching."""
    return contextual_retrieval_engine.rank_and_rescore(
        query=req.query,
        candidates=req.candidates,
        top_k=req.top_k,
    )
