#!/usr/bin/env python3
"""ULSH-01/C-PHYS physical response-rank auditor v1.4.

SIM-70 hardening of v1.3:
- SVD + rank-revealing QR with column pivoting
- 4x4 minor/Cauchy-Binet corroboration for the 4x5 normalized response
- recorded-matrix precision ladder: float64 -> longdouble -> mpmath
- explicit observed finite-difference convergence order
- clustered weakest-singular-subspace stability instead of forcing a
  one-vector comparison in near-degenerate cases

Numerical gate only. It never releases K1-D/K1-E and does not establish
physical correctness, ghost freedom, continuum existence, or uniqueness.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from pathlib import Path

import mpmath as mp
import numpy as np
import scipy.linalg as sla


def read_matrix(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if len(rows) < 2 or len(rows[0]) < 2:
        raise ValueError(f"invalid matrix: {path}")
    controls = [x.strip() for x in rows[0][1:]]
    outputs, values = [], []
    for row in rows[1:]:
        if len(row) != len(controls) + 1 or any(not x.strip() for x in row[1:]):
            raise ValueError(f"invalid row: {path}")
        outputs.append(row[0].strip())
        values.append([float(x) for x in row[1:]])
    matrix = np.asarray(values, dtype=float)
    if np.any(~np.isfinite(matrix)):
        raise ValueError(f"non-finite matrix: {path}")
    return outputs, controls, matrix


def scales(path, controls, outputs):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    control_map = data.get("control_scales", {})
    output_map = data.get("output_scales", {})
    if any(key not in control_map for key in controls) or any(key not in output_map for key in outputs):
        raise ValueError("scale coverage incomplete")
    sc = np.array([float(control_map[key]) for key in controls], dtype=float)
    sy = np.array([float(output_map[key]) for key in outputs], dtype=float)
    if np.any(~np.isfinite(sc)) or np.any(~np.isfinite(sy)) or np.any(sc <= 0) or np.any(sy <= 0):
        raise ValueError("scales must be finite and >0")
    return sc, sy, data


def normalized_jacobian(response, sc, sy):
    return (response * sc[None, :]) / sy[:, None]


def svd_decomp(matrix):
    U, singular_values, Vh = np.linalg.svd(matrix, full_matrices=False)
    condition = (
        float(singular_values[0] / singular_values[-1])
        if singular_values[-1] > 0
        else math.inf
    )
    return U, singular_values, Vh, condition


def rrqr_diagnostics(matrix, rel_tol):
    _, R, pivots = sla.qr(matrix, mode="economic", pivoting=True)
    diagonal = np.abs(np.diag(R))
    scale = float(diagonal[0]) if diagonal.size else 0.0
    threshold = rel_tol * scale
    rank = int(np.count_nonzero(diagonal > threshold)) if scale > 0 else 0
    return {
        "rank": rank,
        "pivot_order": [int(v) for v in pivots],
        "diag_abs": [float(v) for v in diagonal],
        "threshold": float(threshold),
    }


def all_full_row_minors(matrix):
    rows, cols = matrix.shape
    if rows > cols:
        raise ValueError("full-row minors require rows <= columns")
    records = []
    for columns in itertools.combinations(range(cols), rows):
        sub = matrix[:, columns]
        sign, logabs = np.linalg.slogdet(sub)
        det = 0.0 if sign == 0 else float(sign * np.exp(logabs))
        records.append({"columns": list(columns), "determinant": det})
    return records


def minor_diagnostics(matrix, formal_rel_tol):
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    sigmax = float(singular_values[0]) if singular_values.size else 0.0
    records = all_full_row_minors(matrix)
    determinants = np.asarray([item["determinant"] for item in records], dtype=float)
    energy = float(np.linalg.norm(determinants))
    singular_product = float(np.prod(singular_values)) if singular_values.size else 0.0
    threshold = (formal_rel_tol * sigmax) ** matrix.shape[0] if sigmax > 0 else 0.0
    consistency = abs(energy - singular_product) / max(abs(singular_product), abs(energy), 1.0e-300)
    return {
        "records": records,
        "minor_energy": energy,
        "singular_value_product": singular_product,
        "cauchy_binet_relative_mismatch": float(consistency),
        "support_threshold": float(threshold),
        "rank4_support": bool(energy > threshold),
    }


def det_longdouble(square):
    a = np.asarray(square, dtype=np.longdouble).copy()
    n = a.shape[0]
    if a.shape != (n, n):
        raise ValueError("det_longdouble expects square matrix")
    sign = np.longdouble(1)
    det = np.longdouble(1)
    for k in range(n):
        pivot = k + int(np.argmax(np.abs(a[k:, k])))
        pivot_value = a[pivot, k]
        if pivot_value == 0:
            return np.longdouble(0)
        if pivot != k:
            a[[k, pivot]] = a[[pivot, k]]
            sign = -sign
        pivot_value = a[k, k]
        det *= pivot_value
        if k + 1 < n:
            factors = a[k + 1 :, k] / pivot_value
            a[k + 1 :, k + 1 :] -= factors[:, None] * a[k, k + 1 :]
    return sign * det


def precision_ladder(matrix, formal_rel_tol, mp_dps=80):
    rows, cols = matrix.shape
    if rows != 4 or cols < 4:
        return {
            "status": "NOT_APPLICABLE_SHAPE",
            "float64": None,
            "longdouble": None,
            "mpmath": None,
        }

    s = np.linalg.svd(matrix, compute_uv=False)
    sigmax = float(s[0]) if s.size else 0.0
    threshold = (formal_rel_tol * sigmax) ** rows if sigmax > 0 else 0.0

    float_records = all_full_row_minors(matrix)
    float_max = max((abs(item["determinant"]) for item in float_records), default=0.0)

    ld_values = []
    for columns in itertools.combinations(range(cols), rows):
        ld_values.append(abs(det_longdouble(np.asarray(matrix[:, columns], dtype=np.longdouble))))
    ld_max = max(ld_values, default=np.longdouble(0))

    with mp.workdps(int(mp_dps)):
        mp_values = []
        for columns in itertools.combinations(range(cols), rows):
            sub = mp.matrix(
                [[mp.mpf(repr(float(matrix[i, j]))) for j in columns] for i in range(rows)]
            )
            mp_values.append(abs(mp.det(sub)))
        mp_max = max(mp_values) if mp_values else mp.mpf("0")
        mp_threshold = mp.mpf(repr(float(threshold)))
        mp_support = bool(mp_max > mp_threshold)

    return {
        "status": "RECORDED_MATRIX_ANALYSIS_ONLY",
        "note": "Higher arithmetic precision is applied to the recorded matrix; it does not replace a higher-precision solver rerun.",
        "support_threshold_from_float64_svd": float(threshold),
        "float64": {
            "max_abs_minor": float(float_max),
            "rank4_support": bool(float_max > threshold),
        },
        "longdouble": {
            "mantissa_bits": int(np.finfo(np.longdouble).nmant),
            "max_abs_minor": str(ld_max),
            "rank4_support": bool(ld_max > np.longdouble(threshold)),
        },
        "mpmath": {
            "decimal_digits": int(mp_dps),
            "max_abs_minor": mp.nstr(mp_max, 30),
            "rank4_support": mp_support,
        },
    }


def observed_order(d1, d2):
    if d1 <= 0 or d2 <= 0:
        return None
    value = math.log(d1 / d2, 2.0)
    return float(value) if math.isfinite(value) else None


def weakest_cluster_dimension(singular_values, gap_ratio):
    s = np.asarray(singular_values, dtype=float)
    if s.ndim != 1 or not len(s):
        return 0
    k = 1
    weakest = max(float(s[-1]), 0.0)
    if weakest == 0.0:
        while k < len(s) and float(s[-k - 1]) == 0.0:
            k += 1
        return k
    while k < len(s):
        adjacent = float(s[-k - 1])
        if adjacent / weakest <= gap_ratio:
            k += 1
        else:
            break
    return k


def principal_angle_max_deg(Vh_left, Vh_right, dimension):
    if dimension <= 0:
        return None
    left = np.asarray(Vh_left[-dimension:, :], dtype=float)
    right = np.asarray(Vh_right[-dimension:, :], dtype=float)
    overlap_s = np.linalg.svd(left @ right.T, compute_uv=False)
    cosines = np.clip(overlap_s, -1.0, 1.0)
    angles = np.degrees(np.arccos(cosines))
    return float(np.max(angles)) if len(angles) else 0.0


def clean(value):
    if isinstance(value, dict):
        return {key: clean(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(child) for child in value]
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, np.integer):
        return int(value)
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix_h")
    parser.add_argument("matrix_h2")
    parser.add_argument("matrix_h4")
    parser.add_argument("scales_json")
    parser.add_argument("--matrix-h4-refined")
    parser.add_argument("--solver-refinement-epsilon", type=float, default=None)
    parser.add_argument("--run-manifest", required=True)
    parser.add_argument("--q", type=float, default=5.0)
    parser.add_argument("--cond-max", type=float, default=1e6)
    parser.add_argument("--deriv-rel-max", type=float, default=1e-2)
    parser.add_argument("--angle-max-deg", type=float, default=10.0)
    parser.add_argument("--formal-rel-tol", type=float, default=1e-8)
    parser.add_argument("--cluster-gap-ratio", type=float, default=1.5)
    parser.add_argument("--mp-dps", type=int, default=80)
    parser.add_argument("--branch-ok", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    outputs, controls, R = read_matrix(args.matrix_h)
    outputs2, controls2, R2 = read_matrix(args.matrix_h2)
    outputs4, controls4, R4 = read_matrix(args.matrix_h4)
    if (outputs, controls) != (outputs2, controls2) or (outputs, controls) != (outputs4, controls4):
        raise ValueError("labels/order differ")
    if R4.shape[0] != 4 or R4.shape[1] < 4:
        raise ValueError(f"response shape not gate-eligible: {R4.shape}")

    sc, sy, scale_metadata = scales(args.scales_json, controls, outputs)
    manifest = json.loads(Path(args.run_manifest).read_text(encoding="utf-8"))
    evidence_eligible = (
        bool(manifest.get("rank_claim_allowed", False))
        and manifest.get("evidence_effect") == "ELIGIBLE_FOR_INDEPENDENT_RANK_AUDIT_ONLY"
        and not manifest.get("synthetic_jobs", [])
    )

    j, j2, j4 = [normalized_jacobian(x, sc, sy) for x in (R, R2, R4)]
    _, s2, Vh2, _ = svd_decomp(j2)
    _, s4, Vh4, k4 = svd_decomp(j4)

    eps_step = float(np.linalg.norm(j2 - j4, 2))
    eps_solver = 0.0
    solver_source = "none"
    if args.matrix_h4_refined:
        outputs_ref, controls_ref, Rref = read_matrix(args.matrix_h4_refined)
        if (outputs_ref, controls_ref) != (outputs, controls):
            raise ValueError("refined matrix labels/order differ")
        eps_solver = float(np.linalg.norm(j4 - normalized_jacobian(Rref, sc, sy), 2))
        solver_source = "matrix_h4_refined"
    elif args.solver_refinement_epsilon is not None:
        eps_solver = max(0.0, float(args.solver_refinement_epsilon))
        solver_source = "explicit_scalar"

    epsJ = eps_step + eps_solver
    norm_j4 = float(np.linalg.norm(j4, 2))
    relative_change = eps_step / max(1.0, norm_j4)
    d1 = float(np.linalg.norm(j - j2, 2))
    d2 = eps_step
    richardson_ratio = d1 / d2 if d2 > 0 else (4.0 if d1 == 0 else math.inf)
    p_observed = observed_order(d1, d2)

    sigmax = float(s4[0])
    sigmin = float(s4[-1])
    threshold = args.formal_rel_tol * sigmax
    svd_rank = int(np.sum(s4 > threshold))
    separation = sigmin / epsJ if epsJ > 0 else (math.inf if sigmin > 0 else 0.0)

    rrqr = rrqr_diagnostics(j4, args.formal_rel_tol)
    minors = minor_diagnostics(j4, args.formal_rel_tol)
    precision = precision_ladder(j4, args.formal_rel_tol, args.mp_dps)

    cluster_dim = max(
        weakest_cluster_dimension(s2, args.cluster_gap_ratio),
        weakest_cluster_dimension(s4, args.cluster_gap_ratio),
    )
    subspace_angle = principal_angle_max_deg(Vh2, Vh4, cluster_dim)

    convergence_ok = relative_change <= args.deriv_rel_max
    separated = svd_rank == 4 and sigmin > args.q * epsJ
    conditioning_ok = k4 <= args.cond_max
    direction_ok = (
        subspace_angle is not None
        and math.isfinite(subspace_angle)
        and subspace_angle <= args.angle_max_deg
    )
    refinement_present = (
        args.matrix_h4_refined is not None or args.solver_refinement_epsilon is not None
    )

    rank4_method_support = (
        svd_rank == 4
        and rrqr["rank"] == 4
        and minors["rank4_support"]
    )
    precision_rank4_support = (
        precision["float64"]["rank4_support"]
        and precision["longdouble"]["rank4_support"]
        and precision["mpmath"]["rank4_support"]
    )
    robust_rank_deficiency = (
        svd_rank < 4
        and rrqr["rank"] < 4
        and not minors["rank4_support"]
        and sigmin <= args.q * epsJ
    )

    if not evidence_eligible:
        verdict, reason = (
            "SOFTWARE_QA_ONLY_NO_PHYSICAL_VERDICT",
            "run manifest is not eligible for physical rank adjudication",
        )
    elif not args.branch_ok:
        verdict, reason = (
            "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT",
            "external branch/physics gates not asserted",
        )
    elif not refinement_present:
        verdict, reason = (
            "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT",
            "solver-tolerance refinement missing",
        )
    elif not convergence_ok:
        verdict, reason = (
            "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT",
            "no stable step-refinement plateau",
        )
    elif robust_rank_deficiency:
        verdict, reason = (
            "PHYSICAL_RESPONSE_RANK_DEFICIENT",
            "SVD, RRQR and 4x4-minor diagnostics consistently support rank deficiency at the numerical uncertainty floor",
        )
    elif not rank4_method_support:
        verdict, reason = (
            "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT",
            "SVD/RRQR/minor rank diagnostics do not consistently support row rank 4",
        )
    elif not precision_rank4_support:
        verdict, reason = (
            "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT",
            "recorded-matrix rank-4 support is not stable across the arithmetic precision ladder",
        )
    elif not separated:
        verdict, reason = (
            "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT",
            "sigma_4 not separated from empirical Jacobian uncertainty",
        )
    elif not conditioning_ok:
        verdict, reason = (
            "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT",
            "conditioning exceeds guardrail",
        )
    elif not direction_ok:
        verdict, reason = (
            "NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT",
            "weakest singular direction/subspace unstable under refinement",
        )
    else:
        verdict, reason = (
            "PHYSICAL_RESPONSE_RANK_4_CONFIRMED",
            "ULSH-01 numerical response-rank gate passed with SVD/RRQR/minor and recorded-matrix precision corroboration",
        )

    result = {
        "schema": "ulsh01.cphys.response-rank.audit.v1.4",
        "status": "NUMERICAL_AUDIT_ONLY",
        "governance": {"K1-D": "NOT_RELEASED", "K1-E": "NOT_ADMISSIBLE"},
        "outputs": outputs,
        "controls": controls,
        "shape": list(j4.shape),
        "normalization": {
            "formula": "J=Sy^{-1}RSc",
            "control_scales": dict(zip(controls, sc)),
            "output_scales": dict(zip(outputs, sy)),
            "metadata": scale_metadata,
        },
        "refinement": {
            "relative_change_h2_h4": relative_change,
            "richardson_difference_ratio": richardson_ratio,
            "observed_order_log2_d1_over_d2": p_observed,
            "epsilon_step": eps_step,
            "epsilon_solver": eps_solver,
            "epsilon_solver_source": solver_source,
            "epsilon_J": epsJ,
        },
        "svd": {
            "singular_values": s4,
            "formal_rank": svd_rank,
            "condition_number": k4,
            "sigma_4_over_epsilon_J": separation,
        },
        "rrqr": rrqr,
        "minors_4x4": minors,
        "precision_ladder": precision,
        "weakest_subspace": {
            "cluster_gap_ratio": args.cluster_gap_ratio,
            "dimension": cluster_dim,
            "max_principal_angle_h2_h4_deg": subspace_angle,
            "single_vector_angle_used": cluster_dim == 1,
        },
        "run_manifest": {
            "rank_claim_allowed": manifest.get("rank_claim_allowed"),
            "evidence_effect": manifest.get("evidence_effect"),
            "synthetic_job_count": len(manifest.get("synthetic_jobs", [])),
            "evidence_eligible": evidence_eligible,
        },
        "gates": {
            "branch_ok": args.branch_ok,
            "solver_refinement_present": refinement_present,
            "derivative_convergence_ok": convergence_ok,
            "rank4_svd_rrqr_minor_consistent": rank4_method_support,
            "precision_rank4_support": precision_rank4_support,
            "rank4_uncertainty_separated": separated,
            "conditioning_ok": conditioning_ok,
            "weakest_direction_or_subspace_stable": direction_ok,
        },
        "verdict": verdict,
        "reason": reason,
        "physical_interpretation": "NONE",
        "canonical_effect": "NONE",
        "evidence_effect": "NONE_BEYOND_ULSH01_NUMERICAL_GATE",
    }

    text = json.dumps(clean(result), indent=2, ensure_ascii=False, allow_nan=False)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
