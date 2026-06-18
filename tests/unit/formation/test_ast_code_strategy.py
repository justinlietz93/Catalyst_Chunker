from catalyst.boundary.adapters.ast_python.python_ast_parser import PythonAstParser
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.strategies.ast_code_strategy import AstCodeStrategy
from catalyst.source.records.source_record import SourceRecord


def test_ast_code_strategy_prefers_ast_supported_boundaries() -> None:
    source = SourceRecord.from_bytes(
        b"import os\n\nclass A:\n    def method(self):\n        return os.getcwd()\n\ndef b():\n    return A()\n",
        source_kind="code",
    )
    parsed = PythonAstParser().parse(source, "python")

    candidate_set = AstCodeStrategy().form(source, parsed.evidence, SelectionPolicy())

    assert candidate_set.strategy == "ast_code"
    assert len(candidate_set.candidates) == 2
    assert all(candidate.spans for candidate in candidate_set.candidates)
    assert all(candidate.evidence_ids for candidate in candidate_set.candidates)


def test_ast_code_strategy_rejects_malformed_code_without_line_windows() -> None:
    source = SourceRecord.from_bytes(b"def broken(:\n    pass\n", source_kind="code")
    parsed = PythonAstParser().parse(source, "python")

    candidate_set = AstCodeStrategy().form(source, parsed.evidence, SelectionPolicy())

    assert candidate_set.candidates == ()
    assert candidate_set.warnings == ("malformed code observed; candidate set rejected",)
    assert candidate_set.reasons[0].kind == "code_malformed_rejection"


def test_ast_code_strategy_repairs_oversized_units_with_ast_child_spans() -> None:
    source = SourceRecord.from_bytes(
        b"class Big:\n"
        b"    def a(self):\n"
        b"        return one\n"
        b"    def b(self):\n"
        b"        return two\n",
        source_kind="code",
    )
    parsed = PythonAstParser().parse(source, "python")

    candidate_set = AstCodeStrategy().form(
        source,
        parsed.evidence,
        SelectionPolicy(hard_max_tokens=6),
    )

    assert candidate_set.repairs
    assert candidate_set.warnings == ("oversized code units repaired using AST child spans",)
    assert all(candidate.token_count <= 6 for candidate in candidate_set.candidates)
    assert all(candidate.metrics.repair_count == 1 for candidate in candidate_set.candidates)
    assert {reason.kind for reason in candidate_set.reasons} == {"ast_recursive_code_repair"}


def test_ast_code_strategy_leaves_unrepairable_oversized_unit_rejectable() -> None:
    expression = " + ".join(f"word{i}" for i in range(12))
    source = SourceRecord.from_bytes(f"def huge():\n    return {expression}\n".encode(), source_kind="code")
    parsed = PythonAstParser().parse(source, "python")

    candidate_set = AstCodeStrategy().form(
        source,
        parsed.evidence,
        SelectionPolicy(hard_max_tokens=6),
    )

    assert not candidate_set.repairs
    assert len(candidate_set.candidates) == 1
    assert candidate_set.candidates[0].token_count > 6
    assert candidate_set.candidates[0].warnings == (
        "code unit exceeds hard token budget; AST repair or rejection required",
    )
