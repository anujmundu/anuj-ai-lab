from app.rag.sharding.vector_sharder import VectorSharder


def test_vector_sharder_deterministic_routing():
    sharder = VectorSharder(num_shards_per_tenant=4)
    shard_a1 = sharder.route_collection(tenant_id="tenant_alpha", workspace_id="ws_main")
    shard_a2 = sharder.route_collection(tenant_id="tenant_alpha", workspace_id="ws_main")

    assert shard_a1.collection_name == shard_a2.collection_name
    assert shard_a1.tenant_id == "tenant_alpha"
    assert 0 <= shard_a1.shard_index < 4


def test_vector_sharder_multi_tenant_isolation():
    sharder = VectorSharder()
    shard_t1 = sharder.route_collection(tenant_id="tenant_1", workspace_id="finance")
    shard_t2 = sharder.route_collection(tenant_id="tenant_2", workspace_id="finance")

    assert shard_t1.collection_name != shard_t2.collection_name
    assert "tenant_1" in shard_t1.collection_name
    assert "tenant_2" in shard_t2.collection_name


def test_vector_sharder_list_and_document_count():
    sharder = VectorSharder()
    sharder.record_document_added(tenant_id="org_xyz", workspace_id="default")
    sharder.record_document_added(tenant_id="org_xyz", workspace_id="default")

    shards = sharder.list_shards()
    assert len(shards) >= 1
    found = next((s for s in shards if s["tenant_id"] == "org_xyz"), None)
    assert found is not None
    assert found["doc_count"] == 2
