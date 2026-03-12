# AMP RFC 0001: Local Transport Profile

Status: draft  
Track: AMP (Authority Mediation Protocol)  
Authority: protocol design / target architecture  
Current implementation alignment: partial

## 1. Purpose

This document defines the first transport profile for the Authority
Mediation Protocol (AMP).

The local transport profile specifies how an unprivileged local client
communicates with a privileged local control plane over a trusted
machine-local channel.

This RFC does not define the full AMP object model. It defines the
transport and integrity rules for the current local deployment mode.

## 2. Scope

This profile applies to local communication between:

- an operator shell
- a local bridge or UI adapter
- a local worker runtime
- a local privileged control plane

This profile assumes:

- a single host
- machine-local communication only
- no public network exposure
- the control plane is the authority boundary

## 3. Non-Goals

This RFC does not define:

- a remote network transport profile
- browser transport directly to the control plane
- a public internet-facing API
- self-describing bearer tokens
- a generic REST compatibility layer
- transport-independent object semantics beyond what is required here

## 4. Threat Model

This transport profile assumes:

- same-user local processes remain in scope as realistic attackers
- local request forgery is a real concern
- replay attacks on captured local requests are a real concern
- local transport integrity matters even when the channel is not public

This profile does not assume:

- the local machine is fully trusted
- any local process of the same user should automatically gain authority

## 5. Transport

The local transport profile uses:

- Unix domain sockets as the primary transport

The transport profile identifier for this RFC is:

- `local-uds-v1`

The transport is expected to remain:

- local-only
- non-routable
- non-public
- controlled by filesystem permissions

The transport endpoint must not be exposed as a public TCP listener by
default.

## 6. Authentication and Binding

The local transport profile uses a layered authentication model:

1. local transport binding
2. control session binding
3. request-integrity binding
4. scoped capability or approval token binding

The control plane must not rely on bearer possession alone.

### 6.1 Local peer binding

The control plane must bind the session to the local peer identity
available from the operating system where supported.

The peer identity is used to reduce reuse of stolen local tokens across
unrelated local processes.

### 6.2 Control sessions

The control plane issues a local control session after successful local
session establishment.

The control session is:

- opaque
- short-lived
- server-issued
- server-validated
- not a provider credential

### 6.3 Request integrity

Every privileged request must be integrity-protected.

The current local profile uses a server-issued session MAC key and a
signed request envelope.

The signed request envelope must bind:

- method
- path
- control session identifier
- timestamp
- nonce
- request body hash

Unsigned or replayed privileged requests must fail closed.

### 6.4 Scoped tokens

Capability and approval tokens are:

- opaque
- scoped
- short-lived
- server-validated
- never equivalent to provider credentials

Tokens must not be treated as self-describing authority grants.

## 7. Request Rules

A privileged local request must include:

- a valid control session identifier
- a valid signed request envelope
- the required scoped token for the action class

Examples of action classes:

- capability execution
- approval review or decision
- quarantine inspection
- promotion
- model inference

The server must reject:

- missing signatures
- invalid signatures
- expired timestamps
- replayed nonces
- invalid or expired scoped tokens
- requests outside the token's scope

## 8. Response Rules

Responses are trusted only as control-plane responses from the local
authority boundary.

Responses must:

- remain bounded
- avoid secret-bearing data
- preserve explicit denial/error semantics
- preserve classification and provenance metadata where applicable

This profile does not require response signatures in v1.

Future AMP work may define:

- response binding to request identifiers
- response MAC/signature integrity
- stronger transport-level response attestation

## 9. Secrets and Sensitive Material

The local transport profile must not be used to export raw provider
credentials, refresh tokens, client secrets, or raw secure-store
material to unprivileged clients.

The control plane may return:

- structured execution results
- denial objects
- bounded metadata
- artifact references
- memory references

The control plane must not return:

- raw model provider API keys
- raw provider access tokens
- refresh tokens
- private key material
- secure-store contents

## 10. Artifact and Reference Semantics

The local transport profile may carry references to:

- quarantine artifacts
- derived artifacts
- memory artifacts
- wake states
- resonate keys

References are:

- identifiers
- not raw content
- not trust escalation
- not authorization by themselves

Dereference rules remain governed by control-plane policy.

## 11. Denials and Errors

The protocol must favor explicit, typed denials over vague failures.

Denials should distinguish:

- authorization failure
- policy denial
- invalid request
- integrity failure
- replay detection
- missing source bytes
- storage-state mismatch
- unsupported operation

The transport must not silently fall back to permissive behavior when a
validation or integrity rule fails.

## 12. Versioning

The local transport profile should be versioned explicitly.

Versioning should allow:

- forward-compatible transport negotiation
- explicit rejection of unsupported future semantics

This RFC defines the first local profile only.

## 13. Current Implementation Mapping

The current codebase already partially implements this profile:

- Unix domain socket transport
- local peer credential binding where supported
- control sessions
- opaque scoped tokens
- signed request envelopes
- nonce and timestamp replay protection

The protocol itself is not yet formalized as a standalone named layer.

This RFC provides that naming and boundary.

## 14. Invariants

The following invariants apply to this profile:

- natural language never creates authority
- authority is typed, explicit, and mediated
- the control plane is the privileged boundary
- bearer possession alone is insufficient
- secrets do not cross the protocol boundary by default
- requests fail closed on integrity failure
- local transport does not imply full local trust
- references are not content and are not trust escalation

## 15. Future Work

Future AMP RFCs should define:

- local browser/bridge profile
- remote transport profile if ever needed
- response integrity profile
- transport carriage details for additional profiles
