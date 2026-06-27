from app.rag.context_builder import context_builder
from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.prompt_builder import prompt_builder
from app.rag.ranker import ranker
from app.services.ollama_service import ollama_service


class RAGService:

    def ask(
        self,
        question: str,
        k: int = 3
    ) -> dict:

        #
        # Retrieve candidate chunks.
        #
        results = hybrid_retriever.retrieve(
            query=question,
            k=k
        )

        #
        # Apply ranking.
        #
        results = ranker.filter_results(
            results
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        #
        # Build structured context.
        #
        context = context_builder.build_context(
            documents=documents,
            metadatas=metadatas
        )

        #
        # Build the final prompt.
        #
        prompt = prompt_builder.build_prompt(
            question=question,
            documents=context
        )

        #
        # Generate answer.
        #
        answer = ollama_service.generate(
            prompt
        )

        #
        # Build source attribution.
        #
        sources = []

        for metadata in metadatas:

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