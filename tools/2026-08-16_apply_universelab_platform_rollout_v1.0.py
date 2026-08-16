#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = "./assets/2026-08-16_UniverseLab_GlobalShell_v1.1.css"
JS = "./assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js"
CSS_TAG = f'<link rel="stylesheet" href="{CSS}">'
JS_TAG = f'<script src="{JS}"></script>'
SITE_STATE = "registry/2026-08-16_UniverseLab_SiteState_v1.0.json"
SITE_SCHEMA = "schemas/2026-08-16_UniverseLab_SiteStateSchema_v1.0.json"
GOVERNANCE_DOC = "governance/2026-08-16_UniverseLab_PlatformGovernance_v1.1.md"

PAGES = {
    "navigator.html": ("UL-PAGE-NAVIGATOR", "navigator"),
    "hyperlab.html": ("UL-PAGE-HYPERLAB", "hyperlab"),
    "solver-hub.html": ("UL-PAGE-SOLVER-HUB", "solver"),
    "hyperzeit-material-v2.html": ("UL-PAGE-MATERIAL", "material"),
    "hyperzeit-methods.html": ("UL-PAGE-METHODS", "methods"),
    "universelab-audit-2026-07-31.html": ("UL-PAGE-AUDIT-20260731", "audit"),
    "source.html": ("UL-PAGE-SOURCE", "source"),
}


def inject_shell(text: str, page_id: str, domain: str) -> str:
    text = text.replace(
        "./assets/2026-08-16_UniverseLab_GlobalShell_v1.0.css", CSS
    ).replace(
        "./assets/2026-08-16_UniverseLab_GlobalShell_v1.0.js", JS
    )

    if CSS_TAG not in text:
        if "</head>" not in text.lower():
            raise ValueError("HTML has no </head>")
        text = re.sub(r"</head>", CSS_TAG + "\n</head>", text, count=1, flags=re.I)

    if JS_TAG not in text:
        if "</body>" not in text.lower():
            raise ValueError("HTML has no </body>")
        text = re.sub(r"</body>", JS_TAG + "\n</body>", text, count=1, flags=re.I)

    body = re.search(r"<body\b([^>]*)>", text, flags=re.I)
    if not body:
        raise ValueError("HTML has no <body>")
    attrs = body.group(1)
    if "data-ul-page-id=" not in attrs:
        attrs += f' data-ul-page-id="{page_id}"'
    if "data-ul-domain=" not in attrs:
        attrs += f' data-ul-domain="{domain}"'
    text = text[: body.start()] + f"<body{attrs}>" + text[body.end() :]
    return text


def update_manifest(text: str) -> str:
    manifest = json.loads(text)
    pages = manifest.setdefault("canonical_pages", [])

    nav = next((p for p in pages if p.get("id") == "navigator"), None)
    if nav is None:
        nav = {"id": "navigator"}
        pages.insert(0, nav)
    nav.update(
        {
            "path": "navigator.html",
            "live": "./navigator.html",
            "class": "scientific_navigation",
            "status": "ACTIVE",
        }
    )

    legacy = next((p for p in pages if p.get("id") == "navigator_legacy_redirect"), None)
    if legacy is None:
        legacy = {
            "id": "navigator_legacy_redirect",
            "path": "navigator-app.html",
            "live": "./navigator-app.html",
            "class": "compatibility_redirect",
            "status": "LEGACY_REDIRECT",
            "redirect_target": "./navigator.html",
        }
        nav_index = pages.index(nav)
        pages.insert(nav_index + 1, legacy)
    else:
        legacy.update(
            {
                "path": "navigator-app.html",
                "live": "./navigator-app.html",
                "class": "compatibility_redirect",
                "status": "LEGACY_REDIRECT",
                "redirect_target": "./navigator.html",
            }
        )

    solver = next((p for p in pages if p.get("id") == "solver_hub"), None)
    if solver is None:
        solver = {
            "id": "solver_hub",
            "path": "solver-hub.html",
            "live": "./solver-hub.html?v=1",
            "class": "numerical_research_infrastructure",
            "status": "ACTIVE_DIAGNOSTIC",
        }
        insert_at = next(
            (i + 1 for i, p in enumerate(pages) if p.get("id") == "hyperlab"),
            len(pages),
        )
        pages.insert(insert_at, solver)
    else:
        solver.update(
            {
                "path": "solver-hub.html",
                "live": "./solver-hub.html?v=1",
                "class": "numerical_research_infrastructure",
                "status": "ACTIVE_DIAGNOSTIC",
            }
        )

    registries = manifest.setdefault("central_registries", {})
    registries["site_state"] = SITE_STATE
    registries["site_state_schema"] = SITE_SCHEMA
    registries["platform_governance"] = GOVERNANCE_DOC

    manifest["platform_governance"] = {
        "version": "1.1.0",
        "date": "2026-08-16",
        "status": "GLOBAL_SHELL_ROLLED_OUT_TO_CANONICAL_PAGES",
        "canonical_navigator": "navigator.html",
        "legacy_navigator_redirect": "navigator-app.html",
        "global_shell_css": CSS.removeprefix("./"),
        "global_shell_js": JS.removeprefix("./"),
        "site_state": SITE_STATE,
        "site_state_schema": SITE_SCHEMA,
        "rollout_pages": list(PAGES),
        "status_axes_rule": "TECHNICAL_GOVERNANCE_SCIENTIFIC_ARE_INDEPENDENT",
        "physical_gate_effect": "NONE",
    }

    return json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed: list[str] = []

    for rel, (page_id, domain) in PAGES.items():
        path = ROOT / rel
        before = path.read_text(encoding="utf-8")
        after = inject_shell(before, page_id, domain)
        if after != before:
            changed.append(rel)
            if not args.check:
                path.write_text(after, encoding="utf-8")

    manifest_path = ROOT / "project-manifest.json"
    before = manifest_path.read_text(encoding="utf-8")
    after = update_manifest(before)
    if after != before:
        changed.append("project-manifest.json")
        if not args.check:
            manifest_path.write_text(after, encoding="utf-8")

    if args.check and changed:
        print("Platform rollout drift detected:")
        for item in changed:
            print(f" - {item}")
        return 1

    if changed:
        print("Updated:")
        for item in changed:
            print(f" - {item}")
    else:
        print("Platform rollout already synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
