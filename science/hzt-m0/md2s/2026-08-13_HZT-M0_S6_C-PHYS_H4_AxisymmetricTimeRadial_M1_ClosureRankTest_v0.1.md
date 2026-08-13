# HZT-M0 / S6 / C-PHYS H4 — axisymmetrische zeit-radiale M1-Schließung und Rangtest v0.1

**Datum:** 2026-08-13  
**Block:** `C-PHYS-PARENT-H4-AXISYMMETRIC-TIME-RADIAL-NONSEPARABLE-M1-CLOSURE-AND-RANK-TEST`  
**Status:** `PASS_FORMAL_TIME_RADIAL_M1_REDUCTION_STRUCTURALLY_CLOSED_MODULO_GAUGE_LOCAL_FIELDSPACE_PRINCIPAL_RANK_CAPABLE_D2NQ_DYNAMIC_SELECTION_NOT_EXECUTED`  
**Solverausführung:** nein  
**Physische Evidenzwirkung:** `NONE`

## 1. Ziel und Firewall

H3 v0.2 hat die lokale geometrische Brücke

\[
\beta_r=\frac1c\partial_r\ln a,\qquad
\alpha_r=-\frac1c\partial_r\ln n,\qquad
B^2=\beta_r^2
\]

für einen festen beobachteten radialen Schnitt etabliert und zugleich gezeigt, dass das Zielprofil

\[
B^2=B_\Lambda^2+B_m^2a^{-3}
\]

kinematisch bereits mit einer einzigen Normalrichtung realisierbar ist. H4 beantwortet deshalb die nächste, strengere Frage: Ist der minimale axisymmetrische, aber wirklich zeit-radial nichtseparable M1-Sektor als Parent-PDE-System geschlossen und lokal rangfähig, bevor irgendein physischer Solver gestartet wird?

Gemini-Blöcke bleiben `EXTERNAL_UNVERIFIED_GEMINI_DRAFT`. Es wird weder eine zweite Zeitrichtung importiert noch eine externe Gleichung als Prämisse verwendet.

## 2. Minimaler dynamischer 6D-Sektor

Wir schreiben die Geometrie zunächst kovariant als zweidimensionale Basis plus maximalsymmetrischen 3-Raum und Kreis:

\[
ds_6^2=h_{pq}(t,r)dx^pdx^q+a^2(t,r)q_{ij}^{(k)}dx^idx^j+L^2(t,r)d\chi^2,
\qquad p,q\in\{t,r\},
\]

mit

\[
R[q]=6k.
\]

Lokal kann die zweidimensionale Metrik diagonal gewählt werden,

\[
h_{pq}dx^pdx^q=-n^2(t,r)dt^2+c^2(t,r)dr^2.
\]

`g_tr=0` ist hier eine Koordinatenwahl, keine physische Trunkierung.

Der minimale M1-Materiesektor ist

\[
\phi=\phi(t,r),\qquad A_\chi=A_\chi(t,r),
\]

mit

\[
F_{t\chi}=\partial_tA_\chi,\qquad
F_{r\chi}=\partial_rA_\chi,\qquad
F_{tr}=0.
\]

Der Zweig `F_tr=0` ist ein bewusst enger magnetisch-dynamischer Untersektor. Er ist in dieser Symmetrie konsistent: Die Maxwell-Gleichungen für `t` und `r` werden Identitäten, die `chi`-Gleichung bleibt die einzige nichttriviale Maxwell-PDE. Eine Aussage über den vollständigen elektrischen `F_tr != 0`-Zweig folgt daraus nicht.

## 3. Exakte 2D-Reduktion des Bulk-Sektors

Für den obigen Warp-Ansatz ist der 6D-Ricci-Skalar

\[
R_6=R_2+\frac{6k}{a^2}
-6\frac{\Box a}{a}
-6\frac{(\nabla a)^2}{a^2}
-2\frac{\Box L}{L}
-6\frac{\nabla a\cdot\nabla L}{aL}.
\]

Weiter gilt

\[
\sqrt{|g_6|}=\sqrt{|h|}\,a^3L\sqrt{q}.
\]

Nach partieller Integration der Bulk-Totalableitungen, wobei der kanonische GHY-Abschluss ausdrücklich beibehalten wird, lautet die reduzierte Bulk-Wirkung bis auf das konstante Volumen des homogenen 3-Raums und des Kreises:

\[
\begin{aligned}
S_2=\int d^2x\sqrt{|h|}\Bigg\{&\frac{1}{2\kappa_6^2}
\Big[a^3LR_2+6kaL-2\Lambda_{\rm geom}a^3L
+6aL(\nabla a)^2+6a^2\nabla a\cdot\nabla L\Big]\\
&-a^3L\left[\frac12(\nabla\phi)^2+U(\phi)\right]
-\frac12\frac{a^3Z_F(\phi)}{L}(\nabla A_\chi)^2\Bigg\}.
\end{aligned}
\]

Für C-PHYS-M1 bleibt

\[
Z_\phi=1,
\qquad
U(\phi)=\frac12\hat m_\phi^2M_6^6\left(\frac{\phi}{M_6^2}\right)^2,
\qquad
Z_F(\phi)=\exp\!\left[-2a_F\frac{\phi}{M_6^2}\right]>0.
\]

Damit ist die zeit-radiale Reduktion direkt an die eingefrorene M1-Funktionsfamilie gebunden.

## 4. Kovarianter Gleichungssatz

Die benötigten Ricci-Komponenten können ohne eine frühe Koordinatenfixierung geschrieben werden als

\[
R_{pq}^{(6)}=R_{pq}[h]-3a^{-1}\nabla_p\nabla_q a-L^{-1}\nabla_p\nabla_qL,
\]

\[
\frac{R_{(3)}}{g_{(3)}}=rac{2k}{a^2}-\frac{\Box a}{a}
-2\frac{(\nabla a)^2}{a^2}
-\frac{\nabla a\cdot\nabla L}{aL},
\]

und

\[
\frac{R_{\chi\chi}}{L^2}=-\frac{\Box L}{L}
-3\frac{\nabla a\cdot\nabla L}{aL}.
\]

Der Einstein-Sektor ist

\[
G_{AB}+\Lambda_{\rm geom}g_{AB}=\kappa_6^2T_{AB}.
\]

Die reduzierte Skalargleichung lautet

\[
\boxed{
\frac1{a^3L}\nabla_p\left(a^3L\nabla^p\phi\right)
-U_{,\phi}
-\frac12\frac{Z_{F,\phi}}{L^2}(\nabla A_\chi)^2=0
}
\]

und die einzige nichttriviale Maxwell-Gleichung

\[
\boxed{
\nabla_p\left(\frac{a^3Z_F}{L}\nabla^pA_\chi\right)=0.
}
\]

Für die Basis-Komponenten ist

\[
T_{pq}=\partial_p\phi\partial_q\phi
-\frac12h_{pq}\left[(\nabla\phi)^2+2U\right]
+\frac{Z_F}{L^2}
\left[\partial_pA_\chi\partial_qA_\chi
-\frac12h_{pq}(\nabla A_\chi)^2\right].
\]

Die 3-Raum- und Kreisdrücke sind

\[
\frac{T_{(3)}}{g_{(3)}}=-\frac12(\nabla\phi)^2-U
-\frac12\frac{Z_F}{L^2}(\nabla A_\chi)^2,
\]

\[
\frac{T_{\chi\chi}}{L^2}=-\frac12(\nabla\phi)^2-U
+\frac12\frac{Z_F}{L^2}(\nabla A_\chi)^2.
\]

## 5. Die gemischte Parent-Gleichung wird jetzt explizit testbar

In der diagonalen Darstellung ist `G_tr=R_tr`. Es gilt exakt

\[
\boxed{
R_{tr}=-\frac3a\left[a_{tr}-\frac{n_r}{n}a_t-\frac{c_t}{c}a_r\right]
-\frac1L\left[L_{tr}-\frac{n_r}{n}L_t-\frac{c_t}{c}L_r\right]
}
\]

und

\[
\boxed{
T_{tr}=\phi_t\phi_r+\frac{Z_F}{L^2}A_{\chi,t}A_{\chi,r}.
}
\]

Daher lautet die gemischte Einstein-Gleichung

\[
\boxed{R_{tr}=\kappa_6^2T_{tr}}.
\]

Der in H3 verwendete quellfreie Codazzi-Zweig ist damit nicht länger eine abstrakte Zusatzannahme. Innerhalb dieses H4-Sektors kann er an einer Parent-Lösung direkt geprüft werden. `T_tr=0` ist hinreichend für verschwindenden gemischten Materiefluss auf dem beobachteten Schnitt, aber ausdrücklich keine allgemeine M1-Identität.

## 6. Gleichungs-/Unbekannten-Zählung modulo Eichfreiheit

Vor Koordinatenfixierung besitzen wir sieben Funktionen:

\[
\{h_{tt},h_{tr},h_{rr},a,L,\phi,A_\chi\}.
\]

Die sieben Variationsgleichungen sind:

- drei Basis-Einstein-Gleichungen,
- eine isotrope 3-Raum-Einstein-Gleichung,
- eine `chi-chi`-Einstein-Gleichung,
- die Skalargleichung,
- die `chi`-Maxwell-Gleichung.

Zwei lokale `(t,r)`-Diffeomorphismen stehen zwei Noether/Bianchi-Identitäten gegenüber. Somit bleiben

\[
7-2=5
\]

unabhängige Funktionsfreiheiten und ebenso fünf unabhängige Gleichungskanäle. Der Sektor ist daher

\[
\boxed{\text{strukturell quadratisch modulo 2D-Diffeomorphismen}.}
\]

In der diagonalen Darstellung verbraucht `g_tr=0` eine lokale Koordinatenbedingung. Die `tr`-Einstein-Gleichung darf deshalb nicht gelöscht werden; sie bleibt die Impuls-/Mischconstraint.

## 7. Lokaler Rangfähigkeits-Preflight

Für die lokale Hauptteilanalyse kann die 2D-Metrik in eine konforme Repräsentation gebracht werden,

\[
h_{pq}=e^{2\omega}\eta_{pq}.
\]

Für den Feldvektor

\[
q^I=(\omega,a,L,\phi,A_\chi)
\]

enthält der gravitative Hauptteil

\[
\frac{\eta^{pq}}{2\kappa_6^2}
\left[
6a^2L\,\partial_pa\partial_q\omega
+2a^3\partial_pL\partial_q\omega
+6aL\partial_pa\partial_qa
+6a^2\partial_pa\partial_qL
\right].
\]

Der zugehörige gravitative Feldraumblock ist bis auf den gemeinsamen Faktor

\[
M_g=
\begin{pmatrix}
0&3a^2L&a^3\\
3a^2L&6aL&3a^2\\
a^3&3a^2&0
\end{pmatrix}
\]

mit

\[
\boxed{\det M_g=12a^7L}.
\]

Der Skalar- und Maxwell-Hauptteil liefern zusätzlich die nichtverschwindenden Diagonalgewichte

\[
-\frac12a^3L,
\qquad
-\frac12\frac{a^3Z_F}{L}.
\]

Da im aktiven M1-Bereich

\[
a>0,\qquad L>0,\qquad Z_F>0,
\]

gilt, ist die lokale Feldraum-Hauptteilmatrix in dieser Repräsentation Rang 5.

Das ist ein **Rangfähigkeits-PASS**, aber kein Beweis globaler Hyperbolizität, Constraint-Propagation, zulässiger Randbedingungen, Ghostfreiheit oder physischer Stabilität.

## 8. Dynamische Kappen-Junctions

Für eine Kappe bei festem radialem Koordinatenwert definieren wir auf jeder Seite mit outward orientation `epsilon_s`

\[
k_t^{(s)}=\frac{\epsilon_s}{c_s}\partial_r\ln n_s,
\quad
k_a^{(s)}=\frac{\epsilon_s}{c_s}\partial_r\ln a_s,
\quad
k_\chi^{(s)}=\frac{\epsilon_s}{c_s}\partial_r\ln L_s,
\]

und deren outward sums

\[
K_t=\sum_s k_t^{(s)},\qquad
K_a=\sum_s k_a^{(s)},\qquad
K_\chi=\sum_s k_\chi^{(s)}.
\]

Mit

\[
Y_\sigma=Z_\sigma\frac{(N_\sigma-q_\sigma A_\chi)^2}{L^2}
\]

folgen drei metrische Junctionkanäle:

\[
-(3K_a+K_\chi)+\kappa_6^2\left(\lambda+\frac12Y_\sigma\right)=0,
\]

\[
-(K_t+2K_a+K_\chi)+\kappa_6^2\left(\lambda+\frac12Y_\sigma\right)=0,
\]

\[
-(K_t+3K_a)+\kappa_6^2\left(\lambda-\frac12Y_\sigma\right)=0.
\]

Aus den ersten beiden folgt neu

\[
\boxed{K_t-K_a=0},
\]

also die notwendige 4D-Isotropie des radialen extrinsischen Abschlusses der Kappe. Im statischen Grenzfall `K_t=K_a=A_Sigma` werden exakt die bereits eingefrorenen `R_4d`- und `R_chi`-Junctions zurückgewonnen.

Da M1 `lambda` und `Z_sigma` skalarunabhängig eingefroren hat, reduziert sich das skalare Matching auf

\[
\sum_s\frac{\epsilon_s}{c_s}\partial_r\phi_s=0.
\]

Gauge-Matching, globale Fluxquantisierung, Patchkonsistenz und Regularität bleiben eigenständige Gates.

## 9. D2N-Q jetzt ohne freie Zeit-für-Zeit-Fits testen

Auf einem festen beobachteten Schnitt `r=r_star` definieren wir die Eigenzeit-Hubblegröße

\[
H=\frac1n\partial_t\ln a
\]

und

\[
B^2=\beta_r^2=\left(\frac1c\partial_r\ln a\right)^2.
\]

Setze

\[
N=\ln a_{\rm obs}.
\]

Für exakt

\[
B^2(N)=B_\Lambda^2+B_m^2e^{-3N}
\]

gilt die fitfreie Differentialidentität

\[
\boxed{
\mathcal R_{\Lambda m}
=\frac{d^2B^2}{dN^2}+3\frac{dB^2}{dN}=0.
}
\]

Noch wichtiger: Die beiden Amplituden können nach einer Parent-Lösung direkt rekonstruiert werden,

\[
\boxed{
B_m^2=-\frac{e^{3N}}{3}\frac{dB^2}{dN}
}
\]

und

\[
\boxed{
B_\Lambda^2=B^2+\frac13\frac{dB^2}{dN}.
}
\]

Eine echte dynamische Selektion verlangt daher über ein nichttriviales Intervall gleichzeitig:

\[
\mathcal R_{\Lambda m}=0,
\qquad
\frac{dB_m^2}{dN}=0,
\qquad
\frac{dB_\Lambda^2}{dN}=0,
\qquad
B_m^2\ge0,
\qquad
B_\Lambda^2\ge0.
\]

Diese Größen dürfen **erst nach** Lösung der Parent-Gleichungen berechnet werden. Sie sind keine erlaubten frei einstellbaren Randdaten.

Für den zusätzlich quellfreien Zweig `T_tr=0`, `H != 0` muss außerdem

\[
\boxed{
\alpha_r\beta_r=-B^2-\frac12\frac{dB^2}{dN}
}
\]

gelten. Beim Lambda-plus-Dust-Profil ergibt dies automatisch

\[
\alpha_r\beta_r=-B_\Lambda^2+\frac12B_m^2a^{-3}.
\]

## 10. H4-Urteil

H4 schließt die Lücke aus H2 auf **formaler Parent-PDE-Ebene innerhalb des axisymmetrischen `F_tr=0`-Untersektors**:

\[
\boxed{
\text{time-radial bulk closure: PASS formal}
}
\]

\[
\boxed{
\text{equation/unknown count: square modulo gauge}
}
\]

\[
\boxed{
\text{local field-space principal rank capability: PASS}
}
\]

Aber die entscheidende physische Frage bleibt offen:

\[
\boxed{
\text{Erzeugt eine globale reguläre M1-Lösung tatsächlich }
B^2=B_\Lambda^2+B_m^2a^{-3}\ ?
}
\]

Dazu ist jetzt nicht sofort ein physischer Solver zulässig. Zuerst müssen Dimensionless-Form, Initial-/Randdaten, Constraint-Propagation, Kappen-Komplementierung, globale Fluxbedingungen und ein unabhängiger Boundary-Rank-Test geschlossen werden.

## 11. Gate-Stand

`K1-D = NOT_RELEASED`  
`K1-E = NOT_ADMISSIBLE`  
`WP4 = BLOCKED`  
`full ghost freedom = OPEN`  
`bounce = OPEN`  
`physical evidence = NONE`

**Nächster Block:** `C-PHYS-PARENT-H4R1-DIMENSIONLESS-IBVP-CONSTRAINT-PROPAGATION-AND-BOUNDARY-RANK-PREFLIGHT`.
