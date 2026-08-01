#!/usr/bin/env python3
"""Read-only verifier for an MD-2S recovery run package.

Usage:
    python tools/verify_md2s_recovery_package_v0_1.py /path/to/run
    python tools/verify_md2s_recovery_package_v0_1.py /path/to/run --json-out report.json

The verifier checks package completeness, JSON structure, required boundary
fields, benchmark finiteness, residual declarations, profile columns and
SHA-256 output hashes. It does not solve the field equations and cannot certify
physical correctness, uniqueness, stability or ghost freedom.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA = "universelab.md2s-recovery-package-verification.v0.1"
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
RUN_ID = re.compile(r"^MD2S-RUN-[0-9]{8}-[0-9]{3,}$")

REQUIRED_FILES = (
    "parameters.json",
    "conventions.json",
    "solver-config.json",
    "profiles.csv",
    "boundary-left.json",
    "boundary-right.json",
    "residuals.json",
    "benchmarks.json",
    "environment.json",
    "manifest.json",
)

REQUIRED_MANIFEST_FIELDS = (
    "run_id",
    "model_version",
    "equation_set_hash",
    "solver_source_hash",
    "parameter_file_hash",
    "software_versions",
    "floating_point_precision",
    "solver_method",
    "mesh_or_collocation",
    "absolute_tolerance",
    "relative_tolerance",
    "initial_guess_provenance",
    "seed",
    "output_hashes",
    "status",
)

REQUIRED_BOUNDARY_FIELDS = (
    "normal_r",
    "A_prime",
    "L",
    "L_prime",
    "phi",
    "phi_prime",
    "A_chi",
    "Q",
    "Z_F",
)

REQUIRED_PROFILE_COLUMNS = (
    "r",
    "A",
    "A_prime",
    "L",
    "L_prime",
    "phi",
    "phi_prime",
)

REQUIRED_BENCHMARKS = (
    "sqrt_K4_rho_cap",
    "kappa6_squared_lambda_eff_over_4sqrtK4",
    "K4_rho_cap_squared",
    "V_W",
    "R_circle_at_K4_beta_1",
    "Xi_cap_reported",
)

REFERENCE_BENCHMARKS = {
    "sqrt_K4_rho_cap": 1.1196329253611,
    "kappa6_squared_lambda_eff_over_4sqrtK4": 0.8931498683204,
    "K4_rho_cap_squared": 1.2535778875527,
    "V_W": 0.5318111250097,
    "R_circle_at_K4_beta_1": 0.6661500466003,
    "Xi_cap_reported": 0.9999999998535,
}

REQUIRED_RESIDUAL_FIELDS = (
    "equation_id",
    "raw_residual",
    "normalized_residual",
    "absolute_tolerance",
    "relative_tolerance",
    "evaluation_location",
    "status",
)


class VerificationError(RuntimeError):
    """Raised for malformed package content that prevents a meaningful check."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report exact parse/read failure
        raise VerificationError(f"Cannot parse {path.name}: {exc}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_hash(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text.lower().startswith("sha256:"):
        text = text.split(":", 1)[1]
    return text.lower() if HEX64.fullmatch(text) else None


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def safe_relative_path(root: Path, relative: str) -> Path | None:
    if not isinstance(relative, str) or not relative.strip():
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def check_required_files(root: Path) -> dict[str, Any]:
    missing = [name for name in REQUIRED_FILES if not (root / name).is_file()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "missing": missing,
    }


def check_manifest(root: Path, manifest: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(manifest, dict):
        return {"status": "FAIL", "errors": ["manifest.json must contain an object"]}

    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            errors.append(f"missing manifest field: {field}")

    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not RUN_ID.fullmatch(run_id):
        errors.append("run_id must match MD2S-RUN-YYYYMMDD-NNN")

    for field in ("equation_set_hash", "solver_source_hash", "parameter_file_hash"):
        if field in manifest and normalize_hash(manifest.get(field)) is None:
            errors.append(f"{field} is not a SHA-256 digest")

    if manifest.get("status") not in {"PASS", "FAIL", "INCOMPLETE"}:
        errors.append("manifest status must be PASS, FAIL or INCOMPLETE")

    for field in ("absolute_tolerance", "relative_tolerance"):
        value = manifest.get(field)
        if not finite_number(value) or float(value) < 0.0:
            errors.append(f"{field} must be a finite non-negative number")

    for field in ("software_versions", "mesh_or_collocation", "output_hashes"):
        if field in manifest and not isinstance(manifest.get(field), dict):
            errors.append(f"{field} must be an object")

    if manifest.get("seed") is not None and not isinstance(manifest.get("seed"), int):
        errors.append("seed must be null or an integer")

    if manifest.get("status") == "PASS" and errors:
        warnings.append("manifest claims PASS although structural errors exist")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
    }


def check_output_hashes(root: Path, manifest: Any) -> dict[str, Any]:
    errors: list[str] = []
    verified: dict[str, str] = {}

    output_hashes = manifest.get("output_hashes", {}) if isinstance(manifest, dict) else {}
    if not isinstance(output_hashes, dict):
        return {"status": "FAIL", "errors": ["output_hashes must be an object"], "verified": {}}

    for relative, expected_raw in output_hashes.items():
        target = safe_relative_path(root, relative)
        if target is None:
            errors.append(f"unsafe output path: {relative!r}")
            continue
        if target.name == "manifest.json":
            errors.append("manifest.json must not hash itself")
            continue
        expected = normalize_hash(expected_raw)
        if expected is None:
            errors.append(f"invalid SHA-256 for {relative}")
            continue
        if not target.is_file():
            errors.append(f"hashed output missing: {relative}")
            continue
        actual = sha256_file(target)
        if actual != expected:
            errors.append(f"hash mismatch: {relative}")
            continue
        verified[relative] = actual

    mandatory_outputs = {name for name in REQUIRED_FILES if name != "manifest.json"}
    unhashed = sorted(mandatory_outputs.difference(output_hashes.keys()))
    if unhashed:
        errors.append("mandatory outputs absent from output_hashes: " + ", ".join(unhashed))

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "verified": verified,
    }


def check_boundaries(left: Any, right: Any) -> dict[str, Any]:
    side_results: dict[str, Any] = {}
    overall_errors: list[str] = []

    for side, data in (("left", left), ("right", right)):
        errors: list[str] = []
        if not isinstance(data, dict):
            errors.append(f"boundary-{side}.json must contain an object")
        else:
            missing = [field for field in REQUIRED_BOUNDARY_FIELDS if field not in data]
            if missing:
                errors.append("missing fields: " + ", ".join(missing))
            for field in REQUIRED_BOUNDARY_FIELDS:
                if field in data and not finite_number(data[field]):
                    errors.append(f"{field} must be finite numeric")
            if finite_number(data.get("normal_r")) and abs(abs(float(data["normal_r"])) - 1.0) > 1e-12:
                errors.append("normal_r must be +1 or -1 in the declared radial convention")
            if finite_number(data.get("L")) and float(data["L"]) <= 0.0:
                errors.append("L must be positive at a non-degenerate cap junction")
        side_results[side] = {"status": "PASS" if not errors else "FAIL", "errors": errors}
        overall_errors.extend(f"{side}: {error}" for error in errors)

    if isinstance(left, dict) and isinstance(right, dict):
        nl = left.get("normal_r")
        nr = right.get("normal_r")
        if finite_number(nl) and finite_number(nr) and float(nl) * float(nr) >= 0.0:
            overall_errors.append("oriented normals must have opposite signs for the two stored sides")

    return {
        "status": "PASS" if not overall_errors else "FAIL",
        "sides": side_results,
        "errors": overall_errors,
    }


def check_profiles(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    row_count = 0
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            header = reader.fieldnames or []
            missing = [name for name in REQUIRED_PROFILE_COLUMNS if name not in header]
            if missing:
                errors.append("missing profile columns: " + ", ".join(missing))
            previous_r: float | None = None
            for line_number, row in enumerate(reader, start=2):
                row_count += 1
                for name in REQUIRED_PROFILE_COLUMNS:
                    if name not in row:
                        continue
                    try:
                        value = float(row[name])
                    except (TypeError, ValueError):
                        errors.append(f"line {line_number}: {name} is not numeric")
                        continue
                    if not math.isfinite(value):
                        errors.append(f"line {line_number}: {name} is not finite")
                    if name == "r":
                        if previous_r is not None and value <= previous_r:
                            errors.append(f"line {line_number}: r is not strictly increasing")
                        previous_r = value
            if row_count < 3:
                errors.append("profiles.csv must contain at least three data rows")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"cannot read profiles.csv: {exc}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "row_count": row_count,
        "errors": errors,
    }


def check_benchmarks(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    comparisons: dict[str, Any] = {}

    if not isinstance(data, dict):
        return {"status": "FAIL", "errors": ["benchmarks.json must contain an object"]}

    values = data.get("values", data)
    if not isinstance(values, dict):
        return {"status": "FAIL", "errors": ["benchmark values must be an object"]}

    tolerances = data.get("tolerances", {})
    if tolerances is not None and not isinstance(tolerances, dict):
        errors.append("tolerances must be an object when supplied")
        tolerances = {}

    for name in REQUIRED_BENCHMARKS:
        if name not in values:
            errors.append(f"missing benchmark: {name}")
            continue
        value = values[name]
        if not finite_number(value):
            errors.append(f"benchmark {name} must be finite numeric")
            continue
        reference = REFERENCE_BENCHMARKS[name]
        absolute_error = abs(float(value) - reference)
        tolerance = tolerances.get(name) if isinstance(tolerances, dict) else None
        if tolerance is not None and (not finite_number(tolerance) or float(tolerance) < 0.0):
            errors.append(f"invalid tolerance for {name}")
            tolerance = None
        passed = None if tolerance is None else absolute_error <= float(tolerance)
        comparisons[name] = {
            "value": float(value),
            "reference": reference,
            "absolute_error": absolute_error,
            "declared_tolerance": tolerance,
            "within_tolerance": passed,
        }
        if tolerance is None:
            errors.append(f"missing predeclared tolerance for {name}")
        elif not passed:
            errors.append(f"benchmark outside tolerance: {name}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "comparisons": comparisons,
    }


def check_residuals(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    entries: list[Any]

    if isinstance(data, dict):
        entries = data.get("residuals", [])
    else:
        entries = data

    if not isinstance(entries, list) or not entries:
        return {"status": "FAIL", "errors": ["residuals must be a non-empty list"], "count": 0}

    ids: set[str] = set()
    for index, entry in enumerate(entries):
        prefix = f"residual[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = [field for field in REQUIRED_RESIDUAL_FIELDS if field not in entry]
        if missing:
            errors.append(f"{prefix} missing: " + ", ".join(missing))
        equation_id = entry.get("equation_id")
        if not isinstance(equation_id, str) or not equation_id.strip():
            errors.append(f"{prefix} equation_id must be non-empty")
        elif equation_id in ids:
            errors.append(f"duplicate equation_id: {equation_id}")
        else:
            ids.add(equation_id)
        for field in ("raw_residual", "normalized_residual", "absolute_tolerance", "relative_tolerance"):
            if field in entry and (not finite_number(entry[field]) or ("tolerance" in field and float(entry[field]) < 0.0)):
                errors.append(f"{prefix} {field} must be finite and tolerances non-negative")
        if entry.get("status") not in {"PASS", "FAIL", "OPEN", "NOT_EVALUATED"}:
            errors.append(f"{prefix} has invalid status")
        if entry.get("status") == "PASS" and finite_number(entry.get("normalized_residual")):
            atol = float(entry.get("absolute_tolerance", 0.0)) if finite_number(entry.get("absolute_tolerance")) else 0.0
            rtol = float(entry.get("relative_tolerance", 0.0)) if finite_number(entry.get("relative_tolerance")) else 0.0
            if abs(float(entry["normalized_residual"])) > max(atol, rtol):
                errors.append(f"{prefix} claims PASS outside its declared normalized tolerance")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "count": len(entries),
        "equation_ids": sorted(ids),
    }


def verify(root: Path) -> dict[str, Any]:
    root = root.resolve()
    checks: dict[str, Any] = {}
    checks["required_files"] = check_required_files(root)

    if checks["required_files"]["status"] == "FAIL":
        return {
            "schema": SCHEMA,
            "package": str(root),
            "status": "FAIL",
            "checks": checks,
            "scope_warning": "Structural verification only; no physical certification.",
        }

    manifest = load_json(root / "manifest.json")
    left = load_json(root / "boundary-left.json")
    right = load_json(root / "boundary-right.json")
    benchmarks = load_json(root / "benchmarks.json")
    residuals = load_json(root / "residuals.json")

    checks["manifest"] = check_manifest(root, manifest)
    checks["output_hashes"] = check_output_hashes(root, manifest)
    checks["boundaries"] = check_boundaries(left, right)
    checks["profiles"] = check_profiles(root / "profiles.csv")
    checks["benchmarks"] = check_benchmarks(benchmarks)
    checks["residuals"] = check_residuals(residuals)

    failed = [name for name, result in checks.items() if result.get("status") != "PASS"]
    return {
        "schema": SCHEMA,
        "package": str(root),
        "run_id": manifest.get("run_id") if isinstance(manifest, dict) else None,
        "status": "PASS" if not failed else "FAIL",
        "failed_checks": failed,
        "checks": checks,
        "scope_warning": (
            "PASS means package-complete and internally hash/structure-consistent only. "
            "It does not establish correct field equations, uniqueness, junction closure, "
            "stability, ghost freedom, physical identification or empirical evidence."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="MD-2S run-package directory")
    parser.add_argument("--json-out", type=Path, help="optional verification report path")
    args = parser.parse_args()

    try:
        result = verify(args.package)
    except VerificationError as exc:
        result = {
            "schema": SCHEMA,
            "package": str(args.package),
            "status": "FAIL",
            "fatal_error": str(exc),
            "scope_warning": "Structural verification could not be completed.",
        }
    except Exception as exc:  # noqa: BLE001 - do not hide verifier failures
        result = {
            "schema": SCHEMA,
            "package": str(args.package),
            "status": "FAIL",
            "fatal_error": f"unexpected verifier error: {exc}",
            "scope_warning": "Structural verification could not be completed.",
        }

    output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(output)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n", encoding="utf-8")
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
