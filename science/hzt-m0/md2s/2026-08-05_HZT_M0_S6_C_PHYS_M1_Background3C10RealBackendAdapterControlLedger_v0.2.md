# HZT-M0-S6-C-PHYS-M1 — Background-3C10 Real-Backend Adapter Control Ledger v0.2

**Datum:** 2026-08-05  
**Track:** `MD2S-R1-C-PHYS`  
**Block:** `C-PHYS-R1.0-BACKGROUND-3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_ONLY`

## 1. Append-only Korrektur

Der erste Kontrolllauf

```text
HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R1
```

wurde fail-closed beendet, bevor ein Kandidaten-Handoff oder eine unabhängige Backend-Auswertung stattfand. Ursache war die vorab nicht validierte Annahme, dass für alle Primärnetze derselbe Bulk-Residualgrenzwert `1e-9` gelten könne.

Der R1-Status bleibt dauerhaft:

```text
FAIL_CLOSED_PRIMARY_UNIFORM_BULK_THRESHOLD_AT_N96
```

Er wird weder überschrieben noch nachträglich zu PASS umgedeutet.

## 2. Rohbefund nach R1

Eine separate read-only Rohmessung ohne Newton-Aufruf ergab:

| N | Bulk-Residual ∞ | Constraint ∞ | Boundary-Abstand |
|---:|---:|---:|---:|
| 24 | 6.845900235585844e-11 | 1.3877787807814457e-17 | 1.0458300891968975e-13 |
| 48 | 1.929132270594991e-10 | 1.3877787807814457e-17 | 2.744471316873387e-13 |
| 96 | 1.7027736345931466e-08 | 1.3877787807814457e-17 | 1.084909939663703e-12 |

Der achtkomponentige Kontroll-Handoff war auf allen drei Netzen identisch; sein Digest lautet:

```text
6a00f71f4904574841d17eaebba7f8318fc136d477ab6fd324f3354f1b33e400
```

Die N=96-Abweichung ist mit Hochordnungs-Differentiationsrundung vereinbar, aber dieser Mechanismus gilt nicht als bewiesen. Aus den Werten folgt insbesondere kein Kontinuumskonvergenzsatz.

## 3. Neuer Kontrolllauf R2

Jede Änderung eines Akzeptanzvertrags erfordert eine neue Kontrollidentität:

```text
HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R2
```

Unverändert bleiben:

- Modellparameter und Topologiesektor,
- exakter analytischer Kontrollwert `a_F=0`,
- Primärnetze `24,48,96`,
- Independent-Cutoffs `1e-3,5e-4,2.5e-4`,
- reale Backendquellen,
- Handoff-Schema,
- Prozess- und Artefaktfirewalls.

Geändert wird ausschließlich die versionierte Primär-Akzeptanzhülle:

```text
N=24  ≤ 1e-9
N=48  ≤ 1e-9
N=96  ≤ 3e-8
```

Der N=96-Kanal trägt die atomare Klassifikation:

```text
HIGH_ORDER_DIFFERENTIATION_ROUNDOFF_ENVELOPE_CONTROL_ONLY
```

Monotone Bulk-Konvergenz wird nicht verlangt und darf nicht inferiert werden.

## 4. Numerische und physische Grenze

R2 darf weiterhin ausschließlich:

- Primärresiduen des exakten `a_F=0`-Kontrollzustands auswerten,
- den hashgebundenen Kontrollvektor an das Independent-Modul übergeben,
- sechs DOP853-Regionalintegrationen ausführen,
- reale Import-, Timeout-, Signal-, Schema- und Artefaktkontrollen durchführen.

R2 darf nicht:

- `damped_newton` aufrufen,
- einen Shooting-Jacobian bilden,
- einen Root-Solver verwenden,
- CP01R1 oder `a_F=1/4` ausführen,
- einen Grant oder ein physisches Ergebnis erzeugen.

## 5. Unveränderte Gates

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

## 6. Nächster zulässiger Block bei R2-PASS

`C-PHYS-R1.0-BACKGROUND-3C11_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_ONLY`

Auch 3C11 darf keine automatische Ausführung oder Grant-Erzeugung vornehmen.
