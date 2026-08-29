from app.rag.contextual_retriever import (
    ContextualRetrievalEngine,
    contextual_retrieval_engine,
)


def test_enrich_chunk_with_header():
    chunk = contextual_retrieval_engine.enrich_chunk(
        chunk_text="The company's operating margin increased to 24%.",
        doc_title="Q3 Financial Report",
        doc_summary="Analysis of company Q3 earnings and profitability metrics.",
    )
    assert "[Document: Q3 Financial Report" in chunk.contextualized_text
    assert "Summary Context: Analysis of company Q3 earnings" in chunk.contextualized_text
    assert "operating margin increased to 24%" in chunk.contextualized_text


def test_enrich_chunk_without_header():
    chunk = contextual_retrieval_engine.enrich_chunk("Plain text without context.")
    assert chunk.contextualized_text == "Plain text without context."


def test_late_interaction_score():
    engine = ContextualRetrievalEngine()
    # High match
    score_high = engine.calculate_late_interaction_score(
        query="operating margin",
        document_text="The annual operating margin was 24 percent.",
    )
    assert score_high > 0.6

    # Zero match
    score_zero = engine.calculate_late_interaction_score(
        query="satellite orbit",
        document_text="The annual operating margin was 24 percent.",
    )
    assert score_zero == 0.0


def test_rank_and_rescore():
    engine = ContextualRetrievalEngine(late_interaction_weight=0.5)
    candidates = [
        {"id": "doc_1", "text": "Unrelated fruit apple banana", "score": 0.9},
        {"id": "doc_2", "text": "Detailed operating margin analysis", "score": 0.7},
    ]

    ranked = engine.rank_and_rescore("operating margin", candidates, top_k=2)
    assert len(ranked) == 2
    # doc_2 should get boosted by late-interaction match
    assert ranked[0].chunk_id == "doc_2"
    assert ranked[0].late_interaction_score > ranked[1].late_interaction_score
