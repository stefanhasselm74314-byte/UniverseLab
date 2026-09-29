#!/usr/bin/env python3
"""Adversarial QA for SIM-70 response-rank evidence auditor v1.5.

Synthetic software QA only. No physical solver is imported or executed.
"""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

import numpy as np

HERE = Path(__file__).resolve().parent
TARGET = HERE / "2026-09-29_hzt_physical_response_rank_evidence_auditor_v1.5.py"
SPEC = importlib.util.spec_from_file_location("sim70_rank_evidence_v15", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load v1.5 auditor")
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)

CONTROLS = ["c1", "c2", "c3", "c4", "c5"]
OUTPUTS = ["y1", "y2", "y3", "y4"]
A = np.asarray(
    [
        [4.0, 0.0, 0.0, 0.0, 0.10],
        [0.0, 3.0, 0.0, 0.0, 0.10],
        [0.0, 0.0, 2.0, 0.0, 0.10],
        [0.0, 0.0, 0.0, 1.0, 0.10],
    ],
    dtype=float,
)
B = np.asarray(
    [
        [0.03, 0.01, 0.02, 0.015, 0.01],
        [0.01, 0.02, 0.01, 0.010, 0.02],
        [0.02, 0.01, 0.03, 0.020, 0.01],
        [0.01, 0.02, 0.01, 0.025, 0.02],
    ],
    dtype=float,
)


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def y_of(x: np.ndarray) -> np.ndarray:
    return A @ x + B @ (x * x)


def make_job(run_dir: Path, job_id: str, x: np.ndarray) -> None:
    inp = {
        "schema": "synthetic.sim70.v1",
        "job_id": job_id,
        "controls": {k: float(v) for k, v in zip(CONTROLS, x)},
    }
    out = {
        "schema": "synthetic.sim70.out.v1",
        "job_id": job_id,
        "input_sha256": M.canonical_sha256(inp),
        "outputs": {k: float(v) for k, v in zip(OUTPUTS, y_of(x))},
    }
    dump(run_dir / "jobs" / f"{job_id}.input.json", inp)
    dump(run_dir / "jobs" / f"{job_id}.output.json", out)


def write_matrix(path: Path, matrix: np.ndarray) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["output"] + CONTROLS)
        for name, row in zip(OUTPUTS, matrix):
            w.writerow([name] + [f"{float(v):.17g}" for v in row])


def build_fixture(root: Path) -> tuple[Path, Path, Path]:
    run_dir = root / "run"
    run_dir.mkdir(parents=True)
    config_path = root / "config.json"
    scales_path = root / "scales.json"

    config = {
        "schema": "synthetic.response.config.v1",
        "baseline_controls": {k: 0.0 for k in CONTROLS},
        "perturbation_scales": {k: 1.0 for k in CONTROLS},
        "relative_steps": [0.01, 0.005, 0.0025],
    }
    dump(config_path, config)

    jobs = []
    baseline = np.zeros(len(CONTROLS), dtype=float)
    make_job(run_dir, "baseline", baseline)
    jobs.append("baseline")
    labels = [("h", 0.01), ("h2", 0.005), ("h4", 0.0025)]
    for label, h in labels:
        for j, control in enumerate(CONTROLS):
            for suffix, sign in (("plus", 1.0), ("minus", -1.0)):
                x = baseline.copy()
                x[j] += sign * h
                jid = f"{label}__{control}__{suffix}"
                make_job(run_dir, jid, x)
                jobs.append(jid)
    for j, control in enumerate(CONTROLS):
        for suffix, sign in (("plus", 1.0), ("minus", -1.0)):
            x = baseline.copy()
            x[j] += sign * 0.0025
            jid = f"refined__h4__{control}__{suffix}"
            make_job(run_dir, jid, x)
            jobs.append(jid)

    manifest = {
        "schema": "synthetic.response.manifest.v1",
        "run_id": "SIM70-SYNTHETIC-V15",
        "config_sha256": M.canonical_sha256(config),
        "jobs": jobs,
        "rank_claim_allowed": False,
        "evidence_effect": "NONE_SYNTHETIC_OR_QA",
        "synthetic_jobs": jobs,
    }
    dump(run_dir / "manifest.json", manifest)

    for label in ("h", "h2", "h4"):
        write_matrix(run_dir / f"R_{label}.csv", A)
    write_matrix(run_dir / "R_h4_refined.csv", A)

    scale_contract = {
        "schema": "synthetic.scale-sensitivity.v1",
        "status": "FROZEN_BEFORE_RANK_RESULT",
        "primary_scale_set": "PRIMARY",
        "scale_sets": [
            {
                "id": "PRIMARY",
                "rationale": "synthetic unit scales",
                "control_scales": {k: 1.0 for k in CONTROLS},
                "output_scales": {k: 1.0 for k in OUTPUTS},
            },
            {
                "id": "ALT",
                "rationale": "synthetic moderate alternative",
                "control_scales": dict(zip(CONTROLS, [1.2, 0.8, 1.1, 0.9, 1.3])),
                "output_scales": dict(zip(OUTPUTS, [0.9, 1.2, 1.0, 1.1])),
            },
        ],
    }
    dump(scales_path, scale_contract)
    return run_dir, config_path, scales_path


def audit(run_dir: Path, config: Path, scales: Path):
    return M.build_audit(
        run_dir,
        config,
        scales,
        q=5.0,
        cond_max=1.0e6,
        formal_rel_tol=1.0e-8,
        epsilon_floor=1.0e-15,
        monotonic_tolerance=1.0e-12,
    )


def test_happy_path() -> None:
    with tempfile.TemporaryDirectory() as td:
        run_dir, config, scales = build_fixture(Path(td))
        out = audit(run_dir, config, scales)
        assert out["status"] == "READY_FOR_INDEPENDENT_NUMERICAL_RANK_QA"
        assert out["local_linearity"]["all_controls_decrease_under_step_halving"] is True
        assert out["scale_sensitivity"]["rank4_supported_under_all_predeclared_scale_sets"] is True
        assert out["provenance"]["response_evidence_root_sha256"]
        assert out["physical_interpretation"] == "NONE"
        assert out["canonical_effect"] == "NONE"
        assert out["K1-D"] == "NOT_RELEASED"
        assert out["K1-E"] == "NOT_ADMISSIBLE"


def test_matrix_mutation_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as td:
        run_dir, config, scales = build_fixture(Path(td))
        matrix_path = run_dir / "R_h4.csv"
        rows = list(csv.reader(matrix_path.open(encoding="utf-8")))
        rows[1][1] = str(float(rows[1][1]) + 1.0e-4)
        with matrix_path.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(rows)
        try:
            audit(run_dir, config, scales)
        except M.EvidenceAuditError as exc:
            assert "does not match job-output reconstruction" in str(exc)
        else:
            raise AssertionError("matrix mutation must fail closed")


def test_input_hash_chain_mutation_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as td:
        run_dir, config, scales = build_fixture(Path(td))
        output_path = run_dir / "jobs" / "h__c1__plus.output.json"
        out = json.loads(output_path.read_text(encoding="utf-8"))
        out["input_sha256"] = "0" * 64
        dump(output_path, out)
        try:
            audit(run_dir, config, scales)
        except M.EvidenceAuditError as exc:
            assert "input_sha256 mismatch" in str(exc)
        else:
            raise AssertionError("broken input hash chain must fail closed")


def test_nonmonotonic_local_linearity_is_inconclusive() -> None:
    with tempfile.TemporaryDirectory() as td:
        run_dir, config, scales = build_fixture(Path(td))
        for suffix in ("plus", "minus"):
            output_path = run_dir / "jobs" / f"h4__c1__{suffix}.output.json"
            out = json.loads(output_path.read_text(encoding="utf-8"))
            out["outputs"]["y1"] += 0.01
            dump(output_path, out)
        # Rebuild the recorded h4 matrix: the common offset cancels in the central derivative.
        write_matrix(run_dir / "R_h4.csv", A)
        out = audit(run_dir, config, scales)
        assert out["status"] == "INCONCLUSIVE_FAIL_CLOSED"
        assert out["local_linearity"]["all_controls_decrease_under_step_halving"] is False
        assert "LOCAL_LINEARITY_NOT_MONOTONIC" in out["remaining_requirements"]


def test_scale_sensitive_rank_is_inconclusive() -> None:
    with tempfile.TemporaryDirectory() as td:
        run_dir, config, scales = build_fixture(Path(td))
        data = json.loads(scales.read_text(encoding="utf-8"))
        alt = data["scale_sets"][1]
        alt["control_scales"]["c4"] = 1.0e-12
        alt["control_scales"]["c5"] = 1.0e-12
        dump(scales, data)
        out = audit(run_dir, config, scales)
        assert out["status"] == "INCONCLUSIVE_FAIL_CLOSED"
        assert out["scale_sensitivity"]["rank4_supported_under_all_predeclared_scale_sets"] is False
        assert "SCALE_SENSITIVITY_NOT_STABLE" in out["remaining_requirements"]


def test_scale_contract_requires_distinct_predeclared_alternative() -> None:
    with tempfile.TemporaryDirectory() as td:
        run_dir, config, scales = build_fixture(Path(td))
        data = json.loads(scales.read_text(encoding="utf-8"))
        data["scale_sets"] = [data["scale_sets"][0], dict(data["scale_sets"][0], id="COPY")]
        dump(scales, data)
        try:
            audit(run_dir, config, scales)
        except M.EvidenceAuditError as exc:
            assert "no distinct alternative scale set" in str(exc)
        else:
            raise AssertionError("duplicate scale sets must fail closed")


if __name__ == "__main__":
    test_happy_path()
    test_matrix_mutation_is_rejected()
    test_input_hash_chain_mutation_is_rejected()
    test_nonmonotonic_local_linearity_is_inconclusive()
    test_scale_sensitive_rank_is_inconclusive()
    test_scale_contract_requires_distinct_predeclared_alternative()
    print("SIM-70 response-rank evidence auditor v1.5 adversarial QA: PASS (NO PHYSICAL EXECUTION)")
