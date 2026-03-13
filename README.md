# AMP Docs

# AMP — Authority Mediation Protocol

AMP is an open protocol for constraining AI agents.

It defines how an unprivileged AI client interacts with a privileged control plane so that agents can use tools, access resources, and carry out tasks — without being able to grant themselves permissions, exfiltrate secrets, or take actions that nobody approved.

## The problem

AI agent frameworks are getting very good at letting models *do things*. They can call APIs, read and write files, execute code, and chain actions together across services. What’s missing is a principled model for deciding what an agent is *allowed* to do.

Today, most agent systems handle authority in one of three ways:

- **Give the model the keys.** API tokens, credentials, and tool access go directly into the model’s context. The model decides what to call, with what arguments, and the system hopes the model behaves. If the model is tricked by a malicious prompt or simply makes a bad judgment call, there’s no structural barrier between the mistake and the damage.
- **Filter the output.** A regex or classifier inspects what the model wants to do and tries to block dangerous actions. This is inherently fragile — it’s an arms race between the filter and the model’s ability to express the same intent in different ways.
- **Ask the model to be careful.** System prompts instruct the model not to misuse its access. This is not a security control. It’s a suggestion.

None of these approaches separate the agent’s *ability to request* an action from the *authority to execute* it. That separation is the foundation of every serious access control system in computing — and it’s almost entirely absent from the AI agent ecosystem.

## What AMP does

AMP introduces a control plane between the agent and the resources it acts on. The control plane — not the model — is the authority boundary.

The core principles:

- **Natural language never creates authority.** A model cannot gain permissions by asking for them, claiming to have them, or describing them in its output. Authority comes from typed policy, scoped tokens, and explicit approval — never from text.
- **Model output is content, not commands.** Everything an AI produces — tool calls, memory, summaries, status text — is treated as untrusted input that must be validated before it affects anything.
- **Secrets never cross the boundary.** API keys, tokens, and credentials are stored and served by the control plane directly to providers. They never appear in the model’s context, prompt, or output. The model cannot exfiltrate what it cannot see.
- **Every action is mediated.** Tool execution flows through policy evaluation, capability scoping, and (where required) explicit human approval before anything happens. Denials are typed and auditable. There is no silent fallback to permissive behavior.
- **Everything is auditable.** Security-relevant actions produce append-only, hash-chained audit events. The audit trail is tamper-evident and exists independently of the model’s memory or the UI’s rendering.

## How it works

AMP defines a layered model:

1. **Transport** — A local Unix domain socket (or equivalent machine-local channel) with peer credential binding. The control plane is not exposed to the network by default.
1. **Sessions** — The client establishes a control session with negotiated protocol version, transport profile, and a server-issued MAC key. Every subsequent request is HMAC-signed, timestamped, and nonce-protected against replay.
1. **Capabilities** — Tools and actions are registered as typed capabilities with schemas, policy requirements, and approval gates. The control plane evaluates policy and issues scoped, short-lived tokens. Bearer possession alone is never sufficient.
1. **Approvals** — Actions that require human review enter an explicit approval workflow. Approvals are single-use, time-bounded, and cryptographically bound to the exact action being approved via a canonical manifest hash. An operator’s “yes” applies only to the specific request they reviewed — not to a substituted or modified version.
1. **Artifacts and references** — External data entering the system (API responses, file contents, remote payloads) is quarantined by default. References to artifacts are identifiers, not trust grants. Promotion to trusted status creates a new derived artifact — it never blesses the source in place.
1. **Memory and continuity** — Agent memory (distillates, wake states, recall keys) is treated as derived content, not authority. Loading a previous session’s memory does not restore expired permissions, revive terminated sessions, or bypass current policy.

## Specification

AMP is defined by a series of RFCs:

|RFC                                                                |Title                                   |Focus                                                                |
|-------------------------------------------------------------------|----------------------------------------|---------------------------------------------------------------------|
|[0001](./AMP-RFCs/0001-local-transport-profile.md)                 |Local Transport Profile                 |Unix socket transport, peer binding, authentication layers           |
|[0002](./AMP-RFCs/0002-core-object-model.md)                       |Core Object Model                       |Sessions, capabilities, tokens, approvals, artifacts, denials, events|
|[0003](./AMP-RFCs/0003-artifact-and-reference-model.md)            |Artifact and Reference Model            |Quarantine, promotion, lineage, dereference rules                    |
|[0004](./AMP-RFCs/0004-canonical-envelope-and-integrity-binding.md)|Canonical Envelope and Integrity Binding|Request signing, MAC computation, replay protection, test vectors    |
|[0005](./AMP-RFCs/0005-approval-lifecycle-and-decision-binding.md) |Approval Lifecycle and Decision Binding |Approval states, manifest binding, concurrency, race semantics       |
|[0006](./AMP-RFCs/0006-continuity-and-memory-authority.md)         |Continuity and Memory Authority         |Memory artifacts, wake states, recall, derivation boundaries         |
|[0007](./AMP-RFCs/0007-core-envelopes-and-compact-schemas.md)      |Core Envelopes and Compact Schemas      |Shared object shapes for denials, events, references, approvals      |

A [conformance checklist](./conformance/local-uds-v1-checklist.md) is available for implementers targeting the `local-uds-v1` transport profile.

## Reference implementation

[Morph](https://github.com/loop-root/morph) is a reference implementation of AMP built around a local orchestrator (Morph) and a local control plane (Loopgate). It implements the local transport profile, signed request envelopes, policy-gated capability execution, the approval workflow with manifest binding, quarantine and promotion, hash-chained audit, and morphling (subordinate agent) lifecycle management.

## Relationship to MCP

AMP and MCP (Model Context Protocol) solve different problems. MCP provides tool connectivity — it lets models discover and call tools across services. AMP provides authority mediation — it controls *whether* a model is allowed to call a tool, *what* it can pass as arguments, *whether* a human needs to approve it first, and *what evidence* is preserved afterward.

The two protocols are complementary. An agent system could use MCP for tool discovery and AMP for authority enforcement over those tools.

## Status

AMP is in early draft. The RFCs are stable enough to implement against, and the reference implementation demonstrates that the core model works, but the specification is still evolving. Feedback, criticism, and independent implementations are welcome.

## Design documents

- [AMP Implementation Mapping](./design_overview/amp_implementation_mapping.md) — how the current reference implementation maps onto the AMP RFCs, including known gaps and intentional drift

## Contributing

AMP is an open specification. If you find a gap, an ambiguity, or a flaw in the protocol design, open an issue or submit a pull request. The goal is a protocol that any agent framework can adopt — contributions that improve clarity, security, or implementability are especially valued.

## License



## Contents

- [AMP Implementation Mapping](./design_overview/amp_implementation_mapping.md)
- [AMP RFC 0001: Local Transport Profile](./AMP-RFCs/0001-local-transport-profile.md)
- [AMP RFC 0002: Core Object Model](./AMP-RFCs/0002-core-object-model.md)
- [AMP RFC 0003: Artifact and Reference Model](./AMP-RFCs/0003-artifact-and-reference-model.md)
- [AMP RFC 0004: Canonical Envelope and Integrity Binding](./AMP-RFCs/0004-canonical-envelope-and-integrity-binding.md)
- [AMP RFC 0005: Approval Lifecycle and Decision Binding](./AMP-RFCs/0005-approval-lifecycle-and-decision-binding.md)
- [AMP RFC 0006: Continuity and Memory Authority](./AMP-RFCs/0006-continuity-and-memory-authority.md)
- [AMP RFC 0007: Core Envelopes and Compact Schemas](./AMP-RFCs/0007-core-envelopes-and-compact-schemas.md)
- [AMP local-uds-v1 Conformance Checklist](./conformance/local-uds-v1-checklist.md)

## Scope

Keep neutral protocol and object-model documents here. Product-specific runtime
docs, operator docs, and implementation invariants stay in the Morph repo.
