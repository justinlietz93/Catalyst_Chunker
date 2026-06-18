"""Selection policy."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectionPolicy:
    """Policy for selecting admitted chunk candidates."""

    mode: str = "retrieval"
    hard_max_tokens: int = 1200
    target_tokens: int = 650
    prefer_structure: bool = True
    allow_semantic_refinement: bool = False
    allow_late_chunking: bool = False
    require_ast_for_code: bool = True
    max_repair_ratio: float = 0.10
    max_orphan_ratio: float = 0.02

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "hard_max_tokens": self.hard_max_tokens,
            "target_tokens": self.target_tokens,
            "prefer_structure": self.prefer_structure,
            "allow_semantic_refinement": self.allow_semantic_refinement,
            "allow_late_chunking": self.allow_late_chunking,
            "require_ast_for_code": self.require_ast_for_code,
            "max_repair_ratio": self.max_repair_ratio,
            "max_orphan_ratio": self.max_orphan_ratio,
        }
