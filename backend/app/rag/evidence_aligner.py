from __future__ import annotations

from typing import Sequence

from app.rag.embedding_provider import EmbeddingProvider
from app.rag.evidence_config import (
    EvidenceAlignerConfig,
    evidence_config,
)
from app.rag.evidence_models import (
    EvidenceAlignmentResult,
    SentenceEvidence,
)
from app.rag.semantic_matcher import semantic_matcher
from app.rag.text_utils import split_sentences


class EvidenceAligner:
    """
    Aligns generated answer sentences with retrieved
    document chunks.

    This class is responsible for determining which
    retrieved chunk best supports every sentence in
    the generated answer.

    Future consumers:

    - CitationGrounder
    - HallucinationDetector
    - AnswerConsistencyChecker
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider | None = None,
        config: EvidenceAlignerConfig = evidence_config,
    ):

        self.embedding_provider = (
            embedding_provider
            or semantic_matcher.embedding_provider
        )

        self.config = config

    def align(
        self,
        answer: str,
        retrieved_chunks: Sequence,
    ) -> EvidenceAlignmentResult:
        """
        Main entry point.
        """

        raise NotImplementedError

    def _align_sentence(
        self,
        sentence: str,
        retrieved_chunks: Sequence,
    ) -> SentenceEvidence:

        raise NotImplementedError

    def _score_candidate(
        self,
        sentence: str,
        chunk,
    ):

        raise NotImplementedError

    def _compute_lexical_similarity(
        self,
        sentence: str,
        chunk_text: str,
    ) -> float:

        raise NotImplementedError

    def _compute_embedding_similarity(
        self,
        sentence: str,
        chunk_text: str,
    ) -> float:

        raise NotImplementedError

    def _combine_scores(
        self,
        lexical: float,
        embedding: float,
    ) -> float:

        raise NotImplementedError

    def _determine_support(
        self,
        similarity: float,
    ):

        raise NotImplementedError

    def _build_result(
        self,
        sentence_results: list[SentenceEvidence],
    ) -> EvidenceAlignmentResult:

        raise NotImplementedError


evidence_aligner = EvidenceAligner()