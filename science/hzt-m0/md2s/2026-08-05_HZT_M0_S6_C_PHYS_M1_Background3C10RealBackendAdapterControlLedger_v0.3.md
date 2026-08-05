# HZT-M0-S6-C-PHYS-M1 — Background-3C10 Real-Backend Adapter Control Ledger v0.3

**Datum:** 2026-08-05  
**Track:** `MD2S-R1-C-PHYS`  
**Aktiver Kontrolllauf:** `HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R3`

## 1. Unveränderliche Fehlerkette

```text
R1 = FAIL_CLOSED_PRIMARY_UNIFORM_BULK_THRESHOLD_AT_N96
R2 = FAIL_CLOSED_CANDIDATE_JSON_KEY_ORDER_MISTAKEN_FOR_VECTOR_ORDER
```

Beide Ergebnisse bleiben eigenständige, nicht wiederverwendbare Kontrollbefunde. R3 ersetzt weder R1 noch R2.

## 2. R2-Fehlerkern

Der Primärblock von R2 bestand und erzeugte den bekannten Kontroll-Digest:

```text
6a00f71f4904574841d17eaebba7f8318fc136d477ab6fd324f3354f1b33e400
```

Der Independent-Worker wurde vor dem Import gestoppt, weil kanonisches JSON die Schlüssel alphabetisch serialisierte, während die R2-Schnittstelle die dekodierte Mapping-Reihenfolge mit der fachlichen Vektorreihenfolge verglich.

Das war ein Kategorienfehler:

- Ein JSON-Objekt ist eine Abbildung.
- Die Reihenfolge seiner Schlüssel ist nicht der physikalische Vektorindex.
- Der Vektorindex wird durch den versionierten Feldvertrag definiert.

## 3. R3-Handoff-Regel

R3 verlangt exakt die Feldmenge

```text
varphi_N_0, q_N, A_S_0, varphi_S_0,
q_S, rho_N, rho_S, k4
```

und verwirft:

- jedes fehlende Feld,
- jedes unbekannte Feld,
- jeden fehlerhaften SHA-256-Digest.

Nach erfolgreicher Mengen- und Digestprüfung wird der numerische Vektor ausschließlich in der obigen Vertragsreihenfolge rekonstruiert. Die eingehende JSON-Schlüsselreihenfolge bleibt ausdrücklich nicht semantisch.

## 4. Was unverändert bleibt

- exakter Kontrollfall `a_F=0`,
- Primärnetze `24,48,96`,
- Bulk-Hüllen `1e-9,1e-9,3e-8`,
- Independent-Cutoffs `1e-3,5e-4,2.5e-4`,
- sechs DOP853-Regionalintegrationen,
- reale Backendquellen,
- Ressourcen-, Timeout-, Signal- und Artefaktfirewalls,
- Verbot aller Root- und Zielsolve-Pfade.

## 5. Erlaubte Aussage bei PASS

Ein R3-PASS bedeutet ausschließlich, dass die realen Backendmodule für den analytischen `a_F=0`-Kontrollfall über eine explizit geordnete, hashgebundene und ressourcenbegrenzte Adaptertransaktion zusammenarbeiten.

Nicht ableitbar sind:

- CP01R1-Freigabe,
- ein Hintergrund bei `a_F=1/4`,
- Existenz oder Eindeutigkeit,
- Fredholm-Eigenschaft oder invertierbarer Kontinuums-Jacobian,
- Stabilität oder Ghostfreiheit,
- K1-D, K1-E oder physische Evidenz.

## 6. Unveränderte Gates

```text
BACKGROUND_3C_EXECUTION = NOT_AUTHORIZED
BACKGROUND_SOLVER_EXECUTION = NOT_AUTHORIZED
PHYSICAL_BACKGROUND = NOT_ESTABLISHED
R1.1 = BLOCKED
R1.2 = BLOCKED
official_MD2S_solver = NOT_AUTHORIZED
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
physical_evidence_effect = NONE
```

## 7. Nächster zulässiger Block bei PASS

`C-PHYS-R1.0-BACKGROUND-3C11_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_ONLY`
