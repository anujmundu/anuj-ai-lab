from app.rag.hallucination_detector import hallucination_detector


def test_hallucination_detector_supported_answer():
    context = "ChromaDB is an open-source vector database."
    answer = "ChromaDB is an open-source vector database."

    result = hallucination_detector.detect(
        answer=answer,
        context=context,
    )

    assert result["hallucination_risk"] < 0.5
    assert not result["is_potential_hallucination"]


def test_hallucination_detector_unsupported_answer():
    context = "ChromaDB is an open-source vector database."
    answer = "ChromaDB was invented in 1984 by alien civilizations."

    result = hallucination_detector.detect(
        answer=answer,
        context=context,
    )

    assert result["hallucination_risk"] > 0.0