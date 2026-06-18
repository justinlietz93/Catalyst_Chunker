"""App-neutral retrieval ingestion mapping example.

This file is documentation support code. It maps Catalyst retrieval projection
records into a generic ingestion shape without adding a vector database or
application DTO to Catalyst core.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


REQUIRED_RETRIEVAL_FIELDS = (
    "schema_version",
    "projection_kind",
    "chunk_id",
    "source_id",
    "text",
    "source_spans",
    "relations",
)


def retrieval_records_to_ingestion_records(
    records: Iterable[Mapping[str, Any]],
) -> list[dict[str, object]]:
    """Map retrieval projection records to generic ingestion records."""

    return [retrieval_record_to_ingestion_record(record) for record in records]


def retrieval_record_to_ingestion_record(record: Mapping[str, Any]) -> dict[str, object]:
    """Map one retrieval projection record to an app-neutral ingestion record."""

    _require_fields(record)
    relations = record["relations"]
    return {
        "ingestion_record_kind": "generic_retrieval_ingestion_example",
        "projection_schema_version": record["schema_version"],
        "source_projection_kind": record["projection_kind"],
        "chunk_id": record["chunk_id"],
        "source_id": record["source_id"],
        "indexed_text": record["text"],
        "source_spans": list(record["source_spans"]),
        "relation_references": dict(relations) if isinstance(relations, Mapping) else relations,
        "metadata": {
            "token_count": record.get("token_count"),
            "warnings": list(record.get("warnings", ())),
            "omissions": list(record.get("omissions", ())),
        },
    }


def _require_fields(record: Mapping[str, Any]) -> None:
    missing = [field for field in REQUIRED_RETRIEVAL_FIELDS if field not in record]
    if missing:
        raise KeyError(f"retrieval record missing required fields: {', '.join(missing)}")
