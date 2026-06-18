"""Evidence policy for overlap-like retrieval context."""

ALLOWED_OVERLAP_EVIDENCE = (
    "pronoun_dependency",
    "definition_dependency",
    "citation_dependency",
    "table_continuation",
    "speaker_turn_continuation",
    "code_import_dependency",
    "claim_example_dependency",
)


def allows_overlap(evidence_kind: str) -> bool:
    """Return whether evidence may permit overlap-like duplication."""

    return evidence_kind in ALLOWED_OVERLAP_EVIDENCE
