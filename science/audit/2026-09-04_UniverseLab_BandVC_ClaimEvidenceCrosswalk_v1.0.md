# UniverseLab Band V-C — Claim → Equation/Code/Test/Data/Falsifier Crosswalk v1.0

**Datum:** 2026-09-04  
**Basis:** `main` commit `e4e92090d313abf8a53d7b7354923983c9cda939`  
**Modus:** nichtoperativer wissenschaftlicher Audit; keine physische Ausführung; keine Autorisierungs-/Grant-Ausstellung.

## 1. Zweck

Band V-A materialisierte 989 öffentliche Claim-Kandidaten und routete sie auf 15 Claim-Familien. Band V-B schloss die kontextuelle HIGH/MEDIUM-Adjudikation ohne physische Promotion. Band V-C prüft nun auf Familienebene die Evidenzkette:

`Claim → Gleichung/Herleitung → Code → Test → Daten → Falsifikator/Gate`

Fehlende Glieder werden nicht ergänzt oder aus benachbarten Artefakten inferiert. `NOT_APPLICABLE` ist ausdrücklich von `MISSING_REQUIRED_LINK` getrennt.

## 2. Ergebnisübersicht

Die 15 Familien zerfallen epistemisch in vier Gruppen:

1. **Geschlossene technische Referenzketten:** FLRW-Background, Krümmungsdistanzen, lineare GR-Growth-Referenz, reduzierte Bridge-Background-Implementierung und lokale `beta_tau I_B`-Identifizierbarkeit. Diese Ketten belegen Mathematik/Software/QA nur innerhalb ihres deklarierten Scopes.
2. **Fail-closed / offene physikalische Ketten:** Bridge-Perturbationen/Lensing, Parent→Reduced→Observable, physischer Background/Response Rank/Stabilität.
3. **Offene empirische Ketten:** versionierte Daten-/Kovarianz-/Selection-/Nuisance-Bindung und Likelihood/Robustness.
4. **Nichtphysikalische Familien:** Governance, FM-0-Projektstatus, Educational/Visual und Historical/Archive. Für sie sind Gleichungs-, Daten- oder Solverachsen teilweise `NOT_APPLICABLE` und dürfen nicht als Defekt gezählt werden.

## 3. Wissenschaftlich geschlossene Referenzketten

### 3.1 Standard-FLRW

Der kanonische Engine-Vertrag implementiert

`E^2(a)=Omega_r a^-4 + Omega_m a^-3 + Omega_k a^-2 + Omega_DE a^[-3(1+w)]`

mit

`Omega_k=1-Omega_r-Omega_m-Omega_DE`

und fail-closed Behandlung nichtpositiver bzw. nichtendlicher `E^2`-Zustände. Gleichung, Code und unabhängige numerische Tests sind vorhanden. Das ist eine Referenzkosmologie, keine HZT-Parentherleitung und keine empirische HZT-Bestätigung.

### 3.2 Krümmungsdistanzen

Die Kette

`D_C → D_M → D_L,D_A`

ist im kanonischen Engine-Code und in unabhängigen Tests gebunden. Etherington-Reziprozität und der flache Grenzfall sind QA-Falsifikatoren innerhalb der deklarierten FLRW-Annahmen.

### 3.3 Lineares GR-Wachstum

Für LCDM/constant-w ist die lineare GR-Referenzgleichung

`D'' + [2+d ln H/d ln a]D' - (3/2)Omega_m(a)D = 0`

mit `D(1)=1` implementiert und unabhängig getestet. Diese Gleichung darf nicht auf den Bridge/HZT-Pfad übertragen werden, solange keine freigegebene Perturbationsmap existiert.

### 3.4 Reduzierter Bridge-Background

Die reduzierte Diagnose

`E_B^2 = E_LCDM^2 (1+Delta)`

`Delta = beta_tau I_B exp[-(a/a_c)^2]`

`a_c = Rchi/(Rchi+2.5)`

ist als Codevertrag getestet. Der Link von der 6D-Parenttheorie zu `beta_tau`, `I_B`, `Rchi` und den Observablen ist dadurch nicht hergestellt.

### 3.5 Lokale Produktdegenerierung

Im derzeit implementierten Background-Kanal gilt

`A_B = beta_tau I_B`

und damit sind die beiden lokalen Jacobian-Spalten proportional. `rank J_(beta_tau,I_B) <= 1` ist innerhalb dieses reduzierten Kanals ein mathematischer Scope-Claim. Separate physikalische Identifizierbarkeit aus dem 6D-Sektor bleibt offen.

## 4. Offene physikalische und empirische Ketten

Das Missing-Link-Register materialisiert elf Lücken. Zehn davon sind wissenschaftlich/empirisch blockierend; eine ist reine Governance-Provenienz.

### P0: Bridge-Observablen

Keine freigegebene Bridge-Growth-, Poisson-, Slip- oder Lensing-Map. Vorhandene Tests beweisen die korrekte Verweigerung (`fail closed`), nicht die fehlende Physik.

### P0: Parent→Reduced→Observable

FM-G0 bleibt offen. Inventar und Gap-Register dokumentieren die fehlende Kette, ersetzen sie aber nicht. Eine vollständige Kette verlangt Parent-Gleichungen/Randbedingungen, Reduktion, Parameterprovenienz, Observable-Definitionen, Implementierung, Rank/Identifiability und unabhängige Validierung.

### P0: Physischer Background / Response Rank / Stabilität

`PHYSICAL_BACKGROUND=NOT_ESTABLISHED`, `PHYSICAL_RESPONSE_RANK=NOT_EXECUTED`, `K1-D=NOT_RELEASED`, `K1-E=NOT_ADMISSIBLE`. Formale Operator- und lokale IBVP-Arbeit bleibt `REFERENCE_ONLY` gegenüber globaler physischer Existenz, Kontinuumsinvertibilität, Hamiltonian-Positivität und voller Ghostfreiheit.

### P0: Daten und Likelihood

Für HZT-Empirie fehlt die gebundene Release-Kette aus Datenvektor, Kovarianz, Selection Function, Nuisance-Modell, Likelihood-Code, Priors und Robustness-/Recovery-Tests. Didaktische Punkte oder Kurvennähe sind ausdrücklich keine Evidenz.

### P0: Quantitative Vorhersagen/Falsifikatoren

RAR, Expansion, Growth, Lensing und GW sind Forschungsziele. Solange amplituden-/spektral-/parameterabhängige Parent-derived Maps und operative Rejection-Kriterien fehlen, sind sie keine simultan freigegebenen HZT-Vorhersagen.

## 5. P1 Governance-Provenienz

Die aktuell gepointeten Dateien

- `CurrentMainCanonicalState_v1.2`
- `SiteState_v1.3`
- `SessionCheckpoint_v1.33`
- `project-manifest.json`

beschreiben Band V-B noch als `pending/not started`, obwohl PRs #206, #207 und #208 inzwischen gemergt sind. Das ist ein Provenienz-/Freshness-Defekt, **keine** Änderung an physikalischen Gates. Reparaturziel ist ein append-only Successor-Snapshot in einem getrennten, reviewbaren Changeset; historische Snapshots werden nicht rückwirkend editiert.

## 6. Unveränderte Firewalls

- `FM-G0 = OPEN`
- `RATIFIED_HUMAN_TRUST_ROOT = NOT_RATIFIED`
- `RUNTIME_ISSUANCE_BINDINGS = BLOCKED`
- `AuthorizationDecision = NOT_CREATED`
- `SingleUseGrant = NOT_CREATED`
- `BACKEND_IMPORT = NOT_EXECUTED`
- `SOLVER_EXECUTION = NOT_EXECUTED`
- `PHYSICAL_BACKGROUND = NOT_ESTABLISHED`
- `PHYSICAL_RESPONSE_RANK = NOT_EXECUTED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_gate_effect = NONE`
- `physical_evidence_effect = NONE`

## 7. Nächste sichere Schritte

1. V-C-Crosswalk und Missing-Link-Register gegen den 15-Familien-Katalog maschinell prüfen.
2. Exakte Repository-Pfade für alle als `VERIFIED_PRESENT` bezeichneten Code-/Test-/Source-Artefakte verifizieren.
3. Band-V-B-Abschluss (`42/42`, unadjudiziert `0`) als Voraussetzung erzwingen.
4. Die elf Lücken fail-closed registrieren; keine Lücke darf durch `REFERENCE_ONLY` oder `NOT_APPLICABLE` maskiert werden.
5. Nach Merge dieses V-C-Blocks einen separaten append-only State-Freshness-PR für `UL-BVC-G11` erstellen.

Dieser Audit erzeugt **keine** physische Evidenz und autorisiert **keine** Ausführung.
