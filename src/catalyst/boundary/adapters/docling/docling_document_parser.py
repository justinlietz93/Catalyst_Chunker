"""Docling document parser boundary adapter."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from catalyst.boundary.ports.parsed_document import ParsedDocument
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.evidence.observation import Observation
from catalyst.observation.instruments.collect import observe_source
from catalyst.observation.instruments.span_tools import span_from_chars
from catalyst.shared.errors import CatalystError
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord


class DoclingDocumentParser:
    """Translate Docling output into Catalyst-native records."""

    def __init__(self, converter: Any | None = None) -> None:
        self._converter = converter

    def parse(self, raw_bytes: bytes, *, location: str | None = None) -> ParsedDocument:
        converter = self._converter or _load_converter()
        result = _convert_bytes(converter, raw_bytes, location=location)
        canonical_text = _export_text(result, raw_bytes)
        source = SourceRecord.from_canonical_text(
            raw_bytes,
            canonical_text,
            source_kind="document",
            location=location,
            metadata={"document_parser": "docling"},
        )
        evidence = _translate_evidence(source)
        return ParsedDocument(
            source=source,
            evidence=evidence,
            warnings=(),
        )


def _load_converter() -> Any:
    try:
        from docling.document_converter import DocumentConverter
    except ImportError as exc:
        raise CatalystError(
            "Docling adapter requires the optional dependency: catalyst-chunker[docling]"
        ) from exc
    return DocumentConverter()


def _convert_bytes(converter: Any, raw_bytes: bytes, *, location: str | None) -> Any:
    suffix = Path(location).suffix if location else ".bin"
    with NamedTemporaryFile(suffix=suffix or ".bin") as handle:
        handle.write(raw_bytes)
        handle.flush()
        return converter.convert(handle.name)


def _export_text(result: Any, raw_bytes: bytes) -> str:
    document = getattr(result, "document", result)
    for method_name in ("export_to_markdown", "export_to_text"):
        method = getattr(document, method_name, None)
        if callable(method):
            text = method()
            if text:
                return str(text)
    text = getattr(document, "text", None)
    if text:
        return str(text)
    return raw_bytes.decode("utf-8", errors="replace")


def _translate_evidence(source: SourceRecord) -> EvidenceSet:
    base = observe_source(source)
    observations = list(base.observations)
    observations = _replace_repeated_heading_observations(source, observations)
    observations.extend(_ocr_hyphenation_observations(source))
    return EvidenceSet(source_id=source.source_id, observations=tuple(observations))


def _replace_repeated_heading_observations(
    source: SourceRecord,
    observations: list[Observation],
) -> list[Observation]:
    headings = [obs for obs in observations if obs.kind == "markdown_heading"]
    title_counts: dict[str, int] = {}
    for heading in headings:
        title = str(heading.payload.get("title", "")).strip()
        if title:
            title_counts[title] = title_counts.get(title, 0) + 1

    repeated_titles = {title for title, count in title_counts.items() if count > 1}
    output: list[Observation] = []
    for observation in observations:
        if observation.kind != "markdown_heading":
            output.append(observation)
            continue
        title = str(observation.payload.get("title", "")).strip()
        if title not in repeated_titles:
            output.append(observation)
            continue
        output.append(
            Observation(
                observation_id=stable_id(
                    "obs",
                    source.source_id,
                    "pdf_page_header",
                    observation.span.start_char,
                    observation.span.end_char,
                ),
                kind="pdf_page_header",
                span=observation.span,
                confidence=0.85,
                weight=0.7,
                instrument="docling",
                payload={
                    "text": title,
                    "source_observation_id": observation.observation_id,
                },
            )
        )
    return output


def _ocr_hyphenation_observations(source: SourceRecord) -> tuple[Observation, ...]:
    observations: list[Observation] = []
    text = source.canonical_text
    cursor = 0
    while True:
        index = text.find("-\n", cursor)
        if index < 0:
            break
        start = max(0, index - 24)
        end = min(len(text), index + 26)
        observations.append(
            Observation(
                observation_id=stable_id("obs", source.source_id, "ocr_hyphenation", index),
                kind="ocr_hyphenation",
                span=span_from_chars(source, start, end),
                confidence=0.65,
                weight=0.4,
                instrument="docling",
                payload={"position": index},
            )
        )
        cursor = index + 2
    return tuple(observations)
