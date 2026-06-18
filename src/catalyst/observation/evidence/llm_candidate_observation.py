"""LLM-assisted candidate observation."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.observation.evidence.observation import Observation
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan


@dataclass(frozen=True)
class LlmCandidateObservation:
    """Boundary-assisted candidate evidence from an LLM proposal."""

    span: SourceSpan
    proposal_text: str
    prompt_id: str
    policy_id: str
    model_identity: str
    confidence: float
    rejected_alternatives: tuple[str, ...] = ()

    def to_observation(self, source: SourceRecord) -> Observation:
        if self.span.source_id != source.source_id:
            raise ValueError("LLM candidate evidence must reference the source")
        if not 0 <= self.confidence <= 1:
            raise ValueError("LLM candidate confidence must be between 0 and 1")
        return Observation(
            observation_id=stable_id(
                "obs",
                source.source_id,
                "llm_candidate",
                self.span.start_char,
                self.span.end_char,
                self.prompt_id,
                self.model_identity,
            ),
            kind="llm_candidate",
            span=self.span,
            confidence=self.confidence,
            weight=0.2,
            instrument="llm_boundary_assist",
            payload={
                "evidence_family": "boundary_assisted",
                "proposal_text": self.proposal_text,
                "prompt_id": self.prompt_id,
                "policy_id": self.policy_id,
                "model_identity": self.model_identity,
                "confidence": self.confidence,
                "rejected_alternatives": list(self.rejected_alternatives),
                "source_truth": False,
            },
        )
