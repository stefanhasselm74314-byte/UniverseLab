# ULSH-05 / WP1D2 — Kinematic invariant candidate ledger + projector solvability preflight v0.1

**Datum:** 2026-09-14  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Klassifikation:** analytisch · nichtoperativ · fail-closed  
**Basis-main:** `e8fd2594b5ac86e243b278a339a13705be03b725`

## 0. Kernstatus

Dieser Block setzt ausschließlich den von `ULSH-05/WP1D1` ausdrücklich benannten Nachfolger um:

`ULSH-05/WP1D2 = Kinematic invariant candidate ledger and projector solvability preflight`.

Er schließt **keine** physikalische Gaugefixierung, keinen physikalischen Modenraum, keinen Hamiltonschen Constraint-Quotienten und keinen Solver frei.

| Objekt | Status |
|---|---|
| `WP1D2_invariant_candidate_ledger` | `DERIVED_KINEMATICALLY_CONDITIONAL_REPRESENTATIVE_LEVEL` |
| `WP1D2_projector_solvability_preflight` | `DERIVED_FAIL_CLOSED_CLOSED_RANGE_NOT_PROVEN` |
| `WP1D2_pole_extension_audit` | `OPEN_NOT_PROVEN_COMPONENTWISE` |
| `WP1D_constraint_elimination` | `BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING` |
| `WP1D_physical_3plus1_SVT` | `NOT_RELEASED` |
| `WP1D_physical_DOF_count` | `NOT_RELEASED` |
| `WP1_physical_boundary_domain` | `BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA` |
| `PHYSICAL_BACKGROUND` | `NOT_ESTABLISHED` |
| `FM-G0` | `OPEN` |
| `K1-D` | `NOT_RELEASED` |
| `K1-E` | `NOT_ADMISSIBLE` |
| `SOLVER_EXECUTION` | `NOT_EXECUTED` |

`physical_gate_effect = NONE`  
`physical_evidence_effect = NONE`

---

## 1. Eingefrorene Ausgangsstruktur

WP1D1 liefert den strukturell vollständigen linearen kinematischen Gaugeoperator

`G = (G_zeta, G_lambda, G_rho)`

auf dem konditionalen Feldraum `D_cond`.

Die drei Spalten bleiben strikt getrennt:

1. `G_zeta`: 6D-Bulk-Diffeomorphismen plus die gekoppelte Embedding-Kompensation,
2. `G_lambda`: U(1),
3. `G_rho`: unabhängige intrinsische Reparametrisierung der Grenzfläche.

Die Interfacevariablen werden nicht aus dem Operator entfernt. Insbesondere gelten die von WP1D1 geschlossenen Zeilen

`delta_zeta xi = -zeta_perp`,

`delta_zeta tau_a = -zeta_parallel_a`,

`delta_lambda s = q_sigma lambda`,

`delta_lambda Acal_a = D_a lambda`,

`delta_lambda d_a = 0`,

`delta_rho H_ab = 2 D_(a rho_b)`.

Damit ist die frühere unvollständige WP1E-Vorläuferdarstellung **nicht** kanonisch. WP1D2 baut ausschließlich auf dem gemergten WP1D1-Operator auf.

**Status:** `[BEWIESEN/KINEMATISCH]` im deklarierten linearen Variationsvertrag.

---

## 2. Hintergrundansatz und Gültigkeitsbereich

Für die komponentenweise Analyse wird weiterhin der statische analytische Ansatz verwendet:

`dsbar_6^2 = exp(2A(r)) qbar_munu dx^mu dx^nu + dr^2 + L(r)^2 dchi^2`,

`phibar = phibar(r)`,

`Abar = Abar_chi(r) dchi`,

`chi ~ chi + 2pi`.

Wichtig:

`current static ansatz != established physical background`.

Alle komponentenweisen Polarkoordinatenformeln gelten zunächst nur auf dem punktierten Chart

`L(r) > 0`.

Der Übergang zu einem glatten Pol mit `L -> 0` benötigt eine getrennte kartesische oder orthonormale Fortsetzungsprüfung.

---

## 3. Rohoperator auf dem punktierten Polarchart

Schreibe den 4D-Anteil des Bulk-Gaugeparameters als

`zeta_mu = zetaT_mu + D_mu zeta_L`,

mit

`D^mu zetaT_mu = 0`

nur auf einem deklarierten York/Hodge-Repräsentantenschnitt.

Für kovariante interne Komponenten `zeta_A=(zeta_mu,zeta_r,zeta_chi)` folgt

`delta h_munu = 2 D_(mu zetaT_nu) + 2 D_mu D_nu zeta_L + 2 A' exp(2A) qbar_munu zeta_r`,

`delta h_mur = (partial_r - 2A') zetaT_mu + D_mu[zeta_r + (partial_r - 2A') zeta_L]`,

`delta h_muchi = partial_chi zetaT_mu + D_mu[zeta_chi + partial_chi zeta_L]`,

`delta h_rr = 2 partial_r zeta_r`,

`delta h_rchi = partial_r zeta_chi + partial_chi zeta_r - 2(L'/L) zeta_chi`,

`delta h_chichi = 2 partial_chi zeta_chi + 2 L L' zeta_r`.

Für den Bulk-Skalar:

`delta varphi = phibar' zeta_r`.

Für den Maxwellsektor, mit dem 4D-Skalarpotential `alpha`, gilt auf `L>0`:

`delta alpha = lambda + (Abar_chi/L^2) zeta_chi`,

`delta a_r = partial_r lambda + Abar_chi partial_r(zeta_chi/L^2)`,

`delta a_chi = partial_chi lambda + Abar_chi' zeta_r + Abar_chi partial_chi(zeta_chi/L^2)`.

Diese Formeln sind lokale Koordinatenformeln, keine globale Modenzerlegung.

---

## 4. Kompensatoren

Definiere auf demselben Repräsentantenschnitt

`X_r = B_r - 1/2 (partial_r - 2A') B`,

`X_chi = B_chi - 1/2 partial_chi B`.

Aus

`delta B = 2 zeta_L`,

`delta B_r = zeta_r + (partial_r - 2A') zeta_L`,

`delta B_chi = zeta_chi + partial_chi zeta_L`

folgt unmittelbar

`delta X_r = zeta_r`,

`delta X_chi = zeta_chi`.

**Status:** `[BEWIESEN/KINEMATISCH]`.

Diese Aussage benötigt weder `1/phibar'` noch `1/Abar_chi'`, `1/n`, `1/k` oder `D^-2`.

---

## 5. Kinematische Invariantenkandidaten

### 5.1 Tensor-/Vektorsektor

Kandidaten unter `G_zeta` auf dem gemeinsamen Repräsentantenschnitt:

`hhatTT_munu = hTT_munu`,

`Vhat_mur = VT_mur - (partial_r - 2A') VT_mu`,

`Vhat_muchi = VT_muchi - partial_chi VT_mu`,

`AhatT_mu = aT_mu`.

### 5.2 Skalarer Metrik-/Bulk-Skalarsektor

`Hhat = H - D^2 B - 8 A' exp(2A) X_r`,

`hhat_rr = h_rr - 2 partial_r X_r`,

`hhat_rchi = h_rchi - partial_r X_chi - partial_chi X_r + 2(L'/L) X_chi`,

`hhat_chichi = h_chichi - 2 partial_chi X_chi - 2 L L' X_r`,

`varphihat = varphi - phibar' X_r`.

Insbesondere bleibt `varphihat` auch für `phibar'=0` wohldefiniert. Es wurde keine unitary-gauge-artige Division eingeführt.

### 5.3 Maxwell-Skalarsektor

Zunächst

`u_r = a_r - partial_r alpha`,

`u_chi = a_chi - partial_chi alpha`.

Daraus folgt

`delta u_r = -(Abar_chi'/L^2) zeta_chi`,

`delta u_chi = Abar_chi' zeta_r`.

Mit den Kompensatoren erhält man

`Ahat_r = u_r + (Abar_chi'/L^2) X_chi`,

`Ahat_chi = u_chi - Abar_chi' X_r`,

und damit

`delta Ahat_r = 0`,

`delta Ahat_chi = 0`

unter `G_zeta + G_lambda` auf dem deklarierten lokalen Repräsentantenschnitt.

Auch hier wird nicht durch `Abar_chi'` dividiert; für `Abar_chi'=0` reduzieren sich die Kandidaten glatt auf `u_r,u_chi`.

**Status der gesamten Liste:** `[BEWIESEN/KINEMATISCH, KONDITIONAL AUF REPRÄSENTANTENSCHNITT UND L>0]`.

---

## 6. Warum dies noch keine vollständige Gaugeinvariantenbasis ist

Die intrinsische Oberflächenreparametrisierung `G_rho` bleibt unabhängig.

Für die bewegte induzierte Metrik gilt zwar

`G_zeta[H_ab] = 0`,

aber im Allgemeinen

`G_rho[H_ab] = Lie_rho hbar_ab = 2D_(a rho_b) != 0`.

Analog ist

`G_lambda[d_a] = 0`,

und im gepaarten Bulk-Embedding-Kanal

`G_zeta[d_a] = 0`,

aber

`G_rho[d_a] = Lie_rho wbar_a`

im Allgemeinen nicht null.

Daher gilt strikt:

`columnwise invariance != full-G invariance`.

Eine komponentenweise vollständige `G_rho`-invariante Interfacebasis wird hier **nicht** freigegeben.

---

## 7. Projector solvability preflight

Der zentrale funktionalanalytische Punkt ist unabhängig von den konkreten HZT-Koeffizienten.

Sei

`P : D(P) subset H1 -> H2`

ein dicht definierter Operator zwischen Hilberträumen und `P^dagger` sein Adjungierter, soweit auf der eingefrorenen analytischen Domäne definiert.

Dann gilt allgemein

`ker(P^dagger) = (Ran P)^perp`,

und damit

`closure(Ran P) = (ker(P^dagger))^perp`.

### 7.1 Exakte Lösbarkeit

Die Gleichung

`P u = f`

ist exakt lösbar genau dann, wenn

`f in Ran P`.

Daraus folgt als notwendige Bedingung

`f perpendicular ker(P^dagger)`.

Ohne zusätzlich bewiesene Abgeschlossenheit von `Ran P` folgt daraus jedoch nur

`f in closure(Ran P)`, 

nicht notwendigerweise

`f in Ran P`.

Damit ist die oft benutzte Kurzform

`f perpendicular ker(P^dagger) => P u=f solvable`

**ohne Closed-Range-Annahme zu stark**.

### 7.2 Closed-range-Upgrade

Ist separat bewiesen, dass

`Ran P = closure(Ran P)`,

so wird

`f perpendicular ker(P^dagger)`

zur hinreichenden Lösbarkeitsbedingung.

### 7.3 Eindeutigkeit

Ist `u0` eine Lösung, dann ist

`u0 + k`,  `k in ker P`

ebenfalls eine Lösung.

Eindeutigkeit entsteht daher erst nach Fixierung eines Komplements zu `ker P`, einer Normalisierungsbedingung oder einer legitimierten Gaugebedingung.

### 7.4 Relevante Projektoren

Für WP1D/WP1D1 sind insbesondere zu verfolgen:

`D^2`, `Delta_1`, `Delta_L`.

Aktuell gilt für alle drei globalen physikalischen Realisierungen:

`domain/pairing = NOT_FROZEN_PHYSICALLY`,

`closed range = NOT_PROVEN`,

`self-adjoint physical realization = NOT_PROVEN`,

`physical Green operator = NOT_FROZEN`.

Daher wird weder `D^-2` noch eine Pseudoinverse, ein retarded/advanced Greenoperator oder ein physikalischer Modenprojektor eingefroren.

**Status:** `[BEWIESEN]` für die abstrakten Hilbertraumidentitäten; `[OFFEN]` für ihre benötigten globalen HZT-Operatorhypothesen.

---

## 8. Lorentzsignatur- und Kausalitätsfirewall

Eine 4D-kovariante York/Hodge-Buchhaltung ist nicht automatisch ein global elliptischer Projektor auf der späteren physikalischen Lorentzdomäne.

Vor einer physikalischen Reduktion müssen mindestens feststehen:

- Zeit-/ADM-Wahl,
- physikalische Anfangs-/Randdomäne,
- Pairing und Operatorabschluss,
- Nullmodenkomplement,
- gegebenenfalls kausale Greenoperatorwahl,
- ULSH-04 Dirac-Bergmann-Klassifikation.

Daher gilt:

`formal coefficient decomposition != physical 3+1/SVT decomposition`.

---

## 9. Polarkoordinaten-Firewall

Nahe einem glatten Pol ist der Winkelchart singulär. Für die flache Kontrollebene

`ds^2 = dr^2 + r^2 dchi^2`

hat der glatte kartesische Translationsvektor

`partial_x = cos(chi) partial_r - [sin(chi)/r] partial_chi`.

Die kontravariante Winkelkomponente divergiert also wie `1/r`, während

`||partial_x||^2 = cos^2(chi) + r^2[sin^2(chi)/r^2] = 1`.

Damit ist bewiesen:

`divergent polar coordinate component != singular geometric field`.

Folglich dürfen Ausdrücke mit

`L'/L`, `zeta_chi/L^2`, `Abar_chi'/L^2`

am Pol nicht durch naive Komponentenbeschränktheit klassifiziert werden.

Erforderlich bleibt die glatte Fortsetzung in kartesischen oder orthonormalen Variablen.

**Status:** `[BEWIESEN]` als Koordinatengegenbeispiel; `[OFFEN]` für die globale WP1D2-Fortsetzung aller Kandidaten.

---

## 10. Grenzfälle

1. `phibar' -> 0`: `varphihat -> varphi`; keine Singularität.
2. `Abar_chi' -> 0`: `Ahat_r -> u_r`, `Ahat_chi -> u_chi`; keine Singularität.
3. interner Fouriermodus `n=0`: bleibt enthalten; es existiert kein `1/n`.
4. `A' -> 0`: unverwölbter Radialkontrollfall wird glatt erreicht.
5. `L' -> 0` bei `L>0`: zylindrischer lokaler Kontrollfall.
6. `L -> 0`: keine naive Auswertung der `1/L`- oder `1/L^2`-Komponentenformeln.
7. nichttrivialer Projektorkernel: Repräsentanten bleiben nicht eindeutig; daraus folgt kein physikalischer DOF-Count.

---

## 11. Dimensions-/Einheitencheck

WP1D2 führt keine neue dimensionsbehaftete physikalische Konstante ein. Die Kandidaten werden ausschließlich aus bereits gleichartig dimensionierten linearen Störungskoeffizienten und Hintergrundableitungen gebildet. Jede Summe ist durch die jeweilige Komponentenzerlegung homogen.

Insbesondere ist die Polarfirewall koordinatengeometrisch: Faktoren `L^-1` und `L^-2` stammen aus dem inversen Winkelmetrikfaktor und sind kein neuer UV-Massenscale.

Eine physikalische Normierung der 4D-Moden wird hier nicht behauptet.

---

## 12. Harte Negativresultate

`[FALSIFIZIERT/BLOCKIERT]` sind in diesem Block folgende Schlussketten:

- `kinematischer Invariantenkandidat => physikalischer Modus`,
- `Projektor-Nullmode => physikalischer Modus`,
- `Projektor-Nullmode => Gaugerichtung`,
- `f perpendicular ker(P^dagger) => exakte Lösbarkeit` ohne Closed Range,
- `rank(G) => physikalischer DOF-Count`,
- `lokale Polarkomponentenformel => globale glatte Polfortsetzung`,
- `numerische Nichtsingularität => Ghostfreiheit`,
- `grüne QA => physikalische Evidenz`.

---

## 13. Nächste mathematische Pflichten

WP1D2 weist bewusst **keine neue Successor-ID** zu.

Vor einer physikalischen Reduktion bleiben mindestens erforderlich:

1. physikalisch zulässige Zeit-/ADM- und Randdomäne,
2. Projektordomänen, Pairings und Adjungierte,
3. Nullmodenkomplemente,
4. Closed-Range-/Fredholm-Beweis oder Gegenbeispiel für die benötigten Operatoren,
5. kartesische/orthonormale Polfortsetzung,
6. ULSH-04 Dirac-Bergmann-Constraintklassifikation.

Erst danach kann ein reduzierter kinetischer Operator methodisch sinnvoll auf Ghost-/Gradientenstabilität geprüft werden.

---

## 14. Governance-Firewall

Unverändert:

```text
FM-G0                     OPEN
PHYSICAL_BACKGROUND       NOT_ESTABLISHED
WP1_physical_boundary_domain
                          BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA
WP1D_constraint_elimination
                          BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING
WP1D_physical_3plus1_SVT  NOT_RELEASED
WP1D_physical_DOF_count   NOT_RELEASED
WP1_full_quadratic_action NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM NOT_RELEASED
AuthorizationDecision     NOT_CREATED
SingleUseGrant            NOT_CREATED
BACKEND_IMPORT             NOT_EXECUTED
SOLVER_EXECUTION           NOT_EXECUTED
PHYSICAL_RESPONSE_RANK    NOT_EXECUTED
K1-D                       NOT_RELEASED
K1-E                       NOT_ADMISSIBLE
physical_gate_effect       NONE
physical_evidence_effect   NONE
```
