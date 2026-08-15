# HZT-M0 / S6 / C-PHYS H4R4 — Exact compatibility hierarchy, local-IBVP theorem audit and manufactured-solution preflight v0.1

**Datum:** 2026-08-15  
**Block:** `C-PHYS-PARENT-H4R4-EXACT-COEFFICIENT-COMPATIBILITY-HIERARCHY-LOCAL-IBVP-THEOREM-RATIFICATION-AND-MANUFACTURED-SOLUTION-PREFLIGHT`  
**Status:** `H4R4_AUDIT_COMPLETE_LOCAL_IBVP_THEOREM_NOT_RATIFIABLE_YET_EXACT_LOWER_ORDER_COEFFICIENT_AND_BOUNDARY_JET_EXPORT_MISSING_MMS_PREFLIGHT_FROZEN_NO_EXECUTION`  
**Solverausführung:** nein  
**Manufactured-Solution-Ausführung:** nein  
**Physische Evidenzwirkung:** `NONE`

## 1. Ziel

H4R3 hat für den deklarierten nichtentarteten Zustandsbereich einen positiven PDE-Symmetrisierer, einen maximal konservativen Principal-Interface-Raum und eine konditionale nichtlineare Sobolev-Energieabschätzung etabliert. Das reicht jedoch noch nicht für einen lokalen Existenz-/Eindeutigkeitssatz.

H4R4 führt deshalb bewusst **keine weitere Principal-Abkürzung** ein, sondern auditiert die Hypothesen, die vor einer Theorem-Ratifizierung explizit und maschinenprüfbar vorliegen müssen.

Gemini-Blöcke bleiben `EXTERNAL_UNVERIFIED_GEMINI_DRAFT`. Die kanonische Signatur bleibt

\[
(-,+,+,+,+,+).
\]

## 2. Warum H4R3 noch kein lokales IBVP-Theorem ist

Der reduzierte H4R3-Zustand ist

\[
W_s=(U_s,P_s,Q_s),
\qquad
U_s=(\omega,u,v,\varphi,a_\chi),
\]

mit

\[
P_s=\partial_\tau U_s,
\qquad
Q_s=\partial_{x_s}U_s.
\]

Der Principal-Sektor kann in symmetrisch-hyperbolischer Form geschrieben werden. Für ein lokales quasilineares IBVP-Theorem müssen aber zusätzlich die **vollständigen** variablen Koeffizienten, Quellen und Randabbildungen glatt und mit der benötigten Kompatibilitätshierarchie kontrolliert sein.

Die maßgebliche Standardtheorie für quasilineare symmetrisch-hyperbolische IBVPs verlangt nicht nur Principal-Hyperbolizität, sondern auch einen kontrollierten Randrang, geeignete dissipative/maximal nichtnegative Randbedingungen, Glattheit der Koeffizienten und kompatible Anfangs-/Randdaten. H4R4 orientiert sich hierbei an der klassischen Secchi/Friedrichs-Kreiss-Majda-Linie; diese Literatur wird **nicht** als Beweis für HZT übernommen, sondern nur als Anforderungskatalog für die spätere explizite Hypothesenprüfung.

## 3. Exakter H4R4-Export, der noch fehlt

H4 besitzt die kovarianten Bulkgleichungen und die dynamischen Cap-Junctions. Was noch **nicht** als einzelnes kanonisches Artefakt vorliegt, ist die vollständig gauge-fixierte erste-Ordnungsform

\[
A_s^0(W_s)\,\partial_\tau W_s
+A_s^1(W_s)\,\partial_{x_s}W_s
=F_s(W_s)
\]

mit allen lower-order Termen, zusammen mit einem exakten nichtlinearen Interface-Residual

\[
\mathcal B(W_N,W_S,Q_N,Q_S)=0.
\]

Benötigt werden mindestens:

- `A0_s(W)` und `A1_s(W)` als exakte Matrizen,
- der vollständige lower-order-Vektor `F_s(W)`,
- die exakten Constraint-Abbildungen,
- die drei metrischen dynamischen Junction-Residuals,
- skalares Matching,
- Maxwell-/Gauge-Matching,
- die Continuity-Residuals,
- Patch-/Fluxkompatibilität und die globale Regularitätsbindung,
- die Ableitungen dieser Maps bis zur für den gewählten Sobolevindex benötigten Ordnung.

Ohne diesen Export wäre jede höhere Kompatibilitätsbedingung eine stillschweigende Festlegung noch nicht explizierter lower-order Konventionen.

## 4. Exakte Kompatibilitätshierarchie

Seien die Anfangsdaten auf beiden Seiten

\[
W_s(0,x_s)=W_s^0(x_s).
\]

### Ordnung 0

Am Interface müssen zunächst exakt gelten:

\[
\boxed{\mathcal B(W_N^0,W_S^0,Q_N^0,Q_S^0)=0.}
\]

Zusätzlich:

\[
\boxed{C_H[W_s^0]=0,\qquad C_M[W_s^0]=0}
\]

auf jeder Seite sowie

\[
\boxed{R_{\rm patch}=0}
\]

im festgelegten Fluxsektor. Kontinuität, Cap-Regularität und globale Patchorientierung gehören ebenfalls zur Ordnung-0-Kompatibilität.

### Höhere Ordnung

Für einen Zielindex \(m\ge3\) lautet die rekursive Bedingung

\[
\boxed{
\partial_\tau^j\mathcal B\big|_{\tau=0}=0,
\qquad j=1,\ldots,m-1,
}
\]

wobei **jede** Zeit-ableitung rekursiv mit den exakten Evolutionsgleichungen eliminiert werden muss. Schematisch:

\[
\partial_\tau W
=\Phi_1(W,\partial_xW),
\]

\[
\partial_\tau^2W
=\Phi_2(W,\partial_xW,\partial_x^2W),
\]

usw. Deshalb sind die exakten lower-order Maps unverzichtbar.

Die gleiche Ableitungsordnung ist für die Constraint- und Patchidentitäten zu prüfen, soweit dies das später ausgewählte lokale IBVP-Theorem verlangt.

### H4R4-Befund

Die **Form** dieser Hierarchie ist jetzt eingefroren. Die expliziten Jets \(j\ge1\) können aber noch nicht kanonisch expandiert werden, weil `F_s(W)` und der Boundary-Jet-Generator fehlen.

Daher:

\[
\boxed{
\text{compatibility hierarchy defined}
\neq
\text{compatibility hierarchy verified}.
}
\]

## 5. Theorem-Hypothesenmatrix

| Hypothese | H4R4-Stand |
|---|---|
| symmetrisch-hyperbolischer Principal-Sektor | **PASS** aus H4R3 |
| uniform positives `A0` auf kompakter Domäne | **PASS** aus H4R3 |
| maximal konservativer Principal-Randraum | **PASS** aus H4R3 |
| konstanter Principal-Boundary-Rang | **PASS** auf `Z_F>0`-Domäne |
| exakte gauge-fixierte Koeffizientenmaps | **NICHT exportiert** |
| vollständige nonlinear boundary map | **teilweise im Cap-Ledger, kein Jet-Export** |
| Kompatibilität bis notwendige Ordnung | **nicht prüfbar** |
| exakte constraint-preserving Randclosure | **konditional/formal, nicht jet-ratifiziert** |
| lokaler Existenz-/Eindeutigkeitssatz | **NOT_RATIFIED** |

Der wissenschaftlich richtige H4R4-Beschluss lautet deshalb nicht `FAIL` des Parentmodells, sondern:

\[
\boxed{
\texttt{THEOREM\_PROMOTION\_BLOCKED\_PENDING\_EXACT\_COEFFICIENT\_AND\_BOUNDARY\_JET\_EXPORT}
}
\]

Das ist ein konkreter, kleinerer Blocker als vor H4R1–H4R3: Principal-Hyperbolizität und Principal-Randstabilität sind nicht mehr die offenen Punkte; offen ist jetzt die **vollständige lower-order und Kompatibilitäts-Implementierung**.

## 6. Manufactured Solution Method — nur Codeverifikation

H4R4 friert außerdem den späteren Manufactured-Solution-Test vor, führt ihn aber nicht aus.

Wir wählen auf einem kompakten Rechteck glatte analytische Felder

\[
U_s^{\rm MMS}(\tau,x_s)
\]

mit

\[
a>0,\qquad L>0,\qquad Z_F(\varphi)>0.
\]

Dann werden nicht die physikalischen Gleichungen verändert, sondern die für diese künstliche Lösung notwendigen Testquellen **aus dem exakten Operator berechnet**:

\[
\boxed{
f_s^{\rm MMS}=\mathcal E_s[U_s^{\rm MMS}]}
\]

und am Interface

\[
\boxed{
g_\Sigma^{\rm MMS}
=\mathcal B[U_N^{\rm MMS},U_S^{\rm MMS},Q_N^{\rm MMS},Q_S^{\rm MMS}].}
\]

Damit ist die gewählte analytische Funktion per Konstruktion eine Lösung des **manufactured test problem**, nicht des physikalisch homogenen M1-Problems.

### Erforderliche spätere Verifikation

Vor einer Ausführung müssen separat eingefroren werden:

1. Diskretisierungsordnung \(p\),
2. mindestens drei Gitterverfeinerungen,
3. \(L^2\)- und \(L^\infty\)-Bulkfehler,
4. Cap-Residualnorm,
5. Constraint-Residualnorm,
6. Patch-/Flux-Residual im Gauge-Testzweig,
7. zulässige Abweichung der beobachteten von der formalen Konvergenzordnung.

Verboten bleiben Clipping, manuelles Vorzeichenumschalten, nachträgliche Toleranzlockerung oder das Unterdrücken nichtkonvergenter Residuen.

Ein späterer MMS-PASS bedeutet ausschließlich:

\[
\boxed{\text{Code reproduces a known manufactured solution at the declared order}.}
\]

Er bedeutet **nicht**:

\[
\text{physikalische Parent-Lösung},
\quad
\text{D2N-Q-Selektion},
\quad
\text{Ghostfreiheit},
\quad
\text{Evidenz}.
\]

## 7. H4R4-Gateentscheidung

H4R4 ist als Audit abgeschlossen, aber die gewünschte Theorem-Ratifizierung wird bewusst **nicht** erteilt.

Aktueller Stand:

- `exact_compatibility_structure = DEFINED`
- `exact_compatibility_jets = BLOCKED_PENDING_FIRST_ORDER_COEFFICIENT_AND_BOUNDARY_JET_EXPORT`
- `local_quasilinear_IBVP_theorem = NOT_RATIFIED`
- `manufactured_solution_protocol = FROZEN_NOT_EXECUTED`
- `physical_parent_solve_authorized = false`
- `D2NQ_parent_dynamic_selection = OPEN_NOT_EXECUTED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `WP4 = BLOCKED`
- `physical evidence = NONE`

## 8. Nächster Block

Der nächste Schritt ist jetzt eindeutig kleiner und konstruktiver als ein Solverlauf:

`C-PHYS-PARENT-H4R4A-EXACT-GAUGE-FIXED-FIRST-ORDER-COEFFICIENT-EXPORT-BOUNDARY-JET-GENERATOR-AND-INDEPENDENT-THEOREM-REVIEW`

H4R4A muss die exakte gauge-fixierte erste-Ordnungsform samt lower-order-Terms generieren, die vollständige nonlinear boundary map exportieren und daraus die Kompatibilitätsjets maschinenlesbar erzeugen. Erst danach darf die lokale IBVP-Theoremfrage erneut mit PASS/FAIL entschieden werden.

## Referenzrahmen für die spätere Theoremprüfung

- P. Secchi, *Well-posedness of characteristic symmetric hyperbolic systems*, Archive for Rational Mechanics and Analysis **134** (1996), 155–197, DOI 10.1007/BF00379552.
- P. Secchi, *Linear symmetric hyperbolic systems with characteristic boundary*, Mathematical Methods in the Applied Sciences **18** (1995), 855–870, DOI 10.1002/mma.1670181103.
- G. Métivier, K. Zumbrun, *Hyperbolic Boundary Value Problems for Symmetric Systems with Variable Multiplicities*, Journal of Differential Equations **211** (2005), 61–134.

Diese Arbeiten werden ausschließlich als mathematischer Hypothesenrahmen verwendet; sie ersetzen keine projektspezifische Ableitung oder Prüfung.
