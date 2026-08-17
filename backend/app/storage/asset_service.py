from __future__ import annotations

import uuid

from dataclasses import dataclass
from typing import BinaryIO

from sqlmodel import Session

from app.db.models import Asset
from app.storage.asset_storage import (
    AssetStorage,
    StoredAsset,
)


@dataclass(frozen=True, slots=True)
class AssetServiceResult:
    asset: Asset
    stored: StoredAsset | None = None


class AssetService:
    """
    Coordinates persistent asset metadata with
    streaming byte storage.

    Responsibilities:

    1. Create an asset record.
    2. Mark the asset as uploading.
    3. Stream the incoming bytes to AssetStorage.
    4. Persist storage metadata.
    5. Mark successful uploads as completed.
    6. Mark failed uploads as failed.

    This service deliberately does not know about:

        - FastAPI
        - RAG
        - embeddings
        - document parsing
        - video processing
        - background workers
    """

    STATUS_CREATED = "created"
    STATUS_UPLOADING = "uploading"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    def __init__(
        self,
        storage: AssetStorage,
    ) -> None:

        self.storage = storage

    def create_asset(
        self,
        session: Session,
        *,
        original_filename: str,
        mime_type: str = "application/octet-stream",
    ) -> Asset:

        if not original_filename:
            raise ValueError(
                "original_filename must not be empty"
            )

        asset = Asset(
            asset_id=uuid.uuid4().hex,
            filename=original_filename,
            original_filename=original_filename,
            mime_type=mime_type,
            size_bytes=0,
            storage_path="",
            status=self.STATUS_CREATED,
            progress=0.0,
        )

        session.add(asset)
        session.commit()
        session.refresh(asset)

        return asset

    def upload(
        self,
        session: Session,
        file: BinaryIO,
        *,
        original_filename: str,
        mime_type: str = "application/octet-stream",
    ) -> AssetServiceResult:

        asset = self.create_asset(
            session,
            original_filename=original_filename,
            mime_type=mime_type,
        )

        asset.status = self.STATUS_UPLOADING
        asset.progress = 0.0

        session.add(asset)
        session.commit()
        session.refresh(asset)

        try:

            stored = self.storage.store(
                file,
                original_filename=original_filename,
                asset_id=asset.asset_id,
            )

            asset.filename = original_filename
            asset.original_filename = original_filename
            asset.mime_type = mime_type
            asset.size_bytes = stored.size_bytes
            asset.storage_path = stored.storage_path
            asset.checksum = stored.checksum
            asset.status = self.STATUS_COMPLETED
            asset.progress = 1.0

            session.add(asset)
            session.commit()
            session.refresh(asset)

            return AssetServiceResult(
                asset=asset,
                stored=stored,
            )

        except Exception:

            asset.status = self.STATUS_FAILED
            asset.progress = 0.0

            session.add(asset)
            session.commit()
            session.refresh(asset)

            raise


asset_service = AssetService(
    storage=AssetStorage()
)