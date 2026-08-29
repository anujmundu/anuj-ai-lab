from __future__ import annotations

import time
from typing import Any
from sqlmodel import Session, select
from app.db.database import engine
from app.rag.cache.semantic_cache import semantic_cache
from app.rag.vector_store import vector_store


class SystemHealthMonitor:
    """
    Comprehensive diagnostics and health checks for all subsystem dependencies.
    """

    def check_sqlite_health(self) -> dict[str, Any]:
        start = time.perf_counter()
        try:
            with Session(engine) as db_session:
                db_session.exec(select(1)).first()
            latency_ms = round((time.perf_counter() - start) * 1000.0, 2)
            return {"status": "healthy", "latency_ms": latency_ms}
        except Exception as exc:
            return {"status": "unhealthy", "error": str(exc)}

    def check_vector_store_health(self) -> dict[str, Any]:
        start = time.perf_counter()
        try:
            count = vector_store.collection.count()
            latency_ms = round((time.perf_counter() - start) * 1000.0, 2)
            return {
                "status": "healthy",
                "collection_name": vector_store.collection.name,
                "document_count": count,
                "latency_ms": latency_ms,
            }
        except Exception as exc:
            return {"status": "unhealthy", "error": str(exc)}

    def check_cache_health(self) -> dict[str, Any]:
        stats = semantic_cache.get_stats()
        return {
            "status": "healthy",
            "stats": stats,
        }

    def get_full_diagnostics(self) -> dict[str, Any]:
        sqlite_diag = self.check_sqlite_health()
        vector_diag = self.check_vector_store_health()
        cache_diag = self.check_cache_health()

        all_healthy = (
            sqlite_diag.get("status") == "healthy"
            and vector_diag.get("status") == "healthy"
            and cache_diag.get("status") == "healthy"
        )

        return {
            "overall_status": "healthy" if all_healthy else "degraded",
            "timestamp": time.time(),
            "subsystems": {
                "sqlite": sqlite_diag,
                "vector_store": vector_diag,
                "semantic_cache": cache_diag,
            },
        }


system_health_monitor = SystemHealthMonitor()
