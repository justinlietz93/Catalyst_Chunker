"""Collect observations from MVP instruments."""

from __future__ import annotations

from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.instruments.list_instrument import ListInstrument
from catalyst.observation.instruments.markdown_instrument import MarkdownInstrument
from catalyst.observation.instruments.paragraph_instrument import ParagraphInstrument
from catalyst.observation.instruments.sentence_instrument import SentenceInstrument
from catalyst.observation.instruments.table_instrument import TableInstrument
from catalyst.observation.instruments.tokenizer_instrument import TokenizerInstrument
from catalyst.source.records.source_record import SourceRecord


def observe_source(source: SourceRecord) -> EvidenceSet:
    instruments = (
        MarkdownInstrument(),
        ListInstrument(),
        ParagraphInstrument(),
        SentenceInstrument(),
        TableInstrument(),
        TokenizerInstrument(),
    )
    observations = []
    for instrument in instruments:
        observations.extend(instrument.observe(source))
    return EvidenceSet(source_id=source.source_id, observations=tuple(observations))
