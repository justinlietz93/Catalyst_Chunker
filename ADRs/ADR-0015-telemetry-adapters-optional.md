# ADR-0015: Telemetry Adapters Are Optional Boundary Adapters

## Status

Accepted

## Context

Catalyst has a `TelemetrySink` boundary port. Operational users may want metrics or traces for chunk counts, token counts, latency, repair behavior, invariant failures, and adapter failures.

Telemetry is useful observation, but it must not become a runtime dependency or an admission authority.

## Decision

Telemetry adapters are optional boundary adapters.

Core Catalyst may define event names and payload shapes. Concrete Prometheus, OpenTelemetry, file, or in-memory telemetry implementations must remain optional adapters or examples. Telemetry failure must not change chunk admission.

Telemetry must avoid emitting full source text by default.

## Evidence

- Boundary architecture already separates ports from adapters.
- Users embedding Catalyst in agentic applications need operational visibility.
- Source text may be sensitive, so telemetry payloads require conservative defaults.

## Alternatives Considered

- Add Prometheus or OpenTelemetry as required dependencies: rejected because core Catalyst should remain dependency-light.
- Emit no telemetry guidance: rejected because ad hoc events would drift across applications.
- Let telemetry errors fail chunking by default: rejected because observation failure is not source failure.

## Consequences

Telemetry payload schemas need documentation and tests.

Optional adapters can live behind extras if admitted.

Metric names must describe observations, not redefine invariants.

## Implementation Acceptance Criteria

- Documentation lists stable telemetry event names and payload fields.
- A no-op or in-memory telemetry adapter exists for local testing.
- Any Prometheus or OpenTelemetry adapter is optional and behind an extra.
- Telemetry failures are nonfatal unless a caller explicitly chooses strict behavior.
- Default telemetry payloads do not include full source text.

## Review Trigger

Revisit this ADR if operational deployments require strict telemetry delivery guarantees or if telemetry payloads need a versioned public projection.

