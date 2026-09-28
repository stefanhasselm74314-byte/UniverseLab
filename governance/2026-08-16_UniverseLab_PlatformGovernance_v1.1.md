# UniverseLab Platform Governance & Reproducibility Layer v1.1

Status: `P6_GLOBAL_SHELL_ROLLOUT`

Physical gate effect: `NONE`

## Scope

This revision extends the v1.0 platform baseline from the canonical Navigator and ULSH-01 pilot to the remaining canonical public research pages without changing any physical release decision.

## P6 deliverables

1. Synchronize `project-manifest.json` with the canonical direct Navigator architecture.
2. Register `navigator-app.html` only as a legacy compatibility redirect.
3. Register `solver-hub.html` as canonical numerical research infrastructure.
4. Roll Global Shell v1.1 out to:
   - `navigator.html`
   - `hyperlab.html`
   - `solver-hub.html`
   - `hyperzeit-material-v2.html`
   - `hyperzeit-methods.html`
   - `universelab-audit-2026-07-31.html`
   - `source.html`
5. Preserve page-local navigation while removing duplicate global destinations at runtime.
6. Keep the 2026-07-31 Master Audit visibly classified as `ARCHIVED_REFERENCE`.
7. Add CI drift checks for the manifest, shell rollout, Site State linkage, and physical-status invariants.

## Navigation contract

Primary navigation is owned by the Global Shell.

Page-local navigation may remain, but links duplicating the canonical global destinations are demoted/removed from the local navigation layer at runtime.

The global destinations are:

- Navigator
- HyperLab
- Solver
- Material 2.0
- Methoden & QA
- Quellcode
- Portal

## Manifest contract

`project-manifest.json` must expose:

- `navigator.html` as the canonical scientific navigator,
- `navigator-app.html` as `LEGACY_REDIRECT`,
- `solver-hub.html` as `ACTIVE_DIAGNOSTIC`,
- Site State and Site State Schema in `central_registries`,
- an explicit `platform_governance` block with `physical_gate_effect = NONE`.

The manifest synchronization changes only platform metadata. Scientific release, solver authorization, K1-D, K1-E and physical evidence states are not promoted by this rollout.

## Status firewall

The mandatory rules remain:

`technical execution != physical identification`

`numerical stability != ghost freedom`

`good fit != theory confirmation`

`work-package completion != solver release`

The Site State remains an integration snapshot and has no independent physical authority.

## Release criteria for P6

P6 is complete only if:

- all seven canonical pages load Global Shell v1.1,
- the rollout migrator reports no drift in `--check` mode,
- manifest navigation entries match the direct Navigator architecture,
- the archived audit remains explicitly archived,
- ULSH-01 remains `NOT_AUTHORIZED`,
- physical background remains `NOT_ESTABLISHED`,
- K1-D remains `NOT_RELEASED`,
- K1-E remains `NOT_ADMISSIBLE`,
- physical evidence effect remains `NONE`.
