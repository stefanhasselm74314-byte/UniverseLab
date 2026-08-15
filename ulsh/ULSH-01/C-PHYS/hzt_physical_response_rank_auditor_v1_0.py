#!/usr/bin/env python3
"""ULSH-01 / C-PHYS physical response-rank auditor v1.0.

Consumes three CSV Jacobians R(h), R(h/2), R(h/4), plus explicit
control/output scales. The audit is performed on the dimensionless matrix

    J = Sy^{-1} R Sc.

This tool does NOT run the nonlinear BVP and does NOT promote K1-D/K1-E.
It distinguishes PASS, BLOCKED, and INCONCLUSIVE.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import List, Tuple

import numpy as np


def read_matrix(path: str) -> Tuple[List[str], List[str], np.ndarray]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if len(rows) < 2 or len(rows[0]) < 2:
        raise ValueError(f"Invalid matrix CSV: {path}")
    controls = [x.strip() for x in rows[0][1:]]
    outputs, data = [], []
    for row in rows[1:]:
        if len(row) != len(controls) + 1:
            raise ValueError(f"Row width mismatch in {path}: {row}")
        outputs.append(row[0].strip())
        vals = []
        for x in row[1:]:
            if x.strip() == "":
                raise ValueError(f"Blank matrix cell in {path}; BVP derivative missing.")
            vals.append(float(x))
        data.append(vals)
    return outputs, controls, np.asarray(data, dtype=float)


def read_scales(path: str, controls: List[str], outputs: List[str]) -> Tuple[np.ndarray, np.ndarray, dict]:
    with open(path, encoding="utf-8") as f:
        obj = json.load(f)
    c_map = obj.get("control_scales", {})
    y_map = obj.get("output_scales", {})
    missing_c = [c for c in controls if c not in c_map]
    missing_y = [y for y in outputs if y not in y_map]
    if missing_c or missing_y:
        raise ValueError(f"Missing scales: controls={missing_c}, outputs={missing_y}")
    sc = np.asarray([float(c_map[c]) for c in controls])
    sy = np.asarray([float(y_map[y]) for y in outputs])
    if np.any(~np.isfinite(sc)) or np.any(~np.isfinite(sy)) or np.any(sc <= 0) or np.any(sy <= 0):
        raise ValueError("All scales must be finite and strictly positive.")
    return sc, sy, obj


def normalized_jacobian(R: np.ndarray, sc: np.ndarray, sy: np.ndarray) -> np.ndarray:
    return (R * sc[np.newaxis, :]) / sy[:, np.newaxis]


def svd_info(J: np.ndarray) -> dict:
    U, s, Vt = np.linalg.svd(J, full_matrices=True)
    if len(s) == 0:
        return {"singular_values": [], "condition_number": float("inf"), "U": U, "Vt": Vt}
    cond = float(s[0] / s[-1]) if s[-1] > 0 else float("inf")
    return {"singular_values": s, "condition_number": cond, "U": U, "Vt": Vt}


def principal_angle_deg(v: np.ndarray, w: np.ndarray) -> float:
    v = np.asarray(v, dtype=float)
    w = np.asarray(w, dtype=float)
    nv, nw = np.linalg.norm(v), np.linalg.norm(w)
    if nv == 0 or nw == 0:
        return float("nan")
    # singular vectors have arbitrary sign
    cosang = abs(float(np.dot(v, w) / (nv * nw)))
    cosang = min(1.0, max(-1.0, cosang))
    return float(np.degrees(np.arccos(cosang)))


def relative_matrix_change(A: np.ndarray, B: np.ndarray) -> float:
    return float(np.linalg.norm(A - B, ord=2) / max(1.0, np.linalg.norm(B, ord=2)))


def richardson_ratio(Jh: np.ndarray, Jh2: np.ndarray, Jh4: np.ndarray) -> float:
    num = np.linalg.norm(Jh - Jh2, ord=2)
    den = np.linalg.norm(Jh2 - Jh4, ord=2)
    return float(num / den) if den > 0 else float("inf") if num > 0 else 4.0


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("matrix_h", help="CSV response matrix at h")
    p.add_argument("matrix_h2", help="CSV response matrix at h/2")
    p.add_argument("matrix_h4", help="CSV response matrix at h/4")
    p.add_argument("scales_json", help="Frozen control/output scales")
    p.add_argument("--q", type=float, default=5.0, help="sigma_min uncertainty separation factor")
    p.add_argument("--cond-max", type=float, default=1e6)
    p.add_argument("--deriv-rel-max", type=float, default=1e-2)
    p.add_argument("--angle-max-deg", type=float, default=10.0)
    p.add_argument("--formal-rel-tol", type=float, default=1e-8,
                   help="historical formal SVD threshold; diagnostic only")
    p.add_argument("--branch-ok", action="store_true",
                   help="assert external branch-continuity/physics gates passed")
    p.add_argument("--solver-refinement-epsilon", type=float, default=None,
                   help="optional spectral-norm Jacobian uncertainty from stricter BVP tolerance")
    p.add_argument("--output", default=None, help="write JSON audit here")
    a = p.parse_args()

    oh, ch, Rh = read_matrix(a.matrix_h)
    oh2, ch2, Rh2 = read_matrix(a.matrix_h2)
    oh4, ch4, Rh4 = read_matrix(a.matrix_h4)
    if (oh, ch) != (oh2, ch2) or (oh, ch) != (oh4, ch4):
        raise ValueError("Matrix labels/order differ across step sizes.")
    if Rh.shape[0] != 4:
        raise ValueError(f"ULSH-01 gate expects four target rows; got {Rh.shape}.")

    sc, sy, scale_meta = read_scales(a.scales_json, ch, oh)
    Jh = normalized_jacobian(Rh, sc, sy)
    Jh2 = normalized_jacobian(Rh2, sc, sy)
    Jh4 = normalized_jacobian(Rh4, sc, sy)

    info_h = svd_info(Jh)
    info_h2 = svd_info(Jh2)
    info_h4 = svd_info(Jh4)

    # Step-refinement uncertainty: conservative spectral distance between the two finest matrices.
    eps_step = float(np.linalg.norm(Jh2 - Jh4, ord=2))
    eps_solver = float(a.solver_refinement_epsilon or 0.0)
    # Conservative additive bound; avoids assuming statistical independence.
    eps_J = eps_step + eps_solver

    s = info_h4["singular_values"]
    sigma_max = float(s[0]) if len(s) else 0.0
    sigma_min = float(s[-1]) if len(s) else 0.0
    formal_threshold = a.formal_rel_tol * sigma_max
    formal_rank = int(np.sum(s > formal_threshold))

    separation = float(sigma_min / eps_J) if eps_J > 0 else float("inf") if sigma_min > 0 else 0.0
    deriv_rel = relative_matrix_change(Jh2, Jh4)
    rr = richardson_ratio(Jh, Jh2, Jh4)

    vmin_h2 = info_h2["Vt"][-1, :]
    vmin_h4 = info_h4["Vt"][-1, :]
    angle = principal_angle_deg(vmin_h2, vmin_h4)

    convergence_ok = deriv_rel <= a.deriv_rel_max
    rank_separated = formal_rank == 4 and sigma_min > a.q * eps_J
    cond_ok = info_h4["condition_number"] <= a.cond_max
    direction_ok = np.isfinite(angle) and angle <= a.angle_max_deg

    if not a.branch_ok:
        verdict = "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT"
        reason = "External branch-continuity/physics gates not asserted."
    elif not convergence_ok:
        verdict = "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT"
        reason = "Jacobian did not reach required step-refinement convergence."
    elif formal_rank < 4 and sigma_min <= a.q * eps_J:
        verdict = "PHYSICAL_RESPONSE_RANK_DEFICIENT"
        reason = "Converged normalized Jacobian is robustly rank-deficient at the tested benchmark."
    elif not rank_separated:
        verdict = "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT"
        reason = "Smallest singular value is not separated from empirical Jacobian uncertainty."
    elif not cond_ok:
        verdict = "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT"
        reason = "Full rank is formal but conditioning exceeds the frozen guardrail."
    elif not direction_ok:
        verdict = "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT"
        reason = "Smallest right-singular direction is unstable under refinement."
    else:
        verdict = "PHYSICAL_RESPONSE_RANK_4_CONFIRMED"
        reason = "All numerical response-rank conditions passed; downstream physics gates remain separate."

    result = {
        "schema": "ulsh01.cphys.response-rank.audit.v1",
        "status": "NUMERICAL_AUDIT_ONLY",
        "governance": {"K1-D": "NOT_RELEASED", "K1-E": "NOT_ADMISSIBLE"},
        "outputs": oh,
        "controls": ch,
        "shape": list(Jh4.shape),
        "normalization": {
            "formula": "J = Sy^{-1} R Sc",
            "control_scales": {k: float(v) for k, v in zip(ch, sc)},
            "output_scales": {k: float(v) for k, v in zip(oh, sy)},
            "metadata": scale_meta,
        },
        "step_refinement": {
            "relative_change_h2_to_h4": deriv_rel,
            "required_max": a.deriv_rel_max,
            "richardson_difference_ratio_expected_about_4": rr,
            "epsilon_step_spectral": eps_step,
            "epsilon_solver_spectral": eps_solver,
            "epsilon_J_conservative": eps_J,
        },
        "svd_finest": {
            "singular_values": [float(x) for x in s],
            "formal_relative_threshold": formal_threshold,
            "formal_rank": formal_rank,
            "condition_number": float(info_h4["condition_number"]),
            "condition_number_max": a.cond_max,
            "sigma_min_over_epsilon_J": separation,
            "required_separation_q": a.q,
            "smallest_right_singular_direction": [float(x) for x in vmin_h4],
            "smallest_direction_angle_h2_h4_deg": angle,
            "angle_max_deg": a.angle_max_deg,
            "left_nullspace_dimension_formal": int(Jh4.shape[0] - formal_rank),
            "left_nullspace": info_h4["U"][:, formal_rank:].tolist(),
        },
        "gates": {
            "branch_and_physics_external_ok": bool(a.branch_ok),
            "derivative_convergence_ok": bool(convergence_ok),
            "rank4_uncertainty_separated": bool(rank_separated),
            "conditioning_ok": bool(cond_ok),
            "smallest_direction_stable": bool(direction_ok),
        },
        "verdict": verdict,
        "reason": reason,
        "evidence_effect": "NONE_BEYOND_ULSH01_NUMERICAL_GATE",
    }

    text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
    if a.output:
        Path(a.output).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
