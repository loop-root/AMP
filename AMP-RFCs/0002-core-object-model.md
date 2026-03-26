# AMP RFC 0002: Core Object Model

Status: draft  
Track: AMP (Authority Mediation Protocol)  
Authority: protocol design / target architecture  
Current implementation alignment: partial

## 1. Purpose

This document defines the core object vocabulary for the Authority
Mediation Protocol (AMP).

The purpose of the core object model is to give protocol participants a
stable, typed, implementation-neutral language for authority,
artifacts, denials, and state transitions.

## 2. Scope

This RFC defines the principal AMP object classes and the invariants
they must preserve.

This RFC does not define:

- transport details beyond object references
- serialization format
- UI presentation
- product-specific user experience

## 3. Design Principles

The AMP object model is built around the following principles:

- authority is typed and explicit
- natural language never creates authority
- references are not equivalent to underlying content
- artifacts are provenance-bearing
- denials are explicit and typed
- object meaning must not depend on product branding

## 4. Object Classes

### 4.1 Session

A `session` represents a bounded interaction context between an
unprivileged client and the privileged control plane.

A session:

- is server-issued
- is bounded in time
- is validated server-side
- is not a provider credential

### 4.2 Capability

A `capability` represents a typed action the control plane may mediate.

A capability is defined by:

- stable identifier
- input schema
- output schema
- policy requirements
- approval requirements
- execution semantics

A capability is not created by natural-language description.

### 4.3 Capability Token

A `capability_token` is an opaque scoped reference authorizing a
specific class of mediated action.

A capability token:

- is opaque
- is short-lived
- is scoped
- is server-validated
- is not self-describing authority

### 4.4 Approval Request

An `approval_request` represents a pending user- or operator-facing
authorization checkpoint created by the control plane.

An approval request includes:

- object under review
- approval manifest hash
- target action class
- created/expiry time
- lifecycle state

Detailed approval lifecycle semantics are defined by RFC 0005.

### 4.5 Approval Decision

An `approval_decision` is an explicit response to a pending
`approval_request`.

An approval decision is:

- bound to a specific approval request
- bound to the approval manifest hash under review
- bound to a specific control session or equivalent authority path
- bound by a decision nonce for semantic replay protection
- explicit
- auditable

### 4.6 Artifact

An `artifact` is a durable, referenced object with provenance.

Artifact classes include:

- quarantine artifact
- derived artifact
- memory artifact

Wake state is a memory artifact subtype, not a separate top-level
artifact class.

An artifact is not equivalent to its identifier or reference.

### 4.7 Quarantine Artifact

A `quarantine_artifact` is an artifact whose source content remains
untrusted and explicitly quarantined.

Quarantine is a trust state, not a convenience state.

### 4.8 Derived Artifact

A `derived_artifact` is a new artifact created from one or more source
artifacts through explicit governed transformation or promotion.

A derived artifact:

- does not bless the source in place
- must record provenance
- must materialize its own classification

### 4.9 Memory Artifact

A `memory_artifact` is a durable artifact used for continuity,
compaction, or bounded recall.

Examples include:

- distillates
- resonate keys
- wake states

### 4.10 Reference

A `reference` identifies another object without automatically granting
dereference rights or trust.

Reference classes include:

- artifact reference
- quarantine reference
- blob reference
- memory reference

### 4.11 Denial

A `denial` is an explicit typed refusal.

Denials must distinguish:

- authorization failure
- policy denial
- integrity failure
- unsupported operation
- storage-state mismatch
- validation error

### 4.12 Event

An `event` is an append-only record of an observable state transition or
security-relevant action.

Events must be:

- monotonic
- attributable
- durable where policy requires
- separable from user-facing rendering

## 5. Object Relationships

The core object model expects the following relationships:

- sessions request capability execution
- capability tokens scope those requests
- approval requests gate selected actions
- artifacts preserve source and derivation lineage
- references point to artifacts without becoming them
- events record state transitions for all of the above

## 6. Reserved Sentinel Values

The literal string `none` is a reserved protocol sentinel across all AMP
object fields.

When a required field has no concrete value, the value MUST be the
literal string `none`.

Rules:

- `none` MUST NOT be used as a valid identifier, reference, hash, or
  classification value in any AMP object
- implementations MUST NOT create objects whose identifiers, references,
  or other typed fields collide with the literal `none`
- `none` is case-sensitive: only the exact lower-case ASCII string
  `none` is reserved
- fields that carry `none` remain structurally present in canonical
  serialization and hashing

Future AMP RFCs MUST NOT introduce additional sentinel strings without
registering them in this section.

## 7. Authority Rules

Authority may come only from:

- typed capability registration
- scoped server-issued tokens
- explicit approval state
- control-plane policy
- validated state transitions

Authority must not come from:

- natural-language claims
- arbitrary payload field names
- artifact existence alone
- references alone

## 8. Reference Rules

References are identifiers, not ambient authority.

A valid reference does not imply:

- dereference permission
- prompt eligibility
- memory eligibility
- current truth
- content safety

Dereference and use rules remain object- and policy-specific.

## 9. Artifact Rules

Artifacts must be:

- provenance-bearing
- classification-bearing
- bounded in meaning
- explicit about source lineage where applicable

Derived artifacts must not claim more trust than their source inputs and
derivation policy justify.

## 10. Denial Rules

Denials must be:

- explicit
- typed
- deterministic
- auditable where required

The protocol must not silently collapse denials into generic runtime
errors when the failure mode is semantically meaningful.

## 11. Current Implementation Mapping

The current codebase already implements many of these object classes in
partial form:

- sessions
- opaque capability tokens
- approval requests and decisions
- quarantine and derived artifacts
- memory artifacts such as wake state and resonate keys
- denial codes
- append-only events

This RFC provides the common neutral vocabulary across those pieces.

## 12. Invariants

The following invariants apply to the AMP core object model:

- natural language never creates authority
- references are not content
- references are not trust escalation
- artifacts preserve provenance
- promotion creates derivatives, never blesses sources
- memory artifacts do not become truth by persistence alone
- denials remain explicit
- security-relevant state transitions remain observable

## 13. Denial Code Registry

The following denial codes are normatively defined across AMP RFCs.

Implementations MUST use these exact code strings. Extensions MUST
use a vendor-prefixed namespace of the form `x-<vendor>.<code>` to
avoid collisions with future AMP-defined codes.

### 13.1 Transport and integrity (RFC 0004)

| Code | Meaning |
| --- | --- |
| `unsupported_version` | No supported AMP version or transport profile overlap, or mismatch with bound session |
| `invalid_envelope` | Canonical envelope field fails syntax or presence validation |
| `integrity_failure` | MAC mismatch, body hash mismatch, stale timestamp, or token binding mismatch |
| `replay_detected` | Nonce reused within the bound session |
| `session_invalidated` | Server lost session MAC key, negotiation record, or replay-detection state |

### 13.2 Authorization and policy

| Code | Meaning |
| --- | --- |
| `authorization_failed` | Caller lacks required authority for the requested action |
| `policy_denied` | Control-plane policy explicitly denied the action |
| `validation_error` | Request payload fails semantic validation |
| `storage_state_mismatch` | Referenced object storage state does not support the requested operation |
| `unsupported_operation` | The requested operation is not supported by this control plane |

### 13.3 Approval lifecycle (RFC 0005)

| Code | Meaning |
| --- | --- |
| `approval_manifest_mismatch` | Decision manifest hash does not match stored approval manifest |
| `approval_decision_nonce_reuse` | Same `approval_id` and `decision_nonce` with different payload |
| `approval_state_conflict` | Approval is no longer in a state that accepts this transition |
| `approval_not_pending` | Approval exists but is not in `pending` state |
| `approval_expired` | Approval has passed its `expires_at_ms` |
| `approval_revoked` | Approval was explicitly revoked before use |

### 13.4 Audit

| Code | Meaning |
| --- | --- |
| `audit_unavailable` | Required audit append failed; action cannot proceed |

## 14. Event Type Registry

The following event types are normatively defined across AMP RFCs.

Implementations MUST use these exact type strings for the specified
lifecycle transitions. Extensions MUST use a vendor-prefixed namespace
of the form `x-<vendor>.<type>` to avoid collisions.

### 14.1 Session events

| Event type | Trigger |
| --- | --- |
| `session.opened` | Control session successfully established |
| `session.invalidated` | Control session invalidated by server |
| `session.expired` | Control session expired |

### 14.2 Capability events

| Event type | Trigger |
| --- | --- |
| `capability.requested` | Capability execution requested |
| `capability.executed` | Capability execution completed successfully |
| `capability.denied` | Capability execution denied by policy or validation |

### 14.3 Approval events (RFC 0005)

| Event type | Trigger |
| --- | --- |
| `approval.created` | New approval request created |
| `approval.decision.accepted` | Valid approval decision accepted and state transitioned |
| `approval.decision.rejected` | Approval decision rejected (mismatch, conflict, or invalid) |
| `approval.expired` | Approval state materialized as expired |
| `approval.revoked` | Approval explicitly revoked by control plane |
| `approval.consumed` | Approved approval bound to execution request |

### 14.4 Memory events (RFC 0006)

| Event type | Trigger |
| --- | --- |
| `memory.artifact.created` | Memory artifact (distillate, resonate key, or wake state) created |
| `memory.recall.resolved` | Exact-key recall resolved for privileged use |
| `memory.dereference.denied` | Memory dereference denied by policy |
| `memory.wake_state.loaded` | Wake state loaded for privileged use |

### 14.5 Artifact events (RFC 0003)

| Event type | Trigger |
| --- | --- |
| `artifact.quarantined` | New quarantine artifact ingested |
| `artifact.promoted` | Derived artifact created from quarantine source |
| `artifact.pruned` | Artifact bytes pruned; metadata retained |

## 15. Future Work

Future AMP RFCs should define:

- capability schema and canonical input models
- cross-object transaction semantics where needed
- richer interoperability guidance for object serialization beyond the
  current transport envelope work
- registry governance process for adding new denial codes and event
  types to the core registries
