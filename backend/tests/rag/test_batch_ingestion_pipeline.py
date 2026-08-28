from app.rag.batch.batch_ingestion_pipeline import BatchIngestionPipeline


def test_batch_ingestion_pipeline_execution():
    pipeline = BatchIngestionPipeline(default_batch_size=2)
    chunks = [
        "Chunk 1: FastAPI framework high performance async.",
        "Chunk 2: SQLite lightweight relational persistence.",
        "Chunk 3: Sentence-transformers dense embedding model.",
        "Chunk 4: ChromaDB vector store collection indexing.",
    ]
    metadatas = [{"source": f"doc_{i}.md"} for i in range(4)]

    job = pipeline.ingest_chunks_batch(
        job_id="test_batch_job_1",
        chunk_texts=chunks,
        metadatas=metadatas,
        batch_size=2,
    )

    assert job.status == "completed"
    assert job.total_chunks == 4
    assert job.processed_chunks == 4
    assert job.duration_ms > 0
    assert pipeline.get_job("test_batch_job_1") is not None
