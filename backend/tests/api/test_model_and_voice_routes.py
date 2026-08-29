from fastapi.testclient import TestClient
from main import app
from app.db.database import create_db_and_tables

client = TestClient(app)


def setup_module():
    create_db_and_tables()


def test_get_available_models_route():
    res = client.get("/models/available")
    assert res.status_code == 200
    data = res.json()
    assert "installed_models" in data
    assert "preferred_tiers" in data


def test_route_model_request_route():
    res = client.post(
        "/models/route",
        json={"query": "def solve_math(): return 42"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["task_type"] == "code_execution"
    assert "selected_model" in data


def test_voice_synthesize_route():
    res = client.post(
        "/voice/synthesize",
        json={"text": "Hello world from Anuj AI Lab", "voice": "af_sarah"},
    )
    assert res.status_code == 200
    assert res.headers["content-type"] == "audio/wav"
    assert len(res.content) > 1000
