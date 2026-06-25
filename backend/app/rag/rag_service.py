from app.rag.retriever import retriever
from app.rag.prompt_builder import prompt_builder
from app.services.ollama_service import ollama_service


class RAGService:

    def ask(
        self,
        question: str,
        k: int = 3
    ) -> dict:

        results = retriever.retrieve(
            question,
            k
        )

        documents = results["documents"][0]

        prompt = prompt_builder.build_prompt(
            question,
            documents
        )

        answer = ollama_service.generate(
            prompt
        )

        return {
            "question": question,
            "documents": documents,
            "answer": answer
        }


rag_service = RAGService()