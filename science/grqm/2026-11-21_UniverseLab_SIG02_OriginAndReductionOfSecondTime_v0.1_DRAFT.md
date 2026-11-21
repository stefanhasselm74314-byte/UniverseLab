---
title: "UniverseLab — SIG-02: Herkunft und Reduktion der zweiten Zeitdimension"
subtitle: "UL-GRQM-SIG02-001 | Analytischer Forschungsbericht v0.1"
author: "UniverseLab | unabhängige analytische Vorprüfung"
date: "21. November 2026"
lang: de-DE
fontsize: 10pt
geometry: "a4paper,margin=21mm"
mainfont: "Noto Serif"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
colorlinks: true
urlcolor: blue
header-includes:
  - \usepackage{microtype}
  - \usepackage{booktabs}
---

# Kurzresultat und Status

**Kennung:** `UL-GRQM-SIG02-001`  
**Version / Datum:** v0.1 / 2026-11-21  
**Status:** `DRAFT_ANALYTIC_ONLY / NONCANONICAL`  
**Architektur:** HPVS $\rightarrow$ HZT-M0 $\rightarrow$ HZT-Full  
**Physical evidence effect:** `NONE`  
**Physical gate effect:** `NONE`  
**AuthorizationDecision / SingleUseGrant:** `NOT_CREATED`  
**K1-D / K1-E:** `NOT_RELEASED / NOT_ADMISSIBLE`  
**Geltungsgrenze:** Es wurden projektseitig konkrete Dateien auf `main` und externe Primärarbeiten geprüft. Ein vollständiger originaler HZT-Full-2T-Aktionssatz wurde hierbei **nicht** nachgewiesen; keine Vollprüfung privater Archiv-Chats.

**Hauptergebnis [QUELLENBESTÄTIGT].** Die eingefrorene Parentwirkung `SCI-001/SCI-002` und der maschinenlesbare Vertrag `hzt-s6-parent-action-v0.1.json` definieren ausdrücklich einen **einzeitigen** 6D-Kontrollzweig mit Signatur $(-,+,+,+,+,+)$ und positiv definitem zweidimensionalem Innenraum. Der 2T-Sektor von HZT-Full wird dadurch weder konstruiert noch widerlegt. Die Diskus-Metrik ist für diesen Stand als eigene einzeitige Modellklasse zu behandeln, nicht als stillschweigend nachgewiesene 2T-Projektion.

**Hauptergebnis [MATHEMATISCH BEWIESEN – im bezeichneten Regime].** Eine reguläre 4+2-Blockzerlegung mit Lorentz-Signatur $(-,+,+,+)$ in vier Dimensionen und einer fundamentalen 6D-Signatur $(4+,2-)$ besitzt notwendig eine zusätzliche negative Richtung im zweidimensionalen internen Block. Sie kann nicht mit einem positiv definiten Innenraum identisch sein. Eine Eichreduktion ist eine andere, logisch mögliche Konstruktion; für das freie $\mathrm{Sp}(2,\mathbb R)$-Teilchen kann eine konkrete 2T-zu-1T-Eichwahl angegeben werden. Die Übertragung auf eine dynamische Einstein-Maxwell-Skalar-Kappenwirkung bleibt offen.

# 1. Quellenkette: Was liegt im UniverseLab tatsächlich vor?

Die folgenden Dateien wurden über den verbundenen GitHub-Zugang im Repository `stefanhasselm74314-byte/UniverseLab` auf `main` direkt gelesen. Die hier genannten SHA-Werte identifizieren die gelesenen Dateiblobs, nicht einen neu ratifizierten Gesamtkanon.

| Quellenkennung | Prüfbefund | Blob-SHA (kurz) |
|:--|:--|:--|
| `SCI-001/002` | Parentwirkung: ausdrücklich 1T, interne Geometrie positiv | `df1b4a65d613` |
| `S6-PAR-JSON` | Signatur 1T; K1-D und K1-E gesperrt | `aab94691b3a9` |
| `ADM-D2NQ` | ADM nach einer Zeit; kein Import einer 2. Zeit | `b618da55d0be` |
| `ULSH05-WP1` | 2T-Full ausgeschlossen; Hessian/Reduktion offen | `6d18236526a9` |
| `R1-SOURCE` | Historische A0- und GW-Modellidentität offen | `8f2cc4d18246` |

Die zugehörigen Online-Nachweise sind über die vollständigen Pfade in den Literatur- und Quellverweisen am Dokumentende erreichbar.

**Wesentliche Korrektur zu SIG-01:** Die Feststellung, dass der Diskus-Ansatz Signatur $(5+,1-)$ trägt, war korrekt. Die daraus zunächst offengelassene Frage, ob dies unbeabsichtigt sei, wird nun teilweise beantwortet: Für `HZT-M0-S6` ist genau diese einzeitige Signatur ausdrücklich gewählt. **Nicht** beantwortet ist, ob und wie dieser Sektor eine kontrollierte Projektion eines hypothetischen HZT-Full-2T-Parents ist.

# 2. Symbol- und Konventionsblatt

- Signaturkonvention: $(-,+,+,+)$ in 4D; Anzahlen $n_+,n_-$ positiver beziehungsweise negativer Eigenwerte. Die Schreibweise (5,1) bedeutet $(n_+,n_-)=(5,1)$, während die Schreibweise (4,2) genau zwei zeitartige Richtungen bezeichnet.
- $X^M$: sechs Positionen; $P_M$: sechs kanonisch konjugierte Impulse; $\{X^M,P_N\}=\delta^M{}_N$.
- $g_6$: reelle symmetrische, nichtentartete 6D-Metrik; $g_4$: effektive vierdimensionale Metrik.
- $M_6$: sechsdimensionale Gravitation-Massenskala mit $[M_6]=M$; $M_4$ entsprechend in 4D.
- $A$: Warp-Funktion; $L(r)>0$: interner Kreisradius im aktuellen S6-Zweig; $\chi\sim\chi+2\pi$.
- $u,v$: zusätzliche **lichtartige Kombinationen** der zwei weiteren Koordinaten im 2T-Flachraum; sie sind **nicht** einzeln zwei zusätzliche Zeitkoordinaten.
- In den 2T-Rechnungen werden $\hbar=c=1$ verwendet. $[X]=L$, $[P]=L^{-1}$, $[Q_{11}]=L^2$, $[Q_{12}]=1$, $[Q_{22}]=L^{-2}$; ggf. werden die Zwänge durch Skalen normiert.

# 3. Signatur und Volumendichte des kanonischen Kontrollzweigs

Die in der eingefrorenen S6-Wirkung verwendete Hintergrundmetrik lautet

$$
ds_6^2=e^{2A(r)}\bar g_{\mu\nu}dx^\mu dx^\nu+dr^2+L(r)^2d\chi^2,
\qquad \operatorname{In}(\bar g_4)=(3+,1-).
$$

Für $L>0$ und reelles $A$ besitzt sie dieselben vierdimensionalen Signaturen wie $\bar g_4$ sowie zwei zusätzliche **positive** Eigenwerte. Folglich

$$
\boxed{\operatorname{In}(g_6)=(5+,1-).}
$$

Beim alternativen Diskus-Ansatz

$$
ds_6^2=e^{-2A}\eta_{\mu\nu}dx^\mu dx^\nu+e^{2B}dr^2+e^{2C}r^2d\theta^2
$$

folgt für $r>0$

$$
\det g_6=-e^{-8A+2B+2C}r^2<0.
$$

Das ist mit einer **einzeitigen** 6D-Metrik vereinbar. Für einen regulären 6D-2T-Parent mit genau zwei negativen Eigenwerten wäre dagegen $\det g_6>0$ und die reelle invariante Dichte allgemein $\sqrt{|\det g_6|}$. Das unveränderte Einsetzen von $\sqrt{-g_6}$ aus dem 1T-Vertrag ist dort ohne neue Signaturkonvention unzulässig.

**Gültigkeitsgrenze:** Bei $r=0$ kann die Polarkoordinatenmatrix entarten, obwohl der glatte Pol geometrisch regulär ist. Das Determinantenargument bezieht sich daher auf nichtsinguläre Koordinatenbereiche, nicht auf einen vermeintlichen physikalischen Singularitätsbeweis am Pol.

# 4. No-Go für die naive positive-interne 2T-Blockreduktion

Eine allgemeine reelle symmetrische Metrik sei blockweise aufgeteilt:

$$
G=\begin{pmatrix}A&B\\B^T&D\end{pmatrix},
\quad A\in\mathbb R^{4\times4},\quad D\in\mathbb R^{2\times2},\quad\det D\ne0.
$$

Durch eine invertierbare blockdreieckige Kongruenztransformation wird $G$ in die Diagonalform

$$
\operatorname{diag}(S,D),\qquad S=A-BD^{-1}B^T
$$

überführt. Der Satz von Sylvester beziehungsweise die Haynsworth-Additivität liefert:

$$
\boxed{\operatorname{In}(G)=\operatorname{In}(S)+\operatorname{In}(D).}
$$

Wenn $G$ die 2T-Signatur $(4+,2-)$ und $S$ die beobachtete 4D-Signatur $(3+,1-)$ hat, muss gelten:

$$
\boxed{\operatorname{In}(D)=(1+,1-).}
$$

Ist $D$ hingegen positiv definit, so ergibt sich $\operatorname{In}(G)=(5+,1-)$, **unabhängig von nichtverschwindenden gemischten Blöcken** $B$.

Dies ist ein präzises No-Go unter den genannten Regularitäts- und Blockannahmen; es ist kein allgemeines Verbot singulärer Quotienten, Constraints, nichtlokaler Holografie oder einer 2T-Eichreduktion. Insbesondere beweist es nichts über die Existenz oder Nichtexistenz einer noch nicht angegebenen HZT-Full-Wirkung.

# 5. Freie zeitartige Kaluza-Klein-Richtung als Gegenbeispiel

Als unabhängigen Risikotest betrachten wir eine freie reelle skalare Mode in der flachen 6D-Geometrie

$$
ds^2=-dt^2+d\mathbf x^2-R^2d\theta^2+dz^2,
\quad \theta\sim\theta+2\pi.
$$

Hier ist $R>0$ ein **zeitartiger** Kompaktifizierungsradius. Der masselose Wellengleichungsoperator lautet für $z$-unabhängige Felder

$$
\Box_6=\Box_4-\frac{1}{R^2}\partial_\theta^2,\qquad
\Box_4=-\partial_t^2+\nabla^2.
$$

Mit $\Phi(x,\theta)=\sum_n\phi_n(x)e^{in\theta}$ folgt

$$
\left(\Box_4+\frac{n^2}{R^2}\right)\phi_n=0.
$$

Für die 4D-Konvention $(\Box_4-m_n^2)\phi_n=0$ bedeutet das

$$
\boxed{m_n^2=-\frac{n^2}{R^2}\le0.}
$$

Die Dispersionsrelation lautet

$$
\omega_n^2=|\mathbf k|^2-\frac{n^2}{R^2}.
$$

Für $n\ne0$ und $|\mathbf k|<|n|/R$ entstehen exponentiell wachsende beziehungsweise abklingende Lösungen. Eine **gewöhnliche** zeitartige Kompaktifizierung dieser freien Feldtheorie hat also tachyonische nichttriviale Moden. Der Nullmodus $n=0$ besteht diesen speziellen Test, aber seine isolierte Existenz ist weder eine vollständige Quantentheorie noch ein Beweis der Stabilität der gravitativen Sektoren.

**Wichtig:** Ein negativer Massenterm in diesem linearen Beispiel ist nicht mit einem bereits bewiesenen kinetischen Ghost gleichzusetzen. Ghosts betreffen unter anderem die Signatur der physikalisch reduzierten kinetischen Bilinearform und Hilbertraumnormen. Die zusätzlichen 2T-Eichbedingungen eines anderen Parents könnten dieses Gegenbeispiel außerhalb des physikalischen Zustandsraums platzieren.

# 6. Expliziter Sp(2,R)-Eichreduktionszeuge (freies Teilchen)

Der flache 6D-2T-Raum werde dargestellt durch

$$
ds^2=\eta_{\mu\nu}dx^\mu dx^\nu-2\,du\,dv,
\qquad\eta=\operatorname{diag}(-1,1,1,1).
$$

Der $u,v$-Block ist indefinite und fügt **eine** positive und **eine** negative Richtung zur 4D-Minkowski-Signatur hinzu: insgesamt $(4+,2-)$. Verwende kanonische Koordinaten $(x^\mu,u,v)$ mit Impulsen $(p_\mu,\pi_u,\pi_v)$. Die drei Zwangsfunktionen lauten

$$
\begin{aligned}
Q_{11}&=\eta_{\mu\nu}x^\mu x^\nu-2uv,\\
Q_{12}&=x^\mu p_\mu+u\pi_u+v\pi_v,\\
Q_{22}&=\eta^{\mu\nu}p_\mu p_\nu-2\pi_u\pi_v.
\end{aligned}
$$

Ihre kanonischen Poisson-Klammern schließen exakt:

$$
\boxed{\{Q_{11},Q_{22}\}=4Q_{12}},\quad
\boxed{\{Q_{11},Q_{12}\}=2Q_{11}},\quad
\boxed{\{Q_{12},Q_{22}\}=2Q_{22}}.
$$

Das ist eine lokale $\mathrm{Sp}(2,\mathbb R)$-Zwangsalgebra in einem freien Weltlinienmodell. Wähle den Patch und die Eichbedingungen

$$
u=\ell\ne0,\qquad \pi_v=0.
$$

Die Bedingungen $Q_{11}=Q_{12}=0$ lösen sich dann algebraisch zu

$$
\boxed{v=\frac{x^2}{2\ell}},\qquad
\boxed{\pi_u=-\frac{x\cdot p}{\ell}}.
$$

Die verbleibende Zwangsgleichung reduziert sich auf

$$
\boxed{Q_{22}=p^2=0.}
$$

Da $du=0$ und $\pi_v=0$ auf diesem Eichschnitt, reduziert sich die kanonische Einsform

$$
p_\mu dx^\mu+\pi_u du+\pi_v dv
\quad\longrightarrow\quad p_\mu dx^\mu.
$$

Damit bleibt lokal gerade der reduzierte Phasenraum eines **masselosen 4D-Teilchens** mit einer Zeit übrig. Die Freiheitsgradzählung bestätigt:

$$
12-2\cdot3=6\quad\text{(6D mit drei erstklassigen Zwängen)};
\qquad 8-2\cdot1=6\quad\text{(masseloses 4D-Teilchen)}.
$$

**Status [ANALYTISCH BEWIESEN für diesen Patch].** Die algebraische Zwangschließung, die Eichlösung und die Übereinstimmung der reduzierten Phasenraumdimension sind exakt. Die verwendete Fixierung ist nicht global für alle möglichen Zustände und beweist weder Quanten-Unitarität noch Ghostfreiheit eines dynamischen 6D-Gravitationsfelds.

**Abgrenzung:** Die durch Bars untersuchte 2T-Feldgravitation enthält weitere Felder, Eich- und kinematische Nebenbedingungen. Wir dürfen seine Schlussfolgerungen deshalb **nicht** durch das bloße Aufschreiben der drei Weltlinien-Zwänge auf die HZT-M0-Einstein-Maxwell-Skalar-Wirkung übertragen.

# 7. Kontrolle der effektiven 4D-Gravitationsnormierung

Für die **einzeitige** S6-Metrik

$$
ds_6^2=e^{2A(y)}g_{\mu\nu}(x)dx^\mu dx^\nu+\gamma_{ab}(y)dy^a dy^b,
\qquad\gamma_{ab}>0,
$$

enthält der gekrümmte 6D-Skalar den Term $R_6\supset e^{-2A}R_4$. Gleichzeitig gilt $\sqrt{-g_6}=e^{4A}\sqrt{-g_4}\sqrt{\gamma_2}$. Daher

$$
\frac{M_6^4}{2}\int d^6X\sqrt{-g_6}\,R_6
\supset\frac{M_4^2}{2}\int d^4x\sqrt{-g_4}\,R_4
$$

mit

$$
\boxed{M_4^2=M_6^4\int d^2y\sqrt{\gamma_2}\,e^{2A(y)}}.
$$

Dimensionstest: $[M_6^4]=M^4$, $[d^2y]=M^{-2}$, also $[M_4^2]=M^2$. Die Formel ist nur sinnvoll bei endlichem, normalisierbarem Integral und bei einer geeigneten Spektralreduktion. Es handelt sich um den **bekannten Einzeit-Normalisierungskanal** und ausdrücklich nicht um eine 2T-zu-1T-Herleitung.

# 8. Warum emergente Zeit nicht automatisch zwei Zeiten bedeutet

Die Arbeit von Araújo-Regado, Thavanesan und Wall (2026) untersucht Cauchy-Slice-Holografie im de-Sitter-Raum. In dem spezifischen bottom-up-Modell ist die Bulk-Zeit eine emergente Dimension im Zusammenhang mit einer RG-Entwicklung. Dies legitimiert eine mathematische Prüfung, ob Raumzeitkoordinaten sekundär sind. **Es etabliert weder zwei unabhängige physikalische Zeitrichtungen noch unsere HZT-Full-Signatur.**

Eine Fundamentaltheorie ohne vorausgesetzte Metrik könnte hypothetisch einen Zustandsraum $\mathcal H$ und eine Rekonstruktionsabbildung

$$
\mathcal R:\big(\mathcal H,\rho,\text{Algebra},\text{Zwangsstruktur}\big)
\longrightarrow\big(\mathcal M_6,g_{(4,2)},\text{physikalische Sektoren}\big)
$$

besitzen. Dies ist gegenwärtig für UniverseLab eine **Definitionsskizze**, keine konstruierte Abbildung. Der anschließende Übergang $\mathcal P_{2T\to1T}$ müsste ebenfalls explizit hergeleitet werden. Ein Diagramm allein erfüllt keine der beiden Beweispflichten.

# 9. Falsifikations- und Entscheidungsmatrix

| ID | Prüfpflicht | Was derzeit tatsächlich vorliegt | Ergebnis |
|:--|:--|:--|:--|
| `SIG02-SRC` | Quellenidentität 1T/2T | Primär-Artefakte des einzeitigen M0-S6-Parents gelesen | **PASS für die Trennung** |
| `SIG02-ALG` | Trägheitssatz und Blockreduktion | Exakte Kongruenz-/Schur-Aussage, symbolisch und numerisch kontrolliert | **PASS für nichtentartete Blöcke** |
| `SIG02-KK` | Freier zeitartiger KK-Gegenmodus | Tachyonische $n\neq0$-Spektren im 2T-Toy | **PASS als Gegenbeispiel** |
| `SIG02-SP2` | Sp(2,R)-Schließung und lokaler Eichschnitt | Exaktes freies Weltlinienmodell mit 4D-Massenschale | **PASS nur für Toy** |
| `SIG02-PARENT` | Vollständige HZT-Full-2T-Wirkung | Im geprüften Scope nicht nachgewiesen | **OPEN** |
| `SIG02-RED` | Feldtheoretische 2T$\to$M0-S6-Abbildung | Keine explizite Projektion samt Kappe/Maxwell/Skalar | **BLOCKED/OPEN** |
| `SIG02-KIN` | Physikalische Hessian- und Ghostfreiheit | Kein on-shell-HZT-Full-Parent, keine gesamte reduzierte Kinetikmatrix | **OPEN** |
| `SIG02-QM` | Quanten-Hilbertraum, Unitarität und Cauchy-Problem | Nicht ermittelt; freie 2T-Wellengleichung problematisch ohne geeignete Nebenbedingungen | **OPEN** |
| `SIG02-GR` | GR-Grenzfall und normierte 4D-Nullmode | Normierungsformel für 1T bekannt, 2T-Projektion nicht definiert | **PARTIAL_1T_ONLY** |
| `SIG02-OBS` | Eindeutige Observablen HZT-Full zu M0 zu Daten | Keine geschlossene physikalische Forward-Map | **OPEN** |

**Keine Promotionsfolge:** Die PASS-Meldungen bezeichnen ausschließlich die jeweils angegebene beschränkte mathematische Identität. Sie dürfen nicht als Nachweis eines HZT-Full-Modells, einer numerisch gelösten Parentdynamik oder empirischer Unterstützung aufgefasst werden.

# 10. Reproduzierbarkeit und Gegenprüfung

Der Begleittest `2026-11-21_UniverseLab_SIG02_2TReductionChecks_v0.1.py` prüft neun kleine, unabhängig nachrechenbare Eigenschaften:

1. kanonische Sp(2,R)-Poisson-Algebra;
2. lokale 2T-Eichlösung;
3. Freiheitsgradzählung;
4. Determinante und Signatur des Diskus-Ansatzes;
5. Vorzeichen des lichtartigen 2T-Blocks;
6. Schur-Komplement und Inertia mit nichtverschwindender 4D/2D-Mischung;
7. tachyonisches zeitartiges KK-Gegenspektrum;
8. einzeitige Warp-Normierung des 4D-Einstein-Terms;
9. logisches Gegenbeispiel: positiver einzelner kinetischer Eintrag beweist keine positive gesamte Hessian-Signatur.

**Ausführung:** Python 3 / SymPy / NumPy, neun Tests bestanden. Die erste Kontrollausführung deckte eine fehlerhafte Indexidentifikation zwischen kontravarianten und kanonischen kovarianten Impulsen in der Testimplementierung auf; diese wurde vor dem erfolgreichen Testlauf korrigiert. Der Fehler und die Korrektur waren **Testkonvention**, keine Änderung der physikalischen Aussagen. Keine vollständige unabhängige Re-Implementierung der HZT-Gleichungen, kein physischer numerischer Solverlauf.

# 11. Erforderlicher nächster Beweisblock: 2T-01

**Vor Beginn einer quantengravitativen Rekonstruktion erforderlich:**

1. Eine **eigene**, versionierte HZT-Full-2T-Parent-Wirkung mit Signatur $(4+,2-)$, Volumenform, Feldinventar, Randquellen, Topologie und relevanten Nebenbedingungen angeben. Die S6-Einzeitwirkung darf nicht lediglich umbenannt werden.
2. Den Generatorensatz $Q_{ij}$ als funktionale, gegebenenfalls feldtheoretische Constraints explizit definieren und seine off-shell-Erstklassigkeit beziehungsweise Anomaliefreiheit unter spezifizierten Annahmen prüfen.
3. Eine Projektion $\mathcal P_{2T\to1T}$ konstruieren, deren Bild **genau** die dynamischen Feld- und Randbedingungen des HZT-M0-S6-Zweigs besitzt, nicht nur dieselbe Dimensionenzahl.
4. Nach Hintergrundlösung die volle zweite Variation einschließlich Gauge-, Skalar-, Vektor-, Tensor- und Cap-/Bending-Sektoren bestimmen; die nichtphysikalischen Freiheitsgrade entfernen und die physikalische Kinetik sowie Gradientenspektren prüfen.
5. Normierung der gravitativen Nullmode, Positivität des physikalischen Zustandsraums, Kausalität und zulässiges Cauchy-Problem zeigen.
6. Erst anschließend eine observablenfeste und datenprüfbare Forward-Map aufbauen.

**Statusentscheidung v0.1:** Der Quellennachweis für den einzeitigen M0-Zweig ist geschlossen (`SIG02-SRC=PASS_1T`). Eine vollständige HZT-Full-2T-Parentwirkung und ihre feldtheoretische Projektion bleiben `OPEN`. Die Hypothese eines fundamentalen HZT-Full mit zwei Zeiten wird damit nicht widerlegt; die direkte Gleichsetzung mit der bereits eingefrorenen Einzeit-Parentwirkung ist für diesen konkreten Vertrag **BLOCKIERT**.

# 12. Quellen und Primärliteratur

**UniverseLab / `main` (Abruf am 21.11.2026):**

- [SCI-001/002: Kanonische 6D-Parentwirkung](https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md)
- [S6-Parent-Aktionsvertrag, JSON](https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/hzt-s6-parent-action-v0.1.json)
- [Parent-ADM und D2N-Q-Recheck](https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/science/hzt-m0/md2s/2026-08-13_HZT-M0_S6_C-PHYS_ParentADM_D2NQ_Recheck_v0.1.md)
- [ULSH05: Readiness der quadratischen Wirkung](https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/registry/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.json)
- [R1: Quellenrekonstruktionsregister](https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/science/hzt-m0/md2s/R1_SOURCE_RECONSTRUCTION_LEDGER_v0.1.json)

**Originalarbeiten und methodische Literatur:**

1. Bars, I., lokale Phasenraum-Eichsymmetrien: [Phys. Rev. D 58 (1998) 106004](https://doi.org/10.1103/PhysRevD.58.106004) und [Phys. Rev. D 64 (2001) 045004](https://doi.org/10.1103/PhysRevD.64.045004).
2. Bars, I. (2008), *Gravity in 2T-Physics*, Phys. Rev. D 77, 125027: [Originalarbeit](https://doi.org/10.1103/PhysRevD.77.125027) / [Preprint](https://arxiv.org/abs/0804.1585).
3. Craig, W.; Weinstein, S. (2009), *On determinism and well-posedness in multiple time dimensions*: [Preprint](https://arxiv.org/abs/0812.0210). Die Autoren zeigen eine wohlgestellte ultrahyperbolische Cauchy-Aufgabe **unter nichtlokalen Einschränkungen**. Das freie Gegenbeispiel ist deshalb kein universelles Unmöglichkeitstheorem jeder 2T-Theorie.
4. Araújo-Regado, G.; Thavanesan, A.; Wall, A. C. (2026), *Holographic cosmology at finite time*, JHEP 04 (2026) 121: [Originalarbeit](https://doi.org/10.1007/JHEP04(2026)121).
5. Haynsworth-Additivität / Sylvester-Trägheitssatz: Standardresultat der Matrixalgebra; siehe [Darstellung, Abschnitt 6](https://ijmaa.in/index.php/ijmaa/article/download/1437/1397/2044).

---

**Governance-Schlussvermerk:** Dieses Dokument ist eine analytische, wiederholbare Arbeitsgrundlage. `main`, K1-D, K1-E, die physikalische Forward-Map und sämtliche Solver-/Grant-Zustände bleiben davon unberührt. Ein guter mathematischer Toy-Test ist kein HZT-Full-Beweis.