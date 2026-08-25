from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from app.db.database import create_db_and_tables

create_db_and_tables()
client = TestClient(app)



def test_create_and_list_chat_sessions():
    # 1. Create a new session
    resp = client.post("/chat/sessions", json={"title": "Test Session"})
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["title"] == "Test Session"
    session_id = data["session_id"]

    # 2. List sessions
    list_resp = client.get("/chat/sessions")
    assert list_resp.status_code == 200
    sessions = list_resp.json()
    assert any(s["session_id"] == session_id for s in sessions)


def test_get_session_details():
    resp = client.post("/chat/sessions", json={"title": "Detail Session"})
    session_id = resp.json()["session_id"]

    detail_resp = client.get(f"/chat/sessions/{session_id}")
    assert detail_resp.status_code == 200
    data = detail_resp.json()
    assert data["session_id"] == session_id
    assert "messages" in data
    assert isinstance(data["messages"], list)


def test_send_message_in_session():
    # Create session
    resp = client.post("/chat/sessions", json={"title": "RAG Session"})
    session_id = resp.json()["session_id"]

    # Mock rag_service.ask to avoid live Ollama call during test
    with patch("app.services.chat_session_service.rag_service.ask") as mock_ask:
        mock_ask.return_value = {
            "answer": "ChromaDB is an open-source vector store.",
            "sources": [{"filename": "doc1.txt", "chunk_number": 1, "total_chunks": 1}],
            "diagnostics": {"time": 0.1},
        }

        msg_resp = client.post(
            f"/chat/sessions/{session_id}/messages",
            json={"content": "What is ChromaDB?"},
        )
        assert msg_resp.status_code == 200
        msg_data = msg_resp.json()
        assert msg_data["session_id"] == session_id
        assert "ChromaDB is an open-source vector store." in msg_data["answer"]
        assert len(msg_data["sources"]) == 1

    # Verify message persistence
    detail_resp = client.get(f"/chat/sessions/{session_id}")
    data = detail_resp.json()
    assert len(data["messages"]) == 2  # user + assistant
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][0]["content"] == "What is ChromaDB?"
    assert data["messages"][1]["role"] == "assistant"


def test_delete_chat_session():
    resp = client.post("/chat/sessions", json={"title": "To Delete"})
    session_id = resp.json()["session_id"]

    del_resp = client.delete(f"/chat/sessions/{session_id}")
    assert del_resp.status_code == 200

    # Ensure 404 on subsequent get
    get_resp = client.get(f"/chat/sessions/{session_id}")
    assert get_resp.status_code == 404
