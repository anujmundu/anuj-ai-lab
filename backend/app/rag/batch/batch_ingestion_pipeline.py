from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any
from app.rag.embedding_service import embedding_service
from app.rag.vector_store import vector_store



@dataclass(slots=True)
class BatchIngestionJob:
    job_id: str
    total_chunks: int
    batch_size: int = 32
    processed_chunks: int = 0
    duration_ms: float = 0.0
    status: str = "pending"
    error: str | None = None


class BatchIngestionPipeline:
    """
    High-throughput asynchronous micro-batch ingestion pipeline.
    Batches chunk embeddings and vector store insertions to achieve high throughput.
    """

    def __init__(self, default_batch_size: int = 32) -> None:
        self.default_batch_size = default_batch_size
        self._jobs: dict[str, BatchIngestionJob] = {}

    def ingest_chunks_batch(
        self,
        job_id: str,
        chunk_texts: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        batch_size: int | None = None,
    ) -> BatchIngestionJob:
        """
        Processes a list of text chunks in micro-batches with embedding computation.
        """
        bsize = batch_size or self.default_batch_size
        job = BatchIngestionJob(
            job_id=job_id,
            total_chunks=len(chunk_texts),
            batch_size=bsize,
            status="running",
        )
        self._jobs[job_id] = job

        start_time = time.perf_counter()

        try:
            for i in range(0, len(chunk_texts), bsize):
                batch_chunks = chunk_texts[i : i + bsize]
                batch_meta = metadatas[i : i + bsize] if metadatas else None

                # Compute embeddings in batch
                embeddings = [embedding_service.embed(text) for text in batch_chunks]

                # Bulk insert into vector store
                doc_ids = [f"{job_id}_chk_{i + idx}" for idx in range(len(batch_chunks))]
                vector_store.collection.add(
                    documents=batch_chunks,
                    embeddings=embeddings,
                    ids=doc_ids,
                    metadatas=batch_meta,
                )

                job.processed_chunks += len(batch_chunks)



            job.status = "completed"
            job.duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return job

        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)
            job.duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return job

    def get_job(self, job_id: str) -> BatchIngestionJob | None:
        return self._jobs.get(job_id)

    def clear(self) -> None:
        self._jobs.clear()


batch_ingestion_pipeline = BatchIngestionPipeline()
