from fastapi.testclient import TestClient
from main import app
from app.db.database import create_db_and_tables

client = TestClient(app)


def setup_module():
    create_db_and_tables()


def test_create_and_get_agent_task():
    response = client.post(
        "/agents/tasks",
        json={"goal": "Calculate 100 * 25", "max_steps": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    task_id = data["task_id"]

    # Get task
    get_res = client.get(f"/agents/tasks/{task_id}")
    assert get_res.status_code == 200
    task_data = get_res.json()
    assert task_data["task_id"] == task_id
    assert task_data["goal"] == "Calculate 100 * 25"


def test_list_agent_tasks():
    response = client.get("/agents/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert len(tasks) >= 1


def test_stream_agent_task_progress():
    create_res = client.post(
        "/agents/tasks",
        json={"goal": "Explain ChromaDB and BM25", "max_steps": 3},
    )
    task_id = create_res.json()["task_id"]

    stream_res = client.get(f"/agents/tasks/{task_id}/stream")
    assert stream_res.status_code == 200
    assert "text/event-stream" in stream_res.headers["content-type"]
