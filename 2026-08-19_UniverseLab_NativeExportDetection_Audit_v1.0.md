# UniverseLab — Native Export Detection Audit v1.0

**Date:** 2026-08-19  
**Classification:** PRESENTATION_NAVIGATION_UTILITY_ONLY  
**Scientific status effect:** NONE

## Problem

The site-wide `Druck / Export` utility can duplicate page-local export interfaces on pages that already ship a specialized native export system. The Tafelwerk is a confirmed example: it exposes its own export UI and declares `data-ul-export-title` on `<body>` while loading the native UniverseLab export scripts.

## Resolution

The global site-wide print/export utility now performs native-export detection before rendering its floating control.

The global control is suppressed when any of the following explicit signals is present:

- `[data-ul-native-export]`
- `body[data-ul-export-title]`
- a script source containing `UniverseLab_Export_`
- an existing `.ul-export-trigger` or `[data-ul-export-trigger]` element

An explicit page override `data-ul-force-global-export="1"` on `<body>` can re-enable the global control if a future page intentionally wants both interfaces.

## Effect

- Pages without native export keep the site-wide `Druck / Export` control.
- Pages with specialized export, including the Tafelwerk, keep only their native export UI.
- The central Owner multi-page export remains available from pages that use the global utility and can still be opened directly.
- No solver, gate, evidence, registry or physics state is changed.
