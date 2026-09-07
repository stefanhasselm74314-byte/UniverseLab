# ULSH-05 / WP1 — Quadratic Action Readiness v0.1

**Datum:** 2026-09-07  
**Modellidentität:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `6a94d098565655e36b750355499f29625d9cc2d4`  
**Klassifikation:** `NONOPERATIVE_ANALYTIC_READINESS_FREEZE`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Entscheidung

`[KONDITIONAL]` Die Aktionsseite des C-PHYS-M1-Zweigs ist inzwischen weit genug eingefroren, um die **off-shell zweite Variation als wohldefiniertes analytisches Problem** zu beginnen.

`[OFFEN/BLOCKIERT]` Der vollständige physikalische quadratische Perturbationssektor ist **nicht** hergeleitet. Insbesondere fehlen weiterhin:

- die vollständige EH+GHY-Zweitvariation,
- alle metrisch-skalar-gauge gemischten Terme,
- die zweite Variation des Cap-Sektors,
- die perturbierten Israel-/Skalar-/Gauge-/Phasen-Randbedingungen,
- eine explizite Behandlung von Cap-Bending beziehungsweise eine hergeleitete Fixed-Interface-Gauge,
- S/V/T-Zerlegung und Gaugekontrolle,
- Constraint-Elimination,
- ein freigegebener on-shell 6D-Hintergrund,
- die Materieperturbation `Delta_m` und ihre HZT-Kopplung,
- die 6D→4D-Perturbationsreduktion und damit `mu`, `eta`, `Sigma`, Growth und Lensing.

Daher bleibt ULSH-05/WP1:

```text
PREPARATORY_READY_TO_DERIVE_NOT_CLOSED
```

und G01 bleibt `OPEN_BLOCKING`.

---

## 2. Kanonische Quellenkette

Die Readiness-Prüfung benutzt ausschließlich dieselbe kontrollierte Modellkette:

1. `SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md`
2. `hzt-s6-parent-action-v0.1.json`
3. `registry/2026-08-03_MD2S_R1_C_PHYS_GlobalConventionFreezeContract_v0.1.json`
4. `registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json`
5. `science/hzt-m0/md2s/2026-08-03_MD2S_BulkLocalizedActionAndJunctionLedger_v0.1.md`
6. `registry/2026-08-31_HZT_M0_ForwardMap_FM0_Kappa6Binding_v0.1.json`
7. `science/solver-hub/2026-08-07_ULSH-05_SVT-Perturbation_Roadmap_v1.0.md`
8. `registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInventory_v1.0.json`

Keine HZT-Full-, C1-V-, historische A0-, Regge-Teitelboim-, Gauss-Bonnet- oder Baryogenese-4-Form-Formel wird in diesen Zweig importiert.

---

## 3. Eingefrorene Parentwirkung

Für den kontrollierten M1-Zweig ist die strukturelle Wirkung

\[
\begin{aligned}
S={}&\sum_{s=\pm}\int_{\mathcal M_s}d^6X\sqrt{-g}
\left[\frac{M_6^4}{2}(R-2\Lambda_6)
-\frac12(\partial\phi)^2-U(\phi)
-\frac14 Z_F(\phi)F_{AB}F^{AB}\right]\\
&+M_6^4\sum_{s=\pm}\int_{\Sigma_5}d^5x\sqrt{-h}\,K_s
+\int_{\Sigma_5}d^5x\sqrt{-h}\,\mathcal L_\Sigma,
\end{aligned}
\]

mit

\[
\mathcal L_\Sigma=-\lambda(\phi)-\frac12 Z_\sigma(\phi)h^{ab}D_a\sigma D_b\sigma,
\qquad
D_a\sigma=\partial_a\sigma-q_\Sigma A_a.
\]

`[BEWIESEN/AUS QUELLE]` EH-Normierung, GHY-Struktur, kanonische Skalar-Kinetik, Maxwell-Normierung und Cap-Struktur sind versioniert.

`[BEWIESEN/AUS QUELLE]` Für `C-PHYS-M1` sind zusätzlich die exakten Funktionen eingefroren:

\[
U(\phi)=\frac12\hat m_\phi^2 M_6^6\left(\frac{\phi}{M_6^2}\right)^2,
\]

\[
Z_F(\phi)=\exp\!\left(-2a_F\frac{\phi}{M_6^2}\right),
\]

\[
\lambda(\phi)=\hat\lambda M_6^5,
\qquad
Z_\sigma(\phi)=\hat z_\sigma M_6^3.
\]

Der Skalarbereich ist `R`; `mhat_phi_sq>0`, `a_F>0`, `z_sigma_hat>0`, `q_hat>0` innerhalb der aktiven M1-Domäne.

---

## 4. Perturbationsbuchhaltung

Es wird **noch keine Gauge gewählt**. Der reine Feldsplit wird definiert als

\[
g_{AB}(\epsilon)=\bar g_{AB}+\epsilon h_{AB},
\]

\[
\phi(\epsilon)=\bar\phi+\epsilon\varphi,
\]

\[
A_A(\epsilon)=\bar A_A+\epsilon a_A,
\]

\[
F_{AB}(\epsilon)=\bar F_{AB}+\epsilon f_{AB},
\qquad
f_{AB}=2\bar\nabla_{[A}a_{B]},
\]

und auf der Kappe

\[
\sigma(\epsilon)=\bar\sigma+\epsilon s.
\]

Alle Indizes in der algebraischen Expansionsbuchhaltung werden mit \(\bar g_{AB}\) gehoben und gesenkt.

### 4.1 Kinematische Identitäten

Mit

\[
h\equiv \bar g^{AB}h_{AB}
\]

folgt

\[
g^{AB}
=\bar g^{AB}-\epsilon h^{AB}
+\epsilon^2h^A{}_C h^{CB}+O(\epsilon^3),
\]

und

\[
\sqrt{-g}
=\sqrt{-\bar g}
\left[
1+\frac\epsilon2h
+\epsilon^2\left(\frac18h^2-\frac14h_{AB}h^{AB}\right)
+O(\epsilon^3)
\right].
\]

Diese beiden Gleichungen sind **kinematische Matrixidentitäten** und noch keine Aussage über HZT-Dynamik oder Stabilität.

---

## 5. M1-Funktionskerne für die Zweitvariation

Da die Funktionsfamilie exakt eingefroren ist, sind die notwendigen lokalen Ableitungen algebraisch bestimmt.

### 5.1 Skalarpotential

Aus

\[
U(\phi)=\frac12\hat m_\phi^2M_6^2\phi^2
\]

folgt

\[
U_{,\phi}(\bar\phi)=\hat m_\phi^2M_6^2\bar\phi,
\qquad
U_{,\phi\phi}=\hat m_\phi^2M_6^2.
\]

### 5.2 Gaugekinetik

Aus

\[
Z_F(\phi)=e^{-2a_F\phi/M_6^2}
\]

folgt

\[
Z_{F,\phi}(\bar\phi)
=-\frac{2a_F}{M_6^2}Z_F(\bar\phi),
\]

\[
Z_{F,\phi\phi}(\bar\phi)
=\frac{4a_F^2}{M_6^4}Z_F(\bar\phi).
\]

### 5.3 Cap-Funktionen

Für die M1-Konstanten gilt

\[
\lambda_{,\phi}=\lambda_{,\phi\phi}=0,
\qquad
Z_{\sigma,\phi}=Z_{\sigma,\phi\phi}=0.
\]

`[BEWIESEN/ALGEBRAISCH]` Diese Ableitungen folgen direkt aus den eingefrorenen M1-Funktionen. Sie schließen **nicht** den vollständigen Hessian, da dessen metrische, Gauge- und Randmischungen noch fehlen.

---

## 6. Definition des quadratischen Terms

Wir verwenden die eindeutige Konvention

\[
S[\Psi_\epsilon]
=S^{(0)}+\epsilon\,\delta S
+\epsilon^2S_{\rm quad}^{(2)}+O(\epsilon^3),
\]

mit

\[
\boxed{
S_{\rm quad}^{(2)}
=\frac12\left.\frac{d^2}{d\epsilon^2}S[\Psi_\epsilon]\right|_{\epsilon=0}
}.
\]

### Off-shell

Für eine beliebige Hintergrundkonfiguration \(\bar\Psi\) muss

\[
\delta S\neq0
\]

zugelassen werden.

### On-shell

Erst wenn \(\bar\Psi\) sämtliche Bulkgleichungen **und** alle Rand-/Junctionbedingungen erfüllt, darf

\[
\delta S=0
\]

verwendet und \(S_{\rm quad}^{(2)}\) als physikalische quadratische Perturbationswirkung um diesen Hintergrund interpretiert werden.

Da der kanonische Projektstatus weiterhin

```text
PHYSICAL_BACKGROUND = NOT_ESTABLISHED
```

lautet, ist die on-shell Interpretation derzeit blockiert.

---

## 7. Was WP1 jetzt wirklich erlaubt

`[KONDITIONAL]` Zulässig ist als nächster analytischer Schritt die **sektorweise off-shell Hessian-Herleitung**:

\[
S_{\rm quad}^{(2)}
=S_{\rm EH+GHY}^{(2)}
+S_{\phi}^{(2)}
+S_{F}^{(2)}
+S_{\Sigma}^{(2)},
\]

wobei alle Mischterme innerhalb dieser Summe ausdrücklich mitgeführt werden müssen.

Die Herleitung muss mindestens liefern:

1. EH+GHY-Hessian mit expliziten Randtermen;
2. metrisch-skalar gekoppelte Terme;
3. metrisch-Maxwell und Skalar-Maxwell-Mischungen durch \(Z_F(\phi)\);
4. Cap-Hessian aus \(\lambda\), \(Z_\sigma\), \(D_a\sigma\) und induzierter Metrik;
5. perturbierte Israel-, Skalar-, Gauge- und Phasenbedingungen;
6. klare Behandlung der hypersurface displacement / cap-bending Freiheitsgrade oder eine vollständig hergeleitete Fixed-Interface-Gauge.

---

## 8. Zusätzlicher Cap-Bending-Blocker

`[ABGELEITET/OFFEN]` Die vorhandenen Parent- und Junction-Artefakte variieren die Felder auf einer strukturell definierten Kappe, enthalten aber noch **keine versionierte Perturbationsregel für eine bewegte Kappenlage**.

Für die zweite Variation muss daher eine von zwei Möglichkeiten explizit gewählt und hergeleitet werden:

- ein Embedding-/Bending-Perturbationsfeld der Kappe, oder
- eine Fixed-Interface-Gauge, in der die Kappe koordinatenfest bleibt und die entsprechende Gauge-Freiheit vollständig kontrolliert ist.

Ohne diese Entscheidung wäre eine scheinbar vollständige Rand-Hessian-Herleitung unvollständig.

---

## 9. Warum G01 trotzdem offen bleibt

Die G01-Inventur markiert weiterhin

```text
matter_perturbation_Delta_m_definition_and_coupling_for_HZT = MISSING_REQUIRED_LINK
```

und

```text
sixD_to_fourD_perturbative_reduction = MISSING_REQUIRED_LINK
```

Daher kann aus der reinen M1-Aktionsseite noch keine belastbare Kette

\[
\{h_{AB},\varphi,a_A,s\}_{6D}
\rightarrow
\{\Phi,\Psi,\Delta_m\}_{4D}
\rightarrow
\{\mu,\eta,\Sigma,D\}
\]

konstruiert werden.

Insbesondere bleiben die bereits vorhandenen Firewalls verbindlich:

```text
Bridge growth  -> UNRELEASED_GROWTH_MAP
Bridge lensing -> UNRELEASED_LENSING_MAP
```

---

## 10. Nicht zulässige Schlussfolgerungen

Dieses Readiness-Artefakt beweist **nicht**:

- einen physikalischen Hintergrund,
- Gaugekontrolle,
- Constraint-Abschluss,
- Ghostfreiheit,
- kinetische Positivität,
- Gradientstabilität,
- Modenspektren,
- 4D-Newton-Konstante,
- `mu(k,a)`, `eta(k,a)` oder `Sigma(k,a)`,
- Growth oder Lensing,
- K1-D oder K1-E.

Die Statuswerte bleiben:

```text
FM-G0                 OPEN
PHYSICAL_BACKGROUND   NOT_ESTABLISHED
PHYSICAL_RESPONSE_RANK NOT_EXECUTED
K1-D                   NOT_RELEASED
K1-E                   NOT_ADMISSIBLE
physical_gate_effect   NONE
physical_evidence_effect NONE
```

---

## 11. Nächster analytischer Block

Der kleinste sachlich korrekte nächste Schritt ist:

```text
ULSH05-WP1A — sectorwise off-shell Hessian derivation
```

Reihenfolge:

1. Skalar+Maxwell-Hessian auf festem Hintergrund als Kontrollsektor;
2. EH+GHY-Hessian mit vollständiger Randbuchhaltung;
3. Cap-Hessian und pertubierte Junctionbedingungen;
4. erst danach Zusammensetzen des vollständigen off-shell `S_quad^(2)`;
5. on-shell Reduktion erst nach einem separat freigegebenen 6D-Hintergrund.
