---
title: "UniverseLab | UL-GRQM-2T07"
subtitle: "Radiale Constraints, dynamische Kappe und magnetische Gauge-Patches"
author: "UniverseLab – wissenschaftlicher Forschungsentwurf"
date: "27. November 2026"
lang: de-DE
papersize: a4
geometry: margin=17mm
fontsize: 10pt
mainfont: "Caladea"
sansfont: "Carlito"
monofont: "DejaVu Sans Mono"
colorlinks: true
linkcolor: MidnightBlue
urlcolor: MidnightBlue
header-includes:
  - \usepackage{microtype}
  - \usepackage{booktabs}
  - \usepackage{fancyhdr}
  - \pagestyle{fancy}
  - \fancyhf{}
  - \fancyhead[L]{\small UniverseLab / GRQM / 2T-07}
  - \fancyhead[R]{\small DRAFT / NONCANONICAL}
  - \fancyfoot[C]{\thepage}
  - \setlength{\headheight}{14pt}
---

# 0. Identität, Gültigkeit und Kernaussage

**Kennung:** `UL-GRQM-2T07`; **Version:** `v0.1`; **Datum:** `2026-11-27`.

**Modell:** ausschließlich der dokumentierte *einzeitige* Kontrollzweig `HZT-M0-S6-C-PHYS-M1`, Signatur $(-,+,+,+,+,+)$; **kein** Nachweis für eine fundamentale 6D-2T-Theorie. **Architektur:** HPVS $\rightarrow$ HZT-M0 $\rightarrow$ HZT-Full.

**Status:** `DRAFT_ANALYTIC_ONLY / NONCANONICAL`; `PHYSICAL_EVIDENCE_EFFECT=NONE`; `PHYSICAL_GATE_EFFECT=NONE`; `SOLVER_AUTHORIZED=FALSE`; `K1-D=NOT_RELEASED`; `K1-E=NOT_ADMISSIBLE`.

**Kernresultat:** Die vollständige axialsymmetrische Kreisreduktion liefert zwei radial eichinvariante Feldstärken. Die radialen Komponenten $B_r,C_r$ führen im **eingeschränkten** Vektoraktionsfunktional zu longitudinalen Constraint-Gleichungen; ihre Eliminierung kann am glatten Pol wegen degenerierender kinetischer Gewichte nicht durch eine globale punktweise Matrixinverse erfolgen. Dynamische Kappenverschiebungen erzeugen die notwendigen Pullback-Kombinationen $\widehat{\delta a}$, $\widehat{\delta L}$, $\widehat{\delta\phi}$. Schließlich verändert ein magnetischer U(1)-Patchübergang die horizontalen Felder und die lokale Wicklungszahl gemeinsam. Der formale Nullvektor aus 2T-06 ist **patchkovariant**, aber noch **keine bewiesene physikalische Mode**.

**Nicht geleistet:** Keine vollständige zweite Variation der Einstein-Hilbert-plus-GHY-plus-Kappenwirkung; keine Lösung einer physikalischen 6D-Hintergrundkonfiguration; keine vollständige Einbeziehung von $g_{\mu r}$, radialem Lapse und Kappenbiegung; keine on-shell-S/V/T-Diagonalisierung; keine Bestätigung von Ghostfreiheit oder HZT-Observablen.

# 1. Geprüfte Quellen und kontrollierte Modellidentität

Direkt am öffentlichen `main` des Repositories `stefanhasselm74314-byte/UniverseLab` geprüft:

| Quelle | Git-Blob-SHA (Kurzform) | Aussage |
|:--|:--|:--|
| `SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md` | `df1b4a65d613` | 6D-Einzeit-Wirkung, Maxwell-, Israel- und Cap-Variation |
| `hzt-s6-parent-action-v0.1.json` | `aab94691b3a9` | Signatur, Felder, ausgeschlossene Sektoren |
| `registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json` | `13fbe0084dcf` | $Z_F(\phi)$, $Z_\sigma$, Ladungsgitter, Einheiten |
| `registry/2026-08-03_MD2S_R1_C_PHYS_GlobalConventionFreezeContract_v0.1.json` | im GitHub-Repository | Winkelperiode, $A_{\chi,N}-A_{\chi,S}=N_F/q_{\mathrm{ref}}$ |
| `registry/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.json` | `6d18236526a9` | Gravitations-Hessian und Cap-Bending noch nicht geschlossen |
| `science/grqm/2026-11-27_UniverseLab_2T06_CoupledVectorHessianBoundaryPreflight_v0.1_DRAFT.md` | Draft PR #310 | Eingeschränkte 2-Vektor-Hessian- und Robin-Form |

Die GitHub-Einträge aus dem Draft-PR #310 sind nicht mit kanonischen `main`-Quellen zu verwechseln. Das bisherige Modell mit zwei Zeiten (HZT-Full) wird nicht in den einzeitigen HZT-M0-Sektor hineingedeutet.

**Externe methodische Referenzen:** Peloso, Sorbo & Tasinato, *Phys. Rev. D* **73**, 104025 (2006), DOI [10.1103/PhysRevD.73.104025](https://doi.org/10.1103/PhysRevD.73.104025) – linearisiertes 6D-Flux-Branen-Modell; Bars & Chen, *Phys. Rev. D* **79**, 085021 (2009), DOI [10.1103/PhysRevD.79.085021](https://doi.org/10.1103/PhysRevD.79.085021) – 2T-Shadow, ein **anderer** Reduktionsmechanismus. Die nachfolgenden Identitäten sind eigenständig aus dem genannten HZT-M0-Ansatz abgeleitet und nicht als Literaturresultate für dieses Modell auszugeben.

# 2. Vollständige lokale Kreiszerlegung: ohne $C_r=B_r=0$

Im Bereich $L>0$ sei $a,b\in\{0,1,2,3,r\}$ und $\chi\sim\chi+2\pi$:

\[
 ds_6^2=h_{ab}dx^a dx^b+L^2(d\chi+C_a dx^a)^2,
 \qquad \mathcal A_6=B_a dx^a+a_\chi(d\chi+C_a dx^a).
\]

Zur Vermeidung einer Kollision mit dem Warp-Faktor heißt das interne Hintergrund-Gaugepotential $a_\chi=A_\chi$. Alle Felder sind in diesem Block unabhängig von $\chi$. Mit $G=dC$ gilt **exakt**:

\[
 \boxed{\mathcal F_6=H+da_\chi\wedge(d\chi+C),\quad H=dB+a_\chi G.}
\]

Das sechsdimensionale Maß, der Maxwell- und der Ricci-Skalar lassen sich lokal schreiben als

\[
 \sqrt{|g_6|}=L\sqrt{|h_5|},\quad
 \mathcal F_{MN}\mathcal F^{MN}=H_{ab}H^{ab}+\frac{2}{L^2}(\partial a_\chi)^2,
\]
\[
 R_6=R_5-\frac14L^2G_{ab}G^{ab}-2L^{-1}\Box_5L.
\]

Die letzte Identität gilt für die hier festgelegte Riemann-Konvention und eine raumartige $\chi$-Faser. Der $\Box_5L$-Term wird ausdrücklich **nicht gelöscht**, ehe GHY- und Interface-Beiträge behandelt sind.

Einsetzen in den Bulk der eingefrorenen Einstein-Maxwell-Skalar-Wirkung ergibt – vor jeder Randreduktion –

\[
\begin{aligned}
S_{\mathrm{bulk}}=2\pi\sum_s\int d^5x\sqrt{|h|}\bigg\{&
 \frac{M_6^4L}{2}(R_5-2\Lambda_6)
 -\frac{M_6^4L^3}{8}G_{ab}G^{ab}-M_6^4\Box_5 L\\
&-\frac{L Z_F}{4}H_{ab}H^{ab}
 -\frac{Z_F}{2L}(\partial a_\chi)^2
 -\frac L2(\partial\phi)^2-L U(\phi)
\bigg\}.
\end{aligned}
\]

**Einheitenaudit** mit $[\chi]=1$, $[d^5x]=M^{-5}$:
$[L]=M^{-1}$, $[a_\chi]=M$, $[q_\sigma]=M^{-1}$, $[a'_\chi]=M^2$, $[B_\mu]=M^2$, $[C_\mu]=M$, $[Z_\sigma]=M^3$. Jeder Bulk-Lagrangedichte-Summand hat Dimension $M^5$. Diese Koordinatendimension von $A_\chi$ ist von $[A_\mu]=M^2$ zu unterscheiden.

**Entscheidende Subtilität:** Die gewöhnlichen Koordinatenkomponenten erfüllen

\[
 \mathcal F_{r\mu}=H_{r\mu}+a'_\chi C_\mu
 \quad\text{(auf linearem Niveau bei }\bar C=0\text{)},
\]

während der *horizontale* Maxwell-Term nur $H$ enthält. Wer die zusätzliche $a'_\chi C_\mu$-Komponente unreflektiert quadriert und zugleich die vollständige inverse KK-Metrik verwendet, zählt denselben Mix zweimal und produziert einen **falschen** Bulk-Massenterm.

# 3. Radiale Gaugefelder und ihre projizierten Constraints

Definiere die beiden 5D-Feldstärken

\[
 E_{B\mu}=\partial_rB_\mu-\partial_\mu B_r,
 \qquad E_{C\mu}=\partial_rC_\mu-\partial_\mu C_r,
 \quad E_\mu=\binom{E_{B\mu}}{E_{C\mu}}.
\]

Bei 5D-U(1) und axialsymmetrischer Kreis-Diffeomorphie gelten lokal

\[
 \delta B_a=\partial_a\Lambda,\qquad
 \delta C_a=\partial_a\xi,
\]

weshalb $E_{B\mu}$ und $E_{C\mu}$ **exakt invariant** sind. Das sind zwei 5D-Gaugeverschiebungen; die radiale Gravitationsdiffeomorphie $r\mapsto r+\epsilon$ ist eine *dritte*, davon getrennte Symmetrie.

Im eingeschränkten transversalen Vector-Hessian (fixierte metrische Basis und Skalarprofile) gilt mit $Y_\mu=(B_\mu,C_\mu)^T$

\[
 S^{(2)}_{\rm radial,V}=-\frac12\int d^4x\sqrt{|g_4|}\sum_s\int dr_s\,
 E_\mu^T\mathbf P(r_s)E^\mu,
\]
\[
 \mathbf P=e^{2A}\mathbf K,\qquad
 \mathbf K=2\pi L
 \begin{pmatrix}
 Z_F& a_\chi Z_F\\
 a_\chi Z_F& a_\chi^2 Z_F+\tfrac12 M_6^4L^2
 \end{pmatrix}.
\]

Die Variation nach den *nicht festgehaltenen* $B_r,C_r$ liefert in diesem Teilfunktional die longitudinalen Bedingungen

\[
 \boxed{\nabla_\mu(\mathbf P E^\mu)=0.}
\]

Schreibt man $Y_\mu=Y_\mu^{\perp}+\nabla_\mu u$ mit $\nabla^\mu Y_\mu^{\perp}=0$ und $Y_r=(B_r,C_r)^T$, so ist

\[
 E_\mu=\partial_rY_\mu^{\perp}+\nabla_\mu(\partial_r u-Y_r).
\]

In der flachen Fourier-Betrachtung folgt schematisch $k^2\mathbf P(\partial_r u-Y_r)=0$. **Nur** für $k^2\ne0$, invertierbares $\mathbf P$ und ohne zusätzliche Skalar-/Gravitationsquellen ist die lokale Lösung $Y_r=\partial_r u$ ableitbar. Für $k^2=0$, die Pole $L=0$ sowie das vollständige System ist diese Inferenz unzulässig.

Die nicht eliminierte metrische Radialverschiebung $h_{\mu r}$ liefert außerdem die **Einstein-Momentum-Constraint**. In radialer Gauß-Codazzi-Schreibweise besitzt sie unter der verwendeten Extrinsikkrümmungs-Konvention die Struktur

\[
 \boxed{M_6^4D_b(K^b{}_a-\delta^b_aK)=T_{na}}
 \quad (a=\mu,\chi),
\]

wobei die volle 6D-Normale, der Maxwell-Fluxstress und die Kappenbedingungen einzusetzen sind. Diese Einstein-Constraints wurden **nicht** bis zu einer geschlossenen linearen Differentialoperator-Matrix durchgerechnet. Das Einsetzen von $h_{\mu r}=0$ vor ihrer Variation wäre ein Verlust von Bewegungsgleichungen.

# 4. Radiale Diffeomorphie: der fehlende Stueckelberg-Kanal

Für eine lokale radiale Koordinatenverschiebung $r\mapsto r+\epsilon(x,r)$ transformieren der Hintergrund-Gauge-Skalar und die zugehörige Störung zu erster Ordnung

\[
 \delta a_\chi\mapsto\delta a_\chi-a'_\chi\epsilon.
\]

Schreibt man die 5D-Basis *lokal* mit metrischer Radialverschiebung

\[
 ds_5^2=e^{2A}g_{\mu\nu}dx^\mu dx^\nu+(dr+v_\mu dx^\mu)^2,
\]

so gilt für $\epsilon$ unabhängig von $r$ in dieser Lapse-Eichung

\[
 v_\mu\mapsto v_\mu-\partial_\mu\epsilon.
\]

Die Kombination

\[
 \boxed{\mathscr D_\mu(\delta a_\chi)=\partial_\mu(\delta a_\chi)-a'_\chi v_\mu}
\]

ist damit invariant. Tatsächlich hat der Skalar-Gradient in diesem lokalen Ansatz die exakt quadratisch vervollständigte Form

\[
 h^{ab}\partial_a a_\chi\partial_b a_\chi=
 (\partial_r a_\chi)^2+e^{-2A}g^{\mu\nu}
 (\partial_\mu a_\chi-v_\mu\partial_r a_\chi)
 (\partial_\nu a_\chi-v_\nu\partial_r a_\chi).
\]

**Folge:** Bei magnetischem Hintergrund $a'_\chi\ne0$ darf die metrische Radialverschiebung $v_\mu$ nicht als physikalisch belanglos weggelassen werden. Sie steht bereits in der kovarianten Vollständigung des Scalar-Flux-Kanals. Bei allgemeiner $r$-abhängiger radialer Diffeomorphie ist zusätzlich der radiale Lapse mitzuführen; die hier gewählte Gauge $g_{rr}=1$ ist dann nicht erhalten.

# 5. Dynamische Kappe und eichinvariante Pullbacks

Für jede regionale Koordinatenkarte wird die Kappen-Einbettung als

\[
 r_s=\rho_s+\zeta_s(x)
\]

beschrieben. Unter radialer Diffeomorphie gilt $\zeta_s\mapsto\zeta_s+\epsilon_s(\rho_s,x)$, während die Euler-Störungen der Hintergrundprofile um $-f'_s\epsilon_s$ verschoben werden. Daher sind an der Kappe die Kombinationen

\[
 \boxed{\widehat{\delta a}_{\Sigma,s}=\delta a_s(\rho_s)+a_s'(\rho_s)\zeta_s,}\quad
 \boxed{\widehat{\delta L}_{\Sigma,s}=\delta L_s(\rho_s)+L'_s(\rho_s)\zeta_s,}
\]
\[
 \boxed{\widehat{\delta\phi}_{\Sigma,s}=\delta\phi_s(\rho_s)+\bar\phi'_s(\rho_s)\zeta_s.}
\]

Diese Größen sind kinematisch eichinvariant zu erster Ordnung. Für die induzierte vierdimensionale Kappenmetrik gilt ergänzend

\[
 \boxed{\delta h^{\Sigma}_{\mu\nu}=\delta g_{\mu\nu}(\rho)+\zeta\,\partial_r\bar g_{\mu\nu}(\rho)}
\]

bei $\bar g_{r\mu}=0$. Bei $\bar g_{\mu\nu}=e^{2A}\bar g_{4,\mu\nu}$ ist der Verschiebungsbeitrag $2A'e^{2A}\zeta\bar g_{4,\mu\nu}$.

Die inhomogene Wicklung $w=N_\sigma-q_\sigma a_\chi$ verändert sich auf der bewegten Kappe um

\[
 \boxed{\widehat{\delta w}_\Sigma=-q_\sigma(\delta a_\chi+a'_\chi\zeta)}.
\]

Das ist ein *notwendiger*, bisher im fixierten transversalen Teilproblem fehlender Kanal der vollständigen Kappenvariation.

## 5.1 Kappen-Flächenwirkung und lokale Verschiebung

Für einen statischen Hintergrund sei

\[
 T_\Sigma(r)=e^{4A}L\left[\lambda(\phi)+\frac{Z_\sigma(\phi)}{2L^2}w^2\right],
 \qquad w=N_\sigma-q_\sigma a_\chi.
\]

Der Beitrag der **Kappenwirkung allein** auf eine homogene infinitesimale Dislokation lautet

\[
 \delta_\zeta S_\Sigma=-2\pi\int d^4x\sqrt{|g_4|}\,T'_\Sigma(\rho)\zeta(x)
 \quad\text{(erster Ordnung, keine Gradienten)}.
\]

Für die eingefrorenen M1-Funktionen $\lambda=\mathrm{const}$ und $Z_\sigma=\mathrm{const}$ folgt exakt

\[
 \boxed{
 \frac{T'_\Sigma}{e^{4A}L}=
 (4A'+L'/L)\lambda+
 (4A'-L'/L)\frac{Z_\sigma w^2}{2L^2}
 -\frac{Z_\sigma q_\sigma w\,a'_\chi}{L^2}.}
\]

**Strikte Begrenzung:** $T'_\Sigma=0$ ist **keine** eigenständige Kappen-Gleichgewichtsbedingung. Die vollständige Verschiebung der beiden Bulkregionen, der GHY-Terme, der extrinsischen Krümmung und der lokalen Ströme muss berücksichtigt werden. Ein rein lokales Kraftminimum der Kappenwirkung ist nicht gleich der vollständigen Israel-Constraint.

## 5.2 Principal Part der gekrümmten Kappe

Für eine Grapheneinbettung in einem flachen Referenzraum gilt zu erster Ordnung $\delta K_{\mu\nu}=-\partial_\mu\partial_\nu\zeta$ (bei gewählter Normal- und Krümmungskonvention). In der gekrümmten 6D-Theorie kommen Warp-, Hintergrundkrümmungs-, Normierungs- und Gauge-Beiträge hinzu. Ihre vollständige, beidseitig orientierte linearisierte Israel-Gleichung wurde nicht geschlossen.

# 6. Globale magnetische Patches ändern die Form des Nullkandidaten

Der eingefrorene M0-Vertrag setzt den Übergang der zwei regulären Pol-Gauges fest:

\[
 \Lambda_{NS}(\chi)=c\chi,\quad c=\frac{N_F}{q_{\rm ref}},\quad
 a_{\chi,N}=a_{\chi,S}+c,
 \quad N_F\in\mathbb Z.
\]

Die volle 6D-Verbindung erfüllt $\mathcal A_N=\mathcal A_S+d\Lambda_{NS}=\mathcal A_S+c\,d\chi$.

Weil $\mathcal A=B+a_\chi(d\chi+C)$, folgt in derselben geometrischen Winkelkarte **zwingend**

\[
 \boxed{B_N=B_S-cC,\qquad C_N=C_S.}
\]

Für die geladene Kappenphase muss der Wicklungszahl-Vertreter gleichzeitig wechseln:

\[
 \boxed{N_{\sigma,N}=N_{\sigma,S}+q_\sigma c.}
\]

Da $q_\sigma=m_\sigma q_{\rm ref}$ gilt, ist $q_\sigma c=m_\sigma N_F\in\mathbb Z$. Damit bleiben die beiden physikalischen Kombinationen

\[
 \boxed{w=N_\sigma-q_\sigma a_\chi},\qquad
 \boxed{\Xi_\mu=\partial_\mu s-q_\sigma B_\mu-N_\sigma C_\mu}
\]

**über dem Patchübergang invariant**. Dies wurde symbolisch überprüft.

Die in 2T-06 hergeleitete Nullrichtung $Y_0\propto(N_\sigma,-q_\sigma)^T$ ist dabei lokal *kovariant*:

\[
 \binom{B_N}{C_N}=
 \begin{pmatrix}1&-c\\0&1\end{pmatrix}
 \binom{B_S}{C_S},\quad
 \binom{N_{\sigma,N}}{-q_\sigma}=
 \begin{pmatrix}1&-c\\0&1\end{pmatrix}
 \binom{N_{\sigma,S}}{-q_\sigma}.
\]

**Folge:** Der magnetische Patchübergang widerlegt den Nullvektor nicht. Er verbietet aber die unbegründete Annahme, derselbe numerische Komponentenvektor $(B,C)$ und dieselbe Wicklungszahl $N_\sigma$ gälten unverändert in allen Gaugekarten. Eine *globale* Mode erfordert zusätzlich korrekte Polregularität, funktionale Domäne, sämtliche Einstein-/Maxwell-Constraints und endliche Normierung.

# 7. Kreispole: der Schur-Komplement-Ansatz wird singulär

In 2T-06 wurde für den eingeschränkten Vektor-Hessian die positive quadratische Form

\[
 \mathbf K=2\pi L\begin{pmatrix}Z_F&Z_Fa_\chi\\Z_Fa_\chi&Z_Fa_\chi^2+\tfrac12 M_6^4L^2\end{pmatrix}
\]

abgeleitet. Ihre Determinante lautet

\[
 \boxed{\det\mathbf K=2\pi^2M_6^4Z_FL^4.}
\]

Für $L>0$, $Z_F>0$ und $M_6^4>0$ ist sie punktweise positiv definit. **Am glatten Pol** ist jedoch $L(0)=0$ und bei regulärer Winkelgeometrie $L(r)=r+O(r^3)$; zudem gilt im regulären Pol-Patch $a_\chi(r)=O(r^2)$.

Damit verhalten sich die Matrixeinträge für $r\to0$ qualitativ als

\[
 K_{BB}\sim r,\qquad K_{BC}\sim r^3,\qquad K_{CC}\sim r^3,
 \qquad \det\mathbf K\sim r^4.
\]

Ein typischer inverser Operator hätte $K^{-1}_{BB}\sim r^{-1}$ und $K^{-1}_{CC}\sim r^{-3}$. Die normale Punktmatrix ist also am Pol nicht invertierbar, obwohl die vollständige sechsdimensionale Geometrie dort regulär sein kann. Die Kreis-KK-Beschreibung ist an Fixpunkten der $U(1)$-Isometrie eine **singuläre Koordinatenreduktion**, kein automatisch physikalisch singulärer Bulk.

**Zwingender QA-Schritt:** Die radialen Constraints müssen im aus der quadratischen Wirkung hervorgehenden gewichteten Hilbertraum mit geometrischer Polregularität behandelt werden. Positivität im Inneren $r>0$ reicht für einen globalen Selbstadjungiertheits- oder Ghostfreiheitsbeweis nicht aus.

# 8. Was für die vollständige linearisierte 6D-Randdynamik fehlt

Aus der eingefrorenen Parentwirkung folgt beidseitig die Israel-Gleichung

\[
 M_6^4\sum_s(K^{(s)}_{ab}-K_s h_{ab})=S_{ab}.
\]

Ihre linearisierte Form besitzt schematisch die Struktur

\[
 M_6^4\sum_s\left[
 \delta K^{(s)}_{ab}-\bar h_{ab}\delta K_s-\bar K_s\delta h_{ab}
 \right]=\delta S_{ab},
\]

wobei die zweifache Variationsabhängigkeit von $\delta K_s$ (Inverse der induzierten Metrik und extrinsische Krümmung) zu berücksichtigen ist.

Vor einer physikalischen Schlussfolgerung sind mindestens erforderlich:

1. Vollständige zweite Variation von Einstein-Hilbert und GHY einschließlich $h_{r\mu}$ und radialem Lapse, nicht nur der Kreis-Vector-Kinetik.
2. Maxwell- und Skalar-Hessian mit $\bar F_{r\chi}$-Mischungen sowie die vollständigen Gauss- und Einstein-Momentum-Constraints.
3. Bewegte Kappe mit $\zeta_s$, induzierter Metrik, normalisierter Normalenvariation, extrinsischer Krümmung und Stueckelberg-Phase.
4. Zwei-Patch-Kontinuität und Ladungsgitter einschließlich der korrekten Übergangsmatrix $B_N=B_S-cC$.
5. Glatte Pole und selbstadjungierte gewogene Operator-Domäne.
6. Ein tatsächlich freigegebener on-shell 6D-Hintergrund; erst dann kann ein physikalisches quadratisches Störungsspektrum beansprucht werden.
7. Optional erst danach: definierte 4D-Materiequellen und Source-to-Observable-Map für $\mu,\Sigma,\eta$ und verwandte Größen.

Diese Liste ist kein Ersatz für die Rechnung. Das vorhandene `ULSH05_WP1_QuadraticActionReadiness` hält ausdrücklich fest, dass die vollständige zweite Variation, Cap-Bending und Materieeinbettung noch offen sind.

# 9. Symbolische Tests: exakte Reichweite

Die mitgelieferte Python-Datei enthält **33 bestandene** lokale Prüfungen mit SymPy für die KK-Metrikinverse, horizontale Feldstärke, radialen Gauge-Constraint-Kanal, Stückelberg-/Diffeomorphie-Kombinationen, bewegte Kappen-Pullbacks, Winding-Kraftterm, magnetische Patchübergänge und near-pole-Schur-Degenerationsordnung und eine vollständige Christoffel/Ricci-Kontrollrechnung für eine verdrillte 3D-Kreismetrik. Die Tests verifizieren die ausdrücklich programmierten Identitäten; sie sind **keine** zweite unabhängige Feldtheorie und keine phänomenologische Validierung.

| Statusklasse | Urteil |
|:--|:--|
| Kreis-Feldstärke/Volumenmaß, Ward-Kombinationen | **[BEWIESEN – kinematisch]** |
| Radiale $B_r,C_r$-Constraint im eingeschränkten Hessian | **[BEWIESEN – Teilsektor]** |
| Kappen-Pullbacks und magnetische Patch-Kovarianz | **[BEWIESEN – linear bzw. lokal]** |
| Polkriterium $\det K\to0$ | **[BEWIESEN]** |
| Vollständiger linearer Einstein-Maxwell-GHY-Cap-Hessian | **[OFFEN]** |
| On-shell-M0-Hintergrund und globale Nullmode | **[OFFEN]** |
| Ghostfreiheit der gesamten Theorie | **[OFFEN]** |
| Physikalische 2T-/HZT-Identifikation und Empirie | **[OFFEN]** |

**Keine Änderung der Autorität:** `PHYSICAL_GATE_EFFECT=NONE`, `EVIDENCE_EFFECT=NONE`, `AuthorizationDecision=NOT_CREATED`, `SingleUseGrant=NOT_CREATED`, `K1-D=NOT_RELEASED`, `K1-E=NOT_ADMISSIBLE`.

# 10. Streng begrenzter Folgeauftrag: 2T-08

**UL-GRQM-2T08 – Erste Constraint-geschlossene Linearisierung des radialen 6D-Einstein-Maxwell-Skalar-Systems einschließlich Kappen-Bending.**

Priorität ist **nicht** die Berechnung eines vermeintlichen Photon- oder Graviphoton-Massenwerts, sondern das Schließen von $\delta G_{r\mu}$ und $\delta G_{rr}$, der Maxwell-Gauss-Bedingung und der beidseitig orientierten pertubierten Kappen-Constraints auf einer spezifizierten Hintergrund-/Funktionsraumklasse. Falls ein on-shell Hintergrund nicht vorliegt, ist nur eine konsequent off-shell strukturierte Hessian-Rechnung mit expliziter Nicht-Freigabe zulässig.

Erst danach kann die Nullrichtung aus 2T-06/07 auf *physikalische* Existenz, Norm, Stabilität, globale Patchverträglichkeit und Materiekopplung getestet werden.

**Schlussfolgerung:** `ANALYTIC_PARTIAL_PASS / GLOBAL_CONSTRAINT_AND_PHYSICAL_MODE_OPEN / NO_RELEASE`.

# 11. Grenzfälle, Alternativerklärungen und Falsifikationsbedingungen

**Regulärer Pol ($r\to0$):** $L\sim r$, $a_\chi\sim r^2$ und $\det K\sim r^4$. Eine Divergenz der *inversen Kreiskomponentenmatrix* ist keine Krümmungssingularität. Zu prüfen sind die **sechsdimensional glatt fortsetzbaren** Tensor-/Vektorprofile und ihre positiven gewichteten Normen. Das Invertieren vor der Polanalyse ist ein Verfahrensfehler.

**Entladene Kappenphase ($q_\sigma\to0$):** Der Kappen-Massenterm bleibt bei $N_\sigma\ne0$ proportional zu $N_\sigma^2C_\mu C^\mu$. Ein verbleibender Maxwell-Nullkandidat ist eine andere Aussage als zwei masselose Vektoren. Umgekehrt bei $N_{\sigma,S}=0$ und $q_\sigma\ne0$ muss die Patchformel $N_{\sigma,N}=q_\sigma c$ mitgeführt werden.

**Verschwindender magnetischer Flux:** Aus $N_F=0$ folgt $c=0$ und damit eine triviale *Patchübergangsmatrix*. Daraus folgt nicht ohne zusätzliche Feldgleichungen, dass $a'_\chi(r)$ punktweise verschwindet. Die radiale Verschiebungskopplung bleibt separat zu prüfen.

**Schwache Kappenbewegung:** $\zeta\to0$ reproduziert die feste Kappe; dies ist ein kontrollierter Trunkierungslimes, aber noch kein Nachweis ihrer Konsistenz unter Störungen. Die Differenzen $\delta a_\chi$ und $\widehat{\delta a}_\Sigma$ verschwinden nur bei $a'_\chi\zeta=0$.

**Null-Impulsgrenze ($k^2\to0$):** Der Schluss $Y_r=\partial_r u$ aus $k^2\mathbf P(\partial_r u-Y_r)=0$ scheitert selbst für invertierbares $\mathbf P$. Eigenständige Massless-Mode-Gaugefixierung und globale Randbedingungen sind nötig.

**Falsifikation bzw. Abbruch eines konkreten Reduktionskandidaten:** Ein Kandidat ist für die beanspruchte Domäne zurückzuweisen, wenn er (i) eine Gauge-Patch-Relation verletzt, (ii) an einem glatten Pol keinen regulären 6D-Tensor liefert, (iii) die vollständigen radialen Einstein-/Gauss-Constraints verletzt oder (iv) nach tatsächlich durchgeführter Zwangselimination einen negativen Eigenwert der physikalischen kinetischen Form besitzt. Keines dieser Kriterien wurde für einen vollständigen HZT-M0-Kandidaten hier geprüft.

**Beobachtbarkeit:** Ohne freigegebene Materie-Wirkung und modenkonsistente Quellenkopplung gibt es keine seriöse Zuordnung zu einem Photon, zu $\mu(k,z)$, $\Sigma(k,z)$, Gravitationslinsen oder Kosmologie. Ein reines Gauge-/Koordinatenartefakt darf nicht als neue beobachtbare Teilchenart ausgegeben werden.