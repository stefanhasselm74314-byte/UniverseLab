# UniverseLab 2T-01 — Ambient-2T-Weltlinien-Kinematik v0.1

**Kennung:** UL-GRQM-2T01-001  
**Datum:** 2026-11-21  
**Status:** DRAFT_ANALYTIC_NONCANONICAL  
**Wirkung:** physical evidence effect NONE; physical gate effect NONE; no backend execution, no AuthorizationDecision, no SingleUseGrant, no K1-D/K1-E promotion.  
**Vorgänger:** Draft PR #302 (Emergenz); Draft PR #303 (SIG-02).

## Prüfgegenstand und Trennung der Modellklassen

Dies ist eine lokale klassische Weltlinien-Konstruktion mit 6D-Signatur (4+,2-), angelehnt an die Literatur zur 2T Physics und Fefferman-Graham-Ambient-Metrik. Es ist weder ein unabhängig neuer Feldaktionssatz noch eine dynamische Herleitung von HZT-Full.

Das tatsächlich geprüfte kanonische M0-Dokument \`SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md\` fixiert separat **einen** physikalischen Zeitparameter und einen positiv-definiten zweidimensionalen internen Raum, Signatur (5+,1-), mit Einstein-Maxwell-Skalar-Cap-Dynamik. Die Modelle dürfen nicht ohne eine eigenständige Aktion/Abbildung gleichgesetzt werden.

## Postulate und geometrische Konstruktion

Sei X^M=(t,rho,x^mu), t>0, und g_munu(x,rho) eine glatte Lorentz-Metrik mit Signatur (3+,1-), unabhängig von t. In skalierten lokalen Koordinaten definieren wir

\`\`\`text
ds6^2 = 2 rho dt^2 + 2 t dt drho + t^2 g_munu(x,rho) dx^mu dx^nu
B_(t,rho) = [[2rho,t],[t,0]]
inverse(B) = [[0,1/t],[1/t,-2rho/t^2]]
det(B) = -t^2
det(G6) = -t^10 det(g4) > 0
Inertia(G6) = (4 positive, 2 negative).
\`\`\`

Diese Form ist eine **pre-ambient**-Metrik. Keine ambient-Ricci-Flachheit wird vorausgesetzt oder behauptet.

## Zwangsalgebra

Setze V=t d/dt und W=2 rho t^2, ferner

\`\`\`text
Q11 = W
Q12 = V^M P_M = t P_t
Q22 = G^MN P_M P_N
    = (2/t) P_t P_rho - (2 rho/t^2) P_rho^2
      + t^-2 g^munu(x,rho) p_mu p_nu.
\`\`\`

Die kinematischen Gleichungen lauten **stark** (für alle relevanten Phasenraumpunkte)

\`\`\`text
partial_M W = 2 G_MN V^N
Lie_V G_MN = 2 G_MN
V^M partial_M W = 2 W.
\`\`\`

Daraus folgt für die kanonische Poisson-Klammer

\`\`\`text
{Q11,Q12} = 2 Q11
{Q11,Q22} = 4 Q12
{Q12,Q22} = 2 Q22
\`\`\`

für beliebiges g_munu(x,rho) der genannten Klasse. **PASS: klassische Worldline-Constraint-Closure.**

## Eichschnitt und 4D-Shadow

Ein lokal regulärer Eichschnitt ist t=ell>0, P_rho=0. Q11=0 impliziert rho=0; Q12=0 impliziert P_t=0. Die Gauge-Constraint-Jacobideterminante ist -2 t^3 ungleich null. Dann:

\`\`\`text
Q22|slice = ell^-2 g^munu(x,0) p_mu p_nu = 0.
S4 = integral d lambda [ p_mu dot(x^mu) - (e/2)g^munu(x,0)p_mu p_nu].
\`\`\`

Phasenraumzählung: 12 - 2*3 = 6 = 8 - 2*1. **PASS: lokaler masseloser 4D-Teilchenschatten.**

Dieser Schritt ist **keine 6D-Einzeit-M0-Parent-Rekonstruktion** und **keine 4D-Einstein-Feldgleichungsableitung**.

## Expliziter Gegenbeweis gegen eine überzogene Schlussfolgerung

Die zulässige 4D-Metrik

\`\`\`text
ds4^2 = -d tau^2 + exp(2H tau) dx^2 + dy^2 + dz^2, H != 0
R4 = 2 H^2
G_(tau,tau) = 0
G_(y,y) = -H^2
\`\`\`

erfüllt keine quellenfreie Einstein-Gleichung G_munu + Lambda g_munu = 0 mit einer einzigen Konstanten Lambda, ist aber für die oben bewiesene 2T-Algebra erlaubt. Daher:

**Sp(2,R)-Algebraschließung ist eine notwendige kinematische Bedingung dieser Konstruktion, keine hinreichende Gravitationsdynamik.**

Naives Q22 -> Q22+U erfordert in dieser Weltlinien-Konstruktion V(U)=-2U. Ein konstantes U ungleich null verletzt die dritte Klammer; daraus folgt keine Aussage zur 6D-Feldwirkungskonstante Lambda6 von HZT-M0.

## Architektur- und Evidenzgrenzen

- Architektur A: 6D (4+,2-) -> direkt 4D (3+,1-) masseloser 1T-Shadow. Kinematisch gezeigt; dynamischer/quantisierter Shadow offen.
- HZT-M0-S6: separater 6D (5+,1-)-Parent mit anderem Feldinventar und 6D->4D-Reduktionsaufgabe.
- Architektur B (rein hypothetisch): 8D (6+,2-) -> 6D (5+,1-) -> 4D (3+,1-). Das wäre ein neues Modell, **nicht** das bestehende HZT-Full und ohne Autorisierung nicht einzuführen.

**Nicht gezeigt:** 6D-2T-Feldwirkung, Dilaton-/W-Variationsgleichungen, Cap-/GHY-/Israel-Verknüpfung, BRST/Anomaliefreiheit, Ghostfreiheit, GR-Grenzfall, M0-Identität, Vorhersage für Mu/Sigma/E_G/GW, Quantenverschränkungsrekonstruktion, empirische Evidenz.

## Prüfstatus

- Ambient-Determinante/Signatur: ANALYTIC_PASS
- Closed homothety: ANALYTIC_PASS
- Starke Poisson-Algebra: SYMBOLIC_PASS
- Regulärer lokaler Eichschnitt und 4D-Massenschale: SYMBOLIC_PASS
- 4D-Einstein-Nichtimplikation: COUNTEREXAMPLE_CONFIRMED
- Volle 2T-HZT-Parentfeldwirkung: OPEN
- 2T -> HZT-M0-S6-Identität: OPEN
- Ghostfreiheit / GR-Feldgleichungen / Observablen: NOT_ESTABLISHED
- K1-D: NOT_RELEASED
- K1-E: NOT_ADMISSIBLE

Eine vollständige siebenseitige PDF-, MD-, Python-Test- und SHA-256-Fassung liegt als separates, nichtkanonisches Nutzerpaket vor. Dieses GitHub-Ledger ist die kompakte reviewbare Version, nicht eine Byte-Kopie des vollständigen PDFs.

## Primärquellen / Referenzen

- Bars 2000: https://doi.org/10.1103/PhysRevD.62.085015
- Bars 2008: https://doi.org/10.1103/PhysRevD.77.125027
- Bars/Chen 2009: https://doi.org/10.1103/PhysRevD.79.085021
- Kamiński 2023: https://doi.org/10.1007/s00220-023-04703-y
- UniverseLab: https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md
- UniverseLab: https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/hzt-s6-parent-action-v0.1.json

Nächster getrennter Analyseschritt: UL-GRQM-2T02 — feldtheoretischer Bars-Shadow gegen HZT-M0-Parent mit explizitem Wirkungs-, Feld- und Randdatenabgleich, **ohne** kanonische Promotion.
