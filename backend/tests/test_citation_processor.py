from app.rag.citation_processor import citation_processor


def main():

    answer = (
        "ChromaDB is an open-source vector database "
        "designed for AI applications."
    )

    sources = [
        {
            "filename": "python_notes",
            "chunk_id": "python_notes_chunk_004",
            "chunk_number": 4,
            "total_chunks": 9,
        },
        {
            "filename": "sample",
            "chunk_id": "sample_chunk_001",
            "chunk_number": 1,
            "total_chunks": 1,
        },
    ]

    result = citation_processor.process(
        answer=answer,
        sources=sources
    )

    print("\n" + "=" * 80)
    print("CITATION PROCESSOR DIAGNOSTICS")
    print("=" * 80)

    print("\n" + "-" * 80)
    print("ANSWER")
    print("-" * 80)

    print(result["answer"])

    print("\n" + "-" * 80)
    print("INLINE CITATIONS")
    print("-" * 80)

    if result["citations"]:

        for citation in result["citations"]:

            print(citation)

    else:

        print("(none)")

    print("\n" + "-" * 80)
    print("SOURCE MAPPING")
    print("-" * 80)

    if result["source_mapping"]:

        for mapping in result["source_mapping"]:

            print(
                f"{mapping['citation']} -> "
                f"{mapping['filename']} "
                f"(Chunk {mapping['chunk_number']} / "
                f"{mapping['total_chunks']})"
            )

    else:

        print("(none)")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()