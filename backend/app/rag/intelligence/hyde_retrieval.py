from __future__ import annotations

from dataclasses import dataclass

from app.services.ollama_service import (
    OllamaService,
    ollama_service,
)


@dataclass(frozen=True)
class HyDEResult:
    query: str
    hypothetical_document: str


class HyDERetrieval:
    """
    Generates a hypothetical document for HyDE retrieval.

    This component deliberately does not:
        - create embeddings
        - access the vector store
        - execute retrieval
        - rerank documents

    It only transforms a user query into a hypothetical
    document that can later be embedded and retrieved against.
    """

    DEFAULT_PROMPT_TEMPLATE = (
        "Write a concise hypothetical document that "
        "would directly answer the following question. "
        "Use factual, information-rich language suitable "
        "for semantic retrieval.\n\n"
        "Question:\n"
        "{query}\n\n"
        "Hypothetical document:"
    )

    def __init__(
        self,
        *,
        llm_service: OllamaService | None = None,
        prompt_template: str = DEFAULT_PROMPT_TEMPLATE,
    ) -> None:

        self.llm_service = (
            llm_service
            or ollama_service
        )

        self.prompt_template = prompt_template

    def build_prompt(
        self,
        query: str,
    ) -> str:

        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError(
                "query must not be empty"
            )

        return self.prompt_template.format(
            query=normalized_query,
        )

    def generate(
        self,
        query: str,
    ) -> HyDEResult:

        prompt = self.build_prompt(query)

        hypothetical_document = (
            self.llm_service.generate(
                prompt=prompt,
            )
            .strip()
        )

        if not hypothetical_document:
            raise ValueError(
                "LLM returned an empty hypothetical document"
            )

        return HyDEResult(
            query=query,
            hypothetical_document=hypothetical_document,
        )


hyde_retrieval = HyDERetrieval()