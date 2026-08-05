# HZT-M0-S6 C-PHYS-M1 — Background-3C8 Physical Execution Adapter Ledger v0.1

**Datum:** 2026-08-05  
**Track:** `MD2S-R1-C-PHYS`  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Block:** `C-PHYS-R1.0-BACKGROUND-3C8_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_ONLY`

## 1. Ziel

Background-3C8 schließt die technische Lücke zwischen dem in Background-3C6 geprüften Kontrolltransaktionskern und den bereits vorhandenen, aber nicht autorisierten realen numerischen Backends. Der Block implementiert und prüft ausschließlich:

- unveränderliche Bindung an Run-ID, Payload-Hash, Seed-Spezifikation und Netzfolge,
- statische Bindung an die realen Backend-Quellen und erwarteten Exportfunktionen,
- Serialisierung der vollständigen sieben Seeds über fünf Netze,
- Primär-zu-Independent-Kandidatenübergabe,
- Übersetzung in eine strukturell vollständige Vorschau des eingefrorenen Resultatschemas,
- ressourcenbegrenzte Subprozessausführung,
- einmalige Kontrollfähigkeit mit Replay-Verweigerung,
- atomaren, externen Kontrollartefaktabschluss,
- saubere Timeout- und Signalabbrüche.

## 2. Harte wissenschaftliche Grenze

Die ausführbaren 3C8-Tests verwenden ausschließlich hergestellte Backend-Stubs. Die realen Dateien

- `tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py`,
- `tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py`

werden gehasht und per AST auf die erwarteten Exportnamen geprüft. Sie werden weder importiert noch aufgerufen.

Daraus folgt ausdrücklich nicht:

- dass Newton oder Shooting technisch am Zielpunkt funktioniert,
- dass ein Hintergrundkandidat existiert,
- dass Primär- und Independent-Backend physisch übereinstimmen,
- dass die Kontinuumsaufgabe lösbar oder eindeutig ist,
- dass Fredholm-Eigenschaften, Stabilität oder Ghostfreiheit gelten,
- dass K1-D oder K1-E verändert werden dürfen.

## 3. Unveränderliche Bindung

```text
run_id                  = HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1
run_payload_sha256      = 0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302
seed_set_id             = M1-BG3B-CP01-SEEDS-01
seed_spec_sha256        = b6e4319cc29736799a0b46320002e51cd17b70b724a6b4c6e86567a316996161
seed_count              = 7
node_counts             = 24, 32, 48, 64, 96
schedule_entries        = 35
schedule_order          = seed-major, danach aufsteigende Knotenzahl
```

## 4. Kontrolltransaktion

```text
Vertragsprüfung
→ Paket- und Backend-Quellhashes
→ AST-Exportprüfung ohne Import
→ hergestellte Kontrollfähigkeit
→ einmaliger Konsum / Replay-Sperre
→ vollständige Schedule-Serialisierung
→ Primary-Stub im begrenzten Subprozess
→ Kandidaten-Handoff mit SHA-256
→ Independent-Stub im begrenzten Subprozess
→ Resultatschema-Vorschau
→ Klassifikation
→ externer atomarer Kontrollabschluss
```

Vier Kontrollfälle sind registriert:

```text
manufactured_success
manufactured_disagreement
manufactured_timeout
manufactured_signal
```

## 5. Resultatschema-Vorschau

Die Vorschau enthält alle im eingefrorenen Background-3C-Resultatschema geforderten Top-Level-, Primär-, Independent- und Kandidatenfelder. Sie bleibt jedoch in einem externen temporären **Kontrollartefakt** eingebettet und trägt:

```text
execution_started_utc                  = null
execution_finished_utc                 = null
final_classification                   = NOT_EXECUTED_IMPLEMENTATION_FAILURE
result_schema_preview_is_physical_result = false
physical_evidence_effect               = NONE
```

Damit wird ausschließlich die strukturelle Übersetzbarkeit geprüft.

## 6. Kontrollfähigkeit und Replay-Schutz

3C8 erzeugt keine operative Freigabe. Die hergestellte Kontrollfähigkeit besitzt den Scope

```text
MANUFACTURED_ADAPTER_CONTROL_ONLY
```

und ist an Kontroll-ID, Run-ID, Payload-Hash und Adapter-Paketdigest gebunden. Ihr Konsum wird exklusiv geschrieben; ein zweiter Konsum desselben Tokens muss scheitern. Diese Prüfung zeigt die Replay-Mechanik, ersetzt aber keinen späteren append-only Ausführungsgrant.

## 7. Unveränderte Gates

```text
BACKGROUND_3C_EXECUTION       = NOT_AUTHORIZED
BACKGROUND_SOLVER_EXECUTION   = NOT_AUTHORIZED
PHYSICAL_BACKGROUND           = NOT_ESTABLISHED
R1.1                          = BLOCKED
R1.2                          = BLOCKED
official_MD2S_solver          = NOT_AUTHORIZED
K1-D                          = NOT_RELEASED
K1-E                          = NOT_ADMISSIBLE
physical_evidence_effect      = NONE
```

## 8. Erfolgskriterium

3C8 darf nur als bestanden gelten, wenn:

1. alle statischen Bindungen reproduzierbar sind,
2. beide hergestellten Adapterstufen end-to-end funktionieren,
3. absichtliche Abweichung korrekt verworfen wird,
4. Timeout und Signal ohne finales Artefakt enden,
5. Replay und No-Overwrite sicher scheitern,
6. reale Backendimporte und physische Solverzähler exakt null bleiben,
7. CP01R1 weiterhin mit Exitcode 73 verweigert wird.

Ein bestandener Block erlaubt ausschließlich den nächsten Review:

```text
C-PHYS-R1.0-BACKGROUND-3C9_PHYSICAL_ADAPTER_AUTHORIZATION_REVIEW_ONLY
```

Dieser Review darf nicht automatisch einen operativen Grant erzeugen oder CP01R1 ausführen.
