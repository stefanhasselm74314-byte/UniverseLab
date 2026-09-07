# ULSH-05 / WP1C3 — Cap Bending and Perturbed Junction Geometry Preflight v0.1

**Datum:** 2026-09-07  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `95e15217b4ddc173b7e22f3caf32e7346e38b6ed`  
**Status:** `DERIVED_DOUBLY_COVARIANT_LINEAR_MOVING_INTERFACE_GEOMETRY_PREFLIGHT_FULL_PERTURBED_JUNCTION_AND_BOUNDARY_HESSIAN_OPEN`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Zweck

WP1C2 hat die lokalisierte Kappenwirkung bei **festgehaltener Einbettung** bis zur exakten quadratischen Dichte geschlossen. Das ist ein kontrolliertes Rechenproblem, aber keine Aussage, dass die physische Kappe nicht biegt.

WP1C3 führt daher erstmals die bewegte Grenzfläche explizit ein und friert die lineare Geometrie ein, die später für den vollständigen Rand-Hessian und die pertubierten Junction-Bedingungen benötigt wird.

Der Block ist rein analytisch und nichtoperativ. Er erzeugt weder eine Hintergrundlösung noch einen Modensolver oder 4D-Observablen.

## 2. Kanonische Hintergrundgeometrie

Die Kappe ist eine timelike 5D-Hyperfläche `Sigma5` mit intrinsischen Koordinaten `y^a`, Hintergrundseinbettung

\[
\bar Z^A(y),
\]

Tangenten

\[
e_a{}^A=\partial_a\bar Z^A,
\]

und spacelike outward unit normal

\[
\bar n_A e_a{}^A=0,
\qquad
\bar n_A\bar n^A=+1.
\]

Die induzierte Metrik ist

\[
\bar h_{ab}=e_a{}^Ae_b{}^B\bar g_{AB}.
\]

Wir behalten exakt die bereits eingefrorene UniverseLab-Konvention

\[
\boxed{
\bar K_{ab}
=e_a{}^Ae_b{}^B\bar\nabla_A\bar n_B
=\frac12e_a{}^Ae_b{}^B\mathcal L_{\bar n}\bar g_{AB}.
}
\]

Die Normalen zeigen auf jeder Region nach außen.

## 3. Bewegte Einbettung

Setze

\[
g_{AB}=\bar g_{AB}+p_{AB},
\]

\[
Z^A=\bar Z^A+z^A.
\]

Die Einbettungsperturbation wird zerlegt als

\[
\boxed{
z^A=\xi\bar n^A+\tau^ae_a{}^A.
}
\]

`xi` ist die normale Biegungsvariable, `tau^a` der tangentiale beziehungsweise intrinsische Reparametrisierungssektor.

## 4. Zwei verschiedene Gauge-Strukturen

### 4.1 Bulk-D-Gauge

Unter einer infinitesimalen 6D-Koordinatentransformation mit Generator `zeta^A` verwenden wir

\[
p_{AB}\rightarrow p_{AB}-\mathcal L_\zeta\bar g_{AB},
\]

\[
z^A\rightarrow z^A+\zeta^A.
\]

### 4.2 Intrinsische Reparametrisierung

Eine unabhängige Transformation der Oberflächenkoordinaten

\[
y^a\rightarrow y^a+\bar\zeta^a(y)
\]

verschiebt den tangentialen Einbettungsanteil. Pullbacktensoren transformieren dabei als 5D-Tensorperturbationen.

Diese beiden Symmetrien dürfen nicht identifiziert werden.

## 5. Induzierte Metrik — doubly-covariant Masterform

Die lineare Änderung der ersten Fundamentalform lautet

\[
\boxed{
H_{ab}\equiv\delta h_{ab}
=e_a{}^Ae_b{}^B
\left[
p_{AB}+\mathcal L_z\bar g_{AB}
\right].
}
\]

Unter der Bulk-D-Gauge-Transformation kompensieren sich beide Terme exakt.

Mit der Normal-/Tangentialzerlegung folgt

\[
\boxed{
H_{ab}
=p_{ab}+2\xi\bar K_{ab}+2D_{(a}\tau_{b)},
}
\]

wobei

\[
p_{ab}=e_a{}^Ae_b{}^Bp_{AB}.
\]

Im WP1C2-Fixed-Interface-Limit `xi=tau=0` wird daraus wieder `H_ab=p_ab`.

## 6. Variation des Unit-Normalenfeldes

Die universelle lineare Bestimmung von `delta n_A` erfolgt durch Orthogonalität und Normierung:

\[
e_a{}^A\delta n_A
=\bar n_A\mathcal L_z e_a{}^A,
\]

\[
\boxed{
\bar n^A\delta n_A
=\frac12\bar n^A\bar n^B p_{AB}.
}
\]

Eine vereinfachte Komponentenform darf nur in einer ausdrücklich deklarierten adaptierten Koordinaten-/Extensionskonvention verwendet werden. WP1C3 friert deshalb die geometrischen Masterbedingungen ein und vermeidet einen stillen globalen Gauge-Spezialfall.

## 7. Connection-Variation

Mit erster, durch `gbar` abgesenkter Indexposition definieren wir

\[
\boxed{
\delta\Gamma_{CAB}
=\frac12\left(
\bar\nabla_Ap_{CB}
+\bar\nabla_Bp_{CA}
-\bar\nabla_Cp_{AB}
\right).
}
\]

## 8. Extrinsische Krümmung — Masterform

Die doubly-covariant Variation lautet

\[
\boxed{
\delta K_{ab}
=\frac12 e_a{}^Ae_b{}^B
\left[
\mathcal L_{\delta n}\bar g_{AB}
+\mathcal L_z\mathcal L_{\bar n}\bar g_{AB}
-2\bar n^C\delta\Gamma_{CAB}
\right].
}
\]

Diese Form ist unter der deklarierten 6D-D-Gauge-Transformation invariant und verhält sich unter intrinsischen Reparametrisierungen wie eine 5D-Tensorperturbation.

Wir frieren **noch keine** auf Riemann-Komponenten reduzierte Formel ein, weil eine solche Form zusätzlich eine explizite Riemann-Vorzeichenkonvention benötigt.

### Externe mathematische Kontrolle

Die Struktur wird gegen S. Mukohyama, *Perturbation of junction condition and doubly gauge-invariant variables*, Class. Quant. Grav. 17 (2000) 4777–4798, arXiv:hep-th/0006146 gegengeprüft. Diese Literaturreferenz ist mathematische Kontrolle, nicht UniverseLab-Projektautorität.

## 9. Zwei unabhängige Vorzeichenkontrollen

### 9.1 Flache Graphfläche

Für

\[
ds^2=dr^2+\eta_{ab}dy^ady^b
\]

und

\[
r=\epsilon\xi(y)
\]

ist

\[
\bar K_{ab}=0.
\]

Direkte Berechnung des normalisierten Normalenfeldes ergibt am Hintergrund

\[
\boxed{
\delta K_{ab}=-\partial_a\partial_b\xi.
}
\]

Damit wird das Vorzeichen des Bending-Hessian unabhängig vom Masterausdruck kontrolliert.

### 9.2 Parallele Verschiebung eines Warphintergrunds

Für

\[
ds^2=dr^2+e^{2cr}\eta_{ab}dy^ady^b
\]

ist

\[
\bar K_{ab}=c\bar h_{ab}.
\]

Eine konstante Normalverschiebung `xi` liefert exakt

\[
\boxed{
\delta h_{ab}=2\xi\bar K_{ab},
}
\]

und

\[
\boxed{
\delta K_{ab}
=\xi\partial_n\bar K_{ab}
=2c^2\xi\bar h_{ab}.
}
\]

Auch dies ist ein rein geometrischer Kontrollfall und keine C-PHYS-Hintergrundlösung.

## 10. Moving Pullbacks

Für einen Bulk-Tensor `T` gilt allgemein

\[
\boxed{
\delta_\Sigma(X^*T)
=\bar X^*\left(\delta T+\mathcal L_z\bar T\right).
}
\]

Insbesondere

\[
\delta_\Sigma\phi
=\varphi+z^A\bar\nabla_A\bar\phi,
\]

\[
\delta_\Sigma F_{ab}
=e_a{}^Ae_b{}^B
\left(f_{AB}+\mathcal L_z\bar F_{AB}\right),
\]

und für den Gauge-Potential-Pullback

\[
a_a^\Sigma
=e_a{}^A
\left(a_A+\mathcal L_z\bar A_A\right).
\]

Unter U(1)

\[
a_a^\Sigma\rightarrow a_a^\Sigma+D_a\alpha_\Sigma,
\qquad
s\rightarrow s+q_\sigma\alpha_\Sigma,
\]

sodass

\[
\boxed{
d_a^\Sigma=D_as-q_\sigma a_a^\Sigma
}
\]

invariant ist.

Die vollständige Variation der **normalen** Skalar- und Gaugeflüsse wird erst im nächsten Block assembliert.

## 11. Perturbierte erste Fundamentalform

Vor jeder pertubierten Israelgleichung muss gelten

\[
\boxed{
H_{ab}^{(N)}=H_{ab}^{(S)}
}
\]

nach Pullback auf **denselben** deklarierten intrinsischen Interface-Chart.

## 12. Perturbierter Israel-Operator

Definiere auf jeder Seite

\[
J_{ab}=K_{ab}-Kh_{ab}.
\]

Da

\[
\delta K
=\bar h^{cd}\delta K_{cd}
-H^{cd}\bar K_{cd},
\]

folgt exakt

\[
\boxed{
\begin{aligned}
\delta J_{ab}={}&
\delta K_{ab}
-\bar h_{ab}\bar h^{cd}\delta K_{cd}\\
&+\bar h_{ab}\bar K^{cd}H_{cd}
-\bar K H_{ab}.
\end{aligned}
}
\]

Die outward-sum Form des späteren pertubierten Israel-Kanals lautet

\[
\boxed{
M_6^4\sum_{s=\pm}\delta J_{ab}^{(s)}
=\delta S_{ab}.
}
\]

WP1C3 friert diese lineare Operatoridentität ein, veröffentlicht aber noch **kein** vollständig assembliertes Zwei-Seiten-Junctionsystem.

## 13. Variation des M1-Kappenstresses

Mit

\[
S_{ab}
=-\left(\lambda+\frac12Z_\sigma X\right)h_{ab}
+Z_\sigma w_aw_b,
\]

\[
X=h^{ab}w_aw_b
\]

und den in M1 konstanten Funktionen `lambda` und `Z_sigma` folgt

\[
\boxed{
\delta X
=2w^a\delta w_a-H^{ab}w_aw_b,
}
\]

\[
\boxed{
\begin{aligned}
\delta S_{ab}={}&
-\frac12Z_\sigma\delta X\,\bar h_{ab}
-\left(\lambda+\frac12Z_\sigma\bar X\right)H_{ab}\\
&+Z_\sigma\left(
\delta w_a w_b+w_a\delta w_b
\right).
\end{aligned}
}
\]

Dies ist die lineare Oberflächenstressantwort, nicht der vollständige Moving-Boundary-Hessian.

## 14. Zwei-Seiten-Bending bleibt ein echtes Gluing-Problem

Die eingefrorenen lokalen Koordinaten besitzen

```text
r_N : pole -> cap
r_S : pole -> cap
n_N^r = +1
n_S^r = +1
```

in **jeweils eigener** Region.

Daraus darf nicht ohne gemeinsame Einbettungs-/Orientierungsabbildung gefolgert werden, dass

\[
\xi_N=\xi_S
\]

oder

\[
\xi_N=-\xi_S.
\]

Daher bleibt

```text
normal_displacement_gluing_relation = OPEN_REQUIRES_EXPLICIT_INTERFACE_IDENTIFICATION_MAP
```

als harter Blocker für die vollständige pertubierte Junction-Closure bestehen.

## 15. Fixed-Interface-Gauge

Lokal kann eine 6D-D-Gauge mit geeignetem Normalanteil die Einbettungsvariable auf `xi=0` setzen.

Das beweist jedoch nicht, dass die Biegung physikalisch verschwindet. Eine **globale simultane** Fixed-Interface-Gauge auf beiden Regionen muss erst zeigen, dass

1. die Interface-Identifikation kompatibel ist,
2. die Gaugegeneratoren beidseitig zulässig sind,
3. Polregularität und U(1)-Patchbedingungen erhalten bleiben,
4. das Matching der induzierten Metrik erhalten bleibt.

Status:

```text
LOCALLY_AVAILABLE_CONDITIONALLY_GLOBAL_ADMISSIBILITY_NOT_PROVEN
```

## 16. Was jetzt bewiesen ist

`[BEWIESEN]`

- doubly-covariant lineare Variation der induzierten Metrik;
- geometrische Masterbedingungen für den Unit-Normal;
- doubly-covariant lineare Variation von `K_ab`;
- Bulk-D-Gauge-Invarianz der Pullback-Geometrie;
- zwei unabhängige Bending-/Vorzeichenkontrollen;
- generische Moving-Pullback-Regel;
- linearer Israel-Operator `delta J_ab`;
- lineare M1-Surface-Stressvariation.

## 17. Was ausdrücklich offen bleibt

`[OFFEN/BLOCKIERT]`

- Zwei-Seiten-Relation der normalen Biegungsvariablen;
- vollständige Variation des Skalar-Normalflusses;
- vollständige Variation des Gauge-Normalflusses;
- zweiter Moving-Boundary-Variationsschritt von GHY+Kappenwirkung;
- vollständig geschlossener Boundary-Hessian;
- vollständig assembliertes Israel-/Skalar-/Gauge-Junctionsystem;
- S/V/T-Zerlegung;
- Constraint-Elimination;
- physischer Hintergrund;
- Ghostfreiheit/Stabilität;
- 6D→4D-Reduktion und `mu/eta/Sigma`.

## 18. Gate-Status

```text
WP1 moving-interface linear geometry = DERIVED_PREFLIGHT
WP1 full boundary Hessian             = NOT_CLOSED
WP1 full quadratic action             = NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM             = NOT_RELEASED
PHYSICAL_BACKGROUND                   = NOT_ESTABLISHED
FM-G0                                 = OPEN
AuthorizationDecision                 = NOT_CREATED
SingleUseGrant                         = NOT_CREATED
BACKEND_IMPORT                         = NOT_EXECUTED
SOLVER_EXECUTION                       = NOT_EXECUTED
PHYSICAL_RESPONSE_RANK                 = NOT_EXECUTED
K1-D                                   = NOT_RELEASED
K1-E                                   = NOT_ADMISSIBLE
physical_gate_effect                   = NONE
physical_evidence_effect               = NONE
```

Der nächste zulässige Block ist `ULSH-05/WP1C4`: Moving-Boundary-Hessian und vollständige pertubierte Junction-Assembly — weiterhin rein analytisch und ohne physischen Solverlauf.
