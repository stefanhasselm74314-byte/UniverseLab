# HZT-M0 Forward Map — FM-0 Parameter-/Symbol-/Provenienz-Inventar v0.1

**Datum:** 2026-08-29  
**Workstream:** WS1 · HZT-M0 Forward Map & Observables  
**Work Package:** FM-0  
**Status:** `ACTIVE_INITIAL_INVENTORY`  
**Gate:** `FM-G0 = OPEN`  
**Klassifikation:** `PROVENANCE_INVENTORY_NO_NEW_PHYSICS`

## Ziel

FM-0 inventarisiert alle HZT-M0-Kerngrößen so, dass **Definition, Dimension/Einheit, Herkunft, Statusklasse, Konvention/Gültigkeitsbereich und Observable-Bezug** explizit sind. Das Inventar beginnt bewusst mit Lückenmarkierungen; eine Lücke ist zulässig, eine still ergänzte textbook-Konvention nicht.

## Initialer Parametersatz aus dem ratifizierten Programm

| Symbol | Rolle | Dimension | Parent-Provenienz | Mappingstatus |
|---|---|---|---|---|
| `a0` | fundamental / abgeleitet / effektiv: **offen** | `OPEN_RECOVERY_REQUIRED` | `OPEN_RECOVERY_REQUIRED` | `NOT_YET_CLAIMED` |
| `β_τ` | fundamental / abgeleitet / effektiv: **offen** | `OPEN_RECOVERY_REQUIRED` | `OPEN_RECOVERY_REQUIRED` | `NOT_YET_CLAIMED` |
| `R_χ` | fundamental / abgeleitet / effektiv: **offen** | `OPEN_RECOVERY_REQUIRED` | `OPEN_RECOVERY_REQUIRED` | `NOT_YET_CLAIMED` |
| `𝓘_B` | fundamental / abgeleitet / effektiv: **offen** | `OPEN_RECOVERY_REQUIRED` | `OPEN_RECOVERY_REQUIRED` | `NOT_YET_CLAIMED` |
| `κ_6` | fundamental / abgeleitet / effektiv: **offen** | `OPEN_RECOVERY_REQUIRED` | `OPEN_RECOVERY_REQUIRED` | `NOT_YET_CLAIMED` |

Diese Tabelle ist **kein Parent-Beweis**. Sie übernimmt nur den Parametersatz aus dem ratifizierten Arbeitsprogramm und erzwingt die anschließende Provenienz-Recovery.

## Initiale Observable-Blöcke

- `O_RAR`
- `O_cosmo`
- `O_growth`
- `O_lensing`
- `O_GW`

Status jeweils: `INTERFACE_TO_RECOVER_OR_DEFINE`.

## FM-0 Arbeitsreihenfolge

1. Exakte kanonische Definitionen aus ratifizierten/frozen Repository-Artefakten einsammeln.
2. Jede Größe als fundamental, abgeleitet, effektiv, Kandidat oder unresolved klassifizieren.
3. Dimensionen/Units provenance-gebunden erfassen; keine stillen Lehrbuchsubstitutionen.
4. Parent→Reduced- und Reduced→Observable-Lücken als explizite Gap-Einträge erfassen.
5. Grenzfall-/Konventionsabhängigkeiten markieren.
6. Erst nach geschlossenem FM-G0 neue Mapping-Ableitungen beginnen.

## FM-G0 Definition of Done

FM-G0 kann nur geschlossen werden, wenn keine HZT-M0-Kerngröße ohne expliziten Definition-/Unit-/Provenienzstatus verbleibt. **Ungeklärte** Größen dürfen bestehen, müssen aber als explizite Lücken registriert sein.

## Verbotene Schlussfolgerungen

- `PROGRAM_DECLARATION_IS_NOT_PARENT_PROVENANCE`
- `NO_EFFECTIVE_RELATION_IS_A_6D_DERIVATION_WITHOUT_ALL_INTERMEDIATE_STEPS`
- `NO_PARAMETER_FIT_BEFORE_MAPPING_STRUCTURE_FREEZE`
- `NO_PHYSICAL_BACKGROUND_CLAIM`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`

CP01R4-Abhängigkeit für dieses Inventar: `NONE`.  
Physische Evidenzwirkung: `NONE`.
