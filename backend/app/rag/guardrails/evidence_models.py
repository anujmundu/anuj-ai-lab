from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SupportLevel(str, Enum):
    """Represents how well retrieved evidence supports a generated sentence."""

    GROUNDED = "grounded"
    PARTIAL = "partial"
    UNSUPPORTED = "unsupported"


@dataclass(slots=True, frozen=True)
class EvidenceScore:
    """
    Similarity metrics between a sentence and a retrieved chunk.
    """

    overall: float
    lexical: float
    embedding: float


@dataclass(slots=True, frozen=True)
class EvidenceMatch:
    """
    Represents one retrieved chunk supporting a sentence.
    """

    filename: str
    chunk_id: str
    chunk_number: int
    total_chunks: int

    score: EvidenceScore

    support: SupportLevel


@dataclass(slots=True)
class SentenceEvidence:
    """
    Evidence collected for one generated sentence.
    """

    sentence: str

    best_match: EvidenceMatch | None = None

    candidate_matches: list[EvidenceMatch] = field(default_factory=list)

    support: SupportLevel = SupportLevel.UNSUPPORTED

    confidence: float = 0.0
    
    @property
    def has_support(self) -> bool:
        return (
            self.support
            != SupportLevel.UNSUPPORTED
        )
        
    @property
    def match_count(self) -> int:
        return len(self.candidate_matches)
    
    @property
    def has_matches(self) -> bool:
        return bool(self.candidate_matches)


@dataclass(slots=True)
class EvidenceAlignmentResult:
    """
    Complete evidence alignment result for an answer.
    """

    sentences: list[SentenceEvidence] = field(default_factory=list)

    grounded_count: int = 0
    partial_count: int = 0
    unsupported_count: int = 0

    average_similarity: float = 0.0
    average_confidence: float = 0.0
    
    @property
    def total_sentences(self) -> int:
        return len(self.sentences)
    
    @property
    def grounding_score(self) -> float:
        """
        Compute the grounding score based on the number of grounded and partially grounded sentences.
        """
        total = self.total_sentences

        if total == 0:
            return 0.0

        return round(
            (
                self.grounded_count
                + (0.5 * self.partial_count)
            ) / total,
            3,
        )
        
    @property
    def overall_support(self) -> SupportLevel:

        score = self.grounding_score

        if score >= 0.70:
            return SupportLevel.GROUNDED

        if score >= 0.50:
            return SupportLevel.PARTIAL

        return SupportLevel.UNSUPPORTED
    
    @property
    def grounded_sentences(self) -> list[SentenceEvidence]:
        return [
            sentence
            for sentence in self.sentences
            if sentence.support == SupportLevel.GROUNDED
        ]
        
    @property
    def partial_sentences(self) -> list[SentenceEvidence]:
        return [
            sentence
            for sentence in self.sentences
            if sentence.support == SupportLevel.PARTIAL
        ]
    
    @property
    def supported_sentences(self) -> list[SentenceEvidence]:
        return [
            sentence
            for sentence in self.sentences
            if sentence.has_support
        ]
        
    @property
    def unsupported_sentences(self) -> list[SentenceEvidence]:
        return [
            sentence
            for sentence in self.sentences
            if sentence.support == SupportLevel.UNSUPPORTED
        ]