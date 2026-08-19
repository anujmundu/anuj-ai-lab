import io

import pytest

from app.storage.asset_reader import AssetReader


def test_reader_rejects_invalid_chunk_size():

    with pytest.raises(
        ValueError,
        match="chunk_size",
    ):
        AssetReader(chunk_size=0)


def test_reader_opens_existing_asset(tmp_path):

    path = tmp_path / "asset.bin"
    path.write_bytes(b"hello world")

    reader = AssetReader(
        chunk_size=4,
    )

    with reader.open(path) as file:

        assert file.read() == b"hello world"


def test_reader_rejects_missing_asset(tmp_path):

    reader = AssetReader()

    with pytest.raises(
        FileNotFoundError,
        match="not found",
    ):
        reader.open(
            tmp_path / "missing.bin"
        )


def test_reader_iterates_in_bounded_chunks():

    reader = AssetReader(
        chunk_size=4,
    )

    chunks = list(
        reader.iter_chunks(
            io.BytesIO(
                b"abcdefghij"
            )
        )
    )

    assert chunks == [
        b"abcd",
        b"efgh",
        b"ij",
    ]


def test_reader_does_not_require_entire_asset_in_memory():

    reader = AssetReader(
        chunk_size=3,
    )

    stream = io.BytesIO(
        b"123456789"
    )

    iterator = reader.iter_chunks(stream)

    assert next(iterator) == b"123"
    assert next(iterator) == b"456"
    assert next(iterator) == b"789"

    with pytest.raises(StopIteration):
        next(iterator)