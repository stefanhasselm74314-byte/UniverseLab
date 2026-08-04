# HZT-M0-S6-C-PHYS-M1 — BACKGROUND-3A Preregistration Ledger v0.1

**Datum:** 2026-08-04  
**Track:** `MD2S-R1-C-PHYS`  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Block:** `C-PHYS-R1.0-BACKGROUND-3A`  
**Klassifikation:** `BACKGROUND_METHOD_PREREGISTRATION_NO_SOLVER_EXECUTION`  
**Evidenzwirkung:** `METHOD_DEFINITION_AND_CONTROL_SEED_DERIVATION_ONLY`  
**Physikalische Evidenzwirkung:** `NONE`

---

## 1. Ziel

Dieser Block friert **vor jeder numerischen Ausführung** genau einen reproduzierbaren Versuch zur Konstruktion eines M1-Kandidatenhintergrunds ein.

Er legt fest:

- einen Modellparameterpunkt,
- einen diskreten topologischen Sektor,
- einen analytisch hergeleiteten Kontrollseed,
- einen einzigen Homotopiepfad,
- einen primären und einen unabhängigen numerischen Backendtyp,
- Residual- und Fehlernormen,
- Konvergenzschwellen,
- und fail-closed Akzeptanzregeln.

Der Block führt keinen Solver aus und erzeugt kein Hintergrundresultat.

---

## 2. Festes Diagnosemodell

Der einzige in BACKGROUND-3A/3B zulässige Modellpunkt lautet

\[
\boxed{
(\widehat\Lambda,
 \widehat m_\phi^2,
 a_F,
 \widehat\lambda,
 \widehat z_\sigma,
 \widehat q)
=
\left(1,1,\frac14,1,1,1\right)
}
\]

mit diskretem Sektor

\[
\boxed{
(N_F,N_\sigma,m_\sigma)=(1,1,1)
}.
\]

Damit gilt

\[
q_\sigma=q_{\rm ref}.
\]

Die Wahl ist kein Fit und keine Behauptung besonderer physikalischer Wahrscheinlichkeit. Sie ist ein neuer, dimensionsloser O(1)-Diagnosepunkt mit rationalen Koeffizienten innerhalb aller aktiven M1-Domänen.

Der Ansatz

\[
M_6=1
\]

ist ausschließlich die bereits definierte dimensionslose Recheneinheit. Daraus wird kein physikalischer Wert für \(M_6\), \(M_4\) oder eine Observablennormalisierung abgeleitet.

---

## 3. Einziger Homotopiepfad

Nur die Bulk-Skalar-Flux-Kopplung wird über

\[
\boxed{a_F(h)=\frac h4},
\qquad
0\le h\le1
\]

fortgesetzt.

- \(h=0\): deklarierter Entkopplungskontrollpunkt außerhalb des Inneren des aktiven M1-Zweigs,
- \(h=1\): fester Zielpunkt.

Alle übrigen Modellparameter und alle drei ganzen Sektorlabels bleiben unverändert.

Die Ausgangsschrittfolge ist

\[
h_j=\frac j{16},
\qquad j=0,\ldots,16.
\]

Ein fehlgeschlagener Schritt darf nur deterministisch halbiert werden. Die minimale Schrittweite ist

\[
\Delta h_{\min}=\frac1{256}.
\]

Danach gilt zwingend

```text
NO_ACCEPTED_CANDIDATE
```

und nicht Parameteranpassung, Sektorwechsel oder zufälliger Neustart.

---

## 4. Herleitung des Kontrollseeds

Für \(h=0\), also \(a_F=0\), betrachten wir den symmetrischen Bulkansatz

\[
A_N=A_S=0,
\qquad
\varphi_N=\varphi_S=0,
\]

\[
\ell_N(x)=\ell_S(x)=R_0\sin\frac{x}{R_0}.
\]

Die beiden regionalen Fluxkonstanten werden entgegengesetzt gewählt:

\[
q_N=+q_0,
\qquad
q_S=-q_0.
\]

Die Kappositionen liegen am Äquator des Seedprofils:

\[
\rho_N=\rho_S=\frac{\pi R_0}{2}.
\]

### 4.1 Patchquantisierung

Die Gaugeprofile sind

\[
a_{\chi,N}(x)
=+q_0R_0^2\left(1-\cos\frac{x}{R_0}\right),
\]

\[
a_{\chi,S}(x)
=-q_0R_0^2\left(1-\cos\frac{x}{R_0}\right).
\]

Am Kap gilt daher

\[
a_{\chi,N}(\rho_N)-a_{\chi,S}(\rho_S)
=2q_0R_0^2.
\]

Für

\[
N_F=1,
\qquad
\widehat q=1
\]

muss dieser Ausdruck eins sein. Mit

\[
y_0\equiv R_0^{-2}
\]

folgt

\[
q_0=\frac{y_0}{2}.
\]

### 4.2 Bulkgleichungen

Bei \(A=\varphi=0\) und \(a_F=0\) ist

\[
\rho_F=\frac12 q_0^2.
\]

Die \(A\)-Gleichung reduziert sich auf

\[
-6k_{4,0}+1-\frac12q_0^2=0,
\]

also

\[
k_{4,0}=\frac{1-q_0^2/2}{6}.
\]

Da

\[
\frac{\ell''}{\ell}=-R_0^{-2}=-y_0,
\]

liefert die \(\ell\)-Gleichung

\[
y_0=\frac12+\frac34q_0^2.
\]

Mit \(q_0=y_0/2\) folgt

\[
3y_0^2-16y_0+8=0.
\]

Wir registrieren ausschließlich die kleine positive Wurzel

\[
\boxed{
y_0=\frac{8-2\sqrt{10}}3}
\]

und damit

\[
\boxed{
q_0=\frac{4-\sqrt{10}}3
}
\]

sowie

\[
R_0=y_0^{-1/2},
\qquad
k_{4,0}=\frac{1-q_0^2/2}{6}.
\]

Numerisch nur zur Orientierung:

\[
y_0\approx0.5584815599,
\]

\[
q_0\approx0.2792407799,
\]

\[
k_{4,0}\approx0.1601687156.
\]

Diese Dezimalwerte sind nicht die kanonische Definition; kanonisch sind die exakten Radikalausdrücke.

---

## 5. Was der Seed exakt erfüllt

Für beide Regionen gelten exakt

\[
E_A=E_\ell=E_\varphi=E_{\rm gauge}=0,
\]

und

\[
C_{rr}=0.
\]

Außerdem gelten am gemeinsamen Seedkap

\[
R_A=R_\ell=R_\varphi=R_{\rm patch}=R_{\rm scalar}=0.
\]

Insbesondere ist

\[
a_{\chi,N}(\rho_N)=+\frac12,
\qquad
 a_{\chi,S}(\rho_S)=-\frac12,
\]

sodass

\[
R_{\rm patch}
=rac12-\left(-\frac12\right)-1=0.
\]

---

## 6. Was der Seed ausdrücklich nicht erfüllt

Im Südpatch ist

\[
d_\chi
=N_\sigma-m_\sigma\widehat q\,a_{\chi,S}(\rho_S)
=1-(-1/2)
=\frac32.
\]

Daraus folgt

\[
\widehat Y_\sigma
=\frac{\widehat z_\sigma d_\chi^2}{\ell_\Sigma^2}
=\frac94y_0.
\]

Da die Seedableitungen \(A'\) und \(\ell'\) am Äquator verschwinden, lauten die drei bewusst offenen Kapdefekte

\[
\boxed{
R_{4d}=1+\frac98y_0
}
\]

\[
\boxed{
R_\chi=1-\frac98y_0
}
\]

\[
\boxed{
R_{\rm gauge,local}=-\frac32y_0
}.
\]

Diese Defekte sind endliche, analytisch bekannte Startresiduen. Sie dürfen nicht als Rundungsfehler, Diskretisierungsfehler oder „fast gelöst“ bezeichnet werden.

Der Seed ist daher

```text
EXACT_BULK_AND_PATCH_SEED_BOUNDARY_INEXACT
```

und keine Hintergrundlösung.

---

## 7. Darstellung im festen \(\tau\)-Chart

Mit

\[
x_s=\rho_s\sqrt\tau
\]

ist

\[
\widehat L(\tau)
=\frac{2\sin(\pi\sqrt\tau/2)}{\pi\sqrt\tau}.
\]

Die stetige Fortsetzung ist

\[
\widehat L(0)=1.
\]

Daraus folgt

\[
u_\ell(\tau)
=\frac{\widehat L(\tau)-1}{\tau},
\]

mit

\[
u_\ell(0)=-\frac{\pi^2}{24}.
\]

Für die Gaugefunktionen gilt

\[
u_{g,N}(\tau)
=\frac{1-\cos(\pi\sqrt\tau/2)}{2\tau},
\]

\[
u_{g,S}(\tau)
=-\frac{1-\cos(\pi\sqrt\tau/2)}{2\tau},
\]

mit

\[
u_{g,N}(0)=+\frac{\pi^2}{16},
\qquad
u_{g,S}(0)=-\frac{\pi^2}{16}.
\]

Damit liegt der Seed exakt in der durch OPERATOR-2B eingefrorenen Polparitätsklasse.

---

## 8. Primärer Backendvertrag

Der primäre Backendtyp ist eine Chebyshev-Gauss-Lobatto-Kollokation auf den beiden getrennten Intervallen

\[
\tau_N,\tau_S\in[0,1].
\]

Pro Region werden die vier Chartfunktionen

\[
(u_A,u_\ell,u_\varphi,u_g)
\]

kollokiert. Hinzu kommen die acht augmentierten Größen

\[
(\varphi_{N0},q_N,A_{S0},\varphi_{S0},q_S,\rho_N,\rho_S,k_4).
\]

Für Polynomgrad \(N\) ist das System diskret quadratisch:

\[
8(N+1)+8
\]

Unbekannte und ebenso viele regularisierte Bulk- plus Kapresiduen.

Die Homotopie wird bei \(N=32\) ausgeführt. Am Zielpunkt folgen unverändert

\[
N=48,64,96.
\]

Die Jacobi-Matrix wird ausschließlich per komplexem Schritt auf der analytischen Residualabbildung gebildet. Der Newtonschritt wird per SVD gelöst und durch eine deterministische Backtrackingfolge gedämpft.

---

## 9. Unabhängiger Backendvertrag

Der unabhängige Backendtyp verwendet nicht das \(	au\)-Kollokationssystem, sondern

- die physikalische dimensionslose Koordinate \(x_s\),
- die OPERATOR-2A-Polreihen bis \(A_4,\ell_5,\varphi_4,a_{\chi,4}\),
- DOP853-Integration,
- und eine zentrierte Finite-Differenzen-Jacobi-Matrix für die acht Kapresiduen.

Die Polcutoffs sind fest

\[
10^{-3},
\quad 5\times10^{-4},
\quad 2.5\times10^{-4}.
\]

Dieser Backendvergleich ist numerische QA. Er ist keine unabhängige physikalische Bestätigung.

---

## 10. Normen

Neben sämtlichen Rohresiduen wird für jede Gleichung ein komponentenweiser Rückwärtsfehler berechnet:

\[
\epsilon_i
=
\frac{|F_i|}
{1+\sum_j|T_{ij}|},
\]

wobei \(T_{ij}\) die additiven Terme derselben Gleichung sind.

Dasselbe Prinzip wird auf alle acht Kapresiduen und auf den regularisierten Constraint angewendet.

Zusätzlich werden ausgewiesen:

- Profilunterschiede zwischen Auflösungen,
- Unterschiede der acht augmentierten Parameter,
- Chebyshev-Tailnormen,
- vollständige Singularwertspektren,
- und Pole-Cutoff-Konvergenz.

---

## 11. Fail-closed Akzeptanz

Ein späteres Resultat darf nur dann

```text
NUMERICAL_BACKGROUND_CANDIDATE_DIAGNOSTIC
```

heißen, wenn **alle** im Vertrag registrierten Bedingungen gemeinsam erfüllt sind.

Insbesondere:

```text
h=1 erreicht                                      erforderlich
primärer normierter Bulkfehler N=96 <= 1e-9      erforderlich
primärer normierter Kapfehler N=96 <= 1e-10      erforderlich
normierter Constraint N=96 <= 1e-8               erforderlich
Spektraltail N=96 <= 1e-9                         erforderlich
Profiländerung N64->N96 <= 2e-6                   erforderlich
Parameteränderung N64->N96 <= 2e-7                erforderlich
unabhängiger Backend vollständig konvergiert      erforderlich
Backend-Profilübereinstimmung <= 5e-5             erforderlich
Backend-Parameterübereinstimmung <= 1e-5          erforderlich
```

Ein einziger Fehlschlag erzeugt

```text
NO_ACCEPTED_CANDIDATE
```

und keinen teilweise akzeptierten Hintergrund.

---

## 12. Keine Ausführung in BACKGROUND-3A

In diesem Block werden nicht ausgeführt:

- die Schließung des \(h=0\)-Kap-BVP,
- die Homotopie,
- Newton-Iterationen,
- Auflösungsverfeinerung,
- Multiple Shooting,
- Trace-Rangberechnung,
- Kernel- oder Kokernelanalyse,
- Stabilitätsrechnung,
- oder Observablenabbildung.

Der Status bleibt

```text
METHOD_PREREGISTERED_EXECUTION_NOT_AUTHORIZED
```

---

## 13. Gate-Stand

```text
BACKGROUND_3A                         = PASS_METHOD_PREREGISTRATION_PENDING_CI
BACKGROUND_3B                         = NOT_STARTED
diagnostic candidate execution       = NOT_AUTHORIZED_IN_THIS_BLOCK
physical background                  = NOT_ESTABLISHED
background existence                 = NOT_PROVEN
background uniqueness                = NOT_PROVEN
full boundary-trace rank              = NOT_PROVEN
Fredholm property                     = NOT_PROVEN
continuum BVP Jacobian                = NOT_PROVEN
perturbative stability                = OPEN
ghost freedom                         = OPEN
official MD-2S solver                 = NOT_AUTHORIZED
R1.1                                  = BLOCKED
R1.2                                  = BLOCKED
K1-D                                  = NOT_RELEASED
K1-E                                  = NOT_ADMISSIBLE
physical evidence effect              = NONE
```

---

## 14. Exakt nächster Block

Nach grünem BACKGROUND-3A-Vertrag ist der nächste mögliche Block

```text
C-PHYS-R1.0-BACKGROUND-3B
```

Dieser darf die präregistrierte Konstruktion nur unter diagnostischer Quarantäne ausführen. Eine separate versionierte Ausführungsentscheidung ist erforderlich. Der offizielle MD-2S-Solver bleibt auch dann `NOT_AUTHORIZED`.
