"""Canonical JSON serialization per AMP RFC 0007 Section 5.1.

Rules:
- UTF-8 output
- Root value is a JSON object
- Keys sorted recursively by ascending Unicode scalar value
- No insignificant whitespace (no space after : or ,)
- false, true, null are lowercase JSON literals
- Integer numbers have no fraction or exponent part
- / is NOT escaped as \\/
- Strings follow JSON escaping rules
"""

from __future__ import annotations

import hashlib
import json


def canonical_json_bytes(obj: dict) -> bytes:
    """Serialize a dict to canonical JSON bytes per RFC 0007 Section 5.1."""
    if not isinstance(obj, dict):
        raise TypeError(f"canonical JSON root must be a dict, got {type(obj).__name__}")
    return _encode(obj).encode("utf-8")


def canonical_json_sha256(obj: dict) -> str:
    """SHA-256 of canonical JSON bytes, lowercase hex."""
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def _encode(value: object) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        if value == int(value) and not (value != value):  # not NaN
            return str(int(value))
        return json.dumps(value)
    if isinstance(value, str):
        return _encode_string(value)
    if isinstance(value, list):
        return "[" + ",".join(_encode(item) for item in value) + "]"
    if isinstance(value, dict):
        sorted_keys = sorted(value.keys())
        pairs = [_encode_string(k) + ":" + _encode(value[k]) for k in sorted_keys]
        return "{" + ",".join(pairs) + "}"
    raise TypeError(f"canonical JSON does not support {type(value).__name__}")


def _encode_string(s: str) -> str:
    """JSON-escape a string without escaping /."""
    result = ['"']
    for ch in s:
        if ch == '"':
            result.append('\\"')
        elif ch == "\\":
            result.append("\\\\")
        elif ch == "\b":
            result.append("\\b")
        elif ch == "\f":
            result.append("\\f")
        elif ch == "\n":
            result.append("\\n")
        elif ch == "\r":
            result.append("\\r")
        elif ch == "\t":
            result.append("\\t")
        elif ord(ch) < 0x20:
            result.append(f"\\u{ord(ch):04x}")
        else:
            result.append(ch)
    result.append('"')
    return "".join(result)
