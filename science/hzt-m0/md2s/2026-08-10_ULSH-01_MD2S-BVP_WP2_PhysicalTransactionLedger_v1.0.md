# ULSH-01 / MD2S-BVP — WP2 Physical Transaction Ledger v1.0

**Datum:** 2026-08-10  
**Architektur:** `HPVS -> HZT-M0 -> HZT-Full`  
**Aktiver Pfad:** `HZT-M0 -> S6 -> C-PHYS -> C1 -> ULSH-01 / WP2`  
**Status:** `PASS_WP2_TRANSACTION_IMPLEMENTED_RELEASE_READY_NO_SOLVE`  
**Evidenzeffekt:** `NONE`

## 1. Kernentscheidung

WP2 schließt die **Transaktions- und Freigabefähigkeit** für den eingefrorenen physischen BVP-Targetlauf `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1`, ohne den Lauf zu starten.

Gebunden werden:

- WP1 Target Boundary Contract + Ledger,
- der unveränderte CP01R1-Payload mit `a_F=1/4`,
- der deterministische 7-Seed/35-Entry-Plan,
- Primary-, Primary-Base- und Independent-Backend-Quellen,
- Dependency Lock,
- Resource Policy,
- Result Schema,
- ein source-bound Target-Entry-Point,
- ein separater Release- und Single-Use-Grant-Pfad,
- atomarer Grant-Verbrauch mit Replay- und Crash-Schutz.

**Nicht getan:** kein Newton-Lauf, kein Shooting-Root, kein `solve_ivp`-Targetlauf, kein Resultat, kein Kandidat, kein Rank-Test, keine physische Freigabe.

## 2. Unveränderter Target-Payload

Kanonischer Run:

`HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1`

Kanonischer Payload-SHA-256:

`0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302`

Targetkopplung:

`a_F = 1/4`

Der historische `a_F=0`-Kontrollzweig ist im WP2-Targetpfad **verboten**. Der Target-Entry-Point konstruiert beide Modellobjekte ausschließlich mit `control_a_F=False`. Es gibt keinen manufactured/control fallback und keine Parametermutation.

## 3. 7-Seed/35-Entry-Schedule

Seed-Set:

`M1-BG3B-CP01-SEEDS-01`

Feste Multiplikatoren:

`[0, 1/8, -1/8, 1/4, -1/4, 1/2, -1/2]`

Feste Lobatto-Knoten:

`[24, 32, 48, 64, 96]`

Transaktionsordnung:

`seed-major -> node-count`

Damit:

`7 x 5 = 35` geplante Primary-Einträge.

Für einen Seed wird nur ein akzeptierter niedrigerer Mesh-Kandidat als Initialguess zum nächsten preregistrierten Mesh prolongiert. Es werden keine Zwischenmeshes eingefügt.

Der Independent-Backend wird gemäß eingefrorener Resource Policy **nur nach einem Primary-Numerical-Candidate** aufgerufen. Das erzeugt keine zusätzliche Parameter-/Seed-/Mesh-Schedule.

## 4. Backend-Bindings

WP2 unterscheidet strikt zwischen **Raw-File-SHA-256** und den historischen, in 3C10 dokumentierten **normalisierten Implementation-Digests**. Für die operative Source-Bindung gilt der Raw-File-Digest zusammen mit dem Git-Blob.

### Primary Adapter

Pfad:

`tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py`

Raw-File-SHA-256:

`8ce1c0eceed64245d091d4bed492f3cf2a9c8314f631a03045aaa9696fb11c92`

Historischer 3C10 Implementation-Digest:

`13b289fbde886240d993e90d4906776e7f33926dd19a37e24402172045162f26`

Git blob:

`e232537ab80f099b0b3a914c509041c13825e950`

### Primary Base

Pfad:

`tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py`

Raw-File-SHA-256:

`830d4b4fdd28c8888876125479df3542eeb3864d4328764feb96b5d34bd91599`

Historischer 3C10 Implementation-Digest:

`114d00ba10ba1df2f061f022254f5fd1a29b206e1ecf3413eeb062281dc43745`

Git blob:

`d451be299d0ca93a7dc4587782675b7adab5cfd7`

### Independent Backend

Pfad:

`tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py`

Raw-File-SHA-256:

`a8afd7b548366acf9f5ac72e91bcf07372913cc21a8790d86d0a989a89f03e7b`

Historischer 3C10 Implementation-Digest:

`d271a6b9f4783060832b20655700c415098012afa9880fc0b046a94ecbcef217`

Git blob:

`bed68e11a3682d8b140b6db0cbe71fd696c3ff34`

## 5. Dependency-, Resource- und Result-Binding

### Dependency Lock

`requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3B_v0.1.txt`

SHA-256:

`4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f`

Ein zukünftiges `execute` verlangt Python `3.12.x`, `PYTHONHASHSEED=0` beim Prozessstart und exakt die gelockten Paketversionen.

### Resource Policy

Gebunden an:

`registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json`

Insbesondere:

- Gesamt-Wallclock maximal `21600 s`,
- pro Seed/Mesh-Level maximal `1800 s`,
- Prozessspeicher maximal `8589934592 B = 8 GiB`,
- exakt `1` CPU-Thread,
- Resultatbudget maximal `1073741824 B = 1 GiB`,
- Netzwerk aus,
- GPU aus,
- Randomness aus,
- keine parallele Seed-Ausführung,
- keine adaptive Ressourcenanhebung.

### Result Schema

Gebunden an:

`registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json`

WP2 erzeugt heute **kein Resultat**. Ein später autorisierter Lauf schreibt zuerst in ein **externes, nicht im Repository liegendes** Transaktionsverzeichnis. Raw-Ausgaben bleiben quarantänisiert, bis die gebundene Result-Schema-/QA-Schicht sie klassifiziert. Raw-Output ist keine physische Evidenz.

## 6. Source-bound Target-Entry-Point

Neu:

`tools/2026-08-10_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.0.py`

Eigenschaften:

- Auditpfad importiert keine numerischen Backends.
- Keine direkte Solve-CLI.
- Schedule wird aus den eingefrorenen Quellen rekonstruiert und gehasht.
- Backend-Raw-File-SHA-256 werden vor jeder späteren Ausführung erneut geprüft.
- `a_F=1/4` wird vor und nach der Backend-Modellkonstruktion geprüft.
- Numerical imports erfolgen erst nach validierter `TargetExecutionCapability`.
- kein `a_F=0`-Override,
- kein manufactured fallback,
- kein Random-Restart,
- keine adaptive Mesh-Insertion,
- keine stille Parameteränderung.

## 7. Single-Use-Grant

WP2 erzeugt **weder Release noch Grant**.

Zukünftige append-only Pfade:

- Release: `registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.0.json`
- Grant: `registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.0.json`

Der Release muss die exakten Grant-Bytes per SHA-256 pinnen. Release und Grant müssen außerdem Run-ID, Payload-SHA-256, WP2-Contract-SHA-256 und Source-Bundle-SHA-256 pinnen.

Der Grant bindet zusätzlich:

- Schedule-SHA-256,
- `planned_entry_count=35`,
- Dependency-Lock-SHA-256,
- Resource-Policy-Git-Blob,
- Result-Schema-Git-Blob,
- `single_use=true`,
- `no_retry=true`,
- `no_scan=true`,
- `no_fallback=true`,
- Nonce mit 128 bis 256 Bit,
- `issued_at`, `not_before`, `expires_at`,
- maximal 3600 s Start-Gültigkeitsfenster.

Das Zeitfenster autorisiert nur den **Start**. Nach atomarem Verbrauch läuft die Transaktion unter der eingefrorenen Resource Policy weiter.

## 8. Replay- und Crash-Schutz

Für jeden Grant wird außerhalb des Repositories ein Nonce-Verzeichnis verwendet.

Vor Backendimport/Targetsolve wird `spent.json` per exklusivem `O_CREAT|O_EXCL` erzeugt und `fsync`-gesichert.

Zustandsautomat:

`CLAIMED -> RUNNING -> SUCCEEDED | FAILED`

Findet ein späterer Prozess einen bereits verbrauchten Grant mit unvollständigem `CLAIMED`/`RUNNING`-Zustand, wird er zu

`CRASHED_OR_INDETERMINATE`

klassifiziert.

In allen Fällen gilt:

`spent -> derselbe Grant darf nie erneut laufen`.

Nach Fehler oder Crash ist ein **neuer Grant** erforderlich. Es gibt keine automatische Resume-/Retry-Semantik.

## 9. Statushygiene

### bewiesen / formal geschlossen

- WP2-Targetpfad ist source-bound.
- CP01R1-Run-ID und Payload-Digest sind fest verdrahtet und auditierbar.
- der 7x5-Plan enthält exakt 35 Primary-Einträge.
- Backend-, Dependency-, Resource- und Result-Quellen sind content-addressed gebunden.
- Grant-Verbrauch ist als Single-Use-Transaktion mit permanentem Replay-Block implementiert.
- Crash-/Indeterminate-Semantik erzwingt einen neuen Grant.
- CI-/Auditpfad besitzt keinen Solve-Aufruf.

### numerisch bestätigt

Noch nichts am physischen CP01R1-Target. **Kein physischer Solve wurde ausgeführt.**

### konditional

- Die spätere physische Ausführung ist nur bei separatem Release + gültigem Single-Use-Grant + exakter Runtime/Resource-Attestation zulässig.
- Numerische Konvergenz wäre anschließend nur ein numerisches Kandidatensignal unter dem preregistrierten QA-Protokoll.

### offen

- Existenz/Eindeutigkeit des M1-Hintergrunds,
- Kontinuums-Jacobianrang,
- Fredholm-Eigenschaft,
- vollständige Kandidaten-QA,
- Stabilität/Ghostfreiheit,
- physische Identifikation.

### blockiert

- physischer Solve in WP2-Build/CI,
- physischer Background-Release,
- R1.1/R1.2 downstream,
- K1-D,
- K1-E.

## 10. Nächster zulässiger Schritt

Nach grüner WP2-CI und Merge ist als **separater Akt** nur zulässig:

1. Release-Review gegen den gemergten, unveränderten WP2-Source-Bundle-Stand,
2. danach einmaliger zeitgebundener Grant,
3. erst danach optionaler physischer Solve.

Dieser Ledger autorisiert Punkt 3 ausdrücklich **nicht**.
