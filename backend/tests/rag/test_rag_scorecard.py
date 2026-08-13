from app.rag.rag_scorecard import rag_scorecard

def test_scorecard_handles_none_hallucination_risk():
    result = rag_scorecard.build(
        retrieval_quality={"coverage": 0.8},
        prompt_quality={"balanced": True},
        answer_quality={"compression_ratio": 0.8},
        hallucination={"hallucination_risk": None},
        citations={"coverage": {"coverage": 0.8}},
    )

    assert result["grounding"] == 50
    assert isinstance(result["overall"], int)
    assert result["grade"]