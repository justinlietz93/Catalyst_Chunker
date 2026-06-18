import json

from catalyst.boundary.presentation.cli.main import main


def test_cli_chunk_writes_versioned_outputs(tmp_path) -> None:
    source = tmp_path / "sample.md"
    chunks = tmp_path / "chunks.jsonl"
    audit = tmp_path / "audit.json"
    source.write_text("# Title\n\nBody text for Catalyst.", encoding="utf-8")

    exit_code = main(["chunk", str(source), "--out", str(chunks), "--audit", str(audit)])

    assert exit_code == 0
    first_chunk = json.loads(chunks.read_text(encoding="utf-8").splitlines()[0])
    audit_record = json.loads(audit.read_text(encoding="utf-8"))
    assert first_chunk["schema_version"] == "catalyst.retrieval.v1"
    assert first_chunk["source_spans"]
    assert audit_record["schema_version"] == "catalyst.audit.v1"


def test_cli_inspect_boundaries_writes_versioned_output(tmp_path) -> None:
    source = tmp_path / "sample.md"
    out = tmp_path / "boundaries.json"
    source.write_text("# Title\n\nBody text.", encoding="utf-8")

    exit_code = main(["inspect-boundaries", str(source), "--out", str(out)])

    assert exit_code == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["schema_version"] == "catalyst.boundaries.v1"
    assert record["boundary_candidates"]
