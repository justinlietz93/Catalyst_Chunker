"""Minimal reversible normalizer."""

from __future__ import annotations

from catalyst.shared.ids import stable_id
from catalyst.source.normalization.normalization_trace import NormalizationTrace
from catalyst.source.records.source_record import SourceRecord


class ReversibleNormalizer:
    """Current normalizer preserves text exactly and records that fact."""

    def normalize(self, source: SourceRecord) -> tuple[SourceRecord, NormalizationTrace]:
        trace = NormalizationTrace(
            trace_id=stable_id("norm", source.source_id, "identity"),
            source_id=source.source_id,
            reversible=True,
            lossy=False,
            notes=("identity normalization",),
        )
        normalized = SourceRecord(
            identity=source.identity,
            canonical_text=source.canonical_text,
            metadata=source.metadata,
            normalization_trace_id=trace.trace_id,
        )
        return normalized, trace
