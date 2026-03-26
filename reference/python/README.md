# amp-protocol (Python reference)

Reference implementation of the [AMP (Authority Mediation Protocol)](../../README.md)
canonical envelope, signing, and verification.

This library implements:

- **Canonical envelope serialization** per RFC 0004 Section 9
- **HMAC-SHA256 request signing** per RFC 0004 Section 10
- **Request verification** with freshness and replay detection per RFC 0004 Section 12
- **Canonical JSON serialization** per RFC 0007 Section 5.1
- **Field validation** per RFC 0004 Section 8
- **Conformance tests** against the normative test vectors in RFC 0004 Section 15

## Install

```bash
pip install -e .

# with test dependencies
pip install -e ".[test]"
```

## Usage

### Sign a request

```python
from amp import (
    CanonicalEnvelope,
    sign_request,
    compute_body_sha256,
    compute_token_binding,
    generate_nonce,
    generate_timestamp_ms,
)

body = b'{"action":"quarantine.inspect","target_ref":"artifact:amp:1234"}'
token = b"tok_your_capability_token_here"

envelope = CanonicalEnvelope(
    amp_version="1.0",
    transport_profile="local-uds-v1",
    method="POST",
    path="/v1/capabilities/execute",
    session_id="your_session_id",
    token_binding=compute_token_binding(token),
    timestamp_ms=generate_timestamp_ms(),
    nonce=generate_nonce(),
    body_sha256=compute_body_sha256(body),
)

mac_key = b"\x00" * 32  # your actual session MAC key
request_mac = sign_request(envelope, mac_key)
```

### Verify a request

```python
from amp import CanonicalEnvelope, verify_request

seen_nonces: set[str] = set()

try:
    verify_request(
        envelope,
        mac_key,
        presented_mac=request_mac,
        server_receive_time_ms=1735689600123,
        seen_nonces=seen_nonces,
    )
except Exception as e:
    print(f"Denied: {e}")
```

### Canonical JSON for audit hashing

```python
from amp import canonical_json_bytes, canonical_json_sha256

denial = {
    "kind": "denial",
    "code": "policy_denied",
    "message": "write outside allowed root",
    "retryable": False,
    "occurred_at_ms": 1735689601123,
    "request_canonical_sha256": "none",
    "amp_version": "1.0",
    "transport_profile": "local-uds-v1",
}

raw_bytes = canonical_json_bytes(denial)
digest = canonical_json_sha256(denial)
```

## Run tests

```bash
pytest tests/ -v
```

The test suite verifies against the normative test vectors from
RFC 0004 Section 15 and RFC 0007 Section 5.1. If a test fails,
the implementation is non-conformant.

## What this library does NOT do

- Session establishment (that's transport-specific)
- HTTP/socket transport (that's your client)
- Capability execution (that's your control plane)
- Token storage or management
- Nonce persistence (bring your own store)

This is the signing and verification core. Wrap it in your transport layer.

## License

MIT
