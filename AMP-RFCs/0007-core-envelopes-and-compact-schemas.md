# AMP RFC 0007: Core Envelopes and Compact Schemas

Status: draft  
Track: AMP (Authority Mediation Protocol)  
Authority: protocol design / target architecture  
Current implementation alignment: partial

## 1. Purpose

This document provides a compact, implementation-ready schema layer for
small AMP objects that appear across multiple RFCs.

The goal is not to replace the normative semantics defined elsewhere.
The goal is to gather the shared object shapes into one place so an
implementer does not need to reconstruct them across documents.

This RFC compacts the normative object shapes for:

- `denial`
- `event`
- `artifact_ref`
- `memory_ref`
- `approval_request`
- `approval_decision`

Semantics remain governed by the companion RFCs:

- RFC 0004 for canonical request integrity and minimal denial/event
  envelope semantics
- RFC 0005 for approval lifecycle and decision binding
- RFC 0006 for continuity and memory authority

If wording in this compact schema layer ever drifts from those RFCs, the
source RFC for that object class is authoritative.

## 2. Scope

This RFC applies to compact shared object shapes.

This RFC does not define:

- canonical request byte serialization
- transport carriage
- full object-specific payload schemas for every AMP object class
- capability-specific request or response bodies

## 3. Normative Language

The key words `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`, `SHOULD NOT`,
and `MAY` in this document are to be interpreted as normative
requirements.

## 4. Design Principles

The compact schema layer is built around the following principles:

- shared small objects should have one compact home
- compact schemas should reduce ambiguity, not create a second protocol
- compact object shapes should stay implementation-neutral
- references remain identifiers, not authority
- approval objects remain bounded and exact

## 5. Shared Conventions

Unless a specific object definition says otherwise, the following
conventions apply:

- object fields are shown using JSON-like notation for compactness
- field order inside these compact objects is not semantically
  significant unless another RFC defines canonical bytes for that object
- timestamps use Unix epoch milliseconds in UTC and end in `_at_ms` or
  `_ms`
- SHA-256 fields use 64 lower-case hexadecimal characters unless a field
  explicitly requires a prefixed binding form
- example hashes in this RFC are illustrative unless another RFC marks
  them as conformance test vectors
- the literal string `none` is used only where the field is required but
  a concrete value does not exist
- opaque identifiers remain opaque and MUST NOT be interpreted as
  self-describing authority

## 6. Denial Envelope

The compact denial object shape is:

```json
{
  "kind": "denial",
  "code": "unsupported_version",
  "message": "operator-safe denial text",
  "retryable": false,
  "occurred_at_ms": 1735689601123,
  "request_canonical_sha256": "c1216b6165388937bc7b4eabf26ac1a676784339c1dc02052536960efb58597e",
  "amp_version": "1.0",
  "transport_profile": "local-uds-v1"
}
```

Field rules:

- `kind`
  - fixed value `denial`
- `code`
  - stable typed denial code
- `message`
  - short operator-safe text
  - MUST NOT contain raw secret-bearing material
- `retryable`
  - boolean
- `occurred_at_ms`
  - Unix epoch milliseconds UTC
- `request_canonical_sha256`
  - canonical request hash when available, otherwise `none`
- `amp_version`
  - selected AMP version, otherwise `none`
- `transport_profile`
  - selected transport profile, otherwise `none`

Denial code values come from the relevant RFC for the failure class.
Examples include:

- `unsupported_version`
- `invalid_envelope`
- `integrity_failure`
- `replay_detected`
- `authorization_failed`
- `policy_denied`
- `validation_error`
- `storage_state_mismatch`
- `unsupported_operation`
- `approval_manifest_mismatch`
- `approval_decision_nonce_reuse`
- `approval_state_conflict`
- `approval_expired`
- `approval_revoked`

## 7. Event Envelope

The compact event object shape is:

```json
{
  "kind": "event",
  "event_id": "event:amp:01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "event_type": "approval.created",
  "occurred_at_ms": 1735689601123,
  "subject_ref": "approval:01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "actor_ref": "session:sess_01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "causal_ref": "request:c1216b6165388937bc7b4eabf26ac1a676784339c1dc02052536960efb58597e",
  "payload_sha256": "17d8e1b8f0b2f6f77c5418d4a70f2b6584ebebc0b89f9d9d9db2f8f1f59a9a2b",
  "amp_version": "1.0"
}
```

Field rules:

- `kind`
  - fixed value `event`
- `event_id`
  - stable unique event identifier within the authority boundary
- `event_type`
  - stable typed event name
- `occurred_at_ms`
  - Unix epoch milliseconds UTC
- `subject_ref`
  - opaque subject identifier or object reference
- `actor_ref`
  - opaque actor or authority-path identifier
- `causal_ref`
  - request hash, approval id, prior event id, or `none`
- `payload_sha256`
  - structured payload hash, otherwise `none`
- `amp_version`
  - AMP version under which the event semantics were evaluated

The event envelope does not replace the append-only event log. It is the
minimal shared record shape for cross-RFC references.

## 8. Artifact Reference

The compact `artifact_ref` object shape is:

```json
{
  "kind": "artifact_ref",
  "artifact_id": "artifact:amp:01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "artifact_class": "derived_artifact",
  "content_sha256": "3e9663348715e01175b0bf6bee923d06e8cb153353ff32a63301af6462c40723",
  "storage_state": "blob_present",
  "classification": "bounded-derived",
  "source_artifact_id": "artifact:amp:source:01ARZ3NDEKTSV4RRFFQ69G5FAV"
}
```

Field rules:

- `kind`
  - fixed value `artifact_ref`
- `artifact_id`
  - stable artifact identifier
- `artifact_class`
  - one of `quarantine_artifact`, `derived_artifact`, or
    `memory_artifact`
- `content_sha256`
  - referenced content hash when known, otherwise `none`
- `storage_state`
  - stable storage state such as `blob_present`, `blob_pruned`, or
    `metadata_only`
- `classification`
  - bounded classification or `none`
- `source_artifact_id`
  - stable source artifact id or `none`

`artifact_ref` is an identifier plus bounded metadata. It MUST NOT be
treated as:

- content bytes
- dereference permission
- prompt authority
- trust elevation

## 9. Memory Reference

The compact `memory_ref` object shape is:

```json
{
  "kind": "memory_ref",
  "memory_id": "memory:amp:01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "memory_subtype": "wake_state",
  "content_sha256": "none",
  "storage_state": "metadata_only",
  "classification": "bounded-continuity",
  "source_artifact_id": "artifact:amp:source:01ARZ3NDEKTSV4RRFFQ69G5FAV"
}
```

Field rules:

- `kind`
  - fixed value `memory_ref`
- `memory_id`
  - stable memory artifact identifier
- `memory_subtype`
  - one of `distillate`, `wake_state`, or `resonate_key`
- `content_sha256`
  - content hash when bytes are present, otherwise `none`
- `storage_state`
  - stable storage state such as `blob_present`, `blob_pruned`, or
    `metadata_only`
- `classification`
  - bounded classification or `none`
- `source_artifact_id`
  - stable source artifact id or `none`

`memory_ref` is a reference object only. It does not imply:

- content access
- exact-key recall authority
- prompt inclusion
- privileged execution inclusion

## 10. Approval Request

The compact `approval_request` object shape is:

```json
{
  "kind": "approval_request",
  "approval_id": "approval:01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "approval_manifest_sha256": "b0f1d3f5a76f19e3bc03c0ff0fb76bb9c699f7f7d0d893d2fe6d4a80cd8615af",
  "action_class": "capability.execute",
  "subject_class": "artifact",
  "subject_ref": "artifact:amp:01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "subject_binding": "manifest-sha256:3e9663348715e01175b0bf6bee923d06e8cb153353ff32a63301af6462c40723",
  "execution_method": "POST",
  "execution_path": "/v1/capabilities/execute",
  "execution_body_sha256": "3e9663348715e01175b0bf6bee923d06e8cb153353ff32a63301af6462c40723",
  "approval_scope": "single-use",
  "created_at_ms": 1735689601123,
  "expires_at_ms": 1735689661123,
  "state": "pending"
}
```

Field rules:

- `kind`
  - fixed value `approval_request`
- `approval_id`
  - stable approval identifier
- `approval_manifest_sha256`
  - canonical approval manifest hash from RFC 0005
- `action_class`
  - stable action class identifier
- `subject_class`
  - stable subject object class identifier
- `subject_ref`
  - stable subject reference or `none`
- `subject_binding`
  - `manifest-sha256:<hex>` or `object-sha256:<hex>`
- `execution_method`
  - canonical method as defined by RFC 0004
- `execution_path`
  - canonical path as defined by RFC 0004
- `execution_body_sha256`
  - exact approved action-body digest
- `approval_scope`
  - fixed value `single-use` for approval lifecycle v1
- `created_at_ms`
  - creation time
- `expires_at_ms`
  - expiry time
- `state`
  - one of `pending`, `approved`, `denied`, `expired`, `revoked`, or
    `consumed`

## 11. Approval Decision

The compact `approval_decision` object shape is:

```json
{
  "kind": "approval_decision",
  "approval_id": "approval:01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "approval_manifest_sha256": "b0f1d3f5a76f19e3bc03c0ff0fb76bb9c699f7f7d0d893d2fe6d4a80cd8615af",
  "decision": "approve",
  "decision_nonce": "AAECAwQFBgcICQoLDA0ODw"
}
```

Field rules:

- `kind`
  - fixed value `approval_decision`
- `approval_id`
  - stable approval identifier
- `approval_manifest_sha256`
  - exact manifest hash for the approval under review
- `decision`
  - either `approve` or `deny`
- `decision_nonce`
  - base64url without padding, at least 16 raw bytes after decoding

The compact approval decision object does not replace:

- canonical request integrity from RFC 0004
- approval lifecycle and race semantics from RFC 0005

## 12. Invariants

The following invariants apply:

- compact schemas summarize, not supersede, the source RFC semantics
- reference objects remain identifiers, not authority grants
- denial and event envelopes remain minimal and typed
- approval objects remain exact and bounded
- compact schema examples do not redefine canonical byte formats

## 13. Future Work

Future AMP RFCs should define:

- richer typed payload schemas for additional object classes
- compatibility guidance for schema evolution across AMP versions
