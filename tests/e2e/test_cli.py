import json

from catalyst.boundary.presentation.cli.main import main


def test_cli_version_reports_package_version(capsys) -> None:
    try:
        main(["--version"])
    except SystemExit as error:
        assert error.code == 0
    else:
        raise AssertionError("argparse version action should exit")

    assert capsys.readouterr().out.strip() == "catalyst 0.1.5"


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


def test_cli_chunk_reports_empty_source_without_traceback(tmp_path, capsys) -> None:
    source = tmp_path / "empty.md"
    source.write_text("\n\n", encoding="utf-8")

    exit_code = main(["chunk", str(source)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "source contains no chunkable text" in captured.err
    assert "Traceback" not in captured.err


def test_cli_inspect_boundaries_writes_versioned_output(tmp_path) -> None:
    source = tmp_path / "sample.md"
    out = tmp_path / "boundaries.json"
    source.write_text("# Title\n\nBody text.", encoding="utf-8")

    exit_code = main(["inspect-boundaries", str(source), "--out", str(out)])

    assert exit_code == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["schema_version"] == "catalyst.boundaries.v1"
    assert record["boundary_candidates"]


def test_cli_compare_explain_and_audit_commands(tmp_path, capsys) -> None:
    source = tmp_path / "sample.md"
    chunks = tmp_path / "chunks.jsonl"
    audit = tmp_path / "audit.json"
    compare = tmp_path / "compare.json"
    source.write_text("# Title\n\nBody text for Catalyst.", encoding="utf-8")

    assert main(["chunk", str(source), "--out", str(chunks), "--audit", str(audit)]) == 0
    assert main(["compare-strategies", str(source), "--out", str(compare)]) == 0
    comparison = json.loads(compare.read_text(encoding="utf-8"))
    assert comparison["schema_version"] == "catalyst.candidate_evaluation.v1"

    chunk_id = json.loads(chunks.read_text(encoding="utf-8").splitlines()[0])["chunk_id"]
    assert main(["explain-chunk", str(chunks), chunk_id]) == 0
    explained = json.loads(capsys.readouterr().out)
    assert explained["chunk_id"] == chunk_id

    assert main(["audit", str(audit)]) == 0
    audit_summary = json.loads(capsys.readouterr().out)
    assert audit_summary["projection_kind"] == "audit"


def test_cli_retrieval_sanity_writes_versioned_report(tmp_path) -> None:
    fixtures = tmp_path / "fixtures.json"
    out = tmp_path / "retrieval-sanity.json"
    fixtures.write_text(
        json.dumps(
            {
                "schema_version": "catalyst.retrieval_sanity_fixtures.v1",
                "fixtures": [
                    {
                        "fixture_id": "python_call_dependency",
                        "source_family": "code",
                        "source_kind": "code",
                        "query": "Which caller invokes helper?",
                        "expected_terms": ["caller", "helper"],
                        "strategies": ["ast_code"],
                        "text": "def helper():\n    return 1\n\ndef caller():\n    return helper()\n",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    assert main(["retrieval-sanity", str(fixtures), "--out", str(out)]) == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["schema_version"] == "catalyst.retrieval_sanity.v1"
    assert record["projection_kind"] == "retrieval_sanity"
    assert record["authority"]["diagnostic_only"] is True
