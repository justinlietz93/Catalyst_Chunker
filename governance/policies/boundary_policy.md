# Boundary Policy

External document tools are boundary adapters. They may load, parse, convert, or expose structure, but they do not define Catalyst internal truth.

Document adapters must satisfy these criteria:

- implement `DocumentParserPort`
- return `ParsedDocument`
- translate provider output into `SourceRecord` and `EvidenceSet`
- keep provider models in `catalyst.boundary.adapters`
- pass the shared document parser port contract tests
- preserve source lineage where the provider exposes it
- expose provider chunks only as observations or candidates, never as accepted chunks by provider authority alone

Prepared adapter candidates:

- Docling
- Unstructured
- Haystack
- LlamaIndex
