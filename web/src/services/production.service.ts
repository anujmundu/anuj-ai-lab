import { api } from "@/lib/api";

export interface DetailedHealth {
    status: "healthy" | "degraded" | "unhealthy";
    timestamp: string;
    services: {
        sqlite: { status: string; latency_ms: number };
        chromadb: { status: string; total_documents: number; collections: number };
        semantic_cache: { status: string; total_entries: number; hit_rate_pct: number };
    };
}

export interface TelemetryDashboard {
    throughput: {
        total_requests: number;
        avg_latency_ms: number;
        p95_latency_ms: number;
    };
    rag_metrics: {
        dense_searches: number;
        bm25_searches: number;
        avg_retrieval_ms: number;
        cache_hit_rate_pct: number;
    };
    agent_metrics: {
        total_tasks: number;
        success_rate_pct: number;
        avg_steps_per_task: number;
    };
}

export const productionService = {
    async getDetailedHealth(): Promise<DetailedHealth> {
        const { data } = await api.get<DetailedHealth>("/health/detailed");
        return data;
    },

    async getTelemetryDashboard(): Promise<TelemetryDashboard> {
        const { data } = await api.get<TelemetryDashboard>("/telemetry/dashboard");
        return data;
    },

    async getCacheStats(): Promise<any> {
        const { data } = await api.get("/cache/stats");
        return data;
    },

    async clearCache(): Promise<any> {
        const { data } = await api.delete("/cache/clear");
        return data;
    },

    async generateSyntheticEval(chunks: string[]): Promise<any[]> {
        const { data } = await api.post("/eval/synthetic/generate", { chunks });
        return data;
    },
};
