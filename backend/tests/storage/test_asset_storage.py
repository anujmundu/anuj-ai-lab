from __future__ import annotations

import hashlib
import io

import pytest

from app.storage.asset_storage import AssetStorage


def test_small_file_is_stored(tmp_path):

    storage = AssetStorage(
        tmp_path
    )

    content = b"hello Anuj AI Lab"

    result = storage.store(
        io.BytesIO(content),
        original_filename="hello.txt",
    )

    assert result.original_filename == "hello.txt"
    assert result.size_bytes == len(content)

    assert (
        result.checksum
        == hashlib.sha256(content).hexdigest()
    )

    stored_path = tmp_path / result.asset_id

    assert stored_path.exists()
    assert stored_path.read_bytes() == content


def test_storage_uses_streaming_reads(tmp_path):

    storage = AssetStorage(
        tmp_path,
        chunk_size=4,
    )

    class TrackingStream:

        def __init__(self, content):

            self.stream = io.BytesIO(
                content
            )

            self.read_sizes = []

        def read(self, size=-1):

            self.read_sizes.append(size)

            return self.stream.read(size)

    content = b"abcdefghijklmnopqrstuvwxyz"

    stream = TrackingStream(
        content
    )

    result = storage.store(
        stream,
        original_filename="large.bin",
    )

    assert result.size_bytes == len(content)

    assert all(
        size == 4
        for size in stream.read_sizes[:-1]
    )


def test_checksum_is_deterministic(tmp_path):

    storage = AssetStorage(
        tmp_path
    )

    content = b"same content"

    first = storage.store(
        io.BytesIO(content),
        original_filename="one.txt",
        asset_id="asset-one",
    )

    second = storage.store(
        io.BytesIO(content),
        original_filename="two.txt",
        asset_id="asset-two",
    )

    assert (
        first.checksum
        == second.checksum
    )


def test_custom_asset_id_is_preserved(tmp_path):

    storage = AssetStorage(
        tmp_path
    )

    result = storage.store(
        io.BytesIO(b"data"),
        original_filename="file.bin",
        asset_id="my-asset",
    )

    assert result.asset_id == "my-asset"

    assert (
        tmp_path / "my-asset"
    ).exists()


def test_failed_upload_does_not_leave_partial_file(
    tmp_path,
):

    storage = AssetStorage(
        tmp_path
    )

    class FailingStream:

        def __init__(self):

            self.calls = 0

        def read(self, size=-1):

            self.calls += 1

            if self.calls == 1:
                return b"partial data"

            raise RuntimeError(
                "simulated upload failure"
            )

    with pytest.raises(
        RuntimeError,
        match="simulated upload failure",
    ):
        storage.store(
            FailingStream(),
            original_filename="broken.bin",
            asset_id="failed-asset",
        )

    assert not (
        tmp_path / "failed-asset"
    ).exists()

    assert not any(
        path.name.endswith(
            ".uploading"
        )
        for path in tmp_path.iterdir()
    )