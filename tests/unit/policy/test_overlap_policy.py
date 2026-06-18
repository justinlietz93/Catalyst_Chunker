from catalyst.policy.overlap_policy import allows_overlap


def test_overlap_requires_specific_dependency_evidence() -> None:
    assert allows_overlap("definition_dependency")
    assert not allows_overlap("fixed_overlap")
    assert not allows_overlap("default_overlap")
