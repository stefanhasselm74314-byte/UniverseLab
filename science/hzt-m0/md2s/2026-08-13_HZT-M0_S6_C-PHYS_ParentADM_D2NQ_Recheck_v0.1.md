# HZT-M0 / S6 / C-PHYS — Parent-ADM- und D2N-Q-Neuherleitung v0.1

**Datum:** 2026-08-13  
**ID:** `C-PHYS-PARENT-ADM-D2NQ-RECHECK-01`  
**Status:** `PASS_FORMAL_PARENT_ADM_AND_D2NQ_KINEMATIC_PROJECTION_DYNAMICAL_SELECTION_OPEN_NO_K1D_RELEASE`

## 0. Zweck und harte Eingangs-Firewall

Diese Neuherleitung verwendet ausschließlich die bereits kanonischen UniverseLab-Artefakte der SCI-001/SCI-002-Parentwirkung und der C-PHYS-M1-Funktionsfamilie. Die im Chat vorgelegten Gemini-Blöcke werden **nicht** als Gleichungen, Resultate, Code-Validierung oder physikalische Evidenz verwendet.

```text
Gemini material = EXTERNAL_UNVERIFIED_GEMINI_DRAFT
signature imported from Gemini = NO
second time imported into C-PHYS = NO
```

Der kanonische Kontrollzweig bleibt einzeitig:

\[
\operatorname{sig}(g_{AB})=(-,+,+,+,+,+),
\]

mit positiv-definitem zweidimensionalem internen Raum. Die regulierte codimension-2-Quelle wird im aktuellen Parentmodell durch eine **codimension-1 Cap-Schnittstelle** dargestellt. Eine idealisierte \(\delta^{(2)}\)-4D-Brane mit naiv übernommenen codimension-1-Israelbedingungen ist daher **nicht** der kanonische Ausgangspunkt.

---

## 1. Kanonische Parentwirkung

Die eingefrorene SCI-001/SCI-002-Wirkung lautet

\[
\begin{aligned}
S_{\rm core}={}&\sum_{s=\pm}\int_{\mathcal M_s}d^6X\sqrt{-g}\left[
\frac{M_6^4}{2}(R-2\Lambda_6)
-\frac12 g^{AB}\partial_A\phi\partial_B\phi
-U(\phi)
-\frac14 Z_F(\phi)F_{AB}F^{AB}
\right]\\
&+M_6^4\sum_{s=\pm}\int_{\Sigma_5}d^5x\sqrt{-h}\,K_s
+\int_{\Sigma_5}d^5x\sqrt{-h}\,\mathcal L_\Sigma,
\end{aligned}
\]

mit

\[
\mathcal L_\Sigma=-\lambda(\phi)-\frac12 Z_\sigma(\phi)h^{ab}D_a\sigma D_b\sigma,
\qquad
D_a\sigma=\partial_a\sigma-q_\Sigma A_a.
\]

Wichtig für die Dimensionshygiene:

\[
[M_6]=M,
\quad [\Lambda_6]=M^2,
\quad [\phi]=M^2,
\quad [U]=M^6,
\quad [F_{AB}]=M^3.
\]

Damit hat der kosmologische Bulkterm \(M_6^4\Lambda_6\) die korrekte Dichte-Dimension \(M^6\). Eine separate Annahme \([\Lambda_6]=M^6\) wäre mit dieser kanonischen Normierung falsch.

Für M1 gilt zusätzlich

\[
\varphi=\frac{\phi}{M_6^2},
\qquad
U=\frac12\widehat m_\phi^2 M_6^6\varphi^2,
\qquad
Z_F=e^{-2a_F\varphi}>0,
\]

\[
\lambda=\widehat\lambda M_6^5,
\qquad
Z_\sigma=\widehat z_\sigma M_6^3>0
\]

auf dem aktiven Winding-Zweig.

---

## 2. Variation: was tatsächlich aus der Wirkung folgt

Die Variation des Einstein-Hilbert-Terms plus der GHY-Terme liefert im Bulk

\[
M_6^4(G_{AB}+\Lambda_6 g_{AB})=T^{(\phi)}_{AB}+T^{(F)}_{AB},
\]

wobei

\[
T^{(\phi)}_{AB}=\partial_A\phi\partial_B\phi-g_{AB}\left[\frac12(\partial\phi)^2+U\right],
\]

\[
T^{(F)}_{AB}=Z_F\left(F_{AC}F_B{}^C-\frac14g_{AB}F^2\right).
\]

Die unabhängigen Materievariationen ergeben

\[
\Box_6\phi-U_{,\phi}-\frac14 Z_{F,\phi}F^2=0,
\]

\[
\nabla_A(Z_FF^{AB})=0.
\]

An der regulierten Cap-Schnittstelle folgt aus der Metrikvariation

\[
M_6^4\sum_s(K^{(s)}_{ab}-K^{(s)}h_{ab})=S_{ab},
\]

mit

\[
S_{ab}=-\left(\lambda+\frac12Z_\sigma X_\sigma\right)h_{ab}
+Z_\sigma D_a\sigma D_b\sigma,
\qquad
X_\sigma=h^{ab}D_a\sigma D_b\sigma.
\]

Dazu kommen das Skalar-, Gauge- und Phasenmatching der kanonischen Parentwirkung. Diese Variation bestätigt den bestehenden SCI-001/SCI-002-Randabschluss. Sie erzeugt **nicht automatisch** einen Term \(\rho^2\) in einer 4D-Friedmann-Gleichung. Quadratische Materieterme können erst nach einer zusätzlichen Eliminierung der extrinsischen Krümmung durch passende Junction-/Embedding-Gleichungen entstehen.

---

## 3. Zeitliche 5+1-ADM-Zerlegung des einzeitigen Parentraums

Wir zerlegen nach der **einen** physikalischen Zeit:

\[
ds_6^2=-N^2dt^2+h_{ab}(dx^a+N^a dt)(dx^b+N^b dt),
\qquad a,b=1,\ldots,5.
\]

Mit der Konvention

\[
K_{ab}=\frac{1}{2N}(\dot h_{ab}-D_aN_b-D_bN_a)
\]

wird nach Entfernung der üblichen totalen Zeitableitung der Gravitationsanteil

\[
\mathcal L_g=\frac{M_6^4}{2}N\sqrt h
\left({}^{(5)}R+K_{ab}K^{ab}-K^2-2\Lambda_6\right).
\]

### 3.1 Gravitationsimpuls

Direkte Ableitung nach \(\dot h_{ab}\) ergibt

\[
\boxed{
\pi^{ab}=\frac{M_6^4}{2}\sqrt h\,(K^{ab}-h^{ab}K)
}.
\]

Da die räumliche Dimension \(d=5\) ist,

\[
\pi=h_{ab}\pi^{ab}=-2M_6^4\sqrt h\,K,
\]

und somit

\[
\boxed{
K_{ab}=\frac{2}{M_6^4\sqrt h}
\left(\pi_{ab}-\frac14h_{ab}\pi\right).
}
\]

Die \(1/4\)-Spurprojektion ist spezifisch für fünf räumliche Dimensionen. Eine aus 3+1-GR übernommene \(1/2\)-Spurprojektion wäre hier falsch.

### 3.2 Skalar- und Gaugeimpulse

Für den kanonisch normierten Bulk-Skalar:

\[
\boxed{
p_\phi=\frac{\sqrt h}{N}(\dot\phi-N^aD_a\phi).
}
\]

Für das Gaugefeld, mit elektrischem Feld relativ zur ADM-Normale \(E^a\):

\[
\boxed{
\Pi_A^a=\sqrt h\,Z_F E^a.
}
\]

Die Massendimensionen lauten

\[
[\pi^{ab}]=M^5,
\qquad
[p_\phi]=M^3,
\qquad
[\Pi_A^a]=M^3.
\]

---

## 4. Parent-Hamiltonian und Constraints

Bis auf räumliche Rand-/Cap-Terme besitzt die kanonische Form die Struktur

\[
S=\int dt\,d^5x
\left[
\pi^{ab}\dot h_{ab}+p_\phi\dot\phi+\Pi_A^a\dot A_a
-N\mathcal H_\perp-N^a\mathcal H_a-A_0\mathcal G_A
\right]+S_{\rm cap/corner}.
\]

### 4.1 Hamilton-Zwang

Für den Bulk folgt

\[
\boxed{
\begin{aligned}
\mathcal H_\perp={}&
\frac{2}{M_6^4\sqrt h}
\left(\pi_{ab}\pi^{ab}-\frac14\pi^2\right)
+\frac{p_\phi^2}{2\sqrt h}
+\frac{\Pi_{Aa}\Pi_A^a}{2\sqrt h\,Z_F}
\\
&+\sqrt h\left[
-\frac{M_6^4}{2}({}^{(5)}R-2\Lambda_6)
+\frac12D_a\phi D^a\phi
+U(\phi)
+\frac{Z_F}{4}F_{ab}F^{ab}
\right]
\approx0.
\end{aligned}
}
\]

Jeder Term besitzt die Massendimension \(M^6\).

### 4.2 Impuls-Zwang

\[
\boxed{
\mathcal H_a=-2D_b\pi^b{}_a+p_\phi D_a\phi+\Pi_A^bF_{ab}\approx0.
}
\]

### 4.3 Gauge-Zwang

Die Variation von \(A_0\) liefert die Gaußbedingung

\[
\mathcal G_A=-D_a\Pi_A^a+\rho_{\Sigma,A}\,\delta_\Sigma\approx0,
\]

wobei das Vorzeichen der lokalisierten Ladungsdichte an die bereits eingefrorene \(D_a\sigma=\partial_a\sigma-q_\Sigma A_a\)-Konvention gebunden wird.

### 4.4 Cap-Beitrag

Wenn die Cap statisch relativ zur gemeinsamen Zeitfoliation liegt, besitzt ihre Phase lokal die Hamiltonstruktur

\[
\mathcal H_\Sigma=
\frac{p_\sigma^2}{2\sqrt q\,Z_\sigma}
+\sqrt q\left[
\lambda+\frac12Z_\sigma q^{IJ}D_I\sigma D_J\sigma
\right]
\]

zuzüglich Shift-/Gauge-Zwangsterme. Diese Formel ist **konditional** auf eine gemeinsame statische Cap-Foliation; bewegte Caps und Corner-Terme erfordern eine eigene kanonische Behandlung.

---

## 5. Was der Hamiltonian über Ghosts sagt — und was nicht

Für M1 sind die Bulk-Skalar- und Gauge-Momentumquadrate lokal positiv:

\[
\frac{p_\phi^2}{2\sqrt h}\ge0,
\qquad
\frac{\Pi_A^2}{2\sqrt h Z_F}\ge0,
\qquad Z_F>0.
\]

Auf dem aktiven Winding-Zweig gilt ebenso \(Z_\sigma>0\), sodass die Cap-Phasenkinetik bei statischer Cap positiv ist.

Der Gravitationsanteil enthält dagegen die bekannte DeWitt-Kombination

\[
\pi_{ab}\pi^{ab}-\frac14\pi^2.
\]

Der negative Spurterm ist **kein automatischer physikalischer Ghost**. Lapse und Shift sind Lagrange-Multiplikatoren; Hamilton- und Impuls-Zwang sowie Diffeomorphismen reduzieren den Phasenraum. Eine Ghost-Aussage darf erst nach Eliminierung der Constraints und Bestimmung der physikalischen quadratischen Freiheitsgrade erfolgen.

Daher ist aktuell nur zulässig:

```text
bulk scalar kinetic sign = PASS
bulk gauge kinetic sign  = PASS for M1
cap phase kinetic sign   = PASS conditional on static-cap split
full spin-2/1/0 ghost freedom = OPEN
```

Insbesondere wird keine zweite Zeit durch eine zusätzliche Isometriebedingung „weggeeicht“. Der C-PHYS-Zweig besitzt von Anfang an nur eine physikalische Zeit.

---

## 6. Gauß-Projektion auf eine FLRW-symmetrische 4D-Untermannigfaltigkeit

Jetzt wird der D2N-Q-relevante Schritt unabhängig hergeleitet.

Seien \(n_i^A\), \(i=1,2\), zwei **raumartige** orthonormale Normalen mit

\[
\eta_{ij}=\delta_{ij}.
\]

Für eine räumlich isotrope 4D-FLRW-Einbettung ist die allgemeinste extrinsische Krümmung pro Normalrichtung

\[
\boxed{
K^i_{\mu\nu}=\alpha^i u_\mu u_\nu+\beta^i\gamma_{\mu\nu},
}
\]

wobei

\[
\gamma_{\mu\nu}=g_{\mu\nu}+u_\mu u_\nu.
\]

Definiere

\[
\boxed{B^2\equiv\beta_i\beta^i\ge0.}
\]

Dann

\[
K_i=-\alpha_i+3\beta_i,
\qquad
K^i_{\rho\sigma}K_i^{\rho\sigma}=\alpha_i\alpha^i+3\beta_i\beta^i.
\]

Der rein extrinsische Gauß-Tensor sei

\[
Q_{\mu\nu}
=K_iK^i_{\mu\nu}
-K^i_{\mu\rho}K_{\nu}^{i\ \rho}
-\frac12g_{\mu\nu}
\left(K_iK^i-K^i_{\rho\sigma}K_i^{\rho\sigma}\right).
\]

Direkte Kontraktion liefert **exakt**

\[
\boxed{Q_{00}=3B^2}
\]

und

\[
\boxed{
Q_{\mu\nu}^{\rm spatial}
=\left(2\alpha_i\beta^i-B^2\right)\gamma_{\mu\nu}.
}
\]

Dies ist der erste scharfe D2N-Q-Anschluss: Die 00-Komponente des extrinsischen Gaußterms hängt bei FLRW-Symmetrie tatsächlich nur von \(B^2\) ab; der zweite isotrope Extrinsikparameter \(\alpha_i\) fällt aus \(Q_{00}\) heraus.

---

## 7. Effektive D2N-Q-Flüssigkeit — exakt kinematisch, noch nicht dynamisch ausgewählt

Falls die vollständige 4D-Projektionsgleichung nach korrekter Integration/Normalisierung in der Form

\[
M_4^2 G^{(4)}_{\mu\nu}
=T^{(4)}_{\mu\nu}+M_4^2Q_{\mu\nu}+\text{weitere Bulk/Weyl-Terme}
\]

geschrieben werden kann, ist die **kinematische** Identifikation

\[
\boxed{\rho_Q=3M_4^2B^2}
\]

und

\[
\boxed{p_Q=M_4^2(2\alpha_i\beta^i-B^2)}.
\]

Damit

\[
w_Q=\frac{2\alpha_i\beta^i-B^2}{3B^2}.
\]

Diese Gleichungen sind kein Fit und keine Gemini-Annahme; sie folgen algebraisch aus der FLRW-Form von \(K^i_{\mu\nu}\) und dem Gaußterm.

Aber: \(Q_{\mu\nu}\) ist im Allgemeinen **nicht** die gesamte 4D-Korrektur. Projektionen des 6D-Ricci- und Weyl-Tensors sowie mögliche Normalbündel-/Cap-Beiträge müssen separat geschlossen werden.

---

## 8. Normal-Codazzi und die Herkunft der Skalierung

Der kontrahierte Codazzi-Sektor liefert in normalbündel-kovarianter Form

\[
\boxed{
D_t^\perp\beta_i+H(\alpha_i+\beta_i)=\frac13S_i,
}
\]

wobei \(S_i\) die normal-tangentiale Projektion der 6D-Quellen einschließlich der gewählten Normalverbindung zusammenfasst.

In einem lokalen Fermi-Normalrahmen und nur falls der relevante Quellterm verschwindet:

\[
\boxed{\dot\beta_i+H(\alpha_i+\beta_i)=0.}
\]

Dann ergeben sich zwei bemerkenswerte Speziallösungen:

### 8.1 Vakuumartige Komponente

Setze

\[
\alpha_\Lambda=-\beta_\Lambda.
\]

Dann

\[
\dot\beta_\Lambda=0,
\]

und

\[
p_\Lambda=-\rho_\Lambda,
\qquad w_\Lambda=-1.
\]

### 8.2 Materieartige Komponente

Setze

\[
\alpha_m=\frac12\beta_m.
\]

Dann

\[
\dot\beta_m+\frac32H\beta_m=0,
\]

also

\[
\beta_m\propto a^{-3/2},
\qquad
\beta_m^2\propto a^{-3},
\]

und gleichzeitig

\[
p_m=0.
\]

---

## 9. Exakte kinematische Realisierung des bisherigen D2N-Q-Ansatzes

Der zweidimensionale positive Normalraum erlaubt lokal zwei orthonormale Richtungen \(e_\Lambda^i\) und \(e_m^i\). Wähle die **konditionale** Zerlegung

\[
\beta^i
=B_\Lambda e_\Lambda^i
+B_m a^{-3/2}e_m^i,
\]

\[
\alpha^i
=-B_\Lambda e_\Lambda^i
+\frac12B_m a^{-3/2}e_m^i,
\]

mit

\[
e_{\Lambda i}e_m^i=0.
\]

Dann folgt algebraisch

\[
\boxed{
B^2=B_\Lambda^2+B_m^2a^{-3}
}
\]

und damit

\[
\boxed{
\rho_Q=3M_4^2(B_\Lambda^2+B_m^2a^{-3})
}
\]

sowie

\[
\boxed{
p_Q=-3M_4^2B_\Lambda^2.}
\]

Damit ist die **Form** des bisherigen D2N-Q-Ansatzes erstmals aus einer transparenten FLRW-Gauß-Codazzi-Konstruktion reproduziert.

Der Status ist jedoch streng:

\[
\boxed{
\text{D2N-Q functional form: exact kinematic realization}
\neq
\text{parent-dynamical derivation}.
}
\]

Denn die Parentwirkung hat noch nicht gezeigt, dass sie gerade die beiden Relationen

\[
\alpha_\Lambda=-\beta_\Lambda,
\qquad
\alpha_m=\frac12\beta_m
\]

und deren Orthogonalität dynamisch auswählt.

---

## 10. Vierdimensionale Planck-Normierung

Für einen statischen Warp-Faktor im aktuellen Hintergrundansatz

\[
ds_6^2=e^{2A(y)}g_{\mu\nu}^{(4)}dx^\mu dx^\nu+\gamma_{ij}(y)dy^idy^j
\]

enthält die 6D-Ricciwirkung den 4D-Einstein-Term mit

\[
\boxed{
M_4^2=M_6^4\sum_s\int_{\mathcal K_{2,s}}d^2y\sqrt{\gamma_2}\,e^{2A(y)}.
}
\]

Für \(\gamma_2=dr^2+L^2(r)d\chi^2\) wird

\[
M_4^2=M_6^4\sum_s\int dr\,d\chi\,L_s(r)e^{2A_s(r)}.
\]

Dies fixiert die Normierung von \(\rho_Q=3M_4^2B^2\) **konditional** auf eine endliche statische Zero-Mode-Reduktion. In einer voll zeitabhängigen Normalgeometrie muss zusätzlich geprüft werden, ob \(M_4\) konstant bleibt.

---

## 11. Exakter verbleibender K1-D-Blocker

Die bisher diffuse Lücke ist jetzt enger. Für eine echte Parent-Derivation des D2N-Q-Hintergrunds müssen aus den **zeitabhängigen** 6D-M1-Gleichungen und dem Cap-Matching ohne Einsetzen des gewünschten Ergebnisses folgen oder widerlegt werden:

1. der relevante normal-tangentiale Codazzi-Quellterm \(S_i\) bzw. seine genaue Form;
2. die dynamischen Relationen zwischen \(\alpha_i\) und \(\beta_i\);
3. die Existenz zweier orthogonaler normaler Eigenkomponenten mit den erforderlichen Vakuum-/Materie-Skalierungen;
4. die Werte \(B_\Lambda\) und \(B_m\) aus Regularität, Flux, Cap-Daten und Integrationskonstanten;
5. die vollständigen projizierten Ricci-/Weyl-Beiträge;
6. die Konstanz bzw. Dynamik der effektiven Planckmasse;
7. die constrained S/V/T-Stabilität des resultierenden zeitabhängigen Hintergrunds.

Erst wenn diese Punkte geschlossen sind, ist eine Parent-Abbildung

\[
S_{6D}\longrightarrow B^2(a)\longrightarrow \rho_Q(a),p_Q(a)
\]

wirklich hergestellt.

---

## 12. Bounce- und \(\rho^2\)-Disposition

Aus der kanonischen Parentwirkung und dem oben hergeleiteten Hamilton-Zwang folgt **kein** universeller Term

\[
-\frac{\rho^2}{36M_6^4}
\]

in \(H^2\). Schon dimensionsmäßig wäre dieser Ausdruck in der angegebenen Form inkompatibel mit \([H^2]=M^2\), da \([\rho^2/M_6^4]=M^4\) für eine 4D-Dichte \([\rho]=M^4\).

Ein Bounce erfordert mindestens eine tatsächlich gelöste zeitabhängige Constraint-/Evolutionslösung mit

\[
H(t_b)=0,
\qquad
\dot H(t_b)>0,
\]

plus Regularität, Constraint-Persistenz und Störungsstabilität. Keines dieser Bounce-Gates wird durch diese formale Neuherleitung geschlossen.

---

## 13. Ergebnis-Matrix

| Aussage | Status |
|---|---|
| SCI-001/002-Variation reproduziert | **bewiesen / formal rederiviert** |
| 5+1-ADM-Hamilton-Zwang | **bewiesen / formal rederiviert** |
| Skalar-/Gauge-Kinetikzeichen für M1 | **bewiesen lokal** |
| vollständige Ghostfreiheit | **offen** |
| \(Q_{00}=3B^2\) für FLRW-Einbettung | **bewiesen** |
| \(\rho_Q=3M_4^2B^2\) | **konditional auf 4D-Einstein-Normierung** |
| \(B^2=B_\Lambda^2+B_m^2a^{-3}\) | **exakt kinematisch konstruiert** |
| dynamische Auswahl dieser D2N-Q-Zerlegung durch M1 | **offen** |
| \(B_\Lambda,B_m\) aus Parent-Integrationsdaten bestimmt | **offen** |
| negativer \(\rho^2\)-Bounce-Term | **nicht hergeleitet / Gemini-Behauptung verworfen** |
| globaler Bounce | **offen** |
| K1-D | **NOT_RELEASED** |
| K1-E | **NOT_ADMISSIBLE** |
| physikalische Evidenz | **NONE** |

---

## 14. Nächster zulässiger Block

\[
\boxed{
\texttt{C-PHYS-PARENT-H2-DYNAMIC-NORMAL-EQUATIONS-AND-D2NQ-SELECTION-TEST}
}
\]

Dort ist ein zeitabhängiger, einzeitiger 6D-FLRW-plus-internal Ansatz aus der kanonischen M1-Parentwirkung zu variieren. Ziel ist **nicht**, die gewünschte D2N-Q-Skalierung einzusetzen, sondern die Normalgleichungen für \(\alpha_i\), \(\beta_i\), Normalverbindung, Weyl-/Ricci-Projektion und Cap-Daten herzuleiten und anschließend zu prüfen, ob der \(w=-1\) plus \(w=0\)-Sektor tatsächlich eine zulässige Lösung ist.

Keine K1-D-Freigabe erfolgt in diesem Block.
