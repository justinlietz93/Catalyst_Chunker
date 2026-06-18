"""Hierarchical candidate formation."""

from __future__ import annotations

from catalyst.formation.candidates.candidate_metrics import CandidateMetrics
from catalyst.formation.candidates.candidate_reason import CandidateReason
from catalyst.formation.candidates.chunk_candidate import ChunkCandidate
from catalyst.formation.candidates.chunk_candidate_set import ChunkCandidateSet
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.strategies.paragraph_group_strategy import ParagraphGroupStrategy
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.instruments.tokenizer_instrument import count_tokens
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord


class HierarchicalStrategy:
    """Form a parent source candidate plus paragraph-derived children."""

    strategy = "hierarchical"

    def form(
        self,
        source: SourceRecord,
        evidence: EvidenceSet,
        policy: SelectionPolicy,
    ) -> ChunkCandidateSet:
        child_set = ParagraphGroupStrategy().form(source, evidence, policy)
        parent_reason = CandidateReason(
            reason_id=stable_id("reason", source.source_id, self.strategy, "parent"),
            kind="hierarchical_parent",
            evidence_ids=tuple(
                evidence_id
                for child in child_set.candidates
                for evidence_id in child.evidence_ids
            ),
            description="source-level parent candidate for parent/child retrieval context",
        )
        parent_text = source.canonical_text.strip()
        parent = ChunkCandidate(
            candidate_id=stable_id("cand", source.source_id, self.strategy, "parent"),
            source_id=source.source_id,
            spans=(source.full_span(),),
            text=parent_text,
            token_count=count_tokens(parent_text),
            evidence_ids=parent_reason.evidence_ids,
            reason_ids=(parent_reason.reason_id,),
            metrics=CandidateMetrics(
                token_count=count_tokens(parent_text),
                boundary_count=len(child_set.candidates),
            ),
            warnings=("parent candidate is context, not default retrieval unit",),
        )
        return ChunkCandidateSet(
            candidate_set_id=stable_id(
                "candset",
                source.source_id,
                self.strategy,
                tuple(child.candidate_id for child in child_set.candidates),
            ),
            strategy=self.strategy,
            source_id=source.source_id,
            candidates=(parent, *child_set.candidates),
            reasons=(parent_reason, *child_set.reasons),
            warnings=("hierarchical candidate set is projection-oriented",),
        )
