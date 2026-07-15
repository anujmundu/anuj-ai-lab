from dataclasses import dataclass


@dataclass(slots=True)
class PipelineHealthConfig:
    """
    Configuration for pipeline health evaluation.

    Produces a high-level health report from
    existing pipeline diagnostics.
    """

    enabled: bool = True

    retrieval_good_threshold: float = 0.70
    retrieval_fair_threshold: float = 0.45

    hallucination_warning_threshold: float = 0.50

    answer_good_threshold: float = 0.70
    answer_fair_threshold: float = 0.45