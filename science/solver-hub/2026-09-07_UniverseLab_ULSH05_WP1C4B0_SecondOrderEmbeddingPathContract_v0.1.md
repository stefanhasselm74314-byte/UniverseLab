# ULSH-05 / WP1C4B0 — Second-order embedding and moving-pullback path contract v0.1

**Datum:** 2026-09-07  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `fa8749bb87351c7057fb37db6129c3819a4b6ad7`  
**Status:** `DERIVED SECOND-ORDER VARIATIONAL KINEMATICS / MOVING BOUNDARY HESSIAN OPEN`  
**Physical gate effect:** `NONE`  
**Physical evidence effect:** `NONE`

## 1. Warum dieser Zwischenblock notwendig ist

Nach WP1C3 und WP1C4A sind die lineare bewegte Grenzflächengeometrie, die zweiseitige Bending-Identifikation und die linearen Normalfluss-Junctions eingefroren. Für eine zweite Variation ist jedoch zusätzlich ein **zweiter Pfadtangent** nötig.

In einem deklarierten lokalen affinen Konfigurationschart sei

\[
\Phi(\epsilon)=\bar\Phi+\epsilon u+\frac12\epsilon^2v+O(\epsilon^3).
\]

Dann gilt in diesem Chart exakt

\[
\boxed{
\frac{d^2S}{d\epsilon^2}\Big|_0
=D^2S_{\bar\Phi}[u,u]+DS_{\bar\Phi}[v].
}
\]

Damit ist die zweite Ableitung entlang eines Pfades off-shell **nicht automatisch** die zweite Fréchet-Ableitung im gewählten Chart. Solange

```text
PHYSICAL_BACKGROUND = NOT_ESTABLISHED
```

gilt, darf `DS[v]` nicht gestrichen werden.

Für die WP1-Konvention

\[
S(\epsilon)=S^{(0)}+\epsilon\,\delta S+\epsilon^2S_{\rm path,quad}^{(2)}+O(\epsilon^3)
\]

folgt

\[
S_{\rm path,quad}^{(2)}
=\frac12D^2S[u,u]+\frac12DS[v].
\]

Innerhalb **desselben deklarierten Charts** kann daher der vom zweiten Pfadtangenten unabhängige Koeffizient extrahiert werden:

\[
\boxed{
S_{\rm chart,Hess}^{(2)}
=S_{\rm path,quad}^{(2)}-\frac12DS[v]
=\frac12D^2S[u,u].
}
\]

Das ist der zentrale C4B0-Subtraktionsvertrag.

### 1.1 Wichtige Feldraum-Präzisierung

Der Konfigurationsraum aus Metrik, Materiefeldern und Einbettungen ist nicht global ein kanonischer linearer Vektorraum. Außerhalb eines stationären Punkts ist eine zweite Ableitung unter nichtlinearen Feldraum-Koordinatenwechseln deshalb nicht automatisch ein intrinsischer Tensor.

Wählt man eine Konfigurationsraum-Verbindung `nabla_cfg`, lautet die kovariante Identität stattdessen

\[
\boxed{
\frac{d^2S}{d\epsilon^2}\Big|_0
=(\nabla_{\rm cfg}^2S)[u,u]+DS[a_{\rm cfg}],
}
\]

mit

\[
a_{\rm cfg}=\nabla^{\rm cfg}_{u}u
\]

als Feldraum-Beschleunigung der Kurve.

C4B0 friert **keine** solche Konfigurationsraum-Verbindung ein. `D^2S` bezeichnet daher ausschließlich die zweite Fréchet-Ableitung im deklarierten lokalen affinen Perturbationschart. Eine global feldraum-kovariante off-shell Hesse wird nicht beansprucht.

An einem stationären Punkt `DS=0` verschwindet die Verbindungs-/Beschleunigungsabhängigkeit. Dieser Spezialfall darf aber aktuell nicht angenommen werden, weil der physische Hintergrund weiterhin `NOT_ESTABLISHED` ist.

---

## 2. Zeitabhängiger Embedding-Generator

Sei `X_epsilon` die Grenzflächeneinbettung und `v_epsilon` ein zeitabhängiger Umgebungsvektor, der die Bahn erzeugt:

\[
\frac{dX_\epsilon}{d\epsilon}=v_\epsilon\circ X_\epsilon.
\]

Definiere

\[
z\equiv v_\epsilon|_{0},
\qquad
w\equiv \left.\frac{dv_\epsilon}{d\epsilon}\right|_0.
\]

`w^A` ist damit der **zweite Lie-Generator-Datum**, nicht ohne weitere Konvention die rohe Koordinatenbeschleunigung `Xddot^A`.

Ein autonomer Kontrollfluss besitzt `w=0`. Das darf als Rechenpfad benutzt werden, bedeutet aber nicht, dass eine physische Interfacebeschleunigung verschwindet.

---

## 3. Zweite Variation eines bewegten Pullbacks

Für

\[
T(\epsilon)=\bar T+\epsilon T_1+\frac12\epsilon^2T_2+O(\epsilon^3)
\]

gilt

\[
\boxed{Q_1[T]=T_1+\mathcal L_z\bar T}
\]

und

\[
\boxed{
Q_2[T]
=T_2+2\mathcal L_zT_1+
(\mathcal L_w+\mathcal L_z^2)\bar T.
}
\]

`Q1` und `Q2` sind die Koeffizienten der Expansion von `X_epsilon^*T(epsilon)`.

Wichtig: Komponentenformeln für `L_z` oder `L_w` benötigen eine deklarierte regionale Extension. Das geometrisch kanonische Objekt ist die Pullback-Masterformel selbst.

---

## 4. Zweite Bulk-D-Gauge-Transformation

In Fortsetzung der in WP1C3 eingefrorenen ersten Ordnung verwenden wir zwei Gaugegeneratoren `zeta` und `lambda`:

\[
T_1' = T_1-\mathcal L_\zeta\bar T,
\]

\[
T_2'
=T_2-2\mathcal L_\zeta T_1
+(\mathcal L_\zeta^2-\mathcal L_\lambda)\bar T.
\]

Die Embedding-Generatoren transformieren als

\[
z'=z+\zeta,
\]

\[
\boxed{
w'=w+\lambda-[\zeta,z].}
\]

Mit

\[
[\mathcal L_\zeta,\mathcal L_z]
=\mathcal L_{[\zeta,z]}
\]

folgt direkt

\[
Q_1'=Q_1,
\qquad
\boxed{Q_2'=Q_2}.
\]

Der Kommutatorterm in `w'` ist unverzichtbar; ohne ihn bleibt bei nichtkommutierenden Generatoren ein Restterm übrig.

---

## 5. Intrinsische Surface-Reparameterisierung

Für einen intrinsischen Tensorpfad

\[
q=q_0+\epsilon q_1+\frac12\epsilon^2q_2+\cdots
\]

und intrinsische Reparameterisierungsgeneratoren `beta^a`, `gamma^a` gilt analog

\[
q_1'=q_1-\mathcal L_\beta q_0,
\]

\[
q_2'=q_2-2\mathcal L_\beta q_1
+(\mathcal L_\beta^2-\mathcal L_\gamma)q_0.
\]

Dies ist nur ein Kovarianzvertrag. Es wird hier weder eine S/V/T-Zerlegung noch eine intrinsische Gaugefixierung durchgeführt.

---

## 6. Zweite Ordnung der zweiseitigen Gluingrelation

WP1C4A hat

\[
N^A=n_N^A=-n_S^A
\]

und

\[
z^A=\xi N^A+\tau^ae_a^A
\]

eingefroren, woraus

\[
\xi_N=+\xi,
\qquad
\xi_S=-\xi
\]

folgt.

Für den zweiten Generator setzen wir auf derselben gemeinsamen Interface-Identifikation

\[
w^A=\chi N^A+\nu^ae_a^A.
\]

Regional folgt damit auf Generatorniveau

\[
\boxed{
\chi_N=+\chi,
\qquad
\chi_S=-\chi,
\qquad
\nu_N^a=\nu_S^a=\nu^a.
}
\]

oder

\[
\boxed{\chi_N+\chi_S=0.}
\]

Dies ist **keine** Behauptung über ungekennzeichnete rohe Koordinatenwerte `Xddot^A`; diese würden zusätzlich von Verbindung und Extension abhängen.

---

## 7. Kontrollpfad versus physische Aussage

Ein besonders nützlicher Rechenpfad ist der autonome Generatorfluss

\[
w=0.
\]

Dann

\[
Q_2=T_2+2\mathcal L_zT_1+\mathcal L_z^2\bar T.
\]

Aber off-shell bleibt für die Wirkungsableitung der Unterschied zwischen

\[
S_{\rm path,quad}^{(2)}
\]

und dem im deklarierten Chart extrahierten

\[
S_{\rm chart,Hess}^{(2)}
\]

erhalten. Ein autonomer Pfad ist deshalb nur eine **Berechnungskonvention**. C4B1 muss entweder im selben explizit deklarierten Chart `DS[v]` subtrahieren oder vor einem Anspruch auf eine feldraum-kovariante Hesse zusätzlich eine Konfigurationsraum-Verbindung einfrieren.

---

## 8. Unabhängige Kontrollen

### 8.1 Direkter bewegter Skalar-Pullback

Für einen eindimensionalen Kontrollfall wird `T_epsilon(x_epsilon)` direkt finite-differenziert. Die zweite Ableitung rekonstruiert

\[
T_2+2z\,T_1'+z^2\bar T''+w\bar T'.
\]

### 8.2 Nichtkommutierende Gaugeoperatoren

Kleine feste Matrizen repräsentieren `L_z`, `L_zeta`, `L_lambda`, `L_w`. Der Test verwendet einen **nichtverschwindenden Kommutator** und bestätigt algebraisch

\[
Q_1'=Q_1,
\qquad Q_2'=Q_2.
\]

### 8.3 Off-shell-Pfadabhängigkeit

Zwei Konfigurationspfade besitzen denselben ersten Tangenten `u`, aber unterschiedliche zweite Tangenten `v_1`, `v_2`. Ihre zweiten Pfadableitungen unterscheiden sich exakt um

\[
DS[v_1-v_2].
\]

Nach Subtraktion des `DS[v]`-Terms liefern beide im selben affinen Kontrollchart denselben Wert der zweiten Fréchet-Ableitung. Daraus folgt **nicht**, dass bereits eine global feldraum-kovariante Hesse definiert wäre.

### 8.4 Zweite Gluingkontrolle

Mit

\[
y(\epsilon)=\epsilon\xi+\frac12\epsilon^2\chi,
\]

\[
r_N=\rho_N+y,
\qquad r_S=\rho_S-y
\]

folgen direkt die erste und zweite Vorzeichenrelation.

---

## 9. Noch offen

WP1C4B0 schließt **keine** dynamische zweite Randvariation. Offen bleiben:

- Konfigurationsraum-Verbindung für eine kovariante off-shell Hesse;
- zweite Variation des bewegten GHY-Terms;
- zweite Variation der bewegten lokalisierten Kappenwirkung;
- vollständige Boundary-Hesse;
- freigegebener pertubierter Israel-/Skalar-/Gauge-BVP-Operator;
- globale Fixed-Interface-Gauge-Zulässigkeit;
- S/V/T-Zerlegung und Constraint-Elimination;
- physischer Hintergrund;
- Ghostfreiheit und Stabilität;
- 6D→4D-Reduktion und `mu/eta/Sigma`, Growth/Lensing.

Daher unverändert:

```text
WP1_configuration_space_connection = NOT_FROZEN
WP1_full_boundary_hessian = NOT_CLOSED
WP1_full_quadratic_action = NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM = NOT_RELEASED
PHYSICAL_BACKGROUND = NOT_ESTABLISHED
FM-G0 = OPEN
AuthorizationDecision = NOT_CREATED
SingleUseGrant = NOT_CREATED
BACKEND_IMPORT = NOT_EXECUTED
SOLVER_EXECUTION = NOT_EXECUTED
PHYSICAL_RESPONSE_RANK = NOT_EXECUTED
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
physical_gate_effect = NONE
physical_evidence_effect = NONE
```

## 10. Nächster zulässiger Block

`ULSH-05/WP1C4B1` darf nun die zweite Pfadvariation von GHY + lokalisierter Kappenwirkung berechnen. Es muss dabei entweder

1. im hier deklarierten lokalen affinen Konfigurationschart bleiben und
   \[
   S_{\rm chart,Hess}^{(2)}=S_{\rm path,quad}^{(2)}-\frac12DS[v]
   \]
   explizit verwenden,

oder

2. vor einem Anspruch auf eine feldraum-kovariante Hesse eine Konfigurationsraum-Verbindung `nabla_cfg` versioniert einfrieren.

Erst danach ist ein Boundary-Hessian-Closure-Verdict zulässig.
