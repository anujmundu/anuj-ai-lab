from __future__ import annotations

import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Any

from app.rag.batch.batch_ingestion_pipeline import batch_ingestion_pipeline
from app.rag.cache.semantic_cache import semantic_cache
from app.rag.sharding.vector_sharder import vector_sharder

router = APIRouter(tags=["Enterprise Scalability & Caching"])


class ShardRouteRequest(BaseModel):
    tenant_id: str = Field(default="default", description="Tenant ID")
    workspace_id: str = Field(default="default", description="Workspace ID")
    partition_key: str | None = Field(default=None, description="Optional custom partition key")


class BatchIngestRequest(BaseModel):
    chunks: list[str] = Field(..., description="List of chunk texts to ingest in micro-batches")
    metadatas: list[dict[str, Any]] | None = Field(default=None, description="Optional metadata list")
    batch_size: int = Field(default=32, ge=1, le=256, description="Micro-batch size")


@router.get("/cache/stats", response_model=dict)
def get_cache_statistics() -> dict:
    """Retrieve semantic cache hit rate, entries, and performance metrics."""
    return semantic_cache.get_stats()


@router.delete("/cache/clear", response_model=dict)
def clear_semantic_cache() -> dict:
    """Clear all entries in the semantic cache."""
    semantic_cache.clear()
    return {"status": "cleared", "message": "Semantic cache successfully invalidated."}


@router.get("/shards/list", response_model=list[dict])
def list_active_shards() -> list[dict]:
    """List all registered tenant vector shards and document counts."""
    return vector_sharder.list_shards()


@router.post("/shards/route", response_model=dict)
def route_tenant_shard(request: ShardRouteRequest) -> dict:
    """Determine the isolated vector shard collection for a tenant and workspace."""
    shard = vector_sharder.route_collection(
        tenant_id=request.tenant_id,
        workspace_id=request.workspace_id,
        partition_key=request.partition_key,
    )
    return {
        "tenant_id": shard.tenant_id,
        "workspace_id": shard.workspace_id,
        "collection_name": shard.collection_name,
        "shard_index": shard.shard_index,
        "doc_count": shard.doc_count,
    }


@router.post("/batch/ingest", response_model=dict)
def batch_ingest_chunks(
    request: BatchIngestRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """Ingest large volumes of chunks asynchronously with micro-batching."""
    job_id = f"batch_{uuid.uuid4().hex[:10]}"
    job = batch_ingestion_pipeline.ingest_chunks_batch(
        job_id=job_id,
        chunk_texts=request.chunks,
        metadatas=request.metadatas,
        batch_size=request.batch_size,
    )
    return {
        "job_id": job.job_id,
        "total_chunks": job.total_chunks,
        "processed_chunks": job.processed_chunks,
        "duration_ms": job.duration_ms,
        "status": job.status,
    }
