from __future__ import annotations

from collections.abc import Callable

from app.rag.evaluation.models import (
    EvaluationSample,
)
from app.rag.performance_profiler import (
    PerformanceProfiler,
)
from app.rag.pipelines.retrieval_pipeline import (
    RetrievalPipeline,
    retrieval_pipeline,
)
from app.rag.retrieval_models import (
    RetrievalMetadata,
    RetrievalResult,
    RetrievalScores,
)


class ProductionRetrievalAdapter:
    """
    Adapts the production RetrievalPipeline to the
    evaluation framework.

    This adapter is intentionally thin.

    It does not:
    - implement retrieval
    - implement ranking
    - implement filtering
    - implement fusion
    - access ChromaDB directly
    - change production retrieval behavior

    It only converts the production
    RetrievalPipelineResult into canonical
    RetrievalResult objects.
    """

    def __init__(
        self,
        pipeline: RetrievalPipeline | Callable = retrieval_pipeline,
    ) -> None:

        if not callable(
            getattr(
                pipeline,
                "run",
                None,
            )
        ):
            raise TypeError(
                "pipeline must provide a callable run method"
            )

        self.pipeline = pipeline

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @staticmethod
    def _metadata(
        metadata: dict | None,
        index: int,
    ) -> RetrievalMetadata:

        metadata = metadata or {}

        chunk_id = metadata.get(
            "chunk_id",
            "",
        )

        filename = metadata.get(
            "filename",
            "",
        )

        chunk_number = metadata.get(
            "chunk_number",
            0,
        )

        total_chunks = metadata.get(
            "total_chunks",
            0,
        )

        source = metadata.get(
            "source",
            "",
        )

        if not chunk_id:
            chunk_id = (
                f"{filename}_chunk_{chunk_number}"
                if filename
                else f"retrieved_chunk_{index}"
            )

        return RetrievalMetadata(
            filename=filename,
            chunk_id=chunk_id,
            chunk_number=chunk_number,
            total_chunks=total_chunks,
            source=source,
        )

    @staticmethod
    def _scores(
        retrieval: dict | None,
    ) -> RetrievalScores:

        retrieval = retrieval or {}

        return RetrievalScores(
            semantic_score=float(
                retrieval.get(
                    "semantic_score",
                    0.0,
                )
                or 0.0
            ),
            keyword_score=float(
                retrieval.get(
                    "keyword_score",
                    0.0,
                )
                or 0.0
            ),
            combined_score=float(
                retrieval.get(
                    "combined_score",
                    0.0,
                )
                or 0.0
            ),
        )

    # --------------------------------------------------
    # Conversion
    # --------------------------------------------------

    def _convert(
        self,
        *,
        documents: list[str],
        metadatas: list[dict],
        retrieval: list[dict],
    ) -> list[RetrievalResult]:

        results: list[RetrievalResult] = []

        for index, document in enumerate(
            documents
        ):

            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            score = (
                retrieval[index]
                if index < len(retrieval)
                else {}
            )

            canonical_metadata = (
                self._metadata(
                    metadata,
                    index,
                )
            )

            results.append(
                RetrievalResult(
                    doc_id=(
                        canonical_metadata.chunk_id
                    ),
                    document=document,
                    metadata=canonical_metadata,
                    scores=self._scores(
                        score
                    ),
                )
            )

        return results

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def retrieve(
        self,
        sample: EvaluationSample,
        *,
        k: int = 10,
        profiler: PerformanceProfiler | None = None,
    ) -> list[RetrievalResult]:
        """
        Execute production retrieval for one golden
        evaluation sample.
        """

        if not isinstance(
            sample,
            EvaluationSample,
        ):
            raise TypeError(
                "sample must be an EvaluationSample"
            )

        if k <= 0:
            raise ValueError(
                "k must be greater than zero"
            )

        result = self.pipeline.run(
            question=sample.question,
            k=k,
            profiler=profiler,
        )

        return self._convert(
            documents=result.documents,
            metadatas=result.metadatas,
            retrieval=result.retrieval,
        )


production_retrieval_adapter = (
    ProductionRetrievalAdapter()
)
