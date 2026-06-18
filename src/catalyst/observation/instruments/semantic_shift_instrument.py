"""Optional semantic shift observation."""

from __future__ import annotations

import re

from catalyst.observation.evidence.observation import Observation
from catalyst.observation.evidence.semantic_shift_observation import SemanticShiftObservation
from catalyst.observation.instruments.paragraph_instrument import ParagraphInstrument
from catalyst.source.records.source_record import SourceRecord

_WORD_RE = re.compile(r"[A-Za-z0-9_]+")


class SemanticShiftInstrument:
    """Observe local semantic discontinuity as optional refinement evidence."""

    name = "semantic_shift"

    def __init__(
        self,
        *,
        minimum_discontinuity: float = 0.7,
        model_identity: str = "local-lexical-v1",
        policy_id: str = "semantic-refinement-optional",
    ) -> None:
        self.minimum_discontinuity = minimum_discontinuity
        self.model_identity = model_identity
        self.policy_id = policy_id

    def observe(self, source: SourceRecord) -> tuple[Observation, ...]:
        paragraphs = ParagraphInstrument().observe(source)
        observations: list[Observation] = []
        for left, right in zip(paragraphs, paragraphs[1:]):
            discontinuity = _discontinuity(
                source.text_for(left.span),
                source.text_for(right.span),
            )
            if discontinuity < self.minimum_discontinuity:
                continue
            observations.append(
                SemanticShiftObservation(
                    left_span=left.span,
                    right_span=right.span,
                    discontinuity=discontinuity,
                    model_identity=self.model_identity,
                    policy_id=self.policy_id,
                    evidence_ids=(left.observation_id, right.observation_id),
                ).to_observation(source)
            )
        return tuple(observations)


def _discontinuity(left: str, right: str) -> float:
    left_terms = _terms(left)
    right_terms = _terms(right)
    if not left_terms or not right_terms:
        return 0.0
    overlap = len(left_terms & right_terms) / len(left_terms | right_terms)
    return round(1.0 - overlap, 6)


def _terms(text: str) -> set[str]:
    return {match.group(0).lower() for match in _WORD_RE.finditer(text)}
