# HZT-M0-S6-C-PHYS-M1 — Background-3A Preregistration Ledger v0.1

**Datum:** 2026-08-04  
**Track:** `MD2S-R1-C-PHYS`  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Block:** `C-PHYS-R1.0-BACKGROUND-3A`  
**Status:** `PREREGISTERED_NOT_EXECUTED`

## 1. Ziel und strikte Grenze

Dieser Block definiert ausschließlich, **wie** ein zukünftiger numerischer Kandidatenhintergrund gesucht und geprüft werden darf. Er enthält:

- keine konkrete sechsparametrige M1-Instanz,
- keinen topologischen Run-Sektor,
- keine Solverausführung,
- kein numerisches Hintergrundprofil,
- keine Rang-, Fredholm-, Existenz-, Eindeutigkeits- oder Stabilitätsaussage.

Die Reihenfolge ist verbindlich:

```text
Background-3A: Methoden-Vorregistrierung
Background-3B: exakt einen Run-Input einfrieren
Background-3C: erst dann kontrollierte Ausführung erwägen
```

Damit ist ausgeschlossen, dass Parameter, Seeds, Netze oder Toleranzen nach Sichtung eines Resultats angepasst und anschließend als vorregistriert dargestellt werden.

## 2. Eingefrorenes mathematisches Objekt

Operator-2B definiert in beiden Regionen die feste Polkarte

\[
x_s=\rho_s y,\qquad \tau=y^2\in[0,1],
\]

mit

\[
A_s=A_{s0}+\tau u_{A,s},
\]

\[
\ell_s=\rho_s\sqrt\tau\,(1+\tau u_{\ell,s}),
\]

\[
\varphi_s=\varphi_{s0}+\tau u_{\varphi,s},
\]

\[
a_{\chi,s}=\tau u_{g,s}.
\]

Die acht kontinuierlichen Augmentierungsvariablen bleiben

\[
\xi=(\varphi_{N0},q_N,A_{S0},\varphi_{S0},q_S,\rho_N,\rho_S,k_4).
\]

Die sechs M1-Modellkoeffizienten

\[
P_{M1}=(\widehat\Lambda_6,\widehat m_\phi^2,a_F,\widehat\lambda,\widehat z_\sigma,\widehat q)
\]

sind **externe feste Koeffizienten eines Runs**. Sie sind keine Shooting-Variablen und dürfen während eines Runs nicht angepasst werden.

## 3. Warum Background-3A noch keine Parameterwerte auswählt

Eine konkrete Parameterinstanz wäre bereits eine zusätzliche Modell- beziehungsweise Suchentscheidung. Ohne getrennten Run-Input-Vertrag könnten folgende Driftarten auftreten:

1. erfolgreiche Parameterpunkte werden nachträglich bevorzugt;
2. fehlgeschlagene Punkte verschwinden aus dem Bericht;
3. topologische Sektoren werden still gewechselt;
4. Seed- und Toleranzänderungen werden mit dem ursprünglichen Run vermischt;
5. ein numerischer Kontrollpunkt wird irrtümlich als physikalisch abgeleitet beschrieben.

Deshalb legt Background-3A die vollständige Methodik fest, während Background-3B genau eine Parameter- und Topologieinstanz mit Hash einfrieren muss.

## 4. Primäre Diskretisierung

Vorregistriert ist Chebyshev-Lobatto-Kollokation in der regulären Variablen \(\tau\). Die regionalen Knotenzahlen sind fest:

```text
N = 24, 32, 48, 64, 96
```

Es gibt keine adaptive Auswahl nach Ergebnissichtung. Die Pole werden nicht durch singuläre Rohgleichungen behandelt, sondern durch die bereits eingefrorene affine Paritätskarte.

Die Bulkgleichungen werden an inneren Kollokationspunkten ausgewertet. Die acht globalen beziehungsweise Kappenresiduen schließen das augmentierte System.

Der radiale Einstein-Constraint \(C_{rr}\) ist aufgrund der in Operator-2A bewiesenen Identität kein zusätzliches Lösungsresiduum. Er bleibt ein unabhängiger QA-Kanal:

\[
\|C_{rr}\|_\infty\le 10^{-9}.
\]

## 5. Nichtlineares Verfahren

Als zukünftiger Kandidat ist ein gedämpftes Newton-Verfahren mit Trust Region vorregistriert. Der Begriff „Kandidat“ ist hier entscheidend: Background-3A autorisiert seine Ausführung noch nicht.

Festgelegt sind unter anderem:

- maximal 60 Newton-Schritte pro Netz,
- maximal 20 Backtracking-Schritte,
- Armijo-Parameter \(10^{-4}\),
- minimale Schrittlänge \(2^{-20}\),
- rank-revealing QR als primärer linearer Löser,
- SVD ausschließlich als diskrete Konditionsdiagnostik,
- fail-closed Abbruch bei Stagnation.

Ein Scheitern bedeutet ausschließlich:

```text
NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL
```

Es bedeutet nicht, dass das kontinuierliche M1-Modell keine Lösung besitzt.

## 6. Deterministische Seeds

Es werden sieben deterministische Seeds in festgelegter Reihenfolge zugelassen. Zufallsseeds und nachträglich ergänzte Seeds sind untersagt.

Die Amplitudenmultiplikatoren lauten:

```text
0, +1/8, -1/8, +1/4, -1/4, +1/2, -1/2
```

Die konkreten Seedkoeffizienten müssen aus dem späteren Run-Input-Hash deterministisch erzeugt werden. Dadurch kann kein Seed aufgrund seines beobachteten Erfolgs bevorzugt oder verborgen werden.

Konvergieren mehrere voneinander getrennte Kandidaten, müssen alle gespeichert und berichtet werden. Die Klassifikation lautet dann

```text
MULTIPLE_NUMERICAL_CANDIDATE_BACKGROUNDS_DIAGNOSTIC
```

und nicht „eindeutige Lösung“.

## 7. Vorregistrierte Akzeptanzschwellen

Ein zukünftiger Kandidat muss gleichzeitig erfüllen:

\[
\|F_{bulk}\|_\infty\le10^{-10},
\]

\[
\|B\|_\infty\le10^{-10},
\]

\[
\|C_{rr}\|_\infty\le10^{-9}.
\]

Für das feine Netzpaar \((64,96)\) gelten zusätzlich:

\[
\|u_{96}-u_{64}\|_\infty\le10^{-8},
\]

\[
\|\xi_{96}-\xi_{64}\|_\infty\le10^{-9}.
\]

Weiter müssen gelten:

- \(\rho_N,\rho_S\ge10^{-4}\),
- \(\ell>10^{-8}\) im offenen Inneren,
- \(\ell_{cap}>10^{-8}\),
- keine NaN- oder Inf-Werte,
- Ladungsgitter und Patchsektor exakt erfüllt,
- winding gate \(Y_\sigma\ge-10^{-12}\),
- abfallender Spektralschwanz mit maximalem Betrag unter \(10^{-9}\).

Ein einzelnes Netz kann niemals zur Akzeptanz genügen.

## 8. Unabhängiger Backend-Check

Für die Klassifikation `NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC` ist ein zweiter, separat implementierter Backend erforderlich.

Zulässig ist:

- eine vierte Ordnung Finite-Differenzen-Implementierung oder
- eine unabhängig kodierte Lobatto-Kollokation.

Die Residualassemblierung darf keinen gemeinsamen Quellcode mit dem Primärbackend verwenden. Die maximale Kandidatendistanz beträgt

\[
d_{backend}\le10^{-7}.
\]

Auch perfekte Backend-Übereinstimmung bedeutet nur numerische Kreuzprüfung. Sie ist keine unabhängige physikalische Bestätigung.

## 9. Ergebnislogik

Die möglichen Ergebnisse sind vorab festgelegt:

| Bedingung | Klassifikation |
|---|---|
| alle Gates bestanden | `NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC` |
| numerische Nullstelle, aber QA-Gate verletzt | `NUMERICAL_ROOT_REJECTED_BY_QA` |
| kein Seed konvergiert | `NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL` |
| mehrere getrennte Kandidaten bestehen | `MULTIPLE_NUMERICAL_CANDIDATE_BACKGROUNDS_DIAGNOSTIC` |
| Run-Input unvollständig | `NOT_EXECUTED_INPUT_CONTRACT_FAILURE` |

Keine dieser Klassen beweist:

- kontinuierliche Existenz,
- Eindeutigkeit,
- Fredholm-Eigenschaft,
- Invertierbarkeit des kontinuierlichen Jacobians,
- perturbative Stabilität,
- Ghostfreiheit,
- Beobachtungsverträglichkeit,
- physikalische Bestätigung der Hyperzeit-Theorie.

## 10. Warum der diskrete Jacobian nur diagnostisch bleibt

Ein späterer Run darf singuläre Werte und Konditionszahlen des diskreten Systems berichten. Selbst ein voller diskreter Rang impliziert jedoch nicht

\[
D\mathcal G[W_*]:\mathcal X\to\mathcal Y\times\mathbb R^8
\]

sei ein Fredholm-Isomorphismus. Für diese Aussage fehlen weiterhin:

- ein akzeptierter Kandidatenhintergrund,
- der an diesem Hintergrund ausgewertete kontinuierliche Operator,
- Kernel- und Cokernelanalyse,
- Indexkontrolle,
- Diskretisierungs-zu-Kontinuum-Konvergenz.

## 11. Gate-Wirkung dieses Blocks

```text
BACKGROUND-3A            = PREREGISTERED_NOT_EXECUTED
physical background      = NOT_ESTABLISHED
trace rank               = NOT_PROVEN
Fredholm property        = NOT_PROVEN
continuum Jacobian       = NOT_PROVEN
R1.1                     = BLOCKED
R1.2                     = BLOCKED
official solver          = NOT_AUTHORIZED
K1-D                     = NOT_RELEASED
K1-E                     = NOT_ADMISSIBLE
physical evidence effect = NONE
```

## 12. Exakt nächster zulässiger Schritt

```text
C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY
```

Background-3B darf genau eine sechsparametrige M1-Instanz, einen topologischen Sektor, \(\alpha_H\), den Seed-Set-Hash und die Software-/Dependency-Hashes einfrieren. Auch Background-3B darf den Solver noch nicht ausführen.
