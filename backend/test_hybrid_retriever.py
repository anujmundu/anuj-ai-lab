from app.rag.hybrid_retriever import hybrid_retriever

results = hybrid_retriever.retrieve(
    query="What is ChromaDB?",
    k=5
)

print("\n" + "=" * 80)
print("HYBRID RETRIEVAL DIAGNOSTICS")
print("=" * 80)

ids = results["ids"][0]
documents = results["documents"][0]
metadatas = results["metadatas"][0]
retrieval = results["retrieval"][0]

for rank, (
    doc_id,
    document,
    metadata,
    scores
) in enumerate(
    zip(
        ids,
        documents,
        metadatas,
        retrieval
    ),
    start=1
):

    print(f"\nRank #{rank}")
    print("-" * 80)

    print(f"Chunk ID         : {doc_id}")
    print(f"Filename         : {metadata['filename']}")
    print(
        f"Chunk            : "
        f"{metadata['chunk_number']} / {metadata['total_chunks']}"
    )

    print(f"Semantic Score   : {scores['semantic_score']:.4f}")
    print(f"Keyword Score    : {scores['keyword_score']:.4f}")
    print(f"Combined Score   : {scores['combined_score']:.4f}")

    if scores["semantic_rank"] is not None:
        print(f"Semantic Rank    : {scores['semantic_rank']}")

    if scores["keyword_rank"] is not None:
        print(f"Keyword Rank     : {scores['keyword_rank']}")

    preview = document.replace("\n", " ")

    if len(preview) > 180:
        preview = preview[:180] + "..."

    print("\nPreview\n")
    print(preview)

print("\n" + "=" * 80)
print(f"Total Results : {len(ids)}")
print("=" * 80)