from unittest.mock import Mock

from app.rag.builders.diagnostics_builder import DiagnosticsBuilder


def make_retrieval_diagnostics():
    return {
        "strategy": "multi_query",
        "semantic_candidates": 20,
        "keyword_candidates": 6,
        "fused_candidates": 5,
        "filtered_candidates": 3,
        "requested_k": 3,
        "effective_k": 3,
        "retrieved_documents": 3,
        "query": {
            "text": "What is Python?",
            "intent": "definition",
            "complexity": "simple",
            "ambiguity": "medium",
            "requires_rewrite": False,
            "requires_multi_query": True,
        },
    }


def test_retrieval_diagnostics_preserve_strategy():
    diagnostics = make_retrieval_diagnostics()

    assert diagnostics["strategy"] == "multi_query"


def test_retrieval_diagnostics_preserve_candidate_counts():
    diagnostics = make_retrieval_diagnostics()

    assert diagnostics["semantic_candidates"] == 20
    assert diagnostics["keyword_candidates"] == 6
    assert diagnostics["fused_candidates"] == 5
    assert diagnostics["filtered_candidates"] == 3


def test_retrieval_diagnostics_preserve_effective_k():
    diagnostics = make_retrieval_diagnostics()

    assert diagnostics["requested_k"] == 3
    assert diagnostics["effective_k"] == 3
    assert diagnostics["retrieved_documents"] == 3


def test_retrieval_diagnostics_preserve_query_analysis():
    diagnostics = make_retrieval_diagnostics()

    query = diagnostics["query"]

    assert query["text"] == "What is Python?"
    assert query["intent"] == "definition"
    assert query["complexity"] == "simple"
    assert query["ambiguity"] == "medium"
    assert query["requires_rewrite"] is False
    assert query["requires_multi_query"] is True


def test_multi_query_diagnostics_are_distinguishable():
    diagnostics = make_retrieval_diagnostics()

    assert diagnostics["strategy"] == "multi_query"
    assert diagnostics["semantic_candidates"] >= diagnostics["fused_candidates"]
    assert diagnostics["keyword_candidates"] >= diagnostics["filtered_candidates"]
    assert diagnostics["fused_candidates"] >= diagnostics["filtered_candidates"]


def test_diagnostics_builder_imports():
    builder = DiagnosticsBuilder()

    assert builder is not None