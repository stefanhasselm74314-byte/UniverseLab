# ULSH-01 — M1 Parent Field-Content Provenance Recovery v0.1

**Datum:** 2026-08-21  
**Arbeitsbereich:** HPVS → HZT-M0 → S6 → C-PHYS → ULSH-01  
**Work Package:** ULSH-01-WP1  
**Klassifikation:** Governance-/Provenienz-Recovery, **kein Solverlauf**  
**Status:** `RECOVERED_SIGMA_FT_NOT_RATIFIED_IN_FROZEN_M1_C1`

## 1. Ergebnis

Der bisherige Status

`M1_FIELD_CONTENT_SCOPE = RECONSTRUCTION_REQUIRED`

kann auf Basis der kanonischen Parent-, Freeze-, BVP- und Assembly-Artefakte präzisiert werden zu:

`M1_FIELD_CONTENT_SCOPE = RECOVERED`

und

`SIGMA_FT_STATUS = NONCANONICAL_DEVELOPMENT_EXTENSION_NOT_RATIFIED_IN_FROZEN_M1_C1`.

Das ist stärker als ein bloßer Negativbefund aus einer fehlenden Erwähnung. Die kanonischen Quellen definieren den Feldinhalt und die BVP-Dimension positiv:

- sechs-dimensionaler Bulk: `g_AB`, `phi`, `A_A`;
- codim-1-Cap: `sigma_cap` über die Kappenwirkung;
- reguläre Hintergrundprofile pro Region: `A_s`, `L_s`, `phi_s`, `A_chi_s`;
- kanonischer globaler BVP: 8 kontinuierliche Unbekannte und 8 unabhängige Rand-/Globalresiduen;
- diskrete 3A-Assembly: `8*N + 8` gegen `8*N + 8`.

Ein zusätzliches glattes codim-0-Layerfeld `Sigma_FT` ist in diesem eingefrorenen M1/C1-Feldinhalt nicht ratifiziert.

## 2. Kanonische Evidenzbasis

### Parent Action / SCI-001/002

`hzt-s6-parent-action-v0.1.json` und `sci-001-002-parent-closure-v0.1.html` definieren den minimalen Bulk als Einstein–Skalar–Maxwell. Das Feld `sigma` lebt im fünf-dimensionalen Kappensektor `L_Sigma`; es ist kein selbständiges glattes sechs-dimensionales Layerfeld.

### C-PHYS Parent Operator

`registry/2026-08-03_MD2S_R1_C_PHYS_ParentActionOperatorEntryContract_v0.1.json` übernimmt denselben Parent-Feldinhalt und führt als regionale Profilunbekannte ausschließlich `A_s`, `L_s`, `phi_s`, `A_chi_s`.

### M1 Function Freeze

`registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json` friert `U`, `Z_F`, `lambda`, `Z_sigma` sowie `q_ref/q_sigma` für die bereits vorhandenen Parentfelder ein. Der Freeze fügt keinen zusätzlichen Bulk-/Layer-Freiheitsgrad hinzu.

### C1 BVP / 3A Assembly

`registry/2026-08-03_MD2S_C1_BVPPreflightContract_v0.1.json` fixiert das strukturelle 8×8-BVP.  
`registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3AAssemblyCorrectionContract_v0.3.json` diskretisiert genau diesen Feldinhalt als `8*N` Profilwerte plus acht augmentierte globale Unbekannte.

## 3. Wirkung auf den Finite-Thickness-Pfad

Die G3.2–G3.5-Arbeit bleibt mathematisch und softwareseitig als **Development Path** verwertbar. Sie darf jedoch nicht stillschweigend zum physischen Frozen-M1-Target erklärt werden.

Damit gilt:

- `SUPPLEMENTARY_BULK_LAYER_WITH_CANONICAL_CAP = DEVELOPMENT_ONLY`;
- strukturelles 10×10-Matching bleibt ein konditionaler Erweiterungspfad;
- `Sigma_FT` darf nicht in den offiziellen M1/C1-Target-Digest eingebunden werden;
- ein resolved-cap replacement oder ein zusätzlicher Bulk-Layer erfordert eine separat regierte Modell-/Parent-Scope-Änderung;
- kein stiller Wechsel zu C2 oder zu einer neuen Modellversion ist zulässig.

## 4. Reconciliation mit Background-3C11 / 3C12

Das historische 3C11-Artefakt

`registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C11RealBackendControlAuthorizationReview_v0.1.json`

verweigert die Zielausführung und nennt als nächsten zulässigen Block:

`C-PHYS-R1.0-BACKGROUND-3C12_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_IMPLEMENTATION_ONLY`.

Diese 3C12-Erlaubnis ist ausdrücklich **implementation-only** und verbietet Backend-Import, CP01R1, `a_F=1/4`-Zielsolve, operative Grant-Erzeugung, physische Resultate und automatische Autorisierung.

Sie ist zudem historisch an den damaligen kanonischen M1/C1-Pfad gebunden. Sie kann daher weder die spätere `Sigma_FT`-Erweiterung ratifizieren noch den neueren WP1-Provenienzbefund überschreiben.

## 5. Work-Package-Status

| Work Package | Status nach Recovery |
|---|---|
| ULSH-01-WP1 | `NOT_CLOSED` — exakter Targetvertrag muss wieder an kanonisches M1/C1 gebunden oder über eine ausdrücklich autorisierte Modelländerung ersetzt werden |
| ULSH-01-WP2 | vorhandene Implementierungsassets dürfen Development-only bleiben; Target-Rebind ausstehend |
| ULSH-01-WP3 | Software-QA bleibt gültig als Software-QA; keine physische Evidenz |
| ULSH-01-WP4 | `BLOCKED_NOT_AUTHORIZED` |

## 6. Nächster sicherer Schritt

**Kanonischen M1/C1 Zwei-Regionen-8×8-Targetvertrag als exakten WP1-Digest einfrieren und anschließend vorhandene WP2/WP3-Assets gegen genau diesen Digest reconciliieren.**

`Sigma_FT` bleibt außerhalb dieses Targets, solange keine separate, ausdrückliche Modell-Scope-Änderung autorisiert wurde.

## 7. Firewall

- Kein physischer Solverlauf wurde ausgeführt.
- Kein Jacobian wurde physisch ausgewertet.
- Kein Background wurde etabliert.
- Kein operativer Grant wurde erzeugt.
- `R1.1 = BLOCKED`.
- `R1.2 = BLOCKED`.
- `K1-D = NOT_RELEASED`.
- `K1-E = NOT_ADMISSIBLE`.
- `physical_evidence_effect = NONE`.

Die Ausgrenzung von `Sigma_FT` aus dem eingefrorenen M1/C1 ist **keine** physikalische Widerlegung eines Finite-Thickness-Sektors. Sie ist ausschließlich eine Aussage darüber, was im aktuell ratifizierten Modellfeldinhalt enthalten ist.
