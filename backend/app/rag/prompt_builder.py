class PromptBuilder:

    def build(
        self,
        question: str,
        documents: list[str]
    ) -> str:

        context = "\n\n".join(documents)

        prompt = f"""
You are a helpful AI assistant.

Answer the user's question using ONLY the information provided in the context below.

If the answer is not contained in the context, say:

"I don't have enough information in the retrieved documents."

-------------------------
Context:

{context}

-------------------------

Question:

{question}

-------------------------

Answer:
"""

        return prompt.strip()


prompt_builder = PromptBuilder()