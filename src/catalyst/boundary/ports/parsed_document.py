"""Catalyst-native parsed document result."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.source.records.source_record import SourceRecord


@dataclass(frozen=True)
class ParsedDocument:
    """Document parser output translated into Catalyst-native records."""

    source: SourceRecord
    evidence: EvidenceSet
    warnings: tuple[str, ...] = ()
