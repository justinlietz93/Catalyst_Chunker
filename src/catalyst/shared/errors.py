"""Shared error types."""

from __future__ import annotations

from typing import Any


class CatalystError(Exception):
    """Base error for Catalyst failures."""

    error_code = "catalyst.error"

    def __init__(
        self,
        message: str = "",
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.error_code,
            "message": self.message or str(self),
            "details": dict(self.details),
        }


class EmptySourceError(CatalystError):
    """Raised when source material has no chunkable text."""

    error_code = "source.empty"


class InvariantViolation(CatalystError):
    """Raised when an invariant blocks admission."""

    error_code = "invariant.violation"
