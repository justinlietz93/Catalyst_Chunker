from catalyst.formation.selection.selection_policy import SelectionPolicy


def test_semantic_refinement_is_optional_by_default() -> None:
    policy = SelectionPolicy()

    assert policy.allow_semantic_refinement is False
    assert policy.to_dict()["allow_semantic_refinement"] is False
