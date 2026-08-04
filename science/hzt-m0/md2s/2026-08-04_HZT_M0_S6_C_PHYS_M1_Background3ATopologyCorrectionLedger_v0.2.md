# HZT-M0-S6-C-PHYS-M1 — Background-3A Topology Correction Ledger v0.2

**Datum:** 2026-08-04  
**Track:** `MD2S-R1-C-PHYS`  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Klassifikation:** `APPEND_ONLY_MODEL_IDENTITY_CORRECTION_NO_SOLVER_EXECUTION`

## 1. Gefundene Abweichung

Background-3A v0.1 führte als zukünftige topologische Run-Eingabe

```text
(N_F, m_N, m_S, n_N, n_S)
```

auf. Diese fünffache Regionalisierung ist im aktiven M1-Modell nicht definiert.

Die aktuelle Parentwirkung enthält eine einzige gemeinsame lokalisierte Kappenphase

\[
\sigma(\chi),
\qquad
D_a\sigma=\partial_a\sigma-q_\sigma A_a.
\]

Die beiden radialen Regionen \(N\) und \(S\) sind Bulk-Karten, die an derselben Kappe zusammengefügt werden. Sie tragen nicht automatisch zwei voneinander unabhängige lokalisierte Phasen.

## 2. Kanonischer diskreter Sektor

Freeze-1A und M1 definieren

\[
\boxed{
\mathcal T=(N_F,N_\sigma,m_\sigma)
}
\]

mit

\[
N_F\in\mathbb Z,
\qquad
N_\sigma\in\mathbb Z,
\qquad
m_\sigma\in\mathbb Z_{>0}.
\]

Dabei gilt

\[
q_\sigma=m_\sigma q_{\rm ref}
\]

und in dimensionslosen Größen

\[
q_{\rm ref}=\frac{\widehat q}{M_6}.
\]

Die eine eichinvariante Kappenkombination lautet

\[
\boxed{
d_\chi=N_\sigma-m_\sigma\widehat q\,a_{\chi,\Sigma}
}
\]

und die Winding-Anisotropie

\[
\widehat Y_\sigma
=
\widehat z_\sigma
\frac{d_\chi^2}{\ell_\Sigma^2}.
\]

Der unabhängige Bundle-/Fluxsektor wird durch

\[
R_{\rm patch}
=
a_{\chi,N}-a_{\chi,S}-\frac{N_F}{\widehat q}=0
\]

festgelegt. Patch- und Fluxbedingung werden weiterhin genau einmal gezählt.

## 3. Warum keine regionalen \(m_N,m_S,n_N,n_S\) zulässig sind

Die Einführung von

\[
(m_N,m_S,n_N,n_S)
\]

würde eine neue Theorie voraussetzen, beispielsweise

- zwei unabhängige lokalisierte Phasen \(\sigma_N,\sigma_S\),
- zwei getrennte Ladungen,
- zwei Winding-Terme,
- eine erweiterte lokalisierte Wirkung,
- neue Junction- und Gaugegleichungen,
- einen neu gezählten Randoperator.

Keine dieser Erweiterungen ist Teil von `HZT-M0-S6-C-PHYS-M1`.

Eine solche Theorie wäre nicht Background-3A v0.1 oder v0.2, sondern ein neues Modell mit eigener Parentwirkung und eigener Modell-ID.

## 4. Evidenz- und Ausführungswirkung

Die Abweichung wurde entdeckt

```text
vor Background-3B,
vor Auswahl eines Parameterpunkts,
vor Solverimplementierung,
vor Solverausführung,
vor einem numerischen Resultat.
```

Daher wurden keine numerischen Ergebnisse kontaminiert. Es existiert kein Hintergrundlauf, der wiederholt oder verworfen werden müsste.

Die Korrektur wirkt ausschließlich auf die zukünftige Run-Input-Spezifikation.

## 5. Was aus Background-3A v0.1 erhalten bleibt

Unverändert bleiben:

- die feste \(\tau\)-Karte,
- die vier regulären Profile pro Region,
- die acht kontinuierlichen Augmentierungsvariablen,
- die sechs externen M1-Modellkoeffizienten,
- die Kollokationsstufen \(24,32,48,64,96\),
- die Newton-/Trust-Region-Grenzen,
- die sieben deterministischen Seeds,
- alle Residual- und Konvergenzschwellen,
- die Positivitäts- und Admissibilitätsgates,
- die Pflicht zum unabhängigen Backend,
- die fail-closed Ergebnisklassen,
- die vollständige Evidence-Firewall.

Nur der topologische Eingabevektor wird ersetzt.

## 6. Effektiver Background-3A-Status

```text
BACKGROUND-3A = PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE
```

Dies bedeutet:

- Methodik ist vorregistriert.
- Topologieschema ist korrigiert und eingefroren.
- Ein konkreter Run-Input ist weiterhin nicht ausgewählt.
- Ein Solver ist weiterhin nicht autorisiert.

## 7. Anforderungen an Background-3B

Background-3B muss genau einen geordneten Sektor

\[
(N_F,N_\sigma,m_\sigma)
\]

festschreiben.

Es muss jeden Run-Input ablehnen, der regionale Ersatzgrößen

```text
m_N, m_S, n_N, n_S
```

enthält.

Auch Background-3B darf weiterhin keinen Solver ausführen.

## 8. Unveränderte Gates

```text
BACKGROUND_RUN_INPUT     = NOT_FROZEN
BACKGROUND_EXECUTION     = FORBIDDEN_PENDING_BACKGROUND_3B_AND_LATER_GATE
PHYSICAL_BACKGROUND      = NOT_ESTABLISHED
TRACE_RANK               = NOT_PROVEN
FREDHOLM_PROPERTY        = NOT_PROVEN
CONTINUUM_BVP_JACOBIAN   = NOT_PROVEN
R1.1                     = BLOCKED
R1.2                     = BLOCKED
OFFICIAL_MD2S_SOLVER     = NOT_AUTHORIZED
K1-D                     = NOT_RELEASED
K1-E                     = NOT_ADMISSIBLE
PHYSICAL_EVIDENCE_EFFECT = NONE
```
