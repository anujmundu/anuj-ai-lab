from collections import Counter

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
print("FILTER DIAGNOSTICS")
print("=" * 80)

diagnostics = results.get("diagnostics", [])

if diagnostics:

    kept = 0
    filtered = 0

    reasons = Counter()

    for item in diagnostics:

        print(f"\n{item['chunk_id']}")
        print(f"Status : {item['status']}")

        if item["status"] == "FILTERED":
            print(f"Reason : {item['reason']}")
            filtered += 1
            reasons[item["reason"]] += 1
        else:
            kept += 1

    print("\n" + "-" * 80)
    print("FILTER SUMMARY")
    print("-" * 80)

    print(f"Kept Chunks      : {kept}")
    print(f"Filtered Chunks  : {filtered}")

    if reasons:
        print("\nReasons")

        for reason, count in reasons.items():
            print(f"  {reason:<30} {count}")

else:

    print("\nNo diagnostics available.")

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

print(f"Returned Results : {len(ids)}")

documents_counter = Counter(
    metadata["filename"]
    for metadata in metadatas
)

print("\nChunks Per Document")

for filename, count in documents_counter.items():
    print(f"  {filename:<25} {count}")

print("=" * 80)