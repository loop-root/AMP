# AMP RFC 0003: Artifact and Reference Model

Status: draft  
Track: AMP (Authority Mediation Protocol)  
Authority: protocol design / target architecture  
Current implementation alignment: partial

## 1. Purpose

This document defines how AMP represents artifacts, references, and
lineage.

The goal is to make artifacts durable and attributable without letting
references or storage representation silently become authority.

## 2. Scope

This RFC applies to:

- quarantine artifacts
- derived artifacts
- memory artifacts
- blob references
- lineage-preserving metadata

This RFC does not define transport details or UI behavior beyond what is
necessary for artifact semantics.

## 3. Design Principles

The artifact model is built around the following principles:

- references are not content
- storage representation is not trust escalation
- quarantine is a trust state
- promotion creates new artifacts
- cleanup affects storage lifecycle, not trust history
- lineage survives storage pruning

## 4. Artifact Classes

### 4.1 Quarantine Artifact

A `quarantine_artifact` represents source content that remains untrusted
by default.

It must retain:

- artifact identifier
- source lineage
- content hash
- content type
- size
- classification at ingest
- storage state

Quarantine status persists even if storage state changes later.

### 4.2 Derived Artifact

A `derived_artifact` is created from one or more source artifacts
through explicit governed transformation or promotion.

A derived artifact must record:

- source artifact references
- source hash or equivalent source version binding
- derivation policy or transform type
- resulting classification
- creation actor or authority path
- creation time

### 4.3 Memory Artifact

A `memory_artifact` is a derived continuity object such as:

- `distillate`
- `resonate_key`
- `wake_state`

Memory artifacts remain provenance-bearing and bounded.

## 5. Reference Classes

### 5.1 Artifact Reference

An `artifact_ref` identifies an artifact without granting content access
or authority by itself.

### 5.2 Quarantine Reference

A `quarantine_ref` identifies a quarantined source artifact.

It is a handle to governed source content, not a claim of safety.

### 5.3 Blob Reference

A `blob_ref` is a storage-indirection reference to content associated
with an artifact.

A blob reference must carry enough metadata to preserve lineage and
availability state, such as:

- reference kind
- source artifact or quarantine reference
- content hash
- content type
- size
- storage state

Blob references are not content and must not auto-dereference into
prompt, memory, or ordinary render paths.

### 5.4 Memory Reference

A `memory_ref` identifies a bounded memory artifact such as
`distillate`, `wake_state`, or `resonate_key`.

A memory reference does not imply prompt inclusion.

## 6. Storage State

Artifact trust state and storage state are orthogonal.

For example:

- trust state: quarantined
- storage state: blob_present or blob_pruned

Storage state transitions must not silently alter trust state.

## 7. Lineage Rules

Lineage must remain explicit.

At minimum, the system must preserve:

- source artifact identity
- source content hash or equivalent version binding
- derivation relationship
- classification history
- relevant lifecycle events

Cleanup may remove bytes, but must not erase lineage metadata by
default.

## 8. Promotion Rules

Promotion must create new derived artifacts.

Promotion must not:

- bless the source in place
- mutate the source artifact into a trusted artifact
- erase the source artifact's quarantined status

The promoted derivative must carry:

- source reference
- source verification binding
- target use
- derived classification
- provenance metadata

## 9. Cleanup and Pruning Rules

Cleanup is a storage lifecycle concern, not a trust transition.

Pruning may:

- remove blob bytes
- change storage state
- append lifecycle events

Pruning must not:

- increase prompt or memory eligibility
- erase provenance
- erase classification history
- imply that a source is no longer quarantined

Metadata-only retention preserves lineage, not promotability.

## 10. Dereference Rules

Dereference is always governed.

A reference alone does not justify content access.

Dereference should fail closed when:

- bytes are no longer present
- policy denies the action
- verification binding fails
- the operation requires source bytes that are unavailable

## 11. Current Implementation Mapping

The current codebase already partially implements this model:

- quarantine artifacts with metadata and storage-state separation
- blob-pruned state
- derived artifacts created by promotion
- wake-state and key-based memory artifacts
- explicit lineage and hash-bound promotion checks

This RFC gives those pieces a neutral protocol vocabulary.

## 12. Invariants

The following invariants apply:

- references are identifiers, not trust
- storage indirection is not trust escalation
- quarantine can expire as storage but not disappear as evidence
- promotion creates derivatives, not source mutation
- metadata-only retention preserves lineage, not new capability
- dereference requires explicit governed access
- memory artifacts do not become current truth by being stored

## 13. Future Work

Future AMP RFCs should define:

- promotion target semantics
- serialization and compatibility details for artifact records
- artifact portability or federation rules if ever needed
