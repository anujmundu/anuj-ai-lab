from app.memory.exemplar_store import ExecutionExemplar, ExemplarStore
from app.memory.feedback_service import FeedbackService


def test_exemplar_store_search_and_format():
    store = ExemplarStore()
    ex = ExecutionExemplar(
        task_type="rag_search",
        input_query="How to configure dense retrieval in hybrid search?",
        reasoning_steps=["Check embeddings", "Generate vectors"],
        final_answer="Dense retrieval uses sentence-transformers for vector similarity.",
        quality_score=1.2,
    )
    store.add(ex)

    relevant = store.find_relevant("dense retrieval", top_k=1)
    assert len(relevant) == 1
    assert relevant[0].id == ex.id

    context_str = store.format_few_shot_context("dense retrieval")
    assert "FEW-SHOT DEMONSTRATION EXAMPLES" in context_str
    assert "dense retrieval" in context_str.lower()


def test_feedback_service_and_promotion():
    service = FeedbackService()
    rec = service.record_feedback(
        target_type="rag_answer",
        target_id="ans_42",
        vote=1,
        rating=5,
        comment="Extremely helpful!",
        query_text="What is Graph-RAG?",
        answer_text="Graph-RAG enhances vector retrieval with Knowledge Graph entities and relations.",
    )

    assert rec.vote == 1
    metrics = service.get_metrics()
    assert metrics["total_feedback"] >= 1
    assert metrics["positive_rate"] == 1.0
