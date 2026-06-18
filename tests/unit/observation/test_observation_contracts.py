import pytest

from catalyst.observation.evidence.observation import Observation


def test_observation_rejects_missing_source_reference() -> None:
    with pytest.raises(ValueError):
        Observation(
            observation_id="obs",
            kind="bad",
            span=None,  # type: ignore[arg-type]
            confidence=1.0,
            weight=1.0,
            instrument="fixture",
        )
