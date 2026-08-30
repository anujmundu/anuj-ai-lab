from app.rag.ranker_config import RankerConfig


class Ranker:
    """
    Lightweight ranking stage.

    Responsibilities

    • Remove weak retrievals
    • Remove duplicate chunks
    • Limit retrieved context
    • Produce filtering diagnostics

    Future responsibilities

    • Cross-encoder reranking
    • Score normalization
    • Diversity optimization
    • Metadata-aware reranking
    """

    def __init__(
        self,
        config: RankerConfig | None = None,
    ):

        self.config = (
            config
            or RankerConfig()
        )

    def filter_results(
        self,
        results: dict,
    ) -> dict:

        docs_raw = results.get("documents", [[]])
        documents = docs_raw[0] if docs_raw and len(docs_raw) > 0 else []

        metas_raw = results.get("metadatas", [[]])
        metadatas = metas_raw[0] if metas_raw and len(metas_raw) > 0 else []

        ids_raw = results.get("ids", [[]])
        ids = ids_raw[0] if ids_raw and len(ids_raw) > 0 else []

        dists_raw = results.get("distances", [[]])
        distances = dists_raw[0] if dists_raw and len(dists_raw) > 0 else []

        rets_raw = results.get("retrieval", [[]])
        retrieval = rets_raw[0] if rets_raw and len(rets_raw) > 0 else []

        diagnostics = results.get(
            "diagnostics",
            [],
        )

        pipeline = results.get(
            "pipeline",
            {},
        )

        original_candidates = len(documents)

        filtered_documents = []
        filtered_metadatas = []
        filtered_ids = []
        filtered_distances = []
        filtered_retrieval = []

        removed_threshold = 0
        removed_duplicates = 0
        removed_limit = 0
        removed_diversification = 0

        seen_chunks = set()

        for (
            document,
            metadata,
            doc_id,
            distance,
            scores,
        ) in zip(
            documents,
            metadatas,
            ids,
            distances,
            retrieval,
        ):

            combined_score = scores.get("combined_score", 1.0) if isinstance(scores, dict) else 1.0

            if (
                combined_score
                < self.config.minimum_combined_score
            ):

                removed_threshold += 1
                continue

            if self.config.remove_duplicate_chunks:

                chunk = metadata.get("chunk_id", str(doc_id)) if isinstance(metadata, dict) else str(doc_id)

                if chunk in seen_chunks:
                    removed_duplicates += 1
                    continue

                seen_chunks.add(chunk)

            filtered_documents.append(document)
            filtered_metadatas.append(metadata)
            filtered_ids.append(doc_id)
            filtered_distances.append(distance)
            filtered_retrieval.append(scores)

        if (
            len(filtered_documents)
            > self.config.maximum_chunks
        ):

            removed_limit = (
                len(filtered_documents)
                - self.config.maximum_chunks
            )

            filtered_documents = filtered_documents[
                : self.config.maximum_chunks
            ]

            filtered_metadatas = filtered_metadatas[
                : self.config.maximum_chunks
            ]

            filtered_ids = filtered_ids[
                : self.config.maximum_chunks
            ]

            filtered_distances = filtered_distances[
                : self.config.maximum_chunks
            ]

            filtered_retrieval = filtered_retrieval[
                : self.config.maximum_chunks
            ]

        pipeline["filtering"] = {

            "input_candidates": original_candidates,

            "output_candidates": len(
                filtered_documents
            ),

            "removed_by_threshold": removed_threshold,

            "removed_as_duplicates": removed_duplicates,

            "removed_by_document_limit": removed_limit,

            "removed_by_diversification": (
                removed_diversification
            ),
        }

        pipeline["filtered_candidates"] = len(
            filtered_documents
        )

        print("\n===== RAG Search Results =====")

        for doc_id, distance in zip(
            filtered_ids,
            filtered_distances,
        ):
            print(f"{doc_id} -> {distance}")

        print("==============================\n")

        return {

            "documents": [filtered_documents],

            "metadatas": [filtered_metadatas],

            "ids": [filtered_ids],

            "distances": [filtered_distances],

            "retrieval": [filtered_retrieval],

            "diagnostics": diagnostics,

            "pipeline": pipeline,
        }


ranker = Ranker()