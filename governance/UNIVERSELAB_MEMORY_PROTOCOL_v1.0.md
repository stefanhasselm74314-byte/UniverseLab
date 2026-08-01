# UniverseLab Memory & Provenance Protocol v1.0

**Kennung:** `UL-MEM-v1.0`  
**Geltungsbereich:** öffentliches Repository `UniverseLab`  
**Status:** `ACTIVE_GOVERNANCE_PROTOCOL`  
**Datenschutzklasse:** `PUBLIC_SANITIZED`  
**Evidenzwirkung:** `GOVERNANCE_ONLY`

## 0. Leitgrundsatz

> **Der Chat arbeitet. GitHub erinnert. Die Register entscheiden.**

Ein Chatfenster ist ein temporärer Arbeitsraum. Es ist weder das kanonische Projektgedächtnis noch eine hinreichende wissenschaftliche Quelle. Dauerhafte Aussagen müssen in versionierten Artefakten mit Quellen-, Status- und Provenienzangaben gespeichert werden.

Dieses Protokoll verhindert zugleich, dass private Gespräche oder persönliche Daten in das öffentliche Repository übernommen werden.

## 1. Verbindliche Trennung

### 1.1 Öffentliches Projektgedächtnis

Im öffentlichen Repository dürfen gespeichert werden:

- wissenschaftliche Resultate und Gleichungen;
- Gate- und Freigabestatus;
- Quellen-, Claim- und Entscheidungsreferenzen;
- technische Arbeitsstände und reproduzierbare Tests;
- offene Blocker, Annahmen und Gültigkeitsgrenzen;
- Commit-, Datei- und RUN-ID-Provenienz.

### 1.2 Nicht öffentliches Gedächtnis

Nicht in das öffentliche Repository gehören:

- vollständige Chattranskripte oder Rohdialoge;
- private Gesprächszusammenfassungen;
- persönliche Kontaktdaten, Adressen oder Kontoinformationen;
- ChatGPT-Share-Links oder andere nicht freigegebene Links;
- API-Schlüssel, Tokens, Passwörter oder private Schlüssel;
- lokale private Dateipfade und private Cloud-Links;
- persönliche Notizen ohne wissenschaftliche Notwendigkeit.

Private Archive müssen außerhalb dieses öffentlichen Repositorys gespeichert und getrennt gesichert werden.

## 2. Gedächtnisebenen

### Ebene A — Governance

Kanonische Regeln, Architektur und Evidenzdisziplin:

- MD-0 und ratifizierte Nachfolger;
- `project-manifest.json`;
- `convention-registry.json`;
- dieses Protokoll.

### Ebene B — Aktueller Checkpoint

`registry/session-checkpoint-latest.json` enthält den kompakten, öffentlichen Arbeitsstand:

- Basis-Commit;
- aktuelles Ziel;
- Gate-Zustand;
- verifizierte Resultate mit Quellen;
- offene Blocker;
- aktive Annahmen;
- verbotene Schlussfolgerungen;
- exakt nächsten Arbeitsschritt.

Der Checkpoint enthält keine Rohdialoge. Seine Git-Historie bildet ältere Versionen ab.

### Ebene C — Append-only-Entscheidungslog

`registry/decision-log.jsonl` speichert jede kanonische Entscheidung als eigene JSON-Zeile. Einträge werden nicht nachträglich umgedeutet. Änderungen erfolgen durch einen neuen Eintrag mit `supersedes`.

### Ebene D — Claims, Quellen und Reproduktion

Claim-, Quellen-, Run- und Artefaktregister bestimmen, welche Aussage welchen Status besitzt und wodurch sie geändert werden kann.

### Ebene E — Chat-Bootstrap

`prompts/UNIVERSELAB_CHAT_BOOTSTRAP_v1.0.md` definiert die minimale Lesereihenfolge für neue Chats oder neue KI-Sitzungen.

### Ebene F — Vollarchiv

Chat-Exporte, ZIPs, PDFs und historische Arbeitsdateien bilden ein getrenntes Langzeitarchiv. Das Archiv ist keine automatisch freigegebene Quelle. Seine Inhalte müssen vor einer Kanonisierung einzeln geprüft werden.

## 3. Status- und Quellenregeln

1. **Keine Erinnerung ohne Quelle.** Eine historische Behauptung benötigt eine Datei, Claim-ID, Gleichungs-ID, RUN-ID oder einen Commit.
2. **Kein Statuswechsel nur im Chat.** Übergänge wie `OPEN → DERIVED` oder `BLOCKED → RELEASED` benötigen einen versionierten Entscheidungs- und Quellenpfad.
3. **Technik ist keine Evidenz.** Ausführbarer Code, numerische Stabilität oder ein guter Fit ändern keine physikalische Freigabe ohne die dafür definierten Gates.
4. **Mehrdeutigkeit bleibt sichtbar.** Fehlende Normierungen, Randdaten oder Definitionen werden als `OPEN` oder `AMBIGUOUS` gespeichert und nicht erraten.
5. **Keine stillen Überschreibungen.** Revidierte Entscheidungen verweisen auf ihre Vorgänger.

## 4. Checkpoint-Vertrag

Der aktuelle Checkpoint muss mindestens enthalten:

```text
schema
checkpoint_id
timestamp
privacy_classification
basis_commit
architecture
current_goal
current_workstream
gate_state
verified_results
open_blockers
active_assumptions
forbidden_inferences
entry_points
next_exact_action
```

### 4.1 Quellen

Alle Quellen im Checkpoint müssen relative Repositorypfade sein. Externe URLs, Share-Links und private Pfade sind unzulässig.

### 4.2 Basis-Commit

`basis_commit` bezeichnet den geprüften Repositoryzustand, auf dem der Checkpoint beruht. Der Commit muss im Git-Verlauf existieren. Er muss nicht der Commit sein, der den Checkpoint selbst hinzufügt.

### 4.3 Verifizierte Resultate

Jedes Resultat besitzt:

- eine stabile ID;
- eine knappe Aussage;
- einen Status;
- mindestens eine vorhandene Quelle;
- eine explizite Evidenzwirkung.

## 5. Entscheidungslog-Vertrag

Jede JSONL-Zeile enthält mindestens:

```text
decision_id
date
topic
decision
status
reason
sources
evidence_effect
supersedes
```

Regeln:

- `decision_id` ist eindeutig;
- je Thema darf nur eine aktive Entscheidung existieren;
- `supersedes` verweist auf eine frühere Entscheidung oder ist `null`;
- Quellen müssen als relative Pfade existieren;
- ein supersedierter Eintrag bleibt historisch erhalten.

## 6. Privacy Gate

Vor jedem Merge prüft `tools/validate_memory_protocol.py` die Memory-Artefakte auf:

- ChatGPT-Share-Links;
- typische API-, GitHub- und Private-Key-Muster;
- E-Mail-Adressen;
- verbotene personenbezogene oder geheime JSON-Felder;
- Rohdialogmarker;
- externe oder traversierende Quellenpfade;
- fehlende Quellen und doppelte IDs.

Ein Treffer erzeugt:

```text
PRIVACY_GATE = FAIL
MEMORY_CONTRACT = FAIL
```

Der Validator schreibt oder bereinigt keine Inhalte automatisch.

## 7. Arbeitsablauf

### 7.1 Beginn eines Arbeitsblocks

1. Governance und Konventionen lesen.
2. `session-checkpoint-latest.json` lesen.
3. Claim- und Entscheidungsregister lesen.
4. Nur die Quellen des aktiven Arbeitsblocks laden.
5. Basis-Commit und aktuellen `main`-Stand vergleichen.

### 7.2 Während der Arbeit

```text
Herleitung oder Analyse
→ versioniertes Fachartefakt
→ Claim-/Entscheidungsreferenz
→ Tests und CI
→ Pull Request
→ Merge
→ neuer Checkpoint
```

### 7.3 Ende eines Arbeitsblocks

Der Checkpoint wird aktualisiert mit:

- tatsächlich geprüften Ergebnissen;
- unveränderten und geänderten Gates;
- neuen offenen Blockern;
- dem nächsten exakt ausführbaren Schritt.

## 8. Verbotene Abkürzungen

Unzulässig sind insbesondere:

- vollständige Chats als öffentliches Projektgedächtnis zu committen;
- eine Chat-Zusammenfassung als Primärquelle auszugeben;
- einen unbekannten früheren Beschluss aus vermeintlicher Erinnerung zu rekonstruieren;
- fehlende Dateien oder Resultate stillschweigend als vorhanden zu behandeln;
- private Links oder Zugangsdaten als Provenienz zu speichern;
- einen Status ohne Quell- und Entscheidungsweg zu ändern.

## 9. Sicherheitsgrenze

Dieses Protokoll schützt das öffentliche Projektgedächtnis durch Struktur- und Mustertests. Es ersetzt keine vollständige professionelle Geheimnisprüfung und keine verschlüsselte private Archivierung. Hochsensible Daten dürfen niemals erst in einen öffentlichen Branch geschrieben werden.

## 10. Freigabezustand

Die Einführung von `UL-MEM-v1.0` verändert keine physikalische Gate-Entscheidung:

```text
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
Evidenzwirkung = NONE
```
