from fastapi.testclient import TestClient
from main import app
from app.db.database import create_db_and_tables
from app.collaboration.hitl import hitl_gate

client = TestClient(app)


def setup_module():
    create_db_and_tables()


def test_create_and_get_collaboration_session():
    res = client.post(
        "/collaboration/sessions",
        json={"goal": "Design a distributed knowledge graph"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    session_id = data["session_id"]

    # Get session
    get_res = client.get(f"/collaboration/sessions/{session_id}")
    assert get_res.status_code == 200
    session_data = get_res.json()
    assert session_data["session_id"] == session_id
    assert session_data["goal"] == "Design a distributed knowledge graph"


def test_list_collaboration_sessions():
    res = client.get("/collaboration/sessions")
    assert res.status_code == 200
    sessions = res.json()
    assert isinstance(sessions, list)
    assert len(sessions) >= 1


def test_hitl_approval_route():
    session_id = "test_hitl_sess_99"
    hitl_gate.request_approval(session_id, "Modify database schema")

    res = client.post(
        f"/collaboration/sessions/{session_id}/approve",
        json={"approved": True},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_approved"]


def test_stream_collaboration_dialogue():
    create_res = client.post(
        "/collaboration/sessions",
        json={"goal": "Synthesize AI ethics guidelines"},
    )
    session_id = create_res.json()["session_id"]

    stream_res = client.get(f"/collaboration/sessions/{session_id}/stream")
    assert stream_res.status_code == 200
    assert "text/event-stream" in stream_res.headers["content-type"]
