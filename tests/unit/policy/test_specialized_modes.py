from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.policy.specialized_modes import (
    ChunkFreeRetrievalPolicy,
    LateChunkingContext,
    admit_chunk_free_retrieval,
    admit_late_chunking,
)
from catalyst.source.records.source_record import SourceRecord


def test_late_chunking_policy_defaults_to_false() -> None:
    policy = SelectionPolicy()

    assert policy.allow_late_chunking is False
    assert policy.to_dict()["allow_late_chunking"] is False


def test_late_chunking_rejects_default_interactive_context() -> None:
    source = SourceRecord.from_bytes(b"Late chunking source.", source_kind="markdown")

    admission = admit_late_chunking(source, SelectionPolicy(), LateChunkingContext())
    record = admission.record()

    assert admission.admitted is False
    assert record["schema_version"] == "catalyst.specialized_mode_admission.v1"
    assert record["projection_kind"] == "specialized_mode_admission"
    assert record["source_spans"][0]["source_id"] == source.source_id
    assert len(record["rejections"]) == 2


def test_late_chunking_requires_offline_or_premium_context_when_enabled() -> None:
    source = SourceRecord.from_bytes(b"Late chunking source.", source_kind="markdown")
    policy = SelectionPolicy(allow_late_chunking=True)

    interactive = admit_late_chunking(source, policy, LateChunkingContext("interactive"))
    offline = admit_late_chunking(source, policy, LateChunkingContext("offline"))
    premium = admit_late_chunking(source, policy, LateChunkingContext("premium_indexing"))

    assert interactive.admitted is False
    assert interactive.rejections[0].reason == "late chunking requires offline or premium indexing context"
    assert offline.admitted is True
    assert premium.admitted is True
    assert offline.record()["rejections"] == []


def test_chunk_free_retrieval_defaults_to_disabled_experiment() -> None:
    source = SourceRecord.from_bytes(b"Chunk-free experiment source.", source_kind="markdown")

    admission = admit_chunk_free_retrieval(source, ChunkFreeRetrievalPolicy())
    record = admission.record()

    assert admission.admitted is False
    assert record["mode"] == "chunk_free_retrieval"
    assert record["source_spans"][0]["source_id"] == source.source_id
    assert record["invariant_requirements"] == [
        "source_lineage_required",
        "projection_schema_required",
        "audit_record_required",
        "rejection_visibility_required",
    ]


def test_chunk_free_retrieval_runs_only_in_experimental_namespace() -> None:
    source = SourceRecord.from_bytes(b"Chunk-free experiment source.", source_kind="markdown")

    admitted = admit_chunk_free_retrieval(source, ChunkFreeRetrievalPolicy(enabled=True))
    rejected = admit_chunk_free_retrieval(
        source,
        ChunkFreeRetrievalPolicy(namespace="retrieval", enabled=True),
    )

    assert admitted.admitted is True
    assert rejected.admitted is False
    assert rejected.rejections[0].reason == "chunk-free retrieval must use experimental namespace"


def test_chunk_free_primary_mode_requires_new_adr() -> None:
    source = SourceRecord.from_bytes(b"Chunk-free experiment source.", source_kind="markdown")

    rejected = admit_chunk_free_retrieval(
        source,
        ChunkFreeRetrievalPolicy(enabled=True, primary_mode_requested=True),
    )
    admitted = admit_chunk_free_retrieval(
        source,
        ChunkFreeRetrievalPolicy(
            enabled=True,
            primary_mode_requested=True,
            required_adr="ADR-00XX",
        ),
    )

    assert rejected.admitted is False
    assert rejected.rejections[0].reason == "primary chunk-free retrieval requires a new ADR"
    assert admitted.admitted is True
    assert admitted.record()["primary_mode_requires_new_adr"] is True
