"""Catalyst-native parsed code result."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.source.records.source_record import SourceRecord


@dataclass(frozen=True)
class ParsedCode:
    """AST parser output translated into Catalyst-native evidence."""

    source: SourceRecord
    evidence: EvidenceSet
    language: str
    warnings: tuple[str, ...] = ()
