"""Catalyst CLI."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from catalyst import __version__
from catalyst.boundary.adapters.ast_python.python_ast_parser import PythonAstParser
from catalyst.boundary.adapters.filesystem.source_loader import FileSystemSourceLoader
from catalyst.boundary.adapters.jsonl.artifact_writer import JsonlArtifactWriter
from catalyst.invariant.checks.projection_schema_check import check_projection_schema
from catalyst.operation.commands.chunk_source import chunk_source
from catalyst.operation.commands.emit_projection import emit_boundary_inspection, emit_projection
from catalyst.operation.commands.evaluate_candidates import evaluate_candidates
from catalyst.operation.commands.evaluate_performance_benchmark import evaluate_performance_benchmark
from catalyst.operation.commands.evaluate_retrieval_sanity import evaluate_retrieval_sanity
from catalyst.operation.commands.inspect_boundaries import inspect_boundaries
from catalyst.shared.errors import CatalystError


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "chunk":
            return _chunk(args)
        if args.command == "inspect-boundaries":
            return _inspect_boundaries(args)
        if args.command == "compare-strategies":
            return _compare_strategies(args)
        if args.command == "explain-chunk":
            return _explain_chunk(args)
        if args.command == "audit":
            return _audit(args)
        if args.command == "retrieval-sanity":
            return _retrieval_sanity(args)
        if args.command == "performance-benchmark":
            return _performance_benchmark(args)
    except CatalystError as error:
        print(f"catalyst: {error}", file=sys.stderr)
        return 2
    parser.print_help()
    return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="catalyst")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subcommands = parser.add_subparsers(dest="command")

    chunk = subcommands.add_parser("chunk", help="form chunks from a local source")
    chunk.add_argument("source")
    chunk.add_argument("--out", help="write retrieval JSONL to this path")
    chunk.add_argument("--audit", help="write audit JSON to this path")

    inspect = subcommands.add_parser("inspect-boundaries", help="inspect observed boundaries")
    inspect.add_argument("source")
    inspect.add_argument("--out", help="write boundary inspection JSON to this path")

    compare = subcommands.add_parser("compare-strategies", help="compare candidate strategies")
    compare.add_argument("source")
    compare.add_argument("--out", help="write candidate evaluation JSON to this path")

    explain = subcommands.add_parser("explain-chunk", help="print one retrieval chunk record")
    explain.add_argument("chunks_jsonl")
    explain.add_argument("chunk_id")

    audit = subcommands.add_parser("audit", help="inspect an audit projection")
    audit.add_argument("audit_json")

    sanity = subcommands.add_parser("retrieval-sanity", help="evaluate held-out retrieval sanity fixtures")
    sanity.add_argument("fixtures_json")
    sanity.add_argument("--out", help="write retrieval sanity JSON to this path")

    performance = subcommands.add_parser(
        "performance-benchmark",
        help="evaluate diagnostic performance benchmark fixtures",
    )
    performance.add_argument("fixtures_json")
    performance.add_argument("--out", help="write performance benchmark JSON to this path")

    return parser


def _chunk(args: argparse.Namespace) -> int:
    loader = FileSystemSourceLoader()
    writer = JsonlArtifactWriter()
    raw_bytes = loader.load(args.source)
    result = chunk_source(raw_bytes, location=args.source)
    retrieval_records = emit_projection(result, "retrieval")
    audit_record = emit_projection(result, "audit")
    assert isinstance(retrieval_records, list)
    assert isinstance(audit_record, dict)
    _ensure_projection_schema(retrieval_records)
    _ensure_projection_schema(audit_record)

    if args.out:
        writer.write_records(args.out, retrieval_records)
    else:
        for record in retrieval_records:
            print(json.dumps(record, sort_keys=True))

    if args.audit:
        writer.write_record(args.audit, audit_record)

    return 0


def _compare_strategies(args: argparse.Namespace) -> int:
    loader = FileSystemSourceLoader()
    writer = JsonlArtifactWriter()
    raw_bytes = loader.load(args.source)
    record = evaluate_candidates(raw_bytes, location=args.source).record()
    _ensure_projection_schema(record)
    if args.out:
        writer.write_record(args.out, record)
    else:
        print(json.dumps(record, indent=2, sort_keys=True))
    return 0


def _explain_chunk(args: argparse.Namespace) -> int:
    with open(args.chunks_jsonl, encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("chunk_id") == args.chunk_id:
                _ensure_projection_schema(record)
                print(json.dumps(record, indent=2, sort_keys=True))
                return 0
    print(f"catalyst: chunk not found: {args.chunk_id}", file=sys.stderr)
    return 2


def _audit(args: argparse.Namespace) -> int:
    with open(args.audit_json, encoding="utf-8") as handle:
        record = json.load(handle)
    _ensure_projection_schema(record)
    summary = {
        "schema_version": record["schema_version"],
        "projection_kind": record["projection_kind"],
        "source_id": record.get("source_id"),
        "lost_spans": record.get("coverage", {}).get("lost_spans"),
        "violation_count": len(record.get("violations", [])),
        "rejection_count": len(record.get("rejections", [])),
        "warning_count": len(record.get("warnings", [])),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _retrieval_sanity(args: argparse.Namespace) -> int:
    writer = JsonlArtifactWriter()
    with open(args.fixtures_json, encoding="utf-8") as handle:
        fixture_record = json.load(handle)
    fixtures = tuple(fixture_record.get("fixtures", ()))
    record = evaluate_retrieval_sanity(fixtures, ast_parser=PythonAstParser()).record()
    _ensure_projection_schema(record)
    if args.out:
        writer.write_record(args.out, record)
    else:
        print(json.dumps(record, indent=2, sort_keys=True))
    return 0


def _performance_benchmark(args: argparse.Namespace) -> int:
    writer = JsonlArtifactWriter()
    with open(args.fixtures_json, encoding="utf-8") as handle:
        fixture_record = json.load(handle)
    fixtures = tuple(fixture_record.get("fixtures", ()))
    record = evaluate_performance_benchmark(fixtures).record()
    _ensure_projection_schema(record)
    if args.out:
        writer.write_record(args.out, record)
    else:
        print(json.dumps(record, indent=2, sort_keys=True))
    return 0


def _inspect_boundaries(args: argparse.Namespace) -> int:
    loader = FileSystemSourceLoader()
    writer = JsonlArtifactWriter()
    raw_bytes = loader.load(args.source)
    source_id, boundaries = inspect_boundaries(raw_bytes, location=args.source)
    record = emit_boundary_inspection(
        source_id=source_id,
        boundary_candidates=boundaries,
    )
    _ensure_projection_schema(record)

    if args.out:
        writer.write_record(args.out, record)
    else:
        print(json.dumps(record, indent=2, sort_keys=True))

    return 0


def _ensure_projection_schema(records: dict[str, object] | list[dict[str, object]]) -> None:
    result = check_projection_schema(records)
    if not result.passed:
        raise CatalystError(result.message)


if __name__ == "__main__":
    raise SystemExit(main())
