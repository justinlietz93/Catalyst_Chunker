from catalyst.invariant.checks.projection_schema_check import check_projection_schema


def test_projection_schema_check_requires_public_schema_fields() -> None:
    failed = check_projection_schema({"projection_kind": "retrieval"})
    passed = check_projection_schema(
        {
            "schema_version": "catalyst.retrieval.v1",
            "projection_kind": "retrieval",
        }
    )

    assert not failed.passed
    assert passed.passed
