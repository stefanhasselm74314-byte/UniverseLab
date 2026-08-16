# UniverseLab Platform Governance & Reproducibility Layer v1.0

Status: `IMPLEMENTATION_BASELINE`

Physical gate effect: `NONE`

## Purpose

This layer prevents UI state, technical execution state, governance release state and scientific interpretation from collapsing into one status label.

## Mandatory status axes

1. **Technical** — code, schema, test, execution, checksum, backend and reproducibility state.
2. **Governance** — authorization, release gate, K1-D/K1-E and evidence-admissibility state.
3. **Scientific** — established, numerically confirmed, conditional, heuristic, open, blocked or falsified scope.

No axis may automatically promote another.

`technical PASS != physical identification`

`numerical stability != ghost freedom`

`good fit != theory confirmation`

`parameter adjustment != derivation from the 6D parent sector`

## Canonical navigation

`navigator.html` is the canonical scientific navigator.

`navigator-app.html` is retained only as a compatibility redirect and must not contain an iframe or mutate the canonical navigator DOM.

## Global shell

The global shell owns:

- primary navigation,
- active-page state,
- breadcrumbs,
- global K1-D/K1-E/evidence badges,
- archive warnings where a page is explicitly classified as historical reference.

Individual pages own their scientific content but do not own global release truth.

## Site State

The machine-readable site-state snapshot is:

`registry/2026-08-16_UniverseLab_SiteState_v1.0.json`

Schema:

`schemas/2026-08-16_UniverseLab_SiteStateSchema_v1.0.json`

The snapshot is an integration layer over canonical registries; it has no independent physical authority and cannot release K1-D or K1-E.

## ULSH-01 pilot

ULSH-01 / MD2S-BVP is the first integration target because all physical downstream chains depend directly or indirectly on a released MD2S background.

Current status encoded by the site-state snapshot:

- development priority: `ACTIVE_CRITICAL_PATH`
- solver release: `NOT_AUTHORIZED`
- physical background: `NOT_ESTABLISHED`
- K1-D: `NOT_RELEASED`
- K1-E: `NOT_ADMISSIBLE`
- physical evidence effect: `NONE`
- release gate: `NOT_SATISFIED`

Work-package completion is not solver release.

## Rollout order

P0. Remove navigator iframe wrapper.

P1. Introduce canonical global shell and page identity.

P2. Introduce archive/current classification.

P3. Separate technical, governance and scientific status representations.

P4. Introduce site-state schema/registry and CI invariants.

P5. Bind ULSH-01 status card to site-state data.

P6+. Extend the shell and state contract to remaining canonical pages and solvers only after the pilot is stable.
