"""Shared error types."""


class CatalystError(Exception):
    """Base error for Catalyst failures."""


class InvariantViolation(CatalystError):
    """Raised when an invariant blocks admission."""
