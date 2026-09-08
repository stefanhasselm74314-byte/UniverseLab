# UniverseLab — ULSH-05 / WP1C4B2C
## Global corner/support admissibility and physical boundary-domain preflight v0.1

**Datum:** 2026-09-08  
**Modellidentität:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `eab0866b80bbc21730c2af89b54d5ba177c5113a`  
**Klassifikation:** `ANALYTIC_NONOPERATIVE_GLOBAL_TANGENTIAL_CORNER_ADMISSIBILITY_AND_BOUNDARY_DOMAIN_PREFLIGHT`

## 0. Kernresultat

WP1C4B2B beweist eine lokale schwache Hessian-Symmetrie auf einem kompakten tangentialen Testbereich mit periodischer interner Richtung. Für die globale Domänenanalyse muss die bisherige Kurzschreibweise jedoch präzisiert werden.

Für ein randloses beziehungsweise nichtkompaktes \(M_4\) verwenden wir

\[
\mathcal D_0=
C_c^\infty(M_4)\otimes C^\infty_{2\pi}(S^1_\chi).
\]

Sobald stattdessen ein endlicher, randtragender Slab \(M_4\) eingeführt wird, lautet der sichere Testbereich

\[
\boxed{
\mathcal D_0=
C_c^\infty(\operatorname{int}M_4)
\otimes C^\infty_{2\pi}(S^1_\chi)
}
\]

mit

\[
\operatorname{supp}u\Subset \operatorname{int}M_4.
\]

Das heißt: die Störungen verschwinden in einer Umgebung des äußeren Randes. Bloßer „kompakter Support“ auf einer kompakten Mannigfaltigkeit **mit** Rand genügt nicht, weil dort jede glatte Funktion kompakt getragen sein kann, ohne verschwindenden Randtrace zu besitzen.

Der globale Green-/Hessian-Unterschied besitzt strukturell die Form

\[
\langle u,Lv\rangle-\langle Lu,v\rangle
=
\int_{\partial\Omega}\mathcal B[u,v]
+
\sum_C \mathcal C_C[u,v].
\]

Daher ist eine globale Symmetrie- oder Selbstadjungiertheitsaussage erst zulässig, wenn auf dem tatsächlich deklarierten Bereich sämtliche äußeren Rand- und Cornerbeiträge verschwinden oder durch vollständig spezifizierte Rand-/Joint-Terme kompensiert werden.

**Ergebnis dieses Blocks**

`WP1_global_domain_preflight = COMPLETED_CONDITIONAL_NO_PHYSICAL_DOMAIN_RELEASE`

aber

`WP1_physical_boundary_domain = BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA`.

Damit wird keine globale physikalische Randdomäne freigegeben.

---

## 1. Ausgangslage aus WP1C4B2B

WP1C4B2B hat die lokalen linearen Randresiduen komponentisiert:

- metrischer/Israel-Kanal \(\Delta\mathcal R_h\),
- Skalar-Normalfluss \(\Delta\mathcal R_\phi\),
- Gauge-Normalfluss \(\Delta\mathcal R_A\),
- Kappenphasenresiduum \(\Delta\mathcal R_\sigma\),
- Shape-/Normalconstraint \(\Delta\mathcal R_\perp\).

Auf dem korrekt verstandenen lokalen Testbereich gilt

\[
H_\Sigma[u,v]=H_\Sigma[v,u].
\]

Der Beweis verwendet interior-kompakten tangentialen Support bei vorhandener äußerer Begrenzung beziehungsweise gewöhnlichen kompakten Support bei randlosem \(M_4\), zusammen mit \(\chi\)-Periodizität.

### Status

[BEWIESEN] Lokale schwache Hessian-Symmetrie auf dem präzisierten Testbereich.

[OFFEN] Globale physikalische Randbedingungen.

[OFFEN] Physikalische Selbstadjungiertheit, Spektrum, Hamilton-Positivität und Ghostfreiheit.

---

## 2. Geometrischer Rand des Interfaces

Für den im Parent-/Boundary-Vertrag verwendeten lokalen Interface-Typ

\[
\Sigma\simeq M_4\times S^1_\chi
\]

gilt wegen

\[
\partial S^1_\chi=\varnothing
\]

für eine endliche randtragende \(M_4\)-Region formal

\[
\partial\Sigma=(\partial M_4)\times S^1_\chi.
\]

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
\forall u,v\in\mathcal D(L).
\]

Mögliche Mechanismen sind:

1. Support kompakt innerhalb des Inneren der endlichen Region,
2. explizite Dirichlet- oder andere hinreichende Tracebedingungen,
3. kontrollierter asymptotischer Abfall,
4. eine fluxfreie gemischte Unterdomäne,
5. explizite Rand-/Joint-Terme, deren Variation den Rest kompensiert.

Welche dieser Möglichkeiten **physikalisch** zulässig ist, kann ohne etablierten Background und dessen Kausalstruktur nicht entschieden werden.

### Lorentz-Signatur-Firewall

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
\int_0^1\bigl(uLv-(Lu)v\bigr)\,dx
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

und damit

\[
\int_0^1uLv\,dx=-1,
\qquad
\left[-u\,v'+u'v\right]_0^1=-1.
\]

Also

\[
\boxed{
\langle u,Lv\rangle-\langle Lu,v\rangle=-1\neq0
}.
\]

[BEWIESEN] Die formale Symmetrie des Differentialausdrucks \(-d^2/dx^2\) genügt nicht für die Symmetrie eines globalen Operatorbereichs.

Dieser Zeuge schließt zugleich die zuvor zu grobe Formulierung „kompakter Support genügt auf einer endlichen Region“ aus: auf dem kompakten Intervall \([0,1]\) sind \(u=x\) und \(v=x^2\) kompakt getragen, besitzen aber keinen verschwindenden Randtrace. Für die D0-Kontrolle ist daher interior-kompakter Support oder eine explizite Tracebedingung erforderlich.

Wenn dagegen \(u=v=0\) an beiden Endpunkten gefordert wird, verschwindet derselbe Randkonkomitant.

---

## 5. Periodischer \(\chi\)-Kontrollfall

Für

\[
L_\chi=-\frac{d^2}{d\chi^2},
\qquad
\chi\in[0,2\pi],
\]

und

\[
u(\chi)=\sin\chi,\qquad
v(\chi)=\cos\chi
\]

gilt

\[
\left[-u\,v'+u'v\right]_{0}^{2\pi}=0.
\]

[BEWIESEN] Die \(2\pi\)-Periodizität schließt den \(\chi\)-Randkanal.

Sie sagt nichts über die nichtkompakten oder endlichen äußeren \(M_4\)-Ränder.

---

## 6. Kandidatendomänen

### D0 — lokaler analytischer Testbereich

Randloses/nichtkompaktes \(M_4\):

\[
\mathcal D_0=C_c^\infty(M_4)\otimes C^\infty_{2\pi}(S^1_\chi).
\]

Endliches randtragendes \(M_4\):

\[
\boxed{
\mathcal D_0=C_c^\infty(\operatorname{int}M_4)
\otimes C^\infty_{2\pi}(S^1_\chi)
}.
\]

Status:

`PROVEN_ANALYTIC_TEST_DOMAIN`

[BEWIESEN] Auf diesem präzisierten Bereich verschwinden die betreffenden äußeren tangentialen Beiträge durch interior-kompakten Support beziehungsweise bei randlosem \(M_4\) gewöhnlichen kompakten Support; der \(\chi\)-Randterm verschwindet durch Periodizität.

[FIREWALL] \(\mathcal D_0\) ist kein physikalischer Randwertvertrag.

### D1 — endlicher Slab mit verschwindenden äußeren Variationen

Eine mathematisch hinreichende Fallback-Wahl wäre ein endlicher Slab, auf dessen äußerem Rand und an seinen Corners die zulässigen Variationen verschwinden.

Status:

`MATHEMATICALLY_SUFFICIENT_CONDITIONAL_FALLBACK_NOT_PHYSICAL_RELEASE`

Zusätzlich zu prüfen:

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

Die kanonische Parentwirkung enthält Cap-GHY-Terme und die lokalisierte Kappenwirkung. Sie friert jedoch keinen zusätzlichen äußeren vierdimensionalen Slab-Rand und keine daraus entstehenden globalen codimension-2 Joint-Terme ein.

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

Dieser Befund behauptet **nicht**, dass ein bestimmter zusätzlicher Joint-Term unabhängig von der später gewählten globalen Region bereits jetzt zwingend Teil der kanonischen Theorie sein müsse.

---

## 8. Warum die physikalische Domäne jetzt nicht fixiert werden darf

Aktuell gilt

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`.

Damit fehlen mindestens:

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

Ein zukünftiger \(\mathcal D_{\rm phys}\) muss mindestens:

1. \(2\pi\)-Periodizität in \(\chi\) erhalten,
2. Zwei-Seiten-Gluing am gemeinsamen Interface erhalten,
3. unter zulässigen Gauge-Transformationen abgeschlossen sein,
4. eine endliche quadratische Wirkung/Paarung besitzen,
5. den gesamten äußeren Rand- plus Corner-Greenfluss zum Verschwinden bringen oder durch eingefrorene Rand-/Joint-Terme kompensieren,
6. Endpunkte und asymptotische Grenzen explizit versionieren,
7. Operator und Domäne gemeinsam prüfen,
8. keine physikalische Randbedingung aus ΛCDM, C1-V-Manufactured-Verification oder Visualisierungsschichten importieren.

---

## 10. Dimensions- und Regimecheck

Dieser Block führt keinen neuen dimensionsbehafteten Kopplungsparameter ein.

Die Green-Identität vergleicht Terme derselben quadratischen Variationsordnung. Nach Einbezug des jeweiligen induzierten Maßes müssen Bulk-, Rand- und Cornerbeiträge dieselbe Wirkungsdimension besitzen.

Der eindimensionale Gegenzeuge ist ausschließlich ein dimensionsloser QA-Kontrollfall und trägt keine M1-Physik.

Regime:

- **randlos + kompakter Support:** analytisch geschlossen,
- **endlicher Rand + interior-kompakter Support:** analytisch geschlossen,
- **endlicher Rand + bloß kompakter Support:** nicht hinreichend,
- **periodisches \(\chi\):** Edge-Kanal geschlossen,
- **endlicher äußerer Slab mit physikalischen BC:** nur konditional,
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
\text{kompakter Support auf einem kompakten }M_4\text{ mit Rand}
\not\Rightarrow
\text{verschwindender Randtrace},
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

Der Vorgänger WP1C4B2B schreibt für den Fall, dass eine physikalische Domäne einen noch nicht freigegebenen Background benötigt, den fail-closed Fallback vor:

> nur eine konditionale S/V/T-Gauge- und Constraint-Reduktionsdomäne einfrieren, ohne Solverausführung.

Genau dieser Fall liegt vor.

Dieser Block vergibt bewusst **keine erfundene nachfolgende Work-Package-ID**. Der exakte Successor-Identifier wird erst in einem separaten Nachfolgevertrag kanonisch festgelegt.

Maximal zulässiger Abschlussstatus:

`GLOBAL_DOMAIN_PREFLIGHT_COMPLETE_PHYSICAL_DOMAIN_BLOCKED_BY_UNESTABLISHED_BACKGROUND_AND_UNFROZEN_OUTER_BOUNDARY_CORNER_DATA`
