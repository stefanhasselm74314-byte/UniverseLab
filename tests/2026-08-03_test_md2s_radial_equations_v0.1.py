#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "2026-08-03_hzt_m0_md2s_radial_equations_v0.1.py"
SPEC = importlib.util.spec_from_file_location("md2s_radial_equations_v0_1", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestMD2SRadialEquations(unittest.TestCase):
    def assertNearZero(self, value: float, tolerance: float = 1e-11) -> None:
        self.assertLessEqual(abs(value), tolerance)

    def bulk_data(self):
        return {
            "A": 0.17,
            "Ap": 0.08,
            "L": 1.3,
            "Lp": 0.91,
            "phi": 0.4,
            "phip": -0.07,
            "K4": 0.12,
            "Lambda6": 0.31,
            "kappa6_sq": 1.7,
            "Q": 0.23,
            "Z_phi": 1.2,
            "Z_phi_phi": -0.14,
            "Z_F": 0.9,
            "Z_F_phi": 0.11,
            "V": 0.27,
            "V_phi": -0.08,
        }

    def center_data(self):
        return {
            "A0": 0.2,
            "phi0": 0.4,
            "K4": 0.8,
            "Lambda6": 0.7,
            "kappa6_sq": 1.3,
            "Q": 0.3,
            "Z_phi0": 1.4,
            "Z_F0": 1.1,
            "Z_F_phi0": -0.2,
            "V0": 0.4,
            "V_phi0": 0.16,
            "Delta_chi": 2.0 * math.pi,
        }

    def test_flat_vacuum_residuals(self):
        result = mod.residuals(
            A=0.0, Ap=0.0, App=0.0,
            L=2.0, Lp=1.0, Lpp=0.0,
            phi=0.0, phip=0.0, phipp=0.0,
            K4=0.0, Lambda6=0.0, kappa6_sq=1.0,
            Q=0.0, Z_phi=1.0, Z_phi_phi=0.0,
            Z_F=1.0, Z_F_phi=0.0, V=0.0, V_phi=0.0,
        )
        for key in ("E4", "Er_constraint", "Echi", "Ephi", "R6"):
            self.assertNearZero(result[key])

    def test_maxwell_first_integral_is_reconstructed(self):
        values = mod.magnetic_quantities(A=0.3, L=1.7, Q=-0.42, Z_F=1.6)
        self.assertAlmostEqual(values["first_integral"], -0.42, places=13)
        self.assertAlmostEqual(values["M"], 1.6 * values["B_sq"], places=14)

    def test_evolution_equations_zero_selected_residuals(self):
        data = self.bulk_data()
        evolved = mod.evolution_second_derivatives(**data)
        result = mod.residuals(
            **data,
            App=evolved["App"],
            Lpp=evolved["Lpp"],
            phipp=evolved["phipp"],
        )
        self.assertNearZero(result["E4"])
        self.assertNearZero(result["Echi"])
        self.assertNearZero(result["Ephi"])
        self.assertTrue(math.isfinite(result["Er_constraint"]))

    def test_constraint_function_matches_full_residual(self):
        data = self.bulk_data()
        evolved = mod.evolution_second_derivatives(**data)
        result = mod.residuals(
            **data,
            App=evolved["App"],
            Lpp=evolved["Lpp"],
            phipp=evolved["phipp"],
        )
        constraint = mod.radial_constraint(
            A=data["A"], Ap=data["Ap"], L=data["L"], Lp=data["Lp"],
            phip=data["phip"], K4=data["K4"], Lambda6=data["Lambda6"],
            kappa6_sq=data["kappa6_sq"], Q=data["Q"], Z_phi=data["Z_phi"],
            Z_F=data["Z_F"], V=data["V"],
        )
        self.assertAlmostEqual(constraint, result["Er_constraint"], places=13)

    def test_center_coefficients_close_leading_equations(self):
        data = self.center_data()
        coeff = mod.center_series_coefficients(**data)
        residuals = mod.center_einstein_residuals(
            a2=coeff["a2"], c2=coeff["c2"], A0=data["A0"],
            K4=data["K4"], Lambda6=data["Lambda6"],
            kappa6_sq=data["kappa6_sq"], V0=data["V0"], M0=coeff["M0"],
        )
        for value in residuals.values():
            self.assertNearZero(value)
        self.assertNearZero(mod.center_scalar_residual(
            p2=coeff["p2"], Z_phi0=data["Z_phi0"], V_phi0=data["V_phi0"],
            Z_F_phi0=data["Z_F_phi0"], B0_sq=coeff["B0_sq"],
        ))

    def test_smooth_period_and_conical_deficit(self):
        coeff = mod.center_series_coefficients(**self.center_data())
        self.assertAlmostEqual(coeff["ell1"], 1.0, places=14)
        self.assertNearZero(coeff["deficit_angle"])
        deficit = mod.conical_deficit(Delta_chi=2.0 * math.pi, ell1=0.91)
        self.assertGreater(deficit, 0.0)

    def test_bianchi_constraint_propagation(self):
        derivative = mod.bianchi_constraint_derivative(
            Er=0.2, E4=0.0, Echi=0.0, Ap=0.1, L=2.0, Lp=0.5
        )
        expected = -(4.0 * 0.1 + 0.5 / 2.0) * 0.2
        self.assertAlmostEqual(derivative, expected, places=14)
        self.assertNearZero(mod.bianchi_constraint_derivative(
            Er=0.0, E4=0.0, Echi=0.0, Ap=9.0, L=1.0, Lp=8.0
        ))

    def test_nonpositive_kinetic_functions_fail_closed(self):
        with self.assertRaises(mod.ContractError):
            mod.magnetic_quantities(A=0.0, L=1.0, Q=1.0, Z_F=0.0)
        data = self.bulk_data()
        data["Z_phi"] = -1.0
        with self.assertRaises(mod.ContractError):
            mod.evolution_second_derivatives(**data)

    def test_cli_center_mode(self):
        payload = {"mode": "center", "data": self.center_data()}
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(MODULE_PATH), str(source)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        output = json.loads(completed.stdout)
        self.assertEqual(output["status"], "DIAGNOSTIC_ONLY")
        self.assertNearZero(output["result"]["scalar_residual"])


if __name__ == "__main__":
    unittest.main()
