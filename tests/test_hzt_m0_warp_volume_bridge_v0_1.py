#!/usr/bin/env python3
from __future__ import annotations

import math
import unittest

from tools.hzt_m0_warp_volume_bridge_v0_1 import (
    BraneEinsteinTerm4D,
    CapEinsteinTerm5D,
    WarpRegion,
    WarpVolumeError,
    benchmark_volume_candidates,
    brane4d_planck_contribution,
    cap5d_planck_contribution,
    dimensionless_warped_volume,
    effective_planck_mass_squared,
    total_warped_volume,
    warped_volume_axisymmetric,
)


class WarpVolumeBridgeTests(unittest.TestCase):
    def test_flat_disk(self) -> None:
        # For A=0 and L=r: V_W = 2pi int_0^R r dr = pi R^2.
        R = 3.0
        n = 1201
        r = [R * i / (n - 1) for i in range(n)]
        region = WarpRegion(r=r, A=[0.0] * n, L=r)
        self.assertAlmostEqual(warped_volume_axisymmetric(region), math.pi * R * R, places=11)

    def test_constant_warped_cylinder(self) -> None:
        R, L0, A0, period = 2.5, 0.7, -0.2, 1.5
        region = WarpRegion(
            r=[0.0, R],
            A=[A0, A0],
            L=[L0, L0],
            chi_period=period,
        )
        expected = period * R * L0 * math.exp(2.0 * A0)
        self.assertAlmostEqual(warped_volume_axisymmetric(region), expected, places=14)

    def test_regions_add(self) -> None:
        left = WarpRegion(r=[0.0, 1.0], A=[0.0, 0.0], L=[1.0, 1.0], chi_period=2.0)
        right = WarpRegion(r=[1.0, 3.0], A=[0.0, 0.0], L=[1.0, 1.0], chi_period=2.0)
        self.assertAlmostEqual(total_warped_volume([left, right]), 6.0, places=14)

    def test_length_rescaling(self) -> None:
        # r -> s r and L -> s L implies V_W -> s^2 V_W.
        s = 4.0
        base = WarpRegion(r=[0.0, 1.0, 2.0], A=[0.1, -0.1, 0.0], L=[0.0, 0.8, 1.1])
        scaled = WarpRegion(
            r=[s * x for x in base.r],
            A=base.A,
            L=[s * x for x in base.L],
        )
        self.assertAlmostEqual(
            warped_volume_axisymmetric(scaled),
            s * s * warped_volume_axisymmetric(base),
            places=12,
        )

    def test_localized_terms(self) -> None:
        cap = CapEinsteinTerm5D(
            M5_cubed=3.0,
            L_sigma=2.0,
            A_sigma=math.log(2.0) / 2.0,
            chi_period=1.0,
        )
        brane = BraneEinsteinTerm4D(
            M4_local_squared=5.0,
            A_sigma=math.log(3.0) / 2.0,
        )
        self.assertAlmostEqual(cap5d_planck_contribution(cap), 12.0, places=13)
        self.assertAlmostEqual(brane4d_planck_contribution(brane), 15.0, places=13)

    def test_effective_planck_mass(self) -> None:
        result = effective_planck_mass_squared(
            kappa6_squared=2.0,
            warped_volume=8.0,
            cap_terms_5d=[CapEinsteinTerm5D(1.0, 1.0, 0.0, 2.0)],
            brane_terms_4d=[BraneEinsteinTerm4D(3.0, 0.0)],
        )
        self.assertAlmostEqual(result["bulk_M4_squared"], 4.0)
        self.assertAlmostEqual(result["cap5d_M4_squared"], 2.0)
        self.assertAlmostEqual(result["brane4d_M4_squared"], 3.0)
        self.assertAlmostEqual(result["total_M4_squared"], 9.0)
        self.assertAlmostEqual(result["kappa4_squared"], 1.0 / 9.0)
        self.assertAlmostEqual(result["G4"], 1.0 / (72.0 * math.pi))

    def test_dimensionless_volume(self) -> None:
        self.assertAlmostEqual(dimensionless_warped_volume(K4=4.0, warped_volume=0.25), 1.0)

    def test_legacy_benchmark_ambiguity_is_preserved(self) -> None:
        value = 0.5318111250097
        candidates = benchmark_volume_candidates(reported_value=value, K4=1.0)
        self.assertAlmostEqual(candidates["if_full_dimensionless_then_V_W"], value)
        self.assertAlmostEqual(
            candidates["if_per_radian_dimensionless_then_V_W"],
            2.0 * math.pi * value,
        )
        self.assertNotAlmostEqual(
            candidates["if_full_dimensionless_then_V_W"],
            candidates["if_per_radian_dimensionless_then_V_W"],
        )

    def test_invalid_profiles_fail_closed(self) -> None:
        with self.assertRaises(WarpVolumeError):
            warped_volume_axisymmetric(WarpRegion(r=[0.0, 0.0], A=[0.0, 0.0], L=[0.0, 1.0]))
        with self.assertRaises(WarpVolumeError):
            warped_volume_axisymmetric(WarpRegion(r=[0.0, 1.0], A=[0.0, 0.0], L=[0.0, -1.0]))
        with self.assertRaises(WarpVolumeError):
            effective_planck_mass_squared(kappa6_squared=0.0, warped_volume=1.0)
        with self.assertRaises(WarpVolumeError):
            dimensionless_warped_volume(K4=0.0, warped_volume=1.0)


if __name__ == "__main__":
    unittest.main()
