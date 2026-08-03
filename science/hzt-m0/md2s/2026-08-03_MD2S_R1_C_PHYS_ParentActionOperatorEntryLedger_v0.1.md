# MD2S-R1-C-PHYS — Parent Action and Continuum Operator Entry Ledger v0.1

**Datum:** 2026-08-03  
**Track:** `MD2S-R1-C-PHYS`  
**Phase:** `R1.0`  
**Status:** `CONTINUUM_OPERATOR_SCAFFOLD_DEFINED_MODEL_FREEZE_INCOMPLETE`  
**Evidenzwirkung:** `NONE`  
**Solverfreigabe:** `NOT_AUTHORIZED`

## A. Was wurde gemacht?

Aus der aktuellen minimalen SCI-001/SCI-002-Parentwirkung wurde unabhängig vom historischen A0-Zweig und unabhängig vom C1-V-Verifikationsmodell die generische statische radiale Gleichungsstruktur abgeleitet. Zusätzlich wurden:

1. die glatten Polbedingungen und führenden Polserien formuliert,
2. die metrischen, skalaren und gaugetheoretischen Kappenresiduen in einer gemeinsamen Orientierungssprache zusammengeführt,
3. die globale Fluxbedingung vom lokalen Gauge-Matching getrennt,
4. ein regulärer Kandidat für Zustands- und Residualräume angegeben,
5. die offenen Modell-Freeze-Punkte MF-001 bis MF-007 neu klassifiziert,
6. die exakte Grenze zwischen einem Operatorgerüst und einem wohldefinierten quadratischen Randwertproblem festgelegt.

Es wurde **kein** Hintergrund gelöst und **kein** physikalischer Solver begonnen.

---

## 1. Verbindliche Parentwirkung dieses Blocks

Der minimale aktuelle C-PHYS-Zweig verwendet

\[
\begin{aligned}
S=&\sum_{s=N,S}\int_{\mathcal M_s} d^6X\,\sqrt{-g}\Bigg[
\frac{M_6^4}{2}(R-2\Lambda_6)
-\frac12(\partial\phi)^2-U(\phi)
-\frac14 Z_F(\phi)F_{AB}F^{AB}
\Bigg]\\
&+M_6^4\sum_{s=N,S}\int_{\Sigma_5}d^5x\,\sqrt{-h}\,K_s
+\int_{\Sigma_5}d^5x\,\sqrt{-h}\,\mathcal L_\Sigma,
\end{aligned}
\]

mit

\[
\mathcal L_\Sigma
=-\lambda(\phi)
-\frac12 Z_\sigma(\phi)h^{ab}D_a\sigma D_b\sigma,
\qquad
D_a\sigma=\partial_a\sigma-q_\sigma A_a.
\]

### Festgehalten

- Einstein-Hilbert-Normierung: \(M_6^4/2\)
- kosmologische Konvention: \(R-2\Lambda_6\)
- kanonische skalare Kinetik: \(Z_\phi=1\)
- Maxwell-Normierung: \(-Z_FF^2/4\)
- GHY-Term auf beiden Seiten
- lokalisierte Spannung plus Winding-Sektor
- kein Gauss-Bonnet-Term in diesem Modellvertrag

### Weiter offen

\[
U(\phi),\quad Z_F(\phi),\quad\lambda(\phi),\quad Z_\sigma(\phi),
\quad q_\sigma,\quad q_{\rm ref},
\]

sowie Ladungsgitter, Gauge-Patch-Übergang, endgültige Winkelperiode, Frame-Bedingung und Parameterrollen.

Die ältere Aussage, auch \(Z_\phi\) sei im minimalen aktuellen Zweig offen, kollidiert mit der expliziten SCI-001/SCI-002-Wirkung. Für diesen **minimalen** C-PHYS-Vertrag gilt daher

\[
\boxed{Z_\phi=1}
\]

solange keine neue versionierte Parentwirkung den Skalarsektor ausdrücklich erweitert.

---

## 2. Hintergrundansatz

Für jede der beiden Regionen \(s\in\{N,S\}\):

\[
ds_6^2=e^{2A_s(r)}\bar g_{\mu\nu}dx^\mu dx^\nu+dr^2+L_s^2(r)d\chi^2,
\]

\[
\bar R_{\mu\nu}=3\mathcal K_4\bar g_{\mu\nu},
\qquad
\phi=\phi_s(r),
\qquad
A=A_{\chi,s}(r)d\chi.
\]

Die lokale Radialkoordinate wächst jeweils vom glatten Pol bei \(r=0\) zur gemeinsamen Kappe bei \(r=\rho_s\).

Wir definieren

\[
H_s=A_s',
\qquad
B_s=\frac{L_s'}{L_s}.
\]

Die nichtverschwindenden Ricci-Komponenten lauten

\[
\frac{R_{\mu\nu}}{g_{\mu\nu}}
=3\mathcal K_4e^{-2A_s}
-A_s''-4H_s^2-H_sB_s,
\]

\[
R_{rr}=-4A_s''-4H_s^2-\frac{L_s''}{L_s},
\]

\[
\frac{R_{\chi\chi}}{L_s^2}
=-\frac{L_s''}{L_s}-4H_sB_s,
\]

und

\[
R_6=12\mathcal K_4e^{-2A_s}
-8A_s''-20H_s^2-8H_sB_s-2\frac{L_s''}{L_s}.
\]

---

## 3. Maxwell-Sektor

Aus

\[
\nabla_A\left(Z_FF^{A\chi}\right)=0
\]

folgt in jeder Region die erste Integration

\[
\boxed{
F_{r\chi,s}
=\frac{Q_sL_se^{-4A_s}}{Z_F(\phi_s)}
}
\]

mit regionaler Integrationskonstante \(Q_s\).

Die lokale magnetische Energiedichte wird geschrieben als

\[
\boxed{
\rho_{F,s}
=\frac{Q_s^2e^{-8A_s}}{2Z_F(\phi_s)}
}.
\]

Lokales Gauge-Matching und globale Fluxquantisierung bleiben verschiedene Gleichungen. Das eine ersetzt das andere nicht.

---

## 4. Generische radiale Bulkgleichungen

Die Einstein-Gleichung ist

\[
M_6^4(G_{AB}+\Lambda_6g_{AB})
=T^{(\phi)}_{AB}+T^{(F)}_{AB}.
\]

### 4.1 Evolutionsgleichung für \(A_s\)

Aus der \(\chi\chi\)-Komponente:

\[
\boxed{
4A_s''+10H_s^2
-6\mathcal K_4e^{-2A_s}
+\Lambda_6
+M_6^{-4}
\left[
\frac12(\phi_s')^2+U(\phi_s)-\rho_{F,s}
\right]=0
}
\]

### 4.2 Reguläre Gleichung für \(L_s\)

Die \(\mu\nu\)-Komponente wird mit \(L_s\) multipliziert, damit am Pol kein künstlicher Quotient \(L_s''/L_s\) steht:

\[
\boxed{
\begin{aligned}
0={}&L_s''+3A_s''L_s+6H_s^2L_s+3H_sL_s'\\
&-3\mathcal K_4e^{-2A_s}L_s
+\Lambda_6L_s\\
&+M_6^{-4}L_s
\left[
\frac12(\phi_s')^2+U(\phi_s)+\rho_{F,s}
\right].
\end{aligned}
}
\]

### 4.3 Reguläre Skalargleichung

\[
\boxed{
\begin{aligned}
0={}&L_s\phi_s''+(4H_sL_s+L_s')\phi_s'\\
&-L_sU_{,\phi}(\phi_s)
-L_s\rho_{F,s}\,\partial_\phi\ln Z_F(\phi_s).
\end{aligned}
}
\]

### 4.4 Gaugegleichung

\[
\boxed{
A_{\chi,s}'
-\frac{Q_sL_se^{-4A_s}}{Z_F(\phi_s)}=0
}
\]

---

## 5. Radialer Constraint

Die \(rr\)-Komponente ergibt

\[
M_6^4\left[
-6\mathcal K_4e^{-2A_s}
+6H_s^2+4H_sB_s+\Lambda_6
\right]
=
\frac12(\phi_s')^2-U(\phi_s)+\rho_{F,s}.
\]

Polregulär mit \(L_s\) multipliziert:

\[
\boxed{
\begin{aligned}
\mathcal C_{rr,s}={}&
M_6^4L_s\left[
-6\mathcal K_4e^{-2A_s}+6H_s^2+\Lambda_6
\right]\\
&+4M_6^4H_sL_s'
-L_s\left[
\frac12(\phi_s')^2-U(\phi_s)+\rho_{F,s}
\right]=0.
\end{aligned}
}
\]

Dieser Constraint darf erst dann ausschließlich als propagierter QA-Kanal behandelt werden, wenn die Bianchi-/Abhängigkeitsidentität für genau diese Gleichungswahl symbolisch dokumentiert wurde.

\[
\boxed{
\text{Constraint propagation} = \text{OPEN}
}
\]

---

## 6. Glatte Pole

Für Winkelperiode \(\Delta\chi\) definieren wir

\[
\alpha=\frac{2\pi}{\Delta\chi}.
\]

Glatte Polregularität verlangt

\[
L_s(0)=0,\qquad L_s'(0)=\alpha,
\]

\[
A_s'(0)=0,\qquad\phi_s'(0)=0,
\]

und in einer regulären lokalen Pol-Gauge

\[
A_{\chi,s}(0)=0.
\]

Die Paritätsserien lauten

\[
A_s=A_{0,s}+a_{2,s}r^2+O(r^4),
\]

\[
L_s=\alpha r+\ell_{3,s}r^3+O(r^5),
\]

\[
\phi_s=\phi_{0,s}+f_{2,s}r^2+O(r^4),
\]

\[
A_{\chi,s}=g_{2,s}r^2+O(r^4).
\]

Mit

\[
\rho_{F0,s}
=\frac{Q_s^2e^{-8A_{0,s}}}{2Z_F(\phi_{0,s})}
\]

folgt

\[
\boxed{
a_{2,s}
=\frac18\left[
6\mathcal K_4e^{-2A_{0,s}}-\Lambda_6
+M_6^{-4}(-U_0+\rho_{F0,s})
\right]
}
\]

\[
\boxed{
f_{2,s}
=\frac14\left[
U_{,\phi}(\phi_{0,s})
+\rho_{F0,s}\partial_\phi\ln Z_F(\phi_{0,s})
\right]
}
\]

\[
\boxed{
g_{2,s}
=\frac{Q_s\alpha e^{-4A_{0,s}}}{2Z_F(\phi_{0,s})}
}
\]

und

\[
\boxed{
\ell_{3,s}
=\frac{\alpha}{6}\left[
3\mathcal K_4e^{-2A_{0,s}}
-12a_{2,s}-\Lambda_6
+M_6^{-4}(-U_0-\rho_{F0,s})
\right].
}
\]

Für einen späteren Solver reichen diese führenden Koeffizienten noch nicht automatisch aus. Vor numerischer Initialisierung fehlen:

- höhere Ordnungen,
- Invariantenprüfung,
- expliziter Projektor gegen den konischen Rettungsmodus,
- eingefrorene Winkelperiode.

---

## 7. Kappen- und Globalbedingungen

Am gemeinsamen Capradius gelten zunächst die Kontinuitäten

\[
A_N(\rho_N)=A_S(\rho_S),
\]

\[
L_N(\rho_N)=L_S(\rho_S)\equiv L_\Sigma,
\]

\[
\phi_N(\rho_N)=\phi_S(\rho_S)\equiv\phi_\Sigma.
\]

Mit expliziten Normalzeichen \(n_s=\pm1\) definieren wir

\[
\mathcal A_\Sigma=\sum_s n_sA_s'(\rho_s),
\qquad
\mathcal L_\Sigma=\sum_s n_s\frac{L_s'(\rho_s)}{L_\Sigma},
\]

\[
\Phi_\Sigma'=\sum_s n_s\phi_s'(\rho_s).
\]

Für

\[
d_\chi=\frac{2\pi N_\sigma}{\Delta\chi}
-q_\sigma A_{\chi,\Sigma},
\]

\[
X_\sigma=\frac{d_\chi^2}{L_\Sigma^2},
\qquad
Y_\sigma=Z_\sigma(\phi_\Sigma)X_\sigma,
\]

lauten die beiden metrischen Junctionresiduen

\[
\boxed{
R_{4D}=M_6^4(-3\mathcal A_\Sigma-\mathcal L_\Sigma)
+\lambda(\phi_\Sigma)+\frac12Y_\sigma=0
}
\]

und

\[
\boxed{
R_\chi=-4M_6^4\mathcal A_\Sigma
+\lambda(\phi_\Sigma)-\frac12Y_\sigma=0.
}
\]

Ihre Differenz liefert

\[
\boxed{
Y_\sigma=M_6^4(\mathcal L_\Sigma-\mathcal A_\Sigma).
}
\]

Damit gilt im reinen Spannungslimit

\[
Y_\sigma=0
\quad\Longrightarrow\quad
\mathcal A_\Sigma=\mathcal L_\Sigma.
\]

Die skalare Junctionbedingung ist

\[
\boxed{
R_{\phi,\Sigma}
=\Phi_\Sigma'
+\lambda_{,\phi}(\phi_\Sigma)
+\frac12Z_{\sigma,\phi}(\phi_\Sigma)X_\sigma=0.
}
\]

Die lokale gaugetheoretische Bedingung lautet

\[
\boxed{
R_{A,\Sigma}
=\sum_s n_s\frac{Q_se^{-4A_s(\rho_s)}}{L_\Sigma}
-\frac{q_\sigma Z_\sigma(\phi_\Sigma)d_\chi}{L_\Sigma^2}=0.
}
\]

Die globale Fluxgleichung bleibt zusätzlich

\[
\Phi_F
=\Delta\chi\sum_s\int_0^{\rho_s}
\frac{Q_sL_se^{-4A_s}}{Z_F(\phi_s)}\,dr,
\]

\[
\boxed{
R_{\rm flux}=q_{\rm ref}\Phi_F-2\pi N_F=0.
}
\]

Die Gleichsetzung

\[
q_{\rm ref}=q_\sigma
\]

wird nicht angenommen.

---

## 8. Kontinuumsoperator-Gerüst

Der zukünftige physikalische Operator soll die Form

\[
\mathcal R_{\rm CPHYS}:
\mathcal X_{\rm reg}\times\mathcal P_{\rm frozen}
\longrightarrow
\mathcal Y_{\rm bulk}\times\mathbb R^{n_B}
\]

besitzen.

### Profilvariablen je Seite

\[
(A_s,L_s,\phi_s,A_{\chi,s}).
\]

### Kandidaten für globale Schieß- oder Eigenwertvariablen

\[
\rho_N,\rho_S,\mathcal K_4,Q_N,Q_S.
\]

Ob diese Größen fest, gescannt, geschossen oder aus anderen Bedingungen abgeleitet werden, ist noch nicht endgültig eingefroren.

### Reguläre Faktorisierung am Pol

\[
A_s=A_{0,s}+r^2\widetilde A_s(r^2),
\]

\[
\phi_s=\phi_{0,s}+r^2\widetilde\phi_s(r^2),
\]

\[
L_s=\alpha r+r^3\widetilde L_s(r^2),
\]

\[
A_{\chi,s}=r^2\widetilde a_s(r^2).
\]

Ein Kandidat ist ein gewichteter \(C^{2,\gamma}\)-Raum für \(A,L,\phi\), ein gewichteter \(C^{1,\gamma}\)-Raum für \(A_\chi\), gewichtete \(C^{0,\gamma}\)-Bulkresiduen und endlichdimensionale Randresiduen.

Dieser Raum ist noch nicht ratifiziert. Zuvor fehlen:

1. Hauptsymbol- und Randkomplementaritätsaudit,
2. Constraint-Abhängigkeitsbeweis,
3. explizite Frame- und Gauge-Quotientierung,
4. Patch- und Cap-Trace-Audit,
5. quadratische Unbekannten-/Residualzählung.

Daher gilt

\[
\boxed{
D_X\mathcal R_{\rm CPHYS}
\text{ ist noch nicht als Fredholm-Operator definiert.}
}
\]

---

## 9. Model-Freeze-Matrix

| Gate | Neu geschlossener Inhalt | Verbleibender Blocker | Status |
|---|---|---|---|
| MF-001 | EH-, Λ-, kanonische Skalar- und Maxwell-Struktur | \(U,Z_F\), Feldbereich | `PARTIAL_STRUCTURAL_FREEZE` |
| MF-002 | GHY- und Cap-Sektor, formale Junctionformen | λ, \(Z_σ\), \(q_σ\), Normalentabelle | `PARTIAL_STRUCTURAL_FREEZE` |
| MF-003 | generische radiale Gleichungen und rr-Constraint | Bianchi-Abhängigkeit, Spezialisierung, Dimensionslosigkeit | `PARTIAL_DERIVED_CONDITIONAL` |
| MF-004 | Parität und führende Polkoeffizienten | höhere Serie, Invarianten, Δχ, Konusprojektor | `PARTIAL_DERIVED_CONDITIONAL` |
| MF-005 | generische Junction-, Gauge- und Fluxresiduen | Patchregel, Ladungsgitter, Orientierung, finale Zählung | `PARTIAL_DERIVED_CONDITIONAL` |
| MF-006 | vorhandene Dimensions- und Topologiestruktur | Parameterrollen, Frame, Ladungsrelation | `PARTIAL_STRUCTURAL_FREEZE` |
| MF-007 | aktuelles Warped-Volume-Gerüst | \(R_{circle}\), Ξ, λ_eff, historische Identität | `PARTIAL` |

---

## B. Was wurde tatsächlich hergeleitet?

- Generische radiale Einstein-, Skalar- und Maxwellgleichungen aus der aktuellen minimalen Parentwirkung.
- Polreguläre Form der Bulkgleichungen und des rr-Constraints.
- Führende glatte Polserien.
- Generische metrische, skalare und lokale Gauge-Junctions.
- Trennung lokaler Gauge-Junction und globaler Fluxquantisierung.
- Ein mathematisches Interface für den späteren Kontinuumsoperator.

Status:

```text
GENERIC_PARENT_ACTION_RADIAL_SYSTEM = DERIVED_CONDITIONAL
CONTINUUM_OPERATOR                  = SCAFFOLD_ONLY
```

---

## C. Was wurde nicht bewiesen?

Nicht bewiesen oder freigegeben sind:

- exakte physikalische Modellwahl der offenen Funktionen,
- Wohldefiniertheit eines quadratischen BVP,
- Fredholm-Eigenschaft,
- Kontinuums-Jacobianrang,
- lokales oder globales Existenztheorem,
- ein regulärer physikalischer Hintergrund,
- Stabilität oder Ghostfreiheit,
- historische A0-Identität,
- 6D→4D-Forward-Map,
- K1-D oder K1-E.

---

## D. Bearbeiteter Track

```text
MD2S-R1-C-PHYS
```

C1-V und MD2S-R1-L wurden nicht als Gleichungsquellen verwendet.

---

## E. Gate-Wirkung

```text
R1.0                      = ACTIVE_MODEL_FREEZE_INCOMPLETE
R1.1                      = BLOCKED
R1.2                      = BLOCKED
official MD-2S solver     = NOT_AUTHORIZED
continuum BVP operator    = SCAFFOLD_ONLY
continuum BVP Jacobian    = NOT_PROVEN
perturbative stability    = OPEN
ghost freedom             = OPEN
K1-D                      = NOT_RELEASED
K1-E                      = NOT_ADMISSIBLE
physical evidence effect  = NONE
```

---

## F. Neue Artefakte

- `registry/2026-08-03_MD2S_R1_C_PHYS_ParentActionOperatorEntryContract_v0.1.json`
- `science/hzt-m0/md2s/2026-08-03_MD2S_R1_C_PHYS_ParentActionOperatorEntryLedger_v0.1.md`
- `tools/2026-08-03_validate_md2s_r1_c_phys_operator_entry_v0.1.py`
- `tests/2026-08-03_test_md2s_r1_c_phys_operator_entry_v0.1.py`
- `.github/workflows/2026-08-03_UniverseLab_MD2S_R1_C_PHYS_OperatorEntry_v0.1.yml`

---

## G. Nächster blockergetriebener Schritt

```text
C-PHYS-R1.0-FREEZE-1
```

Exakt zu schließen sind:

1. \(U(\phi)\) und \(Z_F(\phi)\),
2. λ(φ) und \(Z_σ(φ)\),
3. \(q_σ\), \(q_{\rm ref}\) und das Ladungsgitter,
4. Gauge-Patch-Übergang,
5. Normalorientierung beider Regionen,
6. endgültige Winkelperiode,
7. 4D-Framebedingung,
8. feste, gescannte, geschossene und abgeleitete Parameterrollen.

Erst danach darf die quadratische BVP-Zählung geschlossen und R1.1 neu bewertet werden.
