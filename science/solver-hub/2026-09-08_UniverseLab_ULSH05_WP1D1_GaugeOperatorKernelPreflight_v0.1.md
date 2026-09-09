# UniverseLab — ULSH-05 / WP1D1
## Gauge-operator, projector-kernel and ULSH-04 handoff preflight v0.1

**Datum:** 2026-09-08  
**Modellidentität:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `a894517e2c8e378bff4f6a975aee67ca85fea785`  
**Klassifikation:** `ANALYTIC_NONOPERATIVE_GAUGE_OPERATOR_KERNEL_AND_CONSTRAINT_HANDOFF_PREFLIGHT`  
**Physical gate/evidence effect:** `NONE / NONE`

## 0. Entscheidung

WP1D friert eine konditionale kinematische Feld- und Gauge-Domäne ein und nennt als nächsten zulässigen Schritt die komponentenweise Registrierung des linearen Gaugeoperators `G`, die getrennte Behandlung von Projektor-Kernel/Cokernel, die Konstruktion nur sicherer kinematischer Invarianten und eine Übergabeschnittstelle zu ULSH-04. Dieser Block weist diesem Nachfolgeschritt erstmals die ID

`ULSH-05/WP1D1`

zu. Die ID ist eine neue Successor-Zuweisung und wird nicht rückwirkend als bereits in WP1D vorgegeben dargestellt.

Kernstatus:

```text
WP1D1_successor_identifier       = FROZEN_BY_THIS_SUCCESSOR_CONTRACT
WP1D1_gauge_operator             = COMPONENTIZED_STRUCTURALLY
WP1D1_gauge_columns              = ZETA_LAMBDA_RHO_SEPARATED
WP1D1_gauge_operator_interface_rows = COMPONENTIZED_ALL_DECLARED_ROWS
WP1D1_projector_kernel_registry  = DEFINED_BACKGROUND_DEPENDENT
WP1D1_full_projector_inverse     = NOT_FROZEN
WP1D1_full_gauge_invariant_basis = NOT_CLAIMED
WP1D1_closed_range_of_G          = NOT_PROVEN
WP1D1_Fredholm_property_of_G     = NOT_PROVEN
WP1D1_ULSH04_handoff             = DEFINED_FAIL_CLOSED
WP1_global_domain_preflight      = COMPLETED_CONDITIONAL_NO_PHYSICAL_DOMAIN_RELEASE
WP1_physical_boundary_domain     = BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA
WP1_full_global_boundary_hessian = NOT_CLOSED_PHYSICAL_DOMAIN_NOT_RELEASED
WP1D_constraint_elimination      = BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING
WP1D_physical_3plus1_SVT         = NOT_RELEASED
WP1D_physical_DOF_count          = NOT_RELEASED
FM-G0                            = OPEN
SOLVER_EXECUTION                 = NOT_EXECUTED
```

## 1. Feld- und Gaugevektoren

Bulkvariablen:

\[
\Psi_{\rm bulk}=(h_{AB},\varphi,a_A).
\]

Interfacevariablen werden in der WP1D-Repräsentation geführt:

\[
\Psi_\Sigma=(s,\xi,\tau_a;\;\text{induzierte Pullbackdaten}).
\]

Die Gaugeparameter sind strikt getrennt:

\[
\epsilon=(\zeta^A,\lambda,\rho^a),
\]

wobei \(\rho^a\) die unabhängige intrinsische Interface-Reparametrisierung bezeichnet und **nicht** mit \(\zeta_\parallel^a\) identifiziert werden darf.

Der lineare Gaugeoperator wird daher blockweise definiert als

\[
\boxed{G=(G_\zeta\; G_\lambda\; G_\rho)},
\qquad
\delta\Psi=G\epsilon.
\]

## 2. Bulkspalten von G

Für den 6D-Diffeomorphismus:

\[
G_\zeta[h]_{AB}=2\bar\nabla_{(A}\zeta_{B)},
\]

\[
G_\zeta[\varphi]=\zeta^A\partial_A\bar\phi,
\]

\[
G_\zeta[a]_A=\mathcal L_\zeta\bar A_A.
\]

Für U(1):

\[
G_\lambda[h]_{AB}=0,
\qquad
G_\lambda[\varphi]=0,
\qquad
G_\lambda[a]_A=\partial_A\lambda.
\]

Die intrinsische Interface-Reparametrisierung besitzt keine zusätzliche Bulkspalte:

\[
G_\rho[h]_{AB}=G_\rho[\varphi]=G_\rho[a_A]=0
\]

als Bulkfelder. Sie wirkt auf Interface-Pullbackrepräsentanten.

## 3. Interfacespalten von G

Unter Bulk-Diffeomorphismus gilt in der eingefrorenen Moving-Interface-Konvention

\[
G_\zeta[\xi]=-\zeta_\perp,
\qquad
G_\zeta[\tau_a]=-\zeta_{\parallel a}.
\]

Für die induzierte Metrikvariation

\[
H_{ab}=p_{ab}+2\xi K_{ab}+2D_{(a}\tau_{b)}
\]

gilt

\[
\boxed{G_\zeta[H_{ab}]=0}.
\]

Die intrinsische Kappenphase ist im deklarierten doubly-covariant Split kein zusätzliches Bulkfeld. Für die **reine** Bulk-Diffeomorphismusspalte gilt daher direkt

\[
G_\zeta[s]=0.
\]

Für einen moving pullback eines Bulk-Tensors folgt aus der WP1C3-Masterregel

\[
\delta_\Sigma(X^*T)=\bar X^*\left(\delta T+\mathcal L_z\bar T\right)
\]

unter der gepaarten aktiven Bulk-/Embedding-Transformation kinematisch

\[
\boxed{G_\zeta[\Delta_\Sigma(X^*T)]=0}.
\]

Insbesondere ist für die gezogene Gauge-One-Form im reinen Diffeomorphismuskanal

\[
G_\zeta[\mathcal A_a]=0.
\]

Damit folgt für

\[
d_a=D_as-q_\sigma\mathcal A_a
\]

auch

\[
\boxed{G_\zeta[d_a]=0}.
\]

Unter U(1):

\[
G_\lambda[s]=q_\sigma\lambda,
\qquad
G_\lambda[\mathcal A_a]=D_a\lambda,
\]

und daher

\[
\boxed{G_\lambda[d_a]=0}.
\]

Unter unabhängiger Interface-Reparametrisierung:

\[
G_\rho[\tau^a]=\rho^a,
\qquad
G_\rho[\xi]=0,
\]

und für einen Hintergrund-Pullbacktensor \(\bar T\) mit linearer Perturbation \(t\):

\[
\boxed{G_\rho[t]=\mathcal L_\rho\bar T}.
\]

Insbesondere

\[
G_\rho[H_{ab}]=2D_{(a}\rho_{b)},
\qquad
G_\rho[s]=\rho^aD_a\bar\sigma,
\]

\[
G_\rho[\mathcal A_a]=(\mathcal L_\rho\bar{\mathcal A})_a.
\]

Mit

\[
\bar w_a=D_a\bar\sigma-q_\sigma\bar{\mathcal A}_a
\]

transformiert die U(1)-invariante Kappen-One-Form unter der **unabhängigen** Interface-Reparametrisierung als One-Form-Perturbation:

\[
\boxed{G_\rho[d_a]=(\mathcal L_\rho\bar w)_a}.
\]

Damit ist `H_ab` unter `G_zeta` invariant, aber nicht unter dem vollständigen `G`; `d_a` ist unter `G_zeta` und `G_lambda` invariant, aber wegen der unabhängigen `rho`-Spalte im Allgemeinen ebenfalls **nicht** unter dem vollständigen `G` invariant.

[FIREWALL] Diese Aussagen sind kinematische Gauge-Transformationsregeln. Sie stellen weder eine physikalische Gaugefixierung noch eine physikalische Modenbasis dar.

## 4. 4D-kovariante Buchhaltung

Wo die konditionalen York/Hodge-Zerlegungen existieren, werden die Gaugeparameter formal als

\[
\zeta_\mu=\zeta^T_\mu+D_\mu\zeta_L,
\qquad D^\mu\zeta^T_\mu=0
\]

geführt, zusätzlich zu \(\zeta_r,\zeta_\chi,\lambda,\rho^a\).

Dies erlaubt eine sektoriell sortierte Matrixdarstellung von `G`. Es wird jedoch **kein** globales `D^{-2}`, keine retarded/advanced Green-Wahl und kein physischer S/V/T-Projektor eingefroren.

## 5. Kernel von G

Der Gaugekernel ist

\[
\ker G=\{\epsilon:\;G\epsilon=0\}.
\]

Er ist background- und domänenabhängig. Beispiele für mögliche Kernelanteile sind Parameter, die gleichzeitig

\[
\mathcal L_\zeta\bar g=0,
\qquad
\zeta^A\partial_A\bar\phi=0,
\qquad
\mathcal L_\zeta\bar A+d\lambda=0
\]

und die entsprechenden Interfacebedingungen erfüllen. Killingvektoren oder kompensierte U(1)-Transformationen sind daher **Kandidaten**, keine allgemein bewiesenen Kernelmoden.

[OFFEN] `ker G` wird nicht numerisch oder dimensionsmäßig gezählt, solange Background und globale Domäne nicht freigegeben sind.

## 6. Projektor-Kernel, Range und Cokernel

Die konditionale 4D-Zerlegung verwendet Differentialoperatoren, deren Inversen Nullräume besitzen können. Schematisch:

\[
\mathcal K_0=\ker D^2,
\qquad
\mathcal K_1=\ker \Delta_1,
\qquad
\mathcal K_2=\ker \Delta_L,
\]

für skalare, transversale One-Form- und symmetrische Tensor-Projektorprobleme. Die exakten Operatoren hängen von \(\bar q_{\mu\nu}\), Signatur und Randdomäne ab.

Eine Zerlegung der Form

\[
f=D^2u
\]

erlaubt daher nur dann \(u=D^{-2}f\), wenn `f` im Bild liegt und eine Kernelbehandlung beziehungsweise Zusatzbedingung angegeben ist.

Für einen dicht definierten Operator zwischen später festgelegten Hilberträumen gilt nach Freeze von Pairing und Domäne zunächst nur die sichere Identität

\[
\boxed{
\ker G^\dagger=(\overline{\operatorname{im}G})^\perp .
}
\]

Der **gewöhnliche** Cokernel ist dagegen

\[
\operatorname{coker}G
=\operatorname{codomain}(G)/\operatorname{im}G.
\]

Daraus folgt im Allgemeinen **nicht**

\[
\operatorname{coker}G\simeq\ker G^\dagger,
\]

wenn \(\operatorname{im}G\) nicht abgeschlossen ist. Die Identifikation mit dem Adjungiertenkernel erfordert zusätzlich mindestens

\[
\boxed{
\operatorname{im}G\ \text{abgeschlossen}
}
\]

beziehungsweise einen stärkeren Fredholm-/Closed-Range-Vertrag. Ohne diesen kann höchstens der reduzierte Cokernel

\[
\overline{\operatorname{coker}}G
:=\operatorname{codomain}(G)/\overline{\operatorname{im}G}
\]

nach geeignetem Hilbert-Pairing durch \(\ker G^\dagger\) repräsentiert werden.

Aktuell gilt deshalb:

```text
G_dagger                    = NOT_FROZEN
closed_range_of_G           = NOT_PROVEN
Fredholm_property_of_G      = NOT_PROVEN
ordinary_cokernel_count     = NOT_AVAILABLE
reduced_cokernel_count      = NOT_AVAILABLE
```

[BEWIESEN/METHODISCH] Pairing-/Domain-Freeze allein reicht für die Gleichsetzung des gewöhnlichen Cokernels mit dem Adjungiertenkernel nicht aus.

## 7. Kinematische Invarianten: maximal sichere Aussage

Zulässig sind die spaltenbezogenen Aussagen, die durch die obige doubly-covariant Kinematik bewiesen sind:

\[
G_\zeta[H_{ab}]=0,
\qquad
G_\zeta[d_a]=0,
\qquad
G_\lambda[d_a]=0.
\]

Wegen

\[
G_\rho[H_{ab}]=\mathcal L_\rho\bar h_{ab},
\qquad
G_\rho[d_a]=\mathcal L_\rho\bar w_a
\]

ist dagegen im Allgemeinen **nicht** zulässig,

\[
G[H_{ab}]=0
\quad\text{oder}\quad
G[d_a]=0
\]

zu behaupten.

Eine vollständige lokale oder globale Basis \(I\) mit

\[
IG=0
\]

wird in diesem Block **nicht** behauptet. Sie erfordert mindestens Projektor-Kernelkontrolle und die vollständige Interface-Pullbackwirkung.

## 8. Quotient und Nullmoden

Der kinematische Quotient bleibt

\[
\mathcal Q_{\rm kin}=\mathcal D_{\rm cond}/\operatorname{im}G.
\]

Moden im Projektorkernel werden nicht automatisch als Gauge verworfen. Nur Elemente von `im G` sind durch diese Definition kinematische Gaugeorbits. Deshalb gilt

\[
\boxed{\text{projector zero mode}\not\Rightarrow\text{gauge mode}}
\]

und ebenso

\[
\boxed{\text{gauge reducibility parameter}\not\Rightarrow\text{physical perturbation mode}}.
\]

[OFFEN] Ob dieser algebraische Quotient in der später gewählten funktionalanalytischen Topologie abgeschlossen/Hausdorff ist, hängt insbesondere von der Closed-Range-Eigenschaft von `G` ab und wird hier nicht behauptet.

## 9. Übergabe an ULSH-04

WP1D1 definiert nur eine fail-closed Übergabeschnittstelle. ULSH-04 erhält als **Input**:

- Feldraum und konditionale Domäne,
- den unverändert offenen Upstream-Gate `WP1_physical_boundary_domain = BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA`,
- blockweisen Gaugeoperator `G=(G_zeta,G_lambda,G_rho)` einschließlich der deklarierten Interface- und generischen moving-pullback-Zeilen,
- explizite Trennung von Bulk- und Interface-Reparametrisierung,
- Projektor-/Zero-Mode-Register,
- bereits bewiesene spaltenbezogene kinematische Invarianten,
- offene globale Domain- und Backgroundabhängigkeiten,
- den offenen Closed-Range-/Fredholm-Status von `G`.

ULSH-04 muss separat liefern:

- physikalisch begründete Zeit-/ADM-Zerlegung,
- kanonische Variablen und Momenta,
- Primär-/Sekundärzwänge,
- Poisson-/Dirac-Algebra,
- first-/second-class Klassifikation,
- tatsächliche Gaugegeneratoren im Hamiltonschen Sinn,
- zulässigen Constraint-Quotienten,
- physischen DOF-Count auf einem freigegebenen Background.

Bis dahin bleibt

`WP1D_constraint_elimination = BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING`

und WP1D1 darf **keine** Variable als nondynamisch eliminieren.

## 10. Schur-Komplement-Firewall

Für

\[
S^{(2)}=\tfrac12\langle q,Aq\rangle+\langle q,Bn\rangle+\tfrac12\langle n,Cn\rangle
\]

bleibt

\[
S_{\rm red}^{(2)}=\tfrac12\langle q,(A-BC^{-1}B^\dagger)q\rangle
\]

nur zulässig, wenn `C` auf der korrekt gauge-/constraint-reduzierten Domäne invertierbar ist. Solange ULSH-04 nicht geschlossen ist, wird keine physische `C^{-1}`-Elimination vorgenommen.

## 11. Firewalls

```text
FM-G0                           = OPEN
PHYSICAL_BACKGROUND             = NOT_ESTABLISHED
WP1_global_domain_preflight     = COMPLETED_CONDITIONAL_NO_PHYSICAL_DOMAIN_RELEASE
WP1_physical_boundary_domain    = BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA
WP1_full_global_boundary_hessian = NOT_CLOSED_PHYSICAL_DOMAIN_NOT_RELEASED
WP1_full_quadratic_action       = NOT_CLOSED
WP1D_constraint_elimination     = BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING
WP1D_physical_3plus1_SVT        = NOT_RELEASED
WP1D_physical_DOF_count         = NOT_RELEASED
PERTURBED_JUNCTION_SYSTEM       = NOT_RELEASED
PHYSICAL_RESPONSE_RANK          = NOT_EXECUTED
K1-D                            = NOT_RELEASED
K1-E                            = NOT_ADMISSIBLE
AuthorizationDecision           = NOT_CREATED
SingleUseGrant                  = NOT_CREATED
BACKEND_IMPORT                  = NOT_EXECUTED
SOLVER_EXECUTION                = NOT_EXECUTED
physical_gate_effect            = NONE
physical_evidence_effect        = NONE
```

## 12. Verbotene Schlussfolgerungen

- Komponentenweise Registrierung von `G` ist keine physische Gaugefixierung.
- `H_ab` ist nicht unter dem vollständigen Gaugeoperator invariant; seine bewiesene Invarianz betrifft die Bulk-Diffeomorphismusspalte.
- `d_a` ist zwar unter der gepaarten Bulk-Diffeomorphismusspalte und unter U(1) invariant, aber wegen der unabhängigen Interface-Reparametrisierung im Allgemeinen nicht unter dem vollständigen `G` invariant.
- Projektor-Nullmoden dürfen nicht ohne Beweis entfernt werden.
- Pairing-/Domain-Freeze allein identifiziert den gewöhnlichen Cokernel nicht mit `ker G^dagger`; dafür ist zusätzlich Closed Range beziehungsweise eine geeignete Fredholm-Bedingung erforderlich.
- `ker G`, `coker G` und physische DOF dürfen nicht ohne Background, Domäne und ULSH-04-Abschluss gezählt werden.
- `WP1_physical_boundary_domain` bleibt `BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA`; weder der physische Hintergrund noch die globalen Corner-/Joint-Daten werden durch WP1D1 freigegeben.
- `WP1D_constraint_elimination` bleibt `BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING`; weder ULSH-04 noch die physikalische Zeitwahl ist durch WP1D1 geschlossen.
- `WP1D_physical_3plus1_SVT` bleibt `NOT_RELEASED`; die 4D-kovariante Buchhaltung ist keine physikalische 3+1-S/V/T-Zerlegung.
- `FM-G0` bleibt `OPEN`; WP1D1 schließt keine Forward-Map-Lücke.
- Kein Ghost-, Stabilitäts-, Spektral-, Observable- oder Solverfreigabe-Claim folgt aus diesem Block.

## 13. Nächster zulässiger analytischer Schritt

Der kleinste nächste Schritt nach erfolgreicher Review dieses Blocks ist eine **WP1D2 kinematic invariant candidate ledger / projector solvability preflight**:

1. für jede 4D-kovariante Sektorvariable die zugehörige `G`-Zeile explizit registrieren;
2. notwendige Lösbarkeitsbedingungen der York/Hodge-Projektoren pro Sektor ausweisen;
3. lokale Kandidaten `I` mit `I G = 0` nur dort konstruieren, wo dies ohne inverse physikalische Green-Operatorwahl algebraisch bewiesen werden kann;
4. alle verbleibenden Kernel-/Cokernelambiguitäten als harte Übergabebedingungen an ULSH-04 markieren.

Maximal zulässiger Abschlussstatus:

`GAUGE_OPERATOR_STRUCTURALLY_COMPONENTIZED_KERNELS_REGISTERED_NO_PHYSICAL_REDUCTION_RELEASED`.
