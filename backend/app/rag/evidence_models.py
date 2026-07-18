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

    confidence: float

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