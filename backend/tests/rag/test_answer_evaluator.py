from app.rag.evaluation.answer_evaluator import (
    answer_evaluator,
)
from app.rag.evaluation.models import (
    EvaluationSample,
)


def make_sample():
    return EvaluationSample(
        sample_id="answer_001",
        question="What is Python?",
        reference_answer=(
            "Python is a programming language."
        ),
    )


def make_grounding(
    *,
    grounding_score=0.9,
    supported_ratio=1.0,
    unsupported_ratio=0.0,
    average_confidence=0.85,
    decision="accept",
    grounded=True,
    repairable=False,
):
    return {
        "decision": decision,
        "grounded": grounded,
        "repairable": repairable,
        "metrics": {
            "evidence": {
                "grounding_score": grounding_score,
                "supported_ratio": supported_ratio,
                "unsupported_ratio": unsupported_ratio,
                "average_confidence": average_confidence,
            }
        },
    }


def make_hallucination(
    risk=0.10,
):
    return {
        "hallucination_risk": risk,
    }


def make_citations(
    coverage=0.90,
):
    return {
        "coverage": {
            "coverage": coverage,
        }
    }


def test_evaluator_preserves_grounding_metrics():

    result = answer_evaluator.evaluate(
        sample=make_sample(),

        grounding_result=make_grounding(
            grounding_score=0.8,
            supported_ratio=0.9,
            unsupported_ratio=0.1,
            average_confidence=0.75,
        ),

        hallucination=make_hallucination(
            0.2
        ),

        citations=make_citations(
            0.85
        ),
    )

    assert result.sample_id == "answer_001"

    assert result.grounding_score == 0.8
    assert result.supported_ratio == 0.9
    assert result.unsupported_ratio == 0.1
    assert result.average_confidence == 0.75

    assert result.hallucination_risk == 0.2
    assert result.citation_coverage == 0.85


def test_evaluator_preserves_grounding_decision():

    result = answer_evaluator.evaluate(
        sample=make_sample(),

        grounding_result=make_grounding(
            decision="repair",
            grounded=False,
            repairable=True,
        ),

        hallucination=make_hallucination(
            0.4
        ),

        citations=make_citations(
            0.5
        ),
    )

    assert result.grounding_decision == "repair"
    assert result.grounded is False
    assert result.repairable is True


def test_evaluator_handles_none_hallucination_risk():

    result = answer_evaluator.evaluate(
        sample=make_sample(),

        grounding_result=make_grounding(),

        hallucination={
            "hallucination_risk": None,
        },

        citations=make_citations(),
    )

    assert result.hallucination_risk is None


def test_evaluator_handles_missing_grounding_metrics():

    result = answer_evaluator.evaluate(
        sample=make_sample(),

        grounding_result={
            "decision": "reject",
            "grounded": False,
            "repairable": False,
            "metrics": {},
        },

        hallucination=make_hallucination(
            0.9
        ),

        citations=make_citations(
            0.0
        ),
    )

    assert result.grounding_score == 0.0
    assert result.supported_ratio == 0.0
    assert result.unsupported_ratio == 0.0
    assert result.average_confidence == 0.0

    assert result.hallucination_risk == 0.9
    assert result.citation_coverage == 0.0


def test_evaluator_handles_missing_citation_coverage():

    result = answer_evaluator.evaluate(
        sample=make_sample(),

        grounding_result=make_grounding(),

        hallucination=make_hallucination(),

        citations={},
    )

    assert result.citation_coverage == 0.0


def test_evaluator_does_not_invent_consistency_score():

    result = answer_evaluator.evaluate(
        sample=make_sample(),

        grounding_result=make_grounding(),

        hallucination=make_hallucination(),

        citations=make_citations(),
    )

    assert result.consistency_score == 0.0


def test_evaluator_rounds_metrics():

    result = answer_evaluator.evaluate(
        sample=make_sample(),

        grounding_result=make_grounding(
            grounding_score=0.876543,
            supported_ratio=0.912345,
            unsupported_ratio=0.087654,
            average_confidence=0.834567,
        ),

        hallucination=make_hallucination(
            0.123456
        ),

        citations=make_citations(
            0.987654
        ),
    )

    assert result.grounding_score == 0.8765
    assert result.supported_ratio == 0.9123
    assert result.unsupported_ratio == 0.0877
    assert result.average_confidence == 0.8346
    assert result.hallucination_risk == 0.1235
    assert result.citation_coverage == 0.9877