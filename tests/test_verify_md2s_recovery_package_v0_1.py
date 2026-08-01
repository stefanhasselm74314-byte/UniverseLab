from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "tools" / "verify_md2s_recovery_package_v0_1.py"
SPEC = importlib.util.spec_from_file_location("md2s_verifier", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load MD-2S verifier module")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


BENCHMARKS = {
    "sqrt_K4_rho_cap": 1.1196329253611,
    "kappa6_squared_lambda_eff_over_4sqrtK4": 0.8931498683204,
    "K4_rho_cap_squared": 1.2535778875527,
    "V_W": 0.5318111250097,
    "R_circle_at_K4_beta_1": 0.6661500466003,
    "Xi_cap_reported": 0.9999999998535,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def build_valid_package(root: Path) -> None:
    write_json(root / "parameters.json", {"K4": 1.0, "beta": 1.0})
    write_json(root / "conventions.json", {"signature": "(-,+,+,+,+,+)", "chi_period": "2*pi"})
    write_json(root / "solver-config.json", {"method": "synthetic-test", "mesh_points": 3})
    write_json(root / "environment.json", {"python": "test"})

    boundary_common = {
        "A_prime": 0.1,
        "L": 1.0,
        "L_prime": 0.2,
        "phi": 0.0,
        "phi_prime": 0.0,
        "A_chi": 0.0,
        "Q": 1.0,
        "Z_F": 1.0,
    }
    write_json(root / "boundary-left.json", {"normal_r": -1.0, **boundary_common})
    write_json(root / "boundary-right.json", {"normal_r": 1.0, **boundary_common})

    profile = (
        "r,A,A_prime,L,L_prime,phi,phi_prime,A_chi,Q,Z_F\n"
        "0.0,0.0,0.0,0.001,1.0,0.0,0.0,0.0,1.0,1.0\n"
        "0.5,0.01,0.02,0.5,0.8,0.0,0.0,0.0,1.0,1.0\n"
        "1.0,0.03,0.05,1.0,0.2,0.0,0.0,0.0,1.0,1.0\n"
    )
    (root / "profiles.csv").write_text(profile, encoding="utf-8")

    write_json(
        root / "benchmarks.json",
        {
            "values": BENCHMARKS,
            "tolerances": {name: 1e-12 for name in BENCHMARKS},
        },
    )
    write_json(
        root / "residuals.json",
        {
            "residuals": [
                {
                    "equation_id": "R-HAMILTONIAN",
                    "raw_residual": 0.0,
                    "normalized_residual": 0.0,
                    "absolute_tolerance": 1e-10,
                    "relative_tolerance": 1e-10,
                    "evaluation_location": "global-max",
                    "status": "PASS",
                }
            ]
        },
    )

    output_names = [
        "parameters.json",
        "conventions.json",
        "solver-config.json",
        "profiles.csv",
        "boundary-left.json",
        "boundary-right.json",
        "residuals.json",
        "benchmarks.json",
        "environment.json",
    ]
    output_hashes = {name: "sha256:" + sha256(root / name) for name in output_names}
    write_json(
        root / "manifest.json",
        {
            "run_id": "MD2S-RUN-20260801-001",
            "model_version": "synthetic-test-v0.1",
            "equation_set_hash": "sha256:" + "1" * 64,
            "solver_source_hash": "sha256:" + "2" * 64,
            "parameter_file_hash": "sha256:" + sha256(root / "parameters.json"),
            "software_versions": {"python": "test"},
            "floating_point_precision": "float64",
            "solver_method": "synthetic-test",
            "mesh_or_collocation": {"points": 3},
            "absolute_tolerance": 1e-10,
            "relative_tolerance": 1e-10,
            "initial_guess_provenance": "unit-test fixture",
            "seed": None,
            "output_hashes": output_hashes,
            "status": "PASS",
        },
    )


class Md2sRecoveryVerifierTests(unittest.TestCase):
    def test_complete_hash_consistent_package_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_valid_package(root)
            result = VERIFIER.verify(root)
            self.assertEqual(result["status"], "PASS", result)
            self.assertEqual(result["failed_checks"], [])

    def test_tampered_profile_fails_hash_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_valid_package(root)
            with (root / "profiles.csv").open("a", encoding="utf-8") as handle:
                handle.write("1.5,0,0,1,0,0,0,0,1,1\n")
            result = VERIFIER.verify(root)
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("output_hashes", result["failed_checks"])

    def test_missing_package_files_fail_without_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = VERIFIER.verify(Path(tmp))
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["checks"]["required_files"]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
