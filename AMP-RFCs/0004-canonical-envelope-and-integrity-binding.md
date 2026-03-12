# AMP RFC 0004: Canonical Envelope and Integrity Binding

Status: draft  
Track: AMP (Authority Mediation Protocol)  
Authority: protocol design / target architecture  
Current implementation alignment: partial

## 1. Purpose

This document defines the canonical request envelope for AMP and the
integrity rules that bind a privileged request to:

- the negotiated AMP version
- the negotiated transport profile
- the control session
- the scoped token binding when required
- the exact request body bytes
- a freshness timestamp
- a replay-resistant nonce

The goal is to ensure that two independent implementations given the
same request inputs produce identical canonical bytes and therefore
identical request MACs.

This RFC also defines minimal denial and event envelopes so later RFCs
can refer to shared envelope fields without leaving cross-document
ambiguity.

## 2. Scope

This RFC applies to all privileged AMP requests after session
establishment.

This RFC does not define:

- the transport-specific carriage of envelope fields
- the session-establishment handshake beyond version/profile negotiation
- response integrity signatures or MACs
- object-specific schemas beyond the minimal denial/event envelopes

The local transport profile defined by RFC 0001 MUST use this canonical
envelope for privileged requests.

## 3. Non-Goals

This RFC does not define:

- a generic REST compatibility layer
- a public internet-facing signature format
- self-describing bearer tokens
- a replacement for object-specific schemas

## 4. Normative Language

The key words `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`, `SHOULD NOT`,
and `MAY` in this document are to be interpreted as normative
requirements.

## 5. Design Principles

The canonical envelope is built around the following principles:

- identical request inputs must produce identical canonical bytes
- integrity must bind the selected AMP version and transport profile
- integrity must bind session and scoped-token context
- replay protection must remain explicit and fail closed
- body bytes must be bound by hash rather than by transport framing
- raw scoped tokens and secret material must not be copied into derived
  binding fields
- denial and event records should share a minimal stable envelope shape

## 6. Version and Profile Negotiation

### 6.1 AMP version syntax

An `amp_version` is an exact ASCII version string in `major.minor`
format.

Rules:

- `major` and `minor` are non-negative decimal integers
- no leading plus sign is allowed
- leading zeroes are forbidden except for the value `0`
- examples of valid versions: `1.0`, `1.1`, `2.0`
- examples of invalid versions: `01.0`, `1`, `v1.0`, `1.0.0`

### 6.2 Transport profile syntax

A `transport_profile` is a lower-case ASCII identifier matching:

- first character: `a-z` or `0-9`
- remaining characters: `a-z`, `0-9`, `.`, or `-`

The RFC 0001 local transport profile identifier is:

- `local-uds-v1`

### 6.3 Negotiation rules

During session establishment:

- the client MUST advertise one or more exact `amp_version` values
- the client MUST advertise one or more exact `transport_profile`
  values
- the server MUST either select one exact `amp_version` and one exact
  `transport_profile` from the intersection or reject session
  establishment

Version selection rules:

- if multiple AMP versions overlap, the server MUST select the highest
  numeric version in the intersection
- clients SHOULD advertise versions in descending preference order

Transport profile selection rules:

- clients MUST advertise profiles in descending preference order
- if multiple transport profiles overlap, the server MUST select the
  first client-advertised profile that it also supports

The selected `amp_version` and `transport_profile` become part of the
control session and MUST be repeated in every canonical privileged
request.

### 6.4 Unsupported-version behavior

If session establishment fails because no exact AMP version or transport
profile overlaps:

- the server MUST fail closed
- the server MUST return a denial envelope with code
  `unsupported_version`
- the denial SHOULD include the server-supported versions and transport
  profiles

If a post-session privileged request carries:

- an unsupported `amp_version`
- an unsupported `transport_profile`
- a version or profile that does not match the bound session

then the server MUST:

- reject the request before action execution
- return denial code `unsupported_version`
- avoid fallback, coercion, or best-effort reinterpretation

## 7. Canonical Request Envelope

### 7.1 Required fields

Every privileged AMP request after session establishment MUST define the
following canonical fields:

- `amp_version`
- `transport_profile`
- `method`
- `path`
- `session_id`
- `token_binding`
- `timestamp_ms`
- `nonce`
- `body_sha256`
- `mac_algorithm`

The `mac_algorithm` value for canonical envelope v1 is fixed:

- `hmac-sha256`

### 7.2 Field semantics

The fields have the following meaning:

- `amp_version`
  - exact negotiated AMP version bound to the session
- `transport_profile`
  - exact negotiated transport profile bound to the session
- `method`
  - transport method or action verb as defined by the transport profile
- `path`
  - canonical absolute request path as defined below
- `session_id`
  - opaque control-session identifier issued by the control plane
- `token_binding`
  - derived binding value for the scoped token required by the action,
    or `none` if no scoped token is required
- `timestamp_ms`
  - client send time in Unix epoch milliseconds in UTC
- `nonce`
  - high-entropy client-generated replay-resistance nonce
- `body_sha256`
  - SHA-256 of the exact application request body bytes
- `mac_algorithm`
  - canonical MAC algorithm identifier

## 8. Field Validation and Normalization

### 8.1 General rules

All canonical envelope values MUST satisfy the following:

- values are UTF-8 strings
- field names are fixed lower-case ASCII names
- no field may appear more than once
- no leading or trailing whitespace is permitted in any field value
- field values are case-sensitive unless this RFC explicitly states
  otherwise

Transport profiles MAY carry additional metadata, but unsigned metadata:

- MUST NOT alter MAC verification
- MUST NOT alter authorization meaning
- MUST NOT rescue an otherwise invalid canonical envelope

### 8.2 `method`

The `method` value MUST:

- contain only upper-case ASCII letters `A-Z`
- be between 1 and 16 characters inclusive

Examples:

- valid: `POST`
- invalid: `post`
- invalid: `POST/1`

### 8.3 `path`

The `path` value MUST:

- begin with `/`
- use only ASCII characters
- omit query strings and fragments
- omit percent-encoding
- omit empty path segments other than the leading `/`
- omit `.` and `..` segments
- omit a trailing `/` unless the full path is exactly `/`

The following are invalid:

- `/v1/approvals?id=1`
- `/v1//approvals`
- `/v1/./approvals`
- `/v1/../approvals`
- `/v1/approvals/`

Canonical envelope v1 treats the path string as already normalized once
it passes these validation rules. Servers MUST reject non-conforming
paths rather than attempting permissive normalization.

### 8.4 `session_id`

The `session_id` value MUST:

- be an opaque ASCII token
- be between 1 and 128 characters inclusive
- contain only `A-Z`, `a-z`, `0-9`, `.`, `_`, or `-`

### 8.5 `token_binding`

The `token_binding` value MUST be one of:

- `none`
- `sha256:` followed by exactly 64 lower-case hexadecimal characters

If the action requires a scoped token:

- the client MUST compute `token_binding` as `sha256:` plus the
  lower-case hexadecimal SHA-256 digest of the exact token octets after
  transport decoding
- the raw scoped token MUST still be carried through the transport
  profile's normal token field

If the action does not require a scoped token:

- `token_binding` MUST be `none`

Servers MUST reject requests where the submitted scoped token and the
submitted `token_binding` do not match.

### 8.6 `timestamp_ms`

The `timestamp_ms` value MUST:

- be an unsigned decimal integer in Unix epoch milliseconds
- contain no leading plus sign
- contain no leading zeroes except for the value `0`

### 8.7 `nonce`

The `nonce` value MUST:

- be base64url without padding
- decode to at least 16 raw bytes

### 8.8 `body_sha256`

The `body_sha256` value MUST:

- be exactly 64 lower-case hexadecimal characters
- equal the SHA-256 digest of the exact application request body bytes

If the request body is empty:

- `body_sha256` MUST equal the SHA-256 of the zero-length byte string

### 8.9 `mac_algorithm`

Canonical envelope v1 supports exactly one `mac_algorithm` value:

- `hmac-sha256`

Servers MUST reject any other value with denial code `invalid_envelope`.

## 9. Canonical Byte Serialization

### 9.1 Exact serialization

Canonical request bytes for canonical envelope v1 are the UTF-8 bytes of
the following exact line sequence in the exact order shown below:

```text
amp-request-v1
amp-version:<amp_version>
transport-profile:<transport_profile>
method:<method>
path:<path>
session-id:<session_id>
token-binding:<token_binding>
timestamp-ms:<timestamp_ms>
nonce:<nonce>
body-sha256:<body_sha256>
mac-algorithm:<mac_algorithm>
```

Serialization rules:

- each line ends with a single line-feed byte `\n`
- there is no carriage return byte `\r`
- there is no blank line
- the final line also ends with `\n`
- field order MUST NOT change
- field names MUST appear exactly as shown above

### 9.2 Canonical request hash

The `canonical_request_sha256` is the lower-case hexadecimal SHA-256
digest of the canonical request bytes.

This derived value is not required as a request field, but servers MAY
use it in denials, events, and audit records as a stable request
binding.

## 10. Hash and MAC Behavior

### 10.1 Body hash

The `body_sha256` value MUST be computed over the exact application
payload bytes:

- after any transport framing is removed
- after any transport-level content decoding is complete
- before the payload is parsed into higher-level objects

For the RFC 0001 local transport profile, the body bytes are the exact
bytes presented to the application handler.

### 10.2 Request MAC

The request MAC for canonical envelope v1 is:

- algorithm: HMAC-SHA-256
- key: the server-issued session MAC key bound to the control session
- message: the canonical request bytes from Section 9

The transmitted request MAC value MUST be:

- base64url without padding
- the encoding of the 32-byte HMAC output

### 10.3 Session MAC key requirements

The session MAC key:

- MUST be cryptographically random
- MUST contain at least 32 raw bytes
- MUST be scoped to exactly one control session
- MUST NOT be reused across unrelated control sessions

If a server cannot preserve session MAC key continuity:

- it MUST invalidate the affected control sessions
- it MUST reject future requests using those sessions

## 11. Freshness, Nonce Scope, and Replay Protection

### 11.1 Freshness window

Unless a negotiated transport profile explicitly defines a different
window and binds that value to the session, the server MUST reject a
privileged request if:

- `abs(server_receive_time_ms - timestamp_ms) > 60000`

Freshness validation MUST occur before action execution.

### 11.2 Nonce scope

For canonical envelope v1, nonce uniqueness is scoped to:

- the `session_id`

A nonce reused within the same `session_id` MUST be rejected even if:

- the body differs
- the path differs
- the scoped token differs
- the earlier request was already denied for a semantic reason after the
  integrity checks passed

### 11.3 Replay cache requirements

The server MUST retain replay-detection state for accepted canonical
nonces for at least the lifetime of the bound control session.

If the server cannot guarantee nonce replay state for an active session:

- it MUST invalidate that session
- it MUST require a new session-establishment flow

Servers SHOULD insert a nonce into the replay cache only after:

- field validation succeeds
- MAC verification succeeds
- freshness validation succeeds

## 12. Verification Algorithm

For every privileged request after session establishment, the server
MUST perform the following steps in order:

1. validate that the carried `amp_version` and `transport_profile` are
   supported and match the bound session
2. validate all canonical field syntax rules
3. recompute `body_sha256` from the received application body bytes
4. rebuild the canonical request bytes exactly as defined in Section 9
5. recompute the request MAC using the bound session MAC key
6. compare the recomputed MAC to the carried request MAC using a
   constant-time comparison
7. validate timestamp freshness
8. validate nonce non-reuse within the bound `session_id`
9. validate the scoped token and its `token_binding` when the action
   requires a scoped token
10. only after all prior steps succeed, evaluate authorization and
    execute the requested action

If any step fails, the server MUST:

- fail closed
- avoid partial action execution
- return a typed denial where the transport state permits one

## 13. Minimal Denial Envelope

To avoid ambiguity across AMP RFCs, a minimal denial envelope contains:

- `kind`
- `code`
- `message`
- `retryable`
- `occurred_at_ms`
- `request_canonical_sha256`
- `amp_version`
- `transport_profile`

Field rules:

- `kind`
  - fixed value `denial`
- `code`
  - stable denial code such as `unsupported_version`,
    `invalid_envelope`, `integrity_failure`, `replay_detected`,
    `authorization_failed`, `policy_denied`, `validation_error`,
    `storage_state_mismatch`, or `unsupported_operation`
- `message`
  - operator-safe short text
  - MUST NOT contain secret-bearing values
- `retryable`
  - boolean
- `occurred_at_ms`
  - Unix epoch milliseconds in UTC
- `request_canonical_sha256`
  - the request hash when available, otherwise `none`
- `amp_version`
  - the selected AMP version if one exists, otherwise `none`
- `transport_profile`
  - the selected transport profile if one exists, otherwise `none`

For `unsupported_version` denials during session establishment, the
denial MAY additionally include:

- `supported_amp_versions`
- `supported_transport_profiles`

## 14. Minimal Event Envelope

To avoid ambiguity across AMP RFCs, a minimal event envelope contains:

- `kind`
- `event_id`
- `event_type`
- `occurred_at_ms`
- `subject_ref`
- `actor_ref`
- `causal_ref`
- `payload_sha256`
- `amp_version`

Field rules:

- `kind`
  - fixed value `event`
- `event_id`
  - stable event identifier unique within the authority boundary
- `event_type`
  - stable typed event name such as `approval.created`
- `occurred_at_ms`
  - Unix epoch milliseconds in UTC
- `subject_ref`
  - opaque subject identifier or object reference
- `actor_ref`
  - opaque actor or authority-path identifier
- `causal_ref`
  - causal binding such as a request hash, approval identifier, or prior
    event identifier, or `none`
- `payload_sha256`
  - hash of the structured event payload if one exists, otherwise `none`
- `amp_version`
  - the AMP version under which the event semantics were evaluated

The event envelope is a minimal common shape. It does not replace the
underlying append-only event log or object-specific event payloads.

## 15. Current Implementation Mapping

The current codebase already partially implements these ideas:

- signed request envelopes
- nonce and timestamp replay protection
- server-issued scoped tokens
- explicit denial codes

This RFC makes the canonical field set, byte serialization, and
negotiation behavior explicit and implementation-neutral.

## 16. Invariants

The following invariants apply:

- the same canonical field values produce the same canonical bytes
- the same canonical bytes under the same session MAC key produce the
  same request MAC
- AMP version and transport profile are integrity-bound
- request body bytes are integrity-bound by hash
- scoped-token context is integrity-bound when required
- replay protection is explicit and session-scoped
- integrity failure never falls back to permissive behavior
- denial and event envelopes remain typed and minimal

## 17. Future Work

Future AMP RFCs should define:

- response integrity and response/request binding
- algorithm agility and negotiated MAC suites beyond `hmac-sha256`
- transport-specific carriage mappings for additional AMP profiles
