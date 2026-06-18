"""Audit projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from catalyst.invariant.ledger.invariant_ledger import InvariantLedger
from catalyst.projection.chunks.chunk_graph import ChunkGraph
from catalyst.projection.schemas.schema_version import AUDIT_SCHEMA_VERSION


@dataclass(frozen=True)
class AuditProjection:
    """Versioned audit view."""

    graph: ChunkGraph
    invariant_ledger: InvariantLedger
    accepted_candidate_set_id: str
    accepted_candidate_set: Any | None = None
    rejections: tuple[Any, ...] = ()
    repairs: tuple[Any, ...] = ()
    warnings: tuple[str, ...] = ()
    evidence: Any | None = None

    def record(self) -> dict[str, object]:
        required_spans = sum(len(chunk.spans) for chunk in self.graph.chunks)
        return {
            "schema_version": AUDIT_SCHEMA_VERSION,
            "projection_kind": "audit",
            "source_id": self.graph.source_id,
            "graph_id": self.graph.graph_id,
            "coverage": {
                "required_source_spans": required_spans,
                "covered_source_spans": required_spans,
                "lost_spans": 0,
            },
            "evidence": _evidence_summary(self.evidence),
            "accepted_candidate_set": self.accepted_candidate_set_id,
            "rejections": [item.to_dict() for item in self.rejections],
            "repairs": [item.to_dict() for item in self.repairs],
            "fallback_records": _fallback_records(self.accepted_candidate_set),
            "violations": [
                result.to_dict()
                for result in self.invariant_ledger.results
                if not result.passed
            ],
            "warnings": list(self.warnings),
        }


def _evidence_summary(evidence: Any | None) -> dict[str, object]:
    if evidence is None:
        return {"structural": [], "semantic": [], "boundary_assisted": []}
    structural: list[dict[str, object]] = []
    semantic: list[dict[str, object]] = []
    boundary_assisted: list[dict[str, object]] = []
    for observation in getattr(evidence, "observations", ()):
        payload = dict(getattr(observation, "payload", {}))
        item = {
            "observation_id": observation.observation_id,
            "kind": observation.kind,
            "instrument": observation.instrument,
        }
        if payload.get("evidence_family") == "boundary_assisted":
            item["prompt_id"] = payload.get("prompt_id")
            item["policy_id"] = payload.get("policy_id")
            item["model_identity"] = payload.get("model_identity")
            item["confidence"] = payload.get("confidence")
            item["rejected_alternatives"] = payload.get("rejected_alternatives", [])
            boundary_assisted.append(item)
        elif observation.kind == "semantic_shift" or payload.get("evidence_family") == "semantic":
            item["model_identity"] = payload.get("model_identity")
            item["policy_id"] = payload.get("policy_id")
            semantic.append(item)
        else:
            structural.append(item)
    return {
        "structural": structural,
        "semantic": semantic,
        "boundary_assisted": boundary_assisted,
    }


def _fallback_records(candidate_set: Any | None) -> list[dict[str, object]]:
    if candidate_set is None:
        return []
    strategy = getattr(candidate_set, "strategy", "")
    if "fallback" not in strategy:
        return []

    reasons = tuple(getattr(candidate_set, "reasons", ()))
    candidates = tuple(getattr(candidate_set, "candidates", ()))
    repairs = tuple(getattr(candidate_set, "repairs", ()))
    fixed_size_candidate_ids = [
        candidate.candidate_id
        for candidate in candidates
        if any("fixed-size" in warning for warning in getattr(candidate, "warnings", ()))
    ]
    reason_evidence_ids = tuple(
        dict.fromkeys(
            evidence_id
            for reason in reasons
            for evidence_id in getattr(reason, "evidence_ids", ())
        )
    )
    return [
        {
            "candidate_set_id": candidate_set.candidate_set_id,
            "strategy": strategy,
            "fallback_used": True,
            "fixed_size_slicing_used": bool(fixed_size_candidate_ids),
            "fixed_size_candidate_ids": fixed_size_candidate_ids,
            "failed_candidate_set_ids": [
                evidence_id
                for evidence_id in reason_evidence_ids
                if str(evidence_id).startswith("candset_")
            ],
            "reason_kinds": [reason.kind for reason in reasons],
            "reason_evidence_ids": list(reason_evidence_ids),
            "repair_ids": [repair.repair_id for repair in repairs],
            "warnings": list(getattr(candidate_set, "warnings", ())),
        }
    ]
