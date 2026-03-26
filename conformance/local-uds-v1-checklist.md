# AMP local-uds-v1 Conformance Checklist

Status: checklist  
Authority: conformance aid  
Scope: AMP RFC 0001 through RFC 0007 (see also RFC 0008 for known gaps)

**Release gate:** For any Loopgate/Haven release that claims **AMP `local-uds-v1` alignment**, either complete every applicable item below or record an explicit waiver (issue + RFC update). Partial alignment is fine only if marketing and docs say so honestly.

Use this as a blunt implementation checklist for the `local-uds-v1`
transport profile.

For byte-level cross-checks, see [test-vectors-v1.md](./test-vectors-v1.md)
alongside RFC 0004 §15.

## Transport and Negotiation

- [ ] The implementation uses Unix domain sockets for the privileged
  control-plane transport.
- [ ] The implementation advertises exact AMP versions and exact
  transport profiles during session establishment.
- [ ] The implementation binds one negotiated `amp_version` and one
  negotiated `transport_profile` to the session.
- [ ] The implementation rejects unsupported or session-mismatched
  versions and profiles with typed denials.

## Session Establishment (RFC 0001 Section 7)

- [ ] The client sends `amp_versions` and `transport_profiles` in the
  session-open request.
- [ ] The server selects the highest overlapping AMP version and the
  first client-preferred transport profile it supports.
- [ ] The server returns `session_id`, `mac_key`, selected
  `amp_version`, and selected `transport_profile`.
- [ ] The server returns a typed denial on session establishment
  failure (not a partial or empty session).
- [ ] The `mac_key` is at least 32 raw bytes of cryptographic random.
- [ ] Actor identifiers pass the identifier policy rules (RFC 0001
  Section 12).

## Canonical Request Integrity

- [ ] Every privileged post-session request uses the canonical envelope
  from RFC 0004.
- [ ] The implementation validates canonical fields exactly, not
  permissively.
- [ ] The implementation computes `body_sha256` over the exact
  application body bytes.
- [ ] The implementation computes the request MAC as `HMAC-SHA-256` over
  the canonical request bytes.
- [ ] The implementation compares MACs in constant time.
- [ ] The implementation rejects stale timestamps beyond 60 seconds
  unless a stricter negotiated profile rule is in force.
- [ ] The implementation rejects nonce replay within the bound session.
- [ ] The implementation invalidates active sessions if replay-cache
  continuity cannot be preserved.
- [ ] The implementation fails closed on any integrity mismatch.

## Tokens, Denials, and Events

- [ ] The implementation binds scoped-token context using
  `token_binding` when the action requires a scoped token.
- [ ] The implementation does not treat bearer possession alone as
  sufficient authority.
- [ ] The implementation returns typed denial objects rather than vague
  failures where transport state permits one.
- [ ] The implementation records append-only events for
  security-relevant state transitions.

## References and Artifacts

- [ ] The implementation treats `artifact_ref` and `memory_ref` as
  identifiers, not authority grants.
- [ ] The implementation does not infer prompt eligibility or content
  access from a reference alone.
- [ ] The implementation preserves provenance and storage-state
  separation for artifacts.

## Approvals

- [ ] Approval requests use the canonical approval manifest from RFC
  0005.
- [ ] Approval decisions bind to `approval_id` and
  `approval_manifest_sha256`.
- [ ] Approval decisions use a semantic `decision_nonce` in addition to
  the transport request nonce.
- [ ] The implementation enforces the approval state machine from RFC
  0005.
- [ ] The implementation treats approvals as `single-use`.
- [ ] The implementation binds approval consumption to the exact
  approved method, path, and execution-body digest.
- [ ] The implementation serializes approval state mutation so the first
  valid transition wins.
- [ ] Stale or non-pending decision attempts return `approval_not_pending`
  or a more specific typed code (RFC 0005 §10.4).
- [ ] The implementation records required approval audit events.

## Memory and Continuity

- [ ] The implementation treats `wake_state`, `distillate`, and
  `resonate_key` as `memory_artifact` subtypes.
- [ ] The implementation treats exact-key recall as governed
  dereference, not ambient authority.
- [ ] The implementation does not allow client-local continuity state to
  become authoritative without rebound through AMP-governed memory
  paths.
- [ ] The implementation does not let loading a wake state resurrect
  expired or revoked authority.

## Capability Execution (RFC 0009)

- [ ] Capability execution requests use the canonical envelope from
  RFC 0004.
- [ ] The execution request body contains `capability`, `arguments`,
  and `request_id`.
- [ ] Arguments are validated against the registered capability schema
  before execution.
- [ ] The `request_id` is unique per control session for requests that
  enter execution or approval flow.
- [ ] Success responses include `status`, `request_id`, `capability`,
  `result`, `result_classification`, and `occurred_at_ms`.
- [ ] Denial responses use the denial envelope from RFC 0004 extended
  with `request_id` and `capability`.
- [ ] Approval-pending responses include `status`, `request_id`,
  `approval_id`, and `approval_manifest_sha256`.
- [ ] Results are filtered and do not contain raw provider credentials.
- [ ] Audit events are recorded for all execution attempts.

## Client Recovery (RFC 0001 Section 14)

- [ ] The client discards all session state on `session_invalidated`
  or connection loss.
- [ ] The client implements exponential back-off on repeated session
  establishment failure.
- [ ] The client refreshes cached projection state after session
  re-establishment.

## Failure Semantics

- [ ] The implementation prefers explicit denial over silent fallback.
- [ ] If persisting hashes of compact `denial` or `event` objects, the
  implementation uses RFC 0007 §5.1 canonical JSON (see
  [test-vectors-v1.md](./test-vectors-v1.md)).
- [ ] The implementation preserves append-only audit behavior.
- [ ] The implementation does not widen transport, memory, or approval
  authority for convenience.
