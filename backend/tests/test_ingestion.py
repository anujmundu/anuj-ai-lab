from app.rag.ingestion_service import ingestion_service

result = ingestion_service.ingest(
    "sample.txt"
)

print(result)