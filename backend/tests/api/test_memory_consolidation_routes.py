from fastapi.testclient import TestClient
from main import app
from app.db.database import create_db_and_tables

client = TestClient(app)


def setup_module():
    create_db_and_tables()


def test_consolidate_endpoint():
    res = client.post("/memory/consolidate")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert "memories_created" in data


def test_feedback_and_metrics_endpoints():
    fb_res = client.post(
        "/memory/feedback",
        json={
            "target_type": "chat_message",
            "target_id": "msg_999",
            "vote": 1,
            "rating": 5,
            "comment": "Awesome speed!",
        },
    )
    assert fb_res.status_code == 200
    assert fb_res.json()["vote"] == 1

    metrics_res = client.get("/memory/feedback/metrics")
    assert metrics_res.status_code == 200
    assert metrics_res.json()["total_feedback"] >= 1


def test_list_exemplars_endpoint():
    res = client.get("/memory/exemplars")
    assert res.status_code == 200
    exemplars = res.json()
    assert isinstance(exemplars, list)
    assert len(exemplars) >= 1


def test_graph_optimize_endpoint():
    res = client.post("/rag/graph/optimize")
    assert res.status_code == 200
    assert res.json()["status"] == "optimized"
