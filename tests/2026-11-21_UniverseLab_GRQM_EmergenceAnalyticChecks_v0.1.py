"""UL-GRQM-EMERG-001: elementary, model-independent consistency checks.

DRAFT / NONCANONICAL. These are exact/toy identities, not a proof of
holographic reconstruction, two-time ghost freedom or 6D model validity.
Run: python tests/2026-11-21_UniverseLab_GRQM_EmergenceAnalyticChecks_v0.1.py
"""
import math
import unittest
from fractions import Fraction


class EmergenceAnalyticChecks(unittest.TestCase):
    def test_modular_ball_integral_exact(self):
        # Integral_0^R (R^2-r^2)r^2 dr = (1/3-1/5) R^5.
        self.assertEqual(Fraction(1, 3) - Fraction(1, 5), Fraction(2, 15))
        # 2*pi*4*pi/(2*R) times (2/15)*R^5 = (8*pi^2/15)*R^4.
        coefficient = (4 * math.pi**2) * float(Fraction(2, 15))
        self.assertAlmostEqual(coefficient, 8 * math.pi**2 / 15, places=13)

    def test_disk_metric_has_one_time(self):
        for A, B, C, r in [(0., 0., 0., 1.), (0.4, -0.3, 0.1, 2.),
                            (-1., 0.2, 1.3, 0.03)]:
            diag = [-math.exp(-2*A)] + [math.exp(-2*A)] * 3
            diag += [math.exp(2*B), math.exp(2*C)*r*r]
            negatives = sum(d < 0 for d in diag)
            positives = sum(d > 0 for d in diag)
            direct = math.prod(diag)
            analytic = -math.exp(-8*A+2*B+2*C) * r*r
            self.assertEqual((positives, negatives), (5, 1))
            self.assertAlmostEqual(direct/analytic, 1.0, places=12)
            self.assertLess(direct, 0.)

    def test_second_time_changes_signature_not_observational_status(self):
        # Illustrative sign flip, not a proposed HZT solution.
        diag = [-1., 1., 1., 1., -1., 1.]
        self.assertEqual((sum(d > 0 for d in diag), sum(d < 0 for d in diag)), (4, 2))
        self.assertGreater(math.prod(diag), 0.)

    def test_unconstrained_two_time_mode_exposes_ir_instability(self):
        L_tau, n, k_squared = 3., 1, 0.
        omega_squared = k_squared - (n/L_tau)**2
        self.assertLess(omega_squared, 0.)
        self.assertEqual(0. - (0/L_tau)**2, 0.)
        # Tachyonic instability is not, by itself, a proof of ghosts.

    def test_bell_pair_entanglement_not_distance(self):
        # The same Bell-pair state can be assigned different external distances.
        s_a = math.log(2.)
        mutual_information = 2*s_a
        assigned_distances = [0.01, 9.4607e15]
        self.assertNotEqual(*assigned_distances)
        self.assertEqual(mutual_information, 2*math.log(2.))


if __name__ == "__main__":
    unittest.main(verbosity=2)
