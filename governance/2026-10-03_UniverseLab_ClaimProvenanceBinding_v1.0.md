# UniverseLab: begrenzte Claim-Provenienz-Reparatur v1.0

Prüfbasis: main `312e767628f003494a51edf685cf679469e35f13` (PR #254).
Status: `IMPLEMENTED_REVIEW_PENDING`; keine Merge- oder Release-Freigabe.

## Befund und Korrektur

| Prüfbereich | Tatsächlicher Befund | Begrenzte Korrektur |
| --- | --- | --- |
| HIGH-Census | 73 statt 72 getrackte HTML-Dateien; hinzugekommen ist `googlebc3b5b4a4888e35c.html`, ohne Claim-Kandidaten. | Vollständiges Pfadinventar, Verifikations-Dateihash und Live-Scanner prüfen; keine bloße Lockerung des Zählers. |
| MEDIUM/G11 | 46 MEDIUM-Claims: 37 direkte historische IDs, zwei zeilenbedingt neue Landingpage-IDs, sieben bestehende Statusseiten-Delta-IDs. | Exakt zwei belegte Zuordnungen zur historischen Prüfung; der historische 39+7-Stand wird als datierter Stand erhalten. |
| Sitemap | Genau zwei veraltete `lastmod`-Werte: `index.html` und `index-en.html`, 2026-08-18 → 2026-09-25. | Unveränderter Datumsalgorithmus mit vollständiger Commit-Historie; alle 34 URLs und übrigen XML-Inhalte bleiben gleich. |

Die ursprüngliche lokale Diagnose von **34** Sitemap-Abweichungen beruhte auf
einem flachen Checkout. Sie ist verworfen. Der GitHub-Lauf
[37111835535](https://github.com/stefanhasselm74314-byte/UniverseLab/actions/runs/37111835535)
und die Wiederholung mit vollständiger lokaler Historie belegen **zwei**.
Der Generator weist flache Historien jetzt vor einer Ausgabe zurück.

## Exakte Claim-Zuordnung

| Seite | Historische ID | Aktuelle ID | Quellzeile alt → neu |
| --- | --- | --- | --- |
| `index-en.html` | `UL-CLAIM-CANDIDATE-2A5F574A7ED88849` | `UL-CLAIM-CANDIDATE-8DA35AA2283D9C5F` | 1 → 13 |
| `index.html` | `UL-CLAIM-CANDIDATE-7FAC1625FAAC6926` | `UL-CLAIM-CANDIDATE-2A1B5F591D31DF61` | 59 → 66 |

Die Originalkandidaten werden aus dem im historischen Completion-Ledger
angegebenen Commit `32bd028ace1068a400067f8c890137b27c05fa3c` gelesen und
mit den dortigen Originalseiten verifiziert. Text, Tag, Region, Seitenscope,
Lexikalklassen, Risikowerte und Statusfelder stimmen vollständig überein.
Nur ID, Zeilennummer und vollständiger Seitenhash unterscheiden sich.
Die Seitendifferenz betrifft Navigation/Layout; die Einordnung als
`METADATA_OR_SCOPE_DESCRIPTION` und die Trennung zwischen etablierter Physik
und spekulativen 6D-Hypothesen bleiben durch den vorhandenen Text gedeckt.
Das ist ein begrenzter Identitäts- und Kontextabgleich, kein neues physisches Review.

Die maschinenlesbare Quelle ist
[`ClaimProvenanceBinding v1.0`](../registry/2026-10-03_UniverseLab_ClaimProvenanceBinding_v1.0.json).
`project-manifest.json` verweist additiv darauf. Die alten Ledger,
CurrentMainCanonicalState v1.3, SiteState v1.4, SessionCheckpoint v1.34 und
G11-Closure bleiben bytegleich; ihre Behauptungen gelten weiterhin für den
Snapshot vom 04.09.2026. Der Live-Census behält seine tatsächlichen IDs.
Nur die geprüfte Zuordnungssicht setzt die beiden Alias-IDs auf ihre historischen
IDs zurück. Die sieben Statusseiten-Delta-IDs werden nicht neu adjudiziert.

## Prüfgrenzen und Anwendung

Der Validator vergleicht alle 993 Live-Kandidaten mit der Materialisierung,
prüft das vollständige HTML-Inventar und bindet alle 46 MEDIUM-Datensätze an
ihren geprüften Inhalt einschließlich Quelldateihash. Unbekannte, mehrdeutige,
geänderte oder zusätzlich eingeführte Claims erfordern ein neues Review.
Historische Dateien werden gegen ihre Git-Originale geschützt. Die drei
bestehenden HIGH/MEDIUM/G11-Tests konsumieren diese geprüfte Zuordnung;
der neue Workflow führt sie auch dann aus, wenn bisherige Pfadfilter nicht greifen.
Historische Git-Objekte sind für diese Prüfung erforderlich.

Diese Reparatur ist unabhängig vom Methoden-Addendum in Draft-PR #256 und
kann mit ihm kombiniert geprüft werden. Die vier automatisch erzeugten
Census-Herkunftsänderungen auf #256 sind keine physischen Änderungen.
#248 bleibt eine separate UI-Änderung: veränderte Quelldateihashes benötigen
weiterhin einen expliziten Provenienzabgleich. Diese Prüfung erklärt weder
#248 noch den gesamten alten Current-main-Snapshot für frisch.

`physical_gate_effect=NONE`, `physical_evidence_effect=NONE`,
`K1-D=NOT_RELEASED`, `K1-E=NOT_ADMISSIBLE`, `FM-G0=OPEN`.
Methodengates, ULSH-07/08 und die zehn FM-0-Lücken bleiben unverändert.
Kein Solverlauf, keine physische Evidenz, kein Merge und keine Gesamtfreigabe.
