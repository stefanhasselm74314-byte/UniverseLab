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
WP1D1_projector_kernel_registry  = DEFINED_BACKGROUND_DEPENDENT
WP1D1_full_projector_inverse     = NOT_FROZEN
WP1D1_full_gauge_invariant_basis = NOT_CLAIMED
WP1D1_ULSH04_handoff             = DEFINED_FAIL_CLOSED
WP1D_constraint_elimination      = BLOCKED
WP1D_physical_DOF_count          = NOT_RELEASED
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

Unter U(1):

\[
G_\lambda[s]=q_\sigma\lambda,
\qquad
G_\lambda[\mathcal A_a]=D_a\lambda,
\]

und daher

\[
\boxed{G_\lambda[d_a]=0},
\qquad
 d_a=D_as-q_\sigma\mathcal A_a.
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
G_\rho[s]=\rho^aD_a\bar\sigma.
\]

Damit ist `H_ab` unter `G_zeta` invariant, aber nicht unter dem vollständigen `G`; `d_a` ist unter `G_lambda` invariant, aber nicht automatisch unter dem vollständigen `G`. Das ist eine zentrale Firewall gegen falsche Vollinvarianzbehauptungen.

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

## 6. Projektor-Kernel und Cokernel

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

Der Cokernel wird formal als

\[
\operatorname{coker}G\simeq\ker G^\dagger
\]

auf einer **später** eingefrorenen Paarung/Domäne verstanden. Da die physikalische globale Paarung noch nicht freigegeben ist, wird kein konkretes `G^dagger` und kein Cokernel-Count behauptet.

## 7. Kinematische Invarianten: maximal sichere Aussage

Zulässig sind nur spaltenbezogene Aussagen, die bereits bewiesen sind:

\[
G_\zeta[H_{ab}]=0,
\qquad
G_\lambda[d_a]=0.
\]

Nicht zulässig ist daraus

\[
G[H_{ab}]=0
\quad\text{oder}\quad
G[d_a]=0
\]

zu folgern.

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

## 9. Übergabe an ULSH-04

WP1D1 definiert nur eine fail-closed Übergabeschnittstelle. ULSH-04 erhält als **Input**:

- Feldraum und konditionale Domäne,
- blockweisen Gaugeoperator `G=(G_zeta,G_lambda,G_rho)`,
- explizite Trennung von Bulk- und Interface-Reparametrisierung,
- Projektor-/Zero-Mode-Register,
- bereits bewiesene spaltenbezogene kinematische Invarianten,
- offene globale Domain- und Backgroundabhängigkeiten.

ULSH-04 muss separat liefern:

- physikalisch begründete Zeit-/ADM-Zerlegung,
- kanonische Variablen und Momenta,
- Primär-/Sekundärzwänge,
- Poisson-/Dirac-Algebra,
- first-/second-class Klassifikation,
- tatsächliche Gaugegeneratoren im Hamiltonschen Sinn,
- zulässigen Constraint-Quotienten,
- physischen DOF-Count auf einem freigegebenen Background.

Bis dahin darf WP1D1 **keine** Variable als nondynamisch eliminieren.

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
PHYSICAL_BACKGROUND      = NOT_ESTABLISHED
WP1_physical_boundary_domain = BLOCKED
WP1_full_quadratic_action = NOT_CLOSED
WP1D_constraint_elimination = BLOCKED
WP1D_physical_DOF_count   = NOT_RELEASED
PERTURBED_JUNCTION_SYSTEM = NOT_RELEASED
PHYSICAL_RESPONSE_RANK    = NOT_EXECUTED
K1-D                      = NOT_RELEASED
K1-E                      = NOT_ADMISSIBLE
AuthorizationDecision     = NOT_CREATED
SingleUseGrant            = NOT_CREATED
BACKEND_IMPORT            = NOT_EXECUTED
SOLVER_EXECUTION          = NOT_EXECUTED
physical_gate_effect      = NONE
physical_evidence_effect  = NONE
```

## 12. Verbotene Schlussfolgerungen

- Komponentenweise Registrierung von `G` ist keine physische Gaugefixierung.
- `H_ab` ist nicht unter dem vollständigen Gaugeoperator invariant; seine bewiesene Invarianz betrifft die Bulk-Diffeomorphismusspalte.
- `d_a` ist nicht automatisch unter dem vollständigen Gaugeoperator invariant; seine bewiesene Invarianz betrifft die U(1)-Spalte.
- Projektor-Nullmoden dürfen nicht ohne Beweis entfernt werden.
- `ker G`, `coker G` und physische DOF dürfen nicht ohne Background, Domäne und ULSH-04-Abschluss gezählt werden.
- Kein Ghost-, Stabilitäts-, Spektral-, Observable- oder Solverfreigabe-Claim folgt aus diesem Block.

## 13. Nächster zulässiger analytischer Schritt

Der kleinste nächste Schritt nach erfolgreicher Review dieses Blocks ist eine **WP1D2 kinematic invariant candidate ledger / projector solvability preflight**:

1. für jede 4D-kovariante Sektorvariable die zugehörige `G`-Zeile explizit registrieren;
2. notwendige Lösbarkeitsbedingungen der York/Hodge-Projektoren pro Sektor ausweisen;
3. lokale Kandidaten `I` mit `I G = 0` nur dort konstruieren, wo dies ohne inverse physikalische Green-Operatorwahl algebraisch bewiesen werden kann;
4. alle verbleibenden Kernel-/Cokernelambiguitäten als harte Übergabebedingungen an ULSH-04 markieren.

Maximal zulässiger Abschlussstatus:

`GAUGE_OPERATOR_STRUCTURALLY_COMPONENTIZED_KERNELS_REGISTERED_NO_PHYSICAL_REDUCTION_RELEASED`.
