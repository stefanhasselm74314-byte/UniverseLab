# UniverseLab — ULSH-05 / WP1D
## Conditional S/V/T gauge-and-constraint reduction domain v0.1

**Datum:** 2026-09-08  
**Modellidentität:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `51a48f23c9b32480ce56b0fb247b14d012fb4a0e`  
**Klassifikation:** `ANALYTIC_NONOPERATIVE_CONDITIONAL_GAUGE_AND_CONSTRAINT_REDUCTION_DOMAIN`  
**Physical gate/evidence effect:** `NONE / NONE`

## 0. Entscheidung und Successor-ID

WP1C4B2C hat die physikalische Randdomäne fail-closed blockiert, weil der physische 6D-Hintergrund, seine Kausalstruktur und ein globaler Outer-Boundary/Corner-Vertrag nicht freigegeben sind. Sein expliziter Fallback lautet daher: nur eine **konditionale S/V/T-Gauge- und Constraint-Reduktionsdomäne** einfrieren, ohne Solverausführung.

Dieser Nachfolgevertrag weist diesem Fallback erstmals kanonisch die ID

`ULSH-05/WP1D`

zu.

Die Zuordnung ist eine **neue Governance-Zuweisung dieses Successor-Vertrags**; sie wird nicht rückwirkend als bereits im Vorgänger vorgegeben dargestellt.

Kernstatus:

```text
WP1D_successor_identifier          = FROZEN_BY_THIS_SUCCESSOR_CONTRACT
WP1D_analytic_field_domain         = FROZEN_CONDITIONAL
WP1D_4D_covariant_SVT_bookkeeping = DEFINED_CONDITIONAL_PROJECTOR_KERNELS_OPEN
WP1D_gauge_action                  = DEFINED_KINEMATICALLY
WP1D_constraint_elimination        = BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING
WP1D_physical_3plus1_SVT           = NOT_RELEASED
WP1D_physical_DOF_count            = NOT_RELEASED
WP1_full_quadratic_action          = NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM          = NOT_RELEASED
SOLVER_EXECUTION                   = NOT_EXECUTED
```

[BEWIESEN] Der folgende Block kann die zulässige **kinematische Feld- und Gauge-Domäne** definieren.

[FALSIFIZIERT/BLOCKIERT] Eine physikalische 3+1-S/V/T-Zerlegung, ein physischer DOF-Count oder eine Constraint-Elimination dürfen daraus nicht abgeleitet werden.

---

## 1. Kanonische Quellenkette

Dieser Block verwendet ausschließlich:

1. `SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md`
2. `registry/2026-08-03_MD2S_R1_C_PHYS_GlobalConventionFreezeContract_v0.1.json`
3. `registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json`
4. `science/solver-hub/2026-08-07_ULSH-04_Constraint_Roadmap_v1.0.md`
5. `science/solver-hub/2026-08-07_ULSH-05_SVT-Perturbation_Roadmap_v1.0.md`
6. `science/solver-hub/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.md`
7. `registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2A_BoundarySecondVariationMaster_v0.1.json`
8. `registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2B_ComponentBoundaryResidualLinearization_v0.1.json`
9. `registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2C_GlobalBoundaryDomainPreflight_v0.1.json`
10. `registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInventory_v1.0.json`

Keine ΛCDM-, C1-V-, HZT-Full-, historische A0- oder Visualisierungsvariable wird als physische HZT-M0-Perturbationsvariable importiert.

---

## 2. Feldraum vor Reduktion

Die linearen Bulkvariablen werden weiterhin als

\[
\Psi_{\rm bulk}=(h_{AB},\varphi,a_A)
\]

geführt. Auf dem gemeinsamen Interface kommen die bereits eingefrorenen bewegten Interfacevariablen hinzu, insbesondere

\[
\Psi_\Sigma=(s,\xi,\tau_a)
\]

zusammen mit den aus den Vorgängerblöcken konstruierten induzierten Variationen.

Dabei gilt:

- \(h_{AB}\): metrische Perturbation,
- \(\varphi\): Bulk-Skalarperturbation,
- \(a_A\): U(1)-Potentialperturbation,
- \(s\): Kappenphasenperturbation,
- \(\xi\): normale Interfaceverschiebung,
- \(\tau_a\): tangentiale Interfaceverschiebung.

Die physikalische Interpretation dieser Variablen wird **nicht** vorausgesetzt.

---

## 3. Konditionale analytische Domäne

Sei lokal

\[
\mathcal M_s\sim M_4\times D_{2,s}
\]

mit \(D_{2,s}\) als regionalem zweidimensionalem Disk-Sektor und \(\chi\sim\chi+2\pi\). Der analytische Fallback-Bereich \(\mathcal D_{\rm cond}\) besteht aus glatten linearen Störungen, die folgende Bedingungen erfüllen:

1. **Tangentialer Support:**
   - falls \(\partial M_4=\varnothing\): kompakter Support in \(M_4\);
   - falls ein endlicher randtragender Slab benutzt wird: Support kompakt enthalten in \(\operatorname{int}M_4\).
2. **Interne Periodizität:** alle Felder sind \(2\pi\)-periodisch in \(\chi\), modulo der bereits eingefrorenen U(1)-Patchstruktur.
3. **Pole:** Regularität wird nicht durch naive Komponenten-Dirichletwerte definiert, sondern durch glatte Fortsetzbarkeit in lokalen kartesischen Koordinaten des jeweiligen Diskpols.
4. **Interface:** die Zwei-Seiten-Gluing- und Moving-Interface-Kinematik der WP1C-Reihe wird erhalten.
5. **Gauge-Abschluss:** zulässige Gaugeparameter müssen dieselben Support-, Periodizitäts-, Pole- und Gluing-Bedingungen erhalten.

Für einen skalaren Fouriermodus

\[
f(r,\chi)=\sum_{n\in\mathbb Z}f_n(r)e^{in\chi}
\]

impliziert glatte Polregularität im einfachsten skalaren Fall

\[
f_n(r)=O(r^{|n|})
\qquad(r\to0).
\]

[FIREWALL] Diese skalare Potenzregel darf nicht blind auf Tensor- oder One-Form-Komponenten übertragen werden; dort ist die glatte kartesische Fortsetzbarkeit die primäre Bedingung.

---

## 4. Gaugegruppe und lineare Wirkung

### 4.1 6D-Diffeomorphismen

Für einen infinitesimalen Vektor \(\zeta^A\) frieren wir die aktive lineare Konvention

\[
\delta_\zeta h_{AB}=2\bar\nabla_{(A}\zeta_{B)}
\]

und

\[
\delta_\zeta\varphi=\zeta^A\partial_A\bar\phi
\]

sowie

\[
\delta_\zeta a_A=\mathcal L_\zeta\bar A_A
\]

für den reinen Diffeomorphismusanteil ein.

### 4.2 U(1)

Mit Gaugeparameter \(\lambda\):

\[
\delta_\lambda a_A=\partial_A\lambda,
\qquad
\delta_\lambda s=q_\sigma\lambda.
\]

Dadurch bleibt die bereits in WP1C4B2B verwendete Kappenkombination

\[
\boxed{d_a=D_as-q_\sigma\mathcal A_a}
\]

unter U(1) invariant:

\[
\delta_\lambda d_a
=D_a(q_\sigma\lambda)-q_\sigma D_a\lambda=0.
\]

**[BEWIESEN]** Dies ist eine exakte lineare U(1)-Invarianz bei konstantem \(q_\sigma\).

### 4.3 Moving-interface-Diffeomorphismus

Für die Zerlegung des Gaugevektors am Interface

\[
\zeta^A|_\Sigma=\zeta_\perp N^A+\zeta_\parallel^a e_a{}^A
\]

wird für die Embeddingstörung die kompensierende Transformation

\[
\delta\xi=-\zeta_\perp,
\qquad
\delta\tau_a=-\zeta_{\parallel a}
\]

verwendet.

Mit der bereits eingefrorenen Moving-Interface-Kombination

\[
H_{ab}=p_{ab}+2\xi K_{ab}+2D_{(a}\tau_{b)}
\]

und

\[
\delta p_{ab}=2D_{(a}\zeta_{\parallel b)}+2K_{ab}\zeta_\perp
\]

folgt

\[
\delta H_{ab}=0.
\]

**[BEWIESEN/KINEMATISCH]** \(H_{ab}\) ist unter dem gepaarten linearen Bulk-/Embedding-Diffeomorphismus invariant. Das ist keine Dynamik- oder Ghostaussage.

---

## 5. Was hier mit „S/V/T“ gemeint ist

Der Begriff S/V/T ist in diesem Block **nicht** die physische kosmologische 3+1-Zerlegung. Eine solche Zerlegung benötigt eine physikalisch ausgewählte Zeitfunktion beziehungsweise räumliche Blätter und damit genau die Kausal-/ADM-Struktur, die laut ULSH-04 und WP1C4B2C noch fehlt.

Stattdessen wird nur eine **konditionale 4D-kovariante Orbit-Buchhaltung** eingefroren.

Seien \(\mu,\nu\) Indizes auf dem vierdimensionalen Faktor und \(i,j\in\{r,\chi\}\). Wo ein geeigneter 4D-York/Hodge-Projektor auf der deklarierten analytischen Domäne existiert, schreiben wir formal

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

Die übrigen Komponenten \(h_{ij},\varphi,a_i,s,\xi\) sind 4D-kovariante Skalare.

### Projektor-Firewall

Diese Zerlegung ist nur dann eindeutig, wenn die benötigten elliptischen/hyperbolischen Inversen auf dem tatsächlich gewählten Bereich wohldefiniert sind. Nullräume, Killingvektoren, konstante Modi, Lorentzsche Green-Operator-Wahl und äußere Randbedingungen können die Zerlegung nicht-eindeutig machen.

Daher wird **kein** globaler Operator \(D^{-2}\), kein retarded/advanced Green-Operator und kein physischer Modenprojektor eingefroren.

Status:

`CONDITIONAL_4D_COVARIANT_DECOMPOSITION_BOOKKEEPING_ONLY`

---

## 6. Gaugeparameter in derselben Buchhaltung

Wo derselbe konditionale 4D-Projektor existiert, wird

\[
\zeta_\mu=\zeta^T_\mu+D_\mu\zeta_L,
\qquad
D^\mu\zeta^T_\mu=0
\]

verwendet, zusammen mit \(\zeta_r\), \(\zeta_\chi\) und \(\lambda\).

Damit ist sektoriell klar, welche Variablen durch reine Kinematik miteinander gemischt werden. Es wird jedoch **noch keine vollständige gauge-invariante physische Basis behauptet**, weil die globalen Projektoren und die Constraint-Klassifikation fehlen.

---

## 7. Kinematischer Quotient versus physischer Phasenraum

Definiere formal

\[
\mathcal Q_{\rm kin}
=\mathcal D_{\rm cond}/\mathcal G_{\rm cond},
\]

wobei \(\mathcal G_{\rm cond}\) aus den Diffeomorphismus- und U(1)-Transformationen besteht, die \(\mathcal D_{\rm cond}\) in sich abbilden.

Dieser Quotient entfernt nur explizite Gauge-Redundanz auf der deklarierten analytischen Testdomäne.

Er ist **nicht** gleich dem physischen reduzierten Phasenraum, denn dafür müssten zusätzlich

1. eine Zeit-/ADM-Zerlegung,
2. kanonische Momenta,
3. Primär-/Sekundärzwänge,
4. Poisson-/Dirac-Algebra,
5. first-/second-class Klassifikation,
6. Gaugegeneratoren,
7. zulässige globale Randbedingungen

vollständig geschlossen sein.

Diese Punkte sind im ULSH-04-Vertrag ausdrücklich noch offen.

---

## 8. Constraint-Elimination: exakte algebraische Bedingung

Für eine quadratische Form mit behaltenen Variablen \(q\) und Kandidaten für nichtpropagierende Variablen \(n\)

\[
S^{(2)}
=\frac12\langle q,Aq\rangle
+\langle q,Bn\rangle
+\frac12\langle n,Cn\rangle
\]

ist die formale Elimination nur zulässig, wenn \(C\) auf dem deklarierten Bereich nach korrekter Gauge-/Constraint-Behandlung invertierbar ist.

Dann

\[
Cn+B^\dagger q=0
\]

und

\[
n_*=-C^{-1}B^\dagger q,
\]

sodass

\[
\boxed{
S_{\rm red}^{(2)}
=\frac12\langle q,
(A-BC^{-1}B^\dagger)q\rangle.
}
\]

Der Operator

\[
A_{\rm Schur}=A-BC^{-1}B^\dagger
\]

ist das Schur-Komplement.

### Nullraum-No-Go

Falls

\[
\ker C\neq\{0\},
\]

ist die direkte Formel mit \(C^{-1}\) unzulässig. Ein Nullraum kann insbesondere Gaugefreiheit, first-class Constraints oder eine echte degenerierte Dynamik signalisieren.

Daher gilt:

\[
\boxed{
\text{singulärer Auxiliary-Block}
\not\Rightarrow
\text{„Variable einfach eliminieren“}
}
\]

und ebenso

\[
\boxed{
\text{formales Schur-Komplement}
\not\Rightarrow
\text{physische kinetische Matrix}.
}
\]

**[BEWIESEN/LINEARE ALGEBRA]** Die Invertierbarkeit des Auxiliary-Blocks ist eine notwendige Voraussetzung für diese direkte Eliminationsformel.

---

## 9. Warum die eigentliche Constraint-Elimination blockiert bleibt

Der ULSH-04-Kanon verlangt eine eindeutige Zeitwahl, ADM-/Hamilton-Zerlegung, Primär-/Sekundärzwänge und Poisson-/Dirac-Algebra. Diese Kette ist noch nicht geschlossen.

Zusätzlich ist

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`.

Damit ist nicht festgelegt, welche Koordinate beziehungsweise welche Hyperflächen physikalisch zeitartig/spacelike sind und welche Variablen tatsächlich Lagrange-Multiplikatoren, Constraints oder propagierende Felder darstellen.

Folglich:

```text
WP1D_constraint_elimination = BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING
```

[FALSIFIZIERT/BLOCKIERT] Jeder jetzige physische DOF-Count.

[FALSIFIZIERT/BLOCKIERT] Jede jetzige Identifikation einer „kinetischen Matrix der physischen Moden“.

[FALSIFIZIERT/BLOCKIERT] Jede Ghostfreiheitsaussage.

---

## 10. U(1)- und Embedding-Kontrollinvarianten

Dieser Block erlaubt zwei harte kinematische Kontrollen unabhängig von der noch offenen Constraintdynamik:

### C1 — Kappen-U(1)

\[
d_a=D_as-q_\sigma\mathcal A_a
\]

bleibt invariant unter

\[
s\mapsto s+q_\sigma\lambda,
\qquad
\mathcal A_a\mapsto\mathcal A_a+D_a\lambda.
\]

### C2 — induzierte Moving-Interface-Metrik

\[
H_{ab}=p_{ab}+2\xi K_{ab}+2D_{(a}\tau_{b)}
\]

bleibt invariant unter der gekoppelten Transformation

\[
\delta p_{ab}=2D_{(a}\zeta_{\parallel b)}+2K_{ab}\zeta_\perp,
\quad
\delta\xi=-\zeta_\perp,
\quad
\delta\tau_a=-\zeta_{\parallel a}.
\]

Beide Kontrollen sind rein kinematisch.

---

## 11. Dimensionscheck

Die Gauge-kovariante Kappenableitung

\[
d_a=D_as-q_\sigma\mathcal A_a
\]

ist per Definition ein wohldefinierter Interface-Kovektor. Daher müssen die beiden Summanden in jeder verwendeten Koordinatenkomponente dieselbe Dimension besitzen. Einzelne Komponenten können wegen der dimensionslosen Winkelkoordinate \(\chi\) andere Koordinatendimensionen tragen als Komponenten entlang dimensionsbehafteter Tangentialkoordinaten; ein komponentenweises pauschales Massendimensionslabel ist deshalb nicht invariant.

Die skalare Kombination der Kappenwirkung ist dagegen eindeutig:

\[
X=d_a d^a=h^{ab}d_a d_b,
\]

und im eingefrorenen M1-Vertrag gilt

\[
[Z_\sigma]=M^3,
\qquad
[X]=M^2,
\]

sodass

\[
[Z_\sigma X]=M^5,
\]

wie für eine 5D-lokalisierte Lagrangedichte erforderlich.

**[BEWIESEN/DIMENSIONELL]** Der Gauge-invariante Kappensektor bleibt dimensionskonsistent, ohne eine koordinatenabhängige Komponentendimension als neue Theorieannahme einzufrieren.

---

## 12. Regime- und Grenzfallprüfung

### U(1)-Decoupling control

Im deklarierten Kontrollgrenzfall \(a_F\to0\) wird \(Z_F\to1\). Das vereinfacht Skalar-Maxwell-Mischungen, ändert aber weder die Diffeomorphismusstruktur noch die Notwendigkeit der Constraintklassifikation.

### Fourier-Nullmode \(n=0\)

Der interne Nullmode ist zulässig, aber gerade dort können Projektor- und Gauge-Nullräume besonders relevant sein. Er darf nicht durch eine formale Division durch \(n\) eliminiert werden.

### Große |n|

Große interne Fourierzahl verschärft die radialen Pol-Regularitätsbedingungen. Sie erzeugt aber ohne physische Hintergrundlösung noch kein freigegebenes KK-Spektrum.

### 4D-Projektor-Nullräume

Konstante Skalare, Killingvektoren oder andere Kernelmoden müssen separat behandelt werden. Eine Pseudoinverse ist eine zusätzliche mathematische Wahl und wird hier nicht als physische Vorschrift eingefroren.

---

## 13. Nicht zulässige Schlussfolgerungen

Dieser Vertrag beweist **nicht**:

- einen freigegebenen 6D-Hintergrund,
- eine physische Zeitwahl,
- eine physische 3+1-S/V/T-Zerlegung,
- einen global eindeutigen York/Hodge-Projektor,
- vollständige Gaugeinvarianten,
- geschlossene Dirac-Bergmann-Constraints,
- einen physischen Freiheitsgrad-Count,
- die physische kinetische Matrix,
- Ghost-, Gradient- oder Tachyonfreiheit,
- einen Moden- oder KK-Spektrumsclaim,
- eine 6D→4D-Perturbationsmap,
- \(\Phi,\Psi,\Delta_m\) als bereits hergeleitete HZT-Variablen,
- \(\mu,\eta,\Sigma\), Growth oder Lensing,
- K1-D oder K1-E.

---

## 14. Gate- und Firewallstatus

Unverändert:

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

Der maximale Abschlussstatus dieses Blocks lautet:

`CONDITIONAL_KINEMATIC_GAUGE_REDUCTION_DOMAIN_FROZEN_CONSTRAINT_ELIMINATION_BLOCKED`

---

## 15. Nächster zulässiger analytischer Schritt

Der nächste sachlich kleinste Schritt ist **nicht** eine Solverausführung, sondern die komponentenweise lineare Gauge-Matrix auf der deklarierten WP1D-Domäne:

1. alle Bulk- und Interfacevariablen in der 4D-kovarianten Buchhaltung registrieren;
2. Diffeomorphismus- und U(1)-Transformationen als linearen Operator \(G\) explizit komponentisieren;
3. Kernel und cokernel der konditionalen Projektoren separat ausweisen;
4. nur kinematische Gaugeinvarianten konstruieren, die ohne Zeit-/Constraintwahl bewiesen werden können;
5. Übergabeschnittstelle zu ULSH-04 definieren, ohne Constraints zu erfinden.

Eine physische Constraint-Elimination bleibt bis zur ULSH-04-Schließung und einer freigegebenen Background-/Zeitstruktur blockiert.
