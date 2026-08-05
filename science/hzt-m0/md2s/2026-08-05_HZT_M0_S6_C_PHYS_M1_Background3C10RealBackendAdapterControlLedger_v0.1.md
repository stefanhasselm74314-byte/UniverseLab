# HZT-M0-S6-C-PHYS-M1 — Background-3C10 Real-Backend Adapter Control Ledger v0.1

**Datum:** 2026-08-05  
**Track:** `MD2S-R1-C-PHYS`  
**Block:** `C-PHYS-R1.0-BACKGROUND-3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_ONLY`

## 1. Zweck

Background-3C10 schließt genau die in Background-3C9 identifizierte Softwarelücke: Die in 3C8 geprüfte Adaptermechanik wird erstmals mit den realen Primär- und Independent-Modulen durchlaufen. Zulässig ist ausschließlich der bereits bekannte exakte analytische Kontrollfall mit

\[
a_F=0.
\]

Der eingefrorene physische Zielwert

\[
a_F=\frac14
\]

wird weder ausgewertet noch gelöst. CP01R1 bleibt unangetastet.

## 2. Reale Primärkontrolle

Das Primärmodul `background_3c_primary_kernel_v0.2.py` wird in einem isolierten Unterprozess importiert. Für die Netze

\[
N\in\{24,48,96\}
\]

wird ausschließlich `control_seed_state(N)` erzeugt und mit `residual(...)` ausgewertet.

Nicht aufgerufen werden:

- `damped_newton`,
- `complex_step_jacobian`,
- `rrqr_step`.

Akzeptanz:

- Bulk-Residualnorm höchstens `1e-9`,
- Constraint-Norm höchstens `1e-10`,
- Abstand zum analytischen Boundary-Vektor höchstens `5e-10`,
- netzübergreifender Abstand des achtkomponentigen Handoff-Vektors höchstens `1e-13`.

## 3. Hashgebundener Kandidaten-Handoff

Der Primärprozess serialisiert ausschließlich

```text
varphi_N_0, q_N, A_S_0, varphi_S_0,
q_S, rho_N, rho_S, k4
```

in kanonischem JSON. Der SHA-256-Digest wird vor der unabhängigen Auswertung erneut berechnet. Eine absichtliche Digest-Manipulation muss fail-closed zurückgewiesen werden.

Dieser Vektor ist ein analytischer Kontrollvektor und kein physischer Hintergrundkandidat.

## 4. Reale unabhängige Kontrolle

Das unabhängige x-Raum-Modul wird in einem zweiten isolierten Prozess importiert. Für

\[
\epsilon\in\{10^{-3},5\times10^{-4},2.5\times10^{-4}\}
\]

werden Nord- und Südregion jeweils einmal mit DOP853 integriert. Insgesamt sind genau sechs Integrationsaufrufe zulässig.

Nicht aufgerufen werden:

- `centered_fd_jacobian`,
- ein Shooting-Root-Solver,
- `least_squares`,
- ein allgemeiner `root`-Aufruf.

Akzeptanz:

- Profilfehler höchstens `2e-8`,
- Constraint-Norm höchstens `2e-10`,
- Boundary-Abstand zur analytischen Lösung höchstens `2e-8`,
- Primär–Independent-Abstand höchstens `2e-8`,
- Shooting-Jacobian-Zähler exakt null.

## 5. Prozess- und Artefaktkontrollen

Die realen Module werden zusätzlich in zwei Sicherheitsproben importiert:

1. Primärimport, danach kontrollierter Timeout und Terminierung.
2. Independent-Import, danach absichtliches `SIGTERM`.

Die übergeordnete Transaktion erzwingt:

- einen Thread,
- deterministischen Python-Hash-Seed,
- begrenzten Adressraum, CPU-Zeit, Dateigröße und offene Dateien,
- begrenzte stdout/stderr-Erfassung,
- externe temporäre Kontrollpfade,
- atomaren Verzeichniswechsel,
- No-Overwrite.

Die Resultatschema-Übersetzung wird nur als vollständige Feldabbildung geprüft. Sie erzeugt kein physisches Resultat.

## 6. Interpretation Firewall

Ein PASS von Background-3C10 bedeutet ausschließlich:

> Die realen Backendmodule können im exakten analytischen \(a_F=0\)-Kontrollfall über die isolierte Adaptergrenze importiert, ausgeführt, hashgebunden übergeben, gemeinsam klassifiziert und sauber abgebrochen werden.

Ein PASS bedeutet ausdrücklich nicht:

- CP01R1 wurde ausgeführt,
- der Zielwert \(a_F=1/4\) wurde gelöst,
- ein physischer Hintergrund existiert,
- die Lösung ist eindeutig,
- der Kontinuumsoperator ist Fredholm,
- der volle Jacobian ist invertierbar,
- Stabilität oder Ghostfreiheit liegt vor,
- K1-D oder K1-E darf geöffnet werden,
- physische Evidenz wurde erzeugt.

## 7. Unveränderte Gates

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

## 8. Nächster zulässiger Block bei PASS

`C-PHYS-R1.0-BACKGROUND-3C11_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_ONLY`

3C11 ist erneut ausschließlich ein Review. Es darf weder automatisch einen operativen Grant erzeugen noch CP01R1 starten.
