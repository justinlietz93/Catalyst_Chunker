from catalyst.policy.document_adapter_admission import DOCUMENT_ADAPTER_ADMISSION


def test_document_adapter_candidates_share_boundary_admission_rules() -> None:
    names = {criteria.adapter_name for criteria in DOCUMENT_ADAPTER_ADMISSION}

    assert {"docling", "unstructured", "haystack", "llamaindex"} <= names
    assert all(criteria.port_contract == "DocumentParserPort" for criteria in DOCUMENT_ADAPTER_ADMISSION)
    assert all(criteria.provider_model_scope == "boundary_only" for criteria in DOCUMENT_ADAPTER_ADMISSION)
    assert all(
        criteria.provider_chunk_authority == "observations_or_candidates_only"
        for criteria in DOCUMENT_ADAPTER_ADMISSION
    )
    assert all(criteria.requires_contract_tests for criteria in DOCUMENT_ADAPTER_ADMISSION)
