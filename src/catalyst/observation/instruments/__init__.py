"""Observation instruments."""

from catalyst.observation.instruments.markdown_instrument import MarkdownInstrument
from catalyst.observation.instruments.paragraph_instrument import ParagraphInstrument
from catalyst.observation.instruments.sentence_instrument import SentenceInstrument
from catalyst.observation.instruments.tokenizer_instrument import TokenizerInstrument

__all__ = [
    "MarkdownInstrument",
    "ParagraphInstrument",
    "SentenceInstrument",
    "TokenizerInstrument",
]
