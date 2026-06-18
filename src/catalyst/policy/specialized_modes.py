"""Policy guards for specialized Catalyst modes."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.formation.selection.rejection_record import RejectionRecord
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord

SPECIALIZED_MODE_SCHEMA_VERSION = "catalyst.specialized_mode_admission.v1"
_LATE_CHUNKING_CONTEXTS = {"offline", "premium_indexing"}
_INVARIANT_REQUIREMENTS = (
    "source_lineage_required",
    "projection_schema_required",
    "audit_record_required",
    "rejection_visibility_required",
)


@dataclass(frozen=True)
class LateChunkingContext:
    """Execution context required before late chunking may run."""

    indexing_context: str = "interactive"


@dataclass(frozen=True)
class ChunkFreeRetrievalPolicy:
    """Experimental namespace for chunk-free retrieval."""

    namespace: str = "experimental"
    enabled: bool = False
    primary_mode_requested: bool = False
    required_adr: str | None = None


@dataclass(frozen=True)
class LateChunkingAdmission:
    """Versioned admission decision for late chunking."""

    source: SourceRecord
    policy: SelectionPolicy
    context: LateChunkingContext
    rejections: tuple[RejectionRecord, ...]

    @property
    def admitted(self) -> bool:
        return not self.rejections

    def record(self) -> dict[str, object]:
        return {
            "schema_version": SPECIALIZED_MODE_SCHEMA_VERSION,
            "projection_kind": "specialized_mode_admission",
            "mode": "late_chunking",
            "source_id": self.source.source_id,
            "source_spans": [self.source.full_span().to_dict()],
            "admitted": self.admitted,
            "policy": self.policy.to_dict(),
            "context": {"indexing_context": self.context.indexing_context},
            "rejections": [rejection.to_dict() for rejection in self.rejections],
            "warnings": (
                []
                if self.admitted
                else ["late chunking did not run; specialized mode admission failed"]
            ),
        }


@dataclass(frozen=True)
class ChunkFreeRetrievalAdmission:
    """Versioned admission decision for chunk-free retrieval experiments."""

    source: SourceRecord
    policy: ChunkFreeRetrievalPolicy
    rejections: tuple[RejectionRecord, ...]

    @property
    def admitted(self) -> bool:
        return not self.rejections

    def record(self) -> dict[str, object]:
        return {
            "schema_version": SPECIALIZED_MODE_SCHEMA_VERSION,
            "projection_kind": "specialized_mode_admission",
            "mode": "chunk_free_retrieval",
            "source_id": self.source.source_id,
            "source_spans": [self.source.full_span().to_dict()],
            "admitted": self.admitted,
            "policy": {
                "namespace": self.policy.namespace,
                "enabled": self.policy.enabled,
                "primary_mode_requested": self.policy.primary_mode_requested,
                "required_adr": self.policy.required_adr,
            },
            "invariant_requirements": list(_INVARIANT_REQUIREMENTS),
            "primary_mode_requires_new_adr": True,
            "rejections": [rejection.to_dict() for rejection in self.rejections],
        }


def admit_late_chunking(
    source: SourceRecord,
    policy: SelectionPolicy,
    context: LateChunkingContext,
) -> LateChunkingAdmission:
    """Evaluate whether late chunking may run."""

    rejections: list[RejectionRecord] = []
    if not policy.allow_late_chunking:
        rejections.append(
            RejectionRecord(
                rejection_id=stable_id("rej", source.source_id, "late_chunking", "policy"),
                rejected_id=source.source_id,
                reason="late chunking policy flag is disabled",
                source_spans=(source.full_span(),),
                reconsideration_trigger="enable allow_late_chunking for a specialized mode run",
            )
        )
    if context.indexing_context not in _LATE_CHUNKING_CONTEXTS:
        rejections.append(
            RejectionRecord(
                rejection_id=stable_id("rej", source.source_id, "late_chunking", "context"),
                rejected_id=source.source_id,
                reason="late chunking requires offline or premium indexing context",
                source_spans=(source.full_span(),),
                reconsideration_trigger="run in offline or premium_indexing context",
            )
        )
    return LateChunkingAdmission(
        source=source,
        policy=policy,
        context=context,
        rejections=tuple(rejections),
    )


def admit_chunk_free_retrieval(
    source: SourceRecord,
    policy: ChunkFreeRetrievalPolicy,
) -> ChunkFreeRetrievalAdmission:
    """Evaluate whether chunk-free retrieval may run as an experiment."""

    rejections: list[RejectionRecord] = []
    if policy.namespace != "experimental":
        rejections.append(_chunk_free_rejection(source, "chunk-free retrieval must use experimental namespace"))
    if not policy.enabled:
        rejections.append(_chunk_free_rejection(source, "chunk-free retrieval experiment flag is disabled"))
    if policy.primary_mode_requested and not policy.required_adr:
        rejections.append(_chunk_free_rejection(source, "primary chunk-free retrieval requires a new ADR"))
    return ChunkFreeRetrievalAdmission(source=source, policy=policy, rejections=tuple(rejections))


def _chunk_free_rejection(source: SourceRecord, reason: str) -> RejectionRecord:
    return RejectionRecord(
        rejection_id=stable_id("rej", source.source_id, "chunk_free_retrieval", reason),
        rejected_id=source.source_id,
        reason=reason,
        source_spans=(source.full_span(),),
        reconsideration_trigger="use experimental namespace, enable the experiment, or add the required ADR",
    )
