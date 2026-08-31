#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CURRENT_NAV_PAGES = [
    "compare-desktop.html",
    "hyperzeit-material-v2.html",
    "hyperzeit-methods.html",
    "md2s-artifact-recovery-rank-audit-v0.1.html",
    "sci-001-002-md2s-substitution-v0.2.html",
    "sci-001-002-parent-closure-v0.1.html",
    "source.html",
]

CURRENT_SHELL_PAGES = [
    "2026-08-19_UniverseLab_BibliographyCatalog_v1.0.html",
    "2026-08-20_UniverseLab_MachineDataViewer_v1.1.html",
    "2026-08-27_UniverseLab_DocumentViewer_v1.0.html",
    "2026-08-27_UniverseLab_SourceTextViewer_v1.0.html",
    "hyperlab.html",
    "hyperzeit-material-v2.html",
    "hyperzeit-methods.html",
    "navigator.html",
    "solver-hub.html",
    "source.html",
]

EXPECTED_HISTORICAL_NAV = {
    "2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.html",
    "2026-08-10_ULSH_MasterBuildOrder_v1.0.html",
    "2026-08-10_ULSH_SolverDevelopmentProgram_v1.1.html",
    "hyperzeit-material.html",
    "source-baryogenesis.html",
    "universelab-audit-2026-07-31.html",
}

EXPECTED_SUPERSEDED_SHELL = {
    "2026-08-19_UniverseLab_MachineDataViewer_v1.0.html",
}

SHELL_CSS = "./assets/2026-08-16_UniverseLab_GlobalShell_v1.1.css"
SHELL_JS = "./assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js"
STAMP = "20260831-phase2"

changed = []

for rel in CURRENT_NAV_PAGES:
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"missing current nav page: {rel}")
    s = p.read_text(encoding="utf-8")
    if "navigator-app.html" not in s:
        continue
    s2 = s.replace("navigator-app.html", "navigator.html")
    p.write_text(s2, encoding="utf-8")
    changed.append(rel)

for rel in CURRENT_SHELL_PAGES:
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"missing current shell page: {rel}")
    s = p.read_text(encoding="utf-8")
    s2 = s
    if SHELL_CSS in s2 and SHELL_CSS + "?" not in s2:
        s2 = s2.replace(SHELL_CSS, SHELL_CSS + "?v=" + STAMP)
    if SHELL_JS in s2 and SHELL_JS + "?" not in s2:
        s2 = s2.replace(SHELL_JS, SHELL_JS + "?v=" + STAMP)
    if s2 != s:
        p.write_text(s2, encoding="utf-8")
        changed.append(rel)

# Verification firewall: current pages may no longer carry the old route or unversioned shell.
for rel in CURRENT_NAV_PAGES:
    s = (ROOT / rel).read_text(encoding="utf-8")
    if "navigator-app.html" in s:
        raise SystemExit(f"legacy navigator route survived on current page: {rel}")

for rel in CURRENT_SHELL_PAGES:
    s = (ROOT / rel).read_text(encoding="utf-8")
    if SHELL_CSS in s or SHELL_JS in s:
        raise SystemExit(f"unversioned GlobalShell survived on current page: {rel}")

# Historical pages are intentionally immutable in this migration.
for rel in sorted(EXPECTED_HISTORICAL_NAV):
    p = ROOT / rel
    if p.exists() and "navigator-app.html" not in p.read_text(encoding="utf-8"):
        raise SystemExit(f"historical navigator provenance unexpectedly changed: {rel}")
for rel in sorted(EXPECTED_SUPERSEDED_SHELL):
    p = ROOT / rel
    if p.exists():
        s = p.read_text(encoding="utf-8")
        if SHELL_CSS not in s and SHELL_JS not in s:
            raise SystemExit(f"superseded shell provenance unexpectedly changed: {rel}")

print("phase2_changed_files=", len(set(changed)))
for rel in sorted(set(changed)):
    print(rel)
