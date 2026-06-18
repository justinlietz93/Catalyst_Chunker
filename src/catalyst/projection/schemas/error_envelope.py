"""Projection error envelope."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorEnvelope:
    """Machine-readable public error."""

    schema_version: str
    projection_kind: str
    error_code: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "projection_kind": self.projection_kind,
            "error": {
                "code": self.error_code,
                "message": self.message,
            },
        }
