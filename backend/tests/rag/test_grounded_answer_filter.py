from app.rag.evidence_models import (
    EvidenceAlignmentResult,
    EvidenceMatch,
    EvidenceScore,
    SentenceEvidence,
    SupportLevel,
)

from app.rag.grounded_answer_filter import (
    GroundingDecision,
    grounded_answer_filter,
)


def make_alignment(
    *,
    overall: float,
    support: SupportLevel,
) -> EvidenceAlignmentResult:

    match = EvidenceMatch(
        filename="test.txt",
        chunk_id="chunk_1",
        chunk_number=1,
        total_chunks=1,
        score=EvidenceScore(
            overall=overall,
            lexical=overall,
            embedding=overall,
        ),
        support=support,
    )

    sentence = SentenceEvidence(
        sentence="Python is a programming language.",
        best_match=match,
        candidate_matches=[match],
        support=support,
        confidence=overall,
    )

    grounded_count = (
        1
        if support == SupportLevel.GROUNDED
        else 0
    )

    partial_count = (
        1
        if support == SupportLevel.PARTIAL
        else 0
    )

    unsupported_count = (
        1
        if support == SupportLevel.UNSUPPORTED
        else 0
    )

    return EvidenceAlignmentResult(
        sentences=[sentence],
        grounded_count=grounded_count,
        partial_count=partial_count,
        unsupported_count=unsupported_count,
        average_similarity=overall,
        average_confidence=overall,
    )


def make_hallucination(
    *,
    risk: float = 0.10,
    unsupported_claims: int = 0,
    contradicted_claims: int = 0,
    contradictions_detected: int = 0,
) -> dict:

    return {
        "hallucination_risk": risk,
        "unsupported_claims": unsupported_claims,
        "contradicted_claims": contradicted_claims,
        "contradictions_detected": contradictions_detected,
    }


def make_consistency(
    *,
    score: float = 1.0,
    status: str = "consistent",
    contradicted_pairs: int = 0,
    sentence_pairs: int = 0,
) -> dict:

    return {
        "consistency_score": score,
        "status": status,
        "contradicted_pairs": contradicted_pairs,
        "sentence_pairs": sentence_pairs,
    }


def make_citation_result(
    *,
    coverage: float = 1.0,
    citation_count: int = 1,
) -> dict:

    return {
        "citations": ["[1]"] * citation_count,
        "coverage": {
            "coverage": coverage,
        },
    }


def test_strong_evidence_is_accepted():

    alignment = make_alignment(
        overall=0.90,
        support=SupportLevel.GROUNDED,
    )

    result = grounded_answer_filter.evaluate(
        answer="Python is a programming language.",
        alignment=alignment,
        hallucination=make_hallucination(),
        consistency=make_consistency(),
        citation_result=make_citation_result(),
    )

    assert result["decision"] == GroundingDecision.ACCEPT.value
    assert result["grounded"] is True
    assert result["repairable"] is False
    assert result["reason"] == (
        "answer_meets_grounding_criteria"
    )


def test_partial_evidence_is_repairable():

    alignment = make_alignment(
        overall=0.55,
        support=SupportLevel.PARTIAL,
    )

    result = grounded_answer_filter.evaluate(
        answer="Python is a programming language.",
        alignment=alignment,
        hallucination=make_hallucination(),
        consistency=make_consistency(),
        citation_result=make_citation_result(),
    )

    assert result["decision"] == GroundingDecision.REPAIR.value
    assert result["grounded"] is False
    assert result["repairable"] is True
    assert result["reason"] == (
        "partial_evidence_available"
    )


def test_unsupported_evidence_is_rejected():

    alignment = make_alignment(
        overall=0.10,
        support=SupportLevel.UNSUPPORTED,
    )

    result = grounded_answer_filter.evaluate(
        answer="Python is a programming language.",
        alignment=alignment,
        hallucination=make_hallucination(
            risk=0.80,
            unsupported_claims=1,
        ),
        consistency=make_consistency(
            score=0.50,
            status="uncertain",
        ),
        citation_result=make_citation_result(
            coverage=0.0,
            citation_count=0,
        ),
    )

    assert result["decision"] == GroundingDecision.REJECT.value
    assert result["grounded"] is False
    assert result["repairable"] is False


def test_no_evidence_is_rejected():

    alignment = EvidenceAlignmentResult()

    result = grounded_answer_filter.evaluate(
        answer="This answer has no supporting evidence.",
        alignment=alignment,
        hallucination=make_hallucination(
            risk=0.90,
            unsupported_claims=1,
        ),
        consistency=make_consistency(),
        citation_result=make_citation_result(
            coverage=0.0,
            citation_count=0,
        ),
    )

    assert result["decision"] == GroundingDecision.REJECT.value
    assert result["grounded"] is False


def test_grounding_metrics_are_present():

    alignment = make_alignment(
        overall=0.90,
        support=SupportLevel.GROUNDED,
    )

    result = grounded_answer_filter.evaluate(
        answer="Python is a programming language.",
        alignment=alignment,
        hallucination=make_hallucination(),
        consistency=make_consistency(),
        citation_result=make_citation_result(),
    )

    assert "metrics" in result
    assert "evidence" in result["metrics"]
    assert "hallucination" in result["metrics"]
    assert "consistency" in result["metrics"]
    assert "citations" in result["metrics"]


def test_grounding_decision_enum_values():

    assert GroundingDecision.ACCEPT.value == "accept"
    assert GroundingDecision.REPAIR.value == "repair"
    assert GroundingDecision.REJECT.value == "reject"