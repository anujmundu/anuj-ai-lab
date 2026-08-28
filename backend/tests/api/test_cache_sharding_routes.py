from fastapi.testclient import TestClient
from main import app
from app.db.database import create_db_and_tables

client = TestClient(app)


def setup_module():
    create_db_and_tables()


def test_cache_stats_and_clear_routes():
    stats_res = client.get("/cache/stats")
    assert stats_res.status_code == 200
    assert "hit_rate" in stats_res.json()

    clear_res = client.delete("/cache/clear")
    assert clear_res.status_code == 200
    assert clear_res.json()["status"] == "cleared"


def test_shards_route_and_list():
    route_res = client.post(
        "/shards/route",
        json={"tenant_id": "tenant_api_test", "workspace_id": "ws_api_test"},
    )
    assert route_res.status_code == 200
    shard_data = route_res.json()
    assert shard_data["tenant_id"] == "tenant_api_test"
    assert "rag_tenant_api_test_ws_api_test" in shard_data["collection_name"]

    list_res = client.get("/shards/list")
    assert list_res.status_code == 200
    assert isinstance(list_res.json(), list)


def test_batch_ingest_route():
    res = client.post(
        "/batch/ingest",
        json={
            "chunks": ["API Test Chunk A", "API Test Chunk B"],
            "batch_size": 2,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["total_chunks"] == 2
    assert data["processed_chunks"] == 2
