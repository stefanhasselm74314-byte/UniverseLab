---
title: "UniverseLab | UL-GRQM-2T05"
subtitle: "Gekoppelter Maxwell-Graviphoton-Kappensektor: Eichstruktur, Randform und Grenzen der Modenaussage"
author: "UniverseLab – analytisches Forschungsprotokoll"
date: "27. November 2026"
lang: de-DE
papersize: a4
geometry: "top=21mm,bottom=21mm,left=21mm,right=21mm"
fontsize: 10pt
mainfont: "DejaVu Serif"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
colorlinks: true
urlcolor: MidnightBlue
header-includes:
  - \usepackage{microtype}
  - \usepackage{booktabs}
  - \usepackage{longtable}
  - \usepackage{fancyhdr}
  - \pagestyle{fancy}
  - \fancyhf{}
  - \fancyhead[L]{\small UniverseLab – GRQM / 2T-05}
  - \fancyhead[R]{\small DRAFT / NONCANONICAL}
  - \fancyfoot[C]{\thepage}
  - \setlength{\headheight}{14pt}
---

# 0. Kurzbefund und Governance

**ID:** `UL-GRQM-2T05`; **Version:** `v0.1`; **Erstellung:** `2026-11-27`; **Theoriepfad:** HPVS $\rightarrow$ HZT-M0 $\rightarrow$ HZT-Full.

**Status:** `DRAFT_ANALYTIC_ONLY / NONCANONICAL`. **Physical evidence effect:** `NONE`; **Physical gate effect:** `NONE`; **K1-D:** `NOT_RELEASED`; **K1-E:** `NOT_ADMISSIBLE`; **Solver authorization:** `FALSE`.

**Kernbefund:** Im einzeitigen Modell `HZT-M0-S6-C-PHYS-M1` koppelt die **bereits dokumentierte** Kappenphase nicht nur an den 4D-Maxwell-Anteil $A_\mu$, sondern wegen des nichtverschwindenden Winklungsgradienten auch an den metrischen 4D-Vektor $g_{\mu\chi}$. Ihre quadratische Transversalform ist eine **positive semidefinite Matrix vom Rang eins**, nicht die isolierte Vektormasse von 2T-04. Eine nicht vom Kappen-Massenterm erfasste Kombination ist dadurch algebraisch ausgewiesen; ob sie propagiert, normalisierbar oder masselos bleibt, ist **nicht** gezeigt.

**Wichtige Grenze:** Eine vollständige zweite Variation von Einstein-Hilbert, GHY, Skalar-, Maxwell- und Kappenwirkung am On-shell-Hintergrund, einschließlich $g_{\mu r}$, $g_{r\chi}$, radialer Gauge-Komponenten und Embedding, ist nicht verfügbar. Daher ist dieser Bericht **kein** vollständiger gekoppelter Vektoroperator, Ghosttest oder Observable-Forward-Map.

# 1. Gelesene Quellen und Modellidentität

Die folgenden Quellen wurden auf dem öffentlichen Repository `stefanhasselm74314-byte/UniverseLab` direkt eingesehen (für jede angegebene Datei wurde der Blob-SHA geprüft):

| Quelle | Blob-SHA (Beginn) | Relevante Festlegung |
|:--|:--|:--|
| `SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md` | `df1b4a65d613` | Einzeit-Signatur, 6D-Wirkung und Kappenphase |
| `hzt-s6-parent-action-v0.1.json` | `aab94691b3a9` | Parentmodell und offene Gates |
| `registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json` | `13fbe0084dcf` | $Z_F>0$, $Z_\sigma>0$, $q_\sigma$ |
| `registry/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.json` | `6d18236526a9` | Vollständiger Hessian und Embedding **nicht hergeleitet** |
| `science/hzt-m0/md2s/2026-08-03_MD2S_BulkLocalizedActionAndJunctionLedger_v0.1.md` | `7bf51f38eae3` | Orientierte Junctions und Winding |
| `science/hzt-m0/bridge/MD2I_MDS05_WARP_VOLUME_BRIDGE_DERIVATION_v0.1.md` | `82a0587a8eb4` | Konditionale 4D-Einstein-Normierung |
| `science/grqm/2026-11-27_UniverseLab_2T04_4DModeCapGaugeAudit_v0.1_DRAFT.md`, PR #308 | `research/...` | **Isolierter** Maxwell-Kappen-Sektor, nicht kanonisch |

Primärliteratur zur Einordnung: Giovannini (2002), *Gauge field localization on Abelian vortices in six dimensions*, [arXiv:hep-th/0205139](https://arxiv.org/abs/hep-th/0205139); Peloso, Sorbo und Tasinato (2006), *Standard 4D gravity on a brane in six-dimensional flux compactifications*, [arXiv:hep-th/0603026](https://arxiv.org/abs/hep-th/0603026); Parameswaran, Randjbar-Daemi und Salvio (2009), *General Perturbations for Braneworld Compactifications and the Six Dimensional Case*, [arXiv:0902.0375](https://arxiv.org/abs/0902.0375). Diese Arbeiten zeigen verwandte gekoppelte S/V/T-Probleme, **identifizieren aber nicht automatisch unser M0-Modell**.

# 2. Postulate und zulässiger Teilsektor

Der dokumentierte HZT-M0-Kern lautet in jeder glatten Region $s=N,S$:

$$
S_{\rm bulk}=\sum_s\int_{\mathcal M_s} d^6X\sqrt{|g_6|}\left[\frac{M_6^4}{2}(R_6-2\Lambda_6)-\frac12(\nabla\phi)^2-U(\phi)-\frac14 Z_F(\phi)F_{MN}F^{MN}\right]
$$

zusammen mit den GHY-Termen und einer **einmal gezählten** lokalisierten Kappenwirkung

$$
S_\Sigma=-\int_{\Sigma_5} d^5x\sqrt{|h|}\left[\lambda(\phi)+\frac12 Z_\sigma(\phi)h^{ab}D_a\sigma D_b\sigma\right],\qquad D_a\sigma=\partial_a\sigma-q_\sigma A_a.
$$

Die Signatur ist $(-,+,+,+,+,+)$, also (5,1), **nicht** die hypothetische 2T-Signatur (4,2). $\chi$ ist eine dimensionslose Winkelkoordinate mit Periode $2\pi$. Die Bulk-Backgroundfelder $A_s(r),L_s(r),\bar\phi_s(r),\bar A_{\chi,s}(r)$ bleiben als Funktionen **symbolisch**. Ein physikalisch freigegebener On-shell-Hintergrund wird nicht vorausgesetzt.

**Symmetriebeschränkung:** Wir behandeln $\chi$-unabhängige ($\ell=0$) infinitesimale Vektoren und die lineare Kappenphase. Eine spätere $\ell\ne0$-Analyse benötigt das gesamte Winkelmodenspektrum. Ein 4D-maximal symmetrischer Hintergrund ermöglicht die übliche Trennung nach 4D-Spin; eine ungeprüfte vollständige Trunkierung wird nicht beansprucht.

# 3. Geometrische Kaluza-Zerlegung

Wir lassen auf der Kappe den metrischen Vektor ausdrücklich zu:

$$
\boxed{\quad ds_{\Sigma}^2=e^{2A_\Sigma}g_{\mu\nu}^{(4)}dx^\mu dx^\nu+L_\Sigma^2\bigl(d\chi+C_\mu dx^\mu\bigr)^2.\quad}
$$

In linearer Ordnung ist $\delta g_{\mu\chi}=L_\Sigma^2 C_\mu$. Das exakte blockweise Inverse lautet (Indexhebung mit $g_4$)

$$
 h^{\mu\nu}=e^{-2A_\Sigma}g_4^{\mu\nu},\qquad
 h^{\mu\chi}=-e^{-2A_\Sigma}C^\mu,\qquad
 h^{\chi\chi}=L_\Sigma^{-2}+e^{-2A_\Sigma}C_\mu C^\mu.
$$

Die Determinante hängt nicht von $C_\mu$ ab:

$$
\boxed{\sqrt{|h|}=e^{4A_\Sigma}L_\Sigma\sqrt{|g_4|}.}
$$

Die mathematische Identität für jeden Kovektor $D_a\sigma$ ist damit **exakt**:

$$
\boxed{
 h^{ab}D_a\sigma D_b\sigma
=e^{-2A_\Sigma}g_4^{\mu\nu}\bigl(D_\mu\sigma-C_\mu D_\chi\sigma\bigr)
\bigl(D_\nu\sigma-C_\nu D_\chi\sigma\bigr)+\frac{(D_\chi\sigma)^2}{L_\Sigma^2}.
}
$$

# 4. Zwei lokale Eichsymmetrien und die physikalische Kappenkombination

Setze in einer regulären lokalen Gauge-Patch

$$
\bar A_\chi=a_\Sigma,\qquad \sigma=N_\sigma\chi+s(x),\qquad
 w_\Sigma=N_\sigma-q_\sigma a_\Sigma.
$$

Der vierdimensionale **horizontale Maxwell-Vektor** ist

$$
B_\mu\equiv A_\mu-a_\Sigma C_\mu.
$$

Aus $D_\mu\sigma-C_\mu D_\chi\sigma$ folgt die Kappenkombination

$$
\boxed{\quad\Xi_\mu=\partial_\mu s-q_\sigma B_\mu-N_\sigma C_\mu
=\partial_\mu s-q_\sigma A_\mu-w_\Sigma C_\mu.\quad}
$$

**Konvention:** Für die aktive infinitesimale Winkelverschiebung $\delta_\xi$ und die U(1)-Transformation $\delta_\alpha$ wählen wir

$$
\delta_\xi C_\mu=\partial_\mu\xi,\quad
\delta_\xi A_\mu=a_\Sigma\partial_\mu\xi,\quad
\delta_\xi s=N_\sigma\xi;
\qquad
\delta_\alpha A_\mu=\partial_\mu\alpha,\quad
\delta_\alpha s=q_\sigma\alpha.
$$

Direktes Einsetzen liefert

$$
\boxed{\delta_\xi\Xi_\mu=\delta_\alpha\Xi_\mu=0.}
$$

**Status: [BEWIESEN, lokale kinematische Identität].** Eine dynamische Eichreduktion mit vollständigen Constraints ist damit noch nicht erbracht. Insbesondere ist die allgemeine Winkelverschiebung $\xi(x,r)$ nicht durch $C_\mu$ allein darstellbar: sie erzeugt zusätzlich $C_r$ und $A_r$, was in einem vollständigen Bulk-Hessian berücksichtigt werden muss.

# 5. Exakte quadratische Kappenform und Rangtest

Mit der obigen Blockidentität ist der transversale quadratische $4D$-Anteil der Kappenwirkung

$$
\boxed{
S_{\Sigma,V}^{(2)}=-\frac{\mathcal C_\Sigma}{2}\int d^4x\sqrt{|g_4|}\,g_4^{\mu\nu}\Xi_\mu\Xi_\nu,
\qquad \mathcal C_\Sigma=2\pi e^{2A_\Sigma}L_\Sigma Z_\sigma>0.
}
$$

Die gleichzeitige Variation der Winkelkomponente $A_\chi$, der Kappenlage und der anderen Felder ist **hier nicht geschlossen**; der angezeigte reine Vektorterm folgt bei festem Hintergrund und aktivem $Z_\sigma$. In transversaler 4D-Zerlegung wird $\partial_\mu s$ longitudinal. Daher ergibt sich **nur für die transversalen Maxwell-/metrischen Vektoren** der Kappenmassenterm

$$
\begin{aligned}
\mathcal L_{\Sigma,\mathrm{mass}}
&=-\frac{\mathcal C_\Sigma}{2}\left(q_\sigma B_\mu+N_\sigma C_\mu\right)^2\\
&=-\frac12
\begin{pmatrix}B_\mu & C_\mu\end{pmatrix}
\underbrace{\mathcal C_\Sigma\begin{pmatrix}q_\sigma^2 & q_\sigma N_\sigma\\q_\sigma N_\sigma & N_\sigma^2\end{pmatrix}}_{\mathbf M_{\Sigma}^2}
\begin{pmatrix}B^\mu\\ C^\mu\end{pmatrix}.
\end{aligned}
$$

Für $q_\sigma\ne0$, $\mathcal C_\Sigma>0$ gilt exakt

$$
\boxed{\operatorname{rank}\mathbf M_\Sigma^2=1,\qquad \det\mathbf M_\Sigma^2=0,\qquad \mathbf M_\Sigma^2\begin{pmatrix}N_\sigma\\-q_\sigma\end{pmatrix}=0.}
$$

In der ursprünglichen $A_\mu,C_\mu$-Basis wird $(q_\sigma,N_\sigma)$ durch $(q_\sigma,w_\Sigma)$ ersetzt. Die Kappenform ist positiv semidefinit, soweit $Z_\sigma>0$ und die normierten 4D-Vektoren ein positives kinetisches inneres Produkt besitzen. **Das ist noch keine positive physikalische Kinetik aller Sektoren.**

## 5.1 Warum die Nullrichtung nicht als physikalisches Photon bezeichnet werden darf

Sei $\mathbf K$ eine angenommene positiv definite kinetische 2x2-Matrix in einem endlichen 4D-Trunkierungsmodell und $\mathbf M_{\rm cap}^2=\mathcal C_\Sigma \mathbf v\mathbf v^T$ mit $\mathbf v^T=(q_\sigma,N_\sigma)$. Für $\mathbf K=\operatorname{diag}(K_B,K_C)$ ergibt die verallgemeinerte Eigenwertgleichung

$$
\det(\mathbf M_{\rm cap}^2-m^2\mathbf K)=0
\quad\Longrightarrow\quad
\boxed{m^2=0\quad\text{oder}\quad m^2=\mathcal C_\Sigma\left(\frac{q_\sigma^2}{K_B}+\frac{N_\sigma^2}{K_C}\right).}
$$

Dieses Ergebnis gilt **nur für dieses Toy-Trunkierungsmodell**. Ein Bulk-Massen-/Mischungsterm, kinetisch nicht normierbare Profile, die globalen Patchbedingungen oder weitere Constraints können die Nullrichtung entfernen. Beispielsweise macht die Zugabe der positiven Matrix $\operatorname{diag}(m_B^2,m_C^2)$ die volle 2x2-Massenmatrix im Allgemeinen positiv definit.

Daher gilt streng:

$$
\boxed{\text{Kappen-Massmatrix mit Rang eins}\ \not\Rightarrow\ \text{masseloser physikalischer 4D-Vektor}.}
$$

## 5.2 Direkter Bezug zu 2T-04

Setzt man künstlich $C_\mu=0$, so folgt $\Xi_\mu=\partial_\mu s-q_\sigma A_\mu$, genau der **isolierte Maxwell-Kappen-Sektor** aus 2T-04. Dessen Robin-Massenanhebung war unter seiner festen-Metrik-Annahme mathematisch korrekt. Ohne die Annahme $C_\mu=0$ ist der Schluss auf die gesamte Vektorbasis **nicht zulässig**.

# 6. Magnetischer Hintergrund: notwendige Bulk-Mischung

Zur Behandlung der axialen Richtung als 1-Form verwenden wir auf der fünfdimensionalen Basis $y^a=(x^\mu,r)$

$$
\theta=d\chi+C_a(y)dy^a,\qquad
A_6=B_a(y)dy^a+a(y)\theta,\qquad a=A_\chi.
$$

Die Exterior-Ableitung ist exakt

$$
\boxed{\quad F_6=dB+da\wedge\theta+a\,dC.\quad}
$$

Dabei sind die horizontalen Komponenten $F^{\mathrm{hor}}_{ab}=(dB+a\,dC)_{ab}$ sowie $F_{a\chi}=\partial_a a$. Für $a=a(r)$ und beispielsweise $C_r=0$ gilt insbesondere

$$
F_{r\mu}^{\mathrm{hor}}=\partial_rB_\mu-\partial_\mu B_r+a(r)(\partial_rC_\mu-\partial_\mu C_r).
$$

In Koordinatenkomponenten tritt zusätzlich $a'(r)C_\mu$ auf, was den Hintergrundflux $F_{r\chi}=a'$ widerspiegelt. Diese Terme sind nicht durch eine isolierte Maxwell-Mode ersetzbar; ebenso entstehen im Einstein-Hilbert-Hessian $C$-Kinetik und Vektorconstraints.

Die **vollständige** gekoppelte quadratische Wirkung $S^{(2)}[B_\mu,C_\mu,g_{\mu r},g_{r\chi},A_r,\delta\sigma,\ldots]$ wurde hier nicht ausgerechnet. Daher werden weder ein vollständiger radialer 2x2-Operator noch gekoppelte physikalische Eigenmassen behauptet.

# 7. Große Eichtransformationen, Flux-Patches und globale Konsistenz

In einer Überlappung zweier regulärer U(1)-Patches ist eine große Eichtransformation $\alpha=\kappa\chi$ möglich, falls $q_{\rm ref}\kappa\in\mathbb Z$ mit korrekt fixiertem Ladungsgitter. Sie verschiebt

$$
a\mapsto a+\kappa,\qquad N_\sigma\mapsto N_\sigma+q_\sigma\kappa,\qquad
B_\mu\mapsto B_\mu-\kappa C_\mu.
$$

Somit bleiben exakt

$$
\boxed{w_\Sigma=N_\sigma-q_\sigma a,\qquad q_\sigma B_\mu+N_\sigma C_\mu,\qquad F^{\rm hor}=dB+a\,dC}
$$

patch-invariant. Einzelne Werte von $a$, $N_\sigma$ und $B$ können patchabhängig sein. **Ein angeblicher globaler Photon-/Graviphotonmodus muss unter diesen Übergangsfunktionen konsistent zusammengefügt werden.**

# 8. Dimensionen, Grenzfälle und Gegenbeispiele

Es gilt im M0-Freeze $[\chi]=[\sigma]=1$, $[A_\mu]=M^2$, $[C_\mu]=M$, $[q_\sigma]=M^{-1}$, $[Z_\sigma]=M^3$, $[L]=M^{-1}$, $[\Xi_\mu]=M$ und $[\mathcal C_\Sigma]=M^2$. Das Wirkungsintegral aus Abschnitt 5 ist damit dimensionslos.

- **$Z_\sigma\to0$:** der Kappen-Massenterm verschwindet. Dies ist die Randgrenze des aktiven Winding-Sektors, keine zulässige stille Parameterverschiebung innerhalb eines eingefrorenen M1-Modellpunkts.
- **$q_\sigma\to0$:** die Maxwell-Kopplung entfällt; je nach $N_\sigma$ kann die Kappe weiterhin den Winkel-Graviphoton-Vektor koppeln. Dies liegt außerhalb der aktiven M1-Ladungsklasse.
- **$N_\sigma=0$:** in der horizontalen $(B,C)$-Basis erfasst die Kappenform nur $B$; das gilt **nicht** als Beweis einer masselosen $C$-Mode.
- **$w_\Sigma=0$:** in der Koordinatenbasis $(A,C)$ ist die Kappenform scheinbar reine Maxwell-Masse, während $A=B+aC$ weiterhin die metrische Feldmischung enthält. Die Basiswahl ist physikalisch nicht neutral gegenüber allen Bulk-Terms.
- **$\mathcal C_\Sigma\to\infty$:** die Kappe unterdrückt formal die Linearkombination $qB+NC$; die übrige Nullrichtung kann weiterhin Bulk-/Rand-Energie tragen. Ein vollständiger Dirichlet-Grenzfall muss operatorseitig gezeigt werden.
- **IR ($k\to0$):** ohne berechnete Eigenwerte und Quellenresiduen keine Aussage über langreichweitige Vektorkräfte.
- **UV ($k\to\infty$):** lokale Quadratik kontrolliert nicht die gesamte 6D-Higher-derivative-/KK-Probe; die Vollständigkeit des Eigenfunktionssystems bleibt zu prüfen.

**Gegenbeispiel zur vorschnellen Nullmodenidentifikation:** Im algebraischen Zweivektormodell besitzt $\mathcal C_\Sigma\mathbf v\mathbf v^T$ eine Nullrichtung. Addiert man eine positive Bulk-Quadratik $\operatorname{diag}(m_B^2,m_C^2)$, verschwindet diese Nullrichtung aus dem 4D-Massenspektrum. Die Kappen-Ranginformation reicht für die Gesamtmasse daher nicht aus.

# 9. Beweispflichten für eine echte HZT-M0-Mode

| Gate | Benötigtes Resultat | Status 2T-05 |
|:--|:--|:--|
| V05-KIN | Kaluza-Geometrie, Doppel-Eichstruktur, $\Xi_\mu$ | **PASS**, lokal |
| V05-CAP | Kappen-Vektorquadratik, Vorzeichen und Rang | **PASS**, eingeschränkter off-shell-Sektor |
| V05-PATCH | Kompatibilität großer Eichtransformationen | **PASS**, algebraische Übergangsidentitäten |
| V05-HESS | Vollständiger Bulk-EH+GHY/Maxwell/Skalar-Hessian | **OPEN** |
| V05-CONSTR | Variationsgleichungen für $A_r$, $g_{\mu r}$, $g_{r\chi}$ und Cap | **OPEN** |
| V05-ON | On-shell-6D-Hintergrund mit Junctions und Flux | **NOT ESTABLISHED** |
| V05-EIG | Selbstadjungierter gekoppelter Operator und Moden-Norm | **OPEN** |
| V05-GHOST | Positivität der *physikalischen* Kinetik nach Constraintabbau | **OPEN** |
| V05-MAT | Gewöhnliche Materiewirkung, Ladungen und 4D-Source-Map | **MISSING REQUIRED LINK** |
| V05-OBS | $\mu,\Sigma,\eta,E_G,f\sigma_8$, GW-Kopplungen | **NOT RELEASED** |
| K1-D / K1-E | Projektfreigabe | **NOT RELEASED / NOT ADMISSIBLE** |

Die lokale Eichalgebra liefert notwendige kinematische Bedingungen, aber keine geschlossene physikalische Lösung. Ein positiver Kappen-Hessian kann negative kinetische Eigenwerte anderer Sektoren nicht ausschließen.

# 10. Testprogramm und Reproduzierbarkeit

`tests/2026-11-27_UniverseLab_2T05_GaugeMixingChecks_v0.1.py` prüft **28** elementare Identitäten: metrisches Blockinverse und Volumenmaß; exakte horizontale Phasenzerlegung; lokale Winkel- und U(1)-Eichinvarianz; Kappen-Massenrang und Nullvektor; verallgemeinerten Toy-Eigenwert; Patchübergänge; radialen Flux-Mischterm; Rückgewinnung der isolierten 2T-04-Form; Anforderungen an $C_r$ bei $r$-abhängigen Winkelverschiebungen.

**Lokaler Testlauf:** `28 tests ... OK` in SymPy. Eine GitHub-CI-Ausführung, ein vollständiger physikalischer Backend-Lauf und eine unabhängige zweite Implementierung des Feld-Hessians wurden **nicht** durchgeführt.

# 11. Lokale Ward-Identitäten und konditionale Interface-Variation

Die Kappenform liefert neben der Ranggleichung auch **lokale Quellenbeziehungen**, die später zur Kontrolle der gekoppelten Feldvariation dienen können. Schreibe bei konstantem Hintergrund und ausgeschlossenen zusätzlichen Cap-Bending-Termen

$$
S_{\Sigma,V}^{(2)}=-\frac{\mathcal C_\Sigma}{2}\int d^4x\sqrt{|g_4|}\,\Xi_\mu\Xi^\mu,
\qquad \Xi_\mu=\partial_\mu s-q_\sigma B_\mu-N_\sigma C_\mu.
$$

Die Euler-Ableitungen ergeben **mit der hier gewählten Variation als Definition der Quellen**

$$
J_B^\mu:=\frac{1}{\sqrt{|g_4|}}\frac{\delta S_\Sigma}{\delta B_\mu}
=\mathcal C_\Sigma q_\sigma\Xi^\mu,\qquad
J_C^\mu:=\frac{1}{\sqrt{|g_4|}}\frac{\delta S_\Sigma}{\delta C_\mu}
=\mathcal C_\Sigma N_\sigma\Xi^\mu,
$$

$$
J_s:=\frac{1}{\sqrt{|g_4|}}\frac{\delta S_\Sigma}{\delta s}
=\mathcal C_\Sigma\nabla_\mu\Xi^\mu.
$$

Somit müssen die **lokalen Ward-Identitäten** gelten:

$$
\boxed{\quad\nabla_\mu J_B^\mu=q_\sigma J_s,\qquad
\nabla_\mu J_C^\mu=N_\sigma J_s.\quad}
$$

Diese Beziehungen sind bei konstantem $\mathcal C_\Sigma$ direkt bewiesen; bei ortsabhängigem $\mathcal C_\Sigma$ gilt dieselbe Struktur mit $J_s=\nabla_\mu(\mathcal C_\Sigma\Xi^\mu)$. **Sie ersetzen nicht die Bulk-Gauß-, Impuls- oder Einstein-Zwänge**. Auf einer zulässigen stationären Kappenphase mit $J_s=0$ müssen beide Kappenströme kovariant erhalten sein.

## 11.1 Was eine vollständige gekoppelte Randbedingung leisten müsste

Für einen allgemeinen hypothetischen zweikomponentigen selbstadjungierten Radialoperator mit symmetrischer Flussmatrix $\mathbf P_s(r)$ und einem gemeinsamen Interfaceprofil $\mathbf f_\Sigma=(f_B,f_C)^T$ wäre die quadratische Form

$$
\mathfrak q[\mathbf f]=\frac12\sum_s\int dr_s\left[(\partial_r\mathbf f)^T\mathbf P_s\partial_r\mathbf f+\mathbf f^T\mathbf Q_s\mathbf f\right]
+\frac{\mathcal C_\Sigma}{2}\bigl(\mathbf v^T\mathbf f_\Sigma\bigr)^2,
\quad\mathbf v^T=(q_\sigma,N_\sigma).
$$

**Nur falls** dieses Modell nach vollständiger Constraint-Elimination tatsächlich gültig wäre, folgte durch Variation die lokale Interface-Bedingung

$$
\boxed{\quad\sum_s n_s^{r_s}\,\mathbf P_s\partial_{r_s}\mathbf f_s
+\mathcal C_\Sigma\mathbf v(\mathbf v^T\mathbf f_\Sigma)=0\quad}
$$

vor möglichen zusätzlichen randlokalisierten Kinetik-, Bending- und Feldmischungsbeiträgen. Hier sind $\mathbf P_s$ und $\mathbf Q_s$ **nicht** aus der vollständigen HZT-Wirkung berechnet. Die Formel ist deshalb ein **konditionaler allgemeiner Variationssatz**, keine neue M0-Modengleichung.

**Zusätzlicher Gegencheck:** Die Variation des Kappenausdrucks erzeugt einen Quellenvektor proportional zu $\mathbf v$, der für *jede* zulässige Feldkonfiguration orthogonal zu $(N_\sigma,-q_\sigma)$ liegt. Dieser algebraische Nullkanal der lokalen Kappenquelle bleibt auch dann bestehen, wenn die Bulk-Dynamik ihn später mit zusätzlicher Energie versieht.

# 12. Wissenschaftliche Gesamtentscheidung und nächster Schritt

**[BEWIESEN/KONDITIONAL]** Die ursprünglich isolierte Kappen-Robin-Masse ist nur die $(A_\mu,A_\mu)$-Projektion eines mit dem Graviphoton gemischten, eichinvarianten Kappenquadratikterms. Dessen transversale Massmatrix hat genau Rang eins bei nichtverschwindendem $q_\sigma$.

**[OFFEN]** Ob auf dem vollständigen, global regulären 6D-Hintergrund eine physikalische 4D-Nullmode existiert und welche Kopplung sie an beobachtete Materie hätte.

**Nächster Block – `UL-GRQM-2T06`:** Vollständiger off-shell-Maxwell-Einstein-Vektor-Hessian einschließlich GHY und Kappenvariation **zuerst analytisch**, dann Zwangselimination und geeignete globale Modendomäne. Eine dynamisch gültige On-shell-Interpretation bleibt gesperrt, bis der Hintergrund und seine Junction-Bedingungen nachgewiesen sind.

**Governance:** Kein Merge, keine neue Parentwirkung, kein Autorisierungs-/Grant-Artefakt, keine Hochstufung von K1-D oder K1-E, kein empirischer Claim.

# 13. Prüfbare Anschlussfragen für 2T-06

Die nächste Untersuchung sollte nicht zuerst einen numerischen Eigenwertsolver entwickeln. Aus der Erfahrung mit 2T-04/2T-05 ist die Reihenfolge **Wirkung → Zwangskern → selbstadjungierter Randoperator → Moden → Quellenresiduen** zwingend.

**A. Vollständiger Vektor-Hessian.** Zunächst sind die linearen Störungsvariablen der fünf- beziehungsweise sechsdimensionalen ADM-/Kaluza-Zerlegung festzulegen. Der Gravitationsanteil muss die Vektorstörungen in $g_{\mu\chi}$ und $g_{\mu r}$, die Kappen-GHY-/Israel-Variation sowie die Impuls- und Hamilton-Gleichungen enthalten. Der Maxwell-Sektor muss gleichzeitig $B_\mu$, $B_r$, $A_\chi$ und den magnetischen Hintergrundfluss behandeln. Die Kappenphase und die geometrische Lage der Kappe sind mit eigener Variationsregel zu führen; eine explizite Fixierung der Kappe darf erst nach Nachweis der entsprechenden Eichfreiheit erfolgen.

**B. Off-shell-Sicherungen.** Die berechnete Quadratik muss für jede zulässige Hintergrundkonfiguration die linearen Eichidentitäten erfüllen, auch wenn die Hintergrundgleichungen noch nicht benutzt werden. Solche Tests unterscheiden reine Kinematik vom dynamischen On-shell-Anspruch. Das im vorliegenden Ledger hergeleitete Quellenpaar $J_B,J_C$ und die beiden Ward-Identitäten sind dafür verwendbare Regressionsinvarianten.

**C. Nachfolgender On-shell-Schritt.** Nach dokumentierter Lösung der Bulkgleichungen müssen die beiden unabhängigen Israel-Junctions, das Skalar- und Maxwell-Matching, die globale Fluxquantisierung, beide glatten Pole und der $rr$-Constraint gemeinsam mit toleranzkontrollierten Residuen geprüft werden. Erst danach darf die linearisierte Störungswirkung als Dynamik physikalischer Moden interpretiert werden.

**D. Physische Reduktion.** Anschließend sind die Lagrange-Multiplikatoren und ihre Constraints zu eliminieren, das Skalarprodukt aus der tatsächlich reduzierten Quadratik zu bestimmen und die Trägheit der kinetischen Matrix im gesamten relevanten Feldraum zu prüfen. Ein Nullvektor der Cap-Massmatrix ist dafür **kein Ersatz**. Der globale Modenoperator muss durch Domäne, Pole, Cap-Junctions und U(1)-Patchübergänge vollständig festgelegt sein.

**E. Observablen erst mit Quellen.** Sobald eine unabhängige gewöhnliche Materiewirkung und deren 4D-Reduktion vorliegen, kann die Antwortfunktion formal als

$$
\mathcal G_{JJ}(p^2)=\mathbf J^T\bigl[p^2\mathbf K+\mathbf M^2+\boldsymbol\Pi(p^2)\bigr]^{-1}\mathbf J
$$

organisiert werden. $\boldsymbol\Pi$ fasst nach ausdrücklicher Definition nichtlokale beziehungsweise integrierte Beiträge zusammen; ohne solche Definition wird dieser Term nicht numerisch eingesetzt. Physikalisch unterschiedliche Modelle lassen sich erst bei gleicher Quellklasse anhand der Polstellen, Residuen und korrelierten Beobachtungsgrößen vergleichen. Eine negative Residuen-Signatur in einem tatsächlich physikalischen, normierten Kanal wäre ein ernster Ghost-Hinweis. Eine positive Residue in einem einzelnen Kanal beweist dagegen keine vollständige Ghostfreiheit.

**Falsifikationskriterien:** Eine widersprüchliche U(1)-Patchklebung, Verletzung der Ward-Identitäten, fehlende Erhaltung des Constraint-Unterraums, negative physikalische kinetische Eigenwerte, nicht erfüllbare Kappen-Junctions oder eine nachweislich inkonsistente Materie-Forward-Map würden jeweils die konkret betroffene Modellvariante blockieren. Ein nicht durchgeführter Test erhält den Status **OFFEN**, nicht PASS und nicht FAIL.
