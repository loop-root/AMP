# AMP local-uds-v1 Conformance Checklist

Status: checklist  
Authority: conformance aid  
Scope: AMP RFC 0001 through RFC 0007

Use this as a blunt implementation checklist for the `local-uds-v1`
transport profile.

## Transport and Negotiation

- [ ] The implementation uses Unix domain sockets for the privileged
  control-plane transport.
- [ ] The implementation advertises exact AMP versions and exact
  transport profiles during session establishment.
- [ ] The implementation binds one negotiated `amp_version` and one
  negotiated `transport_profile` to the session.
- [ ] The implementation rejects unsupported or session-mismatched
  versions and profiles with typed denials.

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

## Failure Semantics

- [ ] The implementation prefers explicit denial over silent fallback.
- [ ] The implementation preserves append-only audit behavior.
- [ ] The implementation does not widen transport, memory, or approval
  authority for convenience.
