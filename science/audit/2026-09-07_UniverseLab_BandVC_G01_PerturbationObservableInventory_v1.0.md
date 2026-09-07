# UniverseLab Band V-C · G01 Perturbation/Observable Inventory v1.0

**Datum:** 2026-09-07  
**Basis:** `main` `c3698b36860f7268a71ba259b36c64c105dd48a9`  
**Gap:** `UL-BVC-G01`  
**Status:** `[OFFEN/BLOCKIERT]` — echte fehlende Herleitung, kein Pointer-/Freshness-Defekt  
**Physischer Gate-/Evidenz-Effekt:** `NONE / NONE`

## 1. Ergebnis

Die repository-weite Provenienzprüfung findet **keine freigegebene HZT-M0-Perturbationsmap** für Wachstum, effektive Poisson-Antwort, Gravitations-Slip oder Lensing. Vorhanden sind:

1. ein reduzierter effektiver Bridge-**Hintergrund**;
2. explizite öffentliche Firewalls `UNRELEASED_GROWTH_MAP` und `UNRELEASED_LENSING_MAP`;
3. Tests dieser Verweigerungssemantik;
4. eine Solver-Roadmap, in der die eigentliche Perturbations- und Cosmology-Ableitung ausdrücklich noch als zukünftige Arbeit geführt wird.

Damit ist G01 wissenschaftlich **nicht** durch Statuspflege lösbar. Die fehlende Kette ist strukturell:

\[
\{\delta g_{AB},\delta\varphi,\delta T_{AB}\}_{6D}
\longrightarrow
\text{linearisierte Bulk- und Junction-Gleichungen}
\longrightarrow
\{\Phi,\Psi,\Delta_m\}_{4D}
\longrightarrow
\{\mu,\eta,\Sigma,D\}.
\]

## 2. Quellenbefund

### Band-V-C-Crosswalk

Für `UL-CLM-BRIDGE-UNRELEASED-OBSERVABLES-001` ist bereits kanonisch registriert:

- Claim: `VERIFIED_PRESENT`
- Gleichung/Herleitung: `MISSING_REQUIRED_LINK`
- Code: `BLOCKED_BY_UNRELEASED_MAP`
- Test: `VERIFIED_PRESENT`
- Daten: `NOT_APPLICABLE`
- Falsifikator/Gate: `VERIFIED_PRESENT`
- Evidence Scope: `FAIL_CLOSED_RELEASE_FIREWALL`

Die existierenden Tests belegen also korrekt die **Verweigerung** einer nicht hergeleiteten Map; sie belegen nicht die fehlende Physik selbst.

### ULSH-05 · PERTURBATION

Die Master-Build-Order führt ULSH-05 als `PREPARATORY_DERIVATION_ONLY` mit den noch offenen Arbeitspaketen:

1. vollständige quadratische Wirkung \(S^{(2)}\) herleiten;
2. gauge-invariante S/V/T-Variablen und Randbedingungen definieren;
3. Constraints eliminieren und gekoppelte Modengleichungen implementieren;
4. GR-/Kontrollgrenzen sowie Auflösungs- und Residualtests validieren.

Der Release-Gate lautet:

`GAUGE_CONTROLLED_QUADRATIC_PERTURBATION_SYSTEM_WITH_REPRODUCIBLE_MODE_EVOLUTION`.

### ULSH-10 · COSMO

ULSH-10 ist `BLOCKED_BY_FOUNDATIONAL_GATES`. Erst dort sind vorgesehen:

1. ratifizierte 6D→4D-Parameterabbildung;
2. Ableitung von Hintergrund-, Wachstums- und Lensing-Gleichungen;
3. Implementierung der Forward-Map zu \(H(z)\), Distanzen, \(f\sigma_8\), \(\mu\), \(\Sigma\), \(\eta\);
4. Kontrolle der K1-D-Identifizierbarkeitsvoraussetzungen.

Damit bestätigt die Roadmap selbst, dass die Observable-Map **noch nicht existiert**.

### Öffentliche/numerische Implementierung

Der kanonische Cosmology Engine verweigert Bridge-Growth mit `UNRELEASED_GROWTH_MAP`. Compare Safe zeigt für die Lensing-Größe ausdrücklich `Σ(a,k): nicht konstruiert` und liefert `UNRELEASED_LENSING_MAP`. Die GR-Identität `Σ=1` darf nicht als Bridge-Resultat übernommen werden.

## 3. Fehlstellenmatrix

| Erforderliches Glied | Befund |
|---|---|
| Effektiver Bridge-Hintergrund \(H(a)\) | `PRESENT_DIAGNOSTIC_ONLY` |
| Perturbations-Gauge und Gauge-Transformationen | `MISSING_REQUIRED_LINK` |
| HZT-Definition/Identifikation von \(\Phi,\Psi\) | `MISSING_REQUIRED_LINK` |
| HZT-Materievariable \(\Delta_m\) und Kopplung | `MISSING_REQUIRED_LINK` |
| 6D-Parent-Perturbationsvariablen | `MISSING_REQUIRED_LINK` |
| linearisierte 6D-Parent-Gleichungen | `MISSING_REQUIRED_LINK` |
| perturbierte Junction-/Randbedingungen | `MISSING_REQUIRED_LINK` |
| Constraint-Elimination / physischer Skalarsektor | `MISSING_REQUIRED_LINK` |
| 6D→4D perturbative Reduktion | `MISSING_REQUIRED_LINK` |
| \(\mu(k,a)\) | `MISSING_REQUIRED_LINK` |
| \(\eta(k,a)\) | `MISSING_REQUIRED_LINK` |
| \(\Sigma(k,a)\) | `MISSING_REQUIRED_LINK` |
| Bridge-Growth-Gleichung | `MISSING_REQUIRED_LINK` |
| gültiger \((k,a)\)-Bereich | `MISSING_REQUIRED_LINK` |
| Initialbedingungen / Modennormierung | `MISSING_REQUIRED_LINK` |
| ausführbare Perturbations-Forward-Map | `BLOCKED_BY_UNRELEASED_MAP` |
| unabhängige physische Perturbationsvalidierung | `MISSING_REQUIRED_LINK` |
| Datenbundle | G08, nicht G01 |
| Likelihood | G09, nicht G01 |

## 4. Reference-Only Observable Interface

Um die spätere Parent-Herleitung eindeutig falsifizierbar zu machen, wird nur die **Zielsprache** eingefroren.

### 4.1 Referenz-Gauge

Als 4D-Referenzkonvention:

\[
ds^2=-(1+2\Psi)dt^2+a^2(1-2\Phi)\delta_{ij}dx^i dx^j,
\]

mit Fourier-Konvention \(\nabla^2\to-k^2\).

Dies ist **keine** Aussage, dass diese Variablen bereits aus dem HZT-Parentsektor hergeleitet wurden.

### 4.2 Effektive Poisson-Antwort

Definition:

\[
-k^2\Psi
=4\pi G a^2\mu(k,a)\rho_m\Delta_m.
\]

Für HZT gilt derzeit:

\[
\mu_{\rm HZT}(k,a)=\texttt{NOT\_RELEASED}.
\]

### 4.3 Gravitations-Slip

Definition:

\[
\eta(k,a)=\frac{\Phi}{\Psi},
\qquad \Psi\neq0.
\]

Für HZT gilt derzeit:

\[
\eta_{\rm HZT}(k,a)=\texttt{NOT\_RELEASED}.
\]

### 4.4 Lensing-Antwort

Definition:

\[
-k^2(\Phi+\Psi)
=8\pi G a^2\Sigma(k,a)\rho_m\Delta_m.
\]

Für HZT gilt derzeit:

\[
\Sigma_{\rm HZT}(k,a)=\texttt{NOT\_RELEASED}.
\]

Aus den **Definitionen allein** folgt, wo \(\eta\) definiert ist:

\[
\Sigma(k,a)
=\frac{\mu(k,a)[1+\eta(k,a)]}{2}.
\]

Das ist eine algebraische Interface-Identität und **keine dynamische HZT-Vorhersage**.

### 4.5 GR-Kontrollgrenze

Die Werte

\[
\mu=1,\qquad \eta=1,\qquad \Sigma=1
\]

werden ausschließlich als `REFERENCE_GR_CONTROL_ONLY_NOT_BRIDGE_RESULT` geführt. Sie dürfen nicht auf die Bridge übertragen werden.

## 5. Referenz-Growth-Ziel — ausdrücklich konditional

Nur unter der zusätzlichen Referenzannahme von druckloser minimal gekoppelter Materie, Standard-Kontinuitäts-/Euler-Gleichungen und einer quasi-statischen Subhorizon-Reduktion ohne zusätzliche HZT-Quellen wäre in \(x=\ln a\):

\[
D''(x)
+\left[2+\frac{d\ln H}{d\ln a}\right]D'(x)
-\frac{3}{2}\Omega_m(a)\mu(k,a)D(x)=0.
\]

Diese Gleichung ist **nicht freigegeben für die Bridge**. Falls die spätere Parent-Reduktion zusätzliche Kräfte, Entropiequellen, nichtlokale Bulk-Antworten oder andere Materiekopplungen erzeugt, muss dieses Referenzziel ersetzt werden.

## 6. Was G01 tatsächlich schließen würde

Eine echte Closure verlangt mindestens:

1. freigegebenen Parent-Hintergrund und Materiekopplung;
2. vollständige Parent-Perturbation und Gauge-Struktur;
3. quadratische Wirkung oder äquivalente linearisierte Feldgleichungen;
4. perturbierte Junction-/Randbedingungen;
5. Constraint-Klassifikation und -Elimination;
6. kontrollierte 6D→4D-Reduktion samt Modennormierung;
7. Identifikation von \(\Phi,\Psi,\Delta_m\);
8. Herleitung von \(\mu,\eta,\Sigma\) und eventuellen Zusatzquellen;
9. freigegebenen \((k,a)\)-Bereich und Initialbedingungen;
10. kanonischen Code plus unabhängige numerische/analytische Kontrollen.

Bis dahin bleibt:

`UL-BVC-G01 = OPEN_BLOCKING`.

## 7. Firewalls

Unverändert:

- `FM-G0 = OPEN`
- `PHYSICAL_BACKGROUND = NOT_ESTABLISHED`
- `PHYSICAL_RESPONSE_RANK = NOT_EXECUTED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `RATIFIED_HUMAN_TRUST_ROOT = NOT_RATIFIED`
- `RUNTIME_ISSUANCE_BINDINGS = BLOCKED`
- `AuthorizationDecision = NOT_CREATED`
- `SingleUseGrant = NOT_CREATED`
- `BACKEND_IMPORT = NOT_EXECUTED`
- `SOLVER_EXECUTION = NOT_EXECUTED`
- `physical_gate_effect = NONE`
- `physical_evidence_effect = NONE`

**Methodische Schlussfolgerung:** Das Reference-Only-Interface reduziert semantische Mehrdeutigkeit und macht die spätere Herleitung prüfbar. Es schließt G01 nicht und erzeugt keine physische Evidenz.
