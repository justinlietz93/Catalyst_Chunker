# ADR-0005: Code Chunking Requires AST-Aware Observation By Default

## Status

Accepted

## Context

Code has native syntactic structure. Functions, classes, imports, blocks, docstrings, and declarations are not interchangeable with line windows. A chunk boundary that breaks syntax can corrupt retrieval, explanation, and downstream code use while still looking acceptable by token count.

Catalyst's standards define code syntax boundary integrity as a required invariant and place AST-aware chunking before recursive split/merge for code.

## Decision

Code chunking requires AST-aware observation by default.

Catalyst may use Tree-sitter, ast-grep, or comparable parsers as boundary instruments, but their outputs are evidence, not internal truth. Accepted code chunks must prefer AST-supported boundaries and must record repair or rejection when a split would break syntax or detach dependent code context.

## Evidence

- `ARCHITECTURE_STANDARDS.md` defines `CodeFunctionObservation`, `CodeClassObservation`, `Code Boundary Integrity`, `AstCodeCandidateSet`, and `CodeProjection`.
- The default strategy matrix says code uses AST-aware chunking with recursive split/merge refinement.
- The research report states that code should use AST-aware chunking rather than line windows and names Tree-sitter and ast-grep as practical CLI-native tools.

## Alternatives Considered

- Line-window code chunking: rejected because line count does not prove syntactic or semantic boundary validity.
- Token-window code chunking: rejected because token limits can split syntax unless governed by AST evidence and repair.
- Parser-owned internal models: rejected because parser outputs are boundary observations and cannot define Catalyst identity.

## Consequences

The code source family requires AST observation fixtures and contradiction tests.

Recursive split/merge for oversized code units must preserve syntax or produce explicit repair and warning records.

Code projections must expose code-relevant lineage and relations such as definitions, calls, imports, and adjacency where admitted.

## Review Trigger

Revisit this ADR if Catalyst supports a language or source form for which no reliable AST instrument exists and a fallback policy is needed with explicit syntax-risk disclosure.
