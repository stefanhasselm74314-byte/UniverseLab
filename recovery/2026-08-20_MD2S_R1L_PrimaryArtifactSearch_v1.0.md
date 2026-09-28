# MD2S-R1-L Primary Artifact Search v1.0

**Date:** 2026-08-20  
**Status:** `SCOPED_RECOVERY_SEARCH_COMPLETE_NO_PRIMARY_ARTIFACT_RECOVERED`  
**Scope:** forensic recovery only; no physical or solver release effect.

## 1. Purpose

This record narrows the recovery step after the legacy-branch and `Hyper.zip` audits. It searches specifically for the historical primary artifacts repeatedly referenced by the MD-2S development record:

- `MD2S_Gesamtpaket`
- `MD2S_reproduction_script`
- `MD2S_SHA256_manifest`
- run-bound solver input/output package
- run-bound one-sided Bulk/Cap boundary export
- historical values for `A_prime_bulk`, `A_prime_cap`, `Lprime_over_L_bulk`, `Lprime_over_L_cap`

The result is intentionally bounded. Failure to recover an artifact from the searched locations is **not** evidence that the artifact never existed elsewhere.

## 2. Search channels and result

### File Library index

Focused searches did not recover the referenced historical Gesamtpaket, reproduction script, or historical MD2S SHA-256 manifest. Later SCI-001/SCI-002 checksum files exist, but they are later forensic packages and must not be relabeled as the missing historical MD2S manifest.

A later forensic junction checker explicitly omits the historical interface derivatives because the surviving archive does not contain them. Therefore zero/default values in later UI tools are not recovered historical boundary data.

### GitHub current code index

Queries for the three named historical targets returned no primary artifact.

### GitHub commit-message index

Queries for `MD2S Gesamtpaket`, `MD2S reproduction`, and the B1.4K numerical fingerprint `0.842636731623` did not recover a historical primary solver/output artifact. Recent forensic commits are not historical solver provenance.

### Hyper.zip audit

The prior archive audit remains decisive for this corpus: `Hyper.zip` contains PDFs only and does not contain the referenced solver scripts, CSV/JSON state, solver inputs/outputs, residual logs, SHA-256 manifests, or referenced subpackages. Its negative result is archive-scoped only.

### ChatGPT export register

The private/export register supplies a new high-value provenance clue: **two exact `Hyperzeit Projektstatus Update` conversation targets were located**. Their private identifiers are deliberately not copied into the public repository.

This audit establishes only that two exact transcript extraction targets are known. It does not claim message-level extraction of those raw transcripts, and chat text alone cannot substitute for a primary solver artifact.

## 3. Forensic verdict

```text
PRIMARY HISTORICAL SOLVER ARTIFACT:        NOT RECOVERED
HISTORICAL RUN-BOUND SOLVER I/O:           NOT RECOVERED
HISTORICAL SHA-256 MANIFEST:               NOT RECOVERED
HISTORICAL TWO-SIDED INTERFACE EXPORT:     NOT RECOVERED
EXACT TRANSCRIPT PROVENANCE TARGETS:        RECOVERED (2, PRIVATE REFERENCES)
GLOBAL NONEXISTENCE CLAIM:                  FORBIDDEN
```

The strongest next recovery action is a targeted extraction/search of the two privately identified `Hyperzeit Projektstatus Update` conversations from an official raw ChatGPT export, if such raw export material is available. Search specifically for attachment names, package paths, download references, SHA-256 strings, run IDs, output filenames, and explicit one-sided Bulk/Cap boundary tables.

## 4. Promotion rule

Transcript evidence may establish that a filename, hash, package, or run was reported. It may refine the recovery graph. It **must not** be promoted to `VERIFIED_SOLVER_OUTPUT` unless the required primary output artifact, code/input identity, run binding, residual or convergence information, and branch association are recovered.

## 5. Governance firewall

Unchanged:

- `official_MD2S_solver = NOT_AUTHORIZED`
- `PHYSICAL_BACKGROUND = NOT_ESTABLISHED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`
- `physical_gate_effect = NONE`

No solver execution, physical run, or evidentiary promotion is part of this search.
