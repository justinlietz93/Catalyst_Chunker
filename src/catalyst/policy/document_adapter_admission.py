"""Admission criteria for document boundary adapters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentAdapterAdmissionCriteria:
    """Rules an external document adapter must satisfy before admission."""

    adapter_name: str
    port_contract: str = "DocumentParserPort"
    provider_model_scope: str = "boundary_only"
    provider_chunk_authority: str = "observations_or_candidates_only"
    requires_contract_tests: bool = True
    requires_lineage_translation: bool = True
    requires_boundary_purity_check: bool = True


DOCUMENT_ADAPTER_ADMISSION = (
    DocumentAdapterAdmissionCriteria(adapter_name="docling"),
    DocumentAdapterAdmissionCriteria(adapter_name="unstructured"),
    DocumentAdapterAdmissionCriteria(adapter_name="haystack"),
    DocumentAdapterAdmissionCriteria(adapter_name="llamaindex"),
)
