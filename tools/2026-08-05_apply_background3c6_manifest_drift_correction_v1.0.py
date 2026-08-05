#!/usr/bin/env python3
"""Correct exact stale nested manifest values after Background-3C6 canonicalization."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
OLD_NEXT_BLOCK = "C-PHYS-R1.0-BACKGROUND-3C6_INTEGRATED_EXECUTION_RELEASE_IMPLEMENTATION_ONLY"
NEW_NEXT_BLOCK = "C-PHYS-R1.0-BACKGROUND-3C7_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_ONLY"
OLD_STATUS = "BACKGROUND_3C_AUTHORIZATION_DENIED_EXECUTION_RUNNER_MISSING"
NEW_STATUS = "BACKGROUND_3C6_CONTROL_RELEASE_AUDITED_AUTHORIZATION_REVIEW_REMAINING"


def replace_exact_values(value: Any, path: str = "$") -> tuple[Any, list[str]]:
    changed: list[str] = []
    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            replaced, nested = replace_exact_values(item, f"{path}.{key}")
            output[key] = replaced
            changed.extend(nested)
        return output, changed
    if isinstance(value, list):
        output = []
        for index, item in enumerate(value):
            replaced, nested = replace_exact_values(item, f"{path}[{index}]")
            output.append(replaced)
            changed.extend(nested)
        return output, changed
    if value == OLD_NEXT_BLOCK:
        return NEW_NEXT_BLOCK, [path]
    if value == OLD_STATUS:
        return NEW_STATUS, [path]
    return value, changed


def find_exact_values(value: Any, target: str, path: str = "$") -> list[str]:
    if isinstance(value, dict):
        found: list[str] = []
        for key, item in value.items():
            found.extend(find_exact_values(item, target, f"{path}.{key}"))
        return found
    if isinstance(value, list):
        found = []
        for index, item in enumerate(value):
            found.extend(find_exact_values(item, target, f"{path}[{index}]"))
        return found
    return [path] if value == target else []


def main() -> None:
    original = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest, changed = replace_exact_values(original)
    parent = manifest.setdefault("parent_action_v0_1", {})
    parent["next_block"] = NEW_NEXT_BLOCK
    operator = manifest.setdefault("c_phys_operator_entry", {})
    operator["status"] = NEW_STATUS
    operator["solver_authorized"] = False
    operator["next_block"] = NEW_NEXT_BLOCK
    remaining = {
        OLD_NEXT_BLOCK: find_exact_values(manifest, OLD_NEXT_BLOCK),
        OLD_STATUS: find_exact_values(manifest, OLD_STATUS),
    }
    remaining = {key: paths for key, paths in remaining.items() if paths}
    if remaining:
        raise RuntimeError(f"stale nested Background-3C values remain: {remaining}")
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "changed_paths": changed}, indent=2))


if __name__ == "__main__":
    main()
