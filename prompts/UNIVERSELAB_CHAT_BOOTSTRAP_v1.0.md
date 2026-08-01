# UniverseLab Chat Bootstrap v1.0

**Zweck:** sicherer Einstieg in einen neuen Chat oder eine neue KI-Sitzung  
**Datenschutzklasse:** `PUBLIC_SANITIZED`  
**Geltungsbereich:** UniverseLab / HPVS → HZT-M0 → HZT-Full

## Verbindliche Startanweisung

Arbeite nicht aus vermeintlicher Erinnerung und behandle den Chat nicht als kanonische Projektquelle.

Lies in dieser Reihenfolge:

1. `governance/UNIVERSELAB_MEMORY_PROTOCOL_v1.0.md`
2. `governance/2026-08-01_UNIVERSELAB_FILE_NAMING_STANDARD_v1.0.md`
3. `registry/session-checkpoint-latest.json`
4. `project-manifest.json`
5. `convention-registry.json`
6. `registry/claim-register-v0.1.json`
7. `registry/decision-log.jsonl`
8. nur die im Checkpoint unter `entry_points` und in den aktiven Quellen genannten Fachartefakte

## Vor dem Weiterarbeiten

Prüfe und berichte kompakt:

- Checkpoint-ID und Basis-Commit;
- aktuelles Ziel und Arbeitsprogramm;
- unveränderte physikalische Gates;
- verifizierte Resultate;
- offene Blocker;
- exakt nächsten zulässigen Arbeitsschritt;
- Abweichungen zwischen Checkpoint und aktuellem Repositoryzustand.

Bei fehlenden oder widersprüchlichen Quellen gilt:

```text
Status = OPEN_OR_INCONSISTENT
keine Rekonstruktion aus Erinnerung
keine stille Plausibilitätsannahme
```

## Wissenschaftliche Firewall

Halte insbesondere fest:

```text
technische Ausführbarkeit ≠ physikalische Identifikation
numerische Stabilität ≠ Ghostfreiheit
guter Fit ≠ Theoriebestätigung
Parameterfit ≠ 6D-Herleitung
Literaturkompatibilität ≠ Ableitung
```

Übernimm keine Statusänderung, die nur in einem früheren Chat erwähnt wurde. Eine Statusänderung benötigt eine versionierte Quelle und einen Entscheidungsweg.

## Datenschutz-Firewall

Das öffentliche Repository darf nicht durch Chatmaterial angereichert werden.

Nicht übernehmen:

- vollständige Dialoge;
- persönliche Angaben oder private Notizen;
- Kontaktdaten;
- Share-Links;
- Zugangsdaten, Schlüssel oder Tokens;
- private Cloud- oder lokale Dateipfade.

Zitiere nur öffentlich freigegebene Repositoryartefakte. Private Materialien dürfen nur nach ausdrücklicher Bereitstellung für die aktuelle Aufgabe ausgewertet und nicht ungeprüft veröffentlicht werden.

## Dateinamen-Firewall

Lege den kanonischen Namen vor dem Erzeugen jeder neuen Datei fest.

Standard:

```text
YYYY-MM-DD_Bereich_Kurztitel_vX.Y.ext
```

Bei mehreren gleichartigen Ausgaben desselben Tages:

```text
YYYY-MM-DD_HHMM_Bereich_Kurztitel_vX.Y.ext
```

Verwende keine undatierten neuen Dateien, außer der Pfad ist als technisch notwendiger stabiler Alias in `registry/2026-08-01_UniverseLab_FileNamingPolicy_v1.0.json` registriert. Ein `latest`-Alias ersetzt niemals die datierte kanonische Fassung.

Bereits vorhandene Legacy-Dateien werden nicht ohne Migrationsplan umbenannt. Für neue Downloads, ZIPs, Dokumente, Tabellen, Quellcodes und Forschungsartefakte gilt derselbe Datumsstandard, sofern der Nutzer keinen anderen Namen vorgibt oder eine Plattform einen festen Pfad verlangt.

## Arbeitszyklus

```text
Quellen lesen
→ Status bestätigen
→ kanonischen datierten Dateinamen festlegen
→ eng definierten Arbeitsschritt durchführen
→ Ergebnis und Grenzen dokumentieren
→ Tests ausführen
→ Claim/Decision/Checkpoint aktualisieren
→ Pull Request prüfen
→ erst nach grünem CI mergen
```

## Abschluss eines Arbeitsblocks

Aktualisiere `registry/session-checkpoint-latest.json` nur mit öffentlichen, bereinigten Informationen:

- neue geprüfte Resultate;
- Quellenpfade;
- unveränderte und geänderte Gates;
- verbleibende Blocker;
- nächster exakt ausführbarer Schritt;
- neuer Basis-Commit.

Für einen neuen zeitabhängigen Checkpoint wird zusätzlich eine datierte kanonische Snapshot-Datei erzeugt. Der stabile `latest`-Alias bleibt der Einstiegspunkt.

Ergänze `registry/decision-log.jsonl`, wenn eine kanonische Entscheidung getroffen, geändert oder ersetzt wurde. Bestehende Einträge werden nicht gelöscht oder umgedeutet; Nachfolger verwenden `supersedes`.

## Aktuelle harte Grundregel

```text
K1-D und K1-E ändern sich nur über die governte Freigabekette.
Ein Memory-, Dateinamen- oder Software-Update besitzt für sich keine physikalische Evidenzwirkung.
```
