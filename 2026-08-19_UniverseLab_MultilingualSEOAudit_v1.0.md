# UniverseLab — Multilingual / SEO Audit v1.0

**Date:** 2026-08-19  
**Classification:** PRESENTATION_NAVIGATION_SEO_ONLY  
**Scientific evidence effect:** NONE  
**Solver release effect:** NONE  
**Gate effect:** NONE

## Scope

Audit of the current German/English UniverseLab presentation layer against the repository state on `main`. The audit covers curated route pairing, language-switcher routing, site-wide delivery, sitemap `hreflang`, x-default behavior and known first-load limitations. It does not change formulas, numerical implementations, physical claims, K1-D, K1-E, solver authorization or evidence status.

## Findings and corrections

### SEO-LANG-001 — Observatory and Validation missing from curated router

`observatory-en.html` and `validation-en.html` existed, but the central language-switcher route matrix did not register the German/English pairs. Selecting English from those German routes could therefore fall back to automatic translation rather than the curated English entry.

**Severity:** HIGH  
**Status after patch:** FIXED

### SEO-LANG-002 — Comparison calculator route mismatch

The public/sitemap German comparison route is `compare-safe.html`, while the language matrix and `compare-en.html` declared `compare-desktop.html` as the German alternate. This created an inconsistent canonical route model.

**Severity:** HIGH  
**Status after patch:** FIXED

Canonical pair after correction:

`compare-safe.html` ↔ `compare-en.html`

`compare-desktop.html` remains a German presentation alias that maps to the same curated English entry.

### SEO-LANG-003 — Incomplete sitemap hreflang reciprocity

The sitemap listed curated DE/EN URLs but only the portal entry carried language alternates. Search engines therefore lacked a complete machine-readable pairing for the remaining curated pages.

**Severity:** HIGH  
**Status after patch:** FIXED

The sitemap now includes reciprocal `de`, `en` and `x-default` alternates for every curated pair.

### SEO-LANG-004 — Language control depended too strongly on per-page HTML

Several canonical German research pages do not directly embed the language-switcher script. The existing root-scope presentation service worker already provides site-wide HTML navigation injection for print/export; the language layer did not use that coverage.

**Severity:** HIGH  
**Status after patch:** FIXED WITH BROWSER-LIFECYCLE LIMITATION

The governed bootstrap now loads the language switcher directly. The existing root-scope service worker now injects both the language switcher and the existing print/export utility into subsequent same-origin HTML navigations when absent. The current machine-data-viewer-aware print/export path is preserved.

### SEO-LANG-005 — First-ever legacy deep-link limitation

A service worker cannot retroactively control the HTML response that first installs it. A first-ever direct navigation to an old page that loads neither bootstrap nor language script can therefore still render once without the language control.

**Severity:** MEDIUM  
**Status:** KNOWN PLATFORM LIMITATION

Full elimination requires either rewriting every legacy HTML entry point or moving to a build/template system that emits the language bootstrap into every page.

## Curated route inventory

13 curated German/English pairs are registered:

1. Portal
2. Scientific Navigator
3. Research Status
4. Solver Hub
5. Methods & QA
6. Material Atlas 2.0
7. SCI-001/SCI-002 Parent & Junction
8. HyperLab
9. Observatory
10. Validation Console
11. Guide
12. Mathematical Reference / Tafelwerk
13. Comparison Calculator

Machine-readable source: `2026-08-19_UniverseLab_MultilingualRouteRegistry_v1.0.json`.

## Unpaired German routes

The following sitemap routes remain German-only and therefore use automatic translation when reached through the language layer:

- `about.html`
- `journey.html`
- `emergence.html`
- `universe3d.html`

This is a content-coverage gap, not an SEO error, provided they are not represented as curated English pages.

## Canonical language policy

- **German (`de`)**: canonical research wording.
- **English (`en`)**: curated scientific translation where explicitly registered.
- **Other languages**: automatic reading translation from the German source.
- **x-default**: German canonical route.

If wording diverges between German and English, the German research source controls scientific interpretation until the translation is re-reviewed.

## Scientific firewall

The multilingual layer must never alter:

- formulas,
- numerical code,
- parameter defaults,
- solver outputs,
- gate values,
- branch status,
- evidence classifications,
- K1-D / K1-E decisions.

A translation or successful page render is a presentation event only.

## Remaining recommended work

### P1 — Native HTML metadata normalization

Add explicit absolute `canonical`, reciprocal `hreflang` and `x-default` elements to both members of every curated pair, not only to the sitemap. This should be generated from the route registry to prevent drift.

### P2 — Build-time validation

Add CI checks that fail when:

- a registered DE or EN route does not exist,
- a pair is not reciprocal,
- sitemap and route registry disagree,
- an English curated page points to a different German canonical route,
- duplicate language codes exist for one URL,
- x-default does not resolve to the declared canonical source.

### P3 — Remove hand-maintained duplication

The route map currently exists in both JavaScript and the machine-readable registry. Migrate the router to a generated artifact from the registry during a build step. Runtime-fetching the registry is possible, but build-time generation is more robust for first paint and static hosting.

### P4 — Finish curated English coverage

Decide whether `about`, `journey`, `emergence` and `universe3d` require curated English versions. Until then, leave them explicitly in automatic-translation fallback status.

## Current verdict

**Curated-route correctness:** PASS AFTER PATCH  
**Sitemap reciprocal hreflang:** PASS AFTER PATCH  
**Site-wide subsequent-navigation coverage:** PASS AFTER PATCH  
**First-ever arbitrary legacy deep-link coverage:** PARTIAL / PLATFORM-LIMITED  
**All-page native canonical/hreflang metadata:** PARTIAL  
**CI enforcement:** OPEN  
**Scientific status effect:** NONE
