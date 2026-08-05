from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RetrievalPipelineResult:
    """
    Result produced by the retrieval stage.

    This becomes the input for the ContextPipeline.
    """

    documents: list[str]

    metadatas: list[dict]

    retrieval: dict

    pipeline: dict

    diagnostics: dict

    retrieval_seconds: float


@dataclass(slots=True)
class ContextPipelineResult:

    context: str

    context_build_seconds: float