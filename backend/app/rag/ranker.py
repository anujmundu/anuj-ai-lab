class Ranker:
    """
    Lightweight ranking stage.

    Currently this stage only logs the retrieved
    documents and preserves retrieval metadata.

    Future versions may perform:

    • Cross-encoder reranking
    • Score normalization
    • Diversity optimization
    • Metadata-aware reranking
    """

    def filter_results(
        self,
        results: dict,
    ) -> dict:

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        ids = results["ids"][0]
        distances = results["distances"][0]

        retrieval = results.get(
            "retrieval",
            [[]],
        )[0]

        diagnostics = results.get(
            "diagnostics",
            [],
        )

        pipeline = results.get(
            "pipeline",
            {},
        )

        print("\n===== RAG Search Results =====")

        for doc_id, distance in zip(ids, distances):
            print(f"{doc_id} -> {distance}")

        print("==============================\n")

        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "ids": [ids],
            "distances": [distances],
            "retrieval": [retrieval],
            "diagnostics": diagnostics,
            "pipeline": pipeline,
        }


ranker = Ranker()