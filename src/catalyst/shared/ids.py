"""Deterministic identifiers and hashes."""

from __future__ import annotations

from hashlib import sha256


def content_hash(value: bytes | str) -> str:
    """Return a SHA-256 hex digest for bytes or text."""

    data = value.encode("utf-8") if isinstance(value, str) else value
    return sha256(data).hexdigest()


def stable_id(prefix: str, *parts: object, size: int = 16) -> str:
    """Create a deterministic compact ID from stable parts."""

    joined = "\x1f".join(str(part) for part in parts)
    return f"{prefix}_{content_hash(joined)[:size]}"
