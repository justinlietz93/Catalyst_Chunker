# Agentic Integration

Catalyst is designed to run inside agentic applications without depending on LLMs.

## Recommended Flow

1. Load source material.
2. Use Catalyst to admit chunks and emit retrieval/audit projections.
3. Give the agent retrieval records, source spans, warnings, and relation context.
4. Let the agent reason over those records.
5. If model output should be preserved, record it as boundary-assisted evidence.

## LLM Independence

The default Catalyst path does not call an LLM:

```text
source bytes
-> source record
-> observations
-> candidate formation
-> selection
-> invariants
-> admitted chunk graph
-> projections
```

LLM output is optional evidence. It is not source truth and cannot override hard invariants.

## Local Ollama Pattern

Your application may call Ollama or another local model outside Catalyst, then translate useful output into a Catalyst observation:

```python
from catalyst.observation.evidence import EvidenceSet, LlmCandidateObservation
from catalyst.observation.instruments.collect import observe_source
from catalyst.operation.commands import chunk_observed_source, emit_projection
from catalyst.source.records.source_record import SourceRecord

source = SourceRecord.from_bytes(b"Boundary-assisted candidate source.")
base = observe_source(source)
llm = LlmCandidateObservation(
    span=source.full_span(),
    proposal_text="candidate source",
    prompt_id="prompt_001",
    policy_id="local_ollama_boundary_assist",
    model_identity="ollama:<model-name>",
    confidence=0.72,
    rejected_alternatives=("too broad",),
).to_observation(source)

result = chunk_observed_source(
    source,
    EvidenceSet(base.source_id, (*base.observations, llm)),
)
audit = emit_projection(result, "audit")
```

The audit projection exposes `boundary_assisted` evidence with prompt ID, policy ID, model identity, confidence, and rejected alternatives.

## Do Not

- Do not replace source spans with model summaries.
- Do not accept model-proposed chunks by provider authority.
- Do not hide prompts, policies, confidence, or rejected alternatives.
- Do not weaken source lineage or projection versioning for agent convenience.

## Provider Token Budgets

Catalyst's default local counter is whitespace-delimited. If an agent uses a provider tokenizer with different behavior, keep that mapping in the application adapter.

For example, a long atomic string may be one Catalyst baseline token but many model tokens. Do not treat `hard_max_tokens` as a universal provider-token guarantee unless your adapter has translated the provider tokenizer's budget into Catalyst policy or evidence.

Use the `source_measure` observation to detect that risk. It records raw character, byte, line, lexical-token, and max-atomic-run counts for the source.
