from fastapi.testclient import TestClient
from main import app
from app.db.database import create_db_and_tables

client = TestClient(app)


def setup_module():
    create_db_and_tables()


def test_detailed_health_route():
    res = client.get("/health/detailed")
    assert res.status_code == 200
    data = res.json()
    assert data["overall_status"] in {"healthy", "degraded"}
    assert "subsystems" in data


def test_synthetic_eval_generation_route():
    res = client.post(
        "/eval/synthetic/generate",
        json={
            "chunks": [
                "FastAPI is an async Python web framework.",
                "SQLite is a self-contained serverless SQL database.",
            ]
        },
    )
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) >= 2


def test_telemetry_dashboard_route():
    res = client.get("/telemetry/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "system_health" in data
    assert "metrics" in data
    assert "cache" in data["metrics"]
    assert "feedback" in data["metrics"]
