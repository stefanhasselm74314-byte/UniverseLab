# ULSH-01 WP2 · Owner-Ratification Bridge v0.2

**Datum:** 2026-09-23  
**Track:** `MD2S-R1-C-PHYS`  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Run:** `HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4`  
**Status:** `DRAFT_NOT_RATIFIED`  
**Klassifikation:** nichtoperativer, fail-closed Owner-Ratification-Bridge-Vertrag  
**Physical gate effect:** `NONE`  
**Physical evidence effect:** `NONE`

## 1. Zweck

Diese Revision ist ein append-only Nachfolger des technischen Authority-/Signaturvertrags v0.1.

v0.1 spezifiziert das kryptographische Signaturprofil, die kanonischen Bytes, Rollen, Trust-Root-Struktur und synthetische QA. Nach der später ratifizierten Governance-Grenze aus PR #236 reicht jedoch

```text
RATIFIED_ACTIVE contract
AND RATIFIED_ACTIVE trust root
```

für eine positive reservierte Entscheidung nicht aus.

Für `AUTHORIZATION_DECISION` und `SINGLE_USE_GRANT` ist zusätzlich eine explizite, aktuelle, sachlich begrenzte und exakt gebundene Owner-Ratifikation erforderlich.

## 2. Verbindlicher Bridge-Status

In v0.2 existiert absichtlich **kein positiver operativer Pfad**.

Solange kein unabhängig verifizierbares Owner-Ratifikationsschema implementiert ist, gilt:

```text
operative-shaped reserved artifact
+ RATIFIED_ACTIVE authority contract
+ RATIFIED_ACTIVE trust root
+ no independently verifiable concrete owner ratification
= OWNER_RATIFICATION_NOT_VERIFIABLE
= FAIL_CLOSED
```

Der Bridge-Verifier darf daher in dieser Revision niemals
`operative_authorization_allowed=true`
für irgendeinen unterstützten operativen Artefakttyp liefern. Das umfasst
`AUTHORIZATION_DECISION`, `SINGLE_USE_GRANT` und
`TRUST_ROOT_RATIFICATION`.

Eine Trust-Root-Proof-of-Possession-Prüfung ist in v0.2 nur im
synthetischen Kontrollpfad zulässig. Ein `RATIFIED_ACTIVE`-Pfad für
`TRUST_ROOT_RATIFICATION` endet ebenfalls fail-closed mit
`OWNER_RATIFICATION_NOT_VERIFIABLE`.

## 3. Warum v0.1 nicht stillschweigend umdefiniert wird

Die kryptographische Signed-Envelope-ID aus v0.1 bleibt für die bestehenden synthetischen Testvektoren eingefroren:

`ULSH01-WP2-AUTHORITY-SIGNATURE-PROVENANCE-v0.1`.

Der neue Governance-/Policy-Vertrag besitzt dagegen die eigene Kennung

`ULSH01-WP2-AUTHORITY-SIGNATURE-PROVENANCE-v0.2`.

Damit sind zwei Ebenen getrennt:

1. eingefrorenes v0.1-Signaturprotokoll und synthetische Kontrollvektoren;
2. v0.2-Policy-Bridge, die jede positive reservierte Operation fail-closed blockiert.

v0.1 darf nach dieser Supersession nicht mehr in einen operativen Zustand hochgestuft werden.

## 4. Erforderliche Bindungen einer späteren Owner-Ratifikation

Ein zukünftiger positiver Pfad benötigt mindestens eine unabhängig überprüfbare Bindung an:

- Owner-Identität;
- konkrete reservierte Decision-ID;
- Artefakttyp;
- Run-ID;
- Target-Digest;
- Run-Payload-Digest;
- Repository-Commit;
- Release-Package-Manifest-Digest;
- Ratifikationszeitpunkt;
- Ablaufzeit oder explizites Gültigkeitsfenster.

Nicht hinreichend sind:

- Erinnerung oder persistenter Kontext;
- Chattitel;
- Repository-Eigentum;
- grüne CI;
- ein nicht eindeutig referenziertes `Go`;
- frei ergänzte Payload-Felder wie `owner_ratification_status=APPROVED`.

## 5. Zukünftiger positiver Pfad

Ein späterer positiver operativer Verifier darf nur über einen **neuen versionierten Vertrag oder einen explizit versionierten Dispatch-Pfad** eingeführt werden.

Er muss die konkrete Owner-Ratifikation vor jeder positiven reservierten Policy-Entscheidung deterministisch prüfen.

Erst danach wäre ein Resultat wie

`PASS_OPERATIVE_AUTHORITY_ATTESTATION`

überhaupt wieder zulässig.

Auch dann bliebe es **nicht hinreichend für Solverausführung**. Runtime-Issuance, Single-Use-Claim, Reservation Store, Environment-Attestation und Execution Harness bleiben unabhängige Gates.

## 6. Adversariale Regression

Die v0.2-QA muss mindestens zeigen:

- operative AuthorizationDecision ohne Owner-Ratifikation → `OWNER_RATIFICATION_NOT_VERIFIABLE`;
- operativer SingleUseGrant ohne Owner-Ratifikation → `OWNER_RATIFICATION_NOT_VERIFIABLE`;
- `authorized=true`, operative Status-/Scope-Literale und nichtleere Commit-/Package-Digests umgehen den Hold nicht;
- frei erfundene Owner-Felder umgehen den Hold nicht;
- synthetische Kontrollartefakte bleiben nonoperativ und bestehen unverändert;
- Backend-Import, Solverlauf, K1-D/K1-E und physikalische Evidenz bleiben unverändert geschlossen.

## 7. Unveränderte Firewalls

```text
Trust Root:                    NOT_RATIFIED
Runtime issuance:              BLOCKED
AuthorizationDecision:         NOT_CREATED
SingleUseGrant:                NOT_CREATED
Backend import:                NOT_EXECUTED
Solver execution:              NOT_EXECUTED
Physical background:           NOT_ESTABLISHED
Physical response rank:        NOT_EXECUTED
K1-D:                          NOT_RELEASED
K1-E:                          NOT_ADMISSIBLE
physical gate effect:          NONE
physical evidence effect:      NONE
```
