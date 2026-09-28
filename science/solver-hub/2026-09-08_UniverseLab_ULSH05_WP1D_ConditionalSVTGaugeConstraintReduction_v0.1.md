# UniverseLab — ULSH-05 / WP1D
## Conditional S/V/T gauge-and-constraint reduction domain v0.1

**Datum:** 2026-09-08  
**Modellidentität:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `51a48f23c9b32480ce56b0fb247b14d012fb4a0e`  
**Klassifikation:** `ANALYTIC_NONOPERATIVE_CONDITIONAL_GAUGE_AND_CONSTRAINT_REDUCTION_DOMAIN`  
**Physical gate/evidence effect:** `NONE / NONE`

## 0. Entscheidung und Successor-ID

WP1C4B2C blockiert die physikalische Randdomäne fail-closed, weil physischer 6D-Hintergrund, Kausalstruktur und globaler Outer-Boundary/Corner-Vertrag nicht freigegeben sind. Der dort vorgeschriebene Fallback ist deshalb ausschließlich eine **konditionale S/V/T-Gauge- und Constraint-Reduktionsdomäne ohne Solverausführung**.

Dieser Nachfolgevertrag weist diesem Fallback erstmals die kanonische ID

`ULSH-05/WP1D`

zu. Diese ID wird durch diesen Successor-Vertrag neu vergeben und nicht rückwirkend als bereits im Vorgänger vorgegeben dargestellt.

Kernstatus:

```text
WP1D_successor_identifier          = FROZEN_BY_THIS_SUCCESSOR_CONTRACT
WP1D_analytic_field_domain         = FROZEN_CONDITIONAL
WP1D_4D_covariant_SVT_bookkeeping = DEFINED_CONDITIONAL_PROJECTOR_KERNELS_OPEN
WP1D_gauge_action                  = DEFINED_KINEMATICALLY_WITH_INDEPENDENT_SURFACE_REPARAMETERIZATION
WP1D_constraint_elimination        = BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING
WP1D_physical_3plus1_SVT           = NOT_RELEASED
WP1D_physical_DOF_count            = NOT_RELEASED
WP1_full_quadratic_action          = NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM          = NOT_RELEASED
SOLVER_EXECUTION                   = NOT_EXECUTED
```

[BEWIESEN] Eine konditionale kinematische Feld- und Gauge-Domäne kann definiert werden.

[FALSIFIZIERT/BLOCKIERT] Daraus folgen weder eine physikalische 3+1-S/V/T-Zerlegung noch ein physischer DOF-Count oder eine physische Constraint-Elimination.

---

## 1. Kanonische Quellenkette

Verwendet werden ausschließlich:

1. `SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md`
2. `registry/2026-08-03_MD2S_R1_C_PHYS_GlobalConventionFreezeContract_v0.1.json`
3. `registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json`
4. `science/solver-hub/2026-08-07_ULSH-04_Constraint_Roadmap_v1.0.md`
5. `science/solver-hub/2026-08-07_ULSH-05_SVT-Perturbation_Roadmap_v1.0.md`
6. `science/solver-hub/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.md`
7. `science/solver-hub/2026-09-07_UniverseLab_ULSH05_WP1C3_CapBendingJunctionGeometry_v0.1.md`
8. `registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2A_BoundarySecondVariationMaster_v0.1.json`
9. `registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2B_ComponentBoundaryResidualLinearization_v0.1.json`
10. `registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2C_GlobalBoundaryDomainPreflight_v0.1.json`
11. `registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInventory_v1.0.json`

Keine ΛCDM-, C1-V-, HZT-Full-, historische A0- oder Visualisierungsvariable wird als physische HZT-M0-Perturbationsvariable importiert.

---

## 2. Feldraum vor Reduktion

Bulk:

\[
\Psi_{\rm bulk}=(h_{AB},\varphi,a_A).
\]

Gemeinsames Interface:

\[
\Psi_\Sigma=(s,\xi,\tau_a),
\]

mit

- \(h_{AB}\): metrischer Perturbation,
- \(\varphi\): Bulk-Skalarperturbation,
- \(a_A\): U(1)-Potentialperturbation,
- \(s\): Kappenphasenperturbation,
- \(\xi\): normaler Interfaceverschiebung,
- \(\tau_a\): tangentialem Einbettungsrepräsentanten.

Diese Variablen sind kinematische lineare Daten und noch keine physikalischen Moden.

---

## 3. Konditionale analytische Domäne

Lokal sei

\[
\mathcal M_s\sim M_4\times D_{2,s},
\qquad \chi\sim\chi+2\pi.
\]

Der Fallback-Bereich \(\mathcal D_{\rm cond}\) enthält glatte lineare Störungen mit:

1. kompaktem tangentialen Support in randlosem \(M_4\), beziehungsweise \(\operatorname{supp}u\Subset\operatorname{int}M_4\) bei einem endlichen randtragenden Slab;
2. \(2\pi\)-Periodizität in \(\chi\), modulo der eingefrorenen U(1)-Patchstruktur;
3. Polregularität durch glatte kartesische Fortsetzbarkeit;
4. Erhaltung des Zwei-Seiten-Gluings und der Moving-Interface-Kinematik;
5. Abschluss unter **allen** zugelassenen Gaugegeneratoren: Bulk-Diffeomorphismus, U(1) und unabhängige intrinsische Interface-Reparametrisierung.

Für einen echten skalaren Fouriermodus

\[
f(r,\chi)=\sum_{n\in\mathbb Z}f_n(r)e^{in\chi}
\]

gilt am glatten Pol als Kontrollfall

\[
f_n(r)=O(r^{|n|}),\qquad r\to0.
\]

[FIREWALL] Diese skalare Potenzregel wird nicht blind auf One-Form- oder Tensorkomponenten übertragen.

Für die intrinsische Interface-Reparametrisierung wird **ein gemeinsamer** Generator \(\rho^a(y)\) auf dem bereits geglueten Interface benutzt. Er muss dieselben Support-, Periodizitäts-, Pol- und Gluingbedingungen erhalten.

---

## 4. Gaugegruppe und lineare Wirkung

### 4.1 6D-Bulk-Diffeomorphismus

Für \(\zeta^A\) benutzen wir die aktive lineare Konvention

\[
\delta_\zeta h_{AB}=2\bar\nabla_{(A}\zeta_{B)},
\]

\[
\delta_\zeta\varphi=\zeta^A\partial_A\bar\phi,
\]

\[
\delta_\zeta a_A=\mathcal L_\zeta\bar A_A.
\]

### 4.2 U(1)

Mit \(\lambda\):

\[
\delta_\lambda a_A=\partial_A\lambda,
\qquad
\delta_\lambda s=q_\sigma\lambda.
\]

Daher ist

\[
\boxed{d_a=D_as-q_\sigma\mathcal A_a}
\]

unter U(1) invariant:

\[
\delta_\lambda d_a
=D_a(q_\sigma\lambda)-q_\sigma D_a\lambda=0.
\]

[BEWIESEN] Diese U(1)-Invarianz gilt für konstantes \(q_\sigma\).

Sie darf nicht mit intrinsischer Oberflächenkoordinateninvarianz verwechselt werden: unter einer Interface-Reparametrisierung transformiert \(d_a\) als Interface-One-Form-Perturbation.

### 4.3 Moving Interface unter Bulk-Diffeomorphismus

Am Interface:

\[
\zeta^A|_\Sigma=\zeta_\perp N^A+\zeta_\parallel^a e_a{}^A.
\]

Für den Einbettungsrepräsentanten:

\[
\delta_\zeta\xi=-\zeta_\perp,
\qquad
\delta_\zeta\tau_a=-\zeta_{\parallel a}.
\]

Mit

\[
H_{ab}=p_{ab}+2\xi K_{ab}+2D_{(a}\tau_{b)}
\]

und

\[
\delta_\zeta p_{ab}
=2D_{(a}\zeta_{\parallel b)}+2K_{ab}\zeta_\perp
\]

folgt

\[
\boxed{\delta_\zeta H_{ab}=0}.
\]

[BEWIESEN/KINEMATISCH] Dies ist die Bulk-Diffeomorphismus-Kompensation der doubly-covariant Moving-Interface-Konstruktion.

### 4.4 Unabhängige intrinsische Interface-Reparametrisierung

WP1C3 hält ausdrücklich eine **zweite**, vom Bulk-Diffeomorphismus unabhängige Symmetrie fest:

\[
y^a\rightarrow y^a+\rho^a(y).
\]

Daher gilt zwingend

\[
\boxed{
\rho^a\ \text{ist nicht mit}\ \zeta_\parallel^a\ \text{zu identifizieren}.
}
\]

In der hier benutzten aktiven Repräsentantenkonvention schreiben wir

\[
\delta_\rho\tau^a=+\rho^a,
\qquad
\delta_\rho\xi=0.
\]

Bulkfelder erhalten dadurch keine zusätzliche Bulk-Gaugetransformation. Stattdessen werden die **Interface-Pullbackrepräsentanten** reparametrisiert. Für eine Perturbation \(t\) eines Hintergrund-Pullbacks \(\bar T\) gilt schematisch

\[
\boxed{
\delta_\rho t=\mathcal L_\rho\bar T.
}
\]

Insbesondere

\[
\delta_\rho H_{ab}
=\mathcal L_\rho\bar h_{ab}
=2D_{(a}\rho_{b)},
\]

\[
\delta_\rho s=\rho^aD_a\bar\sigma,
\]

und für die gezogene Gauge-One-Form

\[
\delta_\rho\mathcal A_a=(\mathcal L_\rho\bar{\mathcal A})_a.
\]

Das bedeutet: \(H_{ab}\) ist unter Bulk-Diffeomorphismus gauge-invariant, aber unter einer **unabhängigen Änderung des Interface-Charts** transformiert es korrekt als Perturbation eines 5D-Tensors. Das ist kein Widerspruch, sondern genau die doubly-covariant Trennung der beiden Symmetrien.

[BEWIESEN/AUS KANONISCHER VORGÄNGERSTRUKTUR] Bulk-Diffeomorphismus und intrinsische Interface-Reparametrisierung sind getrennte Gaugekanäle.

[FALSIFIZIERT] Die frühere Kurzdefinition von \(\mathcal G_{\rm cond}\) nur aus Bulk-Diffeomorphismus und U(1) war unvollständig, solange \(\tau_a\) im Feldraum geführt wird.

Eine reine tangentiale Chartmode ist daher

`GAUGE_ORBIT_NOT_PHYSICAL_MODE`.

Hinweis zur Vorzeichenkonvention: WP1C3 formuliert die unabhängige Oberflächenkoordinatensymmetrie geometrisch. Ein Wechsel zwischen passiver und aktiver Parametrisierung kann das Vorzeichen des Generatorparameters umkehren; die Unabhängigkeit der Symmetrien und ihre Aufnahme in den Quotienten sind davon unberührt.

---

## 5. Bedeutung von „S/V/T“ in WP1D

WP1D friert **keine physikalische kosmologische 3+1-S/V/T-Zerlegung** ein. Eine solche benötigt eine physikalische Zeitfunktion, räumliche Blätter und damit eine freigegebene Kausal-/ADM-Struktur.

Erlaubt ist nur eine konditionale 4D-kovariante York/Hodge-Buchhaltung. Wo die benötigten Projektoren existieren:

\[
\begin{aligned}
h_{\mu\nu}={}&h^{TT}_{\mu\nu}
+2D_{(\mu}V^T_{\nu)}
+\left(D_\mu D_\nu-\frac14\bar q_{\mu\nu}D^2\right)B
+\frac14\bar q_{\mu\nu}H,\\
h_{\mu i}={}&V^T_{\mu i}+D_\mu B_i,\\
a_\mu={}&a^T_\mu+D_\mu\alpha,
\end{aligned}
\]

mit

\[
D^\mu h^{TT}_{\mu\nu}=0,
\qquad
\bar q^{\mu\nu}h^{TT}_{\mu\nu}=0,
\]

\[
D^\mu V^T_\mu=0,
\qquad
D^\mu V^T_{\mu i}=0,
\qquad
D^\mu a^T_\mu=0.
\]

\(h_{ij},\varphi,a_i,s,\xi\) sind in dieser reinen 4D-kovarianten Buchhaltung Skalare.

Projektor-Firewall: Nullräume, Killingvektoren, konstante Modi, Lorentzsche Green-Operator-Wahl und äußere Randbedingungen können die Zerlegung nicht-eindeutig machen. Deshalb werden weder ein globales \(D^{-2}\) noch retarded/advanced Green-Operatoren oder physische Modenprojektoren eingefroren.

Status:

`CONDITIONAL_4D_COVARIANT_DECOMPOSITION_BOOKKEEPING_ONLY`.

---

## 6. Gaugeparameter in derselben Buchhaltung

Wo derselbe konditionale 4D-Projektor existiert:

\[
\zeta_\mu=\zeta^T_\mu+D_\mu\zeta_L,
\qquad D^\mu\zeta^T_\mu=0,
\]

zusammen mit \(\zeta_r,\zeta_\chi,\lambda\) und zusätzlich dem **unabhängigen** Interfacegenerator \(\rho^a\).

Es wird keine vollständige physische gauge-invariante Basis behauptet.

---

## 7. Kinematischer Quotient versus physischer Phasenraum

Korrekt lautet jetzt

\[
\boxed{
\mathcal Q_{\rm kin}
=\mathcal D_{\rm cond}/\mathcal G_{\rm cond}
}
\]

mit \(\mathcal G_{\rm cond}\) erzeugt durch

- Bulk-Diffeomorphismen \(\zeta^A\),
- U(1)-Transformationen \(\lambda\),
- unabhängige intrinsische Interface-Reparametrisierungen \(\rho^a\),

jeweils nur soweit sie \(\mathcal D_{\rm cond}\) in sich abbilden.

Die beiden Diffeomorphismusarten dürfen nicht identifiziert werden. Eine reine \(\rho^a\)-Chartverschiebung von \(\tau_a\) bleibt deshalb nicht als scheinbar physische Tangentialmode im Quotienten zurück.

Dieser Quotient entfernt lediglich explizite kinematische Gauge-Redundanz. Er ist **nicht** der physische reduzierte Phasenraum. Dafür fehlen weiterhin:

1. physische Zeit-/ADM-Zerlegung,
2. kanonische Momenta,
3. Primär-/Sekundärzwänge,
4. Poisson-/Dirac-Algebra,
5. first-/second-class Klassifikation,
6. kanonisch abgeleitete Gaugegeneratoren,
7. physische globale Randbedingungen.

---

## 8. Constraint-Elimination: exakte algebraische Bedingung

Für

\[
S^{(2)}
=\frac12\langle q,Aq\rangle
+\langle q,Bn\rangle
+\frac12\langle n,Cn\rangle
\]

ist eine direkte Elimination von \(n\) nur zulässig, wenn \(C\) auf dem korrekt gauge-/constraint-reduzierten Bereich invertierbar ist:

\[
Cn+B^\dagger q=0,
\qquad
n_*=-C^{-1}B^\dagger q,
\]

\[
\boxed{
S_{\rm red}^{(2)}
=\frac12\langle q,(A-BC^{-1}B^\dagger)q\rangle.
}
\]

Falls

\[
\ker C\neq\{0\},
\]

ist die direkte Inversion unzulässig. Ein Nullraum kann Gaugefreiheit, first-class Constraints, degenerierte Dynamik oder ungelöste Randmoden anzeigen.

Daher

\[
\boxed{
\text{singulärer Auxiliary-Block}\not\Rightarrow\text{direkte Elimination}
}
\]

und

\[
\boxed{
\text{formales Schur-Komplement}\not\Rightarrow\text{physische kinetische Matrix}.
}
\]

---

## 9. Warum die physische Constraint-Elimination blockiert bleibt

ULSH-04 verlangt eine eindeutige Zeitwahl, ADM-/Hamilton-Zerlegung, kanonische Variablen/Momenta, Primär-/Sekundärzwänge und die Poisson-/Dirac-Algebra.

Zusätzlich gilt

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`.

Damit ist nicht physikalisch festgelegt, welche Hyperflächen zeit- beziehungsweise raumartig sind und welche Variablen tatsächlich Lagrange-Multiplikatoren, Constraints oder propagierende Felder darstellen.

Folglich:

`WP1D_constraint_elimination = BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING`.

[FALSIFIZIERT/BLOCKIERT] Physischer DOF-Count.  
[FALSIFIZIERT/BLOCKIERT] Identifikation einer physischen kinetischen Matrix.  
[FALSIFIZIERT/BLOCKIERT] Ghostfreiheitsaussage.

---

## 10. Harte kinematische Kontrollen

**C1 — U(1):**

\[
d_a=D_as-q_\sigma\mathcal A_a,
\qquad \delta_\lambda d_a=0.
\]

**C2 — Bulk-Diffeomorphismus / Moving Interface:**

\[
\delta_\zeta H_{ab}=0.
\]

**C3 — Intrinsische Interface-Reparametrisierung:** \(\rho^a\) ist ein eigener Gaugegenerator; \(\rho^a\neq\zeta_\parallel^a\) als Gaugeidentität. Eine reine tangentiale Chartmode gehört zu \(\mathcal G_{\rm cond}\) und ist kein physischer Kinematikmodus.

**C4 — Polregularität:** skalare Fourierkontrolle \(f_n=O(r^{|n|})\), ohne unzulässige Übertragung auf Tensor-/One-Form-Komponenten.

**C5 — Schur-Komplement:** nur bei invertierbarem Auxiliary-Block.

**C6 — Singulärer Auxiliary-Block:** muss fail-closed behandelt werden.

---

## 11. Dimensionscheck

\(d_a\) ist per Definition ein wohldefinierter Interface-Kovektor. Einzelne Koordinatenkomponenten können wegen der dimensionslosen Winkelkoordinate \(\chi\) unterschiedliche Koordinatendimensionen tragen. Eindeutig ist dagegen

\[
X=h^{ab}d_a d_b,
\]

mit im M1-Vertrag

\[
[Z_\sigma]=M^3,
\qquad [X]=M^2,
\]

also

\[
[Z_\sigma X]=M^5,
\]

wie für eine 5D-lokalisierte Lagrangedichte erforderlich.

---

## 12. Regime- und Grenzfallprüfung

- \(a_F\to0\): Maxwell-Skalar-Decoupling-Kontrolle; schließt weder Constraints noch physische S/V/T.
- interner Nullmode \(n=0\): bleibt zulässig; keine Division durch \(n\).
- große \(|n|\): stärkere Polregularität, aber kein freigegebenes KK-Spektrum.
- 4D-Projektor-Nullräume: konstante Skalare, Killingvektoren und andere Kernelmoden müssen separat behandelt werden; keine stillschweigende Pseudoinverse.
- reine intrinsische Chartmode: bleibt Gaugeorbit und darf in einem späteren Kernel-/DOF-Audit nicht als zusätzliche Tangentialanregung gezählt werden.

---

## 13. Nicht zulässige Schlussfolgerungen

Dieser Vertrag beweist nicht:

- einen freigegebenen 6D-Hintergrund,
- eine physische Zeitwahl,
- eine physische 3+1-S/V/T-Zerlegung,
- einen global eindeutigen York/Hodge-Projektor,
- vollständige physische Gaugeinvarianten,
- geschlossene Dirac-Bergmann-Constraints,
- einen physischen Freiheitsgrad-Count,
- die physische kinetische Matrix,
- Ghost-, Gradient- oder Tachyonfreiheit,
- ein Moden-/KK-Spektrum,
- eine 6D→4D-Perturbationsmap,
- \(\Phi,\Psi,\Delta_m\) als hergeleitete HZT-Variablen,
- \(\mu,\eta,\Sigma\), Growth oder Lensing,
- K1-D oder K1-E.

Zusätzlich verboten ist die Identifikation

\[
\rho^a\equiv\zeta_\parallel^a
\]

als vermeintlich einzige gemeinsame Gaugefreiheit. WP1C3 behandelt diese Symmetrien ausdrücklich getrennt.

---

## 14. Gate- und Firewallstatus

```text
FM-G0                     OPEN
PHYSICAL_BACKGROUND       NOT_ESTABLISHED
PHYSICAL_RESPONSE_RANK    NOT_EXECUTED
K1-D                      NOT_RELEASED
K1-E                      NOT_ADMISSIBLE
AuthorizationDecision     NOT_CREATED
SingleUseGrant            NOT_CREATED
BACKEND_IMPORT            NOT_EXECUTED
SOLVER_EXECUTION          NOT_EXECUTED
physical_gate_effect      NONE
physical_evidence_effect  NONE
```

Maximaler Abschlussstatus:

`CONDITIONAL_KINEMATIC_GAUGE_REDUCTION_DOMAIN_FROZEN_CONSTRAINT_ELIMINATION_BLOCKED`.

---

## 15. Nächster zulässiger analytischer Schritt

Der nächste Schritt bleibt rein analytisch:

1. alle Bulk- und Interfacevariablen in der 4D-kovarianten Buchhaltung registrieren;
2. den linearen Gaugeoperator \(G\) mit **getrennten Spalten** für \(\zeta^A\), \(\lambda\) und \(\rho^a\) komponentisieren;
3. Kernel und Cokernel der konditionalen Projektoren separat ausweisen;
4. nur jene kinematischen Gaugeinvarianten konstruieren, die ohne physische Zeit-/Constraintwahl bewiesen werden können;
5. die Übergabeschnittstelle zu ULSH-04 definieren, ohne Constraints zu erfinden.

Eine physische Constraint-Elimination bleibt bis zur ULSH-04-Schließung, einem freigegebenen Background und einer kompatiblen physischen Randdomäne blockiert.
