# HZT-M0 / S6 / C-PHYS — H4R4A Exact Gauge-Fixed First-Order Export, Boundary-Jet Generator and Theorem Review v0.1

**Datum:** 2026-08-15  
**Block:** `C-PHYS-PARENT-H4R4A-EXACT-GAUGE-FIXED-FIRST-ORDER-COEFFICIENT-EXPORT-BOUNDARY-JET-GENERATOR-AND-INDEPENDENT-THEOREM-REVIEW`  
**Baseline main:** `5fb7b95dcf214c6fa022745c0bcc426ca469a91f`  
**Status:** `PASS_EXACT_CONFORMAL_GAUGE_BULK_BOUNDARY_JET_EXPORT_LOCAL_REDUCED_IBVP_THEOREM_CONDITIONAL_RATIFICATION_NO_PHYSICAL_EXECUTION`  
**Solverausführung:** nein  
**MMS-Ausführung:** nein  
**Physische Evidenzwirkung:** `NONE`

## 1. Zweck und Firewall

H4R4 hat die lokale Existenz-/Eindeutigkeitsfrage bewusst nicht ratifiziert, weil drei Dinge noch nicht gemeinsam als auditiertes Objekt vorlagen:

1. der vollständige gauge-fixierte Lower-Order-Bulkvektor `F_s(W)`,
2. die vollständige nichtlineare lokale Kappenabbildung,
3. ein exakter Generator der Rand-Zeitjets für die Kompatibilitätshierarchie.

H4R4A exportiert diese drei Objekte nun für einen **lokalen, an die zeitartige Kappe angepassten konformen 1+1-Chart**. Es wird weder ein physischer PDE-Lauf noch ein Manufactured-Solution-Test ausgeführt.

Gemini-Material bleibt strikt `EXTERNAL_UNVERIFIED_GEMINI_DRAFT`. Keine Gemini-Gleichung und kein Gemini-Code wird als Prämisse oder Validierung verwendet. Die kanonische Signatur bleibt

\[
(-,+,+,+,+,+),
\]

mit genau **einer** physikalischen Zeit.

## 2. Lokaler konformer Chart und dimensionslose Variablen

Auf jeder Seite `s in {N,S}` wird lokal

\[
h_{pq}^{(s)}dx^pdx^q=e^{2\omega_s}\left(-d\tau^2+dx_s^2\right)
\]

verwendet. Der Koordinatenwert `x_s=0` liegt an der Kappe und `x_s>0` wächst **von der Kappe weg in die jeweilige Bulkregion**.

Damit lautet die dimensionslose outward-Normalableitung

\[
\boxed{\nu_s[f]\equiv-e^{-\omega_s}\partial_{x_s}f}
\]

und ist mit der H4/H4R2-Outward-Sum-Konvention verträglich.

Die H4R1-Variablen werden exakt beibehalten:

\[
U_s=(\omega_s,u_s,v_s,\varphi_s,a_{\chi,s})^T,
\]

\[
\bar a_s=\bar a_{\rm ref}e^{u_s},\qquad
\ell_s=\ell_{\rm ref}e^{v_s},\qquad
\varphi=\phi/M_6^2,\qquad
a_\chi=A_\chi/M_6.
\]

Die Referenzskalen `abar_ref=M6*a_ref>0` und `ell_ref=M6*L_ref>0` werden im lokalen Chart auf beiden Seiten gemeinsam gewählt. Das ist eine Normalisierung, kein neuer physikalischer Parameter.

Für M1 gilt

\[
Z_F=e^{-2a_F\varphi},\qquad z\equiv\frac{Z_F}{\ell^2}>0.
\]

## 3. Exakte reduzierte konforme Wirkung

Setze

\[
S\equiv\bar a^3\ell,\qquad \hat\kappa_6^2\equiv\kappa_6^2M_6^4.
\]

Bis auf die bereits in H4 entfernten konstanten Volumenfaktoren lautet die gauge-fixierte dimensionslose 1+1-Lagrangedichte

\[
\boxed{\begin{aligned}
\mathcal L_{\rm conf}=S\Bigg\{&
\frac{1}{\hat\kappa_6^2}\Big[
3\,\partial u\!\cdot\!\partial\omega
+\partial v\!\cdot\!\partial\omega
+3(\partial u)^2
+3\,\partial u\!\cdot\!\partial v
\Big]\\
&-\frac12(\partial\varphi)^2
-\frac12 z(\partial a_\chi)^2\\
&+e^{2\omega}\left[
\frac{1}{\hat\kappa_6^2}\left(\frac{3k}{\bar a^2}-\hat\Lambda\right)
-\frac12\hat m_\phi^2\varphi^2
\right]\Bigg\}.
\end{aligned}}
\]

Hier bezeichnet der Punkt die Kontraktion mit der 1+1-Minkowski-Metrik,

\[
\partial X\!\cdot\!\partial Y=-\partial_\tau X\,\partial_\tau Y+\partial_xX\,\partial_xY.
\]

Diese Lagrangedichte wurde unabhängig aus der kanonischen H4-2D-Wirkung hergeleitet.

## 4. Exakter First-Order-Export

Definiere

\[
P_s=\partial_\tau U_s,\qquad Q_s=\partial_{x_s}U_s
\]

und

\[
\mathcal D_{XY}\equiv Q_XQ_Y-P_XP_Y.
\]

Die Evolutionsform ist

\[
\boxed{\partial_\tau U=P,\qquad \partial_\tau P=\partial_xQ+F(U,P,Q),\qquad \partial_\tau Q=\partial_xP.}
\]

Damit ist der in H4R4 fehlende Lower-Order-Vektor `F` im konformen Chart vollständig:

\[
\boxed{\begin{aligned}
F_\omega={}&-3\mathcal D_{uu}-3\mathcal D_{uv}
+\frac{\hat\kappa_6^2}{2}\mathcal D_{\varphi\varphi}
+\frac{\hat\kappa_6^2z}{4}\mathcal D_{AA}\\
&+e^{2\omega}\left[
\frac{3k}{\bar a^2}-\frac{\hat\Lambda}{2}
-\frac{\hat\kappa_6^2\hat m_\phi^2\varphi^2}{4}
\right],
\end{aligned}}
\]

\[
\boxed{F_u=3\mathcal D_{uu}+\mathcal D_{uv}-\frac{\hat\kappa_6^2z}{4}\mathcal D_{AA}+e^{2\omega}\left[\frac{\hat\Lambda}{2}+\frac{\hat\kappa_6^2\hat m_\phi^2\varphi^2}{4}-\frac{2k}{\bar a^2}\right],}
\]

\[
\boxed{F_v=3\mathcal D_{uv}+\mathcal D_{vv}+\frac{3\hat\kappa_6^2z}{4}\mathcal D_{AA}+e^{2\omega}\left[\frac{\hat\Lambda}{2}+\frac{\hat\kappa_6^2\hat m_\phi^2\varphi^2}{4}\right],}
\]

\[
\boxed{F_\varphi=3\mathcal D_{u\varphi}+\mathcal D_{v\varphi}+a_Fz\mathcal D_{AA}-\hat m_\phi^2e^{2\omega}\varphi,}
\]

\[
\boxed{F_A=3\mathcal D_{uA}-\mathcal D_{vA}-2a_F\mathcal D_{\varphi A}.}
\]

Der Validator rekonstruiert diese fünf Formeln unabhängig aus Feldraummetrik, Potential und Euler-Lagrange-Gleichung mittels komplexer Schrittableitungen an mehreren deterministischen Testpunkten. Dies ist **Formelverifikation**, kein PDE-Lauf.

## 5. Exakte Constraint-Maps im deklarierten Gauge

Die gemischte Parent-Gleichung aus H4 liefert nach dem konformen Gauge

\[
\boxed{\begin{aligned}
C_M={}&-3\left[\partial_xP_u+P_uQ_u-Q_\omega P_u-P_\omega Q_u\right]\\
&-\left[\partial_xP_v+P_vQ_v-Q_\omega P_v-P_\omega Q_v\right]\\
&-\hat\kappa_6^2\left(P_\varphi Q_\varphi+zP_AQ_A\right)=0.
\end{aligned}}
\]

Die `tt`-Projektion ergibt

\[
\boxed{\begin{aligned}
C_H={}&-3\partial_xQ_u-\partial_xQ_v
+3P_u^2+3P_uP_v+3P_uP_\omega+P_vP_\omega\\
&-6Q_u^2-3Q_uQ_v+3Q_uQ_\omega-Q_v^2+Q_vQ_\omega\\
&+\frac{3ke^{2\omega}}{\bar a^2}-\hat\Lambda e^{2\omega}\\
&-\frac{\hat\kappa_6^2}{2}(P_\varphi^2+Q_\varphi^2)
-\frac{\hat\kappa_6^2z}{2}(P_A^2+Q_A^2)
-\frac{\hat\kappa_6^2}{2}\hat m_\phi^2\varphi^2e^{2\omega}=0.
\end{aligned}}
\]

Diese beiden Gleichungen sind jetzt als konkrete Funktionen von `W` und radialen Ableitungen exportiert. Daraus folgt noch **keine** Existenz global constraint-kompatibler Anfangsdaten.

## 6. Exakte lokale Kappenabbildung

Für die lokale Theoremabbildung wird der Gaugepatch an der Kappe zunächst ausgerichtet. Die globale Patchbedingung

\[
R_{\rm patch}=a_{\chi,N}^{\rm original}-a_{\chi,S}^{\rm original}-\frac{N_F}{\hat q}
\]

bleibt ein separater globaler Kanal.

Die fünf lokalen Stetigkeitsbedingungen lauten

\[
\Delta U=0.
\]

Die outward sums sind

\[
K_\omega=\nu_N[\omega]+\nu_S[\omega],\quad
K_u=\nu_N[u]+\nu_S[u],\quad
K_v=\nu_N[v]+\nu_S[v],\quad
K_\varphi=\nu_N[\varphi]+\nu_S[\varphi].
\]

Mit

\[
q_{\rm cap}=m_\sigma\hat q,\qquad d_\chi=N_\sigma-q_{\rm cap}a_{\chi,\Sigma},
\]

\[
\hat Y_\sigma=\hat z_\sigma\frac{d_\chi^2}{\ell_\Sigma^2}
\]

lauten die drei metrischen Residuen

\[
\boxed{R_1=-(3K_u+K_v)+\hat\kappa_6^2\left(\hat\lambda+\frac12\hat Y_\sigma\right),}
\]

\[
\boxed{R_2=-(K_\omega+2K_u+K_v)+\hat\kappa_6^2\left(\hat\lambda+\frac12\hat Y_\sigma\right),}
\]

\[
\boxed{R_3=-(K_\omega+3K_u)+\hat\kappa_6^2\left(\hat\lambda-\frac12\hat Y_\sigma\right).}
\]

Für M1 ist das skalare Matching

\[
\boxed{R_\varphi=K_\varphi.}
\]

Das dynamische Gauge-Matching ist

\[
\boxed{R_A=\sum_s z_s\nu_s[a_\chi]-q_{\rm cap}\hat z_\sigma\frac{d_\chi}{\ell_\Sigma^2}.}
\]

Damit besitzt die lokale nichtlineare Randabbildung genau zehn Zeilen:

\[
\boxed{\mathcal B_{\rm loc}=(\Delta U,R_1,R_2,R_3,R_\varphi,R_A)^T.}
\]

Für Ableitungen außerhalb der Stetigkeitsmannigfaltigkeit wird die symmetrische glatte Erweiterung

\[
U_\Sigma=\frac12(U_N+U_S)
\]

verwendet. Auf physikalisch zulässigen Randdaten gilt ohnehin `U_N=U_S`; die Wahl der glatten Erweiterung ändert daher die Nullmenge und die Kompatibilitätsjets auf dieser Mannigfaltigkeit nicht.

Der Normal-Jacobian jeder Seite ist

\[
\boxed{\frac{\partial(R_1,R_2,R_3,R_\varphi,R_A)}{\partial Q_s}=-e^{-\omega_s}\operatorname{blockdiag}(B_g,1,z_s),}
\]

mit

\[
B_g=\begin{pmatrix}0&-3&-1\\-1&-2&-1\\-1&-3&0\end{pmatrix},\qquad \det B_g=-4.
\]

Da `z_s>0`, bleibt der Normalrang exakt fünf.

## 7. Exakter Boundary-Jet-Generator

Definiere den Evolutionsoperator

\[
\mathfrak T U=P,\qquad \mathfrak T P=\partial_xQ+F(U,P,Q),\qquad \mathfrak T Q=\partial_xP.
\]

Für glatte Lösungen kommutiert `T` mit `partial_x`. Die Kompatibilitätsjets werden jetzt rekursiv definiert durch

\[
\boxed{\mathcal J_0=\mathcal B_{\rm loc},\qquad \mathcal J_{j+1}=\mathfrak T[\mathcal J_j].}
\]

Insbesondere

\[
\boxed{\mathfrak T\nu_s[I]=-e^{-\omega_s}\left(\partial_xP_{I,s}-P_{\omega,s}Q_{I,s}\right).}
\]

Weiter gilt exakt

\[
\boxed{\mathfrak T z_s=z_s(-2a_FP_{\varphi,s}-2P_{v,s}),}
\]

\[
\boxed{\mathfrak T d_\chi=-q_{\rm cap}P_{A,\Sigma},}
\]

und

\[
\boxed{\mathfrak T\hat Y_\sigma=-\frac{2\hat z_\sigma}{\ell_\Sigma^2}\left(d_\chi^2P_{v,\Sigma}+q_{\rm cap}d_\chi P_{A,\Sigma}\right).}
\]

Der erste Jet ist damit vollständig durch `U,P,Q,partial_x P` bestimmt. Ab dem zweiten Jet tritt `F` über

\[
\partial_\tau P=\partial_xQ+F
\]

ein. Genau deshalb war der vollständige Lower-Order-Export aus H4R4 notwendig.

Für Sobolevordnung `m>=3` bleibt die Datenbedingung

\[
\boxed{\mathcal J_j|_{\tau=0}=0,\qquad j=0,\ldots,m-1.}
\]

H4R4A behauptet nicht, dass beliebige oder bereits vorhandene physikalische Anfangsdaten diese Bedingungen erfüllen. Es liefert nun den Operator, mit dem dies **ohne freie Konventionswahl** geprüft werden kann.

## 8. Unabhängige Theoremprüfung

Für die Theoremprüfung werden drei klassische Primärquellen als Referenzklasse verwendet:

- P. D. Lax und R. S. Phillips, *Local boundary conditions for dissipative symmetric linear differential operators*, Commun. Pure Appl. Math. 13 (1960), DOI `10.1002/cpa.3160130307`.
- P. Secchi, *Well-posedness of characteristic symmetric hyperbolic systems*, Arch. Rational Mech. Anal. 134 (1996), DOI `10.1007/BF00379552`.
- H.-O. Kreiss, O. Reula, O. Sarbach, J. Winicour, *Boundary Conditions for Coupled Quasilinear Wave Equations with Application to Isolated Systems*, Commun. Math. Phys. 289 (2009), arXiv `0807.3207`.

H4R3 liefert für den Ableitungszustand `Y=(P,Q)`

\[
A^0=\begin{pmatrix}D&0\\0&D\end{pmatrix},\qquad A^1=\begin{pmatrix}0&-D\\-D&0\end{pmatrix}
\]

im konformen Chart, mit

\[
D=\operatorname{diag}(1,1,1,1,z)>0.
\]

Nimmt man `U` als zusätzlichen tangentialen ODE-Block auf,

\[
\partial_\tau U=P,
\]

entstehen am Rand Nullgeschwindigkeitsmoden konstanter Multiplizität. Die nichtzero-charakteristische Ableitungsunterstruktur bleibt unverändert.

Auf der Stetigkeitsmannigfaltigkeit gilt wegen `varphi_N=varphi_S` und `v_N=v_S`

\[
D_N=D_S.
\]

Die zeitliche Ableitung der Konfigurationstetigkeit gibt

\[
P_N=P_S.
\]

Der homogene Hauptteil der Junctionbedingungen ist

\[
D_NQ_N+D_SQ_S=0.
\]

Damit verschwindet der kombinierte Randfluss exakt:

\[
P_N^TD_NQ_N+P_S^TD_SQ_S=P_\Sigma^T(D_NQ_N+D_SQ_S)=0.
\]

Der Randunterraum hat zehn Bedingungen für zwanzig nichtzero-charakteristische Ableitungsvariablen und ist damit maximal konservativ beziehungsweise maximal nichtpositiv für die kombinierte Energieform. Die nichtlinearen Kappenquellen sind auf

\[
\ell>0,\qquad z>0
\]

glatt.

### H4R4A-Theoremstatus

Daraus wird **nur** folgender konditionaler Satz ratifiziert:

> Für hinreichend glatte Anfangsdaten des reduzierten H4R4A-Systems, deren Werte in einem kompakten nichtdegenerierten Zustandsbereich mit `abar>0`, `ell>0`, `z>0` liegen und die die erforderliche Kompatibilitätshierarchie erfüllen, ist der lokale gauge-fixierte zweiseitige Transmissions-IBVP analytisch in der Klasse quasilinearer symmetrisch-hyperbolischer/maximal-dissipativer Systeme einzuordnen. Existenz, Eindeutigkeit und stetige Datenabhängigkeit gelten lokal in der entsprechenden reduzierten Problemklasse.

Klassifikation:

\[
\boxed{\text{LOCAL REDUCED IBVP THEOREM}=\texttt{PASS\_CONDITIONAL\_ANALYTIC}}
\]

Das ist **nicht** gleichbedeutend mit

\[
\boxed{\text{GLOBAL PHYSICAL M1 BACKGROUND EXISTS}.}
\]

Der lokale Satz erzeugt insbesondere nicht automatisch global fluxquantisierte Daten, Pole-/Kappenregularität auf einer vollständigen internen Mannigfaltigkeit, eine konkrete constraint-satisfying physikalische Anfangsdatenfamilie, D2N-Q-Selektion, Hamilton-Positivität oder Ghostfreiheit.

## 9. Validierungsumfang

Der H4R4A-Validator führt nur algebraische und lokale Formeltests aus:

1. unabhängige Euler-Lagrange-Rekonstruktion des exportierten `F`-Vektors,
2. Normalrang und exakte Hauptteil-Flussauslöschung,
3. unabhängiger Finite-Difference-Chain-Rule-Test des ersten Rand-Zeitjets,
4. Governance- und Gemini-Firewall.

Es gibt **keine** Zeitintegration, keinen BVP-Solve, keinen MMS-Lauf und keinen physikalischen Backendimport.

## 10. Gate-Disposition

\[
\boxed{\text{exact gauge-fixed bulk export}=\mathrm{PASS}}
\]

\[
\boxed{\text{exact local boundary map}=\mathrm{PASS}}
\]

\[
\boxed{\text{boundary jet generator}=\mathrm{PASS\ formal}}
\]

\[
\boxed{\text{local reduced IBVP theorem}=\mathrm{PASS\ conditional\ analytic}}
\]

Dagegen bleiben

\[
\boxed{\text{full parent global background existence}=\mathrm{OPEN}},
\]

\[
\boxed{\text{physical parent solve authorization}=\mathrm{FALSE}},
\]

\[
\boxed{\text{D2N-Q dynamic selection}=\mathrm{OPEN\_NOT\_EXECUTED}},
\]

\[
\boxed{\text{Hamiltonian positivity}=\mathrm{OPEN},\qquad \text{ghost freedom}=\mathrm{OPEN}},
\]

\[
\boxed{K1\!-\!D=\mathrm{NOT\_RELEASED},\quad K1\!-\!E=\mathrm{NOT\_ADMISSIBLE},\quad WP4=\mathrm{BLOCKED},\quad \text{physical evidence}=\mathrm{NONE}.}
\]

## 11. Nächster Kandidat

`C-PHYS-PARENT-H4R4B-ADMISSIBLE-CONSTRAINT-SATISFYING-INITIAL-DATA-CONSTRUCTION-GLOBAL-SECTOR-CLOSURE-AND-FULL-PARENT-EQUIVALENCE-AUDIT`

Der nächste Block muss erstmals die **Existenz einer nichtleeren Menge zulässiger Anfangsdaten** untersuchen, die gleichzeitig `C_H=C_M=0`, alle lokalen Kappenbedingungen, die Kompatibilitätsjets, den diskreten Patch-/Fluxsektor und die globale Pole-/Kappenregularität erfüllen.

Auch H4R4B darf daraus nicht automatisch eine physikalische Solverfreigabe ableiten.
