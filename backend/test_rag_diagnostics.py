from pprint import pprint

from app.rag.rag_service import rag_service


QUESTION = "What is ChromaDB?"


def main():

    print("\nGenerating a RAG request...\n")

    rag_service.ask(
        question=QUESTION
    )

    diagnostics = rag_service.diagnostics()

    print("=" * 80)
    print("RAG DIAGNOSTICS")
    print("=" * 80)

    pprint(diagnostics)

    print("=" * 80)


if __name__ == "__main__":
    main()