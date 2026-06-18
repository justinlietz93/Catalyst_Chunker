"""Shared error types."""


class CatalystError(Exception):
    """Base error for Catalyst failures."""


class EmptySourceError(CatalystError):
    """Raised when source material has no chunkable text."""


class InvariantViolation(CatalystError):
    """Raised when an invariant blocks admission."""
