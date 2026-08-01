---
title: "UniverseLab 2.1 — P0 Repository Verification and Runtime-Migration Audit"
date: "2026-08-01"
verified_branch: "main"
verified_commit: "97240da23c0fcf33abbe056088f48f0a9b2e4112"
status: "PARTIAL PASS — infrastructure exists, runtime consumption open"
---

# UniverseLab 2.1 — P0-Verifikation

## 0. Entscheidung

Der gemeldete UniverseLab-2.1-Audit ist als echter Repository- und
Dokumentationsstand verifiziert.

Verifiziert wurden insbesondere:

- `project-manifest.json`;
- `convention-registry.json`;
- `universelab-audit-2026-07-31.json`;
- `RELEASE-2.1-AUDIT.md`;
- `CITATION.cff`;
- `hyperzeit-material-v2.html`;
- `hyperzeit-methods.html`;
- `source.html`;
- `navigator-app.html`;
- `hyperlab.html`;
- `baryogenesis.html`;
- `index.html`.

Der letzte verifizierte Release-Commit lautet:

```text
97240da23c0fcf33abbe056088f48f0a9b2e4112
Document UniverseLab 2.1 audit release
```

Die Releasebeschreibung trennt korrekt zwischen Dokumentationsrelease
und physikalischer Freigabe:

```text
K1-D = NOT RELEASED
K1-E = NOT ADMISSIBLE
Evidence effect of diagnostic runs = NONE
```

Gesamtstatus:

\[
\boxed{
\textbf{P0-INFRASTRUKTUR = EXISTIERT}
}
\]

aber:

\[
\boxed{
\textbf{P0-RUNTIME-MIGRATION = NICHT ABGESCHLOSSEN}
}
\]

---

# 1. Konsistenz des Auditregisters

Das maschinenlesbare Audit enthält 26 Positionen:

| Schweregrad | Anzahl |
|---|---:|
| Critical | 7 |
| High | 12 |
| Medium | 7 |
| Gesamt | 26 |

Die im Bericht genannten Zahlen sind damit intern konsistent.

Die sieben Critical-Punkte sind:

- GOV-001;
- SCI-001;
- SCI-002;
- SCI-003;
- SCI-004;
- SCI-005;
- SCI-008.

---

# 2. Verifizierte Stärken

## 2.1 Zentrale Register existieren

Das Manifest enthält:

- HPVS → HZT-M0-S6 / HZT-M0-P5 → HZT-Full;
- S6-Q1 als Kontrollkern;
- K1-Gates;
- kanonische Seiten;
- Datenreleases;
- zentrale Register;
- nächste Blocker.

Das Konventionsregister friert ein:

- Indexbereiche;
- S6-Signatur;
- Krümmungskonvention;
- Einstein-Hilbert-Wirkung;
- Minisuperspace-Konvention;
- Dimensionen;
- Stabilitätsvokabular;
- Statusvokabular;
- numerische Mindestregeln.

## 2.2 Methodische Scope-Firewall

Material- und Methodenseite trennen korrekt zwischen:

- mathematischer Grundlage;
- Vergleichsliteratur;
- QA-Methode;
- No-Go;
- offener Übertragung;
- physikalischer Evidenz.

## 2.3 Release-Nachweis

`RELEASE-2.1-AUDIT.md` und `CITATION.cff` sind vorhanden und verwenden
dieselbe Releasebezeichnung:

```text
2.1-audit
```

---

# 3. Harte P0-Befunde

## GOV-001 — nur teilweise gelöst

`project-manifest.json` existiert, wird aber von den produktiven Seiten
noch nicht als Runtime-Quelle konsumiert.

Beispiele:

- `navigator-app.html` injiziert Links und Queryversionen direkt;
- `hyperlab.html` enthält Gate-Texte und Statuszahlen statisch;
- `source.html` dupliziert Seitenpfade und Versionsparameter;
- `hyperzeit-methods.html` besitzt eine eigene hart codierte Navigation;
- `hyperzeit-material-v2.html` besitzt eine eigene hart codierte Navigation;
- `index.html` besitzt eine unabhängige Navigation.

Daher sollte GOV-001 nicht mehr `OPEN`, sondern präziser lauten:

```text
PARTIAL
infrastructure_created_runtime_consumption_open
```

## GOV-002 — weiterhin offen

Zusammenfassungszahlen werden noch lokal geschrieben, beispielsweise:

- vier Blockierergebnisse;
- acht offene Zweige;
- drei nächste Arbeitsblöcke;
- K1-D/K1-E-Badges.

Diese Zahlen werden nicht aus `universelab-audit-2026-07-31.json`
berechnet.

## NUM-002 — nur teilweise gelöst

Das Konventionsregister existiert. Offen bleibt:

- automatische Eingabevalidierung;
- Schema-validierte Nutzung in Solvern;
- branchenspezifische Konvertierung;
- Test, dass Seiten tatsächlich dieselben Konventionen verwenden.

Daher:

```text
PARTIAL
registry_created_solver_enforcement_open
```

---

# 4. Versions- und Inhaltsdrift

## 4.1 Baryogenese

Die öffentliche Einstiegsseite bezeichnet sich als:

```text
Baryogenese-Labor 1.2
```

und lädt:

```text
baryogenesis-v12.html?v=5
```

Der lokal erreichte Forschungsstand reicht inzwischen bis:

```text
COS-04.2B-1o
Baryogenesis comparator profile 1.8
```

Damit besteht eine deutliche Dokumentationslücke zwischen aktuellem
Projektstand und veröffentlichtem Labor.

## 4.2 Queryparameter

Das Manifest enthält unter anderem:

```text
navigator-app.html?v=3
hyperlab.html?v=10
baryogenesis.html?v=16
compare-safe.html?v=safe2
```

Die Zielseiten verwenden zusätzlich eigene interne Versionsparameter.
Es existiert keine einzelne Releasevariable, die alle Cacheparameter
ersetzt.

## 4.3 Release-Unveränderlichkeit

Manifest, CFF und Release enthalten noch keinen gemeinsamen:

- Git-Commit;
- Manifest-Hash;
- Konventionsregister-Hash;
- Audit-Hash;
- Schema-Lock.

Historische Releases könnten daher bei späteren Dateiänderungen nicht
vollständig bytegenau rekonstruiert werden.

---

# 5. Erforderliche P0-Migration

## P0-A — Runtime-Loader

Alle produktiven Seiten sollen genau diese Quellen laden:

```text
project-manifest.json
convention-registry.json
universelab-audit-2026-07-31.json
```

## P0-B — deklarative DOM-Bindung

Beispiele:

```html
<span data-ul-gate="K1-D"></span>
<span data-ul-gate="K1-E"></span>
<span data-ul-issue-count="CRITICAL"></span>
<a data-ul-page="hyperlab"></a>
```

## P0-C — Release-Lock

Erforderlich:

```json
{
  "release": "2.1-audit",
  "git_commit": "...",
  "manifest_sha256": "...",
  "conventions_sha256": "...",
  "audit_sha256": "..."
}
```

## P0-D — Schema und CI

Mindesttests:

- JSON-Parsing;
- Schemafelder;
- kanonische Pfade existieren;
- keine unbekannten Gate-Werte;
- Auditanzahlen stimmen;
- CFF-Version stimmt mit Manifest überein;
- interne Links;
- JavaScript-Syntax;
- HTML-Validierung;
- Accessibility;
- keine hart codierten Gate-Texte außerhalb klar markierter Fallbacks.

---

# 6. P0-Gate-Status

```text
P0-01 MANIFEST EXISTS:
PASS

P0-02 CONVENTION REGISTRY EXISTS:
PASS

P0-03 MACHINE-READABLE AUDIT EXISTS:
PASS

P0-04 RELEASE AND CITATION METADATA:
PASS

P0-05 AUDIT COUNTS:
PASS

P0-06 RUNTIME MANIFEST CONSUMPTION:
FAIL

P0-07 CENTRAL STATUS RENDERER:
FAIL

P0-08 SINGLE CACHE/RELEASE VERSION:
FAIL

P0-09 BARYOGENESIS CURRENT-STATE INTEGRATION:
FAIL

P0-10 BYTE-REPRODUCIBLE RELEASE LOCK:
FAIL

P0 OVERALL:
PARTIAL PASS
```

---

# 7. Konsequenz

Die Website-Architektur ist jetzt wissenschaftlich besser organisiert,
aber die zentrale Wahrheit ist noch deklarativ statt operativ.

Der nächste Webschritt ist nicht eine weitere Inhaltsseite, sondern:

\[
\boxed{
\text{Manifest}
\rightarrow
\text{Runtime-Loader}
\rightarrow
\text{zentrale Komponenten}
\rightarrow
\text{CI}
}
\]

Parallel darf die Theoriearbeit nun zu SCI-001/SCI-002 wechseln, sofern
der neue Parentabschluss ausdrücklich vom älteren
Lovelock-/D2N-Q-Audit getrennt wird.
