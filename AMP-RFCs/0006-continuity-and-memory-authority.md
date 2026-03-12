# AMP RFC 0006: Continuity and Memory Authority

Status: draft  
Track: AMP (Authority Mediation Protocol)  
Authority: protocol design / target architecture  
Current implementation alignment: partial

## 1. Purpose

This document defines the AMP continuity and memory model and clarifies
which memory operations belong to the authority boundary.

This RFC reconciles:

- RFC 0002 core object vocabulary
- RFC 0003 artifact and reference rules
- the current implementation mapping around wake states, distillates,
  resonate keys, and exact-key recall

The goal is to preserve bounded continuity without allowing memory
references, stored summaries, or client-local caches to become ambient
authority.

## 2. Scope

This RFC applies to:

- active continuity stream semantics
- control-plane inspector derivation boundary
- `memory_artifact`
- `distillate`
- `wake_state`
- `resonate_key`
- `memory_ref`
- recall bundle projections
- memory dereference and recall operations
- client-local versus AMP-governed memory authority

This RFC does not define:

- ranking or embedding algorithms
- retention policy durations
- storage backend layout
- public API shapes for internet-facing memory services

## 3. Normative Language

The key words `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`, `SHOULD NOT`,
and `MAY` in this document are to be interpreted as normative
requirements.

## 4. Design Principles

The continuity and memory model is built around the following
principles:

- continuity is modeled as an append-only active stream
- memory artifacts are derived artifacts, not truth sources
- references identify memory objects without granting dereference or
  inclusion rights
- continuity is bounded, attributable, and auditable
- the control-plane inspector is the derivation boundary between
  transient continuity flow and durable memory artifacts
- wake states do not restore authority or revive expired objects
- exact-key recall is governed dereference, not a shortcut around policy
- projections may re-enter active context only by governed reference or
  bounded inclusion
- continuity artifacts and recall handles never become authority
- client-local memory views are projections or suggestions, not
  authority

### 4.1 Active continuity stream

Within an AMP authority context, continuity during active operation MUST
be modeled as an append-only active stream.

The active stream MAY include:

- operator messages
- model outputs
- tool results
- continuity annotations
- other attributable observations within the authority path

Active-stream rules:

- stream ordering MUST remain monotonic within the authority context
- items in the active stream MUST remain attributable
- active-stream presence alone MUST NOT create durable memory authority
- active-stream presence alone MUST NOT imply prompt inclusion,
  dereference rights, or trust elevation

The active stream is the transient continuity flow from which durable
memory artifacts may later be derived. It is not itself a permission
grant.

### 4.2 Control-plane inspector

The control-plane inspector is the control-plane-owned derivation
boundary between transient active continuity flow and durable memory
artifacts.

For privileged use, only the control-plane inspector or an equivalent
control-plane-owned derivation path MAY:

- inspect bounded active-stream windows
- inspect explicit source sets of artifacts or events
- derive or accept authoritative distillates
- derive or accept authoritative resonate keys
- derive or accept authoritative wake states

Client-local summarizers, ranking helpers, and continuity views MAY
propose hints, but for privileged use they remain untrusted content
until rebound through the control-plane inspector path.

### 4.3 Derived continuity forms

The continuity pipeline produces bounded derived forms rather than
ambient memory authority.

Derived continuity rules:

- distillates are derived from bounded active-stream windows or explicit
  source sets with preserved lineage
- resonate keys are bounded retrieval handles over eligible distillates
  or equivalent bounded derived continuity results
- wake states encode bounded resumption projections assembled from
  derived forms and continuity metadata
- recall bundles are bounded projections assembled from derived forms
  and continuity metadata

### 4.4 Reintroduction into active context

Derived continuity forms and bounded projections MAY be reintroduced into
active context only by governed reference or bounded inclusion.

Reintroduction rules:

- reintroduction MUST preserve lineage to contributing artifacts,
  references, or source windows
- reintroduction MUST remain bounded, attributable, and auditable
- reintroduction MUST NOT convert a continuity artifact or recall handle
  into authority
- reintroduction MUST NOT revive expired, revoked, or terminated
  authority
- reintroduction MUST NOT bypass prompt-inclusion or execution-inclusion
  policy

## 5. Taxonomy

### 5.1 Memory artifact

A `memory_artifact` is a subtype of `derived_artifact` used for bounded
continuity, compaction, recall, or resumption.

Every memory artifact MUST preserve:

- source references
- source hash or version binding
- derivation type
- classification
- creation actor or authority path
- creation time

### 5.2 Distillate

A `distillate` is a memory artifact containing bounded derived continuity
content synthesized from a bounded active-stream window or an explicit
source set of artifacts or events.

A distillate:

- is provenance-bearing
- is bounded in scope
- preserves lineage to the bounded stream window or explicit source set
  from which it was derived
- does not become truth by persistence alone
- does not grant prompt inclusion by existence alone

### 5.3 Wake state

A `wake_state` is a memory artifact representing a bounded resumption
bundle for a continuity context.

Normatively, a `wake_state` remains a `memory_artifact`, but its use in
active context is a bounded projection assembled from derived continuity
forms and continuity metadata rather than a restoration of raw prior
context.

Normatively, `wake_state` is a subtype of `memory_artifact`.

RFC 0002 listed wake state alongside top-level artifact classes as
shorthand. The normative hierarchy is:

- `artifact`
  - `derived_artifact`
    - `memory_artifact`
      - `wake_state`
      - `distillate`
      - `resonate_key`

### 5.4 Resonate key

A `resonate_key` is a memory artifact containing a bounded recall
selector or retrieval handle for eligible distillates or equivalent
bounded derived continuity results derived from source continuity state.

A resonate key:

- is a durable derived object
- is a bounded retrieval handle rather than raw authority-bearing memory
- is not equivalent to the memory it may later help retrieve
- does not imply automatic recall, prompt inclusion, or truth

### 5.5 Memory reference

A `memory_ref` identifies a memory artifact without granting:

- content access
- prompt inclusion
- execution inclusion
- policy authority

A `memory_ref` may identify:

- a distillate
- a wake state
- a resonate key

## 6. Provenance and Binding Rules

Every memory artifact MUST record enough metadata to preserve lineage
and bounded meaning.

At minimum, a memory artifact record MUST include:

- memory artifact identifier
- artifact subtype
- source references
- source hash or equivalent source-version binding
- derivation type
- classification
- created_at timestamp
- creation actor or authority path

If the memory artifact contains derived bytes or structured content, the
record SHOULD also preserve:

- content hash
- storage state

If the system cannot preserve provenance for a proposed memory artifact:

- it MUST NOT treat the object as an authoritative memory artifact
- it MAY retain the bytes only as quarantined or non-authoritative local
  content

## 7. Authority Model

### 7.1 Control-plane authority

The privileged control plane is the authority boundary for all memory
operations that affect:

- prompt eligibility
- privileged model input
- capability execution
- approval decisions
- recall dereference of AMP-governed memory artifacts
- wake-state use for privileged execution

For those operations, the control plane MUST own:

- inspection and derivation from the active continuity stream
- memory artifact creation or acceptance
- classification
- dereference authorization
- recall resolution
- prompt inclusion decisions
- assembly of wake-state or recall-bundle projections for privileged use
- lifecycle transitions affecting availability or use

### 7.2 Unprivileged client behavior

An unprivileged client MAY maintain local continuity aids such as:

- cached renderings
- projected summaries
- local ranking hints
- user-authored notes
- optimistic UI projections

Those local objects are not authoritative AMP memory artifacts unless
and until the control plane validates and records them through the
memory artifact path.

Client-local memory views:

- MUST be treated as untrusted content
- MUST NOT create authority
- MUST NOT bypass dereference policy
- MUST NOT force prompt inclusion

### 7.3 Current implementation drift and target state

The current implementation mapping notes that wake-state build/load and
exact-key recall remain partly client-local today.

The target AMP state defined by this RFC is:

- authoritative memory dereference belongs to the control plane
- authoritative continuity derivation belongs to the control-plane
  inspector path
- client-local continuity data remains a projection or suggestion only
- any client-proposed memory content used in privileged flows must be
  revalidated and rebound through AMP-governed memory objects

## 8. Dereference and Inclusion Semantics

Memory operations are distinct and MUST NOT be collapsed into one
another.

### 8.1 Metadata inspection

Metadata inspection reveals bounded metadata such as:

- identifier
- subtype
- lineage
- classification
- storage state

A valid `memory_ref` MAY allow metadata inspection if policy permits.

### 8.2 Content dereference

Content dereference loads the memory artifact's stored derived content
or structured payload.

Content dereference:

- MUST be explicitly authorized
- MUST fail closed when bytes are unavailable
- MUST NOT be inferred from reference possession alone

### 8.3 Recall resolution

Recall resolution maps a selector such as a `resonate_key` to one or
more memory artifacts or other bounded recall results.

Recall resolution:

- is a governed dereference operation
- MUST be policy-evaluated
- MUST be bounded in output size
- MUST preserve provenance for the returned results

### 8.4 Projection reintroduction

A materialized wake-state result or recall bundle is a bounded
projection assembled from derived continuity forms and continuity
metadata.

Projection reintroduction rules:

- a projection MAY be reintroduced into active context only by governed
  reference or bounded inclusion
- a projection MUST preserve lineage to contributing distillates,
  resonate keys, memory refs, and source windows where applicable
- a projection MUST remain bounded and attributable
- a projection MUST NOT become policy authority, prompt authority, or
  current truth solely by being assembled or reintroduced

### 8.5 Prompt or execution inclusion

Prompt inclusion or execution inclusion is a separate governed step.

Even after content dereference succeeds:

- the resulting memory content MUST still pass inclusion policy
- inclusion MUST remain bounded and explainable
- inclusion MUST NOT be implied by exact-key match, artifact existence,
  or prior storage

## 9. Distillate Rules

A distillate MUST remain bounded and provenance-bearing.

Distillate rules:

- it MUST identify the bounded source set or bounded source window from
  which it was derived
- it MUST carry derivation classification
- it MUST NOT overwrite or replace the authoritative source history
- it MUST NOT be treated as current truth solely because it is durable
- it MUST preserve lineage sufficient to reconstruct the relevant source
  window or source-set membership

If a distillate is later pruned as bytes:

- lineage MUST remain
- references to the distillate remain references, not authority

## 10. Wake-State Rules

A wake state is a resumable continuity package, not a restored authority
context.

Its materialized use is a bounded projection assembled from distillates,
resonate keys, memory refs, and continuity metadata rather than a direct
reinstatement of prior active context.

Wake-state rules:

- loading a wake state MUST NOT recreate expired or revoked approvals
- loading a wake state MUST NOT recreate expired or terminated sessions
- loading a wake state MUST NOT recreate prior scoped tokens
- loading a wake state MAY return bounded memory refs, derived content,
  or continuity metadata
- loading a wake state MUST preserve lineage to the derived forms from
  which its projection is assembled
- a materialized wake-state projection MAY be reintroduced into active
  context only by governed reference or bounded inclusion
- a materialized wake-state projection MUST remain non-authoritative
- using a wake state in a privileged flow requires fresh policy
  evaluation at use time

Wake states SHOULD record:

- source event or artifact window
- source bindings
- build time
- build actor or authority path

## 11. Resonate Keys and Exact-Key Recall

### 11.1 Resonate-key semantics

A resonate key is a bounded memory artifact that stores a canonical
recall selector for eligible distillates or equivalent bounded derived
continuity results.

An eligible distillate is a distillate whose use remains permitted by:

- current policy
- current classification and scope
- current storage state
- current subject or session binding where applicable

The selector itself:

- is not content authority
- is not prompt authority
- is not a trust upgrade
- is not raw authority-bearing memory

### 11.2 Exact-key recall

Exact-key recall is a governed dereference operation over a
`resonate_key` or equivalent selector.

Exact-key recall MUST:

- validate the caller's authority and policy
- use the control plane's authoritative key resolution path for
  privileged use
- resolve only against eligible distillates or equivalent bounded
  derived continuity results
- return a bounded result set or a typed denial
- preserve provenance for returned artifacts or refs

Exact-key recall MUST NOT:

- bypass prompt-inclusion policy
- bypass storage-state checks
- bypass subject or session scoping rules
- treat a client-local key string as authoritative without control-plane
  validation

### 11.3 Client-suggested key resolution

An unprivileged client MAY propose a key or local match candidate.

For privileged use, the control plane MUST treat that proposal as:

- untrusted input
- a hint only

The control plane MUST perform its own authoritative resolution before
the result may affect privileged execution.

### 11.4 Recall bundles

A recall bundle is an ephemeral bounded projection assembled from one or
more eligible distillates, associated memory refs, resonate-key
resolution results, and continuity metadata.

A recall bundle:

- is not a new authority-bearing object class
- MAY be returned as a bounded result of governed recall
- MAY be reintroduced into active context only by governed reference or
  bounded inclusion
- MUST preserve lineage to contributing derived forms
- MUST NOT be treated as truth, permission, or self-authorizing memory

## 12. Morph-Local Versus AMP-Governed Memory

This RFC uses neutral terms, but the current product split can be stated
directly:

- Morph-local continuity views are allowed as UX projections
- Loopgate-governed memory use is required for privileged authority

Normative split:

- local client memory may assist rendering, ranking, and operator UX
- control-plane memory authority governs dereference, recall, prompt
  inclusion, and privileged reuse

If a current implementation still performs local continuity operations,
it MUST ensure that:

- those operations do not create ambient authority
- privileged use still flows through control-plane validation
- client-local continuity outputs remain non-authoritative until
  rederived or accepted by the control-plane inspector path
- local summaries, wake-state views, and recall hints are treated as
  content rather than authority

## 13. Outside AMP Today

The following behaviors may exist in current implementations but remain
outside AMP today unless and until a future AMP RFC standardizes them:

- client-local wake-state rendering caches
- client-local continuity ranking hints
- client-local exact-key recall hints or optimistic matches
- client-local projected summaries or continuity views
- user-authored local notes not yet rebound as memory artifacts

Outside AMP today means:

- these behaviors are non-authoritative
- these behaviors are implementation-local
- these behaviors MUST NOT by themselves justify dereference,
  prompt inclusion, or privileged execution inclusion
- any privileged use derived from them requires rebound through
  AMP-governed memory objects and policy evaluation

## 14. Required Observability

The following memory-related actions are security-relevant and SHOULD be
observable through the append-only event stream using RFC 0004 event
envelopes:

- control-plane inspector derivation from active stream to distillate,
  resonate key, or wake state
- memory artifact creation
- wake-state load for privileged use
- exact-key recall resolution for privileged use
- recall-bundle assembly or projection reintroduction for privileged use
- memory dereference denial
- prompt-inclusion acceptance or denial for memory-derived content

User-facing projections remain derived views. They do not replace the
authoritative event stream.

## 15. Current Implementation Mapping

The current codebase already partially implements this model:

- wake states
- distillates
- resonate keys
- bounded recall
- lineage-bearing continuity objects

The main implementation drift remains:

- wake-state build/load is still partly client-local
- exact-key recall is still partly client-local

This RFC defines the target authority placement for those operations.

## 16. Compact Schema Alignment

RFC 0007 provides the compact shared schema for `memory_ref`.

RFC 0007 does not replace the authority and dereference semantics in
this document.

## 17. Invariants

The following invariants apply:

- continuity is modeled as an append-only active stream
- the control-plane inspector is the derivation boundary between
  transient continuity flow and durable memory artifacts
- memory artifacts are derived artifacts, not authority grants
- distillates preserve lineage to bounded source windows or source sets
- wake states are memory artifacts, not standalone authority objects
- resonate keys are bounded retrieval handles for eligible distillates,
  not prompt authority or raw memory authority
- materialized wake-state projections and recall bundles are bounded
  projections assembled from derived continuity forms
- memory references do not imply dereference or inclusion rights
- exact-key recall is governed dereference
- projections may re-enter active context only by governed reference or
  bounded inclusion
- continuity artifacts and recall handles never become authority
- client-local continuity state is untrusted content
- stored memory does not become current truth by persistence alone
- loading memory never resurrects expired, revoked, or terminated
  authority

## 18. Future Work

Future AMP RFCs should define:

- bounded recall ranking semantics
- retention and pruning policies for memory artifacts
- portability rules for memory artifacts across authority boundaries
- richer memory artifact subtypes if the model later needs them
