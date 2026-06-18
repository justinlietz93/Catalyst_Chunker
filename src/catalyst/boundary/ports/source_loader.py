"""Source loading port."""

from __future__ import annotations

from typing import Protocol


class SourceLoader(Protocol):
    """Boundary port for loading source bytes."""

    def load(self, location: str) -> bytes:
        """Load bytes from a boundary location."""
