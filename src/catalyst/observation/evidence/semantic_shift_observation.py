"""Semantic shift observation record."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.observation.evidence.observation import Observation
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan


@dataclass(frozen=True)
class SemanticShiftObservation:
    """Semantic discontinuity evidence between adjacent source spans."""

    left_span: SourceSpan
    right_span: SourceSpan
    discontinuity: float
    model_identity: str
    policy_id: str
    evidence_ids: tuple[str, ...] = ()

    def to_observation(self, source: SourceRecord) -> Observation:
        if self.left_span.source_id != source.source_id or self.right_span.source_id != source.source_id:
            raise ValueError("semantic shift spans must belong to the source")
        if not 0 <= self.discontinuity <= 1:
            raise ValueError("semantic discontinuity must be between 0 and 1")

        start_char = min(self.left_span.start_char, self.right_span.start_char)
        end_char = max(self.left_span.end_char, self.right_span.end_char)
        span = _span_from_chars(source, start_char, end_char)
        return Observation(
            observation_id=stable_id(
                "obs",
                source.source_id,
                "semantic_shift",
                self.left_span.start_char,
                self.right_span.start_char,
                self.discontinuity,
                self.model_identity,
                self.policy_id,
            ),
            kind="semantic_shift",
            span=span,
            confidence=min(0.95, 0.45 + (self.discontinuity / 2)),
            weight=0.35,
            instrument="semantic_shift",
            payload={
                "evidence_family": "semantic",
                "discontinuity": self.discontinuity,
                "left_span": self.left_span.to_dict(),
                "right_span": self.right_span.to_dict(),
                "model_identity": self.model_identity,
                "policy_id": self.policy_id,
                "source_truth": False,
                "evidence_ids": list(self.evidence_ids),
            },
        )


def _span_from_chars(source: SourceRecord, start_char: int, end_char: int) -> SourceSpan:
    return SourceSpan(
        source_id=source.source_id,
        start_byte=len(source.canonical_text[:start_char].encode("utf-8")),
        end_byte=len(source.canonical_text[:end_char].encode("utf-8")),
        start_char=start_char,
        end_char=end_char,
    )
