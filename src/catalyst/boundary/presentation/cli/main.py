"""Catalyst CLI."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from catalyst.boundary.adapters.filesystem.source_loader import FileSystemSourceLoader
from catalyst.boundary.adapters.jsonl.artifact_writer import JsonlArtifactWriter
from catalyst.invariant.checks.projection_schema_check import check_projection_schema
from catalyst.operation.commands.chunk_source import chunk_source
from catalyst.operation.commands.inspect_boundaries import inspect_boundaries
from catalyst.projection.views.audit_view import AuditProjection
from catalyst.projection.views.boundary_inspection_view import BoundaryInspectionProjection
from catalyst.projection.views.retrieval_view import RetrievalProjection
from catalyst.shared.errors import CatalystError


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "chunk":
            return _chunk(args)
        if args.command == "inspect-boundaries":
            return _inspect_boundaries(args)
    except CatalystError as error:
        print(f"catalyst: {error}", file=sys.stderr)
        return 2
    parser.print_help()
    return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="catalyst")
    subcommands = parser.add_subparsers(dest="command")

    chunk = subcommands.add_parser("chunk", help="form chunks from a local source")
    chunk.add_argument("source")
    chunk.add_argument("--out", help="write retrieval JSONL to this path")
    chunk.add_argument("--audit", help="write audit JSON to this path")

    inspect = subcommands.add_parser("inspect-boundaries", help="inspect observed boundaries")
    inspect.add_argument("source")
    inspect.add_argument("--out", help="write boundary inspection JSON to this path")

    return parser


def _chunk(args: argparse.Namespace) -> int:
    loader = FileSystemSourceLoader()
    writer = JsonlArtifactWriter()
    raw_bytes = loader.load(args.source)
    result = chunk_source(raw_bytes, location=args.source)
    retrieval_records = RetrievalProjection(result.graph).records()
    audit_record = AuditProjection(
        graph=result.graph,
        invariant_ledger=result.invariant_ledger,
        accepted_candidate_set_id=result.selection.accepted.candidate_set_id,
        rejections=result.selection.rejections,
    ).record()
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


def _inspect_boundaries(args: argparse.Namespace) -> int:
    loader = FileSystemSourceLoader()
    writer = JsonlArtifactWriter()
    raw_bytes = loader.load(args.source)
    source_id, boundaries = inspect_boundaries(raw_bytes, location=args.source)
    record = BoundaryInspectionProjection(
        source_id=source_id,
        boundary_candidates=boundaries,
    ).record()
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
