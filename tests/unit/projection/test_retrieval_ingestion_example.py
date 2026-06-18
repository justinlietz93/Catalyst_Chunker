from __future__ import annotations

import importlib.util
from pathlib import Path

from catalyst.operation.commands import chunk_source, emit_projection


EXAMPLE_PATH = Path("docs/examples/retrieval_ingestion.py")


def test_retrieval_ingestion_example_maps_public_projection_fields() -> None:
    example = _load_example()
    result = chunk_source(b"# Title\n\nBody text for retrieval ingestion.")
    retrieval_records = emit_projection(result, "retrieval")

    ingestion = example.retrieval_records_to_ingestion_records(retrieval_records)

    assert ingestion
    first = ingestion[0]
    source_record = retrieval_records[0]
    assert first["ingestion_record_kind"] == "generic_retrieval_ingestion_example"
    assert first["projection_schema_version"] == source_record["schema_version"]
    assert first["source_projection_kind"] == "retrieval"
    assert first["chunk_id"] == source_record["chunk_id"]
    assert first["source_id"] == source_record["source_id"]
    assert first["indexed_text"] == source_record["text"]
    assert first["source_spans"] == source_record["source_spans"]
    assert first["relation_references"] == source_record["relations"]
    assert first["metadata"]["token_count"] == source_record["token_count"]


def test_retrieval_ingestion_example_fails_when_projection_fields_drift() -> None:
    example = _load_example()

    try:
        example.retrieval_record_to_ingestion_record(
            {
                "schema_version": "catalyst.retrieval.v1",
                "projection_kind": "retrieval",
            }
        )
    except KeyError as error:
        assert "chunk_id" in str(error)
    else:
        raise AssertionError("missing required projection fields should fail")


def test_retrieval_ingestion_example_stays_app_neutral() -> None:
    example = _load_example()
    result = chunk_source(b"# Title\n\nBody text.")
    ingestion = example.retrieval_records_to_ingestion_records(
        emit_projection(result, "retrieval")
    )
    keys = " ".join(ingestion[0].keys()).lower()
    text = f"{keys} {EXAMPLE_PATH.read_text(encoding='utf-8').lower()}"

    assert "crux" not in text
    assert "neuroca" not in text


def _load_example():
    spec = importlib.util.spec_from_file_location("retrieval_ingestion_example", EXAMPLE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load retrieval ingestion example")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
