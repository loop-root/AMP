**Last updated:** 2026-03-26

# AMP — Authority Mediation Protocol

AMP is an open, vendor-neutral protocol for constraining AI agents.

It defines how an unprivileged AI client interacts with a privileged
control plane so that agents can use tools, access resources, and carry
out tasks without being able to grant themselves permissions, exfiltrate
secrets, or take actions that nobody approved.

The core thesis: **authority is typed, explicit, and mediated -- never
inferred from natural language, references, or bearer possession
alone.**

## Who this is for

- **You want to build your own control plane** that governs what AI
  agents can do on a local machine.
- **You want to build a client** that talks to an AMP-compliant control
  plane.
- **You want to understand the security model** before trusting an
  agent orchestrator.

## The problem

AI agent frameworks are getting very good at letting models do things:
call APIs, read and write files, execute code, and chain actions
together across services. What is usually missing is a principled model
for deciding what an agent is actually allowed to do.

Today, most agent systems handle authority in one of three ways:

- **Give the model the keys.** API tokens, credentials, and tool access
  go directly into the model context. If the model is tricked or makes a
  bad call, there is no structural barrier between the mistake and the
  damage.
- **Filter the output.** A regex or classifier tries to block dangerous
  actions after the fact. This is fragile and easy to route around.
- **Ask the model to be careful.** A system prompt is not a security
  control.

None of these approaches separates the agent's ability to request an
action from the authority to execute it. AMP is an attempt to make that
separation explicit.

## What AMP does

AMP introduces a control plane between the agent and the resources it
acts on. The control plane, not the model, is the authority boundary.

The core principles:

- **Natural language never creates authority.** Authority comes from
  typed policy, scoped tokens, and explicit approval, never from text.
- **Model output is content, not commands.** Tool calls, memory,
  summaries, and status text are untrusted input until validated.
- **Secrets never cross the boundary.** API keys, tokens, and
  credentials stay in the control plane and are not exposed to the
  model.
- **Every action is mediated.** Tool execution flows through policy
  evaluation, capability scoping, and explicit approval when required.
- **Everything is auditable.** Security-relevant actions produce
  append-only, attributable records.

## How it works

AMP defines a layered model:

1. **Transport** -- a local Unix domain socket or equivalent
   machine-local channel with peer credential binding.
2. **Sessions** -- the client establishes a control session with
   negotiated protocol version, transport profile, and a server-issued
   MAC key.
3. **Capabilities** -- tools and actions are registered as typed
   capabilities with schemas, policy requirements, and approval gates.
4. **Approvals** -- actions that require human review enter an explicit,
   bounded approval workflow.
5. **Artifacts and references** -- external data is quarantined by
   default; references are identifiers, not trust grants.
6. **Memory and continuity** -- memory remains derived content rather
   than authority.

## Quick-start for implementers

If you want to build a working AMP client from scratch, read these in
order:

1. **[RFC 0001: Local Transport Profile](./AMP-RFCs/0001-local-transport-profile.md)**  
   how to connect, establish a session, and recover from failures.
2. **[RFC 0004: Canonical Envelope and Integrity Binding](./AMP-RFCs/0004-canonical-envelope-and-integrity-binding.md)**  
   how to sign every privileged request. Section 15 contains the primary
   request-signing vectors.
3. **[RFC 0009: Capability Execution Operation](./AMP-RFCs/0009-capability-execution-operation.md)**  
   how to invoke a capability and handle the response.
4. **[RFC 0005: Approval Lifecycle and Decision Binding](./AMP-RFCs/0005-approval-lifecycle-and-decision-binding.md)**  
   how approval-gated execution works.

If you want to build a control plane, also read:

5. **[RFC 0002: Core Object Model](./AMP-RFCs/0002-core-object-model.md)**  
   object vocabulary, denial registry, event registry, and authority
   rules.
6. **[RFC 0003: Artifact and Reference Model](./AMP-RFCs/0003-artifact-and-reference-model.md)**  
   quarantine, promotion, lineage, dereference, and storage-state
   behavior.
7. **[RFC 0006: Continuity and Memory Authority](./AMP-RFCs/0006-continuity-and-memory-authority.md)**  
   memory authority, continuity derivation, and governed reintroduction
   into active context.

## Specification

AMP is defined by the following RFC set:

| RFC | Title | Focus |
| --- | --- | --- |
| [0001](./AMP-RFCs/0001-local-transport-profile.md) | Local Transport Profile | Unix socket transport, peer binding, sessions, request/response operation framing |
| [0002](./AMP-RFCs/0002-core-object-model.md) | Core Object Model | Sessions, capabilities, tokens, approvals, artifacts, denials, events |
| [0003](./AMP-RFCs/0003-artifact-and-reference-model.md) | Artifact and Reference Model | Quarantine, promotion, lineage, dereference, storage-state rules |
| [0004](./AMP-RFCs/0004-canonical-envelope-and-integrity-binding.md) | Canonical Envelope and Integrity Binding | Request signing, MAC computation, freshness, replay protection, test vectors |
| [0005](./AMP-RFCs/0005-approval-lifecycle-and-decision-binding.md) | Approval Lifecycle and Decision Binding | Approval states, manifest binding, concurrency, race semantics |
| [0006](./AMP-RFCs/0006-continuity-and-memory-authority.md) | Continuity and Memory Authority | Continuity stream, derivation boundary, memory authority, recall semantics |
| [0007](./AMP-RFCs/0007-core-envelopes-and-compact-schemas.md) | Core Envelopes and Compact Schemas | Shared object shapes for denials, events, references, approvals |
| [0008](./AMP-RFCs/0008-open-issues-gaps-and-assumptions.md) | Open Issues, Gaps, and Assumptions | Non-normative gap register and challenged assumptions |
| [0009](./AMP-RFCs/0009-capability-execution-operation.md) | Capability Execution Operation | Protocol-level capability invocation and response semantics |

Normative rule: **RFC 0004 wins over RFC 0001** if canonical request
integrity wording conflicts.

## Reference material

- **[Conformance Checklist](./conformance/local-uds-v1-checklist.md)**  
  blunt checklist for claiming `local-uds-v1` alignment.
- **[Conformance test vectors v1](./conformance/test-vectors-v1.md)**  
  UTF-8 hex dumps and canonical JSON digests for verifying
  implementations.
- **[AMP Implementation Mapping](./design_overview/amp_implementation_mapping.md)**  
  descriptive bridge between the neutral AMP RFCs and the current
  product implementation.

## Reference implementations

- **[Python reference implementation](./reference/python/README.md)**  
  canonical envelope serialization, signing, verification, canonical
  JSON helpers, and tests against the published conformance vectors.

## Relationship to MCP

AMP and MCP solve different problems. MCP provides tool connectivity.
AMP provides authority mediation over those tools: whether a call is
allowed, what arguments are permitted, whether approval is required, and
what evidence is preserved afterward.

The two protocols are complementary. A system can use MCP for tool
discovery and AMP for authority enforcement.

## Status

AMP is in active draft. The RFCs are specific enough to implement
against, but the spec set is still evolving and the gap register remains
open.

## Release gate

Before claiming **"aligned with AMP local-uds-v1"**, complete the
[local-uds-v1 checklist](./conformance/local-uds-v1-checklist.md) or
document explicit waivers with linked RFCs or issues. RFC 0008 tracks
known gaps that may block a full claim.

## Scope boundary

- **Here (this repo):** neutral names, transport profile, object model,
  integrity, approvals, memory authority, capability execution,
  conformance helpers, and reference implementations.

## Contributing

If you find ambiguity, missing edge cases, or places where you had to
guess, that is a spec bug. Open an issue or a PR against the RFC or
helper document that was unclear.
