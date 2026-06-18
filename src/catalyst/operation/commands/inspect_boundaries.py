"""Inspect observed boundaries."""

from __future__ import annotations

from catalyst.formation.boundaries.boundary_candidate import BoundaryCandidate
from catalyst.formation.boundaries.boundary_score import BoundaryScore
from catalyst.observation.instruments.collect import observe_source
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord


def inspect_boundaries(raw_bytes: bytes, *, location: str | None = None) -> tuple[str, tuple[BoundaryCandidate, ...]]:
    """Return boundary candidates from structural observations."""

    source = SourceRecord.from_bytes(raw_bytes, source_kind="markdown", location=location)
    evidence = observe_source(source)
    boundaries: list[BoundaryCandidate] = []
    for observation in evidence.by_kind("paragraph"):
        boundaries.append(
            BoundaryCandidate(
                boundary_id=stable_id("bnd", observation.observation_id, observation.span.start_char),
                source_id=source.source_id,
                position=observation.span.start_char,
                score=BoundaryScore(value=0.85, evidence_ids=(observation.observation_id,)),
                accepted=True,
            )
        )
    return source.source_id, tuple(boundaries)
