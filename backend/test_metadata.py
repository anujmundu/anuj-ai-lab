from app.rag.metadata import metadata_builder

metadata = metadata_builder.build(
    filename="python_book",
    chunk_number=3,
    total_chunks=12
)

print(metadata)