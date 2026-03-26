# AMP RFC 0008: Open issues, gaps, and challenged assumptions

Status: draft -- **working analysis** (not yet normative protocol text)  
Track: AMP (Authority Mediation Protocol)  
Authority: design review / gap register  
Current implementation alignment: n/a (meta-RFC)

## 1. Purpose

This document records **known gaps**, **edge cases**, and **assumptions worth challenging** across AMP RFCs 0001-0009 and the current Haven + Loopgate implementation. It exists so spec work can proceed deliberately: either tighten RFCs, add test vectors, or narrow claimed scope.

**Normative precedence:** RFCs 0001-0009 remain authoritative where they are explicit. This RFC does not override them.

## 2. Spec gaps (missing or under-specified)

### 2.1 Response integrity (called out in RFC 0001 Section 9)

- **Partially addressed:** RFC 0001 Section 9.1 now defines optional `request_id` correlation for request-response binding.
- **Residual gap:** v1 does not require response MAC/signature. Same-user attacker with ability to interpose between client and socket (e.g. ptrace, injected library, compromised client process) could forge responses.
- **Mitigation options:** Define optional signed response envelope for high-assurance profiles; or bind UI channel to launch ancestry (out of band of AMP v1).

### 2.2 Version and profile negotiation edge cases (RFC 0004 Section 6)

- **Normative:** Session-bound tuple failures and server replacement are pinned in RFC 0004 Section 6.4, 6.5, and 11.4.
- **Residual:** Mixed-version clients advertising overlapping ranges remain a product concern; the server still selects one exact negotiated pair.

### 2.3 Nonce cache bounds and persistence (RFC 0004)

- **Normative:** Restart without durable replay state requires session invalidation or equivalent fail-closed behavior (RFC 0004 Section 11.4).
- **Residual:** Eviction policies for very long-lived sessions and bounded storage of nonce material remain implementation-defined.

### 2.4 Clock skew and time semantics

- **Normative:** Wall-clock semantics and prohibition on silently widening the freshness window are in RFC 0004 Section 11.5.
- **Residual:** Optional `server_time_ms` (or similar) in denials for operator resync is not defined in v1 minimal envelopes.

### 2.5 Approval UI vs decision race (RFC 0005 + product reality)

- **Normative:** Concurrent decisions, idempotency, and stale UI behavior use `approval_state_conflict`, `approval_not_pending`, and related codes (RFC 0005 Section 10.4-10.5, 13).
- **Residual:** Multi-tab UX copy and audit presentation for the losing operator path remain product-level.

### 2.6 Multi-hop artifacts and partial promotion (RFC 0003)

- **Gap:** Multi-parent derived artifacts and partial failure (one parent pruned) need explicit lineage and operator-visible **degraded** states.
- **Risk:** Silent drop of derivation chain vs hard denial -- policy choice must be visible in audit.

### 2.7 Memory authority split (RFC 0006 vs code)

- **Normative:** Explicit degraded-profile labeling for client-local privileged paths is in RFC 0006 Section 4.5.
- **Residual:** Moving those paths behind the inspector remains an implementation milestone (see implementation mapping).

### 2.8 Compact schemas vs JSON on the wire (RFC 0007)

- **Normative:** Canonical JSON rules and worked digests for minimal `denial` and `event` examples are in RFC 0007 Section 5.1.
- **Residual:** Hashing of larger payloads and nested objects must apply the same recursive key-sort rules or define a separate envelope.

### 2.9 Capability registry format (RFC 0009)

- **Gap:** RFC 0009 defines the capability execution operation envelope but defers capability schema declaration to future work. Implementers cannot yet declare new capability types at the protocol level.
- **Risk:** Capability argument validation remains implementation-specific until a registry format is defined.

### 2.10 Streaming results (RFC 0009)

- **Gap:** RFC 0009 defines request-response execution but does not cover streaming or long-running capabilities (e.g. model inference that streams tokens).
- **Risk:** Implementers will need product-specific streaming semantics until a future RFC addresses this.

## 3. Implementation gaps relative to AMP (Loopgate / Haven)

From [implementation mapping](../design_overview/amp_implementation_mapping.md), still open:

1. No shared neutral `amp` package -- acceptable short term; increases drift risk.
2. No unified `artifact_ref` / envelope type across quarantine, promotion, memory.
3. Capability arguments narrower than the generalized AMP JSON object model (`map[string]string` vs JSON object).
4. Memory: authority not fully Loopgate-mediated for all recall paths.
5. Canonical envelope signing payload does not yet match RFC 0004 Section 9.1 (see RFC 0004 Section 18 divergence notes).
6. Session establishment does not yet negotiate `amp_version` or `transport_profile` (see RFC 0001 Section 7).

## 4. Assumptions to challenge

| Assumption | Why it might fail | What to do |
|------------|-------------------|------------|
| Unix socket + peer UID is enough binding | Same-user malware is in scope per threat model | Keep layered model; consider optional executable pinning; document that **peer binding is not malware immunity** |
| Operator reads denial text as safe | Denial strings could be confused with instructions if ever echoed into prompts | Keep denials structured; forbid mixing raw denial `message` into model context without classification |
| Single control plane per machine | Future: multiple Loopgate instances or profiles | RFC 0001 should reserve **socket path / instance id** in profile or session binding |
| `single-use` approval covers all product flows | Long-running workflows might need explicit "session-scoped" future scope | Keep 0005 strict; add new **scope enum** in a future RFC rather than overloading `single-use` |
| Local transport never exposed on TCP | Misconfiguration bugs happen | **MUST** remain product invariant; add conformance checklist item for "default listen" |

## 5. Conformance and release process

Treat [local-uds-v1 conformance checklist](../conformance/local-uds-v1-checklist.md) as a **pre-release gate** for any claim of "AMP local-uds-v1 aligned":

- Complete or explicitly waive each item with a linked issue/RFC update.
- Add **conformance version** string when checklist itself changes.

## 6. Normative follow-ups status

The following gap-register items are now pinned in normative RFC text (or in the conformance helper file):

| Topic | Normative location |
| --- | --- |
| Nonce persistence / restart policy | RFC 0004 Section 11.4, 6.5 |
| Clock semantics for freshness | RFC 0004 Section 11.5 |
| Stale approval / non-pending decisions | RFC 0005 Section 10.4, 10.5, 13 (`approval_not_pending`) |
| Canonical JSON for `denial` / `event` hashing | RFC 0007 Section 5.1 |
| Memory authority degraded labeling | RFC 0006 Section 4.5 |
| Signed request + body test vectors | RFC 0004 Section 15; [`conformance/test-vectors-v1.md`](../conformance/test-vectors-v1.md) |
| Reserved `none` sentinel | RFC 0002 Section 6 |
| Denial code registry | RFC 0002 Section 13 |
| Event type registry | RFC 0002 Section 14 |
| Session establishment protocol operation | RFC 0001 Section 7 |
| Client recovery and re-establishment | RFC 0001 Section 14 |
| Request-response correlation | RFC 0001 Section 9.1 |
| Identifier policy | RFC 0001 Section 12 |
| Capability execution operation | RFC 0009 |
| Approval manifest includes `created_at_ms` | RFC 0005 Section 6.2 |
| Implementation divergence notes | RFC 0004 Section 18 (non-normative) |

Items in Section 2 without a "Normative" or "Partially addressed" bullet remain open for future RFC work.

## 7. Document history

- 2026-03-24 -- Initial gap register and assumption review in Morph `docs/AMP/`.
- 2026-03-25 -- Cross-linked closed follow-ups to RFC 0004 (Section 6.5, 11.4-11.5); RFC 0005 `approval_not_pending`; RFC 0007 Section 5.1; RFC 0006 Section 4.5; `conformance/test-vectors-v1.md`.
- 2026-03-25 -- Added: `none` sentinel (RFC 0002 Section 6), registries (RFC 0002 Section 13-14), session establishment (RFC 0001 Section 7), client recovery (RFC 0001 Section 14), response binding (RFC 0001 Section 9.1), identifier policy (RFC 0001 Section 12), capability execution (RFC 0009), `created_at_ms` in manifest (RFC 0005 Section 6.2), divergence notes (RFC 0004 Section 18). Added gap items for capability registry format and streaming results.
