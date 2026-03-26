"""Field validation per AMP RFC 0004 Section 8."""

from __future__ import annotations

import base64
import re

_METHOD_RE = re.compile(r"^[A-Z]{1,16}$")
_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
_AMP_VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_TRANSPORT_PROFILE_RE = re.compile(r"^[a-z0-9][a-z0-9.\-]*$")
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_TOKEN_BINDING_RE = re.compile(r"^(none|sha256:[0-9a-f]{64})$")
_TIMESTAMP_RE = re.compile(r"^(0|[1-9][0-9]*)$")


class EnvelopeValidationError(ValueError):
    """Raised when a canonical envelope field fails validation."""


def validate_method(value: str) -> str:
    if not _METHOD_RE.match(value):
        raise EnvelopeValidationError(
            f"method must be 1-16 uppercase ASCII letters, got {value!r}"
        )
    return value


def validate_path(value: str) -> str:
    if not value.startswith("/"):
        raise EnvelopeValidationError("path must start with /")
    if not value.isascii():
        raise EnvelopeValidationError("path must contain only ASCII characters")
    if "?" in value or "#" in value:
        raise EnvelopeValidationError("path must not contain query strings or fragments")
    if "//" in value:
        raise EnvelopeValidationError("path must not contain empty segments")
    segments = value.split("/")[1:]
    for seg in segments:
        if seg in (".", ".."):
            raise EnvelopeValidationError("path must not contain . or .. segments")
    if len(value) > 1 and value.endswith("/"):
        raise EnvelopeValidationError("path must not have a trailing / unless it is exactly /")
    return value


def validate_session_id(value: str) -> str:
    if not _SESSION_ID_RE.match(value):
        raise EnvelopeValidationError(
            f"session_id must be 1-128 chars of [A-Za-z0-9._-], got {value!r}"
        )
    return value


def validate_token_binding(value: str) -> str:
    if not _TOKEN_BINDING_RE.match(value):
        raise EnvelopeValidationError(
            f"token_binding must be 'none' or 'sha256:<64 hex>', got {value!r}"
        )
    return value


def validate_nonce(value: str) -> str:
    """Validate nonce is base64url without padding, decoding to >= 16 bytes."""
    if value != value.strip():
        raise EnvelopeValidationError("nonce must not have leading or trailing whitespace")
    try:
        padding = 4 - (len(value) % 4)
        if padding < 4:
            padded = value + "=" * padding
        else:
            padded = value
        raw = base64.urlsafe_b64decode(padded)
    except Exception as exc:
        raise EnvelopeValidationError(f"nonce must be valid base64url: {exc}") from exc
    if len(raw) < 16:
        raise EnvelopeValidationError(
            f"nonce must decode to at least 16 bytes, got {len(raw)}"
        )
    return value


def validate_timestamp_ms(value: str) -> str:
    if not _TIMESTAMP_RE.match(value):
        raise EnvelopeValidationError(
            f"timestamp_ms must be unsigned decimal integer, got {value!r}"
        )
    return value


def validate_body_sha256(value: str) -> str:
    if not _HEX64_RE.match(value):
        raise EnvelopeValidationError(
            f"body_sha256 must be exactly 64 lowercase hex chars, got {value!r}"
        )
    return value


def validate_mac_algorithm(value: str) -> str:
    if value != "hmac-sha256":
        raise EnvelopeValidationError(
            f"mac_algorithm must be 'hmac-sha256', got {value!r}"
        )
    return value


def validate_amp_version(value: str) -> str:
    if not _AMP_VERSION_RE.match(value):
        raise EnvelopeValidationError(
            f"amp_version must be major.minor (no leading zeros), got {value!r}"
        )
    return value


def validate_transport_profile(value: str) -> str:
    if not _TRANSPORT_PROFILE_RE.match(value):
        raise EnvelopeValidationError(
            f"transport_profile must be lowercase ASCII with [a-z0-9.-], got {value!r}"
        )
    return value
