from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TenantShard:
    tenant_id: str
    workspace_id: str
    collection_name: str
    shard_index: int
    doc_count: int = 0


class VectorSharder:
    """
    Manages multi-tenant vector partitioning, horizontal sharding, and collection routing.
    """

    def __init__(self, num_shards_per_tenant: int = 4) -> None:
        self.num_shards_per_tenant = num_shards_per_tenant
        self._shards: dict[str, TenantShard] = {}

    def get_shard_index(self, key: str) -> int:
        """Determines the shard index using consistent SHA-256 hashing."""
        hash_val = int(hashlib.sha256(key.encode("utf-8")).hexdigest(), 16)
        return hash_val % self.num_shards_per_tenant

    def route_collection(
        self,
        tenant_id: str = "default",
        workspace_id: str = "default",
        partition_key: str | None = None,
    ) -> TenantShard:
        """
        Calculates and returns the isolated shard collection name for a given tenant/workspace.
        """
        routing_key = partition_key or f"{tenant_id}:{workspace_id}"
        shard_idx = self.get_shard_index(routing_key)
        collection_name = f"rag_{tenant_id}_{workspace_id}_s{shard_idx}"

        shard_key = f"{tenant_id}:{workspace_id}:{shard_idx}"
        if shard_key not in self._shards:
            shard = TenantShard(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                collection_name=collection_name,
                shard_index=shard_idx,
            )
            self._shards[shard_key] = shard

        return self._shards[shard_key]

    def list_shards(self) -> list[dict[str, Any]]:
        return [
            {
                "tenant_id": s.tenant_id,
                "workspace_id": s.workspace_id,
                "collection_name": s.collection_name,
                "shard_index": s.shard_index,
                "doc_count": s.doc_count,
            }
            for s in self._shards.values()
        ]

    def record_document_added(self, tenant_id: str, workspace_id: str, partition_key: str | None = None) -> None:
        shard = self.route_collection(tenant_id, workspace_id, partition_key)
        shard.doc_count += 1

    def clear(self) -> None:
        self._shards.clear()


vector_sharder = VectorSharder()
