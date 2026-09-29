#!/usr/bin/env python3
"""SIM-70 response-rank evidence auditor v1.5.

Closes three pre-execution QA gaps left after v1.4:
- F12: bind recorded response matrices to the run manifest/config/job bytes;
- F13: automate the local-linearity diagnostic eta_i(h);
- F14: automate sensitivity of the rank verdict to multiple predeclared scale sets.

This module is numerical/provenance QA only. It never authorizes a physical
solver run, never releases K1-D/K1-E, and never creates physical evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
V14_PATH = HERE / "2026-09-28_hzt_physical_response_rank_auditor_v1.4.py"
SPEC = importlib.util.spec_from_file_location("sim70_response_rank_v14", V14_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load response-rank auditor v1.4")
V14 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V14
SPEC.loader.exec_module(V14)

LEVELS = (("h", 0), ("h2", 1), ("h4", 2))


class EvidenceAuditError(RuntimeError):
    pass


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise EvidenceAuditError(f"expected JSON object: {path}")
    return data


def finite_vector(mapping: dict[str, Any], keys: list[str], label: str) -> np.ndarray:
    values = []
    for key in keys:
        if key not in mapping:
            raise EvidenceAuditError(f"{label}: missing {key}")
        value = float(mapping[key])
        if not math.isfinite(value):
            raise EvidenceAuditError(f"{label}: non-finite {key}")
        values.append(value)
    return np.asarray(values, dtype=float)


def parse_scale_sets(path: Path, controls: list[str], outputs: list[str]) -> dict[str, Any]:
    data = load_json(path)
    if data.get("status") != "FROZEN_BEFORE_RANK_RESULT":
        raise EvidenceAuditError("scale-sensitivity contract must be frozen before the rank result")
    sets = data.get("scale_sets")
    if not isinstance(sets, list) or len(sets) < 2:
        raise EvidenceAuditError("at least two predeclared scale sets are required")
    primary_id = data.get("primary_scale_set")
    if not isinstance(primary_id, str) or not primary_id:
        raise EvidenceAuditError("primary_scale_set missing")

    normalized = {}
    signatures = set()
    for item in sets:
        if not isinstance(item, dict):
            raise EvidenceAuditError("invalid scale-set record")
        sid = item.get("id")
        if not isinstance(sid, str) or not sid or sid in normalized:
            raise EvidenceAuditError("scale-set ids must be unique non-empty strings")
        sc_map = item.get("control_scales", {})
        sy_map = item.get("output_scales", {})
        if any(k not in sc_map for k in controls) or any(k not in sy_map for k in outputs):
            raise EvidenceAuditError(f"{sid}: incomplete scale coverage")
        sc = np.asarray([float(sc_map[k]) for k in controls], dtype=float)
        sy = np.asarray([float(sy_map[k]) for k in outputs], dtype=float)
        if (
            np.any(~np.isfinite(sc))
            or np.any(~np.isfinite(sy))
            or np.any(sc <= 0)
            or np.any(sy <= 0)
        ):
            raise EvidenceAuditError(f"{sid}: scales must be finite and >0")
        signature = tuple(sc.tolist() + sy.tolist())
        signatures.add(signature)
        normalized[sid] = {
            "control_scales": sc,
            "output_scales": sy,
            "rationale": item.get("rationale"),
        }

    if primary_id not in normalized:
        raise EvidenceAuditError("primary scale set not found")
    if len(signatures) < 2:
        raise EvidenceAuditError("scale-sensitivity contract contains no distinct alternative scale set")

    return {
        "raw": data,
        "primary_scale_set": primary_id,
        "sets": normalized,
    }


def read_job_bundle(run_dir: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    jobs_dir = run_dir / "jobs"
    jobs = manifest.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise EvidenceAuditError("run manifest has no job list")

    bundle = {}
    for job_id in jobs:
        if not isinstance(job_id, str) or not job_id:
            raise EvidenceAuditError("invalid job id")
        input_path = jobs_dir / f"{job_id}.input.json"
        output_path = jobs_dir / f"{job_id}.output.json"
        if not input_path.is_file() or not output_path.is_file():
            raise EvidenceAuditError(f"missing input/output job artifact for {job_id}")
        inp = load_json(input_path)
        out = load_json(output_path)
        expected_input_sha = canonical_sha256(inp)
        if out.get("input_sha256") != expected_input_sha:
            raise EvidenceAuditError(f"{job_id}: output input_sha256 mismatch")
        if out.get("job_id") != job_id:
            raise EvidenceAuditError(f"{job_id}: output job identity mismatch")
        bundle[job_id] = {
            "input": inp,
            "output": out,
            "input_path": input_path,
            "output_path": output_path,
            "input_file_sha256": file_sha256(input_path),
            "output_file_sha256": file_sha256(output_path),
            "input_canonical_sha256": expected_input_sha,
        }
    return bundle


def recompute_matrix(
    bundle: dict[str, dict[str, Any]],
    config: dict[str, Any],
    controls: list[str],
    outputs: list[str],
    level_index: int,
    *,
    prefix: str = "",
) -> np.ndarray:
    label, idx = LEVELS[level_index]
    steps = config.get("relative_steps")
    scales = config.get("perturbation_scales", {})
    if not isinstance(steps, list) or len(steps) != 3:
        raise EvidenceAuditError("config relative_steps must contain h,h/2,h/4")
    h = float(steps[idx])
    result = np.zeros((len(outputs), len(controls)), dtype=float)
    for j, control in enumerate(controls):
        if control not in scales:
            raise EvidenceAuditError(f"missing perturbation scale for {control}")
        delta = h * float(scales[control])
        if not math.isfinite(delta) or delta <= 0:
            raise EvidenceAuditError(f"invalid perturbation delta for {control}")
        plus_id = f"{prefix}{label}__{control}__plus"
        minus_id = f"{prefix}{label}__{control}__minus"
        if plus_id not in bundle or minus_id not in bundle:
            raise EvidenceAuditError(f"missing perturbation jobs for {label}/{control}")
        plus = finite_vector(bundle[plus_id]["output"].get("outputs", {}), outputs, plus_id)
        minus = finite_vector(bundle[minus_id]["output"].get("outputs", {}), outputs, minus_id)
        result[:, j] = (plus - minus) / (2.0 * delta)
    return result


def compare_recorded_matrix(path: Path, expected: np.ndarray) -> dict[str, Any]:
    outputs, controls, observed = V14.read_matrix(path)
    if observed.shape != expected.shape:
        raise EvidenceAuditError(f"{path.name}: shape mismatch")
    diff = observed - expected
    scale = max(1.0, float(np.max(np.abs(expected))))
    max_abs = float(np.max(np.abs(diff)))
    tolerance = 2.0e-14 * scale
    if max_abs > tolerance:
        raise EvidenceAuditError(
            f"{path.name}: recorded matrix does not match job-output reconstruction "
            f"(max_abs={max_abs:.3e}, tol={tolerance:.3e})"
        )
    return {
        "path": str(path),
        "sha256": file_sha256(path),
        "shape": list(observed.shape),
        "outputs": outputs,
        "controls": controls,
        "max_abs_reconstruction_error": max_abs,
        "reconstruction_tolerance": tolerance,
    }


def local_linearity(
    bundle: dict[str, dict[str, Any]],
    config: dict[str, Any],
    controls: list[str],
    outputs: list[str],
    sy: np.ndarray,
    *,
    epsilon_floor: float,
    monotonic_tolerance: float,
) -> dict[str, Any]:
    if "baseline" not in bundle:
        raise EvidenceAuditError("baseline job is required for local-linearity audit")
    y0 = finite_vector(bundle["baseline"]["output"].get("outputs", {}), outputs, "baseline")
    steps = config.get("relative_steps")
    records = {}
    all_monotonic = True

    for control in controls:
        eta = {}
        for label, idx in LEVELS:
            plus_id = f"{label}__{control}__plus"
            minus_id = f"{label}__{control}__minus"
            plus = finite_vector(bundle[plus_id]["output"].get("outputs", {}), outputs, plus_id)
            minus = finite_vector(bundle[minus_id]["output"].get("outputs", {}), outputs, minus_id)
            q = plus + minus - 2.0 * y0
            odd = plus - minus
            q_norm = float(np.linalg.norm(q / sy, 2))
            odd_norm = float(np.linalg.norm(odd / sy, 2))
            value = q_norm / max(odd_norm, epsilon_floor)
            eta[label] = {
                "relative_step": float(steps[idx]),
                "eta": value,
                "q_norm": q_norm,
                "odd_response_norm": odd_norm,
            }
        monotonic = (
            eta["h2"]["eta"] <= eta["h"]["eta"] + monotonic_tolerance
            and eta["h4"]["eta"] <= eta["h2"]["eta"] + monotonic_tolerance
        )
        records[control] = {"levels": eta, "decreases_under_step_halving": monotonic}
        all_monotonic = all_monotonic and monotonic

    return {
        "epsilon_floor": epsilon_floor,
        "monotonic_tolerance": monotonic_tolerance,
        "controls": records,
        "all_controls_decrease_under_step_halving": all_monotonic,
    }


def scale_sensitivity(
    R: np.ndarray,
    R2: np.ndarray,
    R4: np.ndarray,
    R4_ref: np.ndarray | None,
    scale_contract: dict[str, Any],
    *,
    q: float,
    cond_max: float,
    formal_rel_tol: float,
) -> dict[str, Any]:
    records = {}
    all_supported = True
    for sid, item in scale_contract["sets"].items():
        sc = item["control_scales"]
        sy = item["output_scales"]
        j = V14.normalized_jacobian(R, sc, sy)
        j2 = V14.normalized_jacobian(R2, sc, sy)
        j4 = V14.normalized_jacobian(R4, sc, sy)
        _, s4, _, condition = V14.svd_decomp(j4)
        eps_step = float(np.linalg.norm(j2 - j4, 2))
        eps_solver = (
            float(np.linalg.norm(j4 - V14.normalized_jacobian(R4_ref, sc, sy), 2))
            if R4_ref is not None
            else 0.0
        )
        eps_j = eps_step + eps_solver
        sigmax = float(s4[0])
        sigmin = float(s4[-1])
        formal_rank = int(np.sum(s4 > formal_rel_tol * sigmax)) if sigmax > 0 else 0
        rrqr = V14.rrqr_diagnostics(j4, formal_rel_tol)
        minors = V14.minor_diagnostics(j4, formal_rel_tol)
        supported = (
            formal_rank == 4
            and rrqr["rank"] == 4
            and minors["rank4_support"]
            and sigmin > q * eps_j
            and condition <= cond_max
        )
        records[sid] = {
            "rationale": item.get("rationale"),
            "formal_rank": formal_rank,
            "rrqr_rank": rrqr["rank"],
            "minor_rank4_support": minors["rank4_support"],
            "singular_values": [float(v) for v in s4],
            "condition_number": float(condition) if math.isfinite(condition) else None,
            "epsilon_step": eps_step,
            "epsilon_solver": eps_solver,
            "epsilon_J": eps_j,
            "sigma_min_over_epsilon_J": (
                sigmin / eps_j if eps_j > 0 else (math.inf if sigmin > 0 else 0.0)
            ),
            "rank4_supported_under_this_scale_set": supported,
        }
        all_supported = all_supported and supported

    return {
        "primary_scale_set": scale_contract["primary_scale_set"],
        "scale_set_count": len(records),
        "records": records,
        "rank4_supported_under_all_predeclared_scale_sets": all_supported,
    }


def build_audit(
    run_dir: Path,
    config_path: Path,
    scale_sensitivity_path: Path,
    *,
    q: float,
    cond_max: float,
    formal_rel_tol: float,
    epsilon_floor: float,
    monotonic_tolerance: float,
) -> dict[str, Any]:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.is_file():
        raise EvidenceAuditError("manifest.json missing")
    manifest = load_json(manifest_path)
    config = load_json(config_path)

    expected_cfg_hash = manifest.get("config_sha256")
    actual_cfg_hash = canonical_sha256(config)
    if expected_cfg_hash != actual_cfg_hash:
        raise EvidenceAuditError("manifest/config SHA-256 binding mismatch")

    bundle = read_job_bundle(run_dir, manifest)

    matrix_paths = {
        "h": run_dir / "R_h.csv",
        "h2": run_dir / "R_h2.csv",
        "h4": run_dir / "R_h4.csv",
    }
    for path in matrix_paths.values():
        if not path.is_file():
            raise EvidenceAuditError(f"missing recorded matrix: {path.name}")

    labels_h = V14.read_matrix(matrix_paths["h"])
    outputs, controls = labels_h[0], labels_h[1]
    if len(outputs) != 4 or len(controls) < 4:
        raise EvidenceAuditError("response-matrix shape is not gate-eligible")

    expected_R = recompute_matrix(bundle, config, controls, outputs, 0)
    expected_R2 = recompute_matrix(bundle, config, controls, outputs, 1)
    expected_R4 = recompute_matrix(bundle, config, controls, outputs, 2)

    matrix_binding = {
        "h": compare_recorded_matrix(matrix_paths["h"], expected_R),
        "h2": compare_recorded_matrix(matrix_paths["h2"], expected_R2),
        "h4": compare_recorded_matrix(matrix_paths["h4"], expected_R4),
    }

    R4_ref = None
    refined_path = run_dir / "R_h4_refined.csv"
    if refined_path.is_file():
        expected_ref = recompute_matrix(bundle, config, controls, outputs, 2, prefix="refined__")
        matrix_binding["h4_refined"] = compare_recorded_matrix(refined_path, expected_ref)
        R4_ref = expected_ref

    scale_contract = parse_scale_sets(scale_sensitivity_path, controls, outputs)
    primary = scale_contract["sets"][scale_contract["primary_scale_set"]]
    linearity = local_linearity(
        bundle,
        config,
        controls,
        outputs,
        primary["output_scales"],
        epsilon_floor=epsilon_floor,
        monotonic_tolerance=monotonic_tolerance,
    )
    sensitivity = scale_sensitivity(
        expected_R,
        expected_R2,
        expected_R4,
        R4_ref,
        scale_contract,
        q=q,
        cond_max=cond_max,
        formal_rel_tol=formal_rel_tol,
    )

    job_hashes = {
        job_id: {
            "input_file_sha256": item["input_file_sha256"],
            "output_file_sha256": item["output_file_sha256"],
            "input_canonical_sha256": item["input_canonical_sha256"],
        }
        for job_id, item in sorted(bundle.items())
    }
    provenance_payload = {
        "manifest_file_sha256": file_sha256(manifest_path),
        "manifest_canonical_sha256": canonical_sha256(manifest),
        "config_file_sha256": file_sha256(config_path),
        "config_canonical_sha256": actual_cfg_hash,
        "scale_sensitivity_file_sha256": file_sha256(scale_sensitivity_path),
        "matrix_files": {key: value["sha256"] for key, value in matrix_binding.items()},
        "jobs": job_hashes,
    }
    evidence_root = canonical_sha256(provenance_payload)

    ready = (
        linearity["all_controls_decrease_under_step_halving"]
        and sensitivity["rank4_supported_under_all_predeclared_scale_sets"]
        and R4_ref is not None
    )

    return {
        "schema": "universelab.ulsh01.sim70.response-rank-evidence-audit.v1.5",
        "status": "READY_FOR_INDEPENDENT_NUMERICAL_RANK_QA" if ready else "INCONCLUSIVE_FAIL_CLOSED",
        "run_id": manifest.get("run_id") or manifest.get("schema"),
        "matrix_provenance_binding": matrix_binding,
        "local_linearity": linearity,
        "scale_sensitivity": sensitivity,
        "provenance": {
            **provenance_payload,
            "response_evidence_root_sha256": evidence_root,
        },
        "remaining_requirements": (
            []
            if ready
            else [
                item
                for item, failed in (
                    ("LOCAL_LINEARITY_NOT_MONOTONIC", not linearity["all_controls_decrease_under_step_halving"]),
                    ("SCALE_SENSITIVITY_NOT_STABLE", not sensitivity["rank4_supported_under_all_predeclared_scale_sets"]),
                    ("SOLVER_REFINED_H4_MATRIX_MISSING", R4_ref is None),
                )
                if failed
            ]
        ),
        "physical_interpretation": "NONE",
        "canonical_effect": "NONE",
        "physical_evidence_effect": "NONE_NUMERICAL_QA_ONLY",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "limitations": [
            "Matrix-byte provenance and numerical QA do not prove the physical model.",
            "This auditor does not execute or authorize the physical BVP solver.",
            "Scale-set choices must be scientifically justified and frozen before inspecting the rank result.",
            "A ready packet still requires independent CTRL-02 review and any separately required high-precision solver replay.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("config_json", type=Path)
    parser.add_argument("scale_sensitivity_json", type=Path)
    parser.add_argument("--q", type=float, default=5.0)
    parser.add_argument("--cond-max", type=float, default=1.0e6)
    parser.add_argument("--formal-rel-tol", type=float, default=1.0e-8)
    parser.add_argument("--epsilon-floor", type=float, default=1.0e-15)
    parser.add_argument("--linearity-monotonic-tolerance", type=float, default=1.0e-12)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = build_audit(
        args.run_dir.resolve(),
        args.config_json.resolve(),
        args.scale_sensitivity_json.resolve(),
        q=args.q,
        cond_max=args.cond_max,
        formal_rel_tol=args.formal_rel_tol,
        epsilon_floor=args.epsilon_floor,
        monotonic_tolerance=args.linearity_monotonic_tolerance,
    )
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if result["status"] == "READY_FOR_INDEPENDENT_NUMERICAL_RANK_QA" else 2


if __name__ == "__main__":
    raise SystemExit(main())
