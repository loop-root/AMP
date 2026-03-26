**Last updated:** 2026-03-24

# AMP Implementation Mapping

Status: current-state mapping  
Authority: descriptive / implementation-facing  
Location: **canonical copy** under `docs/AMP/` in this repository (vendored north star; periodically sync with a standalone AMP checkout if you maintain one alongside Morph).  
North star: [AMP RFCs](../AMP-RFCs/0001-local-transport-profile.md) — if this tree and standalone AMP diverge, reconcile by copying RFCs here and re-running link checks.

## Purpose

This document maps the current **Haven + Loopgate** implementation onto the
Authority Mediation Protocol (AMP) RFC track.

The AMP RFCs describe the intended neutral protocol and object model.
This document explains how the current codebase implements those ideas
today, where it is already aligned, and where the implementation is
still product-specific or intentionally ahead/behind the RFCs.

Use this document as:

- a reference for implementers
- a bridge between the codebase and the AMP RFCs
- a place to record intentional drift or partial alignment

Do not treat this document as the protocol specification.

If this document and an AMP RFC drift, the RFC text is authoritative.

Links into `internal/` and `cmd/` in this document are **Morph codebase** pointers only. They are not part of the neutral protocol specification.

**Product integrity:** [Morph RFC 0001 (Loopgate token policy)](../../rfcs/0001-loopgate-token-policy.md) is the Loopgate-local articulation of tokens and signing; it MUST stay consistent with [AMP RFC 0004](../AMP-RFCs/0004-canonical-envelope-and-integrity-binding.md) for canonical request bytes and MAC rules (AMP 0004 wins on conflict).

## Reading order

For protocol intent, read:

1. [AMP RFC 0001: Local Transport Profile](../AMP-RFCs/0001-local-transport-profile.md)
2. [AMP RFC 0002: Core Object Model](../AMP-RFCs/0002-core-object-model.md)
3. [AMP RFC 0003: Artifact and Reference Model](../AMP-RFCs/0003-artifact-and-reference-model.md)
4. [AMP RFC 0004: Canonical Envelope and Integrity Binding](../AMP-RFCs/0004-canonical-envelope-and-integrity-binding.md)
5. [AMP RFC 0005: Approval Lifecycle and Decision Binding](../AMP-RFCs/0005-approval-lifecycle-and-decision-binding.md)
6. [AMP RFC 0006: Continuity and Memory Authority](../AMP-RFCs/0006-continuity-and-memory-authority.md)
7. [AMP RFC 0007: Core Envelopes and Compact Schemas](../AMP-RFCs/0007-core-envelopes-and-compact-schemas.md)
8. [AMP RFC 0008: Open issues, gaps, and challenged assumptions](../AMP-RFCs/0008-open-issues-gaps-and-assumptions.md) (non-normative working analysis)

For current implementation, read this document and the linked code.

For implementation verification, read:

- [AMP local-uds-v1 Conformance Checklist](../conformance/local-uds-v1-checklist.md)

## Layer mapping

Current product layers:

- **Haven** (`cmd/haven/`)
  - sole shipped operator shell
  - planning and presentation
  - bounded continuity projection
  - user interaction
- `Loopgate`
  - privileged control-plane implementation
  - policy, approvals, execution, secrets, audit
- `AMP`
  - neutral protocol/object model spanning transport, capabilities,
    approvals, artifacts, denials, and continuity references

Today, AMP exists primarily as a specification layer and partial
conceptual model. The runtime code still uses product-specific package
names and structs.

## Object mapping

### Session

AMP object:

- `session`

Current implementation:

- [OpenSessionRequest](../../../internal/loopgate/types.go)
- [OpenSessionResponse](../../../internal/loopgate/types.go)
- [controlSession](../../../internal/loopgate/server.go)

Alignment:

- strong

Notes:

- current sessions are local, server-issued, opaque, and peer-bound
- session meaning is implementation-specific but semantically aligned

### Capability

AMP object:

- `capability`

Current implementation:

- [CapabilitySummary](../../../internal/loopgate/types.go)
- [CapabilityRequest](../../../internal/loopgate/types.go)
- [CapabilityResponse](../../../internal/loopgate/types.go)
- configured capability records in [integration_config.go](../../../internal/loopgate/integration_config.go)

Alignment:

- strong for current local profile

Notes:

- request arguments are still `map[string]string`, which is narrower and
  more implementation-specific than the future AMP object model likely
  wants

### Capability Token

AMP object:

- `capability_token`

Current implementation:

- [capabilityToken](../../../internal/loopgate/server.go)
- token denial codes in [types.go](../../../internal/loopgate/types.go)

Alignment:

- strong

Notes:

- current tokens are opaque, scoped, short-lived, and validated
  server-side
- request integrity is carried by the signed request envelope, not the
  token itself

### Approval Request / Decision

AMP objects:

- `approval_request`
- `approval_decision`

Current implementation:

- [pendingApproval](../../../internal/loopgate/server.go)
- [ApprovalDecisionRequest](../../../internal/loopgate/types.go)
- UI approval shapes in [ui_types.go](../../../internal/loopgate/ui_types.go)

Alignment:

- strong

Notes:

- approvals are Loopgate-owned
- approval decisions are bound to approval token + decision nonce
- Haven renders but does not authorize

### Artifact

AMP object:

- `artifact`

Current implementation:

- quarantine artifacts in [quarantine.go](../../../internal/loopgate/quarantine.go)
- derived artifacts in [promotion.go](../../../internal/loopgate/promotion.go)
- memory artifacts in [wake_state.go](../../../internal/memory/wake_state.go), [distillate.go](../../../internal/memory/distillate.go), and [recall.go](../../../internal/memory/recall.go)

Alignment:

- medium

Notes:

- artifact semantics are real
- artifact envelopes are not yet unified under a neutral shared AMP type

### Quarantine Artifact

AMP object:

- `quarantine_artifact`

Current implementation:

- [quarantinedPayloadRecord](../../../internal/loopgate/quarantine.go)
- quarantine metadata/view/prune request and response types in [quarantine.go](../../../internal/loopgate/quarantine.go) and [types.go](../../../internal/loopgate/types.go)

Alignment:

- strong

Notes:

- trust state and storage state are distinct
- metadata and blob bytes are separated
- pruning preserves lineage

### Derived Artifact

AMP object:

- `derived_artifact`

Current implementation:

- [derivedArtifactRecord](../../../internal/loopgate/promotion.go)

Alignment:

- strong

Notes:

- promotion is derivative-based
- source remains quarantined
- exact duplicate semantics are explicit

### Memory Artifact

AMP object:

- `memory_artifact`

Current implementation:

- [WakeState](../../../internal/memory/wake_state.go)
- [Distillate](../../../internal/memory/distillate.go)
- resonate key documents in [recall.go](../../../internal/memory/recall.go)

Alignment:

- medium

Notes:

- artifacts exist and are bounded
- governance is still more **client-local** than the RFC target state
- current client-local continuity behavior is descriptive drift only and
  remains non-authoritative until it is rebound through Loopgate-owned
  AMP paths

### Reference

AMP object:

- `reference`

Current implementation:

- quarantine refs
- derived artifact refs
- wake-state source refs
- resonate keys

Alignment:

- medium

Notes:

- references exist semantically
- most are still represented as raw strings or ad hoc structs instead of
  a shared neutral reference type

### Denial

AMP object:

- `denial`

Current implementation:

- [DenialCode*](../../../internal/loopgate/types.go)
- denial-bearing [CapabilityResponse](../../../internal/loopgate/types.go)

Alignment:

- strong

Notes:

- explicit denial taxonomy already exists
- this is one of the strongest AMP-aligned parts of the system

### Event

AMP object:

- `event`

Current implementation:

- [Event](../../../internal/ledger/ledger.go)
- Loopgate audit events in [server.go](../../../internal/loopgate/server.go)
- continuity annotations in [continuity.go](../../../internal/memory/continuity.go)

Alignment:

- strong

Notes:

- append-only semantics exist
- chain verification now exists before append/bootstrap
- artifacts and continuity both already rely on event-style state

## Flow mapping

### Local session establishment

AMP RFC:

- local transport profile
- session creation
- scoped token issuance

Current implementation:

- [POST /v1/session/open](../../../internal/loopgate/server.go)
- client session open in [client.go](../../../internal/loopgate/client.go)

Alignment:

- strong

### Capability execution

AMP RFC:

- capability request
- signed request envelope
- explicit denial or structured result

Current implementation:

- [POST /v1/capabilities/execute](../../../internal/loopgate/server_capability_handlers.go)
- request and response types in [types.go](../../../internal/loopgate/types.go)

Alignment:

- strong

### Approval flow

AMP RFC:

- approval request
- approval decision
- explicit state transitions

Current implementation:

- [POST /v1/approvals/{id}/decision](../../../internal/loopgate/server_capability_handlers.go)
- UI approval flow in [ui_server.go](../../../internal/loopgate/ui_server.go)

Alignment:

- strong

### Model inference

AMP RFC:

- local signed request
- privileged execution via control plane

Current implementation:

- [POST /v1/model/reply](../../../internal/loopgate/server_model_handlers.go)
- client call in [client.go](../../../internal/loopgate/client.go)

Alignment:

- strong

Notes:

- this recently moved fully behind Loopgate
- this is now one of the clearest examples of AMP-style mediation

### Quarantine inspection and pruning

AMP RFC:

- artifact metadata inspection
- governed view
- explicit prune lifecycle

Current implementation:

- [POST /v1/quarantine/metadata](../../../internal/loopgate/server_quarantine_handlers.go)
- [POST /v1/quarantine/view](../../../internal/loopgate/server_quarantine_handlers.go)
- [POST /v1/quarantine/prune](../../../internal/loopgate/server_quarantine_handlers.go)

Alignment:

- strong

### Promotion

AMP RFC:

- derivative-based artifact promotion
- target-specific classification
- lineage preservation

Current implementation:

- promotion logic in [promotion.go](../../../internal/loopgate/promotion.go)

Alignment:

- strong

### Memory continuity and recall

AMP RFC:

- continuity stream
- wake state
- memory artifact handling
- bounded recall

Current implementation:

- continuity annotations in [continuity.go](../../../internal/memory/continuity.go)
- wake-state build/load in [wake_state.go](../../../internal/memory/wake_state.go)
- recall in [recall.go](../../../internal/memory/recall.go)

Alignment:

- medium

Notes:

- semantics are aligned
- authority placement is not fully aligned
- current code is still more client-local than the AMP / product-RFC target

## Intentional drift

The following drifts are intentional for now:

### Product-specific package names

The implementation still uses product-oriented names (`morph` module, `Haven`, `Loopgate`) rather than neutral `amp` package names.

Reason:

- product-specific names are still the clearest implementation anchors
- premature neutral package churn would add refactor cost without clear
  runtime value yet

### Memory boundary placement

Wake-state build/load and exact-key recall remain **client-local** (Haven-side packages) in parts of the codebase.

Reason:

- the bounded continuity model is useful already
- the runtime does not yet need a full Loopgate-mediated memory API to
  preserve core invariants

Drift marker:

- these behaviors are outside AMP today
- these behaviors remain non-authoritative until rebound through
  Loopgate-owned AMP paths

### Ad hoc reference representations

Many references are still strings or local structs rather than a unified
AMP reference object.

Reason:

- semantics matter more than envelope reuse at this stage

## Current gaps relative to AMP

1. No shared neutral AMP package in code
2. No unified artifact envelope type
3. No unified reference type
4. Memory authority still partly local to the Haven client packages
5. Capability arguments are still narrower than a future generalized AMP
   object model likely needs

## Recommended alignment steps

In order:

1. keep AMP as a specification layer first
2. align memory authority and recall semantics before broad package
   renaming
3. introduce neutral wrappers only when they reduce real duplication or
   drift
4. avoid product-wide renames until the protocol model is stable enough
   to justify them

## What to treat as north star vs current state

North star:

- AMP RFCs

Current state:

- this mapping
- current product architecture docs
- current code

When the code differs from the RFCs:

- preserve invariants first
- record the difference here
- only then choose whether to move code toward the RFC or narrow the RFC
  toward reality
