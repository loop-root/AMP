# AMP RFC 0005: Approval Lifecycle and Decision Binding

Status: draft  
Track: AMP (Authority Mediation Protocol)  
Authority: protocol design / target architecture  
Current implementation alignment: partial

## 1. Purpose

This document defines the lifecycle for AMP approval objects and the
binding rules that prevent approvals from becoming open-ended authority
grants.

This RFC defines:

- approval states
- legal state transitions
- expiry and revocation semantics
- approval manifest binding
- decision idempotency and replay protection
- concurrent decision handling
- required audit events

The goal is to ensure that an approval applies only to the exact
reviewed object and the exact reviewed action shape, not to a later or
broader interpretation.

## 2. Scope

This RFC applies to:

- `approval_request`
- `approval_decision`
- approval-bound execution of privileged AMP actions
- required audit events related to approval lifecycle transitions

This RFC does not define:

- multi-party or quorum approvals
- long-lived reusable approval grants
- delegation or sharing of approval authority across trust domains

Canonical request integrity remains defined by RFC 0004.

## 3. Normative Language

The key words `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`, `SHOULD NOT`,
and `MAY` in this document are to be interpreted as normative
requirements.

## 4. Design Principles

The approval model is built around the following principles:

- approvals are explicit, typed, and bounded
- approvals are single-use by default
- approvals bind to stable subject state and exact execution shape
- decision replay must not duplicate authority or audit transitions
- the first valid state transition wins
- terminal approval states do not silently reopen
- approval use must remain auditable

## 5. Approval Objects

### 5.1 Approval request

An `approval_request` represents a pending authorization checkpoint
created by the control plane.

Every approval request MUST carry:

- `approval_id`
- `approval_manifest_sha256`
- `action_class`
- `subject_class`
- `subject_ref` or `none`
- `subject_binding`
- `execution_method`
- `execution_path`
- `execution_body_sha256`
- `approval_scope`
- `created_at_ms`
- `expires_at_ms`
- `state`

### 5.2 Approval scope

AMP approval lifecycle v1 defines exactly one approval scope:

- `single-use`

An approval with scope `single-use` authorizes at most one matching
execution binding. After the first matching bind, the approval MUST
transition to `consumed` whether or not the downstream action succeeds.

### 5.3 Subject binding

The `subject_binding` field binds the approval to stable reviewed state.

It MUST be one of:

- `manifest-sha256:<64 lower-case hex>`
- `object-sha256:<64 lower-case hex>`

If the control plane cannot produce a stable subject binding with one of
those forms:

- it MUST NOT create the approval request
- it MUST fail closed rather than creating an open-ended approval

### 5.4 Approval decision

An `approval_decision` is an explicit response to a single
`approval_request`.

Every approval decision MUST carry:

- `approval_id`
- `approval_manifest_sha256`
- `decision`
- `decision_nonce`

The `decision` value MUST be one of:

- `approve`
- `deny`

## 6. Canonical Approval Manifest

### 6.1 Purpose

The approval manifest is the exact object that an approval decision
authorizes or denies.

The `approval_manifest_sha256` is the SHA-256 digest of the canonical
approval manifest bytes defined below.

### 6.2 Canonical approval manifest bytes

Canonical approval manifest bytes are the UTF-8 bytes of the following
exact line sequence:

```text
amp-approval-manifest-v1
action-class:<action_class>
subject-class:<subject_class>
subject-ref:<subject_ref_or_none>
subject-binding:<subject_binding>
execution-method:<execution_method>
execution-path:<execution_path>
execution-body-sha256:<execution_body_sha256>
approval-scope:<approval_scope>
expires-at-ms:<expires_at_ms>
```

Serialization rules:

- each line ends with a single line-feed byte `\n`
- there is no carriage return byte `\r`
- there is no blank line
- the final line also ends with `\n`
- field order MUST NOT change

### 6.3 Manifest field rules

The following rules apply:

- `action_class`
  - stable action class identifier
- `subject_class`
  - stable subject object class identifier
- `subject_ref_or_none`
  - opaque stable reference or the literal value `none`
- `subject_binding`
  - stable binding from Section 5.3
- `execution_method`
  - canonical method string as defined by RFC 0004
- `execution_path`
  - canonical path string as defined by RFC 0004
- `execution_body_sha256`
  - exact SHA-256 of the action body bytes the approval authorizes
- `approval_scope`
  - fixed value `single-use` for approval lifecycle v1
- `expires_at_ms`
  - absolute approval expiry time in Unix epoch milliseconds UTC

An approval decision MUST bind to the stored `approval_manifest_sha256`.
If the hash in the decision request does not match the stored manifest
hash, the server MUST reject the decision with denial code
`approval_manifest_mismatch`.

## 7. Approval States

Approval lifecycle v1 defines the following states:

- `pending`
- `approved`
- `denied`
- `expired`
- `revoked`
- `consumed`

### 7.1 State meanings

- `pending`
  - waiting for a valid explicit decision
- `approved`
  - explicitly approved and still eligible for one matching bound use
- `denied`
  - explicitly denied and terminal
- `expired`
  - no longer usable because the expiry time passed and terminal
- `revoked`
  - invalidated by the control plane before use and terminal
- `consumed`
  - already bound to one matching execution request and terminal

### 7.2 Legal transitions

The only legal transitions are:

- creation -> `pending`
- `pending` -> `approved`
- `pending` -> `denied`
- `pending` -> `expired`
- `pending` -> `revoked`
- `approved` -> `consumed`
- `approved` -> `expired`
- `approved` -> `revoked`

All other transitions are forbidden.

In particular, the following are forbidden:

- `denied` -> any other state
- `expired` -> any other state
- `revoked` -> any other state
- `consumed` -> any other state
- `approved` -> `denied`
- `approved` -> `pending`

## 8. Expiry Rules

Every approval request MUST define `expires_at_ms` at creation time.

Rules:

- `expires_at_ms` MUST be greater than `created_at_ms`
- a server MUST NOT accept a decision if the server receive time is
  greater than or equal to `expires_at_ms`
- a server MUST NOT consume an approval if the binding attempt occurs at
  or after `expires_at_ms`

If a decision or execution attempt encounters an approval past its
expiry:

- the server MUST materialize state `expired` before returning
- the server MUST fail closed

An implementation MAY materialize expiry earlier through a background
task, but background materialization is not required for correctness.

## 9. Revocation Rules

The control plane MAY revoke an approval that is currently:

- `pending`
- `approved`

Revocation reasons may include:

- policy change
- subject-state invalidation
- session or authority-path invalidation
- explicit operator cancellation

Revocation rules:

- revocation MUST be explicit and auditable
- revocation MUST transition the approval to `revoked`
- revocation MUST invalidate future consumption attempts
- revocation MUST NOT be silently converted into expiry or denial

## 10. Decision Binding, Idempotency, and Replay Protection

### 10.1 Decision nonce

Every approval decision MUST include a `decision_nonce`.

The `decision_nonce`:

- MUST be base64url without padding
- MUST decode to at least 16 raw bytes
- MUST be unique per `approval_id` for distinct decision attempts

### 10.2 Decision binding rules

A valid approval decision request MUST be bound to:

- the `approval_id`
- the stored `approval_manifest_sha256`
- the decision actor's current authority path as evaluated by policy
- the canonical request integrity rules from RFC 0004

The control plane MUST reject a decision if:

- the approval is not currently `pending`
- the decision manifest hash does not match
- the decision actor is not authorized
- the approval is expired

### 10.3 Idempotency rules

Idempotency for approval decisions is keyed by:

- `approval_id`
- `decision_nonce`

If the server receives the same `approval_id` and `decision_nonce`
again:

- and the decision payload is byte-for-byte identical to the previously
  accepted decision payload, the server MUST return the same stored
  result without adding a second state transition
- and the decision payload differs, the server MUST reject the request
  with denial code `approval_decision_nonce_reuse`

The transport request nonce from RFC 0004 does not replace the decision
nonce. A client retry after transport uncertainty MUST use:

- a new transport request nonce
- the same `decision_nonce`

### 10.4 Concurrent decisions

The control plane MUST serialize mutation of an approval object's state.

Concurrent decision rules:

- the first valid transition out of `pending` wins
- later decisions MUST observe the post-transition state
- later decisions MUST NOT overwrite the winning terminal or approved
  state
- an exact idempotent retry of the winning decision MAY return the
  stored prior result
- a different decision against a non-`pending` approval MUST be rejected
  with denial code `approval_state_conflict`

## 11. Consumption Rules

An `approved` approval may be consumed only by an execution request that
matches the stored approval manifest exactly.

To consume an approval, the server MUST verify:

- `execution_method` matches
- `execution_path` matches
- the execution request body hash matches `execution_body_sha256`
- the referenced subject still matches the stored `subject_binding`
- the approval is still in state `approved`
- the approval is not expired or revoked

Consumption rules:

- consumption MUST be atomic with binding the approval to the execution
  request
- the approval MUST transition to `consumed` before or with action
  dispatch
- downstream execution failure MUST NOT restore `approved`
- a consumed approval MUST NOT be reusable

## 12. Required Audit Events

Approval lifecycle events MUST use the minimal event envelope from RFC
0004 plus object-specific payload fields.

The following event types are REQUIRED:

- `approval.created`
  - payload MUST include `approval_id`, `approval_manifest_sha256`,
    `subject_binding`, `expires_at_ms`
- `approval.decision.accepted`
  - payload MUST include `approval_id`, `approval_manifest_sha256`,
    `decision`, `decision_nonce_sha256`
- `approval.decision.rejected`
  - payload MUST include `approval_id` when known,
    `rejection_code`, `approval_manifest_sha256` when known
- `approval.expired`
  - payload MUST include `approval_id`, `approval_manifest_sha256`
- `approval.revoked`
  - payload MUST include `approval_id`, `approval_manifest_sha256`,
    `revocation_reason_class`
- `approval.consumed`
  - payload MUST include `approval_id`, `approval_manifest_sha256`,
    `execution_request_canonical_sha256`

Audit rules:

- the event stream MUST remain append-only
- exactly one winning decision transition may be recorded for a given
  approval lifecycle
- idempotent retries MUST NOT create duplicate winning-transition events
- rejected decision attempts SHOULD be observable

## 13. Minimal Denial Codes for Approval Lifecycle

Approval lifecycle v1 relies on the general denial envelope from RFC
0004 and additionally defines the following stable denial codes:

- `approval_manifest_mismatch`
- `approval_decision_nonce_reuse`
- `approval_state_conflict`
- `approval_expired`
- `approval_revoked`

These codes are additive. They do not replace the general AMP denial
taxonomy.

## 14. Current Implementation Mapping

The current codebase already partially implements these ideas:

- approval requests owned by the control plane
- explicit approval decisions
- approval tokens and decision nonces
- auditable approval flows

This RFC makes the state machine, manifest binding, and replay behavior
explicit and implementation-neutral.

## 15. Invariants

The following invariants apply:

- approvals are single-use and bounded
- approval authority never exists without an explicit approval object
- approval decisions bind to an exact approval manifest hash
- subject state is bound by stable object or manifest hash
- expiry and revocation are explicit
- the first valid state transition wins
- idempotent retries do not duplicate authority or audit events
- consumed approvals never silently reopen

## 16. Future Work

Future AMP RFCs should define:

- multi-party approval policies
- quorum or threshold approval semantics
- structured revocation taxonomies
- bounded multi-use approval forms if ever needed
