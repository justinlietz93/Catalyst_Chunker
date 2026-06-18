from catalyst.invariant.rules.invariant import Invariant
from catalyst.invariant.rules.invariant_registry import InvariantRegistry
from catalyst.invariant.rules.invariant_result import InvariantResult


def test_invariant_registry_records_results_in_order() -> None:
    registry = InvariantRegistry(
        invariants=(
            Invariant(
                invariant_id="I-test",
                name="test invariant",
                check=lambda: InvariantResult(
                    invariant_id="I-test",
                    passed=True,
                    message="passed",
                ),
            ),
        )
    )

    results = registry.evaluate()

    assert len(results) == 1
    assert results[0].passed
    assert results[0].message == "passed"
