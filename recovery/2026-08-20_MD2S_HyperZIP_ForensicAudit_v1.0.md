# MD2S Hyper.zip Forensic Audit v1.0

**Date:** 2026-08-20  
**Status:** `FORENSIC_ARCHIVE_AUDIT_ONLY`  
**Physical evidence effect:** `NONE`  
**Physical gate effect:** `NONE`

## 1. Scope

This record binds a previously completed full-text archive analysis of `Hyper.zip` to the MD2S-R1-L forensic recovery chain.

The inspected archive-level report states that `Hyper.zip` contained 40 PDF files and 1,279 pages, including three long ChatGPT PDF exports totaling 1,191 pages. The report records full text extraction of all pages and visual checks of the compact PDFs plus representative pages of the long chat exports.

This repository record does **not** embed the archive, does not independently recompute its contents in CI, and does not promote chat-reported numbers to solver outputs.

## 2. High-value MD2S finding

The archive analysis identifies the MD-2S chain as the strongest dynamics work present in that archive and reports development through `MD-2S-B1.4N`.

The archive-level terminal state is recorded as:

- unrestricted linear system: algebraically solvable;
- required rescue: conical center mode;
- fixed smooth center plus minimal cap controls: no global solution;
- consequence: an additional independent geometric control is required.

`MD-2S-B1.4O` appears only as the next planned audit at the end of the 312-page project-status chat; no B1.4O result is present in the inspected archive.

## 3. What the archive does contain

The report preserves the A0 benchmark block as reported values:

- `sqrt(K4) * rho_cap = 1.1196329253611`
- `kappa6^2 * lambda_eff / (4 * sqrt(K4)) = 0.8931498683204`
- `K4 * rho_cap^2 = 1.2535778875527`
- `V_W = 0.5318111250097`
- for `K4 = beta = 1`: `R_circle = 0.6661500466003`

These remain reported benchmark/provenance material, not rerunnable solver transactions.

## 4. What the archive does not contain

The archive analysis states that `Hyper.zip` contains PDFs only. It specifically records absence from that archive of the repeatedly referenced:

- Python scripts;
- CSV files;
- JSON status files;
- solver inputs and solver outputs;
- residual logs;
- DOT graphs;
- SHA-256 manifests;
- DOCX/LaTeX sources;
- referenced subpackages and ZIP packages.

It further notes that the MD-2S chat repeatedly refers to a `Gesamtpaket`, a reproduction script and a SHA-256 manifest, but those artifacts are not present in `Hyper.zip`.

Therefore this archive cannot independently reproduce the numerical MD2S claims contained in its chat PDFs.

## 5. Consequence for MD2S-R1-L recovery

This is a stronger archive-scoped negative result than a keyword search alone:

`HYPER_ZIP_PRIMARY_SOLVER_TRANSACTION_RECOVERY = NEGATIVE`

`HYPER_ZIP_B1_4O_RESULT_RECOVERY = NEGATIVE`

`HYPER_ZIP_REPRODUCIBLE_MD2S_NUMERICS = NEGATIVE`

However, the scope is strictly bounded:

> absence from `Hyper.zip` is not proof that the historical artifacts never existed elsewhere.

The historical one-sided interface values and their run-bound solver/residual provenance therefore remain unrecovered.

## 6. Evidence classification

This audit introduces one archive-level evidence class:

`E7_ARCHIVE_LEVEL_FORENSIC_AUDIT`

Meaning: a surviving archive was systematically inventoried/full-text analyzed and can support claims about what that specific archive contains or lacks, but cannot by itself establish global nonexistence outside the archive.

The existing classes remain unchanged:

- A0 benchmark block: `E1_VERIFIED_REPORTED_ARTIFACT`
- B1.4K/B1.4L numerical reports: `E4_UNVERIFIED_HISTORICAL_CHAT_REPORT`
- missing historical two-sided interface export: `E5_MISSING_SURVIVING_ARCHIVE`
- later rebuild/C1 data: `E6_REBUILD_OR_C1_DATA_NOT_HISTORICAL`

## 7. Remaining recovery target

The next forensic target is no longer another pass over the 40-PDF `Hyper.zip` corpus. The remaining high-value targets are external to that archive:

1. the referenced MD-2S `Gesamtpaket`;
2. the referenced reproduction script;
3. the referenced SHA-256 manifest;
4. any solver input/output package carrying run identity and residual/convergence data;
5. any export containing the one-sided Bulk/Cap boundary values bound to the historical run.

Until such primary artifacts are recovered, no historical MD2S numerical value is promoted to `VERIFIED_SOLVER_OUTPUT`.

## 8. Governance invariants

Unchanged:

- `official_MD2S_solver = NOT_AUTHORIZED`
- `PHYSICAL_BACKGROUND = NOT_ESTABLISHED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`
- `physical_gate_effect = NONE`
