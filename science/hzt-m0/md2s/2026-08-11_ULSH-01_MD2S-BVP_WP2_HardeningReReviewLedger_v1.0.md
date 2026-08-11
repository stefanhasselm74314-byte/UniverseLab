# ULSH-01 / MD2S-BVP — WP2-RR2 Hardening Re-Review Ledger v1.0

**Datum:** 2026-08-11  
**Architektur:** `HPVS -> HZT-M0 -> HZT-Full`  
**Pfad:** `HZT-M0 -> S6 -> C-PHYS -> C1 -> ULSH-01 -> WP2-RR2`  
**Review-Status:** `BLOCKED_WP2_RR2_NEW_RELEASE_BLOCKERS_FOUND_NO_SOLVE`  
**Evidenzeffekt:** `NONE`

## 1. Ziel

WP2-RR2 prüft den gemergten WP2-H-Stand unabhängig gegen die bereits eingefrorenen Preregistration-, Resource- und Result-Schema-Verträge. Der Review darf weder einen Release noch einen Grant erzeugen und führt keinen Newton-, Shooting-, IVP- oder BVP-Solve aus.

Reviewbasis:

- WP2-H Merge: `6a79ee11268f37df6ba98b4d64807bef9550f8db`
- aktueller `main`: `b10f3fb3029e1092b6aa8a7a9875f869f734d78d`
- zwischen beiden Commits wurden nur UniverseLab-Vergleichsrechner-Dateien verändert; die WP2-H-Source-Blobs sind unverändert.

## 2. Ergebnis der ursprünglichen vier RR-Blocker

Die vier im ersten Release Review gefundenen Implementierungslücken sind in ihrem **ursprünglichen engen Scope** tatsächlich geschlossen:

| ursprüngliches Gate | RR2-Befund |
|---|---|
| RR-B01 per Seed/Mesh-Level Timeout | `VERIFIED_CLOSED_IN_ORIGINAL_SCOPE` |
| RR-B02 1-GiB Resultatbudget | `VERIFIED_CLOSED_IN_ORIGINAL_SCOPE` |
| RR-B03 Pflichtkanäle/QA/Result-Capture | `VERIFIED_CLOSED_IN_ORIGINAL_SCOPE` |
| RR-B04 CPU/BLAS/LAPACK-Metadaten | `VERIFIED_CLOSED_IN_ORIGINAL_SCOPE` |

Damit war WP2-H kein Scheinerfolg: Die dort implementierten vier Maßnahmen sind im Code vorhanden und reproduzierbar. RR2 findet jedoch zusätzliche, bislang nicht geprüfte Release-Blocker in den bereits eingefrorenen Verträgen.

## 3. Neuer Blocker RR2-B01 — Existing-Path Preflight zu spät

Der eingefrorene ResultSchema-Vertrag verlangt:

`existing_path_action = ABORT_BEFORE_SOLVER_INITIALIZATION`

Im gehärteten Transaction-Pfad ist die Reihenfolge derzeit:

1. Release/Grant validieren,
2. Grant atomar verbrauchen,
3. physischen Target-Schedule ausführen,
4. **erst danach** `result_dir.exists()` prüfen.

Damit kann eine bereits vorhandene immutable Resultatadresse erst nach Solverausführung entdeckt werden.

**Status:** `BLOCKER`

**Erforderliche Schließung:** Alle transaktionalen und kanonischen Zielpfade müssen aus dem validierten Grant vor Grant-Spend/Backendimport/Solverinitialisierung abgeleitet und auf Kollision geprüft werden.

## 4. Neuer Blocker RR2-B02 — Ein-Thread-Grenze nicht vor BLAS-Initialisierung erzwungen

Die eingefrorene Resource Policy verlangt:

`thread_count = 1`

und

`maximum_cpu_threads = 1`.

Der aktuelle Ablauf ruft `validate_runtime()` auf, das NumPy/SciPy zur BLAS/LAPACK-Attestation importiert. Erst später setzt `enforce_process_limits()` die Thread-Umgebungsvariablen auf `1`. Zusätzlich akzeptiert `validate_runtime()` Werte `UNSET` oder `1`.

Ein BLAS-Backend kann dadurch bereits mit seiner Default-Threadzahl initialisiert worden sein, bevor die Variablen nachträglich auf `1` gesetzt werden.

**Status:** `BLOCKER`

**Erforderliche Schließung:** Vor dem ersten NumPy-/SciPy-/Backendimport müssen alle Thread-Control-Variablen fail-closed exakt auf `1` stehen; zusätzlich ist die effektive numerische Threadpool-Grenze positiv zu attestieren.

## 5. Neuer Blocker RR2-B03 — Gesamt-Wallclock nicht durchgehend hart begrenzt

Die 35 einzelnen Schedule-Einträge besitzen einen per-entry Timer. Nach dem Schedule-Loop läuft jedoch `_finalize(...)` ohne aktiven Gesamt-Timer. Erst nach dessen Rückkehr wird

`execution_elapsed_wall_clock_seconds`

berechnet. Die Transaction kann bei negativem Restbudget die Packaging-Phase abbrechen, aber dann wurde die Gesamtgrenze bereits überschritten.

**Status:** `BLOCKER`

**Erforderliche Schließung:** Ein unabhängiger Gesamt-Deadline-Guard muss Schedule, Target-Finalisierung und immutable Packaging vollständig überspannen; die per-entry Timer bleiben als strengere innere Limits erhalten.

## 6. Neuer Blocker RR2-B04 — Higher-Precision-Pfad fehlt

Die Preregistration friert ausdrücklich ein:

`80_BIT_OR_GREATER_REQUIRED_FOR_ANY_BORDERLINE_ACCEPTANCE`

Der aktuelle Target-Pfad arbeitet ausschließlich mit dem binary64-Primärpfad und besitzt weder eine >=80-Bit-Reevaluation noch eine fail-closed Borderline-Klasse. Damit könnte ein knapp innerhalb der Akzeptanzschwelle liegender Kandidat ohne preregistrierten Precision-Audit als `NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC` klassifiziert werden.

**Status:** `BLOCKER`

**Erforderliche Schließung:** Vor Ausführung ist eine objektive Borderline-Zone zu definieren. Jeder Kandidat in dieser Zone benötigt einen >=80-Bit-Audit; ist dieser nicht verfügbar oder nicht eindeutig bestanden, darf kein akzeptierter Kandidatenstatus vergeben werden.

## 7. Warnung RR2-W01 — Quarantänepfad und kanonischer Pfad

Die externe Quarantäne wird aktuell unter

`results/<grant_nonce>/`

geschrieben. Das frozen ResultSchema nennt dagegen

`artifacts/hzt-m0/md2s/background3c/<run_id>/<authorization_decision_id>/`.

Das Manifest enthält zwar bereits ein zukünftiges byte-for-byte Promotion Target, aber noch keinen ausführbaren/verifizierenden Promotion-Vertrag. Das ist nach RR2 kein eigener Solve-Blocker, sollte jedoch im nächsten Hardening-Pass gemeinsam mit RR2-B01 bereinigt werden.

## 8. Governance

Der RR2-Befund verändert keinerlei physikalischen Status:

- `physical_solve_authorized = false`
- `physical_solve_executed = false`
- `release_authorization_present = false`
- `single_use_grant_present = false`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`

Weder ein erfolgreicher Software-Audit noch eine spätere numerische Konvergenz ist ein Existenzbeweis, eine physikalische Identifikation, ein Stabilitätsbeweis oder ein Ghostfreiheitsnachweis.

## 9. Nächster zulässiger Schritt

`ULSH-01 / WP2-H2 — RR2-B01 bis RR2-B04 technisch schließen, weiterhin NO SOLVE.`

Erst danach ist ein erneuter unabhängiger Review zulässig. Release, Single-Use-Grant und CP01R1-Ausführung bleiben bis dahin verboten.
