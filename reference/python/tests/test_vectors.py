"""Conformance tests against AMP RFC 0004 Section 15 and RFC 0007 Section 5.1.

These test vectors are normative. If this file disagrees with the RFCs
on a numeric digest, the RFC wins.
"""

import pytest

from amp.envelope import (
    CanonicalEnvelope,
    compute_body_sha256,
    compute_token_binding,
    sign_request,
    verify_request,
)
from amp.canonical_json import canonical_json_bytes, canonical_json_sha256
from amp.validation import EnvelopeValidationError


# ---------------------------------------------------------------------------
# RFC 0004 Section 15.1: Positive canonical signing vector
# ---------------------------------------------------------------------------

MAC_KEY_HEX = "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
SCOPED_TOKEN = b"tok_01ARZ3NDEKTSV4RRFFQ69G5FAV"
REQUEST_BODY = b'{"action":"quarantine.inspect","target_ref":"artifact:amp:1234"}'

EXPECTED_TOKEN_BINDING = "sha256:53d7f667585f8e951c12f9d383f5570aa272d30a14cafb0040bea8e8e68cc34b"
EXPECTED_BODY_SHA256 = "3e9663348715e01175b0bf6bee923d06e8cb153353ff32a63301af6462c40723"
EXPECTED_CANONICAL_SHA256 = "c1216b6165388937bc7b4eabf26ac1a676784339c1dc02052536960efb58597e"
EXPECTED_REQUEST_MAC = "mdOwITZBIj5fBhqpIxX2XkAhlwp_eTs7xoRIUk5DjBQ"

ENVELOPE = CanonicalEnvelope(
    amp_version="1.0",
    transport_profile="local-uds-v1",
    method="POST",
    path="/v1/capabilities/execute",
    session_id="sess_01ARZ3NDEKTSV4RRFFQ69G5FAV",
    token_binding=EXPECTED_TOKEN_BINDING,
    timestamp_ms="1735689600123",
    nonce="AAECAwQFBgcICQoLDA0ODw",
    body_sha256=EXPECTED_BODY_SHA256,
)


class TestPositiveVector:

    def test_body_sha256(self):
        assert compute_body_sha256(REQUEST_BODY) == EXPECTED_BODY_SHA256

    def test_token_binding(self):
        assert compute_token_binding(SCOPED_TOKEN) == EXPECTED_TOKEN_BINDING

    def test_canonical_bytes_length(self):
        raw = ENVELOPE.canonical_bytes()
        assert len(raw) == 392

    def test_canonical_bytes_end_with_newline(self):
        raw = ENVELOPE.canonical_bytes()
        assert raw[-1:] == b"\n"

    def test_canonical_bytes_no_carriage_return(self):
        raw = ENVELOPE.canonical_bytes()
        assert b"\r" not in raw

    def test_canonical_sha256(self):
        assert ENVELOPE.canonical_sha256() == EXPECTED_CANONICAL_SHA256

    def test_request_mac(self):
        mac_key = bytes.fromhex(MAC_KEY_HEX)
        mac = sign_request(ENVELOPE, mac_key)
        assert mac == EXPECTED_REQUEST_MAC

    def test_verify_succeeds(self):
        mac_key = bytes.fromhex(MAC_KEY_HEX)
        verify_request(
            ENVELOPE,
            mac_key,
            EXPECTED_REQUEST_MAC,
            server_receive_time_ms=1735689600123,
        )

    def test_canonical_bytes_exact_content(self):
        """Verify the exact canonical string matches the RFC example."""
        expected = (
            "amp-request-v1\n"
            "amp-version:1.0\n"
            "transport-profile:local-uds-v1\n"
            "method:POST\n"
            "path:/v1/capabilities/execute\n"
            "session-id:sess_01ARZ3NDEKTSV4RRFFQ69G5FAV\n"
            "token-binding:sha256:53d7f667585f8e951c12f9d383f5570aa272d30a14cafb0040bea8e8e68cc34b\n"
            "timestamp-ms:1735689600123\n"
            "nonce:AAECAwQFBgcICQoLDA0ODw\n"
            "body-sha256:3e9663348715e01175b0bf6bee923d06e8cb153353ff32a63301af6462c40723\n"
            "mac-algorithm:hmac-sha256\n"
        )
        assert ENVELOPE.canonical_bytes() == expected.encode("utf-8")


# ---------------------------------------------------------------------------
# RFC 0004 Section 15.2: Negative conformance vectors
# ---------------------------------------------------------------------------

class TestNegativeVectors:

    def test_stale_timestamp(self):
        """Skew > 60s between request timestamp and server receive must reject."""
        stale = CanonicalEnvelope(
            amp_version=ENVELOPE.amp_version,
            transport_profile=ENVELOPE.transport_profile,
            method=ENVELOPE.method,
            path=ENVELOPE.path,
            session_id=ENVELOPE.session_id,
            token_binding=ENVELOPE.token_binding,
            timestamp_ms="1735689480000",
            nonce=ENVELOPE.nonce,
            body_sha256=ENVELOPE.body_sha256,
        )
        mac_key = bytes.fromhex(MAC_KEY_HEX)
        mac = sign_request(stale, mac_key)
        with pytest.raises(EnvelopeValidationError, match="integrity_failure.*timestamp"):
            verify_request(
                stale,
                mac_key,
                mac,
                server_receive_time_ms=1735689605000,
            )

    def test_replayed_nonce(self):
        """Same nonce in same session must reject on second use."""
        mac_key = bytes.fromhex(MAC_KEY_HEX)
        mac = sign_request(ENVELOPE, mac_key)
        seen: set[str] = set()
        verify_request(
            ENVELOPE,
            mac_key,
            mac,
            server_receive_time_ms=1735689600123,
            seen_nonces=seen,
        )
        with pytest.raises(EnvelopeValidationError, match="replay_detected"):
            verify_request(
                ENVELOPE,
                mac_key,
                mac,
                server_receive_time_ms=1735689600123,
                seen_nonces=seen,
            )

    def test_body_hash_mismatch(self):
        """Mismatched body_sha256 produces a different MAC."""
        wrong_body_hash = "753c60833eb047be4ed7353fba637bfc63ffaab5c981a8c84ec101efba7cf0b5"
        tampered = CanonicalEnvelope(
            amp_version=ENVELOPE.amp_version,
            transport_profile=ENVELOPE.transport_profile,
            method=ENVELOPE.method,
            path=ENVELOPE.path,
            session_id=ENVELOPE.session_id,
            token_binding=ENVELOPE.token_binding,
            timestamp_ms=ENVELOPE.timestamp_ms,
            nonce=ENVELOPE.nonce,
            body_sha256=wrong_body_hash,
        )
        mac_key = bytes.fromhex(MAC_KEY_HEX)
        with pytest.raises(EnvelopeValidationError, match="integrity_failure.*MAC"):
            verify_request(
                tampered,
                mac_key,
                EXPECTED_REQUEST_MAC,
                server_receive_time_ms=1735689600123,
            )

    def test_mac_mismatch(self):
        """Wrong MAC must reject."""
        mac_key = bytes.fromhex(MAC_KEY_HEX)
        with pytest.raises(EnvelopeValidationError, match="integrity_failure.*MAC"):
            verify_request(
                ENVELOPE,
                mac_key,
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                server_receive_time_ms=1735689600123,
            )


# ---------------------------------------------------------------------------
# Field validation tests
# ---------------------------------------------------------------------------

class TestFieldValidation:

    def test_invalid_method_lowercase(self):
        with pytest.raises(EnvelopeValidationError, match="method"):
            CanonicalEnvelope(
                amp_version="1.0", transport_profile="local-uds-v1",
                method="post", path="/v1/test", session_id="sess_abc",
                token_binding="none", timestamp_ms="1000",
                nonce="AAECAwQFBgcICQoLDA0ODw",
                body_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            )

    def test_invalid_path_query_string(self):
        with pytest.raises(EnvelopeValidationError, match="query"):
            CanonicalEnvelope(
                amp_version="1.0", transport_profile="local-uds-v1",
                method="POST", path="/v1/test?id=1", session_id="sess_abc",
                token_binding="none", timestamp_ms="1000",
                nonce="AAECAwQFBgcICQoLDA0ODw",
                body_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            )

    def test_invalid_path_dot_segment(self):
        with pytest.raises(EnvelopeValidationError, match="\\.\\."):
            CanonicalEnvelope(
                amp_version="1.0", transport_profile="local-uds-v1",
                method="POST", path="/v1/../secret", session_id="sess_abc",
                token_binding="none", timestamp_ms="1000",
                nonce="AAECAwQFBgcICQoLDA0ODw",
                body_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            )

    def test_invalid_amp_version_leading_zero(self):
        with pytest.raises(EnvelopeValidationError, match="amp_version"):
            CanonicalEnvelope(
                amp_version="01.0", transport_profile="local-uds-v1",
                method="POST", path="/v1/test", session_id="sess_abc",
                token_binding="none", timestamp_ms="1000",
                nonce="AAECAwQFBgcICQoLDA0ODw",
                body_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            )

    def test_invalid_mac_algorithm(self):
        with pytest.raises(EnvelopeValidationError, match="mac_algorithm"):
            CanonicalEnvelope(
                amp_version="1.0", transport_profile="local-uds-v1",
                method="POST", path="/v1/test", session_id="sess_abc",
                token_binding="none", timestamp_ms="1000",
                nonce="AAECAwQFBgcICQoLDA0ODw",
                body_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                mac_algorithm="sha256",
            )

    def test_mac_key_too_short(self):
        mac_key = b"\x00" * 16
        with pytest.raises(EnvelopeValidationError, match="32 bytes"):
            sign_request(ENVELOPE, mac_key)

    def test_nonce_too_short(self):
        with pytest.raises(EnvelopeValidationError, match="16 bytes"):
            CanonicalEnvelope(
                amp_version="1.0", transport_profile="local-uds-v1",
                method="POST", path="/v1/test", session_id="sess_abc",
                token_binding="none", timestamp_ms="1000",
                nonce="AQIDBA",  # 4 bytes
                body_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            )


# ---------------------------------------------------------------------------
# RFC 0007 Section 5.1: Canonical JSON test vectors
# ---------------------------------------------------------------------------

DENIAL_EXAMPLE = {
    "kind": "denial",
    "code": "unsupported_version",
    "message": "operator-safe denial text",
    "retryable": False,
    "occurred_at_ms": 1735689601123,
    "request_canonical_sha256": "c1216b6165388937bc7b4eabf26ac1a676784339c1dc02052536960efb58597e",
    "amp_version": "1.0",
    "transport_profile": "local-uds-v1",
}

EVENT_EXAMPLE = {
    "kind": "event",
    "event_id": "event:amp:01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "event_type": "approval.created",
    "occurred_at_ms": 1735689601123,
    "subject_ref": "approval:01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "actor_ref": "session:sess_01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "causal_ref": "request:c1216b6165388937bc7b4eabf26ac1a676784339c1dc02052536960efb58597e",
    "payload_sha256": "17d8e1b8f0b2f6f77c5418d4a70f2b6584ebebc0b89f9d9d9db2f8f1f59a9a2b",
    "amp_version": "1.0",
}

EXPECTED_DENIAL_SHA256 = "60df78ff5084e2cb9bb7db4e569988cb18ec9f9f1aefa43fbacef7d84b482c8b"
EXPECTED_EVENT_SHA256 = "d584de63d0adc5fc2b07dfcc1b1bead89a697f932ac6a8b02aa861e76cdbe135"


class TestCanonicalJson:

    def test_denial_sha256(self):
        assert canonical_json_sha256(DENIAL_EXAMPLE) == EXPECTED_DENIAL_SHA256

    def test_event_sha256(self):
        assert canonical_json_sha256(EVENT_EXAMPLE) == EXPECTED_EVENT_SHA256

    def test_denial_key_order(self):
        raw = canonical_json_bytes(DENIAL_EXAMPLE).decode("utf-8")
        keys = []
        for part in raw.strip("{}").split(","):
            key = part.split(":")[0].strip('"')
            if key:
                keys.append(key)
        assert keys == sorted(keys)

    def test_no_spaces_after_separators(self):
        raw = canonical_json_bytes(DENIAL_EXAMPLE).decode("utf-8")
        assert ": " not in raw
        assert ", " not in raw

    def test_no_escaped_forward_slash(self):
        obj = {"url": "https://example.com/path"}
        raw = canonical_json_bytes(obj).decode("utf-8")
        assert "\\/" not in raw

    def test_integer_no_fraction(self):
        obj = {"count": 42}
        raw = canonical_json_bytes(obj).decode("utf-8")
        assert raw == '{"count":42}'

    def test_boolean_lowercase(self):
        obj = {"active": True, "deleted": False}
        raw = canonical_json_bytes(obj).decode("utf-8")
        assert '"active":true' in raw
        assert '"deleted":false' in raw

    def test_null_literal(self):
        obj = {"value": None}
        raw = canonical_json_bytes(obj).decode("utf-8")
        assert raw == '{"value":null}'


# ---------------------------------------------------------------------------
# Empty body SHA-256 (RFC 0004)
# ---------------------------------------------------------------------------

class TestEmptyBody:

    def test_empty_body_sha256(self):
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert compute_body_sha256(b"") == expected
