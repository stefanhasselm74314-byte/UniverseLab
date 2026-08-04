# HZT-M0-S6-C-PHYS-M1 — Background-3B Run-Input Freeze Ledger v0.1

**Datum:** 2026-08-04  
**Track:** `MD2S-R1-C-PHYS`  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Block:** `C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY`  
**Status:** `RUN_INPUT_FROZEN_EXECUTION_NOT_AUTHORIZED`

## 1. Zweck und Grenze

Background-3B friert genau einen zukünftigen numerischen Run-Input ein. Der Block enthält:

- einen sechsparametrigen M1-Kontrollpunkt,
- einen kanonischen Ein-Kappen-Topologiesektor,
- einen festen Little-Hölder-Exponenten,
- einen deterministischen Siebener-Seed-Satz,
- eine Dependency-Lockdatei,
- kryptographische Payload-Hashes.

Der Block enthält ausdrücklich nicht:

- keine Solverimplementierung,
- keine Solverinitialisierung,
- keine nichtlineare Iteration,
- keinen Parameter- oder Topologiescan,
- kein numerisches Hintergrundprofil,
- keine Trace-Matrix,
- keine Rang-, Fredholm-, Existenz-, Eindeutigkeits- oder Stabilitätsaussage.

Die korrekte logische Reihenfolge bleibt

```text
Background-3A: Methode und QA vorregistrieren
Background-3B: exakt einen Run-Input einfrieren
Background-3C: Implementierung und Ausführung getrennt prüfen und gegebenenfalls autorisieren
```

## 2. Eingefrorener M1-Kontrollpunkt

Der geordnete Parametervektor lautet

\[
\boxed{
P_{\rm CP01}
=
\left(
\widehat\Lambda_6,
\widehat m_\phi^2,
a_F,
\widehat\lambda,
\widehat z_\sigma,
\widehat q
\right)
=
\left(1,1,\frac14,1,1,1\right).
}
\]

Die Wahl ist ein **ordnungs-eins rationaler Kontrollpunkt**. Sie wurde nicht gewonnen aus

- Beobachtungsdaten,
- einem Best Fit,
- dem historischen A0-Modell,
- dem C1-V-Verifikationsmodell,
- einem zufälligen oder adaptiven Parameterscan.

Sie ist deshalb weder physikalisch bevorzugt noch empirisch bestätigt.

Alle aktiven M1-Domänen sind erfüllt:

\[
\widehat m_\phi^2>0,
\qquad
a_F>0,
\qquad
\widehat z_\sigma>0,
\qquad
\widehat q>0.
\]

## 3. Dimensionale Recheneinheit

Für den dimensionslosen Run-Input wird

```text
M6 = 1 as dimensionless computational unit only
```

gesetzt. Dies bedeutet nicht

\[
M_6=1\;\text{GeV},
\]

oder irgendeinen anderen physikalischen Zahlenwert. Es folgt daraus weder eine vierdimensionale Planck-Normierung noch eine reale Längen-, Energie- oder Zeitskala.

Die spätere dimensionsvolle Rekonstruktion bleibt ein eigener 6D→4D-Normierungsblock.

## 4. Eingefrorener topologischer Sektor

Nach der append-only Background-3A-Korrektur ist der einzige zulässige Sektorvektor

\[
\boxed{
\mathcal T_{\rm CP01}
=(N_F,N_\sigma,m_\sigma)
=(1,1,1).
}
\]

Damit gilt

\[
q_\sigma=q_{\rm ref}
\]

nur deshalb, weil für diesen Run

\[
m_\sigma=1
\]

ausgewählt wurde. Es ist keine allgemeine Identität des Modells.

Die regionalisierten Bezeichnungen

```text
m_N, m_S, n_N, n_S
```

sind im M1-Run-Input unzulässig. Sie würden zwei unabhängige lokalisierte Phasen voraussetzen und damit eine neue Parentwirkung und Modell-ID erfordern.

## 5. Little-Hölder-Exponent

Für diesen Run wird

\[
\boxed{\alpha_H=\frac12}
\]

festgelegt. Dieser Exponent gehört zur funktionalanalytischen Regularitätsklasse

\[
h^{k,\alpha_H}([0,1])
\]

und ist nicht mit der physikalischen Kopplung \(a_F\) zu verwechseln.

Eine Änderung von \(\alpha_H\) benötigt einen neuen Run-Input und eine neue Hashkette.

## 6. Exakter Bulk-/Patch-Kontrollseed

Als Basis des deterministischen Seed-Satzes wird ein analytischer Kontrollseed am entkoppelten Randpunkt

\[
a_F=0
\]

verwendet. Dieser Randpunkt gehört nicht zum aktiven M1-Inneren, dient aber als algebraischer Kontrollzustand.

Definiert werden

\[
y_0=\frac{8-2\sqrt{10}}{3},
\]

\[
R_0=\frac{1}{\sqrt{y_0}},
\]

\[
q_0=\frac{y_0}{2}=\frac{4-\sqrt{10}}{3},
\]

\[
\rho_{N0}=\rho_{S0}=\frac{\pi R_0}{2},
\]

\[
k_{4,0}=\frac{1-q_0^2/2}{6}.
\]

Die Profile lauten

\[
A_N=A_S=0,
\qquad
\varphi_N=\varphi_S=0,
\]

\[
\ell_N(x)=\ell_S(x)=R_0\sin\left(\frac{x}{R_0}\right),
\]

\[
q_N=+q_0,
\qquad
q_S=-q_0,
\]

\[
a_{\chi,N}(x)=+q_0R_0^2\left[1-\cos\left(\frac{x}{R_0}\right)\right],
\]

\[
a_{\chi,S}(x)=-q_0R_0^2\left[1-\cos\left(\frac{x}{R_0}\right)\right].
\]

## 7. Exakte Identitäten des Kontrollseeds

Es gilt

\[
3y_0^2-16y_0+8=0,
\]

\[
y_0=\frac12+\frac34q_0^2,
\]

und

\[
2q_0R_0^2=1=\frac{N_F}{\widehat q}.
\]

Daraus folgen bei \(a_F=0\):

- sämtliche vier Bulkgleichungen in beiden Regionen verschwinden exakt,
- der radiale Constraint verschwindet exakt,
- \(R_A,R_\ell,R_\varphi,R_{\rm patch},R_{\rm scalar}\) verschwinden exakt.

Insbesondere erfüllt der Seed die Patchbedingung

\[
a_{\chi,N}(\rho_N)-a_{\chi,S}(\rho_S)
=1
=\frac{N_F}{\widehat q}.
\]

## 8. Zwingend sichtbare Kappendefekte

Der Seed ist keine vollständige Lösung. Im südlichen regulären Patch gilt

\[
d_\chi=\frac32,
\]

und

\[
\widehat Y_\sigma=\frac{9y_0}{4}.
\]

Die drei bewusst nicht verschwindenden Residuen sind

\[
\boxed{R_{4d}=1+\frac{9y_0}{8}},
\]

\[
\boxed{R_\chi=1-\frac{9y_0}{8}},
\]

\[
\boxed{R_{\rm gauge}=-\frac{3y_0}{2}}.
\]

Numerisch ungefähr:

```text
y0       ≈ 0.5584815599
R_4d     ≈ 1.6282917549
R_chi    ≈ 0.3717082451
R_gauge  ≈ -0.8377223398
```

Diese Größen dürfen weder verborgen noch als Rundungsfehler bezeichnet werden. Die korrekte Klassifikation lautet

```text
EXACT_BULK_AND_PATCH_SEED_BOUNDARY_INEXACT
```

und nicht `BACKGROUND_SOLUTION`.

## 9. Deterministischer Siebener-Seed-Satz

Die sieben Seed-Multiplikatoren bleiben in der in Background-3A festgelegten Reihenfolge

```text
0, +1/8, -1/8, +1/4, -1/4, +1/2, -1/2.
```

Sie wirken mit einer festen Gesamtamplitude \(1/20\) auf eine vorab definierte Profil- und Augmentierungsrichtung.

Es werden keine Zufallszahlen verwendet. Nachträgliche Seeds sind unter derselben Seed-Set-ID verboten. Konvergieren später mehrere getrennte Kandidaten, müssen alle erhalten und berichtet werden.

Der Seed-Satz ist durch

```text
b6e4319cc29736799a0b46320002e51cd17b70b724a6b4c6e86567a316996161
```

gebunden.

## 10. Dependency- und Run-Payload-Hashes

Die gewählte Reproduktionsumgebung wird als Method-Pin festgelegt:

```text
numpy==2.1.3
scipy==1.14.1
sympy==1.13.3
mpmath==1.3.0
```

Diese Versionen werden nicht als jeweils neueste Versionen behauptet.

Hash der Lockdatei:

```text
4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f
```

Hash des vollständigen kanonischen Run-Payloads:

```text
625118d21d70fb563c310e985ba83126a18b8680278b7b11908c1bc550f79536
```

Jede Änderung eines Parameters, Sektors, Exponenten, Seeds oder Dependencies erzeugt einen neuen Run-Input mit neuer ID und neuen Hashes.

## 11. Warum keine Homotopie in Background-3B ergänzt wird

Der quarantänisierte PR #47 enthielt zusätzlich eine konkrete Homotopie in \(a_F\). Diese wird nicht in Background-3B übernommen, weil Background-3A v0.1 bereits die numerische Methode eingefroren hat.

Eine neue Homotopie wäre eine Methodenänderung und müsste daher zuerst als neue Background-3A-Version vorregistriert werden. Background-3B darf nur Eingabedaten einfrieren, nicht die Methodik nachträglich erweitern.

Der analytische \(a_F=0\)-Zustand wird deshalb ausschließlich als deterministischer Initial-Seed dokumentiert.

## 12. Ausführungsstatus

```text
run input              = FROZEN_CP01
solver implementation  = NOT_PRESENT
solver initialization  = false
solver execution       = false
background candidate   = false
physical background    = NOT_ESTABLISHED
```

## 13. Unveränderte Gates

```text
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

## 14. Nächster zulässiger Block

```text
C-PHYS-R1.0-BACKGROUND-3C_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE
```

Background-3C darf eine quarantänisierte Solverimplementierung definieren und prüfen. Eine tatsächliche Ausführung benötigt weiterhin eine separate, versionierte Autorisierungsentscheidung. Der eingefrorene CP01-Run-Input löst keine automatische Ausführung aus.
