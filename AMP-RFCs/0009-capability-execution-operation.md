# AMP RFC 0009: Capability Execution Operation

Status: draft  
Track: AMP (Authority Mediation Protocol)  
Authority: protocol design / target architecture  
Current implementation alignment: partial

## 1. Purpose

This document defines the protocol-level operation for requesting,
mediating, and returning the result of a capability execution through
an AMP control plane.

RFCs 0001 and 0004 define how to establish a session and sign a
request. RFC 0002 defines what a capability *is*. This RFC defines
how a client *invokes* one and what the control plane returns.

The goal is to make the capability execution exchange concrete enough
that a second implementation can build a working client without
reading product-specific source code.

## 2. Scope

This RFC applies to:

- the capability execution request envelope
- the capability execution response envelope
- structured result semantics
- denial semantics specific to capability execution
- approval-gated execution flow

This RFC does not define:

- specific capability schemas (those are registry entries)
- transport carriage details beyond the envelope shapes
- UI presentation of results
- model inference specifics (those are a capability class)

## 3. Normative Language

The key words `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`, `SHOULD NOT`,
and `MAY` in this document are to be interpreted as normative
requirements.

## 4. Design Principles

The capability execution operation is built around the following
principles:

- capabilities are mediated, not directly invoked
- the control plane decides whether to execute, deny, or gate behind
  approval
- arguments are structured and validated before execution
- results are bounded and classified
- denial is explicit and typed
- the client never receives raw provider credentials as part of a
  result

## 5. Capability Identifiers

A capability identifier MUST:

- be a stable ASCII string
- contain only `a-z`, `0-9`, `.`, `_`, or `-`
- be between 1 and 128 characters inclusive
- be unique within the control plane's capability registry

Capability identifiers are not self-describing authority. Possession
of a capability identifier does not imply execution permission.

Examples of valid capability identifiers:

- `http.request`
- `shell.exec`
- `quarantine.inspect`
- `quarantine.promote`
- `memory.recall`
- `model.inference`

## 6. Capability Execution Request

### 6.1 Request envelope

A capability execution request is a privileged AMP request using the
canonical envelope from RFC 0004.

The application request body MUST be a JSON object containing:

- `capability`
  - the capability identifier to execute
- `arguments`
  - a JSON object containing capability-specific input fields
- `request_id`
  - a client-generated opaque identifier for this execution request
  - MUST be unique per control session
  - MUST pass the identifier policy rules from RFC 0001

### 6.2 Argument rules

Arguments are untrusted input from the client.

The control plane MUST:

- validate argument structure against the registered capability schema
- reject unknown or unexpected fields
- reject arguments that fail policy checks before execution
- normalize arguments where the capability schema defines normalization
  rules

The control plane MUST NOT:

- trust argument values as authority
- pass raw arguments to external systems without validation
- allow argument fields to redefine the execution envelope or policy

### 6.3 Request integrity

The canonical request envelope MUST bind:

- the exact `capability` and `arguments` through `body_sha256`
- the scoped `capability_token` through `token_binding`
- the control session through `session_id`

The server MUST verify that the requested capability is within the
scope of the presented capability token before execution.

## 7. Execution Flow

### 7.1 Direct execution

If the capability and arguments pass policy evaluation and do not
require operator approval:

1. the control plane validates the request
2. the control plane executes the capability
3. the control plane returns a structured result or denial

### 7.2 Approval-gated execution

If the capability or arguments require operator approval:

1. the control plane validates the request
2. the control plane creates an `approval_request` per RFC 0005
3. the control plane returns a response indicating approval is pending
4. the operator reviews and decides per RFC 0005
5. on approval, the control plane executes the capability using the
   exact approved arguments
6. the control plane returns a structured result or denial

The pending response MUST include:

- `status`: `approval_pending`
- `approval_id`: the identifier of the created approval request
- `request_id`: echoed from the original request

### 7.3 Execution boundary

The control plane is the execution boundary. The client does not
execute capabilities directly.

The control plane:

- owns the connection to external systems
- owns provider credentials and secret material
- owns result filtering and redaction
- owns audit logging for the execution

## 8. Capability Execution Response

### 8.1 Success response

A successful execution response MUST contain:

- `status`
  - `ok`
- `request_id`
  - echoed from the request
- `capability`
  - echoed capability identifier
- `result`
  - a JSON object containing capability-specific output fields
- `result_classification`
  - a stable classification label for the result content
  - examples: `structured`, `bounded-text`, `artifact-ref`,
    `memory-ref`
- `occurred_at_ms`
  - execution completion time in Unix epoch milliseconds UTC

### 8.2 Denial response

A denied execution response MUST use the denial envelope from
RFC 0004 Section 13, extended with:

- `request_id`
  - echoed from the request when available
- `capability`
  - echoed capability identifier when available

### 8.3 Approval pending response

When execution is gated behind approval, the response MUST contain:

- `status`
  - `approval_pending`
- `request_id`
  - echoed from the request
- `capability`
  - echoed capability identifier
- `approval_id`
  - the identifier of the created approval request
- `approval_manifest_sha256`
  - the manifest hash for the approval

### 8.4 Result rules

Results are control-plane output, not raw external system output.

The control plane:

- MUST filter or redact secret-bearing material from results
- MUST classify results before returning them
- MUST NOT return raw provider API responses verbatim unless the
  capability schema explicitly defines pass-through semantics with
  appropriate classification
- SHOULD bound result size

Results are content, not authority. The client MUST NOT treat a
result as a permission grant, policy change, or trust elevation.

## 9. Capability-Specific Denial Codes

In addition to the general denial codes from RFC 0002 Section 13,
capability execution defines:

| Code | Meaning |
| --- | --- |
| `capability_not_found` | The requested capability identifier is not registered |
| `capability_not_in_scope` | The capability is not within the presented token's scope |
| `capability_arguments_invalid` | Arguments fail schema or policy validation |
| `capability_execution_failed` | Execution was attempted but the external operation failed |
| `capability_result_unavailable` | Execution succeeded but the result cannot be returned |

## 10. Request ID Uniqueness

The `request_id` serves two purposes:

- idempotency: the control plane MAY use `request_id` per session to
  detect duplicate execution requests
- correlation: the client uses `request_id` to match responses to
  requests, especially in approval-gated flows

Rules:

- the server MUST reject a `request_id` that has already been used
  within the same control session for a request that entered execution
  or approval flow
- the server MAY reject duplicate `request_id` values at any point
- the `request_id` MUST NOT be treated as a nonce replacement; the
  canonical envelope nonce from RFC 0004 remains required

## 11. Required Audit Events

Capability execution MUST produce the following audit events using the
event envelope from RFC 0004 Section 14:

- `capability.requested`
  - payload MUST include `request_id`, `capability`, redacted
    argument summary
- `capability.executed`
  - payload MUST include `request_id`, `capability`,
    `result_classification`
- `capability.denied`
  - payload MUST include `request_id`, `capability`, `denial_code`

If the execution is approval-gated, the approval events from
RFC 0005 Section 12 also apply.

## 12. Current Implementation Mapping

The current Loopgate implementation partially implements this
operation:

- `POST /v1/capabilities/execute` accepts a capability name and
  arguments
- arguments are currently `map[string]string`, narrower than the JSON
  object model defined here
- results use a product-specific `CapabilityResponse` type
- approval gating exists for capabilities that require it
- audit events are logged for execution and denial

This RFC provides the neutral protocol-level operation envelope that
the product-specific routes already approximate.

## 13. Invariants

The following invariants apply:

- capabilities are mediated by the control plane, not directly invoked
- capability identifiers are not authority
- arguments are untrusted input
- results are bounded, classified, and redacted
- the client never receives raw provider credentials in a result
- execution is integrity-bound through the canonical envelope
- denial is explicit and typed
- audit events are required for all execution attempts

## 14. Future Work

Future AMP RFCs should define:

- a capability registry format for declaring schemas, policy
  requirements, and approval rules
- streaming result semantics for long-running capabilities
- capability composition or chaining semantics if needed
- batch execution semantics if needed
