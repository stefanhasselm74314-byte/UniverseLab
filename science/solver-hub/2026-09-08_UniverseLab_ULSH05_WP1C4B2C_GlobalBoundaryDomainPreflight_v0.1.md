# UniverseLab — ULSH-05 / WP1C4B2C
## Global corner/support admissibility and physical boundary-domain preflight v0.1

**Datum:** 2026-09-08  
**Modellidentität:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `eab0866b80bbc21730c2af89b54d5ba177c5113a`  
**Klassifikation:** `ANALYTIC_NONOPERATIVE_GLOBAL_TANGENTIAL_CORNER_ADMISSIBILITY_AND_BOUNDARY_DOMAIN_PREFLIGHT`

## 0. Kernresultat

Der in WP1C4B2B bewiesene lokale schwache Symmetriesatz gilt auf dem dort deklarierten Testbereich

\[
\mathcal T_\Sigma =
C_c^\infty(M_4)\otimes C^\infty_{2\pi}(S^1_\chi),
\]

also für glatte Störungen mit kompaktem Support in den vier nichtkompakten tangentialen Richtungen und \(2\pi\)-Periodizität in \(\chi\).

Dieser Testbereich beseitigt per Konstruktion die tangentialen Rand- und Cornerterme der lokalen schwachen Paarung. Er ist **kein** physikalisch freigegebener Randwertbereich.

Der globale Green-/Hessian-Unterschied besitzt strukturell die Form

\[
\langle u,Lv\rangle-\langle Lu,v\rangle
=
\int_{\partial\Omega}\mathcal B[u,v]
+
\sum_C \mathcal C_C[u,v].
\]

Daher ist eine globale Symmetrie- oder Selbstadjungiertheitsaussage erst dann zulässig, wenn für den tatsächlich deklarierten globalen Bereich sämtliche äußeren Rand- und Cornerbeiträge verschwinden oder durch eine vollständig spezifizierte Rand-/Joint-Wirkung kompensiert werden.

**Ergebnis dieses Blocks**

`WP1_global_domain_preflight = COMPLETED_CONDITIONAL_NO_PHYSICAL_DOMAIN_RELEASE`

aber

`WP1_physical_boundary_domain = BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA`.

Damit wird die globale physikalische Randdomäne **nicht** freigegeben.

---

## 1. Ausgangslage aus WP1C4B2B

WP1C4B2B hat die lokalen linearen Randresiduen komponentisiert:

- metrischer/Israel-Kanal \(\Delta\mathcal R_h\),
- Skalar-Normalfluss \(\Delta\mathcal R_\phi\),
- Gauge-Normalfluss \(\Delta\mathcal R_A\),
- Kappenphasenresiduum \(\Delta\mathcal R_\sigma\),
- Shape-/Normalconstraint \(\Delta\mathcal R_\perp\).

Außerdem gilt für die zweite Variation der kanonischen Wirkung auf \(\mathcal T_\Sigma\)

\[
H_\Sigma[u,v]=H_\Sigma[v,u].
\]

Der Beweis benutzt ausdrücklich kompakten tangentialen Support und \(\chi\)-Periodizität. Deshalb folgt daraus nicht automatisch eine Aussage für einen globalen physikalischen Störungsraum.

### Status

[BEWIESEN] Lokale schwache Hessian-Symmetrie auf \(\mathcal T_\Sigma\).

[OFFEN] Globale physikalische Randbedingungen.

[OFFEN] Physikalische Selbstadjungiertheit, Spektrum, Hamilton-Positivität und Ghostfreiheit.

---

## 2. Geometrischer Rand des Interfaces

Für den im Parent-/Boundary-Vertrag verwendeten lokalen Interface-Typ

\[
\Sigma \simeq M_4\times S^1_\chi
\]

gilt wegen

\[
\partial S^1_\chi=\varnothing
\]

formal

\[
\partial\Sigma
=
(\partial M_4)\times S^1_\chi
\]

sofern \(M_4\) als endliche Region mit äußerem Rand betrachtet wird.

Für ein nichtkompaktes \(M_4\) ist statt eines endlichen \(\partial M_4\) ein asymptotischer Grenzfluss zu kontrollieren.

Die Periodizität in \(\chi\) beseitigt daher nur den \(\chi\)-Edge-Kanal. Sie legt keine zeitlichen, räumlich-asymptotischen oder radiativen Bedingungen in \(M_4\) fest.

---

## 3. Green-Identität und globale Domänenfrage

Sei \(L\) der aus der quadratischen Wirkung abgeleitete linearisierte Operator. Für zwei zulässige Störungen \(u,v\) lautet die globale Green-Struktur schematisch

\[
\mathfrak G[u,v]
:=
\langle u,Lv\rangle-\langle Lu,v\rangle
=
\int_{\partial\Omega}\mathcal B_\Omega[u,v]
+
\sum_{C\subset\partial\Omega}\mathcal C_C[u,v].
\]

Dabei bezeichnet

- \(\mathcal B_\Omega\) den äußeren Randkonkomitanten,
- \(C\) mögliche codimension-2 Schnittmengen/Corner,
- \(\mathcal C_C\) den zugehörigen Joint-/Cornerbeitrag.

Für einen global symmetrischen Operatorbereich \(\mathcal D(L)\) muss mindestens gelten

\[
\mathfrak G[u,v]=0
\qquad
\forall\,u,v\in\mathcal D(L).
\]

Dies kann durch verschiedene Mechanismen geschehen:

1. kompakter Support,
2. Dirichlet- oder andere hinreichende Randbedingungen,
3. asymptotischen Abfall,
4. eine fluxfreie gemischte Unterdomäne,
5. explizite Rand-/Joint-Terme, deren Variation den Rest kompensiert.

Welche dieser Möglichkeiten **physikalisch** zulässig ist, kann ohne etablierten Background und dessen Kausalstruktur nicht entschieden werden.

### Wichtige Lorentz-Signatur-Firewall

Die Bedingung

\[
\mathfrak G[u,v]=0
\]

ist für sich allein **kein** Beweis einer Hilbertraum-Selbstadjungiertheit eines Lorentzschen hyperbolischen Operators. Ebenso folgt daraus weder

- Hamilton-Positivität,
- kinetische Positivität,
- Ghostfreiheit,
- ein reelles physikalisches Spektrum,
- noch die Existenz eines physischen Backgrounds.

---

## 4. Exakter Gegenzeuge gegen den Evidenzsprung

Betrachte auf \([0,1]\)

\[
L=-\frac{d^2}{dx^2}.
\]

Dann gilt

\[
\int_0^1
\bigl(uLv-(Lu)v\bigr)\,dx
=
\left[-u\,v'+u'v\right]_0^1.
\]

Wähle

\[
u(x)=x,\qquad v(x)=x^2.
\]

Dann ist

\[
Lu=0,\qquad Lv=-2,
\]

und daher

\[
\int_0^1uLv\,dx
=
-2\int_0^1x\,dx
=
-1.
\]

Der Randterm ist ebenfalls

\[
\left[-u\,v'+u'v\right]_0^1=-1.
\]

Also

\[
\boxed{
\langle u,Lv\rangle-\langle Lu,v\rangle=-1\neq0
}
\]

auf dem unbeschränkten glatten Funktionsraum.

[BEWIESEN] Die formale Symmetrie des Differentialausdrucks \( -d^2/dx^2 \) genügt nicht für die Symmetrie eines globalen Operatorbereichs.

Wenn dagegen \(u=v=0\) an beiden Endpunkten gefordert wird, verschwindet derselbe Randkonkomitant. Die Operatoraussage hängt also wesentlich von der Domäne ab.

---

## 5. Periodischer \(\chi\)-Kontrollfall

Für

\[
L_\chi=-\frac{d^2}{d\chi^2},
\qquad
\chi\in[0,2\pi],
\]

und periodische Funktionen

\[
u(\chi)=\sin\chi,\qquad
v(\chi)=\cos\chi
\]

gilt

\[
\left[-u\,v'+u'v\right]_{0}^{2\pi}=0.
\]

[BEWIESEN] Die \(2\pi\)-Periodizität schließt den \(\chi\)-Randkanal.

Sie sagt jedoch nichts über die nichtkompakten oder endlichen äußeren \(M_4\)-Ränder.

---

## 6. Kandidatendomänen

### D0 — lokaler Testbereich

\[
\mathcal D_0=
C_c^\infty(M_4)\otimes C^\infty_{2\pi}(S^1_\chi).
\]

Status:

`PROVEN_ANALYTIC_TEST_DOMAIN`

[BEWIESEN] Auf diesem Bereich verschwinden die in WP1C4B2B ausgeschlossenen tangentialen Edge-/Cornerbeiträge durch kompakten Support und Periodizität.

[FIREWALL] \(\mathcal D_0\) ist kein physikalischer Randwertvertrag.

### D1 — endlicher Slab mit verschwindenden äußeren Variationen

Eine mathematisch hinreichende Fallback-Wahl wäre ein endlicher äußerer Slab, auf dessen äußerem Rand und an seinen Corners die zulässigen Variationen verschwinden.

Status:

`MATHEMATICALLY_SUFFICIENT_CONDITIONAL_FALLBACK_NOT_PHYSICAL_RELEASE`

Diese Wahl ist nur zulässig, wenn zusätzlich geprüft wird:

- exakte Definition des äußeren Randes,
- Erhaltung durch zulässige Gauge-Transformationen,
- Kompatibilität mit Interface-Gluing,
- Differenzierbarkeit der Gesamtwirkung am Corner.

### D2 — asymptotischer Abfall

Status:

`NOT_SPECIFIED_BACKGROUND_DEPENDENT`

Ein physikalisch sinnvoller Abfall hängt vom asymptotischen Background, der Norm und dem Operatorsektor ab.

### D3 — fluxfreie gemischte/Robin-Unterdomäne

Status:

`TARGET_ONLY_REQUIRES_COMPONENT_GREEN_FORM_AND_BACKGROUND`

Eine solche Domäne kann erst nach vollständiger komponentenweiser Globalisierung des Green-Konkomitanten und Background-Freeze ausgewählt werden.

### D4 — retardierte/ausgehende Bedingungen

Status:

`NOT_DEFINABLE_BEFORE_BACKGROUND_CAUSAL_STRUCTURE`

Retardiert, advanced oder outgoing sind kausale Begriffe. Ohne etablierten physischen Background ist die erforderliche Kausalstruktur nicht freigegeben.

---

## 7. Corner-/Joint-Preflight

Die kanonische Parentwirkung enthält die Cap-GHY-Terme und lokalisierte Kappenwirkung. Sie friert jedoch keinen zusätzlichen äußeren vierdimensionalen Slab-Rand und keine daraus entstehenden globalen codimension-2 Joint-Terme ein.

Wird später eine endliche Region \(\Omega\) mit äußerem Rand \(\partial\Omega\) gewählt, können Schnittmengen

\[
C=\Sigma\cap\partial\Omega
\]

entstehen.

Dann muss **eine** der folgenden Bedingungen explizit erfüllt werden:

1. Die zulässigen Variationen machen den Cornerbeitrag identisch null.
2. Eine kompatible äußere Rand- und Joint-Wirkung wird kanonisch eingefroren und ihre erste sowie zweite Variation neu hergeleitet.

Bis dahin lautet der Gap:

`MISSING_GLOBAL_CORNER_COMPLETION_OR_ZERO_VARIATION_CONDITION`

Wichtig: Dieser Befund behauptet **nicht**, dass ein bestimmter zusätzlicher Joint-Term bereits jetzt zwingend Teil der kanonischen Theorie sein müsse. Die Notwendigkeit hängt von der später gewählten globalen Region und Variationsklasse ab.

---

## 8. Warum die physikalische Domäne jetzt nicht fixiert werden darf

Aktuell gilt

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`.

Daher fehlen für eine physikalische Domänenwahl mindestens:

1. die reale Kausalstruktur des Backgrounds,
2. der kausale Typ möglicher äußerer Hypersurfaces,
3. ein freigegebener Cauchy-/Initialwertbereich,
4. asymptotische beziehungsweise Normalisierbarkeitsbedingungen,
5. gegebenenfalls retardierte/ausgehende Bedingungen,
6. ein eingefrorener globaler Corner-/Joint-Vertrag.

Folglich:

\[
\boxed{
\texttt{PHYSICAL\_BOUNDARY\_DOMAIN\_NOT\_FIXABLE\_BEFORE\_BACKGROUND\_CAUSAL\_STRUCTURE}
}
\]

Status: [FALSIFIZIERT/BLOCKIERT] für jede Behauptung, der gegenwärtige lokale Testbereich sei bereits die physikalische Störungsdomäne.

---

## 9. Invarianten eines späteren physikalischen Bereichs

Ein zukünftiger \(\mathcal D_{\rm phys}\) muss mindestens alle folgenden Bedingungen erfüllen:

1. \(2\pi\)-Periodizität in \(\chi\) erhalten.
2. Zwei-Seiten-Gluing am gemeinsamen Interface erhalten.
3. Zulässige Gauge-Transformationen bilden \(\mathcal D_{\rm phys}\) in sich ab.
4. Quadratische Wirkung/Paarung bleibt endlich.
5. Gesamter äußerer Rand- plus Corner-Greenfluss verschwindet oder wird durch eingefrorene Rand-/Joint-Terme kompensiert.
6. Endpunkte, asymptotische Grenzen und deren Regularität sind explizit versioniert.
7. Operator und Domäne werden gemeinsam geprüft; erst danach sind globale Symmetrie-/Spektralaussagen zulässig.
8. Keine physikalische Randbedingung wird aus ΛCDM, C1-V-Manufactured-Verification oder Visualisierungsschichten importiert.

---

## 10. Dimensions- und Regimecheck

Dieser Block führt keinen neuen dimensionsbehafteten Kopplungsparameter ein.

Die Green-Identität vergleicht Terme derselben quadratischen Variationsordnung; Rand- und Bulkseite besitzen nach Einbezug des induzierten Maßes dieselbe Wirkungsdimension.

Der eindimensionale Gegenzeuge wird ausschließlich als dimensionsloser QA-Kontrollfall verwendet und trägt keine M1-Physik.

Regime:

- **lokal/kompakter Support:** geschlossen durch WP1C4B2B + diesen Preflight,
- **periodisches \(\chi\):** geschlossen als Edge-Kanal,
- **endlicher äußerer Slab:** nur konditional,
- **räumlich/zeitlich asymptotisch:** offen,
- **retardiert/ausgehend:** blockiert bis Background/Kausalstruktur,
- **physisches Spektrum/Ghostanalyse:** blockiert.

---

## 11. Gate-State

| Gate | Status |
|---|---|
| WP1 boundary residual linearizations | `COMPONENTIZED_LOCAL_INTERFACE_OPERATOR` |
| WP1 local weak boundary Hessian | `SYMMETRIC_ON_DECLARED_TEST_DOMAIN` |
| WP1 global domain preflight | `COMPLETED_CONDITIONAL_NO_PHYSICAL_DOMAIN_RELEASE` |
| WP1 physical boundary domain | `BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA` |
| WP1 full global boundary Hessian | `NOT_CLOSED_PHYSICAL_DOMAIN_NOT_RELEASED` |
| WP1 full quadratic action | `NOT_CLOSED` |
| Perturbed junction system | `NOT_RELEASED` |
| Physical background | `NOT_ESTABLISHED` |
| FM-G0 | `OPEN` |
| AuthorizationDecision | `NOT_CREATED` |
| SingleUseGrant | `NOT_CREATED` |
| Backend import | `NOT_EXECUTED` |
| Solver execution | `NOT_EXECUTED` |
| Physical response rank | `NOT_EXECUTED` |
| K1-D | `NOT_RELEASED` |
| K1-E | `NOT_ADMISSIBLE` |
| Physical gate effect | `NONE` |
| Physical evidence effect | `NONE` |

---

## 12. Verbotene Schlussfolgerungen

\[
\text{lokale schwache Symmetrie}
\not\Rightarrow
\text{globale physikalische Selbstadjungiertheit},
\]

\[
\text{verschwindender Green-Randterm auf }\mathcal D_0
\not\Rightarrow
\text{physikalische Randbedingungen},
\]

\[
\text{symmetrische quadratische Form}
\not\Rightarrow
\text{Ghostfreiheit},
\]

\[
\text{mathematisch zulässige Fallback-Domäne}
\not\Rightarrow
\text{physikalisch identifizierte Domäne}.
\]

Kein Backendimport, Solverlauf, Response-Rank-Lauf oder physikalischer Gate-Übergang wird durch diesen Block autorisiert.

---

## 13. Fortsetzung

Der Vorgänger WP1C4B2B schreibt für den Fall, dass eine physikalische Domäne einen noch nicht freigegebenen Background benötigt, ausdrücklich den Fallback vor:

> nur eine konditionale S/V/T-Gauge- und Constraint-Reduktionsdomäne einfrieren, ohne Solverausführung.

Genau dieser Fall liegt vor.

Dieser Block vergibt bewusst **keine erfundene nachfolgende Work-Package-ID**. Der exakte Successor-Identifier wird erst in einem separaten Nachfolgevertrag kanonisch festgelegt.

Maximal zulässiger Abschlussstatus:

`GLOBAL_DOMAIN_PREFLIGHT_COMPLETE_PHYSICAL_DOMAIN_BLOCKED_BY_UNESTABLISHED_BACKGROUND_AND_UNFROZEN_OUTER_BOUNDARY_CORNER_DATA`
