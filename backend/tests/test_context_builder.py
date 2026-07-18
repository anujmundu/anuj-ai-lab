from app.rag.context_builder import context_builder
from app.rag.hybrid_retriever import hybrid_retriever


QUERY = "What is ChromaDB?"
TOP_K = 5


def main():

    results = hybrid_retriever.retrieve(
        query=QUERY,
        k=TOP_K
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    #
    # Reuse the production grouping logic.
    #
    grouped = context_builder._group_by_document(
        documents=documents,
        metadatas=metadatas
    )

    #
    # Build the exact context that will be
    # sent to the LLM.
    #
    context = context_builder.build_context(
        documents=documents,
        metadatas=metadatas
    )

    print("\n" + "=" * 80)
    print("CONTEXT BUILDER DIAGNOSTICS")
    print("=" * 80)

    total_chunks = 0
    chunk_word_counts: list[int] = []

    for filename, chunks in grouped.items():

        print("\n" + "=" * 80)
        print(f"Document: {filename}.txt")
        print("=" * 80)

        for metadata, document in chunks:

            total_chunks += 1

            words = len(document.split())
            chunk_word_counts.append(words)

            print(
                f"\nChunk "
                f"{metadata['chunk_number']} / "
                f"{metadata['total_chunks']}"
            )

            print("-" * 80)
            print(document)

    print("\n" + "=" * 80)
    print("FORMATTED CONTEXT")
    print("=" * 80)

    print(context)

    print("\n" + "=" * 80)
    print("CONTEXT STATISTICS")
    print("=" * 80)

    total_words = len(context.split())

    print(f"Characters          : {len(context)}")
    print(f"Words               : {total_words}")
    print(f"Documents           : {len(grouped)}")
    print(f"Chunks              : {total_chunks}")

    if chunk_word_counts:

        average = (
            sum(chunk_word_counts)
            / len(chunk_word_counts)
        )

        print(
            f"Average Chunk Words : "
            f"{average:.1f}"
        )

        print(
            f"Largest Chunk       : "
            f"{max(chunk_word_counts)}"
        )

        print(
            f"Smallest Chunk      : "
            f"{min(chunk_word_counts)}"
        )

    print("=" * 80)


if __name__ == "__main__":
    main()