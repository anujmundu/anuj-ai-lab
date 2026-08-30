from __future__ import annotations

from typing import Sequence

from app.rag.evidence_config import (
    EvidenceAlignerConfig,
    evidence_config,
)
from app.rag.evidence_models import (
    EvidenceAlignmentResult,
    EvidenceMatch,
    EvidenceScore,
    SentenceEvidence,
    SupportLevel,
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
        matcher=semantic_matcher,
        config: EvidenceAlignerConfig = evidence_config,
    ) -> None:

        self.matcher = matcher
        self.config = config

    def align(
        self,
        answer: str,
        documents: Sequence[str],
        metadatas: Sequence[dict],
    ) -> EvidenceAlignmentResult:
        """
        Align every sentence in the generated answer with
        the retrieved document chunks.
        """

        if len(documents) != len(metadatas):
            raise ValueError(
                "documents and metadatas must have the same length."
            )

        sentences = split_sentences(answer)

        sentence_results = [
            self._align_sentence(
                sentence=sentence,
                documents=documents,
                metadatas=metadatas,
            )
            for sentence in sentences
            if sentence.strip()
        ]

        return self._build_result(
            sentence_results,
        )

    def _align_sentence(
        self,
        sentence: str,
        documents: Sequence[str],
        metadatas: Sequence[dict],
    ) -> SentenceEvidence:
        """
        Align a generated sentence against the retrieved
        document chunks and return the supporting evidence.
        """

        matches = [
            self._score_candidate(
                sentence=sentence,
                document=document,
                metadata=metadata,
            )
            for document, metadata in zip(
                documents,
                metadatas,
            )
        ]

        matches.sort(
            key=lambda match: match.score.overall,
            reverse=self.config.sort_descending,
        )

        if self.config.store_all_matches:
            selected_matches = matches
        else:
            selected_matches = matches[
                : self.config.max_candidate_matches
            ]

        best_match = (
            selected_matches[0]
            if selected_matches
            else None
        )

        confidence = (
            best_match.score.overall
            if best_match is not None
            else 0.0
        )

        support = (
            best_match.support
            if best_match is not None
            else SupportLevel.UNSUPPORTED
        )

        return SentenceEvidence(
            sentence=sentence,
            best_match=best_match,
            candidate_matches=selected_matches,
            confidence=confidence,
            support=support,
        )

    def _score_candidate(
        self,
        sentence: str,
        document: str,
        metadata: dict,
    ) -> EvidenceMatch:
        """
        Score one retrieved document against a generated
        sentence and return the resulting evidence match.
        """

        score = self._compute_similarity(
            sentence=sentence,
            chunk=document,
        )

        support = self._determine_support(
            score.overall,
        )

        return EvidenceMatch(
            filename=metadata["filename"],
            chunk_id=metadata["chunk_id"],
            chunk_number=metadata["chunk_number"],
            total_chunks=metadata["total_chunks"],
            score=score,
            support=support,
        )

    def _compute_similarity(
        self,
        sentence: str,
        chunk: str,
    ) -> EvidenceScore:
        """
        Compute lexical, embedding and overall similarity
        using the shared SemanticMatcher.

        EvidenceAligner intentionally delegates all
        similarity computation to SemanticMatcher so that
        improvements to the similarity engine
        automatically benefit evidence alignment.
        """

        comparison = self.matcher.compare(
            sentence,
            chunk,
        )

        metrics = comparison["metrics"]

        return EvidenceScore(
            overall=metrics["overall"],
            lexical=metrics["lexical"],
            embedding=metrics["embedding"],
        )

    def _determine_support(
        self,
        similarity: float,
    ) -> SupportLevel:
        """
        Determine the evidence support level based on the
        overall similarity score.
        """

        if similarity >= self.config.grounded_threshold:
            return SupportLevel.GROUNDED

        if similarity >= self.config.partial_threshold:
            return SupportLevel.PARTIAL

        return SupportLevel.UNSUPPORTED

    def _build_result(
        self,
        sentence_results: list[SentenceEvidence],
    ) -> EvidenceAlignmentResult:
        """
        Build the final evidence alignment result from the
        sentence-level evidence.
        """

        grounded = sum(
            sentence.support == SupportLevel.GROUNDED
            for sentence in sentence_results
        )

        partial = sum(
            sentence.support == SupportLevel.PARTIAL
            for sentence in sentence_results
        )

        unsupported = sum(
            sentence.support == SupportLevel.UNSUPPORTED
            for sentence in sentence_results
        )

        if sentence_results:
            average_confidence = (
                sum(
                    sentence.confidence
                    for sentence in sentence_results
                )
                / len(sentence_results)
            )

            average_similarity = average_confidence
        else:
            average_confidence = 0.0
            average_similarity = 0.0

        return EvidenceAlignmentResult(
            sentences=sentence_results,
            grounded_count=grounded,
            partial_count=partial,
            unsupported_count=unsupported,
            average_similarity=average_similarity,
            average_confidence=average_confidence,
        )


evidence_aligner = EvidenceAligner()