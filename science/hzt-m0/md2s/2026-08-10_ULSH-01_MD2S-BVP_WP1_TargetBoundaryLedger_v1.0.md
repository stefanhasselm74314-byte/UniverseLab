# ULSH-01 · MD2S-BVP · WP1 Target- und Randbedingungsabschluss v1.0

## Status

`WP1_TARGET_EQUATION_AND_BOUNDARY_CONTRACT_CLOSED_SPECIFICATION_ONLY`

Dieser Abschluss konsolidiert den bereits kanonisch eingefrorenen C-PHYS-M1-Modell-, Operator-, Pol-, Topologie-, Orientierungs- und Randdatenstand in **einen solver-facing Vertrag**. Er erzeugt **keine Solverfreigabe** und **keinen physischen Hintergrund**.

- `BACKGROUND_SOLVER_EXECUTION = NOT_AUTHORIZED`
- `CP01R1 = NOT_AUTHORIZED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`

Der ULSH-Masterplan definiert WP1 als „Targetgleichungs- und Randbedingungsvertrag aus kanonischem M1 schließen“. Genau diese Spezifikationslücke wird hier geschlossen; WP2 bleibt separat.

## 1. Theorie-Skelett

### Postulate / Modellselektion

Aktiv ist der zweiregionale 6D-C-PHYS-M1-Kandidat mit Einstein-Skalar-Maxwell-Bulk und einer gemeinsamen lokalisierten Cap-Phase. Die M1-Funktionsfamilie ist **versionierte Modellselektion**, keine Herleitung aus Hyperzeit-Erstprinzipien.

Dimensionlose Variablen:

`x_s=M6 r_s`, `ell_s=M6 L_s`, `varphi_s=phi_s/M6^2`, `a_chi_s=A_chi_s/M6`,
`q_s=Q_s/M6^3`, `k4=K4/M6^2`, `Lambda_hat=Lambda6/M6^2`.

Exakte M1-Funktionen:

`U=0.5 mhat_phi_sq M6^6 varphi^2`

`Z_phi=1`

`Z_F=exp(-2 a_F varphi)`

`lambda=lambda_hat M6^5`

`Z_sigma=z_sigma_hat M6^3`

`q_ref=q_hat/M6`, `q_sigma=m_sigma q_ref`.

Aktive Parameterdomänen:

`mhat_phi_sq>0`, `a_F>0`, `z_sigma_hat>0`, `q_hat>0`, `M6>0`, während `Lambda_hat, lambda_hat in R`.

### Dynamik

Für jede Region `s in {N,S}`:

`rho_F_s = 0.5 q_s^2 exp(-8 A_s + 2 a_F varphi_s)`.

Die vier unabhängigen Bulkgleichungen sind

`E_A_s = 4 A_s,xx + 10 A_s,x^2 - 6 k4 exp(-2 A_s) + Lambda_hat + 0.5 varphi_s,x^2 + 0.5 mhat_phi_sq varphi_s^2 - rho_F_s = 0`

`E_ell_s = ell_s,xx + 3 A_s,xx ell_s + 6 A_s,x^2 ell_s + 3 A_s,x ell_s,x - 3 k4 exp(-2 A_s) ell_s + Lambda_hat ell_s + ell_s(0.5 varphi_s,x^2 + 0.5 mhat_phi_sq varphi_s^2 + rho_F_s) = 0`

`E_varphi_s = ell_s varphi_s,xx + (4 A_s,x ell_s + ell_s,x) varphi_s,x - ell_s mhat_phi_sq varphi_s + 2 a_F ell_s rho_F_s = 0`

`E_gauge_s = a_chi_s,x - q_s ell_s exp(-4 A_s + 2 a_F varphi_s) = 0`.

Der `rr`-Constraint ist **kein fünfter Bulk-Residual**:

`C_rr_s = ell_s[-6 k4 exp(-2 A_s)+6 A_s,x^2+Lambda_hat] + 4 A_s,x ell_s,x - ell_s[0.5 varphi_s,x^2 - 0.5 mhat_phi_sq varphi_s^2 + rho_F_s]`.

Die symbolisch geschlossene Abhängigkeit lautet

`C_rr_s,x + 4 A_s,x C_rr_s = ell_s,x E_A_s + 4 A_s,x E_ell_s - varphi_s,x E_varphi_s`.

Auf dem unabhängigen System folgt daher

`C_rr_s,x = -4 A_s,x C_rr_s`

und somit

`C_rr_s(x)=C_rr_s(x0) exp[-4(A_s(x)-A_s(x0))]`.

**Status:** bewiesen, konditional auf Maxwell-Erstintegral, Differenzierbarkeit und regulären Polgrenzwert.

## 2. Pol- und Funktionsraumvertrag

Beide lokalen Radialkoordinaten laufen vom glatten Pol zur gemeinsamen Cap:

`x_N in [0,rho_N]`, `x_S in [0,rho_S]`.

Mit `tau in [0,1]` und `x_s=rho_s sqrt(tau)` wird die reguläre Paritätsklasse fest eingebaut:

North:

`A_N=tau u_A_N(tau)`

`ell_N=rho_N sqrt(tau)[1+tau u_ell_N(tau)]`

`varphi_N=varphi_N0+tau u_varphi_N(tau)`

`a_chi_N=tau u_g_N(tau)`.

South:

`A_S=A_S0+tau u_A_S(tau)`

`ell_S=rho_S sqrt(tau)[1+tau u_ell_S(tau)]`

`varphi_S=varphi_S0+tau u_varphi_S(tau)`

`a_chi_S=tau u_g_S(tau)`.

Damit sind automatisch gebunden:

- `A_N(0)=0` als 4D-Framefixierung,
- `A_N,x(0)=A_S,x(0)=0`,
- `ell_N(0)=ell_S(0)=0`,
- `ell_N,x(0)=ell_S,x(0)=1`,
- `varphi_N,x(0)=varphi_S,x(0)=0`,
- `a_chi_N(0)=a_chi_S(0)=0`.

`Delta_chi=2 pi`; konische Poldefekte sind im aktiven Vertrag ausgeschlossen.

Der Hauptteil des Operators hat Determinante `4 ell`. Daher ist der Operator im Inneren für `ell>0` vollrangig, während `ell->0` am Pol ein regulär-singulärer Endpunkt ist. Die Paritätsfaktorisierung ist deshalb Teil der Operatordomäne und nicht bloß ein numerischer Seed-Trick.

Die Profilräume bleiben

`X_s = h^(2,alpha_H)^3 x h^(1,alpha_H)`, `0<alpha_H<1`,

mit `X_prof=X_N x X_S` und regulisiertem Bulkziel `Y_bulk=h^(0,alpha_H)^4 x h^(0,alpha_H)^4`.

## 3. Solver-facing Bulkziel

Die am Pol regulisierten Komponenten sind

`F_A_s = E_A_s`

`F_ell_s = E_ell_s/ell_s` mit stetiger `tau=0`-Fortsetzung

`F_varphi_s = E_varphi_s/ell_s` mit stetiger `tau=0`-Fortsetzung

`F_gauge_s = E_gauge_s/sqrt(tau)` mit stetiger `tau=0`-Fortsetzung.

Feste Reihenfolge:

`[F_A_N,F_ell_N,F_varphi_N,F_gauge_N,F_A_S,F_ell_S,F_varphi_S,F_gauge_S]`.

Für `N` Lobatto-Punkte je Region gilt der korrigierte diskrete Aufbau:

- Profilunbekannte: `8N`
- augmentierte Unbekannte: `8`
- Bulkresiduen an **allen** Knoten: `8N`
- Cap-/Globalresiduen zusätzlich: `8`
- Gesamt: `8N+8` Unbekannte gegen `8N+8` Residuen.

Kein Bulkrow wird durch eine Randgleichung ersetzt. `C_rr` wird nicht angehängt.

## 4. Augmentierte kontinuierliche Unbekannte

Feste Reihenfolge:

`p = (varphi_N0, q_N, A_S0, varphi_S0, q_S, rho_N, rho_S, k4)`.

Damit: **8 kontinuierliche augmentierte Unbekannte**.

Nicht darin enthalten sind die sechs Modellformparameter

`(Lambda_hat,mhat_phi_sq,a_F,lambda_hat,z_sigma_hat,q_hat)`,

die innerhalb einer Modellinstanz extern fixiert bleiben.

Diskreter Sektor:

`(N_F,N_sigma,m_sigma)`, mit `N_F,N_sigma in Z`, `m_sigma in Z_(>0)`.

Die frühere regionale Fünfer-Duplizierung `(N_F,m_N,m_S,n_N,n_S)` ist kanonisch korrigiert und für M1 verboten.

## 5. Orientierung und globale U(1)-Struktur

Lokale outward normals an der gemeinsamen Cap:

`n_N^x=+1`, `n_S^x=+1`.

Globale Zweiform-Orientierung:

`epsilon_N=+1`, `epsilon_S=-1`.

Diese beiden Vorzeichensysteme dürfen nicht vermischt werden.

Reguläre Polgauge:

`a_chi_N(0)=a_chi_S(0)=0`.

Patchrelation an der Cap:

`R_patch = a_chi_N(rho_N)-a_chi_S(rho_S)-N_F/q_hat = 0`.

Unter diesen Konventionen ist globale Fluxquantisierung äquivalent zur Patchbedingung und wird **nicht ein zweites Mal** als unabhängige Randbedingung gezählt.

## 6. Cap-Traces und acht unabhängige Randresiduen

Definiere

`A_hat_Sigma = A_N,x(rho_N)+A_S,x(rho_S)`,

`L_hat_Sigma = ell_N,x(rho_N)/ell_N(rho_N) + ell_S,x(rho_S)/ell_S(rho_S)`,

`ell_Sigma = ell_N(rho_N)=ell_S(rho_S)>0` nach Kontinuität.

Für den lokalisierten Cap-Chart wird

`a_chi_Sigma := a_chi_N(rho_N)`,

`d_chi = N_sigma - m_sigma q_hat a_chi_Sigma`,

`Y_hat_sigma = z_sigma_hat d_chi^2/ell_Sigma^2`.

Die feste Residualreihenfolge ist:

1. `R_A = A_N(rho_N)-A_S(rho_S) = 0`
2. `R_ell = ell_N(rho_N)-ell_S(rho_S) = 0`
3. `R_varphi = varphi_N(rho_N)-varphi_S(rho_S) = 0`
4. `R_patch = a_chi_N(rho_N)-a_chi_S(rho_S)-N_F/q_hat = 0`
5. `R_4d = -3 A_hat_Sigma - L_hat_Sigma + lambda_hat + 0.5 Y_hat_sigma = 0`
6. `R_chi = -4 A_hat_Sigma + lambda_hat - 0.5 Y_hat_sigma = 0`
7. `R_scalar = varphi_N,x(rho_N)+varphi_S,x(rho_S) = 0`
8. `R_gauge_local = q_N exp[-4A_N(rho_N)]/ell_Sigma + q_S exp[-4A_S(rho_S)]/ell_Sigma - m_sigma q_hat z_sigma_hat d_chi/ell_Sigma^2 = 0`.

Damit ist der strukturelle Count

`8 augmentierte kontinuierliche Unbekannte <-> 8 unabhängige Rand-/Globalresiduen`.

**Status:** `SQUARE_CONDITIONAL`, nicht Invertibilitätsbeweis.

Nicht zusätzlich:

- `R_flux`: identisch zum einmal gezählten Patch-/Flux-Topologiekanal,
- `C_rr_N`, `C_rr_S`: QA,
- Phasengleichung: automatisch für statisch-homogenen Winding-Ansatz.

## 7. Übergangsregime und Grenzfälle

### `a_F -> 0`

`Z_F -> 1`; der explizite Term `2 a_F ell rho_F` in der Skalargleichung verschwindet.

**Status:** deklarierter analytischer Entkopplungskontrollfall, **nicht** aktiver M1-Targetzweig und keine Identität mit C1-V.

### `mhat_phi_sq -> 0`

Grenze der aktiven Parameterdomäne. Ein leichter/langreichweitiger Skalar bzw. Verlust der schweren Skalar-Kontrolle kann auftreten.

**Status:** konditionaler Grenzfall außerhalb des aktiven M1-Innenraums.

### `z_sigma_hat -> 0`

Grenze des aktiven Winding-Zweigs; Cap-Anisotropie-Unterstützung kann verloren gehen.

### `k4 -> 0`

Formaler flacher 4D-Krümmungsgrenzfall: alle expliziten `k4 exp(-2A)`-Terme verschwinden.

**Kein Evidenzsprung:** daraus folgt nicht, dass ein regulärer globaler M1-BVP-Hintergrund mit `k4=0` existiert.

### schwacher Flux

Lokal gilt `rho_F=O(q_s^2)`. Ein physischer Run darf `q_s` jedoch nicht losgelöst von Topologie/Patchvertrag und Run-ID mutieren.

### stark gekrümmtes Regime

Diagnostisch beginnt es, wenn `|k4| exp(-2A)` mit `|Lambda_hat|`, `rho_F` und Skalarpotentialtermen vergleichbar oder größer wird. Ohne globale Lösung wird daraus keine asymptotische physische Branch-Aussage abgeleitet.

## 8. Was WP1 jetzt beweist — und was nicht

### bewiesen / formal geschlossen

- exakte M1-Bulkgleichungen und deren solver-facing Residualreihenfolge,
- symbolische `rr`-Constraint-Propagation,
- glatte Polparitätsklasse und regulisierte `tau`-Darstellung,
- lokale Normalen- und globale Zweiformorientierung,
- U(1)-Patch-/Fluxzählung ohne Doppelzählung,
- exakt acht unabhängige Rand-/Globalresiduen,
- `8N+8` gegen `8N+8` diskreter Assembly-Count.

### konditional

- `SQUARE_CONDITIONAL`,
- volle Innenrangigkeit des Hauptteils für `ell>0`,
- stetige Polfortsetzung innerhalb der eingefrorenen Paritätsklasse.

### offen

- Existenz eines M1-Hintergrunds,
- Eindeutigkeit,
- Fredholm-Eigenschaft,
- Kontinuums-Jacobianrang/-Invertierbarkeit,
- Konditionierung,
- perturbative Stabilität,
- Ghostfreiheit,
- physische Identifikation.

### blockiert

- CP01R1-Targetsolve,
- physischer Background-Release,
- alle physischen Downstream-Solverfreigaben,
- K1-D und K1-E.

## 9. WP2-Handoff

WP2 darf **Implementierung und Freigabefähigkeit vorbereiten**, aber noch nicht automatisch physisch ausführen. Der nächste Vertrag muss mindestens binden:

1. diesen WP1-Vertrag samt Repository-/Commit-Identität,
2. den unveränderten CP01R1-Targetpayload,
3. einen source-bound `a_F=1/4`-Target-Entry-Point, der den `a_F=0`-Control-Override explizit verweigert,
4. die eingefrorene 7-Seed/35-Schedule,
5. Primary- und Independent-Backend-Hashes,
6. Resource Policy, Dependency Lock und Result Schema,
7. Single-Use-Grant mit Nonce, Zeitfenster, atomarem Verbrauch, Replay-Schutz und Crash-Semantik.

**WP1-Abschluss ≠ WP2-Freigabe ≠ Solverfreigabe.**
