# ULSH-05 / WP1C4A — Two-side bending gluing and normal-flux junctions v0.1

**Datum:** 2026-09-07  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Status:** `DERIVED_LINEAR_PREFLIGHT / FULL MOVING-BOUNDARY HESSIAN OPEN`  
**Physical gate effect:** `NONE`  
**Physical evidence effect:** `NONE`

## 1. Ziel

WP1C3 hat die lokale bewegte Grenzflächengeometrie eingefroren, aber das Vorzeichen der regionalen Bending-Variablen absichtlich offengelassen. WP1C4A schließt genau diese Identifikationslücke und leitet anschließend die linearen bewegten Skalar- und Gauge-Normalfluss-Junctions ab.

Nicht Bestandteil dieses Blocks ist die zweite Variation der bewegten GHY- und Kappenwirkung. Der vollständige Boundary-Hessian bleibt daher offen.

## 2. Zwei regionale Koordinaten und eine physische Grenzfläche

Die eingefrorenen regionalen Koordinaten erfüllen:

- `r_N` wächst vom Nordpol zur Kappe;
- `r_S` wächst vom Südpol zur Kappe;
- die lokalen outward normals besitzen jeweils `n_s^r=+1`.

Führe lokal um die gemeinsame Grenzfläche eine gemeinsame Koordinate `y` ein, die physisch von der N-Seite zur S-Seite zeigt. Dann kann man ohne Verlust der Allgemeinheit schreiben

\[
r_N=\rho_N+y,
\qquad
r_S=\rho_S-y.
\]

Am Interface `y=0` folgt

\[
n_N=+\partial_y,
\qquad
n_S=-\partial_y.
\]

Definiere den gemeinsamen Normalenvektor

\[
N^A\equiv n_N^A=-n_S^A.
\]

Eine einzige physische Interfaceverschiebung lautet

\[
z^A=\xi N^A+\tau^a e_a^A.
\]

Regional muss dasselbe geometrische Objekt zugleich geschrieben werden als

\[
z^A=\xi_N n_N^A+\tau_N^a e_a^A
=\xi_S n_S^A+\tau_S^a e_a^A.
\]

Daher

\[
\boxed{\xi_N=+\xi,\qquad \xi_S=-\xi,\qquad \tau_N^a=\tau_S^a=\tau^a.}
\]

Äquivalent:

\[
\boxed{\xi_N+\xi_S=0.}
\]

Dies ist keine zusätzliche Dynamik, sondern reine Geometrie der expliziten Interface-Identifikation.

## 3. Moving-pullback Operator

Für einen regionalen Skalar `Q_s` wird die Lagrange-artige Grenzflächenvariation definiert als

\[
\Delta_\Sigma Q_s
=\bar X_s^*\left[\delta Q_s+\mathcal L_{z_s}\bar Q_s\right].
\]

Wichtig: `δ` ist hier die **Eulerian Feldvariation bei festem Hintergrundpullback**. Die Grenzflächenbewegung wird ausschließlich durch den separaten Lie-Term erfasst. Damit wird die Biegung nicht doppelt gezählt.

## 4. Skalarer Normalfluss

Hintergrund:

\[
Q_{\phi,s}=n_s^A\nabla_A\phi_s.
\]

Seine Eulerian Variation ist

\[
\delta Q_{\phi,s}
=(\delta n_s^A)\bar\nabla_A\bar\phi_s
+\bar n_s^A\bar\nabla_A\varphi_s.
\]

Der bewegte Pullback lautet daher

\[
\boxed{
\Delta_\Sigma Q_{\phi,s}
=\bar X_s^*\left[
(\delta n_s^A)\bar\nabla_A\bar\phi_s
+\bar n_s^A\bar\nabla_A\varphi_s
+\mathcal L_{z_s}(\bar n_s^A\bar\nabla_A\bar\phi_s)
\right].
}
\]

Die Hintergrund-Junction ist

\[
\sum_s Q_{\phi,s}
+\lambda_{,\phi}
+\frac12Z_{\sigma,\phi}X_\sigma=0.
\]

Für `C-PHYS-M1` sind

\[
\lambda_{,\phi}=0,
\qquad
Z_{\sigma,\phi}=0,
\]

und auch deren zweite Ableitungen verschwinden. Deshalb folgt linear

\[
\boxed{
\sum_{s=N,S}\Delta_\Sigma Q_{\phi,s}=0.
}
\]

### Lokaler Kontrollfall

Setze in den regionalen Normalrichtungen

\[
\bar\phi_s(r_s)=a_s r_s+\frac12b_s r_s^2,
\qquad
\varphi_s(r_s)=c_s r_s.
\]

Eine physische Verschiebung `y=epsilon xi` erzeugt

\[
\delta r_N=+\epsilon\xi,
\qquad
\delta r_S=-\epsilon\xi.
\]

Direktes Differenzieren von `d phi_s/dr_s` an der bewegten Kappe liefert

\[
\delta Q_{\phi,N}=c_N+\xi b_N,
\qquad
\delta Q_{\phi,S}=c_S-\xi b_S,
\]

also exakt den regionalen Lie-drag-Vorzeichenvertrag.

## 5. Gauge-Normalfluss

Definiere zuerst das vollständig intrinsische, bereits gepullbackte Hintergrundobjekt

\[
\mathcal Q_{F,s}^a
\equiv
\bar X_s^*\left[e_B{}^a n_{sA}Z_F(\phi_s)F_s^{AB}\right].
\]

Seine lineare bewegte Variation ist definitionsgemäß

\[
\boxed{
\Delta_\Sigma\mathcal Q_{F,s}^a
=
\bar X_s^*\left[
\delta(e_B{}^a n_A Z_F F^{AB})
+\mathcal L_{z_s}(e_B{}^a\bar n_A\bar Z_F\bar F^{AB})
\right].
}
\]

Diese Form ist bewusst invariant formuliert; eine komponentenreduzierte Fassung darf erst nach Wahl eines Extensions-/Koordinatenvertrags verwendet werden.

Die Hintergrund-Kappenstromdichte ist

\[
j_\Sigma^a=q_\sigma Z_\sigma w^a,
\qquad
w_a=D_a\bar\sigma.
\]

Mit

\[
d_{\Sigma a}=D_as-q_\sigma a_{\Sigma a},
\]

und

\[
\delta h^{ab}=-H^{ab}
\]

folgt für konstantes `Z_sigma`:

\[
\boxed{
\delta j_\Sigma^a
=q_\sigma Z_\sigma
\left(
\bar h^{ab}d_{\Sigma b}-H^{ab}w_b
\right).
}
\]

Die lineare Gauge-Junction lautet daher

\[
\boxed{
\sum_{s=N,S}\Delta_\Sigma\mathcal Q_{F,s}^a
=
q_\sigma Z_\sigma
\left(
\bar h^{ab}d_{\Sigma b}-H^{ab}w_b
\right).
}
\]

Unter

\[
s\rightarrow s+q_\sigma\alpha_\Sigma,
\qquad
a_{\Sigma a}\rightarrow a_{\Sigma a}+D_a\alpha_\Sigma
\]

bleibt

\[
d_{\Sigma a}\rightarrow d_{\Sigma a}
\]

und damit die rechte Seite U(1)-invariant.

## 6. Was damit geschlossen ist

`[BEWIESEN / ANALYTISCH]`

- die explizite regionale Bending-Gluingrelation `xi_N=-xi_S`;
- die gemeinsame tangentiale Verschiebung im selben Intrinsic Chart;
- der bewegte lineare Skalar-Normalflussoperator;
- die M1-Skalar-Junction ohne lokale Skalarquelle;
- der bewegte lineare Gauge-Normalflussoperator;
- die Variation des M1-Kappenstroms;
- die linearisierte U(1)-Invarianz.

## 7. Was ausdrücklich offen bleibt

`[OFFEN / BLOCKIERT]`

- zweite Variation des bewegten GHY-Terms;
- zweite Variation der bewegten lokalisierten Wirkung einschließlich Bending;
- der daraus resultierende vollständige Boundary-Hessian;
- released perturbed Israel/scalar/gauge BVP operator;
- globale Fixed-Interface-Gauge-Admissibilität;
- S/V/T- und Diffeomorphismus-Constraint-Reduktion;
- physischer Hintergrund;
- Ghostfreiheit/Stabilität;
- 6D→4D-Observablemap.

Daher weiterhin:

```text
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
