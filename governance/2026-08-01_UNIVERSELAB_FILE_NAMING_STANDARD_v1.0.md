# UniverseLab File Naming Standard v1.0

**Kennung:** `UL-FNS-v1.0`  
**Erstellung:** `2026-08-01`  
**Status:** `ACTIVE_GOVERNANCE_STANDARD`  
**Geltungsbereich:** UniverseLab-Repository, Forschungsartefakte, Exporte, Berichte, Datenpakete und künftig durch Assistenz erzeugte Dateien

## 1. Zweck

UniverseLab verwendet ab diesem Standard eine sichtbare Datumskennung im Namen jeder neu erzeugten kanonischen Datei. Dadurch bleiben Erstellungszeit, Themenblock und Versionslinie auch außerhalb eines Chats oder einer Git-Historie unmittelbar erkennbar.

Der Standard ersetzt keine fachliche Provenienz. Die zeitliche Einordnung im Dateinamen wird gemeinsam mit Versionsnummer, Commit, Quellenregister und gegebenenfalls RUN_ID verwendet.

## 2. Verbindliches Grundschema

```text
YYYY-MM-DD_Bereich_Kurztitel_vX.Y.ext
```

Beispiele:

```text
2026-08-01_HZT-M0_MDS05_Warpvolumen_v0.1.md
2026-08-01_UniverseLab_SessionCheckpoint_v1.0.json
2026-08-01_MD2S_BackgroundSolver_v0.1.py
2026-08-01_UniverseLab_CanonicalBackup_v1.0.zip
```

Das Datum steht am Anfang, damit gewöhnliche alphabetische Sortierung zugleich eine zeitliche Sortierung ergibt.

## 3. Mehrere gleichartige Dateien am selben Tag

Bei einer Namenskollision oder mehreren zeitlich getrennten Ausgaben desselben Tages wird die lokale Erstellungszeit in 24-Stunden-Notation ergänzt:

```text
YYYY-MM-DD_HHMM_Bereich_Kurztitel_vX.Y.ext
```

Beispiel:

```text
2026-08-01_1725_MD2S_ResidualAudit_v0.1.json
```

Die Uhrzeit ist kein Ersatz für eine Versionsnummer. Sie dient nur der eindeutigen zeitlichen Zuordnung.

## 4. Bedeutung der Bestandteile

| Bestandteil | Regel |
|---|---|
| `YYYY-MM-DD` | tatsächliches Datum der Ersterstellung dieser Artefaktlinie |
| `HHMM` | optional; lokale Erstellungszeit bei Kollision oder mehreren Tagesausgaben |
| `Bereich` | Projekt- oder Modulkennung, etwa `UniverseLab`, `HZT-M0`, `MD2S` oder `GW` |
| `Kurztitel` | kurze fachliche Beschreibung ohne Leerzeichen |
| `vX.Y` | fachliche Version; mindestens Haupt- und Nebenversion |
| `ext` | tatsächliches Dateiformat |

Erlaubt sind im technischen Dateinamen grundsätzlich:

```text
A-Z  a-z  0-9  Punkt  Bindestrich  Unterstrich
```

Nicht verwendet werden:

- Leerzeichen;
- Umlaute oder `ß`;
- uneindeutige Zusätze wie `neu`, `finalfinal`, `letzteVersion`;
- Versionsangaben ohne klaren numerischen Stand.

## 5. Datum und Versionslinie

### 5.1 Überarbeitung derselben Artefaktlinie

Das ursprüngliche Erstellungsdatum bleibt erhalten; die Versionsnummer wird erhöht.

```text
2026-08-01_HZT-M0_MDS05_Warpvolumen_v0.1.md
2026-08-01_HZT-M0_MDS05_Warpvolumen_v0.2.md
2026-08-01_HZT-M0_MDS05_Warpvolumen_v1.0.md
```

### 5.2 Materiell neuer Nachfolger

Eine fachlich neue Artefaktlinie, ein neuer Snapshot oder ein neuer Lauf erhält das neue Erstellungsdatum.

```text
2026-08-04_MD2S_BackgroundRun_RUN-004_v1.0.json
```

### 5.3 Statussuffix

Ein Statussuffix ist nur ergänzend erlaubt und steht hinter der Version:

```text
2026-08-01_MD2S_ModelFreeze_v0.1_DRAFT.md
2026-08-01_MD2S_ModelFreeze_v1.0_RELEASED.md
```

Der Status im Dateinamen ersetzt niemals den kanonischen Status im Register.

## 6. Stabile Alias-Dateien

Bestimmte maschinell konsumierte Einstiegspunkte benötigen einen unveränderten Pfad. Dafür sind ausdrücklich registrierte Alias-Dateien zulässig, beispielsweise:

```text
registry/session-checkpoint-latest.json
```

Der kanonische zeitlich eingeordnete Snapshot lautet zusätzlich beispielsweise:

```text
registry/2026-08-01_UniverseLab_SessionCheckpoint_v1.0.json
```

Verbindliche Aliasregeln:

1. Ein Alias muss im maschinenlesbaren File-Naming-Policy-Register eingetragen sein.
2. Der Eintrag muss Zweck und Aliasart nennen.
3. Ein `latest`-Alias muss auf eine datierte kanonische Fassung verweisen oder inhaltsgleich zu ihr sein.
4. Ein Alias darf nicht als einzige archivierte Fassung eines zeitabhängigen Zustands dienen.
5. Neue Ausnahmen ohne Governance-Eintrag sind unzulässig.

Das append-only Entscheidungslog `registry/decision-log.jsonl` ist ein stabiler kanonischer Logpfad und kein wechselnder Snapshot. Auch diese Ausnahme ist ausdrücklich registriert.

## 7. Bestehende Dateien

Der Standard gilt nicht rückwirkend für bereits vorhandene Dateien. Historische Dateien werden nicht massenhaft umbenannt, weil dies Links, Quellverweise, Git-Historie, Webseiten und reproduzierbare Manifeste beschädigen könnte.

Für Altbestände gilt:

```text
LEGACY_GRANDFATHERED
```

Sobald ein materiell neuer Nachfolger erstellt wird, gilt das neue Namensschema.

## 8. Geltung außerhalb des Repositorys

Auch vom Assistenzsystem erzeugte Downloads und Übergabepakete verwenden standardmäßig dieses Schema:

```text
2026-08-01_UniverseLab_CanonicalBackup_v1.0.zip
2026-08-01_HZT-M0_Formelwerk_v0.3.docx
2026-08-01_HZT-M0_Formelwerk_v0.3.pdf
```

Ein vom Nutzer ausdrücklich gewünschter Dateiname hat Vorrang. Bei technisch vorgegebenen Namen wird die Abweichung offengelegt.

## 9. Automatische Durchsetzung

Der File-Naming-Validator prüft ausschließlich **neu hinzugefügte Dateien** eines Pull Requests oder Pushes. Er kontrolliert:

- gültiges ISO-Datum;
- optional gültige Uhrzeit `HHMM`;
- beschreibenden Namensanteil;
- numerische Version `vX.Y`;
- zulässige Zeichen;
- registrierte stabile Alias-Ausnahmen.

Bestehende Legacy-Dateien werden nicht beanstandet. Der Validator ist read-only und fail-closed.

## 10. Verantwortungsregel

Vor dem Erzeugen einer Datei wird zuerst der kanonische Name festgelegt. Nachträgliche spontane Umbenennungen werden vermieden.

Der operative Grundsatz lautet:

```text
Datum ordnet ein.
Version beschreibt die Entwicklung.
Commit fixiert den exakten Zustand.
Register bestimmt den wissenschaftlichen Status.
```
