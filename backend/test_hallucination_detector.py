from app.rag.hallucination_detector import hallucination_detector


TEST_CASES = [
    {
        "title": "Supported Answer",
        "context": (
            "ChromaDB is an open-source vector database. "
            "It stores vector embeddings for semantic search."
        ),
        "answer": (
            "ChromaDB is an open-source vector database "
            "that stores vector embeddings."
        ),
    },
    {
        "title": "Partially Supported Answer",
        "context": (
            "ChromaDB stores vector embeddings "
            "for semantic search."
        ),
        "answer": (
            "ChromaDB stores vector embeddings "
            "and was created by OpenAI."
        ),
    },
    {
        "title": "Hallucinated Answer",
        "context": (
            "ChromaDB stores vector embeddings "
            "for semantic search."
        ),
        "answer": (
            "ChromaDB was invented in 1984 "
            "by Google."
        ),
    },
]


def print_result(result: dict) -> None:

    print(
        f"Risk                    : "
        f"{result['hallucination_risk']:.2f}"
    )

    print(
        f"Context Overlap         : "
        f"{result['context_overlap']:.2f}"
    )

    print(
        f"Supported Terms         : "
        f"{result['supported_terms']}"
    )

    print(
        f"Unsupported Terms       : "
        f"{result['unsupported_terms']}"
    )

    print(
        f"Potential Hallucination : "
        f"{result['is_potential_hallucination']}"
    )

    print(
        "Unsupported Term List   : "
        f"{result['unsupported_term_list']}"
    )


def main():

    print("\n" + "=" * 80)
    print("HALLUCINATION DETECTOR DIAGNOSTICS")
    print("=" * 80)

    for case in TEST_CASES:

        print("\n" + "-" * 80)
        print(case["title"])
        print("-" * 80)

        print("\nContext:\n")
        print(case["context"])

        print("\nAnswer:\n")
        print(case["answer"])

        result = hallucination_detector.detect(
            answer=case["answer"],
            context=case["context"]
        )

        print("\nDiagnostics:\n")

        print_result(result)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()