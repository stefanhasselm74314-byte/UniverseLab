# UniverseLab — RC-VALIDATION-18: Draft-Veröffentlichung und Autodiscovery

**Datum:** 2026-11-03  
**Status:** DRAFT / STATIC AUDIT PASS / PUBLICATION BLOCKER CONFIRMED  
**Quellenbasis:** main commit 51bcc8fccb092c104ac0fca5fc98a5b996dcb914; Tree 65f423f04bbb2f1462f120a6b31073644cdc28cc  
**GitHub-Actions-Lauf:** 41661852782 — SUCCESS  
**Maschinenlesbarer Befund:** drafts/2026-11-03_UniverseLab_RC18_ExposureFindings_v1.0_DRAFT.json

## 1. Zentraler Sicherheitsbefund

**[BESTÄTIGT]** Der aktive Workflow .github/workflows/deploy-pages.yml verwendet actions/upload-pages-artifact@v4 mit dem Parameter **path: .**. Er wird auf push nach main oder manuell gestartet. Dieser Pfad lädt die Repository-Root-Inhalte als statisches Pages-Artefakt und enthält keine explizite Liste ausschließlich zur Veröffentlichung freigegebener Dateien.

**Konsequenz:** Wenn in Zukunft neue Dateien aus drafts/ nach main gemergt und das Deployment erfolgreich ausgeführt wird, können diese Dateien Bestandteil des Pages-Artefakts werden. Nicht verlinkte Dateien sind dadurch nicht zuverlässig vor direktem URL-Zugriff geschützt. Eine tatsächliche öffentliche RC18-Draft-URL wurde nicht erzeugt oder abgerufen.

**[BESTÄTIGT]** UniverseLab ist ein öffentliches GitHub-Repository. Auch ohne Pages-Deployment sind Dateien auf öffentlichen Repository-Branches und Pull Requests öffentlich über GitHub zugänglich. DRAFT ist ein kanonischer Status, **kein Vertraulichkeitslabel**.

Das zuvor erwogene automatische Routinedraft-Mergen ist daher **BLOCKED**. Ein bestandenes Dateischema darf keine Veröffentlichungserlaubnis schaffen.

## 2. Prüfungsumfang und konkrete Ergebnisse

Das Scanner-Skript tools/2026-11-03_UniverseLab_RC18_DraftExposureAudit_v1.0.py hat über git archive **1.157 von 1.157 getrackten Git-Blobs** des gepinnten Main-Trees eingelesen, insgesamt **9.242.253 Byte**. Die GitHub-CI bestätigte außerdem **13/13 Testmethoden**.

| Eintrag | Ergebnis |
|---|---:|
| Main-Dateien unter drafts/ | 0 |
| Wörtliche Textverweise auf drafts/ | 0 |
| Dateien mit allgemeinen Such-, Glob- oder Artefaktmustern | 50 |
| Ungefiltertes Pages-Root-Deployment | Ja |
| Tatsächliche künftige Pages-Auslieferung einer Draft-Datei getestet | Nein |

Die 50 lexikalischen Treffer umfassen 28 Workflows, drei Tests, 18 Tools und ein Root-Prüfskript. Das sind **Kandidaten für semantische Folgeprüfung, keine 50 bestätigten Draft-Importer**. Ein vollständiger statischer Textscan beweist nicht, dass dynamische oder externe Leser fehlen.

## 3. Zwei zusätzliche konkret belegte Datenflussrisiken

**Datenschutz:** Der vorhandene Scanner tools/2026-08-03_validate_public_repository_privacy_v1.0.py durchsucht in SCAN_ROOTS nur registry, governance, prompts und science sowie eine feste Auswahl von Root-Dateien. drafts/ ist nicht enthalten. Somit gewährleistet der bestehende Privacy-Scan keine Prüfung künftiger Draft-Notizen.

**Indirekte Forschungsdiagnostik:** tools/2026-08-31_scan_hzt_m0_fm0_beta_tau_provenance_v0.1.py verwendet ROOT.rglob("*") und berücksichtigt JSON-Dateien als Text. Der Workflow .github/workflows/2026-08-31_HZT_M0_FM0_BetaTauProvenanceScan_v0.1.yml läuft bei Pull Requests. Enthalten neue Drafts die abgefragten beta_tau-Tokens, können sie diagnostische Treffer und Zählungen beeinflussen. Das ist keine Solverausführung und keine automatische wissenschaftliche Ratifikation, verhindert aber die Behauptung vollständiger Draft-Isolation.

## 4. Notwendige technische Abhilfe — eigenständiger künftiger Review

1. **Vertraulichkeit:** Private Forschungsnotizen und personenbezogene Daten nicht in das öffentliche Repo committen. Eine spätere Pages-Allowlist macht ein öffentliches GitHub-Repository nicht privat. Ggf. ein separates privates Forschungs-Repository nutzen.
2. **Pages explizit filtern:** Statt path: . ein definiertes, vorher gebautes Public-Only-Stagingverzeichnis wie _site/ verwenden. Dateien nur über eine versionierte Publikations-Allowlist kopieren; drafts/, interne Tools und Governance-Dateien nicht pauschal übernehmen.
3. **Bestehende Website erhalten:** Vor der Umstellung alle tatsächlich benutzten öffentlichen HTML-, JS-, CSS-, Service-Worker-, Asset- und Registry-Referenzen nachverfolgen und auf fehlende Ziele prüfen. Sonst drohen neue 404-Fehler.
4. **Negative Publikations-Canary:** Einen harmlosen synthetischen Draft-Marker ausschließlich im temporären Staging-Test erzeugen. Beweisen, dass weder das Public-Only-Build noch ein simuliertes Pages-Artefakt ihn enthalten. Keine vertraulichen Daten für diesen Test verwenden.
5. **Privacy-Gate erweitern:** Neue öffentlich lesbare Drafts, falls gewünscht, einschließlich verbotener JSON-Schlüssel, personenbezogener Inhalte und Secret-Muster scannen. Das ist getrennt von wissenschaftlichen Claims.
6. **Diagnostik abgrenzen:** Globale Provenienz-Scanner müssen Draft-Funde als nichtkanonisch klassifizieren oder ausdrücklich aus kanonischen Evidenz-Zählungen ausschließen.
7. **Freigabegrenzen:** Erst nach separater Owner-Entscheidung zu öffentlicher Sichtbarkeit, einem geprüften Pages-Build, realen Negativtests und aktiven geschützten GitHub-Required-Checks darf ein Routinemerge-Pfad erwogen werden.

Diese Schritte sind **Arbeitsanforderungen**, keine Autorisierung zur Änderung der Hauptwebsite oder GitHub-Einstellungen.

## 5. Evidenzklassen

- **[BESTÄTIGT]** Alle 1.157 gepinnten Git-Blobs wurden eingelesen; Root-Deployment, fehlende Draft-Abdeckung im Datenschutzscanner und eine potenzielle indirekte diagnostische Draft-Verarbeitung sind im Quellcode erkennbar.
- **[KONDITIONAL]** Draft-Dateien werden nach zukünftigem Merge Teil eines unverändert betriebenen GitHub-Pages-Artefakts. Keine künftige Datei wurde tatsächlich veröffentlicht oder als konkrete Website-URL verifiziert.
- **[OFFEN]** Vollständige Laufzeit-Datenflussanalyse, externe Leser, semantische Prüfung aller 50 Kandidaten, zukünftiges Deployment-Artefakt, konkrete GitHub-Actions-/Required-Check-Installation.
- **[NICHT BEHAUPTET]** Mathematischer Beweis, physikalische Validierung, empirische HZT-Identifikation oder Ghostfreiheit.

**Statusvertrag:** RC18_FULL_MAIN_LEXICAL_SCAN=PASS; RC18_ROOT_PUBLICATION=BLOCKER; RC18_ROUTINE_AUTO_MERGE=HOLD; PR263=DRAFT_UNMERGED; PR264=DRAFT_UNMERGED; MAIN=UNCHANGED; PHYSICAL_GATE_EFFECT=NONE; PHYSICAL_EVIDENCE_EFFECT=NONE.
