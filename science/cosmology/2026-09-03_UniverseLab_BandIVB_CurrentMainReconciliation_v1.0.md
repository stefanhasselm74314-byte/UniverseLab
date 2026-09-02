# UniverseLab Band IV-B · Current-main-, Test- und Public-Status-Reconciliation v1.0

**Datum:** 2026-09-03  
**Basis-`main`:** `30b781f84d9c7c9fc74fac1adb34e4d935b1679b`  
**Scope:** numerische QA, Provenienz, öffentlicher Status, Metadaten und Zugänglichkeit  
**Physische Ausführung:** keine  
**Physical gate effect:** `NONE`  
**Physical evidence effect:** `NONE`

## 1. Anlass

Band IV-A identifizierte drei voneinander zu trennende Fehlerklassen:

1. zwei spezialisierte Browser-Resettests verwendeten die ältere Näherung `Omega_DE=1-Omega_m=0.685`, obwohl der gemeinsame Referenzzustand Strahlung explizit enthält;
2. der allgemeine Bridge-Rechenkern deklarierte `Rchi>0`, regularisierte jedoch intern `Rchi<0.02` durch einen nicht ausgewiesenen Floor;
3. mehrere öffentliche und maschinenlesbare Statusquellen lagen hinter dem bereits gemergten Repositoryzustand zurück.

Zusätzlich bestanden eine überzogene Emergence-Kurzbezeichnung, deaktivierter mobiler Zoom und nicht aktualisierte Sitemap-Metadaten.

## 2. Radiation-inclusive Closure

Der öffentliche flache Referenzsatz lautet

`Omega_r=0.000092`,

`Omega_m=0.315`,

`Omega_DE=0.684908`,

`Omega_k=0`.

Damit gilt exakt

`Omega_r+Omega_m+Omega_DE+Omega_k=1`.

Die Differenz zwischen dem alten Testwert `0.685` und dem implementierten Wert `0.684908` ist

`0.000092=Omega_r`.

Der Fehler lag daher nicht in der Friedmann-Dynamik, sondern in einer veralteten Test-Closure, welche Strahlung still ausließ. Observatory und Compare Safe prüfen nach dem Reset nun alle vier Dichteanteile und die Gesamtsumme.

**Status:** `[BEWIESEN ALS TESTREKONSTRUKTION]`

## 3. Bridge-Skala und Klein-Rchi-Asymptotik

Die deklarierte reduzierte Bridge-Skala ist

`a_c(Rchi)=1/(1+2.5/Rchi)=Rchi/(Rchi+2.5)`,

für

`Rchi>0`.

Für `Rchi -> 0+` folgt

`a_c(Rchi)=Rchi/2.5+O(Rchi^2)`

und damit

`a_c/Rchi -> 0.4`.

Die frühere Implementierung verwendete im Nenner `max(0.02,Rchi)`. Dadurch war `a_c` unterhalb `Rchi=0.02` konstant und die deklarierte Asymptotik falsch. Der Floor wurde entfernt; `Rchi<=0` bleibt über `INVALID_RCHI` fail-closed.

Die öffentliche Compare-Safe-Oberfläche erlaubt weiterhin nur `Rchi>=0.1`. Deshalb verändert die Härtung keine derzeit sichtbare Standardkurve, schließt aber den allgemeinen Engine-Vertrag.

**Status:** `[BEWIESEN ALS IMPLEMENTIERUNGS- UND ASYMPTOTIKVERTRAG]`

Die Bridge bleibt dennoch ein reduziertes effektives Hintergrundmodell. Daraus folgen weder eine 6D-Parent-Herleitung noch freigegebene Perturbations-, Growth- oder Lensing-Abbildungen.

## 4. Append-only Statusreconciliation

Die datierten Zustandsdateien vom 1. September bleiben als historische Snapshots erhalten. Neue Nachfolger sind:

- `registry/2026-09-03_UniverseLab_CurrentMainCanonicalState_v1.1.json`,
- `registry/2026-09-03_UniverseLab_SiteState_v1.2.json`,
- `registry/2026-09-03_UniverseLab_SessionCheckpoint_v1.32.json`.

`project-manifest.json`, `registry/session-checkpoint-latest.json` und die globale Shell zeigen auf diese Nachfolger. Ein offener Pull Request besitzt weiterhin keinen kanonischen Effekt; die neuen Zustände werden erst durch einen grünen Merge kanonisch.

## 5. Öffentliche Semantik

Emergence bezeichnet den Kosmologiepfad nun als

`LambdaCDM-Anzeigezeit (Referenz)`

statt als isoliertes `Physikalisch: LambdaCDM`. Der Zellautomat bleibt mathematisch und dynamisch vom FLRW-Hintergrund und von der linearen GR-Growth-ODE getrennt. Die Anzeigeauflösung ist ein Renderzustand, kein physikalischer Expansions- oder Strukturbildungsmechanismus.

Der Viewport verbietet mobilen Zoom nicht mehr. Dies ist eine Zugänglichkeitskorrektur ohne physikalische oder numerische Wirkung.

## 6. Sitemap-Provenienz

`tools/2026-09-03_generate_UniverseLab_SitemapLastmod_v1.0.py` ordnet jede Sitemap-URL genau einer Repository-Seitenressource zu. Das Datum wird aus dem letzten Commit dieser Ressource in der Zeitzone `Europe/Berlin` abgeleitet. Der Generator lehnt fehlende Seiten, doppelte URLs, doppelte Dateizuordnungen und nicht parsbare Einträge fail-closed ab.

Damit gilt

`lastmod(page)=local_date(latest_commit_touching_page)`.

Ein globaler pauschaler Aktualitätsstempel wird vermieden.

## 7. QA-Struktur

Band IV-B verlangt auf demselben Exact Head:

- gemeinsame Engine-Regression in Node und unabhängiger Python-Rekonstruktion;
- Observatory-Static- und Browser-QA;
- Compare-Safe-Static- und Browser-QA;
- Emergence-Static-, Hardening- und Browser-QA;
- expliziten Klein-`Rchi`-Asymptotiktest;
- Reset-Closure einschließlich `Omega_r`;
- Pointerkonsistenz zwischen Manifest, SiteState, CurrentMain und Checkpoint;
- Erhaltung der älteren datierten Snapshots;
- reproduzierbare Sitemap;
- deutsch/englische Statuskonsistenz;
- unveränderte Autorisierungs- und Physikfirewalls.

## 8. Unveränderte Grenzen

```text
Ratified human trust root:       NOT_RATIFIED
Authority signature provenance:  BLOCKED_PENDING_EXPLICIT_HUMAN_TRUST_ROOT_RATIFICATION
Runtime issuance bindings:       BLOCKED
AuthorizationDecision:           NOT_CREATED
SingleUseGrant:                   NOT_CREATED
Backend import:                   NOT_EXECUTED
Solver execution:                NOT_EXECUTED
Physical background:             NOT_ESTABLISHED
Physical response rank:          NOT_EXECUTED
ULSH-01 WP3:                      NOT_STARTED
ULSH-01 WP4:                      BLOCKED_NOT_AUTHORIZED
K1-D:                             NOT_RELEASED
K1-E:                             NOT_ADMISSIBLE
```

Die Trust-Root-Ratifikation ist als externe menschliche Handlung geparkt, bis ein ausschließlich vom Nutzer kontrollierter Rechner verfügbar ist. Sie ist keine Voraussetzung für Band IV-B.

## 9. Evidenzlogik

`grüne QA != empirische Evidenz`,

`korrekte Klein-Rchi-Asymptotik != 6D-Parent-Herleitung`,

`öffentliche Statuskonsistenz != physische Identifikation`,

`numerische Stabilität != Ghostfreiheit`,

`Trust-Root-Vorbereitung != menschliche Ratifikation`.

Nach grünem Merge ist der nächste zulässige Analyseblock Band V: öffentliche wissenschaftliche Claims gegen HZT-M0-Parentstatus, Observablen, Datenquellen und Falsifikationsregister. Es wird kein CP01R4-Lauf gestartet.
