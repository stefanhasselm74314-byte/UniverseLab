# SDL-2026-012 — MD-2S Dual-Track Recovery Proposal

**Status:** PROPOSED  
**Date:** 2026-08-01  
**Layer:** HZT-M0 / MD-2 / MD-4 / MD-6  
**Evidence effect:** NONE  
**Decision authority required:** HDA / project owner ratification

## Decision proposed

The MD-2S recovery shall be split into two explicitly versioned tracks:

1. **MD2S-R1-L — Legacy reproduction**  
   Reconstruct the historical A0 through B1.4N calculation as faithfully as possible from the original equations and conventions.

2. **MD2S-R1-C — Canonical rebuild**  
   Derive a new static radial background solver from the current SCI-001/SCI-002 parent action, current convention registry and a complete MD-6 reproducibility package.

The two tracks MUST remain distinct until equation-level model identity has been demonstrated.

## Rationale

The accessible archive consistently preserves the reported A0 benchmarks and the B1.4N negative result, but not the executable solver, full radial equation set, localized action, oriented boundary data or residual logs. The current SCI-001/SCI-002 parent skeleton is newer and cannot silently be assumed to be identical to the missing historical implementation.

Without the split, there are two unacceptable risks:

- the old benchmark values could be used to tune and thereby define the new parent theory;
- a new consistent model could be falsely presented as an independent reproduction of the old calculation.

## Consequences

### Legacy track

- Historical benchmark numbers are legitimate regression targets.
- Reported PASS/FAIL outcomes remain `REPORTED_NOT_INDEPENDENTLY_REPRODUCED` until an executable reconstruction exists.
- Missing equations or conventions may not be filled by undocumented guesswork.

### Canonical track

- The current parent action, boundary terms and conventions must be frozen before solver code.
- The current model receives a new explicit model version.
- Legacy benchmarks are compared only after a model-identity analysis.
- Failure to reproduce legacy numbers does not automatically falsify the canonical model if the actions differ.

### Shared restrictions

Neither track changes:

```text
K1-D = NOT RELEASED
K1-E = NOT ADMISSIBLE
Evidence effect = NONE
```

Neither track may claim full ghost freedom from background regularity or numerical stability.

## Affected artifacts

- `science/hzt-m0/md2s/R0_ARTIFACT_INVENTORY_v0.1.json`
- `science/hzt-m0/md2s/R1_MODEL_FREEZE_GATE_v0.1.json`
- `science/hzt-m0/md2s/R1_SOURCE_RECONSTRUCTION_LEDGER_v0.1.json`
- `science/hzt-m0/md2s/MD2S_RECOVERY_CONTRACT_v0.1.md`
- `registry/research-continuation-manifest-v0.1.json`
- future MD-2, MD-4 and MD-6 specifications

## Acceptance conditions

This SDL becomes ACTIVE only when the project owner or HDA explicitly ratifies:

- the two model IDs,
- ownership of physics versus solver specifications,
- the rule that benchmark agreement does not establish action identity,
- the rule that legacy and canonical outputs remain separately labelled.

Until ratification, this document is a governance proposal and has no canon-changing force.
