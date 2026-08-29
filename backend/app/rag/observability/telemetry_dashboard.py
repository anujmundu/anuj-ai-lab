from __future__ import annotations

import time
from typing import Any
from app.memory.feedback_service import feedback_service
from app.rag.cache.semantic_cache import semantic_cache
from app.rag.production.system_health import system_health_monitor
from app.rag.sharding.vector_sharder import vector_sharder


class TelemetryDashboardService:
    """
    Central telemetry dashboard service aggregating real-time metrics across all system layers.
    """

    def get_dashboard_summary(self) -> dict[str, Any]:
        health_diag = system_health_monitor.get_full_diagnostics()
        cache_stats = semantic_cache.get_stats()
        feedback_metrics = feedback_service.get_metrics()
        shards = vector_sharder.list_shards()

        return {
            "system_health": health_diag["overall_status"],
            "timestamp": time.time(),
            "metrics": {
                "cache": {
                    "total_entries": cache_stats["total_entries"],
                    "hit_rate": cache_stats["hit_rate"],
                    "hits": cache_stats["hits"],
                    "misses": cache_stats["misses"],
                },
                "feedback": {
                    "satisfaction_rate": feedback_metrics.get("positive_rate", 1.0),
                    "total_reviews": feedback_metrics.get("total_feedback", 0),
                },
                "sharding": {
                    "total_active_shards": len(shards),
                    "shards": shards,
                },
                "subsystems": health_diag["subsystems"],
            },
        }


telemetry_dashboard_service = TelemetryDashboardService()
