"""Collections of observations."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.observation.evidence.observation import Observation


@dataclass(frozen=True)
class EvidenceSet:
    """Evidence collected from one source."""

    source_id: str
    observations: tuple[Observation, ...]

    def by_kind(self, kind: str) -> tuple[Observation, ...]:
        return tuple(obs for obs in self.observations if obs.kind == kind)

    def by_id(self, observation_id: str) -> Observation | None:
        for observation in self.observations:
            if observation.observation_id == observation_id:
                return observation
        return None

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "observations": [obs.to_dict() for obs in self.observations],
        }
