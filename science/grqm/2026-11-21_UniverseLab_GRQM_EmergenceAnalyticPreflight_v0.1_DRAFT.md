---
title: "UniverseLab | Emergenz von Raumzeit und Gravitation"
subtitle: "UL-GRQM-EMERG-001 | Analytische Vorprüfung v0.1"
author: "UniverseLab – Forschungsentwurf"
date: "21. November 2026"
lang: de-DE
papersize: a4
geometry: margin=23mm
fontsize: 10pt
colorlinks: true
linkcolor: MidnightBlue
urlcolor: MidnightBlue
header-includes:
  - \usepackage{microtype}
  - \usepackage{booktabs}
---

# Status, Geltungsbereich und Kurzbefund

**ID:** `UL-GRQM-EMERG-001`  
**Datum:** 2026-11-21  
**Version:** v0.1  
**Status:** `DRAFT_ANALYTIC_ONLY / NONCANONICAL`  
**Architektur:** HPVS → HZT-M0 → HZT-Full  
**Physical gate effect:** `NONE`  
**Physical evidence effect:** `NONE`  
**Solver-/Grant-Autorisierung:** `FALSE`  
**Originaltexte der besprochenen Chats:** nicht als Volltext überprüft; Anknüpfung über den expliziten Gesprächskontext und den vorliegenden Repository-Auszug.

**Kernresultat.** Die Verschränkungsentropie ist in geeigneten holografischen Modellen mit Geometrie verknüpft. Das Rekonstruktionsresultat von Faulkner *et al.* liefert unter expliziten Annahmen die linearisierten Gravitationsgleichungen um AdS. Es liefert **weder** die allgemeine Emergenz unserer de-Sitter-nahen Raumzeit **noch** eine Rechtfertigung einer zweiten physikalischen Zeitrichtung. Die gegenwärtig diskutierte 6D-Diskus-Metrik besitzt bei reellen Warp-Funktionen und gewöhnlicher 4D-Minkowski-Metrik die Signatur (5,1), nicht (4,2). Eine direkte Identifikation als fundamentale 2T-Metrik ist damit für diesen Ansatz blockiert; als effektive 1T-Projektion bleibt er konditional zulässig.

## Konventionen

- Wir verwenden zunächst $c=\hbar=k_\mathrm B=1$. Energien haben Dimension $L^{-1}$, Energiedichten $L^{-4}$ in 4D.
- Die Signaturangabe $(n_s,n_t)$ zählt zunächst raumartige und danach zeitartige Eigenrichtungen. Eine Zeitrichtung wird mit negativem Vorzeichen geschrieben.
- $D$ bezeichnet die Dimension einer gravitativen Bulk-Theorie; $G_D$ ist ihre *D*-dimensionale Newton-Konstante.
- $\rho$ ist ein Dichteoperator; $A$ ist eine Quanten-Teilregion, $\bar A$ ihr Komplement; $R>0$ ist der Radius einer kugelförmigen Region.
- **[BEWIESEN]** bezeichnet nachfolgend nur die explizit angegebene, selbst nachvollziehbare mathematische Aussage unter ihren Annahmen, nicht eine empirische Theorie- oder Universumsbestätigung.

# 1. Minimaler analytischer Kern

## 1.1 Der erste Hauptsatz der Verschränkungsentropie

Für einen regulierten Zustand $\rho_A(\lambda)$ mit $\operatorname{Tr}\rho_A=1$ und vollem Rang im betrachteten Zustandsbereich gilt

$$
S_A(\lambda)=-\operatorname{Tr}(\rho_A\ln\rho_A),\qquad
K_A^{(0)}=-\ln\rho_A(0).
$$

Wir variieren bei $\lambda=0$:

$$
\delta S_A=-\operatorname{Tr}(\delta\rho_A\ln\rho_A^{(0)})
-\operatorname{Tr}(\delta\rho_A).
$$

Aus $\operatorname{Tr}(\delta\rho_A)=0$ folgt

$$
\boxed{\delta S_A=\operatorname{Tr}(\delta\rho_A K_A^{(0)})=\delta\langle K_A^{(0)}\rangle.}
\tag{1}
$$

**Status [BEWIESEN]**, für regulierte, differenzierbare Zustandsfamilien; in kontinuierlichen Quantenfeldtheorien bedarf die Formulierung lokaler Dichteoperatoren bzw. Entropien zusätzlicher algebraischer oder UV-regulierter Präzisierung. Gleichung (1) setzt **keine** Gravitation voraus.

## 1.2 Expliziter 4D-CFT-Test für eine Kugel

Für das Vakuum einer *vierdimensionalen konformen Feldtheorie* in flacher Raumzeit besitzt eine kugelförmige Region zum Zeitpunkt $t=0$ den lokalen modularen Hamiltonoperator

$$
K_R=2\pi\int_{|\mathbf x|<R}\!\mathrm d^3x\;
\frac{R^2-r^2}{2R}T_{00}(\mathbf x)+C.
\tag{2}
$$

$C$ ist zustandsunabhängig. Für eine **räumlich konstante** kleine Änderung der Energiedichte $\delta\epsilon$ gilt

$$
\delta S_R=2\pi\frac{4\pi}{2R}\,\delta\epsilon
\int_0^R(R^2-r^2)r^2\,\mathrm dr.
$$

Mit

$$
\int_0^R(R^2-r^2)r^2\,\mathrm dr
=\frac{R^5}{3}-\frac{R^5}{5}=\frac{2R^5}{15}
$$

folgt unmittelbar

$$
\boxed{\delta S_R=\frac{8\pi^2}{15}\,R^4\delta\epsilon.}
\tag{3}
$$

**Dimensionstest:** $[R^4\delta\epsilon]=L^4L^{-4}=1$. **Grenzfall:** Bei $\delta\epsilon=0$ verschwindet die lineare Entropievariation. Für $R\to0$ geht die Variation bei endlicher $\delta\epsilon$ wie $R^4$ gegen null. Bei inhomogenem glattem $\delta T_{00}$ ist (3) die lokale führende Näherung um den Kugelmittelpunkt, nicht generell die exakte Integralformel.

**Status [BEWIESEN]** unter den obigen CFT-, Kugel- und Störungsannahmen. Dies ist **noch keine** Gleichung der Einstein-Gravitation.

## 1.3 Notwendige Zusatzannahme: eine holografische Dualität

Im führenden semiklassischen Regime geeigneter AdS/CFT-Theorien lautet die Ryu-Takayanagi-Beziehung für statische Zustände:

$$
S_A=\frac{\operatorname{Area}(\gamma_A)}{4G_D\hbar}
\quad(c=1),
\tag{4}
$$

wobei $\gamma_A$ eine homologe minimalflächige Bulkfläche der **Kodimension zwei** ist. Für zeitabhängige Situationen benötigt man die kovariante HRT-Verallgemeinerung; quantenkorrigiert treten zusätzliche Bulk-Entropieterme auf. Aus (1), (4) sowie der Gültigkeit der holografischen Wörterbuchregeln für alle kugelförmigen Regionen folgt in der Klasse von Faulkner *et al.* die linearisierte gravitative Dynamik um **AdS**. Das ist ein Literaturresultat, **keine hier neu ausgeführte vollständige Holografie-Herleitung**.

$$
\delta S_A=\delta\langle K_A\rangle\quad\overset{\mathrm{AdS/CFT\;Annahmen}}{\Longrightarrow}
\quad\delta E_{MN}^{\mathrm{grav}}=0.
\tag{5}
$$

**Dimensionstest 6D:** $[G_6\hbar]=L^4$ bei $c=1$ und $[\operatorname{Area}(\gamma_A)]=L^4$. Das bestätigt nur die dimensionsrichtige Schreibweise, nicht die Existenz einer 6D-HZT-Holografie.

**Dimensions- und Signaturwarnung:** Gewöhnliche AdS$_6$/CFT$_5$ koppelt eine sechsdimensionale Bulk-Theorie an eine fünfdimensionale Randtheorie. Eine vierdimensionale Brane plus **zwei** Zeitrichtungen ist nicht ohne zusätzliche Konstruktion mit dieser Dualität gleichzusetzen.

# 2. Nichtidentifizierbarkeit: Gegenbeispiel zur Aussage „Verschränkung = Entfernung“

Wir betrachten zwei Qubits im Bell-Zustand

$$
|\Phi^+\rangle=\frac{|00\rangle+|11\rangle}{\sqrt2},\qquad
\rho_A=\rho_B=\frac{I_2}{2}.
$$

Daraus folgen

$$
S(A)=S(B)=\ln2,\qquad S(AB)=0,\qquad I(A\!:\!B)=2\ln2.
\tag{6}
$$

Die gleichen Dichtematrizen und Korrelationsmaße sind möglich, wenn die Qubits in einer extern vorgegebenen Geometrie einen Zentimeter oder ein Lichtjahr auseinanderliegen. Es existiert daher **keine eindeutige inverse Abbildung** von dem einzelnen Verschränkungsmaß $I(A:B)$ auf eine physikalische Entfernung.

**Status [BEWIESEN]** als Gegenbeispiel zur uneingeschränkten Behauptung. Für eine tatsächliche Geometriere­konstruktion werden mindestens zusätzliche Daten über Algebra/Subregionen, viele Freiheitsgrade, Dynamik, Lokalität und Konsistenzbedingungen benötigt. Welche dieser Voraussetzungen für HZT konstruiert werden können, ist **[OFFEN]**.

# 3. Signatur-Audit der diskutierten Diskus-Metrik

Für reelle $A(r,\theta)$, $B(r,\theta)$ und $C(r,\theta)$ setzen wir

$$
\mathrm ds^2=e^{-2A}\eta_{\mu\nu}\mathrm dx^\mu\mathrm dx^\nu
+e^{2B}\mathrm dr^2+e^{2C}r^2\mathrm d\theta^2,
\qquad\eta=\operatorname{diag}(-1,+1,+1,+1).
\tag{7}
$$

Für $r>0$ gilt aufgrund der Blockdiagonalität

$$
\det g_6=e^{-8A}\det\eta\cdot e^{2B}\cdot e^{2C}r^2
=\boxed{-e^{-8A+2B+2C}r^2}.
\tag{8}
$$

Alle fünf raumartigen Diagonaleinträge sind positiv, genau ein Eintrag ist negativ:

$$
\boxed{(n_s,n_t)=(5,1)\ne(4,2).}
\tag{9}
$$

Eine nichtsinguläre reelle Koordinatentransformation kann die Signatur nach dem Trägheitssatz von Sylvester **nicht** ändern. Bei der gewünschten 2T-Signatur wäre $\det g_6>0$ (für zwei negative Eigenwerte). In einer allgemeinen 2T-Wirkung ist daher $\sqrt{|\det g_6|}$ die sichere reelle Volumendichte, anstelle einer unverändert aus der Einzeit-Konvention übernommenen $\sqrt{-\det g_6}$.

**Einschränkung:** $r=0$ ist in (7) ein koordinatenbedingt entarteter Ort der Polardarstellung; dort ist die punktweise Signaturanalyse in dieser Karte nicht anwendbar. Die Aussage gilt auf dem nicht entarteten Bereich $r>0$.

**Befund SIG-01 [BEWIESEN für Ansatz (7)]:** Als fundamentale Zweizeit-Metrik in der gegebenen Form nicht möglich. **Alternative [KONDITIONAL]:** Ansatz (7) als einzeitige effektive Projektion einer getrennt zu spezifizierenden 2T-Theorie interpretieren und diese Projektion explizit herleiten.

# 4. Ultrahyperbolische Dynamik: exaktes 2T-Risikobeispiel

Als **Gegenbeispiel zur automatischen Stabilität**, nicht als Modell der HZT, betrachten wir einen freien masselosen reellen Skalar auf flachem $\mathbb R^{4,2}$:

$$
\eta_{MN}=\operatorname{diag}(-,+,+,+,-,+),\qquad
\square_6\phi=(-\partial_t^2+\nabla_3^2-\partial_\tau^2+\partial_y^2)\phi=0.
\tag{10}
$$

Wir betrachten formal eine Fourier-Mode der zusätzlichen zeitartigen Richtung

$$
\phi(t,\mathbf x,\tau,y)=\chi(t,\mathbf x)e^{in\tau/L_\tau},
\qquad\partial_y\phi=0.
$$

$L_\tau>0$ ist nur eine Modenskala; die periodische Identifikation einer zeitartigen Koordinate wäre zusätzlich **kausal problematisch** und wird hier nicht als physikalische Konstruktion vorgeschlagen. Mit $\chi=e^{-i\omega t+i\mathbf k\cdot\mathbf x}$ folgt

$$
\boxed{\omega^2=|\mathbf k|^2-\frac{n^2}{L_\tau^2}.}
\tag{11}
$$

Für $n\ne0$ und $|\mathbf k|<|n|/L_\tau$ folgt $\omega^2<0$ und somit exponentielles Wachsen/Abfallen in $t$.

**Status [BEWIESEN für dieses freie Toy-Modell].** Diese Instabilität ist eine **tachyonische Mode**, nicht allein ein Beweis für einen kinetischen Ghost. Unter denselben Konventionen besitzt die zugehörige $t$-Hamiltondichte einen negativen $\tau$-Gradientenbeitrag:

$$
\mathcal H_t=\frac12\Big[(\partial_t\phi)^2+|\nabla_3\phi|^2+(\partial_y\phi)^2-(\partial_\tau\phi)^2\Big].
\tag{12}
$$

Damit ist die Energie ohne Zusatzbedingungen nach unten unbeschränkt. Dies illustriert, warum eine zweite Zeitrichtung nicht allein durch eine positive 4D-Kinetikmatrix abgesichert ist. **Dynamische Zwangsbedingungen und Eichreduktion können die Schlussfolgerung verändern.** Für 2T-Gravitation zeigen Arbeiten von Bars eine solche, für ihre eigene Wirkung ausgearbeitete Struktur; deren Ergebnisse lassen sich nicht ungeprüft auf HZT übertragen.

Als zusätzliche mathematische Nuance zeigen Craig und Weinstein, dass eine ultrahyperbolische Anfangswertaufgabe auf geeigneten Flächen unter **nichtlokalen Fourier-Beschränkungen** wohlgestellt sein kann. Eine naive universelle Unmöglichkeitsbehauptung wäre somit falsch.

# 5. Forschungsarchitektur und Beweispflichten

## 5.1 Tentative Postulate (keine HZT-Kanonänderung)

- **E0 – Zustandsraum:** Ein konkret definierter Hilbertraum bzw. eine Observablenalgebra mit physikalischem Positivitätsbegriff.
- **E1 – Subregionen:** Eine konsistente Zuordnung von Observablenalgebren zu Teilbereichen, noch ohne Interpretation als vorgegebene Raumregionen.
- **E2 – Rekonstruktion:** Eine mathematisch definierte Abbildung $\mathcal R:\text{Quantendaten}\to(g_{MN},\text{Geometrie})$; ihre Nicht-Eindeutigkeit und Eichäquivalenzen sind anzugeben.
- **E3 – 2T-Struktur:** Falls $(4,2)$ fundamental sein soll, sind Symmetrien, Zwangsfunktionen und der positive physikalische Zustandsraum ausdrücklich zu konstruieren.
- **E4 – 4D-Projektion:** Eine Abbildung $\mathcal P$ auf einen dynamisch konsistenten 4D-Einzeitsektor einschließlich normierter Moden, positiver Kinetik und geeigneter Kausalität.
- **E5 – Dynamik und Daten:** Erst ein hergeleiteter 4D-Wirkungsgrenzfall liefert beobachtbare Abweichungen, die ohne ad-hoc-Parameter gegenüber Referenzmodellen getestet werden können.

Die schematische Kette lautet

$$
(\mathcal A,\rho,\text{Dynamik})
\xrightarrow[\text{offen}]{\mathcal R}
(g^{(6)}_{MN},\text{2T-Zwangsstruktur})
\xrightarrow[\text{offen}]{\mathcal P}
(S^{(4)}_{\mathrm{eff}},g^{(4)}_{\mu\nu})
\xrightarrow[\text{offen}]{\mathrm{Forward\ Map}}
\mathcal O.
\tag{13}
$$

Die Quantendaten auf der linken Seite sind **nicht** bereits als fundamentaler Teil des HZT-Kanons etabliert. Auch $\mathcal R$, $\mathcal P$ und die Forward-Map sind für diese Hypothese nicht hergeleitet.

## 5.2 Falsifikations- und Admissibilitäts-Gates

| Gate | Erforderlicher Nachweis | Stand v0.1 |
|:--|:--|:--|
| G-SIG | Klare Zuordnung: fundamentale $(4,2)$-Metrik oder effektive $(5,1)$-Projektion | **BLOCKIERT** für direkte Identifikation mit (7) |
| G-QST | Explizite algebraische Quantendaten, Dynamik, Positivität | **OFFEN** |
| G-REC | Wohldefinierte Rekonstruktionsabbildung samt Äquivalenzen und 6D-Zieldaten | **OFFEN** |
| G-2T | 2T-Zwangsalgebra, Entfernung redundanter Moden, Kausalität | **OFFEN** |
| G-PHYS | Positives physikalisches kinetisches System; Spektrum und Hamiltonian überprüft | **OFFEN** |
| G-GR | Konsistenter 4D-GR-Grenzfall samt Materiekopplungen | **OFFEN** |
| G-OBS | Deterministische, quellengebundene Kette bis zu $H(z)$, $f\sigma_8$, $\mu$, $\Sigma$, GW usw. | **OFFEN** |
| G-DATA | Identifizierbarkeit, Sensitivität, Kovarianzen, Gegenmodelle, Datentrennung | **NICHT BEGONNEN** |

**Sperrregel:** Weder eine schöne Visualisierung noch ein Toy-Fit noch die Existenz holografischer Literatur ersetzen die Gates G-REC, G-2T, G-GR oder G-OBS. Die gegenwärtigen K1-D/K1-E-Gates werden durch dieses Dokument in keiner Weise verändert.

## 5.3 Priorisierte nächste analytische Arbeit

1. **SIG-02:** Im Original-HZT-Bulk eindeutig verifizieren, welche Koordinaten die zwei zeitartigen Freiheitsgrade darstellen; den Status der Diskus-Metrik als *fundamental* oder *reduziert* schriftlich fixieren.
2. **2T-01:** Die vollständige quadratische Wirkung unter Berücksichtigung der Constraints herleiten und das reduzierte kinetische System einschließlich der zeitartigen Gradienten prüfen.
3. **REC-01:** Ein minimales, wohldefiniertes Quantenmodell auswählen und zeigen, welche geometrischen Observablen ohne willkürlich vorausgesetzte Entfernung tatsächlich rekonstruierbar sind.
4. **GR-01:** Nur falls REC-01 bestanden ist, einen kontrollierten effektiven Einstein-Grenzfall prüfen; AdS-Resultate nicht stillschweigend in dS oder die Diskus-Geometrie übertragen.
5. **OBS-01:** Erst nach GR-01 eine konkrete Vorhersage mit Parameter- und Datenprovenienz ableiten; HPVS → HZT-M0 → HZT-Full beibehalten.

# 6. Quellennachweise und Zugriffsumfang

**Primärliteratur, Abstracts / Verlagsinformationen tatsächlich geprüft (2026-11-21):**

1. Ryu, S.; Takayanagi, T. (2006): *Holographic Derivation of Entanglement Entropy from AdS/CFT*, Phys. Rev. Lett. 96, 181602. https://arxiv.org/abs/hep-th/0603001
2. Faulkner, T.; Guica, M.; Hartman, T.; Myers, R. C.; Van Raamsdonk, M. (2014): *Gravitation from entanglement in holographic CFTs*, JHEP 03, 051. https://doi.org/10.1007/JHEP03(2014)051
3. Jacobson, T. (2016): *Entanglement Equilibrium and the Einstein Equation*, Phys. Rev. Lett. 116, 201101. https://doi.org/10.1103/PhysRevLett.116.201101
4. Bars, I. (2008): *Gravity in two-time physics*, Phys. Rev. D 77, 125027. https://doi.org/10.1103/PhysRevD.77.125027
5. Araújo-Regado, G.; Thavanesan, A.; Wall, A. C. (2026): *Holographic cosmology at finite time*, JHEP 04, 121. https://doi.org/10.1007/JHEP04(2026)121
6. Craig, W.; Weinstein, S. (2009): *On determinism and well-posedness in multiple time dimensions*, arXiv:0812.0210. https://arxiv.org/abs/0812.0210
7. Hubeny, V. E.; Rangamani, M.; Takayanagi, T. (2007): *A Covariant Holographic Entanglement Entropy Proposal*, JHEP 07, 062. https://arxiv.org/abs/0705.0016
8. Casini, H.; Huerta, M.; Myers, R. C. (2011): *Towards a derivation of holographic entanglement entropy*, JHEP 05, 036. https://doi.org/10.1007/JHEP05(2011)036

**Projektquellen, `main` über GitHub-Zugriff gelesen:**

- `governance/2026-08-01_UNIVERSELAB_FILE_NAMING_STANDARD_v1.0.md`
- `governance/2026-09-01_UniverseLab_CurrentMainCanonicalStateReconciliation_v1.0.md` (historischer Snapshot, nicht automatisch heutiger Gate-Stand)
- `governance/2026-09-14_UniverseLab_ProvenanceConsistencyDetectabilityRule_v1.1.md`
- `README.md`

**Nicht durchgeführt:** vollständige Prüfung der Original-Fachpaper auf Gleichungsniveau; 6D-Parent-Wirkung aus Original-HZT-Dateien erneut abgeleitet; quantitative HZT-Fits; Constraint-Algebra von HZT; vollständiger Ghostfreiheitsbeweis; Beobachtungsanalyse. Numerische/symbolische Begleitchecks in diesem Arbeitspaket prüfen **nur** die ausgewiesenen elementaren Identitäten.

---

**Abschlussstatus v0.1:** Ein konkreter analytischer Zugang (1)–(5) ist dokumentiert; SIG-01 und das 2T-Risikobeispiel sind geprüft. Kein Nachweis einer 6D-Quantengravitation und keine Freigabe einer HZT-Änderung.