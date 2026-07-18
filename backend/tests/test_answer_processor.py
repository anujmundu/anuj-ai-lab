from app.rag.answer_processor import answer_processor


CONTEXT = """
ChromaDB is an open-source vector database designed for AI applications.
It stores vector embeddings and enables semantic search.
"""


UNKNOWN = (
    "I don't have enough information "
    "in the retrieved documents."
)


TEST_CASES = [
    (
        "Normal Answer",
        (
            "ChromaDB is an open-source vector database "
            "designed for AI applications."
        ),
    ),
    (
        "Unknown Answer",
        UNKNOWN,
    ),
    (
        "Empty Answer",
        "",
    ),
    (
        "Messy Whitespace",
        "\n\n  ChromaDB    stores     vector "
        "embeddings.\n\n",
    ),
]


def main():

    print("\n" + "=" * 80)
    print("ANSWER PROCESSOR DIAGNOSTICS")
    print("=" * 80)

    for name, raw_answer in TEST_CASES:

        result = answer_processor.process(
            answer=raw_answer,
            context=CONTEXT
        )

        print("\n" + "-" * 80)
        print(name)
        print("-" * 80)

        print("\nOriginal:")
        print(repr(raw_answer))

        print("\nProcessed:")
        print(result["answer"])

        print(
            "\nConfidence : "
            f"{result['confidence']:.2f}"
        )

        print(
            f"Unknown     : "
            f"{result['is_unknown']}"
        )

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()