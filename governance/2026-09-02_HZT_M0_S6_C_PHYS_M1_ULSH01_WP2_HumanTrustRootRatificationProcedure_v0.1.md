# ULSH-01 WP2 · Human-Trust-Root-Ratifikationsverfahren v0.1

**Datum:** 2026-09-02  
**Basis-`main`:** `3286bdbf9c89e744d0a4f0117315acff9bd78795`  
**Status:** `PREPARATION_ONLY_NOT_RATIFIED`  
**Physical gate effect:** `NONE`  
**Physical evidence effect:** `NONE`

## 1. Kernresultat

Dieser Block bereitet den menschlichen Trust-Bootstrap technisch vor, ratifiziert ihn aber nicht.

Die notwendige logische Kette lautet:

`menschlich kontrollierter Private Key`
→ `öffentlicher Schlüssel`
→ `Kandidaten-Trust-Root`
→ `Root-Key Proof of Possession`
→ `expliziter Projektinhaber-Adoptionsdatensatz`
→ `manuelle Attributionsprüfung`
→ `neues versioniertes RATIFIED_ACTIVE-Artefakt`.

Kein Schritt dieses Pull Requests darf die letzte Transition selbst ausführen.

## 2. Warum Besitznachweis und Autorität getrennt bleiben

Eine gültige Ed25519-Signatur über einen Proof-of-Possession-Nachrichtensatz zeigt unter den kryptographischen Annahmen, dass der Signierer den zum Kandidaten-Public-Key gehörenden privaten Schlüssel kontrolliert.

Sie zeigt nicht:

- dass der Schlüsselinhaber ein Mensch ist;
- dass dieser Mensch die legitime Projektinstanz kontrolliert;
- dass die im Trust Root eingetragenen Rollen vom Projektinhaber akzeptiert wurden;
- dass die Private-Key-Custody-Erklärung faktisch wahr ist;
- dass ein Revokationskanal tatsächlich erreichbar ist.

Formal:

`PoP(K_pub, sigma)=PASS`

impliziert nur Schlüsselkontrolle, nicht

`authority_id ∈ ratified_project_authorities`.

Der Bootstrap benötigt deshalb einen separaten Adoptionsdatensatz, der den exakten Kandidaten- und PoP-Digest bindet. Dessen menschliche Zurechenbarkeit bleibt eine manuelle Reviewfrage.

## 3. Sicherheitsgrenze

Die Repository-Werkzeuge akzeptieren ausschließlich einen **öffentlichen** Ed25519-Schlüssel.

Sie dürfen nicht:

- einen privaten Schlüssel erzeugen;
- einen privaten Schlüssel lesen;
- einen privaten Schlüssel als CLI-Argument entgegennehmen;
- eine Signatur erzeugen;
- Schlüsselmaterial in Repository, CI, Chat oder Assistenzkontext übertragen.

Der Private Key bleibt vollständig auf einem vom Menschen kontrollierten Offline-System. Nur Public Key, Fingerprint, signierter PoP-Envelope und nichtgeheime Metadaten dürfen das Offline-System verlassen.

## 4. Rollenmodell und Least Privilege

Der erste Root Key sollte standardmäßig nur die Rolle

`TRUST_ROOT_RATIFIER`

erhalten.

Die Rollen

- `AUTHORIZATION_DECISION_ISSUER`,
- `SINGLE_USE_GRANT_ISSUER`

werden nicht automatisch vergeben. Separate operative Schlüssel sind empfohlen. Ein Einpersonenprojekt ist zulässig, muss aber im späteren Adoptionsdatensatz ausdrücklich offenlegen, dass die manuelle Prüfung als Self-Review erfolgte.

## 5. Offline-Ablauf

### Schritt A — Schlüssel außerhalb des Repositories erzeugen

Der Mensch erzeugt auf einem Offline-System ein Ed25519-Schlüsselpaar mit einem vertrauenswürdigen RFC-8032-kompatiblen Werkzeug.

Nicht zulässig:

- CI-Secret als Root Key;
- Assistant-generierter Root Key;
- Chat-Upload des Private Keys;
- Repository-Commit des Private Keys;
- Weitergabe des Private Keys an Automationen.

### Schritt B — Public Key vorbereiten

Der Public Key wird als 32 rohe Bytes oder als Base64 dieser 32 Bytes in eine lokale Datei geschrieben.

Der Preparer wird ausschließlich auf dem Offline-System ausgeführt:

```text
python tools/2026-09-02_prepare_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_HumanTrustRootCandidate_v0.1.py candidate \
  --public-key-file PUBLIC_KEY_FILE \
  --authority-id PROJECT-AUTHORITY-01 \
  --display-identity PSEUDONYMOUS_PROJECT_IDENTITY \
  --key-id ROOT-ED25519-01 \
  --role TRUST_ROOT_RATIFIER \
  --valid-from-utc 2026-09-02T00:00:00Z \
  --valid-until-utc 2031-09-02T00:00:00Z \
  --signed-at-utc 2026-09-02T00:00:00Z \
  --attestation-id ROOT-POP-01 \
  --challenge-nonce RANDOM_NONCE \
  --proof-expires-at-utc 2026-09-03T00:00:00Z \
  --output-dir OFFLINE_OUTPUT
```

Der Preparer erzeugt:

- einen Kandidaten-Trust-Root;
- einen unsignierten PoP-Envelope;
- die exakt zu signierenden domain-separierten Bytes;
- SHA-256-Digests;
- eine nichtoperative Zusammenfassung.

### Schritt C — Proof of Possession offline signieren

Die Datei mit den signierten Bytes wird auf demselben Offline-System mit dem Root Private Key signiert. Die 64-Byte-Signatur wird als Base64 in den PoP-Envelope eingetragen.

Die Signaturdomäne lautet:

`UNIVERSELAB-TRUST-ROOT-PROOF-OF-POSSESSION-V1 || 0x00`.

Signiert wird:

`domain_separator || canonical_json({protected,payload})`.

Der PoP-Envelope bleibt ausdrücklich:

`proof_of_possession_is_project_authority = false`.

### Schritt D — Projektinhaber-Adoptionsdatensatz vorbereiten

Nach Vorliegen des signierten PoP-Envelopes:

```text
python tools/2026-09-02_prepare_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_HumanTrustRootCandidate_v0.1.py adoption \
  --candidate CANDIDATE_JSON \
  --proof SIGNED_POP_JSON \
  --adoption-id OWNER-ADOPTION-01 \
  --project-identity PSEUDONYMOUS_PROJECT_IDENTITY \
  --adopted-at-utc 2026-09-02T00:00:00Z \
  --repository-commit-or-tag FUTURE_COMMIT_OR_TAG \
  --verification-provider HUMAN_REVIEW \
  --verification-reason EXPLICIT_PROJECT_OWNER_ADOPTION \
  --custody-location-class OFFLINE_ENCRYPTED_REMOVABLE_MEDIA \
  --backup-policy HUMAN_DEFINED_BACKUP_POLICY \
  --revocation-procedure HUMAN_DEFINED_REVOCATION_PROCEDURE \
  --single-human-self-review true \
  --output ADOPTION_JSON
```

Der erzeugte Datensatz hat weiterhin:

`ratified = false`.

### Schritt E — Technisch prüfen

```text
python tools/2026-09-02_verify_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_HumanTrustRootRatificationPackage_v0.1.py candidate \
  --contract CONTRACT_JSON \
  --candidate CANDIDATE_JSON \
  --proof SIGNED_POP_JSON \
  --adoption ADOPTION_JSON \
  --now-utc 2026-09-02T12:00:00Z
```

Der einzig zulässige positive Status lautet:

`PASS_CRYPTOGRAPHIC_BINDINGS_MANUAL_HUMAN_RATIFICATION_REQUIRED`.

Er bedeutet:

- Public-Key-Fingerprint stimmt;
- PoP-Signatur stimmt;
- Kandidaten-, PoP- und Adoptionsdigests stimmen;
- Rollen- und Zeitbindungen sind intern konsistent;
- **keine** menschliche Identität wurde maschinell bewiesen;
- **kein** Trust Root wurde ratifiziert;
- **keine** operative Ausführung wurde autorisiert.

## 6. Manuelle Attributionsprüfung

Vor einem späteren Ratifikations-PR muss ein Mensch prüfen:

1. Wer kontrolliert die angegebene Projektidentität?
2. Hat diese Instanz den exakten Kandidatendigest ausdrücklich angenommen?
3. Stimmt der Public-Key-Fingerprint mit dem offline kontrollierten Schlüssel überein?
4. Ist die Proof-of-Possession-Signatur gültig?
5. Sind Rollen, Gültigkeitszeitraum und Revokationsverfahren beabsichtigt?
6. Ist der Private Key tatsächlich von Repository, CI, Chat, Assistenten und Automationen getrennt?
7. Ist ein Einpersonen-Self-Review ausdrücklich offengelegt?

Repository- oder Commit-Eigentum ist unterstützende Provenienz, aber allein kein mathematischer Beweis menschlicher Identität.

## 7. Finale Ratifikation

Die finale Ratifikation darf nicht durch Änderung der Templates dieses Blocks erfolgen.

Erforderlich ist ein **neues versioniertes Artefakt** mit:

- `status = RATIFIED_ACTIVE`;
- `ratified = true`;
- exakt gebundenem Kandidaten-Raw- und Canonical-Digest;
- exakt gebundenem PoP-Digest;
- exakt gebundenem Adoptionsdatensatz;
- manueller Reviewentscheidung;
- Public-Key-Fingerprint;
- Rollen;
- Gültigkeitsfenster;
- Revokations- und Rotationsregen;
- Repository-Commit oder Tag der Adoption.

Dieser spätere PR benötigt einen eigenen Verifier und ein separates Review. Der hier gelieferte Verifier lehnt `RATIFIED_ACTIVE` absichtlich ab.

## 8. Nachgelagerte, unabhängige Sperren

Auch nach einer zukünftigen Trust-Root-Ratifikation bleiben blockiert:

- Runtime-Issuance-Bindings;
- Execution-Environment-Identität;
- persistenter Reservation Store;
- crash-persistente Single-Use-Semantik;
- exklusiver Resultatpfad;
- AuthorizationDecision;
- SingleUseGrant;
- Backendimport;
- CP01R4-Ausführung.

Daher:

`Trust-Root-Ratifikation ≠ Runtime-Freigabe ≠ Grant ≠ physische Ausführung`.

## 9. Unveränderter Gate-Status

```text
Ratified human trust root:  NOT_RATIFIED
Runtime issuance:           BLOCKED
AuthorizationDecision:      NOT_CREATED
SingleUseGrant:             NOT_CREATED
Backend import:              NOT_EXECUTED