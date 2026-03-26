"""AMP (Authority Mediation Protocol) reference implementation.

Canonical envelope serialization, signing, and verification per AMP RFC 0004.
Canonical JSON serialization per AMP RFC 0007 Section 5.1.
"""

from amp.envelope import (
    CanonicalEnvelope,
    sign_request,
    verify_request,
    compute_body_sha256,
    compute_token_binding,
)
from amp.canonical_json import canonical_json_bytes, canonical_json_sha256
from amp.validation import (
    validate_method,
    validate_path,
    validate_session_id,
    validate_nonce,
    validate_timestamp_ms,
    validate_amp_version,
    validate_transport_profile,
)

__all__ = [
    "CanonicalEnvelope",
    "sign_request",
    "verify_request",
    "compute_body_sha256",
    "compute_token_binding",
    "canonical_json_bytes",
    "canonical_json_sha256",
    "validate_method",
    "validate_path",
    "validate_session_id",
    "validate_nonce",
    "validate_timestamp_ms",
    "validate_amp_version",
    "validate_transport_profile",
]
