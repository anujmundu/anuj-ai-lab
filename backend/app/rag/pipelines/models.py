from __future__ import annotations

from dataclasses import dataclass

from app.rag.query.models import QueryAnalysisResult

@dataclass(slots=True)
class RetrievalPipelineResult:

    documents: list[str]
    metadatas: list[dict]
    retrieval: list[dict]
    pipeline: dict
    diagnostics: dict

    query_analysis: QueryAnalysisResult

    requested_k: int
    effective_k: int

    retrieval_seconds: float


@dataclass(slots=True)
class ContextPipelineResult:

    context: str

    context_build_seconds: float