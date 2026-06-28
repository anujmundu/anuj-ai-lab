from app.rag.context_builder import context_builder
from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.prompt_builder import prompt_builder


QUERY = "What is ChromaDB?"
TOP_K = 5


def main():

    results = hybrid_retriever.retrieve(
        query=QUERY,
        k=TOP_K
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = context_builder.build_context(
        documents=documents,
        metadatas=metadatas
    )

    prompt = prompt_builder.build_prompt(
        question=QUERY,
        documents=context
    )

    print("\n" + "=" * 80)
    print("PROMPT BUILDER DIAGNOSTICS")
    print("=" * 80)

    print(prompt)

    print("\n" + "=" * 80)
    print("PROMPT STATISTICS")
    print("=" * 80)

    print(f"Characters : {len(prompt)}")
    print(f"Words      : {len(prompt.split())}")
    print(f"Lines      : {len(prompt.splitlines())}")

    print("=" * 80)


if __name__ == "__main__":
    main()