#!/usr/bin/env python3
"""Preregistered symmetric predictor-only residual-order test for C1-V G1.1.

The program evaluates X_pred(delta)=X0+delta*X'(0) without a nonlinear
corrector. It is a discrete verification diagnostic only. It does not compute
or authorize a nonlinear branch, continuum theorem, stability result, physical
background, K1-D transition, or K1-E transition.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import pathlib
import statistics
import sys
from dataclasses import replace
from typing import Any, Callable, Iterable, Sequence

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registry" / "2026-08-03_HZT_M0_S6_C1_V_G1_1_SymmetricPredictorContract_v0.1.json"
REFERENCE_PATH = ROOT / "tools" / "2026-08-03_md2s_c1_dimensionless_jacobian_v0.1.py"
INDEPENDENT_PATH = ROOT / "tools" / "2026-08-03_md2s_c1_independent_backend_continuation_v0.1.py"


class ContractError(RuntimeError):
    """Raised when the preregistered diagnostic contract is violated."""


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ContractError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_contract() -> dict[str, Any]:
    if not CONTRACT_PATH.is_file():
        raise ContractError(f"missing preregistration contract: {CONTRACT_PATH}")
    data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if data.get("status") != "PREREGISTERED_NOT_EXECUTED":
        raise ContractError("G1.1 contract must remain the immutable preregistration record")
    if data.get("track_id") != "HZT-M0-S6-C1-V":
        raise ContractError("unexpected track identifier")
    if data.get("block") != "G1.1":
        raise ContractError("unexpected block identifier")
    if data["predictor"].get("nonlinear_corrector") is not False:
        raise ContractError("nonlinear corrector is forbidden")
    return data


def canonical_json_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def file_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm_inf(values: Iterable[float]) -> float:
    return max(abs(float(value)) for value in values)


def norm_l2(values: Iterable[float]) -> float:
    return math.sqrt(sum(float(value) ** 2 for value in values))


def relative_difference(left: float, right: float, floor: float = 1.0e-300) -> float:
    return abs(left - right) / max(0.5 * (abs(left) + abs(right)), floor)


def loglog_slope(magnitudes: Sequence[float], norms: Sequence[float]) -> float:
    if len(magnitudes) != len(norms) or len(magnitudes) < 2:
        raise ContractError("log-log fit requires matching vectors with at least two points")
    if any(value <= 0.0 for value in magnitudes) or any(value <= 0.0 for value in norms):
        raise ContractError("log-log fit requires strictly positive inputs")
    x = [math.log(value) for value in magnitudes]
    y = [math.log(value) for value in norms]
    x_mean = statistics.fmean(x)
    y_mean = statistics.fmean(y)
    denominator = sum((value - x_mean) ** 2 for value in x)
    if denominator == 0.0:
        raise ContractError("degenerate log-log fit window")
    return sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y)) / denominator


def predictor(anchor: Sequence[float], tangent: Sequence[float], delta: float) -> list[float]:
    if len(anchor) != len(tangent):
        raise ContractError("anchor and tangent dimensions differ")
    return [float(value) + delta * float(direction) for value, direction in zip(anchor, tangent)]


def check_between(value: float, corridor: Sequence[float]) -> bool:
    return float(corridor[0]) <= value <= float(corridor[1])


def group_records(
    records: Sequence[dict[str, Any]],
    backend: str,
    resolution: int,
    sign: int,
) -> dict[float, dict[str, Any]]:
    selected = {
        float(record["magnitude"]): record
        for record in records
        if record["backend"] == backend
        and int(record["resolution"]) == resolution
        and int(record["sign"]) == sign
    }
    return selected


def run_registered_test() -> dict[str, Any]:
    contract = load_contract()
    reference = load_module("c1_v_g1_1_reference", REFERENCE_PATH)
    independent = load_module("c1_v_g1_1_independent", INDEPENDENT_PATH)

    anchor = [float(value) for value in independent.ANCHOR_VECTOR]
    tangent_report = independent.continuation_tangent_report(base_steps=100)
    reference_tangent = [float(value) for value in tangent_report["reference_tangent"]]
    independent_tangent = [float(value) for value in tangent_report["independent_tangent"]]

    corridors = contract["acceptance_corridor"]
    tangent_checks = {
        "relative_tangent_difference": float(tangent_report["tangent_relative_difference"]),
        "relative_tangent_difference_pass": float(tangent_report["tangent_relative_difference"])
        <= float(corridors["tangent_relative_difference_maximum"]),
        "linear_closure_infinity_norm": float(tangent_report["linear_closure_infinity_norm"]),
        "linear_closure_pass": float(tangent_report["linear_closure_infinity_norm"])
        <= float(corridors["linear_closure_infinity_norm_maximum"]),
    }

    evaluators: dict[str, tuple[Sequence[int], Sequence[float], Callable[[Sequence[float], float, int], list[float]]]] = {}

    def evaluate_reference(vector: Sequence[float], delta: float, steps: int) -> list[float]:
        parameters = replace(reference.DEFAULT_PARAMETERS, lambda0=float(delta))
        residuals = reference.normalized_residuals(vector, parameters, steps=steps)
        return [float(reference.scalar_value(value)) for value in residuals]

    def evaluate_independent(vector: Sequence[float], delta: float, base_steps: int) -> list[float]:
        parameters = replace(independent.DEFAULT_PARAMETERS, lambda0=float(delta))
        residuals = independent.normalized_residuals_independent(
            vector,
            parameters,
            base_steps=base_steps,
        )
        return [float(value) for value in residuals]

    evaluators["reference"] = (
        [int(value) for value in contract["backends"]["reference"]["steps"]],
        reference_tangent,
        evaluate_reference,
    )
    evaluators["independent"] = (
        [int(value) for value in contract["backends"]["independent"]["base_steps"]],
        independent_tangent,
        evaluate_independent,
    )

    absolute_floor = 1.0e-13
    separation_factor = float(contract["numerical_floor"]["asymptotic_separation_factor"])
    anchor_floors: dict[str, dict[str, float]] = {}
    records: list[dict[str, Any]] = []

    for backend_name, (resolutions, tangent, evaluator) in evaluators.items():
        anchor_floors[backend_name] = {}
        for resolution in resolutions:
            anchor_residuals = evaluator(anchor, 0.0, resolution)
            anchor_norm = norm_inf(anchor_residuals)
            floor = max(anchor_norm, absolute_floor)
            anchor_floors[backend_name][str(resolution)] = floor
            for magnitude in [float(value) for value in contract["symmetric_step_magnitudes"]]:
                for sign in (-1, 1):
                    delta = sign * magnitude
                    vector = predictor(anchor, tangent, delta)
                    residuals = evaluator(vector, delta, resolution)
                    primary = norm_inf(residuals)
                    records.append(
                        {
                            "backend": backend_name,
                            "resolution": resolution,
                            "sign": sign,
                            "magnitude": magnitude,
                            "delta": delta,
                            "residual_infinity_norm": primary,
                            "residual_l2_norm": norm_l2(residuals),
                            "floor": floor,
                            "floor_separation": primary / floor,
                            "fit_eligible": primary >= separation_factor * floor,
                            "normalized_residual_vector": residuals,
                        }
                    )

    fit_magnitudes = [float(value) for value in contract["windows"]["asymptotic_fit"]]
    analyses: list[dict[str, Any]] = []
    analysis_checks: list[bool] = []
    for backend_name, (resolutions, _tangent, _evaluator) in evaluators.items():
        for resolution in resolutions:
            for sign in (-1, 1):
                selected = group_records(records, backend_name, resolution, sign)
                fit_records = [selected[magnitude] for magnitude in fit_magnitudes]
                eligible = all(record["fit_eligible"] for record in fit_records)
                norms = [float(record["residual_infinity_norm"]) for record in fit_records]
                slope = loglog_slope(fit_magnitudes, norms)
                ratios = [norms[index] / norms[index + 1] for index in range(len(norms) - 1)]
                slope_pass = check_between(slope, corridors["loglog_slope"])
                ratios_pass = all(
                    check_between(value, corridors["halving_ratio_R_delta_over_R_half_delta"])
                    for value in ratios
                )
                minimum_points_pass = len(fit_records) >= int(
                    corridors["minimum_consecutive_fit_magnitudes"]
                )
                passed = eligible and slope_pass and ratios_pass and minimum_points_pass
                analysis_checks.append(passed)
                analyses.append(
                    {
                        "backend": backend_name,
                        "resolution": resolution,
                        "sign": sign,
                        "fit_magnitudes": fit_magnitudes,
                        "fit_norms": norms,
                        "slope": slope,
                        "halving_ratios": ratios,
                        "all_fit_points_above_floor": eligible,
                        "slope_pass": slope_pass,
                        "ratios_pass": ratios_pass,
                        "minimum_points_pass": minimum_points_pass,
                        "pass": passed,
                    }
                )

    signed_pair_checks: list[dict[str, Any]] = []
    for backend_name, (resolutions, _tangent, _evaluator) in evaluators.items():
        for resolution in resolutions:
            positive = group_records(records, backend_name, resolution, 1)
            negative = group_records(records, backend_name, resolution, -1)
            values = {
                str(magnitude): relative_difference(
                    float(positive[magnitude]["residual_infinity_norm"]),
                    float(negative[magnitude]["residual_infinity_norm"]),
                    max(float(positive[magnitude]["floor"]), float(negative[magnitude]["floor"])),
                )
                for magnitude in fit_magnitudes
            }
            maximum = max(values.values())
            signed_pair_checks.append(
                {
                    "backend": backend_name,
                    "resolution": resolution,
                    "relative_asymmetry_by_magnitude": values,
                    "maximum": maximum,
                    "pass": maximum
                    <= float(corridors["maximum_signed_pair_relative_asymmetry"]),
                }
            )

    resolution_checks: list[dict[str, Any]] = []
    for backend_name, (resolutions, _tangent, _evaluator) in evaluators.items():
        if len(resolutions) != 2:
            raise ContractError("G1.1 preregistration requires exactly two resolutions per backend")
        coarse, fine = resolutions
        for sign in (-1, 1):
            coarse_records = group_records(records, backend_name, coarse, sign)
            fine_records = group_records(records, backend_name, fine, sign)
            values = {
                str(magnitude): relative_difference(
                    float(coarse_records[magnitude]["residual_infinity_norm"]),
                    float(fine_records[magnitude]["residual_infinity_norm"]),
                    max(float(coarse_records[magnitude]["floor"]), float(fine_records[magnitude]["floor"])),
                )
                for magnitude in fit_magnitudes
            }
            maximum = max(values.values())
            resolution_checks.append(
                {
                    "backend": backend_name,
                    "sign": sign,
                    "coarse_resolution": coarse,
                    "fine_resolution": fine,
                    "relative_difference_by_magnitude": values,
                    "maximum": maximum,
                    "pass": maximum
                    <= float(corridors["maximum_same_backend_resolution_relative_difference"]),
                }
            )

    reference_fine = max(evaluators["reference"][0])
    independent_fine = max(evaluators["independent"][0])
    backend_checks: list[dict[str, Any]] = []
    for sign in (-1, 1):
        reference_records = group_records(records, "reference", reference_fine, sign)
        independent_records = group_records(records, "independent", independent_fine, sign)
        values = {
            str(magnitude): relative_difference(
                float(reference_records[magnitude]["residual_infinity_norm"]),
                float(independent_records[magnitude]["residual_infinity_norm"]),
                max(float(reference_records[magnitude]["floor"]), float(independent_records[magnitude]["floor"])),
            )
            for magnitude in fit_magnitudes
        }
        maximum = max(values.values())
        backend_checks.append(
            {
                "sign": sign,
                "reference_steps": reference_fine,
                "independent_base_steps": independent_fine,
                "relative_difference_by_magnitude": values,
                "maximum": maximum,
                "pass": maximum <= float(corridors["maximum_fine_backend_relative_difference"]),
            }
        )

    regime_report: dict[str, Any] = {}
    for backend_name, (resolutions, _tangent, _evaluator) in evaluators.items():
        fine = max(resolutions)
        regime_report[backend_name] = {}
        for sign in (-1, 1):
            selected = group_records(records, backend_name, fine, sign)
            regime_report[backend_name][str(sign)] = {
                "large_step_probe": {
                    str(value): selected[float(value)]["residual_infinity_norm"]
                    for value in contract["windows"]["large_step_probe"]
                },
                "quadratic_fit_window": {
                    str(value): selected[float(value)]["residual_infinity_norm"]
                    for value in contract["windows"]["asymptotic_fit"]
                },
                "small_step_floor_probe": {
                    str(value): {
                        "residual_infinity_norm": selected[float(value)]["residual_infinity_norm"],
                        "floor_separation": selected[float(value)]["floor_separation"],
                    }
                    for value in contract["windows"]["small_step_floor_probe"]
                },
            }

    checks = {
        "tangent_agreement": tangent_checks["relative_tangent_difference_pass"],
        "linear_closure": tangent_checks["linear_closure_pass"],
        "all_registered_sign_resolution_fits": all(analysis_checks),
        "signed_pair_symmetry": all(item["pass"] for item in signed_pair_checks),
        "same_backend_resolution_agreement": all(item["pass"] for item in resolution_checks),
        "fine_backend_agreement": all(item["pass"] for item in backend_checks),
        "predictor_only": True,
        "nonlinear_corrector_absent": True,
        "second_derivative_absent": True,
    }
    passed = all(checks.values())

    return {
        "schema": "universelab.hzt-m0-s6-c1-v.g1-1-symmetric-predictor-run.v0.1",
        "date": "2026-08-03",
        "run_id": contract["run_id"],
        "track_id": "HZT-M0-S6-C1-V",
        "model_id": "HZT-M0-S6-C1-V",
        "classification": "MANUFACTURED_VERIFICATION_MODEL",
        "block": "G1.1",
        "phase": "C1-V3",
        "status": "PASS_DIAGNOSTIC" if passed else "FAIL_DIAGNOSTIC",
        "result_status": "NUMERICALLY_CONFIRMED" if passed else "OPEN",
        "qualifier": "DIAGNOSTIC",
        "preregistration_hash": canonical_json_hash(contract),
        "code_hash": file_hash(pathlib.Path(__file__)),
        "reference_code_hash": file_hash(REFERENCE_PATH),
        "independent_code_hash": file_hash(INDEPENDENT_PATH),
        "parameter_hash": contract["parameter_hash"],
        "anchor_vector": anchor,
        "reference_tangent": reference_tangent,
        "independent_tangent": independent_tangent,
        "tangent_checks": tangent_checks,
        "anchor_floors": anchor_floors,
        "evaluations": records,
        "fit_analyses": analyses,
        "signed_pair_checks": signed_pair_checks,
        "resolution_checks": resolution_checks,
        "backend_checks": backend_checks,
        "regime_report": regime_report,
        "checks": checks,
        "evidence_effect": "DISCRETE_PREDICTOR_QA_ONLY",
        "physical_evidence_effect": "NONE",
        "validity_regime": [
            "declared C1-V manufactured model and anchor",
            "registered lambda0_hat predictor",
            "registered symmetric steps and fixed fit window",
            "declared normalized residual chart",
            "tested finite RK4 and implicit-midpoint/Richardson discretizations"
        ],
        "forbidden_inference": contract["forbidden_inference"],
        "gate_state": {
            "G1.1": "PASS_DIAGNOSTIC" if passed else "FAIL_DIAGNOSTIC",
            "C1-V3": "PARTIAL",
            "C1-V4": "NOT_STARTED",
            "nonlinear_solution_family": "NOT_ESTABLISHED",
            "continuum_BVP_Jacobian": "NOT_PROVEN",
            "perturbative_stability": "OPEN",
            "ghost_freedom": "OPEN",
            "R1.1": "BLOCKED",
            "official_MD2S_solver": "NOT_AUTHORIZED",
            "K1-D": "NOT_RELEASED",
            "K1-E": "NOT_ADMISSIBLE",
            "physical_evidence_effect": "NONE"
        },
        "next_gate_if_pass": "G1.2_LOCAL_SECOND_ORDER_DISCRETE_RESPONSE_DIAGNOSTIC",
        "next_gate_if_fail": "G1.1_DIAGNOSTIC_REVIEW_WITHOUT_FIT_WINDOW_SUBSTITUTION",
        "nonlinear_corrector_implemented": False,
        "root_solver_implemented": False,
        "branch_tracking_implemented": False,
        "second_derivative_computed": False
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, help="optional JSON output path")
    parser.add_argument("--compact", action="store_true", help="emit compact JSON")
    args = parser.parse_args()
    result = run_registered_test()
    text = json.dumps(
        result,
        indent=None if args.compact else 2,
        sort_keys=True,
        separators=(",", ":") if args.compact else None,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
