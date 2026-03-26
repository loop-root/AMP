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
transport and binding rules for the current local deployment mode.

RFC 0004 is authoritative for:

- the canonical request envelope
- canonical request byte serialization
- request MAC calculation
- freshness rules
- nonce replay semantics

If wording in this RFC and RFC 0004 ever drifts on canonical request
integrity behavior, RFC 0004 wins.

### 1.1 Companion: Morph Loopgate token RFC

The Morph repository carries a **product-local** articulation of the same boundary: [RFC 0001: Loopgate Token and Request Integrity Policy](../../rfcs/0001-loopgate-token-policy.md) (HTTP on Unix socket, session open, capability/approval tokens, signing). It MUST NOT contradict **AMP RFC 0004** on canonical request bytes or MAC semantics. Use the AMP RFCs for neutral interop language; use the Morph RFC for route-level and denial-code detail in Loopgate today.

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

RFC 0004 defines the exact canonical field set, canonical byte sequence,
request MAC algorithm, freshness window, and nonce replay rules for that
envelope.

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

## 7. Session Establishment

### 7.1 Overview

Session establishment is the protocol operation that creates a new
control session between an unprivileged client and the privileged
control plane.

Session establishment:

- is the first privileged exchange on a new connection
- is not itself protected by a signed request envelope because no
  session MAC key exists yet
- produces the control session identifier, the session MAC key, and
  any scoped tokens required for subsequent requests
- binds the session to the negotiated AMP version and transport profile

### 7.2 Client request

The client sends a session-open request containing:

- `amp_versions`
  - ordered list of exact `amp_version` strings the client supports,
    in descending preference order
- `transport_profiles`
  - ordered list of exact `transport_profile` strings the client
    supports, in descending preference order
- `actor`
  - opaque client-chosen label identifying the requesting client
  - MUST pass the identifier policy rules in Section 12
- `requested_capabilities`
  - list of capability identifiers the client requests authorization
    for

The session-open request does not carry a signed envelope, nonce, or
timestamp. Transport-level peer binding (Section 6.1) provides the
initial trust anchor.

### 7.3 Server response

If session establishment succeeds, the server returns:

- `session_id`
  - opaque control-session identifier
- `mac_key`
  - base64url-encoded session MAC key (at least 32 raw bytes)
  - the client MUST treat this value as secret material
  - the server MUST NOT log or persist this value outside volatile
    session state
- `amp_version`
  - the exact negotiated AMP version
- `transport_profile`
  - the exact negotiated transport profile
- `capability_token`
  - opaque scoped token for capability execution
- `approval_token`
  - opaque scoped token for approval decisions
- `expires_at_ms`
  - session expiry time in Unix epoch milliseconds UTC

Version and profile selection follows RFC 0004 Section 6.3.

### 7.4 Failure

If session establishment fails, the server MUST return a denial
envelope (RFC 0004 Section 13).

Common denial codes for session establishment:

- `unsupported_version` — no AMP version or transport profile overlap
- `authorization_failed` — peer identity not authorized
- `policy_denied` — policy denies session creation
- `validation_error` — malformed request fields

The server MUST NOT issue a session or MAC key on failure.

### 7.5 Session binding

After successful establishment, all subsequent privileged requests on
this session MUST:

- use the negotiated `amp_version` and `transport_profile` in the
  canonical envelope
- use the issued `session_id` in the canonical envelope
- be signed with the issued `mac_key`

The server MUST reject requests where the carried `amp_version` or
`transport_profile` does not match the session-bound values.

## 8. Request Rules

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

## 9. Response Rules

Responses are trusted only as control-plane responses from the local
authority boundary.

Responses must:

- remain bounded
- avoid secret-bearing data
- preserve explicit denial/error semantics
- preserve classification and provenance metadata where applicable

### 9.1 Request-response correlation

Every response to a privileged request SHOULD include a
`request_id` field containing a stable identifier that the client
can use to correlate the response with the originating request.

The `request_id` MAY be:

- the `canonical_request_sha256` from RFC 0004 Section 9.2
- an opaque server-assigned identifier returned alongside the response
- the client-supplied `nonce` echoed back

The server MUST NOT include secret-bearing material in the
`request_id`.

### 9.2 Response integrity

This profile does not require response signatures or MACs in v1.

Clients SHOULD treat control-plane responses as authoritative for the
local boundary but MUST NOT extend that trust to content fields that
originate from model output, tool output, or external sources.

Future AMP versions may define:

- response MAC or signature binding
- stronger transport-level response attestation

## 10. Secrets and Sensitive Material

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

## 11. Artifact and Reference Semantics

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

## 12. Identifier Policy

Identifiers used in session establishment and protocol objects MUST be
inert labels.

An identifier value MUST:

- contain only ASCII letters `A-Z`, `a-z`, digits `0-9`, `.`, `_`,
  or `-`
- be between 1 and 128 characters inclusive
- not contain path traversal sequences (`.`, `..`, `/`, `\`)
- not contain shell metacharacters or template syntax

The server MUST reject identifiers that fail these rules with denial
code `validation_error`.

## 13. Denials and Errors

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

## 14. Client Recovery

### 14.1 Session loss

When a client receives a denial with code `session_invalidated` or
detects that the transport connection has been lost:

- the client MUST discard the session MAC key, session identifier,
  and all scoped tokens bound to the lost session
- the client MUST NOT reuse nonces or MAC keys from the lost session
- the client MAY attempt to establish a new session

### 14.2 Back-off

Clients SHOULD implement exponential back-off when session
establishment fails repeatedly.

Recommended minimum:

- initial delay: 500 milliseconds
- maximum delay: 30 seconds
- jitter: randomized within each delay interval

Clients MUST NOT retry session establishment in a tight loop.

### 14.3 State after recovery

A new session is a fresh authority context.

After re-establishment:

- prior scoped tokens are invalid
- prior approval states are not carried forward
- prior nonces are not reusable
- prior capability results may be stale
- the client SHOULD refresh any cached projection state

## 15. Versioning

The local transport profile should be versioned explicitly.

Versioning should allow:

- forward-compatible transport negotiation
- explicit rejection of unsupported future semantics

This RFC defines the first local profile only.

## 16. Current Implementation Mapping

The current codebase already partially implements this profile:

- Unix domain socket transport
- local peer credential binding where supported
- control sessions
- opaque scoped tokens
- signed request envelopes
- nonce and timestamp replay protection

RFC 0004 now makes the canonical integrity behavior explicit.

The protocol itself is not yet formalized as a standalone named layer.

This RFC provides that naming and boundary.

## 17. Invariants

The following invariants apply to this profile:

- natural language never creates authority
- authority is typed, explicit, and mediated
- the control plane is the privileged boundary
- bearer possession alone is insufficient
- secrets do not cross the protocol boundary by default
- requests fail closed on integrity failure
- local transport does not imply full local trust
- references are not content and are not trust escalation

## 18. Future Work

Future AMP RFCs should define:

- local browser/bridge profile
- remote transport profile if ever needed
- response integrity profile
- transport carriage details for additional profiles
