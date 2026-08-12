#!/usr/bin/env python3
"""AIP-LENS-01-NULL-N1 deterministic synthetic weak-lensing null-pilot execution.

Methods-only pilot. The generator is a declared toy/synthetic summary-statistic
model, not an N-body, ray-tracing, KiDS, DES, Euclid or HZT simulator.
Standard-library only.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import random
from pathlib import Path

SEEDS = {"TRAIN": 11001, "VALIDATION": 11002, "CALIBRATION": 11003, "FINAL_TEST": 11004, "OOD_STRESS": 11005}
SIZES = {"TRAIN": 512, "VALIDATION": 128, "CALIBRATION": 128, "FINAL_TEST": 256, "OOD_STRESS": 256}
TARGETS = ("Omega_m", "S8")
TRAIN_RANGE = {"Omega_m": (0.22, 0.38), "sigma8": (0.68, 0.90), "noise": (0.02, 0.06), "ia": (-0.25, 0.25)}
THRESHOLDS = {
    "abs_bias_max": {"Omega_m": 0.010, "S8": 0.010},
    "rmse_max": {"Omega_m": 0.040, "S8": 0.040},
    "ml_rmse_over_baseline_max": 1.0,
    "coverage68_min": 0.55,
    "coverage68_max": 0.82,
    "coverage95_min": 0.88,
    "coverage95_max": 1.0,
    "nuisance_abs_corr_max": 0.20,
    "ood_fpr_max": 0.05,
    "ood_tpr_min": 0.90,
    "stratified_rmse_over_global_max": 2.0,
}
CONTRACT_PATH = Path("registry/2026-08-12_UniverseLab_AIP-LENS-01-NULL-N1_ExecutionContract_v0.1.json")
PARENT_PATH = Path("registry/2026-08-12_UniverseLab_AIP-LENS-01-NULL_Contract_v0.1.json")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def generate_split(split: str):
    rng = random.Random(SEEDS[split])
    rows = []
    for i in range(SIZES[split]):
        if split == "OOD_STRESS":
            if i % 2 == 0:
                omega_m = rng.uniform(0.14, 0.20)
                sigma8 = rng.uniform(0.55, 0.65)
            else:
                omega_m = rng.uniform(0.40, 0.46)
                sigma8 = rng.uniform(0.94, 1.04)
            noise = rng.uniform(0.07, 0.12)
            ia = rng.uniform(-0.50, 0.50)
        else:
            omega_m = rng.uniform(*TRAIN_RANGE["Omega_m"])
            sigma8 = rng.uniform(*TRAIN_RANGE["sigma8"])
            noise = rng.uniform(*TRAIN_RANGE["noise"])
            ia = rng.uniform(*TRAIN_RANGE["ia"])

        s8 = sigma8 * math.sqrt(omega_m / 0.3)
        amplitude = s8**2 * (omega_m / 0.3)**0.55
        f = []
        for b, z in enumerate((0.3, 0.5, 0.7, 0.9, 1.1, 1.3)):
            growth = (1.0 + z)**(-0.8 - 0.15 * (omega_m - 0.3))
            value = amplitude * growth * (1.0 + 0.12 * ia * (b - 2.5) / 2.5)
            value += 0.18 * (omega_m - 0.3)**2 * (b + 1)
            value += 0.04 * math.sin(3.0 * s8 + b * 0.4)
            value += rng.gauss(0.0, noise * (0.08 + 0.01 * b))
            f.append(value)
        features = f + [
            f[0] / max(f[5], 1e-12),
            sum(f[:3]) / 3.0,
            sum(f[3:6]) / 3.0,
            max(f[:6]) - min(f[:6]),
            noise,
            ia,
        ]
        rows.append({
            "id": f"{split}:{i:04d}",
            "features": features,
            "targets": {"Omega_m": omega_m, "S8": s8},
            "nuisance": {"noise": noise, "ia": ia},
            "diagnostic": {"sigma8": sigma8},
        })
    return rows


def feature_stats(rows):
    p = len(rows[0]["features"])
    means, stds = [], []
    for j in range(p):
        vals = [r["features"][j] for r in rows]
        m = sum(vals) / len(vals)
        var = sum((x - m)**2 for x in vals) / (len(vals) - 1)
        means.append(m)
        stds.append(math.sqrt(var) if var > 1e-24 else 1.0)
    return means, stds


def zfeatures(x, means, stds):
    return [(x[j] - means[j]) / stds[j] for j in range(len(x))]


def baseline_map(x, means, stds):
    z = zfeatures(x, means, stds)
    return [1.0] + z[:6]


def ml_map(x, means, stds):
    z = zfeatures(x, means, stds)
    out = [1.0] + z
    out.extend(v * v for v in z)
    for i in range(10):
        for j in range(i + 1, 10):
            out.append(z[i] * z[j])
    return out


def solve_linear(a, b):
    n = len(b)
    m = [list(a[i]) + [b[i]] for i in range(n)]
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: abs(m[i][k]))
        if abs(m[pivot][k]) < 1e-12:
            raise RuntimeError("singular normal matrix")
        m[k], m[pivot] = m[pivot], m[k]
        d = m[k][k]
        for j in range(k, n + 1):
            m[k][j] /= d
        for i in range(n):
            if i == k:
                continue
            factor = m[i][k]
            if factor != 0.0:
                for j in range(k, n + 1):
                    m[i][j] -= factor * m[k][j]
    return [m[i][n] for i in range(n)]


def fit_ridge(rows, target, mapper, means, stds, lam):
    xmat = [mapper(r["features"], means, stds) for r in rows]
    y = [r["targets"][target] for r in rows]
    p = len(xmat[0])
    a = [[0.0] * p for _ in range(p)]
    b = [0.0] * p
    for x, yy in zip(xmat, y):
        for i in range(p):
            b[i] += x[i] * yy
            for j in range(p):
                a[i][j] += x[i] * x[j]
    for i in range(1, p):
        a[i][i] += lam
    return solve_linear(a, b)


def predict(weights, x, mapper, means, stds):
    phi = mapper(x, means, stds)
    return sum(w * v for w, v in zip(weights, phi))


def quantile(values, q):
    values = sorted(values)
    idx = (len(values) - 1) * q
    lo, hi = math.floor(idx), math.ceil(idx)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - idx) + values[hi] * (idx - lo)


def conformal_quantile(values, coverage):
    values = sorted(values)
    k = min(len(values) - 1, max(0, math.ceil((len(values) + 1) * coverage) - 1))
    return values[k]


def corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    da = sum((x - ma)**2 for x in a)
    db = sum((x - mb)**2 for x in b)
    if da <= 0.0 or db <= 0.0:
        return 0.0
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(da * db)


def rmse(pred, truth):
    return math.sqrt(sum((p - t)**2 for p, t in zip(pred, truth)) / len(truth))


def evaluate_target(target, splits, means, stds):
    wb = fit_ridge(splits["TRAIN"], target, baseline_map, means, stds, 1e-6)
    wm = fit_ridge(splits["TRAIN"], target, ml_map, means, stds, 0.5)
    cal_abs = [
        abs(predict(wm, r["features"], ml_map, means, stds) - r["targets"][target])
        for r in splits["CALIBRATION"]
    ]
    q68 = conformal_quantile(cal_abs, 0.68)
    q95 = conformal_quantile(cal_abs, 0.95)

    rows = splits["FINAL_TEST"]
    truth = [r["targets"][target] for r in rows]
    pb = [predict(wb, r["features"], baseline_map, means, stds) for r in rows]
    pm = [predict(wm, r["features"], ml_map, means, stds) for r in rows]
    residual = [p - t for p, t in zip(pm, truth)]
    global_rmse = rmse(pm, truth)

    ordered = sorted(range(len(rows)), key=lambda i: truth[i])
    bins = [ordered[i * len(rows)//4:(i + 1) * len(rows)//4] for i in range(4)]
    bin_ratios = []
    for idxs in bins:
        br = rmse([pm[i] for i in idxs], [truth[i] for i in idxs])
        bin_ratios.append(br / global_rmse if global_rmse else 0.0)

    return {
        "weights_digest": sha256_bytes(canonical_json({"baseline": wb, "ml": wm}).encode()),
        "baseline_rmse": rmse(pb, truth),
        "ml_rmse": global_rmse,
        "ml_rmse_over_baseline": global_rmse / rmse(pb, truth),
        "bias": sum(residual) / len(residual),
        "coverage68": sum(abs(v) <= q68 for v in residual) / len(residual),
        "coverage95": sum(abs(v) <= q95 for v in residual) / len(residual),
        "q68": q68,
        "q95": q95,
        "corr_residual_noise": corr(residual, [r["nuisance"]["noise"] for r in rows]),
        "corr_residual_ia": corr(residual, [r["nuisance"]["ia"] for r in rows]),
        "stratified_rmse_over_global": bin_ratios,
        "predictions": pm,
    }


def ood_metrics(splits, means, stds):
    def score(row):
        return max(abs(v) for v in zfeatures(row["features"], means, stds))
    valid_scores = [score(r) for r in splits["VALIDATION"]]
    threshold = quantile(valid_scores, 0.99)
    ood_scores = [score(r) for r in splits["OOD_STRESS"]]
    return {
        "score": "max_abs_training_z",
        "threshold_from_validation_q99": threshold,
        "validation_fpr": sum(v > threshold for v in valid_scores) / len(valid_scores),
        "ood_tpr": sum(v > threshold for v in ood_scores) / len(ood_scores),
    }


def assess(metrics):
    failures = []
    for target in TARGETS:
        m = metrics["targets"][target]
        if abs(m["bias"]) > THRESHOLDS["abs_bias_max"][target]:
            failures.append(f"{target}:bias")
        if m["ml_rmse"] > THRESHOLDS["rmse_max"][target]:
            failures.append(f"{target}:rmse")
        if m["ml_rmse_over_baseline"] > THRESHOLDS["ml_rmse_over_baseline_max"]:
            failures.append(f"{target}:baseline_comparison")
        if not THRESHOLDS["coverage68_min"] <= m["coverage68"] <= THRESHOLDS["coverage68_max"]:
            failures.append(f"{target}:coverage68")
        if not THRESHOLDS["coverage95_min"] <= m["coverage95"] <= THRESHOLDS["coverage95_max"]:
            failures.append(f"{target}:coverage95")
        if abs(m["corr_residual_noise"]) > THRESHOLDS["nuisance_abs_corr_max"]:
            failures.append(f"{target}:noise_corr")
        if abs(m["corr_residual_ia"]) > THRESHOLDS["nuisance_abs_corr_max"]:
            failures.append(f"{target}:ia_corr")
        if max(m["stratified_rmse_over_global"]) > THRESHOLDS["stratified_rmse_over_global_max"]:
            failures.append(f"{target}:stratified_rmse")
    o = metrics["ood"]
    if o["validation_fpr"] > THRESHOLDS["ood_fpr_max"]:
        failures.append("ood:fpr")
    if o["ood_tpr"] < THRESHOLDS["ood_tpr_min"]:
        failures.append("ood:tpr")
    return failures


def verify_contracts():
    contract = json.loads(CONTRACT_PATH.read_text())
    parent = json.loads(PARENT_PATH.read_text())
    assert contract["pilot_id"] == "AIP-LENS-01-NULL-N1"
    assert contract["status"] == "AUTHORIZED_FOR_DETERMINISTIC_SYNTHETIC_EXECUTION"
    assert contract["hzt_comparison"] is False
    assert contract["physical_evidence_effect"] == "NONE"
    assert parent["next_candidate"]["id"] == "AIP-LENS-01-NULL-N1"
    assert parent["status"] == "PILOT_PROTOCOL_FROZEN_NOT_EXECUTED"
    assert contract["split"]["seeds"] == SEEDS
    assert contract["split"]["sizes"] == SIZES
    assert contract["predeclared_thresholds"] == THRESHOLDS
    return contract, parent


def run_pipeline(run_class):
    contract, parent = verify_contracts()
    splits = {name: generate_split(name) for name in SIZES}
    ids = [r["id"] for rows in splits.values() for r in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("split lineage collision")
    means, stds = feature_stats(splits["TRAIN"])
    target_metrics = {t: evaluate_target(t, splits, means, stds) for t in TARGETS}
    ood = ood_metrics(splits, means, stds)
    compact_targets = {}
    for target, m in target_metrics.items():
        compact_targets[target] = {k: v for k, v in m.items() if k != "predictions"}
    metrics = {"targets": compact_targets, "ood": ood}
    failures = assess(metrics)
    split_manifest = {
        name: {
            "seed": SEEDS[name],
            "size": len(rows),
            "id_first": rows[0]["id"],
            "id_last": rows[-1]["id"],
            "content_sha256": sha256_bytes(canonical_json(rows).encode()),
        }
        for name, rows in splits.items()
    }
    summary = {
        "schema": "universelab.ai-for-physics.aip-lens-01-null-n1.execution-result.v1",
        "pilot_id": "AIP-LENS-01-NULL-N1",
        "run_class": run_class,
        "generator_class": "DECLARED_TOY_SYNTHETIC_WEAK_LENSING_INSPIRED_SUMMARY_MODEL",
        "physical_simulator": False,
        "hzt_comparison": False,
        "targets": list(TARGETS),
        "metrics": metrics,
        "thresholds": THRESHOLDS,
        "failures": failures,
        "status": "PASS_N1_SYNTHETIC_THRESHOLDS" if not failures else "FAIL_N1_SYNTHETIC_THRESHOLDS",
        "gate_claims": {
            "AIP-G0": "PRESERVED",
            "AIP-G1": "PASS_FOR_THIS_SYNTHETIC_EXECUTION",
            "AIP-G2": "PASS_SCHEMA_AND_UNIT_CONTRACT_ONLY_NOT_PHYSICAL_SIMULATOR_VALIDATION",
            "AIP-G3": "PASS" if not failures else "FAIL",
            "AIP-G4": "PASS" if not failures else "FAIL",
            "AIP-G5": "PASS_SYNTHETIC_TRUTH_RETURN_ONLY",
            "AIP-G6": "NOT_TESTED_REAL_DATA_BLOCKED",
            "AIP-G7": "SEPARATE_REVIEW_REQUIRED",
        },
        "governance": {
            "WP4": "BLOCKED",
            "K1-D": "NOT_RELEASED",
            "K1-E": "NOT_ADMISSIBLE",
            "physical_evidence_effect": "NONE",
            "N2_real_data": "BLOCKED_PENDING_SEPARATE_N1_REVIEW",
        },
        "bindings": {
            "contract_sha256": sha256_bytes(CONTRACT_PATH.read_bytes()),
            "parent_contract_sha256": sha256_bytes(PARENT_PATH.read_bytes()),
            "split_manifest_sha256": sha256_bytes(canonical_json(split_manifest).encode()),
        },
        "split_manifest": split_manifest,
    }
    return summary, splits, target_metrics


def write_outputs(outdir, summary, splits, target_metrics):
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "N1_execution_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (outdir / "split_manifest.json").write_text(json.dumps(summary["split_manifest"], indent=2, sort_keys=True) + "\n")
    with (outdir / "final_test_predictions.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "Omega_m_true", "Omega_m_pred", "S8_true", "S8_pred", "noise", "ia"])
        rows = splits["FINAL_TEST"]
        for i, row in enumerate(rows):
            w.writerow([
                row["id"],
                f'{row["targets"]["Omega_m"]:.12g}',
                f'{target_metrics["Omega_m"]["predictions"][i]:.12g}',
                f'{row["targets"]["S8"]:.12g}',
                f'{target_metrics["S8"]["predictions"][i]:.12g}',
                f'{row["nuisance"]["noise"]:.12g}',
                f'{row["nuisance"]["ia"]:.12g}',
            ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="aip-lens-n1-output")
    ap.add_argument("--run-class", choices=("PR_REHEARSAL", "CANONICAL_MAIN"), default="PR_REHEARSAL")
    args = ap.parse_args()
    summary, splits, target_metrics = run_pipeline(args.run_class)
    write_outputs(Path(args.output_dir), summary, splits, target_metrics)
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(0 if summary["status"].startswith("PASS") else 2)


if __name__ == "__main__":
    main()
