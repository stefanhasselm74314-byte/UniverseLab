# UniverseLab — Site Print & Export Audit v1.0

**Date:** 2026-08-19  
**Classification:** PRESENTATION_NAVIGATION_UTILITY_ONLY  
**Scientific evidence effect:** NONE  
**Solver release effect:** NONE  
**Governance status effect:** NONE

## Objective

Provide a consistent print/export control for UniverseLab pages and subpages without rewriting scientific content, solver state, formulas, data, or evidence labels.

## Components

- `assets/2026-08-19_UniverseLab_SitePrintExport_v1.0.js` — floating page utility.
- `assets/2026-08-19_UniverseLab_SitePrintExportBootstrap_v1.0.js` — loads the utility and registers the root-scope service worker.
- `2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js` — injects the shared utility into subsequent HTML navigation responses under `/UniverseLab/`.
- `2026-08-11_UniverseLab_OwnerPrintExport_v1.0.html?owner=1` — existing multi-page selection / A4 / PDF / HTML export hub, reused rather than duplicated.

## User functions

The floating control exposes:

1. current-page browser print / Save as PDF,
2. current-page HTML DOM snapshot,
3. direct-link copy,
4. multi-page UniverseLab export via the existing Owner Print Export hub.

The control is hidden during `include-iframe=1` export rendering and by `@media print`.

## Coverage model

The bootstrap is loaded directly by governed entry points and is chained from the existing site language compatibility loader. Once the service worker is registered, its scope is `/UniverseLab/` and subsequent HTML navigations under that scope receive the shared print/export script even if the underlying legacy HTML file has not yet been rewritten.

### First-load boundary

A service worker cannot control the very first direct navigation that installs it. Therefore a first-ever direct deep link to a legacy HTML page that does not itself load the bootstrap may lack the floating control on that single first response. After registration from a governed entry point (for example the UniverseLab start page or Link Hub), subsequent navigations/reloads within `/UniverseLab/` are covered.

This boundary is a browser service-worker lifecycle constraint, not a scientific or repository-state issue.

## Safety constraints

- No response is cached by the print/export service worker.
- Only same-origin `GET` navigation responses with `text/html` content under `/UniverseLab/` are rewritten.
- `include-iframe=1` responses are passed through unchanged.
- JSON, CSV, JavaScript, CSS, images, APIs, solver outputs and other non-HTML resources are never rewritten.
- Existing page content is not transformed; only one external utility script is inserted before `</body>` when needed.
- Response entity headers invalidated by textual injection (`content-length`, `content-encoding`, `etag`, `last-modified`) are removed from the reconstructed HTML response.

## Existing export reuse

The pre-existing Owner Print Export already performs recursive local-page discovery, selectable page bundling and browser A4/PDF export. The site-wide utility links to that established mechanism instead of creating a second competing multi-page export implementation.

## Status

Implementation is a UI/navigation facility only. A successful print, PDF, snapshot, or exported bundle does not establish physical validity, numerical convergence, solver release, rank conditions, or theory confirmation.
