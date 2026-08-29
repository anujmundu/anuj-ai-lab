from fastapi.testclient import TestClient
from main import app
from app.db.database import create_db_and_tables

client = TestClient(app)


def setup_module():
    create_db_and_tables()


def test_enrich_chunk_route():
    res = client.post(
        "/retrieval/enrich-chunk",
        json={
            "chunk_text": "Net revenue reached $500M.",
            "doc_title": "Annual Summary",
            "doc_summary": "Summary of fiscal year 2026.",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "Annual Summary" in data["contextualized_text"]
    assert "Net revenue reached $500M." in data["contextualized_text"]


def test_late_interaction_rank_route():
    res = client.post(
        "/retrieval/late-interaction-rank",
        json={
            "query": "revenue earnings",
            "candidates": [
                {"id": "1", "text": "Something completely unrelated", "score": 0.8},
                {"id": "2", "text": "Total revenue and quarterly earnings report", "score": 0.6},
            ],
            "top_k": 2,
        },
    )
    assert res.status_code == 200
    ranked = res.json()
    assert len(ranked) == 2
    assert ranked[0]["chunk_id"] == "2"
