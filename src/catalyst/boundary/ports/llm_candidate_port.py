"""LLM candidate boundary port."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class LlmCandidatePrompt:
    """Prompt record sent to a boundary LLM candidate proposer."""

    prompt_id: str
    source_id: str
    policy_id: str
    text: str


@dataclass(frozen=True)
class LlmCandidateProposal:
    """Candidate text proposed by a boundary LLM."""

    proposal_id: str
    text: str
    model_identity: str
    confidence: float
    rejected_alternatives: tuple[str, ...] = ()


@runtime_checkable
class LlmCandidatePort(Protocol):
    """Boundary port for LLM-assisted candidate proposals."""

    def propose(self, prompt: LlmCandidatePrompt) -> tuple[LlmCandidateProposal, ...]:
        """Return candidate proposals without admitting them as source truth."""
