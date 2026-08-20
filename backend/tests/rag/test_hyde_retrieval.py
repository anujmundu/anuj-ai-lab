from app.rag.intelligence.hyde_retrieval import (
    HyDERetrieval,
)


class FakeLLM:

    def __init__(
        self,
        response: str = "hypothetical answer",
    ) -> None:

        self.response = response
        self.calls = []

    def generate(
        self,
        *,
        prompt: str,
    ) -> str:

        self.calls.append(prompt)

        return self.response


def test_build_prompt_contains_query():

    llm = FakeLLM()

    hyde = HyDERetrieval(
        llm_service=llm,
    )

    prompt = hyde.build_prompt(
        "What is retrieval augmented generation?"
    )

    assert (
        "What is retrieval augmented generation?"
        in prompt
    )

    assert "Hypothetical document:" in prompt


def test_build_prompt_strips_query():

    llm = FakeLLM()

    hyde = HyDERetrieval(
        llm_service=llm,
    )

    prompt = hyde.build_prompt(
        "   What is Python?   "
    )

    assert "What is Python?" in prompt


def test_empty_query_is_rejected():

    llm = FakeLLM()

    hyde = HyDERetrieval(
        llm_service=llm,
    )

    try:
        hyde.build_prompt("   ")
    except ValueError as exc:
        assert str(exc) == "query must not be empty"
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_generate_returns_hypothetical_document():

    llm = FakeLLM(
        response=(
            "Python is a high-level programming "
            "language used for general-purpose software "
            "development."
        )
    )

    hyde = HyDERetrieval(
        llm_service=llm,
    )

    result = hyde.generate(
        "What is Python?"
    )

    assert result.query == "What is Python?"

    assert result.hypothetical_document == (
        "Python is a high-level programming "
        "language used for general-purpose software "
        "development."
    )

    assert len(llm.calls) == 1


def test_generate_strips_llm_response():

    llm = FakeLLM(
        response="   hypothetical document   "
    )

    hyde = HyDERetrieval(
        llm_service=llm,
    )

    result = hyde.generate(
        "Explain embeddings"
    )

    assert (
        result.hypothetical_document
        == "hypothetical document"
    )


def test_empty_llm_response_is_rejected():

    llm = FakeLLM(
        response="   "
    )

    hyde = HyDERetrieval(
        llm_service=llm,
    )

    try:
        hyde.generate(
            "Explain embeddings"
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "LLM returned an empty hypothetical document"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_hyde_does_not_execute_retrieval():

    llm = FakeLLM(
        response="hypothetical document"
    )

    hyde = HyDERetrieval(
        llm_service=llm,
    )

    result = hyde.generate(
        "What is RAG?"
    )

    # HyDE's responsibility ends at generation.
    assert result.hypothetical_document


def test_custom_prompt_template_is_supported():

    llm = FakeLLM()

    hyde = HyDERetrieval(
        llm_service=llm,
        prompt_template=(
            "Generate retrieval text for: {query}"
        ),
    )

    prompt = hyde.build_prompt(
        "Explain vector databases"
    )

    assert prompt == (
        "Generate retrieval text for: "
        "Explain vector databases"
    )