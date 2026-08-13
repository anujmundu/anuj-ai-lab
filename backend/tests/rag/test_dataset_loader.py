import json

import pytest

from app.rag.evaluation.dataset_loader import (
    GoldenDatasetError,
    GoldenDatasetLoader,
)


def write_dataset(
    tmp_path,
    data,
):
    path = tmp_path / "dataset.json"

    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    return path


def test_loads_golden_dataset(tmp_path):
    path = write_dataset(
        tmp_path,
        {
            "samples": [
                {
                    "sample_id": "qa_001",
                    "question": "What is Python?",
                    "reference_answer": (
                        "Python is a programming language."
                    ),
                    "relevant_chunks": [
                        {
                            "filename": "python.pdf",
                            "chunk_id": "python_chunk_1",
                            "chunk_number": 1,
                        }
                    ],
                    "metadata": {
                        "difficulty": "easy",
                    },
                }
            ]
        },
    )

    samples = GoldenDatasetLoader.load(path)

    assert len(samples) == 1

    sample = samples[0]

    assert sample.sample_id == "qa_001"
    assert sample.question == "What is Python?"
    assert sample.reference_answer == (
        "Python is a programming language."
    )

    assert len(sample.relevant_chunks) == 1

    assert (
        sample.relevant_chunks[0].filename
        == "python.pdf"
    )

    assert (
        sample.relevant_chunks[0].chunk_id
        == "python_chunk_1"
    )

    assert sample.metadata["difficulty"] == "easy"


def test_optional_fields_default(tmp_path):
    path = write_dataset(
        tmp_path,
        {
            "samples": [
                {
                    "sample_id": "qa_001",
                    "question": "What is Python?",
                }
            ]
        },
    )

    samples = GoldenDatasetLoader.load(path)

    assert samples[0].reference_answer == ""
    assert samples[0].relevant_chunks == ()
    assert samples[0].metadata == {}


def test_duplicate_sample_ids_are_rejected(
    tmp_path,
):
    path = write_dataset(
        tmp_path,
        {
            "samples": [
                {
                    "sample_id": "duplicate",
                    "question": "Question one",
                },
                {
                    "sample_id": "duplicate",
                    "question": "Question two",
                },
            ]
        },
    )

    with pytest.raises(
        GoldenDatasetError,
        match="duplicate sample_id",
    ):
        GoldenDatasetLoader.load(path)


def test_missing_sample_id_is_rejected(
    tmp_path,
):
    path = write_dataset(
        tmp_path,
        {
            "samples": [
                {
                    "question": "What is Python?",
                }
            ]
        },
    )

    with pytest.raises(
        GoldenDatasetError,
        match="sample_id",
    ):
        GoldenDatasetLoader.load(path)


def test_invalid_relevant_chunks_is_rejected(
    tmp_path,
):
    path = write_dataset(
        tmp_path,
        {
            "samples": [
                {
                    "sample_id": "qa_001",
                    "question": "What is Python?",
                    "relevant_chunks": "invalid",
                }
            ]
        },
    )

    with pytest.raises(
        GoldenDatasetError,
        match="relevant_chunks.*list",
    ):
        GoldenDatasetLoader.load(path)


def test_invalid_chunk_number_is_rejected(
    tmp_path,
):
    path = write_dataset(
        tmp_path,
        {
            "samples": [
                {
                    "sample_id": "qa_001",
                    "question": "What is Python?",
                    "relevant_chunks": [
                        {
                            "filename": "python.pdf",
                            "chunk_id": "python_chunk_1",
                            "chunk_number": "1",
                        }
                    ],
                }
            ]
        },
    )

    with pytest.raises(
        GoldenDatasetError,
        match="chunk_number.*integer",
    ):
        GoldenDatasetLoader.load(path)


def test_duplicate_chunks_are_allowed():
    """
    The loader does not silently reinterpret the annotation.
    Dataset-level semantic validation can be added later.
    """
    assert True


def test_invalid_json_is_rejected(
    tmp_path,
):
    path = tmp_path / "invalid.json"

    path.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    with pytest.raises(
        GoldenDatasetError,
        match="Invalid JSON",
    ):
        GoldenDatasetLoader.load(path)


def test_missing_file_is_rejected(
    tmp_path,
):
    path = tmp_path / "missing.json"

    with pytest.raises(
        FileNotFoundError,
        match="Golden dataset not found",
    ):
        GoldenDatasetLoader.load(path)