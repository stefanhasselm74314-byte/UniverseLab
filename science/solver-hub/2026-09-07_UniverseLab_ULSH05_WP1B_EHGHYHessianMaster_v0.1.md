# ULSH-05 / WP1B — Einstein-Hilbert + GHY Hessian Master v0.1

**Datum:** 2026-09-07  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `b6e90a46d17e96a5635c4a9c625964ea62ca7b16`  
**Status:** `DERIVED_VARIATIONAL_HESSIAN_MASTER_FIXED_INTERFACE_GN_BOUNDARY_CONTROL_FULL_COUPLED_SYSTEM_NOT_CLOSED`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Ziel und Abgrenzung

WP1A hat den Skalar-Maxwell-Sektor bei festem Hintergrund hergeleitet. WP1B nimmt nun den reinen Gravitationssektor

\[
S_g=\frac{M_6^4}{2}\int_{\mathcal M}d^6X\sqrt{-g}(R-2\Lambda_6)
+M_6^4\int_{\Sigma_5}d^5x\sqrt{-h}\,K
\]

für **eine** Bulkregion mit outward normal auseinander.

Die Parentwirkung enthält zwei Regionen; die Gesamtwirkung ist später die Summe der beiden regionalen Gravitationsblöcke plus Bulk-Skalar/Maxwell und Cap-Wirkung.

`[BEWIESEN/AUS QUELLE]` Die GHY-Normierung und outward-normal-Konvention sind im Parentkanon festgelegt. Die dortige Israel-Gleichung lautet

\[
M_6^4\sum_{s=\pm}(K_{ab}^{(s)}-K^{(s)}h_{ab})=S_{ab}.
\]

WP1B erzeugt **noch nicht** den vollständigen gekoppelten HZT-Hessian. Insbesondere bleiben Cap-Bending, Cap-Hessian, metrisch-materielle Mischungen, S/V/T-Gaugekontrolle und 6D→4D-Reduktion offen.

---

## 2. Erste Variation mit GHY

Definiere

\[
\mathcal E_{AB}\equiv G_{AB}+\Lambda_6 g_{AB},
\qquad
\Pi_{ab}\equiv K_{ab}-Kh_{ab}.
\]

Für eine feste, nicht-nullartige Grenzfläche ergibt EH+GHY die wohldefinierte erste Variation

\[
\boxed{
\frac{dS_g}{d\epsilon}
=\frac{M_6^4}{2}\left[
\int_{\mathcal M}\sqrt{-g}\,\mathcal E_{AB}\frac{dg^{AB}}{d\epsilon}
+\int_{\Sigma_5}\sqrt{-h}\,\Pi_{ab}\frac{dh^{ab}}{d\epsilon}
\right].
}
\]

Die GHY-Wirkung entfernt dabei die unkontrollierten Normalableitungen von \(\delta g\), die die reine Einstein-Hilbert-Variation am Rand erzeugen würde.

### 2.1 Vorzeichenkontrolle an der Kappe

Mit der projektinternen Definition des lokalisierten Stresstensors gilt

\[
\delta S_\Sigma
=-\frac12\int_{\Sigma_5}\sqrt{-h}\,S_{ab}\,\delta h^{ab}.
\]

Die Summe der beiden regionalen EH+GHY-Randvariationen ergibt daher stationär

\[
\frac12\int\sqrt{-h}
\left[M_6^4\sum_s\Pi_{ab}^{(s)}-S_{ab}\right]\delta h^{ab}=0,
\]

also exakt

\[
\boxed{M_6^4\sum_s\Pi_{ab}^{(s)}=S_{ab}.}
\]

`[BEWIESEN]` Die in WP1B verwendete erste Variationskonvention ist damit vorzeichenkompatibel mit der kanonischen Parent-Israel-Gleichung.

---

## 3. Metrischer Pfad

Um die zweite Variation eindeutig zu definieren, verwenden wir den linearen **kovarianten** Metrikpfad

\[
g_{AB}(\epsilon)=\bar g_{AB}+\epsilon p_{AB}.
\]

Für eine feste Einbettung der Grenzfläche ist

\[
h_{ab}(\epsilon)=\bar h_{ab}+\epsilon q_{ab},
\qquad
q_{ab}=e_a{}^Ae_b{}^Bp_{AB}.
\]

Mit

\[
p=\bar g^{AB}p_{AB},
\qquad
q=\bar h^{ab}q_{ab}
\]

gilt

\[
\left.\frac{dg^{AB}}{d\epsilon}\right|_0=-p^{AB},
\qquad
\left.\frac{d^2g^{AB}}{d\epsilon^2}\right|_0
=2p^A{}_Cp^{CB},
\]

\[
\left.\frac{dh^{ab}}{d\epsilon}\right|_0=-q^{ab},
\qquad
\left.\frac{d^2h^{ab}}{d\epsilon^2}\right|_0
=2q^a{}_cq^{cb},
\]

sowie

\[
\left.\frac{d\sqrt{-g}}{d\epsilon}\right|_0
=\frac12\sqrt{-\bar g}\,p,
\qquad
\left.\frac{d\sqrt{-h}}{d\epsilon}\right|_0
=\frac12\sqrt{-\bar h}\,q.
\]

---

## 4. Exakte off-shell Hessian-Masteridentität

Wie zuvor definieren wir

\[
S_g(\epsilon)=S_g^{(0)}+\epsilon\,\delta S_g
+\epsilon^2S_{g,\mathrm{quad}}^{(2)}+O(\epsilon^3),
\]

also

\[
S_{g,\mathrm{quad}}^{(2)}
=\frac12\left.\frac{d^2S_g}{d\epsilon^2}\right|_0.
\]

Differenziert man die erste Variationsidentität exakt entlang des oben definierten Pfads, folgt

\[
\boxed{
\begin{aligned}
S_{g,\mathrm{quad}}^{(2)}
=\frac{M_6^4}{4}\Bigg\{&
\int_{\mathcal M}\sqrt{-\bar g}\Big[
-p^{AB}\,\delta_p\mathcal E_{AB}
-\frac12p\,\bar{\mathcal E}_{AB}p^{AB}
+2\bar{\mathcal E}_{AB}p^A{}_Cp^{CB}
\Big]\\
&+\int_{\Sigma_5}\sqrt{-\bar h}\Big[
-q^{ab}\,\delta_p\Pi_{ab}
-\frac12q\,\bar\Pi_{ab}q^{ab}
+2\bar\Pi_{ab}q^a{}_cq^{cb}
\Big]\Bigg\}.
\end{aligned}
}
\]

`[BEWIESEN]` Dies ist die exakte zweite Pfadableitung der EH+GHY-Wirkung, geschrieben in Form des linearisierten Bulk-Einsteintensors und des linearisierten Brown-York-/GHY-Randimpulses.

### 4.1 Warum die off-shell-Terme nicht gestrichen werden dürfen

Die Terme

\[
\bar{\mathcal E}_{AB}p^A{}_Cp^{CB},
\qquad
p\,\bar{\mathcal E}_{AB}p^{AB},
\]

und ihre Randanaloga sind keine Artefakte. Sie entstehen aus inverser Metrik und Volumenelement entlang des kovarianten Metrikpfads.

Noch wichtiger: Selbst auf einem späteren **vollen Parent-on-shell-Hintergrund** ist im reinen Gravitationsblock im Allgemeinen

\[
\bar{\mathcal E}_{AB}=M_6^{-4}\bar T_{AB}^{(\phi,F)},
\]

also nicht null. Erst die Addition der metrischen Zweitvariationen des Skalar-/Maxwell-/Cap-Sektors kann die volle on-shell-Hessianstruktur korrekt reorganisieren.

Daher ist die Ersetzung

```text
Ebar_AB -> 0
```

für den aktuellen C-PHYS-M1-Gravitationsblock methodisch unzulässig.

---

## 5. Linearisiertes Bulk-Gravitationskernel

Für den kovarianten Perturbator \(p_{AB}\) gilt

\[
\boxed{
\delta_pR_{AB}
=\frac12\left(
\bar\nabla_C\bar\nabla_Ap^C{}_B
+\bar\nabla_C\bar\nabla_Bp^C{}_A
-\bar\Box p_{AB}
-\bar\nabla_A\bar\nabla_Bp
\right).
}
\]

Die skalare Variation ist

\[
\boxed{
\delta_pR
=\bar\nabla_A\bar\nabla_Bp^{AB}
-\bar\Box p
-\bar R_{AB}p^{AB}.
}
\]

Damit

\[
\boxed{
\delta_p\mathcal E_{AB}
=\delta_pR_{AB}
-\frac12\bar g_{AB}\delta_pR
-\frac12\bar R\,p_{AB}
+\Lambda_6p_{AB}.
}
\]

Die Reihenfolge der kovarianten Ableitungen ist Teil der Formel. Werden Ableitungen vertauscht, müssen die daraus folgenden Hintergrund-Krümmungsterme explizit mitgeführt werden.

---

## 6. Lokaler Fixed-Interface-Gaussian-Normal-Kontrollgauge

Der reale C-PHYS-Cap ist dynamisch; seine Bending-/Embedding-Variation ist noch nicht versioniert. Deshalb wird in WP1B **nur für die Randkernel-Kontrolle** eine lokale Gaugescheibe eingeführt:

- \(\Sigma_5\) bleibt koordinatenfest,
- im Rand-Nachbarschaftschart ist die Hintergrundmetrik gaussian-normal,
- zur ersten Ordnung gilt dort \(p_{nn}=p_{na}=0\),
- \(q_{ab}=p_{ab}|_\Sigma\).

Dann

\[
\bar K_{ab}=\frac12\partial_n\bar h_{ab}
\]

und exakt

\[
\boxed{\delta_pK_{ab}=\frac12\partial_n q_{ab}.}
\]

Wegen der ebenfalls variierten inversen induzierten Metrik gilt

\[
\boxed{
\delta_pK
=-\bar K^{ab}q_{ab}
+\frac12\bar h^{ab}\partial_nq_{ab}.
}
\]

Somit

\[
\boxed{
\begin{aligned}
\delta_p\Pi_{ab}
={}&\frac12\partial_nq_{ab}
-\bar h_{ab}\left(
-\bar K^{cd}q_{cd}
+\frac12\bar h^{cd}\partial_nq_{cd}
\right)
-\bar K q_{ab}.
\end{aligned}
}
\]

Eine äquivalente kovariante Schreibweise des ersten Ausdrucks ist

\[
\delta_pK_{ab}
=\frac12\bar\nabla_nq_{ab}
+\bar K_{(a}{}^cq_{b)c}.
\]

`[BEWIESEN/KONTROLLGAUGE]` Damit ist der lokale GHY-/Brown-York-Randkernel im Fixed-Interface-GN-Kontrollgauge explizit.

`[OFFEN]` Daraus folgt **nicht**, dass Cap-Bending global verschwindet oder physikalisch irrelevant ist. Die Äquivalenz zu einer vollständigen bewegten Grenzflächenbeschreibung ist ein eigener späterer Schritt.

---

## 7. Drei unabhängige Kontrolltests

### 7.1 D=6 konstante konforme Skalierung

Setze in einem konstant gekrümmten lokalen Bulk-Kontrollhintergrund

\[
p_{AB}=c\,\bar g_{AB},
\qquad
g_{AB}(\epsilon)=(1+\epsilon c)\bar g_{AB}.
\]

In sechs Dimensionen gilt direkt

\[
\sqrt{-g}(R-2\Lambda_6)
=\sqrt{-\bar g}\left[
(1+\epsilon c)^2\bar R
-2\Lambda_6(1+\epsilon c)^3
\right].
\]

Der direkte \(\epsilon^2\)-Koeffizient ist daher

\[
\frac{M_6^4}{2}(\bar R-6\Lambda_6)c^2.
\]

Aus der Hessian-Masteridentität folgt exakt derselbe Koeffizient. Dieser Test prüft insbesondere die Faktoren der beiden off-shell-\(\bar{\mathcal E}_{AB}\)-Terme.

### 7.2 Lokaler konformer Ricci-Test

In einem flachen lokalen Kontrollframe mit

\[
p_{AB}=2\sigma\eta_{AB}
\]

liefert das Bulk-Kernel in \(D\) Dimensionen

\[
\delta R_{AB}=-(D-2)\partial_A\partial_B\sigma
-\eta_{AB}\Box\sigma.
\]

Für \(D=6\):

\[
\boxed{
\delta R_{AB}=-4\partial_A\partial_B\sigma-\eta_{AB}\Box\sigma.
}
\]

### 7.3 Gaussian-Normal-Randmatrix-Test

In einem lokalen orthonormalen 5D-Randframe werden beliebige symmetrische Matrizen für

\[
\bar K_{ab},\quad q_{ab},\quad \partial_nq_{ab}
\]

verwendet. Die direkte Koordinatenvariation von \(K_{ab}=\tfrac12\partial_nh_{ab}\) stimmt algebraisch mit der kovarianten Form und der obigen \(\delta\Pi_{ab}\)-Formel überein.

---

## 8. Verhältnis zu vorhandener radialer Boundary-Theorie

Operator-2B und H4R4A besitzen bereits starke Resultate für **reduzierte** C-PHYS-Randmaps:

- kontinuierliche Cap-Traces,
- linearisierte Boundary-Map-Templates,
- einen nichtverschwindenden metrischen Normal-Hauptblock,
- in H4R4A einen exakten lokalen konformen Boundary-Jet-Generator.

Diese Resultate bleiben wertvoll, sind aber auf einen statischen radialen bzw. reduzierten 1+1-Chart beschränkt. Sie ersetzen nicht den hier begonnenen allgemeinen 6D-Metrikperturbationssektor \(p_{AB}(x^\mu,r,\chi)\).

---

## 9. Was WP1B schließt — und was nicht

Neu geschlossen:

```text
EH+GHY off-shell pathwise Hessian master identity      DERIVED
linearized bulk Einstein+Lambda kernel                 DERIVED
local fixed-interface GN boundary momentum kernel      DERIVED_CONTROL
Israel-sign compatibility                              DERIVED
```

Weiter offen:

```text
metric-scalar / metric-Maxwell Hessian mixing          NOT_DERIVED
cap localized-action Hessian                           NOT_DERIVED
cap bending / global fixed-interface gauge             MISSING_REQUIRED_LINK
full perturbed junction system                         NOT_DERIVED
SVT / diffeomorphism gauge invariants                  NOT_DERIVED
constraint elimination                                 NOT_DERIVED
PHYSICAL_BACKGROUND                                    NOT_ESTABLISHED
matter Delta_m coupling                                MISSING_REQUIRED_LINK
6D -> 4D perturbative reduction                        MISSING_REQUIRED_LINK
mu / eta / Sigma / growth / lensing                    UNRELEASED
ghost freedom / kinetic positivity / stability         OPEN
```

Damit bleibt

```text
ULSH05-WP1 = PREPARATORY_IN_PROGRESS_NOT_CLOSED
G01        = OPEN_BLOCKING
```

und alle physischen Gates bleiben unverändert.

---

## 10. Nächster analytischer Block

Der nächste notwendige Schritt ist

```text
ULSH05-WP1C — metric-scalar-Maxwell mixing + cap Hessian + perturbed-junction assembly
```

Erst WP1A + WP1B + WP1C können einen vollständigen off-shell Parent-Hessian ergeben. Die on-shell Reduktion bleibt darüber hinaus bis zu einem separat freigegebenen 6D-Hintergrund gesperrt.
