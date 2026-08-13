from __future__ import annotations

import json
from pathlib import Path

from app.rag.evaluation.models import (
    EvaluationSample,
    RelevantChunk,
)


class GoldenDatasetError(ValueError):
    """Raised when a golden dataset is malformed."""


class GoldenDatasetLoader:
    """
    Loads golden RAG evaluation samples from JSON.

    The loader is intentionally independent of:
    - ChromaDB
    - the LLM
    - the retrieval pipeline
    - FastAPI

    Its only responsibility is converting validated JSON data
    into EvaluationSample objects.
    """

    @staticmethod
    def _require_string(
        value: object,
        field: str,
    ) -> str:
        if not isinstance(value, str) or not value.strip():
            raise GoldenDatasetError(
                f"{field} must be a non-empty string"
            )

        return value

    @classmethod
    def _parse_relevant_chunk(
        cls,
        data: object,
        index: int,
    ) -> RelevantChunk:
        if not isinstance(data, dict):
            raise GoldenDatasetError(
                f"relevant_chunks[{index}] must be an object"
            )

        filename = cls._require_string(
            data.get("filename"),
            f"relevant_chunks[{index}].filename",
        )

        chunk_id = cls._require_string(
            data.get("chunk_id"),
            f"relevant_chunks[{index}].chunk_id",
        )

        chunk_number = data.get(
            "chunk_number",
            0,
        )

        if (
            not isinstance(chunk_number, int)
            or isinstance(chunk_number, bool)
        ):
            raise GoldenDatasetError(
                f"relevant_chunks[{index}].chunk_number "
                "must be an integer"
            )

        if chunk_number < 0:
            raise GoldenDatasetError(
                f"relevant_chunks[{index}].chunk_number "
                "must be >= 0"
            )

        return RelevantChunk(
            filename=filename,
            chunk_id=chunk_id,
            chunk_number=chunk_number,
        )

    @classmethod
    def _parse_sample(
        cls,
        data: object,
        index: int,
    ) -> EvaluationSample:
        if not isinstance(data, dict):
            raise GoldenDatasetError(
                f"samples[{index}] must be an object"
            )

        sample_id = cls._require_string(
            data.get("sample_id"),
            f"samples[{index}].sample_id",
        )

        question = cls._require_string(
            data.get("question"),
            f"samples[{index}].question",
        )

        reference_answer = data.get(
            "reference_answer",
            "",
        )

        if not isinstance(reference_answer, str):
            raise GoldenDatasetError(
                f"samples[{index}].reference_answer "
                "must be a string"
            )

        raw_chunks = data.get(
            "relevant_chunks",
            [],
        )

        if not isinstance(raw_chunks, list):
            raise GoldenDatasetError(
                f"samples[{index}].relevant_chunks "
                "must be a list"
            )

        relevant_chunks = tuple(
            cls._parse_relevant_chunk(
                chunk,
                chunk_index,
            )
            for chunk_index, chunk in enumerate(
                raw_chunks
            )
        )

        metadata = data.get(
            "metadata",
            {},
        )

        if not isinstance(metadata, dict):
            raise GoldenDatasetError(
                f"samples[{index}].metadata "
                "must be an object"
            )

        return EvaluationSample(
            sample_id=sample_id,
            question=question,
            relevant_chunks=relevant_chunks,
            reference_answer=reference_answer,
            metadata=metadata,
        )

    @classmethod
    def load(
        cls,
        path: str | Path,
    ) -> list[EvaluationSample]:
        """
        Load a golden dataset from a JSON file.

        Expected root structure:

        {
            "samples": [
                {
                    "sample_id": "...",
                    "question": "...",
                    "reference_answer": "...",
                    "relevant_chunks": [],
                    "metadata": {}
                }
            ]
        }
        """

        dataset_path = Path(path)

        if not dataset_path.exists():
            raise FileNotFoundError(
                f"Golden dataset not found: {dataset_path}"
            )

        if not dataset_path.is_file():
            raise GoldenDatasetError(
                f"Golden dataset path is not a file: "
                f"{dataset_path}"
            )

        try:
            with dataset_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except json.JSONDecodeError as exc:
            raise GoldenDatasetError(
                f"Invalid JSON in golden dataset: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise GoldenDatasetError(
                "Golden dataset root must be an object"
            )

        raw_samples = data.get("samples")

        if not isinstance(raw_samples, list):
            raise GoldenDatasetError(
                "Golden dataset must contain a "
                "'samples' list"
            )

        samples = [
            cls._parse_sample(
                sample,
                index,
            )
            for index, sample in enumerate(
                raw_samples
            )
        ]

        sample_ids = [
            sample.sample_id
            for sample in samples
        ]

        if len(sample_ids) != len(set(sample_ids)):
            raise GoldenDatasetError(
                "Golden dataset contains duplicate "
                "sample_id values"
            )

        return samples


golden_dataset_loader = GoldenDatasetLoader()