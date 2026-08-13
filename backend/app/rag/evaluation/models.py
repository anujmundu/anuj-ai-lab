from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class RelevantChunk:
    """
    Ground-truth reference to a relevant retrieved chunk.

    Evaluation operates at chunk level so retrieval quality can
    be measured independently from answer generation.
    """

    filename: str

    chunk_id: str

    chunk_number: int = 0


@dataclass(slots=True, frozen=True)
class EvaluationSample:
    """
    One golden evaluation example.

    A sample contains the user question, optional reference answer,
    and the chunks that are considered relevant ground truth.
    """

    sample_id: str

    question: str

    relevant_chunks: tuple[RelevantChunk, ...] = ()

    reference_answer: str = ""

    metadata: dict = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class RetrievalEvaluationResult:
    """
    Retrieval metrics for one evaluation sample.
    """

    sample_id: str

    hit_at_1: float = 0.0
    hit_at_3: float = 0.0
    hit_at_5: float = 0.0
    hit_at_10: float = 0.0

    precision_at_1: float = 0.0
    precision_at_3: float = 0.0
    precision_at_5: float = 0.0
    precision_at_10: float = 0.0

    recall_at_1: float = 0.0
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    recall_at_10: float = 0.0

    reciprocal_rank: float = 0.0

    ndcg_at_5: float = 0.0
    ndcg_at_10: float = 0.0


@dataclass(slots=True)
class AnswerEvaluationResult:
    """
    Evaluation signals for one generated answer.

    These metrics are derived from the existing RAG verification
    pipeline rather than implementing another verification system.
    """

    sample_id: str

    grounding_score: float = 0.0

    supported_ratio: float = 0.0

    unsupported_ratio: float = 0.0

    average_confidence: float = 0.0

    hallucination_risk: float | None = None

    consistency_score: float = 0.0

    citation_coverage: float = 0.0

    grounding_decision: str = ""

    grounded: bool = False

    repairable: bool = False


@dataclass(slots=True)
class BenchmarkResult:
    """
    Aggregate result of an evaluation benchmark run.
    """

    total_samples: int = 0

    retrieval: dict = field(default_factory=dict)

    answers: dict = field(default_factory=dict)

    runtime: dict = field(default_factory=dict)

    metadata: dict = field(default_factory=dict)