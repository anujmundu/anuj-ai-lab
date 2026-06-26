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
        metadatas = results["metadatas"][0]

        prompt = prompt_builder.build(
            question,
            documents
        )

        answer = ollama_service.generate(prompt)

        sources = []

        for metadata in metadatas:

            if metadata:

                sources.append(
                    {
                        "filename": metadata["filename"],
                        "chunk_id": metadata["chunk_id"],
                        "chunk_number": metadata["chunk_number"],
                        "total_chunks": metadata["total_chunks"]
                    }
                )

        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }


rag_service = RAGService()