# ULSH-05 / WP1C4B2A — Boundary Second-Variation Master

**Datum:** 2026-09-08  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `7d688ebf5b658307892d0efe89afa5b3e34ea219`  
**Klassifikation:** analytischer, nichtoperativer Second-Order-Chain-Rule-Master  
**Physical gate/evidence effect:** `NONE / NONE`

## 1. Ziel und harte Grenze

WP1C4B1D hat die erste bewegte Gesamtwirkungsvariation auf dem Interface in einer gemeinsamen Residualbasis geschlossen. WP1C4B2A differenziert genau diese First-Variation-Struktur ein zweites Mal und trennt dabei strikt

1. die tatsächliche bilineare zweite Fréchet-Variation im deklarierten lokalen affinen Konfigurationschart;
2. die durch einen gewählten beschleunigten Pfad erzeugten Terme `DS[v]`;
3. nichtlineare zweite Pullback-/Induced-Field-Terme, die bereits quadratisch in der ersten Tangente sind und deshalb **zur Chart-Hesse gehören**;
4. off-shell Terme proportional zu den First-Residualen, die nicht verworfen werden dürfen, solange `PHYSICAL_BACKGROUND=NOT_ESTABLISHED` gilt.

Dieser Block schließt noch **nicht** den vollständig komponentisierten Boundary-Hessian-Operator. Insbesondere `Delta R_sigma` und `Delta R_perp` werden hier als wohldefinierte linearisierte Residuen geführt, aber erst im nächsten Block vollständig komponentisiert.

## 2. First-Variation-Basis aus WP1C4B1D

Auf dem abstrakten Interface verwenden wir

\[
U_1=(H_{ab},\Phi_\Sigma,\mathcal A_a,s,\xi)
\]

mit Residuen

\[
\mathcal R=(\mathcal R_h^{ab},\mathcal R_\phi,
\mathcal R_A^a,\mathcal R_\sigma,\mathcal R_\perp).
\]

Der First-Variation-Integrand lautet

\[
B_1
=-\frac12\mathcal R_h^{ab}H_{ab}
-\mathcal R_\phi\Phi_\Sigma
-\mathcal R_A^a\mathcal A_a
+\mathcal R_\sigma s
+\xi\mathcal R_\perp .
\]

Somit

\[
\delta S_\Sigma^{(1)}
=\int_\Sigma\sqrt{-\bar h}\,B_1.
\]

Für die erste Maßvariation gilt

\[
\delta\sqrt{-h}
=\sqrt{-\bar h}\,m_1,
\qquad
m_1=\frac12H,
\qquad
H=\bar h^{ab}H_{ab}.
\]

## 3. Exakte zweite Pfadvariation

Sei

\[
U(\epsilon)
=\bar U+\epsilon U_1+\frac12\epsilon^2U_2+O(\epsilon^3)
\]

mit

\[
U_2=(H_{2,ab},\Phi_{2,\Sigma},\mathcal A_{2,a},s_2,\xi_2).
\]

Die Residuen besitzen

\[
\mathcal R(\epsilon)
=\bar{\mathcal R}+\epsilon\Delta\mathcal R+O(\epsilon^2).
\]

Direktes Differenzieren von `sqrt(-h) B1` liefert

\[
\frac{d^2S_\Sigma}{d\epsilon^2}\Big|_0
=\int_\Sigma\sqrt{-\bar h}\,B_{2,\mathrm{path}}
\]

mit

\[
\begin{aligned}
B_{2,\mathrm{path}}={}&m_1B_1
-\frac12\left(\Delta\mathcal R_h^{ab}H_{ab}
+\mathcal R_h^{ab}H_{2,ab}\right)\\
&-\left(\Delta\mathcal R_\phi\Phi_\Sigma
+\mathcal R_\phi\Phi_{2,\Sigma}\right)\\
&-\left(\Delta\mathcal R_A^a\mathcal A_a
+\mathcal R_A^a\mathcal A_{2,a}\right)\\
&+\left(\Delta\mathcal R_\sigma s
+\mathcal R_\sigma s_2\right)\\
&+\left(\xi\Delta\mathcal R_\perp
+\xi_2\mathcal R_\perp\right).
\end{aligned}
\]

Der Koeffizient von `epsilon^2` in der Pfadentwicklung ist

\[
S_{\Sigma,\mathrm{path}}^{(2)}
=\frac12\int_\Sigma\sqrt{-\bar h}\,B_{2,\mathrm{path}}.
\]

Diese Gleichung ist nur die Kettenregel; keine EOM und keine Junctionbedingung wurden eingesetzt.

## 4. Chart-Hesse versus Pfadbeschleunigung

WP1C4B0 friert den lokalen affinen Konfigurationschart ein:

\[
\Phi(\epsilon)=\bar\Phi+\epsilon u+\frac12\epsilon^2v+\cdots
\]

und damit

\[
\frac{d^2S}{d\epsilon^2}\Big|_0
=D^2S[u,u]+DS[v].
\]

Die zweite Interfacevariation zerfällt entsprechend in

\[
U_2=U_{2,\mathrm{bil}}[u,u]+U_{2,\mathrm{acc}}[v].
\]

`U2_bil` enthält geometrisch nichtlineare zweite Pullbacks/induzierte Größen, die bereits durch die **erste** Konfigurationstangente erzeugt werden. `U2_acc` ist dagegen linear in der frei gewählten zweiten Pfadtangente `v` einschließlich des zugehörigen zweiten Embedding-Generatoranteils.

Damit ist

\[
\frac12DS[v]
=\frac12\int_\Sigma\sqrt{-\bar h}
\left[
-\frac12\mathcal R_h^{ab}H_{2,\mathrm{acc},ab}
-\mathcal R_\phi\Phi_{2,\mathrm{acc}}
-\mathcal R_A^a\mathcal A_{2,\mathrm{acc},a}
+\mathcal R_\sigma s_{2,\mathrm{acc}}
+\xi_{2,\mathrm{acc}}\mathcal R_\perp
\right]
\]

plus die entsprechenden Bulk-/Tangentialkanäle.

Nach **nur dieser** Subtraktion lautet der Boundary-Chart-Hessian-Integrand

\[
\begin{aligned}
B_{2,\mathrm{chart}}={}&m_1B_1
-\frac12\left(\Delta\mathcal R_h^{ab}H_{ab}
+\mathcal R_h^{ab}H_{2,\mathrm{bil},ab}\right)\\
&-\left(\Delta\mathcal R_\phi\Phi_\Sigma
+\mathcal R_\phi\Phi_{2,\mathrm{bil},\Sigma}\right)\\
&-\left(\Delta\mathcal R_A^a\mathcal A_a
+\mathcal R_A^a\mathcal A_{2,\mathrm{bil},a}\right)\\
&+\left(\Delta\mathcal R_\sigma s
+\mathcal R_\sigma s_{2,\mathrm{bil}}\right)\\
&+\left(\xi\Delta\mathcal R_\perp
+\xi_{2,\mathrm{bil}}\mathcal R_\perp\right).
\end{aligned}
\]

### Zentrale Firewall

`PHYSICAL_BACKGROUND=NOT_ESTABLISHED`. Daher darf man **nicht** alle Terme proportional zu `R` verwerfen. Nur der nach C4B0 eindeutig als `DS[v]` identifizierte Acceleration-Anteil wird bei der deklarierten Chart-Hesse subtrahiert.

Ein Term wie

\[
\mathcal R_h^{ab}H_{2,\mathrm{bil},ab}
\]

kann off shell Teil der tatsächlichen zweiten Fréchet-Variation sein und bleibt erhalten.

## 5. Intrinsische Kappenwirkung: exakte Chain Rule

Die gemergte WP1C2-Wirkung ist intrinsisch auf dem abstrakten `Sigma`:

\[
S_\Sigma=-\int\sqrt{-h}
\left[\lambda+\frac12Z_\sigma h^{ab}B_aB_b\right],
\qquad B_a=D_a\sigma.
\]

Für die erste totale induzierte Variation setzen wir

\[
Y_1=(H_{ab},d_{1,a}),
\qquad
d_{1,a}=D_as_1-q_\sigma\mathcal A_{1,a}.
\]

Die zweite totale induzierte Variation sei

\[
Y_2=(H_{2,ab},d_{2,a})
=Y_{2,\mathrm{bil}}+Y_{2,\mathrm{acc}}.
\]

### 5.1 Linearer Dichtekoeffizient

Für beliebige erste Daten `(q_ab,d_a)` gilt

\[
D_1[q,d]=\ell_1[q,d]+n_1[q]\ell_0,
\]

\[
n_1[q]=\frac12q,
\]

\[
\ell_1[q,d]
=-\frac12Z_\sigma
\left(2w^ad_a-q^{ab}w_aw_b\right).
\]

### 5.2 Zweiter Koeffizient eines allgemeinen nichtlinearen Pfads

WP1C2 bezeichnet mit `C2[Y1]` den exakten `epsilon^2`-Koeffizienten eines **affinen induced-field**-Pfads mit erster Tangente `Y1`.

Für

\[
Y(\epsilon)=\bar Y+\epsilon Y_1+\frac12\epsilon^2Y_2+\cdots
\]

gilt durch die normale Taylor-Kettenregel exakt

\[
\boxed{
C_{\Sigma,\mathrm{path}}^{(2)}
=C_2[Y_1]+\frac12D_1[Y_2]
}.
\]

Nach C4B0-Chartsubtraktion bleibt

\[
\boxed{
C_{\Sigma,\mathrm{chart}}^{(2)}
=C_2[Y_1]+\frac12D_1[Y_{2,\mathrm{bil}}]
}.
\]

Das ist entscheidend: **nur** `C2` mit `q→H` einzusetzen wäre im Allgemeinen unvollständig, weil die induzierten Felder bei bewegter Einbettung bereits für einen affinen Parent-Feldpfad nichtlinear in `epsilon` sein können.

### Fixed-interface-Grenzfall

Bei fester Einbettung und affinem induced-field-Pfad gilt

\[
Y_{2,\mathrm{bil}}=0,
\]

und damit

\[
C_{\Sigma,\mathrm{chart}}^{(2)}=C_2[Y_1],
\]

also exakt der gemergte WP1C2-Vertrag.

## 6. Unabhängige nichtlineare Kappenkontrolle

Wir verwenden eine diagonale Lorentz-Metrik

\[
\bar h_{ab}=\mathrm{diag}(-1.2,1.1,0.95,1.3,0.8)
\]

und nichtlineare Pfade

\[
h_i(\epsilon)=\bar h_i+\epsilon q_i+\frac12\epsilon^2r_i,
\]

\[
B_i(\epsilon)=w_i+\epsilon d_i+\frac12\epsilon^2e_i.
\]

Die **unexpandierte** Dichte lautet

\[
F(\epsilon)=\sqrt{-\prod_i h_i(\epsilon)}
\left[-\lambda-\frac12Z_\sigma\sum_i\frac{B_i(\epsilon)^2}{h_i(\epsilon)}\right].
\]

Eine zentrale direkte Finite Difference bestimmt den `epsilon^2`-Koeffizienten. Unabhängig davon werden `C2[q,d]` und `D1[r,e]` aus ihren analytischen Formeln berechnet. Der Test verlangt

\[
F^{(2)}_{\rm coeff}
=C_2[q,d]+\frac12D_1[r,e].
\]

Anschließend wird

\[
r=r_{\rm bil}+r_{\rm acc},
\qquad
e=e_{\rm bil}+e_{\rm acc}
\]

gewählt. Nach Subtraktion von

\[
\frac12D_1[r_{\rm acc},e_{\rm acc}]
\]

muss der direkte Pfadwert

\[
C_2[q,d]+\frac12D_1[r_{\rm bil},e_{\rm bil}]
\]

ergeben. Damit werden bilineare nichtlineare Pullbackterme und echte Pfadbeschleunigung numerisch getrennt.

## 7. Bewegte EH+GHY-Shape-Kontrolle zweiter Ordnung

Der C4B1D-Warpkontrollraum besitzt für einen bewegten oberen Rand `rho`

\[
S_g'(\rho)=e^{5c\rho}(10c^2-\Lambda_6),
\]

\[
S_g''(\rho)=5c\,e^{5c\rho}(10c^2-\Lambda_6).
\]

Wähle einen beschleunigten Randpfad

\[
\rho(\epsilon)
=\rho_0+\epsilon\xi+\frac12\epsilon^2\chi.
\]

Dann ist der direkte Pfadkoeffizient

\[
\boxed{
S_{g,\mathrm{path}}^{(2)}
=\frac12\xi^2S_g''(\rho_0)
+\frac12\chi S_g'(\rho_0)
}.
\]

Der zweite Term ist genau `1/2 DS[v]` im eindimensionalen Shape-Kontrollchart. Nach seiner Subtraktion bleibt

\[
\boxed{
S_{g,\mathrm{chart}}^{(2)}
=\frac12\xi^2S_g''(\rho_0)
}.
\]

Der Kontrollfall wird absichtlich off shell mit `S_g'(rho0) != 0` gewählt, damit eine versehentliche Eliminierung sämtlicher First-Residual-Terme auffällt.

## 8. Residual-Linearisierungsstatus

Der Chain-Rule-Master ist jetzt geschlossen, der vollständig komponentisierte Operator jedoch noch nicht:

- `Delta R_h`: aus WP1C3 linearisiertem Israel-Operator plus WP1C2 Kappenstressvariation assemblierbar;
- `Delta R_phi`: linearer moving scalar-flux Preflight in C4A vorhanden;
- `Delta R_A`: linearer moving gauge-flux Preflight in C4A vorhanden;
- `Delta R_sigma`: für den allgemeinen bewegten Interfacepfad noch nicht komponentisiert;
- `Delta R_perp`: als Linearisierung des C4B1D-`NN`-Constraint-Jumps wohldefiniert, aber noch nicht vollständig in `p,varphi,a,H,xi` komponentisiert.

Daher gilt

```text
WP1_boundary_second_variation_chain_rule = DERIVED
WP1_boundary_residual_linearizations      = PARTIAL_NOT_FULLY_COMPONENTIZED
WP1_full_boundary_hessian                 = NOT_CLOSED_COMPONENT_OPERATOR_AND_SYMMETRY_TEST_OPEN
```

## 9. Was bewiesen ist

**[BEWIESEN]** Exakte zweite Chain Rule der gesamten C4B1D-Interfacebasis.

**[BEWIESEN]** Saubere Trennung `U2_bil + U2_acc` im C4B0-Chart.

**[BEWIESEN]** Die bewegte intrinsische Kappenwirkung erfüllt

\[
C_{\rm path}^{(2)}=C_2[Y_1]+\frac12D_1[Y_2]
\]

und nicht im Allgemeinen nur `C2[Y1]`.

**[BEWIESEN]** Beschleunigte Moving-GHY-Kontrolle trennt den `chi*S_g'`-Pfadterm vom bilinearen `xi^2*S_g''`-Chartterm.

**[OFFEN]** Vollständige komponentisierte `Delta R_sigma`- und `Delta R_perp`-Operatoren.

**[OFFEN]** Gemischte Zwei-Parameter-Symmetrieprüfung des vollständigen gekoppelten Boundary-Hessians.

## 10. Unveränderte Firewalls

```text
WP1 first shape level           CLOSED_ANALYTICALLY_AS_REDUNDANT_CONSTRAINT_CHANNEL
WP1 full boundary Hessian       NOT_CLOSED_COMPONENT_OPERATOR_AND_SYMMETRY_TEST_OPEN
WP1 full quadratic action       NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM       NOT_RELEASED
PHYSICAL_BACKGROUND             NOT_ESTABLISHED
FM-G0                           OPEN
AuthorizationDecision           NOT_CREATED
SingleUseGrant                  NOT_CREATED
BACKEND_IMPORT                  NOT_EXECUTED
SOLVER_EXECUTION                NOT_EXECUTED
PHYSICAL_RESPONSE_RANK         NOT_EXECUTED
K1-D                            NOT_RELEASED
K1-E                            NOT_ADMISSIBLE
physical_gate_effect            NONE
physical_evidence_effect        NONE
```

Nächster Block: `ULSH-05/WP1C4B2B` — komponentisierte Boundary-Residual-Linearisierung und gemischter Zwei-Parameter-Hessian-Symmetrieabschluss.