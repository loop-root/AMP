"""Canonical envelope serialization, signing, and verification per AMP RFC 0004."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from dataclasses import dataclass

from amp.validation import (
    EnvelopeValidationError,
    validate_amp_version,
    validate_body_sha256,
    validate_mac_algorithm,
    validate_method,
    validate_nonce,
    validate_path,
    validate_session_id,
    validate_timestamp_ms,
    validate_token_binding,
    validate_transport_profile,
)

_ENVELOPE_V1_HEADER = "amp-request-v1"
_MAC_ALGORITHM = "hmac-sha256"
_DEFAULT_FRESHNESS_MS = 60_000


def compute_body_sha256(body: bytes) -> str:
    """SHA-256 of exact application body bytes, lowercase hex."""
    return hashlib.sha256(body).hexdigest()


def compute_token_binding(token_octets: bytes) -> str:
    """Compute token_binding as 'sha256:<hex>' from raw scoped token bytes."""
    digest = hashlib.sha256(token_octets).hexdigest()
    return f"sha256:{digest}"


def generate_nonce(raw_bytes: int = 16) -> str:
    """Generate a cryptographic nonce: base64url without padding, >= 16 raw bytes."""
    raw = os.urandom(raw_bytes)
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def generate_timestamp_ms() -> str:
    """Current time as Unix epoch milliseconds string."""
    return str(int(time.time() * 1000))


@dataclass(frozen=True)
class CanonicalEnvelope:
    """Immutable representation of an AMP canonical request envelope.

    All fields are pre-validated strings matching RFC 0004 Section 7-8.
    """

    amp_version: str
    transport_profile: str
    method: str
    path: str
    session_id: str
    token_binding: str
    timestamp_ms: str
    nonce: str
    body_sha256: str
    mac_algorithm: str = _MAC_ALGORITHM

    def __post_init__(self) -> None:
        validate_amp_version(self.amp_version)
        validate_transport_profile(self.transport_profile)
        validate_method(self.method)
        validate_path(self.path)
        validate_session_id(self.session_id)
        validate_token_binding(self.token_binding)
        validate_timestamp_ms(self.timestamp_ms)
        validate_nonce(self.nonce)
        validate_body_sha256(self.body_sha256)
        validate_mac_algorithm(self.mac_algorithm)

    def canonical_bytes(self) -> bytes:
        """Exact canonical request bytes per RFC 0004 Section 9.1.

        Each line ends with \\n. Field order is fixed. The final line
        also ends with \\n.
        """
        lines = [
            _ENVELOPE_V1_HEADER,
            f"amp-version:{self.amp_version}",
            f"transport-profile:{self.transport_profile}",
            f"method:{self.method}",
            f"path:{self.path}",
            f"session-id:{self.session_id}",
            f"token-binding:{self.token_binding}",
            f"timestamp-ms:{self.timestamp_ms}",
            f"nonce:{self.nonce}",
            f"body-sha256:{self.body_sha256}",
            f"mac-algorithm:{self.mac_algorithm}",
        ]
        return ("".join(line + "\n" for line in lines)).encode("utf-8")

    def canonical_sha256(self) -> str:
        """SHA-256 of the canonical request bytes, lowercase hex."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def sign_request(envelope: CanonicalEnvelope, mac_key: bytes) -> str:
    """Compute the request MAC per RFC 0004 Section 10.2.

    Returns base64url without padding.
    """
    if len(mac_key) < 32:
        raise EnvelopeValidationError(
            f"session MAC key must be at least 32 bytes, got {len(mac_key)}"
        )
    mac_bytes = hmac.new(mac_key, envelope.canonical_bytes(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac_bytes).rstrip(b"=").decode("ascii")


def verify_request(
    envelope: CanonicalEnvelope,
    mac_key: bytes,
    presented_mac: str,
    server_receive_time_ms: int | None = None,
    seen_nonces: set[str] | None = None,
    freshness_ms: int = _DEFAULT_FRESHNESS_MS,
) -> None:
    """Verify a canonical request per RFC 0004 Section 12.

    Raises EnvelopeValidationError on any failure. This is a reference
    verification sequence -- production implementations should add
    session-bound version/profile checking and scoped token validation.

    Args:
        envelope: The canonical envelope to verify.
        mac_key: The session MAC key (>= 32 bytes).
        presented_mac: The MAC value carried with the request (base64url, no padding).
        server_receive_time_ms: Server receive time for freshness check.
            If None, uses current time.
        seen_nonces: Mutable set for replay detection. If provided, the
            nonce is checked and inserted. Caller owns nonce storage lifecycle.
        freshness_ms: Maximum allowed abs(server_time - timestamp_ms).
            Default 60000 per RFC 0004 Section 11.1.
    """
    # Step 5-6: recompute MAC and constant-time compare
    expected_mac = sign_request(envelope, mac_key)
    if not hmac.compare_digest(expected_mac, presented_mac):
        raise EnvelopeValidationError("integrity_failure: MAC mismatch")

    # Step 7: freshness
    if server_receive_time_ms is None:
        server_receive_time_ms = int(time.time() * 1000)
    request_time = int(envelope.timestamp_ms)
    skew = abs(server_receive_time_ms - request_time)
    if skew > freshness_ms:
        raise EnvelopeValidationError(
            f"integrity_failure: timestamp skew {skew}ms exceeds {freshness_ms}ms"
        )

    # Step 8: nonce replay
    if seen_nonces is not None:
        nonce_key = f"{envelope.session_id}:{envelope.nonce}"
        if nonce_key in seen_nonces:
            raise EnvelopeValidationError("replay_detected: nonce already used")
        seen_nonces.add(nonce_key)
