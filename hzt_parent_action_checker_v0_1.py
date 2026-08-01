#!/usr/bin/env python3
"""HZT S6 parent-action and cap-junction checker v0.1."""

from __future__ import annotations

import argparse
import json
import math
import sys


DIMENSIONS = {
    "M6": 1,
    "M6^4": 4,
    "R": 2,
    "Lambda6": 2,
    "phi": 2,
    "d_phi": 3,
    "U": 6,
    "A": 2,
    "F": 3,
    "Z_F": 0,
    "K": 1,
    "lambda_cap": 5,
    "Z_sigma": 3,
    "D_sigma": 1,
}


def dimension_audit():
    terms = {
        "M6^4 R": DIMENSIONS["M6^4"] + DIMENSIONS["R"],
        "M6^4 Lambda6": DIMENSIONS["M6^4"] + DIMENSIONS["Lambda6"],
        "(d phi)^2": 2 * DIMENSIONS["d_phi"],
        "U": DIMENSIONS["U"],
        "F^2": 2 * DIMENSIONS["F"],
        "GHY density M6^4 K": DIMENSIONS["M6^4"] + DIMENSIONS["K"],
        "cap lambda": DIMENSIONS["lambda_cap"],
        "cap Z_sigma (D sigma)^2":
            DIMENSIONS["Z_sigma"] + 2 * DIMENSIONS["D_sigma"],
    }
    expected = {
        "M6^4 R": 6,
        "M6^4 Lambda6": 6,
        "(d phi)^2": 6,
        "U": 6,
        "F^2": 6,
        "GHY density M6^4 K": 5,
        "cap lambda": 5,
        "cap Z_sigma (D sigma)^2": 5,
    }
    return {
        name: {
            "dimension": value,
            "expected": expected[name],
            "pass": value == expected[name],
        }
        for name, value in terms.items()
    }


def junction_audit(M6, A_sigma, L_sigma, lambda_cap=None, Y_sigma=None):
    M64 = M6**4

    if Y_sigma is None:
        Y_required = M64 * (L_sigma - A_sigma)
    else:
        Y_required = Y_sigma

    if lambda_cap is None:
        lambda_from_internal = 4.0 * M64 * A_sigma + 0.5 * Y_required
        lambda_from_4d = M64 * (3.0 * A_sigma + L_sigma) - 0.5 * Y_required
    else:
        lambda_from_internal = lambda_cap
        lambda_from_4d = lambda_cap

    residual_4d = (
        M64 * (-3.0 * A_sigma - L_sigma)
        - (-lambda_from_4d - 0.5 * Y_required)
    )
    residual_internal = (
        M64 * (-4.0 * A_sigma)
        - (-lambda_from_internal + 0.5 * Y_required)
    )

    scale = max(
        1.0,
        abs(M64 * A_sigma),
        abs(M64 * L_sigma),
        abs(lambda_from_4d),
        abs(lambda_from_internal),
        abs(Y_required),
    )

    pure_tension_residual = A_sigma - L_sigma
    return {
        "M6": M6,
        "A_sigma": A_sigma,
        "L_sigma": L_sigma,
        "Y_sigma_required": Y_required,
        "Y_sigma_positive": Y_required >= 0.0,
        "pure_tension_condition": abs(pure_tension_residual) <= 1e-12 * max(
            1.0, abs(A_sigma), abs(L_sigma)
        ),
        "pure_tension_residual": pure_tension_residual,
        "lambda_from_4d": lambda_from_4d,
        "lambda_from_internal": lambda_from_internal,
        "junction_4d_relative_residual": residual_4d / scale,
        "junction_internal_relative_residual": residual_internal / scale,
    }


def background_residuals(
    M6, Lambda6, K4, A, Ap, App, ell, Lpp_over_L,
    phip, U, rhoF
):
    M64 = M6**4
    e2 = math.exp(-2.0 * A)

    lhs_munu = M64 * (
        3.0 * App + 6.0 * Ap**2 + 3.0 * Ap * ell
        + Lpp_over_L - 3.0 * K4 * e2 + Lambda6
    )
    rhs_munu = -0.5 * phip**2 - U - rhoF

    lhs_rr = M64 * (
        6.0 * Ap**2 + 4.0 * Ap * ell
        - 6.0 * K4 * e2 + Lambda6
    )
    rhs_rr = 0.5 * phip**2 - U + rhoF

    lhs_chi = M64 * (
        4.0 * App + 10.0 * Ap**2
        - 6.0 * K4 * e2 + Lambda6
    )
    rhs_chi = -0.5 * phip**2 - U + rhoF

    scale = max(
        1.0,
        abs(lhs_munu), abs(rhs_munu),
        abs(lhs_rr), abs(rhs_rr),
        abs(lhs_chi), abs(rhs_chi),
    )

    return {
        "munu_relative_residual": (lhs_munu - rhs_munu) / scale,
        "rr_relative_residual": (lhs_rr - rhs_rr) / scale,
        "chichi_relative_residual": (lhs_chi - rhs_chi) / scale,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--M6", type=float, default=1.0)
    parser.add_argument("--A-sigma", type=float, default=1.0)
    parser.add_argument("--L-sigma", type=float, default=1.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = {
        "dimension_audit": dimension_audit(),
        "junction_audit": junction_audit(
            args.M6, args.A_sigma, args.L_sigma
        ),
    }

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
