"""Boundary inspection projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from catalyst.projection.schemas.schema_version import BOUNDARY_INSPECTION_SCHEMA_VERSION


@dataclass(frozen=True)
class BoundaryInspectionProjection:
    """Versioned boundary inspection view."""

    source_id: str
    boundary_candidates: tuple[Any, ...]
    rejections: tuple[Any, ...] = ()

    def record(self) -> dict[str, object]:
        return {
            "schema_version": BOUNDARY_INSPECTION_SCHEMA_VERSION,
            "projection_kind": "boundary_inspection",
            "source_id": self.source_id,
            "boundary_candidates": [item.to_dict() for item in self.boundary_candidates],
            "rejections": [item.to_dict() for item in self.rejections],
        }
