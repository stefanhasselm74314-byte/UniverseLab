# ULSH-01 / MD2S-BVP — WP2 Physical Release Review Ledger v1.0

**Datum:** 2026-08-11  
**Architektur:** `HPVS -> HZT-M0 -> HZT-Full`  
**Pfad:** `HZT-M0 -> S6 -> C-PHYS -> C1 -> ULSH-01 -> WP2-RR`  
**Review-Baseline:** `437b4e14edb65ae6abf7362d6247fe285026bf6b`  
**Status:** `BLOCKED_WP2_PHYSICAL_RELEASE_REVIEW_NO_SOLVE`  
**Evidenzeffekt:** `NONE`

## 1. Entscheidung

Der gemergte WP2-Stand ist als **Transaktionsrahmen** belastbar, aber noch **nicht sicher genug für die Erzeugung eines physischen Solve-Releases oder Single-Use-Grants**.

Der Review bestätigt die wesentlichen WP2-Stärken: unveränderter CP01R1-Payload, `a_F=1/4`, deterministischer 7x5-Plan, Source-/Backend-Bindings, fail-closed Release-/Grant-Pfad, atomarer Single-Use-Spend und Replay-/Crash-Schutz.

Trotzdem blockieren vier konkrete Lücken die Freigabe. Daher gilt:

`WP2 transaction-ready != physical-release-ready`.

Es wurde **kein Solver ausgeführt**, kein Release erzeugt und kein Grant erzeugt.

## 2. Review-Baseline

Kanonischer Commit:

`437b4e14edb65ae6abf7362d6247fe285026bf6b`

Run:

`HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1`

Payload-SHA-256:

`0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302`

Die drei relevanten CI-Gates des Baseline-Commits waren grün:

- ULSH-01 WP2 physical transaction no-solve contract — Run `31402294613`
- Research contracts — Run `31402294359`
- UniverseLab dated file naming contract — Run `31402294515`

## 3. Bestätigte Stärken

### Source- und Target-Bindung

Der Review bestätigt:

- WP2-Contract Git blob `f384801d5693c35a93863c59fa413121061dfdb0`
- Target Entry Point Git blob `ea02d02f61e8c072c1191577c1bf7660038ad516`
- Transaction Guard Git blob `110ca418cfed89f9661018c499342a0cd3bc6821`
- Resource Policy Git blob `954a9730d3fa34864df7168555912ebba2dd6c3d`
- Result Schema Git blob `b1fdf45aa9fb3d585e73795e9294dfa0c185fc39`
- Preregistration Git blob `9789101e0a168580b6906eb21edad5a5db2b64ce`

### Target-Schedule

Unverändert:

- `a_F = 1/4`
- 7 deterministische Seeds
- Knoten `24, 32, 48, 64, 96`
- insgesamt 35 geplante Primary-Einträge
- kein Parameter-Scan
- keine Random-Restarts
- keine adaptive Mesh-Insertion
- Independent Backend nur nach Primary-Numerical-Candidate

### Single-Use-Semantik

Der Grant-Spend ist weiterhin fail-closed und replay-sicher angelegt. Ein bereits verbrauchter Grant darf nach Erfolg, Fehler oder Crash nicht wiederverwendet werden.

Diese Punkte reichen jedoch nicht für eine physische Solve-Freigabe, solange die nachfolgenden Blocker offen sind.

## 4. RR-B01 — Per-Seed/Per-Level-Timeout fehlt

**Status:** `BLOCKER`

Die eingefrorene Resource Policy verlangt:

`maximum_wall_clock_seconds_per_seed_per_level = 1800 s`.

Der aktuelle WP2-Transaction Guard erzwingt nur das Gesamtbudget:

`maximum_wall_clock_seconds_total = 21600 s`.

Damit könnte ein einzelner Seed/Mesh-Schritt länger als 1800 s laufen und trotzdem unter dem Gesamtbudget bleiben.

### Erforderliche Korrektur

Jeder der 35 geplanten Schedule-Einträge muss innerhalb eines deterministischen Stage-Timeouts laufen. Bei Überschreitung muss exakt die eingefrorene Timeout-Semantik greifen:

`CLASSIFY_NOT_EXECUTED_OR_NO_CANDIDATE_FOR_AFFECTED_STAGE_AND_PRESERVE_COMPLETE_LOG`.

Kein Retry mit veränderter Methode oder erhöhtem Budget.

## 5. RR-B02 — Result-Byte-Budget wird nicht erzwungen

**Status:** `BLOCKER`

Die Resource Policy verlangt:

`maximum_result_bytes = 1073741824 B = 1 GiB`.

WP2 bindet diesen Wert deklarativ, erzwingt ihn beim Staging/Commit aber nicht.

### Erforderliche Korrektur

Die Summe aller Result-/Auxiliary-Artefakte muss vor Commit gegen das 1-GiB-Budget geprüft werden. Bei Überschreitung: fail-closed, kein Overwrite, kein Retry mit geänderter Methode; der Single-Use-Grant bleibt verbraucht.

## 6. RR-B03 — Result-/QA-Artefaktclosure unvollständig

**Status:** `BLOCKER`

Die Preregistration verlangt unter anderem:

- per-seed convergence log,
- per-mesh residual table,
- alle acht Boundary-Residuals,
- `rr`-Constraint-Profil,
- Profile-/Augmented-Convergence,
- Spectral-Tail-Tabelle,
- diagnostische RRQR-/SVD-/Condition-Daten,
- Independent-Backend-Vergleich,
- maschinenlesbare Final Classification.

Das eingefrorene Result Schema verlangt zusätzlich eine schema-konforme Struktur mit `primary_backend`, `independent_backend`, `candidate_inventory`, `acceptance_audit` und den Kandidatenartefakt-Hashes.

Der aktuelle WP2-Targetpfad liefert dagegen nur einen kompakten Raw-Matrix-Record. Für mehrere zwingende QA-Kanäle werden die zugrunde liegenden Daten nicht verlustlos konserviert.

### Konsequenz

Ein Single-Use-Solve könnte numerisch laufen, den Grant verbrauchen und danach einen Datensatz hinterlassen, aus dem das preregistrierte Resultat nicht vollständig rekonstruiert werden kann.

Das ist vor Release unzulässig.

### Erforderliche Korrektur

Die Ausführung muss alle zwingenden Run-Artefakte verlustlos erfassen und entweder unmittelbar schema-konform schreiben oder in einem formal definierten, verlustlosen Quarantäneformat ablegen, aus dem `result.json` deterministisch erzeugt werden kann.

## 7. RR-B04 — CPU-/BLAS-Attestation unvollständig

**Status:** `BLOCKER`

Die Resource Policy verlangt ausdrücklich:

`cpu_and_blas_metadata_required = true`.

WP2 protokolliert Python-Version, Dependency-Versionen, Thread-Variablen und logische Kerne. Es fehlt jedoch eine positive CPU-Identifikation sowie BLAS/LAPACK-Implementationsmetadaten.

### Erforderliche Korrektur

Die immutable Runtime-Attestation muss mindestens enthalten:

- CPU-/Machine-/Processor-Identität,
- OS/Architektur,
- NumPy/SciPy BLAS-/LAPACK-Konfiguration,
- Threading-Konfiguration,
- exakte Dependency-Versionen,
- Backend-/Source-Hashes.

## 8. Hinweise ohne aktuellen Byte-Blocker

### RR-W01 — Dependency-Lock-Pfad

WP2 nennt den Background3B-Lock, die Resource Policy den Background3C-Lock. Beide Dateien sind derzeit byte-identisch und haben denselben Git blob:

`2c3a8126fc5ec23bd82f0e99d6922610d9250bfc`.

Aktuell liegt daher **kein Dependency-Byte-Mismatch** vor. Der Pfad sollte beim Hardening trotzdem semantisch vereinheitlicht werden.

### RR-W02 — Raw-Quarantäne versus kanonischer Result-Pfad

Das Result Schema definiert:

`artifacts/hzt-m0/md2s/background3c/<run_id>/<authorization_decision_id>/`.

WP2 schreibt einen späteren Raw-Lauf zunächst in ein externes Transaktionsverzeichnis. Das ist als Schutz gegen Repository-Mutationen sinnvoll, benötigt aber einen expliziten, verlustlosen Promotion-/Packaging-Vertrag.

## 9. Statushygiene

### bewiesen / formal geschlossen

- Review-Baseline ist content-addressed fixiert.
- Release und Grant fehlen weiterhin.
- kein numerischer Backend-Aufruf ist Bestandteil dieses Reviews.
- die vier Blocker sind aus den eingefrorenen Verträgen und dem WP2-Quellstand reproduzierbar.

### numerisch bestätigt

Keine physische CP01R1-Lösung. Nur No-Solve-Audit-/CI-Logik.

### konditional

Nach Schließung von RR-B01 bis RR-B04 kann ein **neuer** Physical Release Review stattfinden.

### offen

- physischer Solve,
- numerischer Kandidat,
- Kontinuums-Jacobianrang,
- Fredholm-Eigenschaft,
- Stabilität/Ghostfreiheit,
- physische Identifikation.

### blockiert

- Physical Solve Release Authorization,
- Single-Use Execution Grant,
- CP01R1-Solve,
- downstream R1.1/R1.2,
- K1-D,
- K1-E.

## 10. Nächster zulässiger Schritt

`ULSH-01 / WP2-H — Release Hardening`

Ziel: RR-B01 bis RR-B04 vollständig schließen, **weiterhin ohne physischen Solve**. Danach muss der geänderte Source-Bundle-Stand erneut content-addressed reviewed werden.

Bis dahin gilt ausdrücklich:

`DO NOT CREATE PHYSICAL SOLVE RELEASE OR SINGLE-USE GRANT`.
