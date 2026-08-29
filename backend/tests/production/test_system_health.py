from app.db.database import create_db_and_tables
from app.rag.production.system_health import SystemHealthMonitor


def setup_module():
    create_db_and_tables()


def test_sqlite_health_check():
    monitor = SystemHealthMonitor()
    res = monitor.check_sqlite_health()
    assert res["status"] == "healthy"
    assert res["latency_ms"] >= 0


def test_vector_store_health_check():
    monitor = SystemHealthMonitor()
    res = monitor.check_vector_store_health()
    assert res["status"] == "healthy"
    assert res["document_count"] >= 0


def test_cache_health_check():
    monitor = SystemHealthMonitor()
    res = monitor.check_cache_health()
    assert res["status"] == "healthy"
    assert "stats" in res


def test_full_system_diagnostics():
    monitor = SystemHealthMonitor()
    diag = monitor.get_full_diagnostics()
    assert diag["overall_status"] in {"healthy", "degraded"}
    assert "sqlite" in diag["subsystems"]
    assert "vector_store" in diag["subsystems"]
    assert "semantic_cache" in diag["subsystems"]
