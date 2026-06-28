from app.rag.rag_service import rag_service
from app.services.ollama_service import ollama_service


QUESTION = "What is ChromaDB?"


def main():

    response = rag_service.ask(
        question=QUESTION
    )

    generation = ollama_service.last_generation
    request = rag_service.last_request

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(response["answer"])

    print("\n" + "=" * 80)
    print("SOURCES")
    print("=" * 80)

    for source in response["sources"]:

        print(
            f"{source['filename']} "
            f"(Chunk {source['chunk_number']} / "
            f"{source['total_chunks']})"
        )

    print("\n" + "=" * 80)
    print("LLM DIAGNOSTICS")
    print("=" * 80)

    print(f"Model                : {generation['model']}")
    print(f"Temperature          : {generation['temperature']}")
    print(f"Top P                : {generation['top_p']}")
    print(f"Repeat Penalty       : {generation['repeat_penalty']}")
    print(f"Seed                 : {generation['seed']}")
    print(f"Max Tokens           : {generation['max_tokens']}")
    print(f"Stream               : {generation['stream']}")

    print()

    print(
        f"Prompt Characters    : "
        f"{generation['prompt_characters']}"
    )

    print(
        f"Prompt Words         : "
        f"{generation['prompt_words']}"
    )

    print(
        f"Response Characters  : "
        f"{generation['response_characters']}"
    )

    print(
        f"Response Words       : "
        f"{generation['response_words']}"
    )

    print(
        f"Generation Time (s)  : "
        f"{generation['latency_seconds']:.3f}"
    )

    print("\n" + "=" * 80)
    print("RAG PIPELINE")
    print("=" * 80)

    print(
        f"Retrieval (s)        : "
        f"{request['retrieval_seconds']:.3f}"
    )

    print(
        f"Context Build (s)    : "
        f"{request['context_build_seconds']:.3f}"
    )

    print(
        f"Prompt Build (s)     : "
        f"{request['prompt_build_seconds']:.3f}"
    )

    print(
        f"Generation (s)       : "
        f"{request['generation_seconds']:.3f}"
    )

    print(
        f"Total Request (s)    : "
        f"{request['total_seconds']:.3f}"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()