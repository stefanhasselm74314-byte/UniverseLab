"""UniverseLab / Hyperzeit HPVS
HZT-M0-S6 MD-2S Background BVP Solver v1.0-alpha1

Status
------
Numerical infrastructure scaffold. This file does NOT claim that the complete
MD-2S background equations have been recovered. It provides the canonical BVP
contract, convergence diagnostics and one-sided boundary export required by
SCI-001/SCI-002 v0.2.

A physical run is admissible only after the complete ODE system and boundary
conditions have been rederived from the canonical parent action and supplied
through ModelCallbacks.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
from typing import Callable, Dict, Any, Optional
import json
import numpy as np

try:
    from scipy.integrate import solve_bvp
except Exception:  # pragma: no cover
    solve_bvp = None

Array = np.ndarray


@dataclass(frozen=True)
class SolverConfig:
    r_left: float
    r_right: float
    mesh_points: int = 400
    tol: float = 1e-7
    bc_tol: float = 1e-8
    max_nodes: int = 50000
    verbose: int = 1
    convention_id: str = "HZT-M0-S6-SCI001002-v0.1"
    branch: str = "HZT-M0-S6 / S6-Q1 / MD-2S"

    def validate(self) -> None:
        if not np.isfinite(self.r_left) or not np.isfinite(self.r_right):
            raise ValueError("r_left and r_right must be finite")
        if self.r_right <= self.r_left:
            raise ValueError("require r_right > r_left")
        if self.mesh_points < 20:
            raise ValueError("mesh_points must be >= 20")
        if self.tol <= 0 or self.bc_tol <= 0:
            raise ValueError("tolerances must be positive")


@dataclass
class ModelCallbacks:
    """Complete physical model contract.

    ode(r, y, p) must return dy/dr with the same shape as y.
    bc(ya, yb, p) must return all boundary residuals.
    initial_guess(r, p) returns initial y on the mesh.

    field_index maps canonical names onto y rows. The minimum expected set is
    A, A_prime, L, L_prime, phi, phi_prime, A_chi.
    """
    ode: Callable[[Array, Array, Dict[str, float]], Array]
    bc: Callable[[Array, Array, Dict[str, float]], Array]
    initial_guess: Callable[[Array, Dict[str, float]], Array]
    field_index: Dict[str, int]
    equation_set_id: str

    def validate(self) -> None:
        required = {"A", "A_prime", "L", "L_prime", "phi", "phi_prime", "A_chi"}
        missing = required.difference(self.field_index)
        if missing:
            raise ValueError(f"field_index missing canonical fields: {sorted(missing)}")
        if not self.equation_set_id.strip():
            raise ValueError("equation_set_id is required")


@dataclass
class RunDiagnostics:
    success: bool
    status: int
    message: str
    niter: int
    nodes: int
    max_rms_residual: float
    max_bc_residual: float
    mesh_convergence_delta: Optional[float]
    equation_set_id: str
    convention_id: str


CANONICAL_BOUNDARY_KEYS = (
    "r_sigma", "normal_r", "A_prime", "L", "L_prime",
    "phi", "phi_prime", "A_chi", "Q", "Z_F"
)


def _file_sha256(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _max_abs(x: Array) -> float:
    x = np.asarray(x, dtype=float)
    return float(np.max(np.abs(x))) if x.size else 0.0


def solve_background(
    config: SolverConfig,
    model: ModelCallbacks,
    parameters: Dict[str, float],
    *,
    perform_mesh_check: bool = True,
):
    """Solve one branch of the MD-2S BVP.

    No hidden physics defaults are supplied. The complete ODE and BC system is
    injected explicitly through ModelCallbacks.
    """
    config.validate()
    model.validate()
    if solve_bvp is None:
        raise RuntimeError("scipy.integrate.solve_bvp is required")

    r = np.linspace(config.r_left, config.r_right, config.mesh_points)
    y0 = np.asarray(model.initial_guess(r, parameters), dtype=float)

    def ode(rr: Array, yy: Array) -> Array:
        out = np.asarray(model.ode(rr, yy, parameters), dtype=float)
        if out.shape != yy.shape:
            raise ValueError(f"ODE shape {out.shape} != state shape {yy.shape}")
        return out

    def bc(ya: Array, yb: Array) -> Array:
        return np.asarray(model.bc(ya, yb, parameters), dtype=float)

    sol = solve_bvp(
        ode, bc, r, y0,
        tol=config.tol,
        bc_tol=config.bc_tol,
        max_nodes=config.max_nodes,
        verbose=config.verbose,
    )

    rms = np.asarray(getattr(sol, "rms_residuals", np.array([np.nan])), dtype=float)
    max_rms = float(np.nanmax(rms)) if rms.size else float("nan")
    max_bc = _max_abs(bc(sol.y[:, 0], sol.y[:, -1]))

    mesh_delta = None
    if perform_mesh_check and sol.success:
        r2 = np.linspace(config.r_left, config.r_right, 2 * config.mesh_points - 1)
        y02 = sol.sol(r2)
        sol2 = solve_bvp(
            ode, bc, r2, y02,
            tol=config.tol,
            bc_tol=config.bc_tol,
            max_nodes=config.max_nodes,
            verbose=0,
        )
        if sol2.success:
            probe = np.linspace(config.r_left, config.r_right, 257)
            scale = max(1.0, _max_abs(sol.sol(probe)))
            mesh_delta = _max_abs(sol2.sol(probe) - sol.sol(probe)) / scale

    diag = RunDiagnostics(
        success=bool(sol.success),
        status=int(sol.status),
        message=str(sol.message),
        niter=int(getattr(sol, "niter", -1)),
        nodes=int(sol.x.size),
        max_rms_residual=max_rms,
        max_bc_residual=max_bc,
        mesh_convergence_delta=mesh_delta,
        equation_set_id=model.equation_set_id,
        convention_id=config.convention_id,
    )
    return sol, diag


def sample_boundary(
    sol,
    r_sigma: float,
    model: ModelCallbacks,
    *,
    normal_r: float,
    Q: float,
    Z_F: float,
) -> Dict[str, float]:
    """Sample the solution on one side of r_sigma.

    For a discontinuous interface, call this function on the independently
    solved bulk and cap solution objects. Do not interpolate through the jump.
    """
    if normal_r not in (-1.0, 1.0):
        raise ValueError("normal_r must be +1 or -1 under the current radial convention")
    y = np.asarray(sol.sol(float(r_sigma)), dtype=float)
    idx = model.field_index
    out = {
        "r_sigma": float(r_sigma),
        "normal_r": float(normal_r),
        "A_prime": float(y[idx["A_prime"]]),
        "L": float(y[idx["L"]]),
        "L_prime": float(y[idx["L_prime"]]),
        "phi": float(y[idx["phi"]]),
        "phi_prime": float(y[idx["phi_prime"]]),
        "A_chi": float(y[idx["A_chi"]]),
        "Q": float(Q),
        "Z_F": float(Z_F),
    }
    if out["L"] == 0.0:
        raise ZeroDivisionError("L(r_sigma)=0 is not an admissible cap interface for L'/L")
    return out


def junction_quantities(
    bulk: Dict[str, float],
    cap: Dict[str, float],
    M6: float,
) -> Dict[str, float]:
    """Compute the SCI-001/002 v0.1 two-junction diagnostics."""
    if M6 <= 0:
        raise ValueError("M6 must be positive")
    for side_name, side in (("bulk", bulk), ("cap", cap)):
        missing = set(CANONICAL_BOUNDARY_KEYS).difference(side)
        if missing:
            raise ValueError(f"{side_name} boundary export missing {sorted(missing)}")

    A_sigma = (
        bulk["normal_r"] * bulk["A_prime"]
        + cap["normal_r"] * cap["A_prime"]
    )
    L_sigma = (
        bulk["normal_r"] * bulk["L_prime"] / bulk["L"]
        + cap["normal_r"] * cap["L_prime"] / cap["L"]
    )
    m64 = M6 ** 4
    Y_required = m64 * (L_sigma - A_sigma)
    return {
        "A_sigma": float(A_sigma),
        "L_sigma": float(L_sigma),
        "pure_tension_residual": float(A_sigma - L_sigma),
        "Y_sigma_required": float(Y_required),
        "positive_winding_candidate": bool(Y_required >= 0.0),
    }


def export_run(
    output_dir: str | Path,
    *,
    config: SolverConfig,
    parameters: Dict[str, float],
    diagnostics: RunDiagnostics,
    bulk_boundary: Optional[Dict[str, float]] = None,
    cap_boundary: Optional[Dict[str, float]] = None,
    junction: Optional[Dict[str, float]] = None,
) -> Path:
    """Write a provenance-first JSON run record."""
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "schema": "universelab.md2s-bvp-run.v1",
        "status": "NUMERICAL_DIAGNOSTIC_ONLY",
        "config": asdict(config),
        "parameters": {k: float(v) for k, v in parameters.items()},
        "diagnostics": asdict(diagnostics),
        "bulk_boundary": bulk_boundary,
        "cap_boundary": cap_boundary,
        "junction": junction,
        "governance": {
            "K1-D": "NOT_RELEASED",
            "K1-E": "NOT_ADMISSIBLE",
            "evidence_effect": "NONE"
        },
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    path = outdir / "md2s_run.json"
    path.write_text(text, encoding="utf-8")
    (outdir / "md2s_run.sha256").write_text(_file_sha256(path) + "  md2s_run.json\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    raise SystemExit(
        "MD2S solver infrastructure is installed, but no physical equation set "
        "is bundled yet. Supply a rederived ModelCallbacks implementation before running."
    )
