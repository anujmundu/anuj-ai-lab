class ResponseBuilder:
    """
    Builds the public API response returned
    by the RAG service.
    """

    def build(
        self,
        *,
        question: str,
        answer: str,
        confidence: float,
        sources: list[dict],
    ) -> dict:

        return {
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "sources": sources,
        }


response_builder = ResponseBuilder()