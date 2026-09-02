# ULSH-01 WP2 · Authority- und Signaturprovenienzvertrag v0.1

**Datum:** 2026-09-02  
**Track:** `MD2S-R1-C-PHYS`  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Run:** `HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4`  
**Status:** `DRAFT_NOT_RATIFIED`  
**Klassifikation:** nichtoperativer Vertragskandidat  
**Physical gate effect:** `NONE`  
**Physical evidence effect:** `NONE`

## 1. Kernresultat

Der bisherige technische Decision-/Grant-Vertrag bindet Run-ID, Release-Subject, Target-Digest, Run-Payload, Paketdigest, Zeitfenster, Nonce und Single-Use-Semantik. Er beantwortet jedoch nicht die logisch vorgelagerte Frage:

> Welche bereits ratifizierte Autorität ist berechtigt, die operative Decision beziehungsweise den Grant auszustellen, und wie wird kryptographisch geprüft, dass genau diese Autorität die kanonischen Bytes signiert hat?

Der neue Block schließt die **technische Spezifikations- und Verifikationslücke**, nicht die menschliche Ratifikation.

Damit gilt jetzt:

```text
Authority-/Signaturprofil:          IMPLEMENTIERT
reiner Verifier:                    IMPLEMENTIERT
synthetische Positiv-/Negativ-QA:   IMPLEMENTIERT
ratifizierte operative Autorität:   NICHT VORHANDEN
ratifizierter Trust Root:           NICHT VORHANDEN
operative Decision:                 NICHT ERZEUGT
operativer SingleUseGrant:          NICHT ERZEUGT
```

Folglich bleibt

`AUTHORITY_SIGNATURE_PROVENANCE = BLOCKD_PENDING_EXPLICIT_HUMAN_TRUST_ROOT_RATIFICATION`.

## 2. Warum eine Signatur allein keine Autorität erzeugt

Sei `K_pub` ein öffentlicher Schlüssel und `K_priv` der zugehörige private Schlüssel. Eine gültige Signatur beweist innerhalb der kryptographischen Annahmen lediglich:

1. der Signierer kontrollierte beim Signieren `K_priv`;
2. die signierten Bytes wurden nach dem Signieren nicht verändert.

Sie beweist **nicht aus sich selbst*, dass der Schlüsselinhaber im UniverseLab-Forschungsprogramm ausstellungsberechtigt ist. Dafür ist eine externe Zuordnung nötig:

`K_pub → authority_id → ratifizierte Rolle`.

Ohne diese Zuordnung entsteht ein Bootstrap-Zirkel:

`Schlüssel ist autorisiert, weil er ein Dokument signiert, das den Schlüssel autorisiert.`

Der Vertrag verlangt deshalb zusätzlich zur Root-Key-Proof-of-Possession eine explizite, menschlich zurechenbare Projektinhaber-Adoption des exakten Trust-Root-Digests.

## 3. Trust-Bootstrap

Ein zukünftiger operativer Trust Root benötigt mindestens:

- eine stabile `authority_id`;
- eine menschlich kontrollierte Projektidentität oder pseudonyme Projektidentität;
- die Rollen `AUTHORIZATION_DECISION_ISSUER` und/oder `SINGLE_USE_GRANT_ISSUER`;
- einen rohen Ed25519-Public-Key;
- `SHA256(raw_public_key)` als Fingerprint;
- Gültigkeitsbeginn und -ende;
- Revocation- und Rotationsemantik;
- eine Root-Key-Proof-of-Possession-Signatur;
- eine explizite menschliche Adoption des exakten Trust-Root-Artefaktdigests;
- einen überprüfbaren Repository-Commit oder Tag für diese Adoption;
- eine Erklärung, dass der private Schlüssel weder Repository-CI noch Assistenzsystemen oder Automationen zugänglich ist.

Nicht hinreichend sind jeweils allein:

- ein Chat-Kommando wie `Go`;
- Repository-Eigentum ohne gebundenen Schlüssel;
- eine Selbstsignatur ohne Projektinhaber-Adoption;
- ein gemergtes JSON-Artefakt ohne zurechenbare Ratifikation;
- grüne CI;
- ein AuthorizationReview;
- ausgefüllte, aber unsignierte Decision-/Grant-Dateien.

## 4. Signaturprofil

### 4.1 Nachrichtenbildung

Der signierte Inhalt besteht aus

```json
{
  "protected": { ... },
  "payload": { ... }
}
```

Die kanonischen Bytes heïsen `C`. Die tatsächlich signierte Nachricht lautet

`M = domain_separator || C`,

mit

`domain_separator = UTF8("UNIVERSELAB-AUTHORITY-ATTESTATION-V1") || 0x00`.

Die Domain-Separation verhindert, dass eine formal gültige Signatur aus einem anderen Protokollkontext als UniverseLab-Autorisierung wiederverwendet wird.

### 4.2 Canonical-JSON-Profil

`UL-CANONICAL-JSON-v1` verlangt:

- UTF-8 ohne BOM;
- keine doppelten Objektschlüssel;
- lexikographisch nach Unicode-Codepoints sortierte Schlüssel;
- keine überflussigen Leerzeichen;
- ausschliesslich `null`, boolesche Werte, Strings, Arrays, Objekte und Ganzzahlen;
- keine Gleitkommazahlen;
- Ganzzahlen nur in `[-(2^53-1), +(2^53-1)]`;
- keine isolierte UTF-16-Surrogatcodepoints.

Die Float-Sperre ist absichtlich streng. Autorisierungsartefakte bestehen aus IDs, Digests, Flags, Zeitstempeln und diskten Zahlern; eine plattformabhaengige Dezimalserialisierung ist daher unnoetig und wuerde die Byteidentitaet gefaehrden.

### 4.3 Ed25519-Pruefung

Das Profil verwendet Ed25519 gemaessRFC 8032. Mit Basepoint `B`, Public-Key-Punkt `A`, Nonce-Punkt `R`, Skalar `S` und

`h = SHA512(R || A || M) mod L`

wird geprueft:

`[S]B = R + [h]A`.

Der Verifierakzeptiert nur:

- exakt 32 Byte Public-Key;
- exakt 64 Byte Signatur;
- kanonische Punktkodierungen;
- nichttriviale Punkte in der Primordnungs-Untergruppe;
- `S < L`;
- uebereinstimmenden Public-Key-Fingerprint;
- uebereinstimmenden Digest der domain-separierten signierten Bytes.

Das Tool enthaelt bewusst **keine Signierfunktion**.

## 5. Rollen und Artefakte

### AuthorizationDecision

Erforderliche Schluesselrolle:

`AUTHORIZATION_DECISION_ISSUER`.

Ein zukuenftiger operativer Payload muss weiterhin den bereits eingefrorenen Statusliteral verwenden:

`AUTHORIZED_SINGLE_USE_WP2_CP01R4_PRIMARY_TARGET_EXECUTION`.

### SingleUseGrant

Erforderliche Schluesselrolle:

`SINGLE_USE_GRANT_ISSUER`.

Der operative Scope bleibt:

`HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4_TARGET_ONLY`.

Decision und Grant bleiben getrennte Artefakte. Beide benoetigen eine gueltige Attestation und muessen dieselben Run-, Target-, Release-Subject- und Paketbindungen besitzen.

### TrustRootRatification

Die Rolle `TRUST_ROOT_RATIFIER` dient zunaechst der Root-Key-Proof-of-Possession. Diese Selbstsignatur ersetzt nicht die externe menschliche Adoption.

## 6. Key-Custody, Rotation und Revocation

Der Vertrag verbietet:

- private Schluessel im Repository;
- private Schluessel in CI-Secrets fuer diesen Autorisierungspfad;
- private Schluessel in Chats;
- Uebergabe privater Schluessel an Assistenzsysteme oder Automationen.

Ein operativer Verifier akzeptiert nur einen aktuell `ACTIVE` Schluessel. Ein als widerrufen markierter Schluessel scheitert fail-closed unabhaengig vom frueheren Signaturzeitpunkt. Rotation erfordert ein neues versioniertes Trust-Root-Artefakt mit expliziter Vorgaenger-/Nachfolgerbindung.

Diese strenge Regel priorisiert die sichere Ausfuehrungssperre. Eine spaetere historische Archivvalidierung kann getrennt spezifiziert werden; sie darf nicht mit operativer Zulaessigkeit verwechselt werden.

## 7. Synthetische QA

Die Tests verwenden ausschliesslich einen oeffentlichen synthetischen Testschluessel und fest signierte Kontrollartefakte. Der private Testschluessel wird nicht committed.

Ein synthetischer Positivtest endet zwingend mit

`PASS_SYNTHETIC_CONTROL_ONLY_NO_AUTHORIZATION`.

Er setzt immer:

```text
operative_authorization_allowed = false
backend_imported = false
solver_executed = false
physical_evidence_effect = NONE
```

Negativ geprueft werden unter anderem:

- unratifizierter Repository-Trust-Root;
- Payload- und Signaturmutation;
- unbekannte Autoritaet oder unbekannter Schluessel;
- Fingerprintabweichung;
- fehlende Schluesselrolle;
- widerrufener oder abgelaufener Schluessel;
- Signaturzeitpunkt in der Zukunft;
- Float im signierten Payload;
- doppelter JSON-Schluessel;
- falsche Run-ID trotz kryptographisch gueltiger synthetischer Signatur.

## 8. Noch offene menschliche Ratifikation

Die Repository-Datei

`2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorityTrustRootCandidate_v0.1.json`

ist absichtlich leer. Sie etabliert weder Autoritaet noch Trust Root. Fuer eine spaetere Ratifikation muss Stefan beziehungsweise eine von ihm ausdruecklich bezeichnete Projektinstanz ausserhalb der Assistenzautomation einen Ed25519-Schluessel kontrollieren und ausschliesslich den Public-Key sowie den Fingerprint in einen neuen versionierten Trust Root eintragen.

Bis zur expliziten Ratifikation muss der Verifier fuer operative Artefakte mit

`TRUST_ROOT_NOT_RATIFIED`

abbrechen.

## 9. Unabhaengiger zweiter Blocker

Selbst ein spaeter gueltiger Autoritaet-Attestation-PASS genuegt nicht zur Ausfuehrung. Unabhaengig davon bleibt

`RUNTIME_ISSUANCE_BINDINGS = BLOCKED`.

Noch erforderlich sind insbesondere:

- Execution-Environment-ID;
- persistenter Reservation Store;
- Crash-Persistenz und Zugriffssteuerung;
- exklusiver Resultatpfad;
- Runtime-, Dependency-, Thread-, GPU-, Network- und Memory-Attestationen.

Damit gilt logisch:

`gueltige Authoritaetssignatu ∧ gueltige Decision ∧ gueltiger Grant`

ist notwendig, aber ohne Runtime-Issuance-Bindings nicht hinreichend.

## 10. Gate-Status

```text
Authority-Signature-Vertragsprofil: IMPLEMENTED_DRAFT
Trust Root:                         NOT_RATIFIED
Authority verifier:                 IMPLEMENTED_NON_SIGNING
Synthetic QA:                       PASS_LOCAL_PRECOMMIT
Runtime issuance:                   BLOCKED
AuthorizationDecision:              NOT_CREATED
SingleUseGrant:                     NOT_CREATED
Backendimport:                      NOT_EXECUTED
CP01R4:                              NOT_EXECUTED
physical background:               NOT_ESTABLISHED
physical response rank:             NOT_EXECUTED
WP3:                                NOT_STARTED
WP4:                                BLOCKED_NOT_AUTHORIZED
K1-D:                              NOT_RELEASED
K1-E:                               NOT_ADMISSIBLE
physical gate effect:               NONE
physical evidence effect:           NONE
```
