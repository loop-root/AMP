# AMP conformance helpers — test vectors v1

**Authority:** conformance aid (implements RFC 0004 §15 and RFC 0007 §5.1)  
**Last updated:** 2026-03-25

This file collects **UTF-8 byte listings** and **canonical JSON** digests so
implementers can cross-check parsers, MAC verification, and audit hashing
without re-deriving bytes by hand.

**Normative precedence:**

- Canonical request field values, `canonical_request_sha256`, and
  `request_mac` for the positive signing example are defined in
  [RFC 0004 §15.1](../AMP-RFCs/0004-canonical-envelope-and-integrity-binding.md#151-positive-canonical-signing-vector).
- Canonical JSON serialization rules are defined in
  [RFC 0007 §5.1](../AMP-RFCs/0007-core-envelopes-and-compact-schemas.md#51-canonical-json-for-stable-hashing).

If this document disagrees with those sections on a numeric digest, the RFC
wins.

## 1. Positive canonical request — UTF-8 hex dump

The following is the exact UTF-8 encoding of the canonical request string
from RFC 0004 §15.1 (392 bytes, final byte is `0x0a` after
`mac-algorithm:hmac-sha256`).

```text
0000  61 6d 70 2d 72 65 71 75 65 73 74 2d 76 31 0a 61  amp-request-v1.a
0010  6d 70 2d 76 65 72 73 69 6f 6e 3a 31 2e 30 0a 74  mp-version:1.0.t
0020  72 61 6e 73 70 6f 72 74 2d 70 72 6f 66 69 6c 65  ransport-profile
0030  3a 6c 6f 63 61 6c 2d 75 64 73 2d 76 31 0a 6d 65  :local-uds-v1.me
0040  74 68 6f 64 3a 50 4f 53 54 0a 70 61 74 68 3a 2f  thod:POST.path:/
0050  76 31 2f 63 61 70 61 62 69 6c 69 74 69 65 73 2f  v1/capabilities/
0060  65 78 65 63 75 74 65 0a 73 65 73 73 69 6f 6e 2d  execute.session-
0070  69 64 3a 73 65 73 73 5f 30 31 41 52 5a 33 4e 44  id:sess_01ARZ3ND
0080  45 4b 54 53 56 34 52 52 46 46 51 36 39 47 35 46  EKTSV4RRFFQ69G5F
0090  41 56 0a 74 6f 6b 65 6e 2d 62 69 6e 64 69 6e 67  AV.token-binding
00a0  3a 73 68 61 32 35 36 3a 35 33 64 37 66 36 36 37  :sha256:53d7f667
00b0  35 38 35 66 38 65 39 35 31 63 31 32 66 39 64 33  585f8e951c12f9d3
00c0  38 33 66 35 35 37 30 61 61 32 37 32 64 33 30 61  83f5570aa272d30a
00d0  31 34 63 61 66 62 30 30 34 30 62 65 61 38 65 38  14cafb0040bea8e8
00e0  65 36 38 63 63 33 34 62 0a 74 69 6d 65 73 74 61  e68cc34b.timesta
00f0  6d 70 2d 6d 73 3a 31 37 33 35 36 38 39 36 30 30  mp-ms:1735689600
0100  31 32 33 0a 6e 6f 6e 63 65 3a 41 41 45 43 41 77  123.nonce:AAECAw
0110  51 46 42 67 63 49 43 51 6f 4c 44 41 30 4f 44 77  QFBgcICQoLDA0ODw
0120  0a 62 6f 64 79 2d 73 68 61 32 35 36 3a 33 65 39  .body-sha256:3e9
0130  36 36 33 33 34 38 37 31 35 65 30 31 31 37 35 62  663348715e01175b
0140  30 62 66 36 62 65 65 39 32 33 64 30 36 65 38 63  0bf6bee923d06e8c
0150  62 31 35 33 33 35 33 66 66 33 32 61 36 33 33 30  b153353ff32a6330
0160  31 61 66 36 34 36 32 63 34 30 37 32 33 0a 6d 61  1af6462c40723.ma
0170  63 2d 61 6c 67 6f 72 69 74 68 6d 3a 68 6d 61 63  c-algorithm:hmac
0180  2d 73 68 61 32 35 36 0a                          -sha256.
```

**SHA-256 (canonical request bytes):**
`c1216b6165388937bc7b4eabf26ac1a676784339c1dc02052536960efb58597e`

**Session MAC key (32 bytes, hex):**
`000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f`

**Request MAC (base64url, no padding):**
`mdOwITZBIj5fBhqpIxX2XkAhlwp_eTs7xoRIUk5DjBQ`

**Application body bytes (UTF-8):**

```text
{"action":"quarantine.inspect","target_ref":"artifact:amp:1234"}
```

**Body SHA-256:** `3e9663348715e01175b0bf6bee923d06e8cb153353ff32a63301af6462c40723`

**Scoped token octets (for `token_binding`):** `tok_01ARZ3NDEKTSV4RRFFQ69G5FAV`

**Token binding:** `sha256:53d7f667585f8e951c12f9d383f5570aa272d30a14cafb0040bea8e8e68cc34b`

## 2. Canonical JSON — minimal `denial` (RFC 0007 §6 example)

Canonical JSON byte sequence (keys sorted per RFC 0007 §5.1; no spaces):

```text
{"amp_version":"1.0","code":"unsupported_version","kind":"denial","message":"operator-safe denial text","occurred_at_ms":1735689601123,"request_canonical_sha256":"c1216b6165388937bc7b4eabf26ac1a676784339c1dc02052536960efb58597e","retryable":false,"transport_profile":"local-uds-v1"}
```

**SHA-256:** `60df78ff5084e2cb9bb7db4e569988cb18ec9f9f1aefa43fbacef7d84b482c8b`

## 3. Canonical JSON — minimal `event` (RFC 0007 §7 example)

Canonical JSON byte sequence:

```text
{"actor_ref":"session:sess_01ARZ3NDEKTSV4RRFFQ69G5FAV","amp_version":"1.0","causal_ref":"request:c1216b6165388937bc7b4eabf26ac1a676784339c1dc02052536960efb58597e","event_id":"event:amp:01ARZ3NDEKTSV4RRFFQ69G5FAV","event_type":"approval.created","kind":"event","occurred_at_ms":1735689601123,"payload_sha256":"17d8e1b8f0b2f6f77c5418d4a70f2b6584ebebc0b89f9d9d9db2f8f1f59a9a2b","subject_ref":"approval:01ARZ3NDEKTSV4RRFFQ69G5FAV"}
```

**SHA-256:** `d584de63d0adc5fc2b07dfcc1b1bead89a697f932ac6a8b02aa861e76cdbe135`

## 4. Empty application body (illustrative)

SHA-256 of the zero-length body (used in `body_sha256` when there is no
payload):

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

This file does not define a full alternate canonical request MAC for an empty
body; reuse RFC 0004 §9 field rules and recompute Section 9 bytes for your
`method`, `path`, `nonce`, and `timestamp_ms`.

## Document history

- 2026-03-25 — Initial v1 helpers aligned with RFC 0004 §15.1 and RFC 0007 §5.1.
