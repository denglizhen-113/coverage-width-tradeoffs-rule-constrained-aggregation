"""Independent same-information maximum-entropy center baselines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import linprog, minimize


@dataclass(frozen=True)
class MaximumEntropyResult:
    point: np.ndarray
    feasible: bool
    solver_success: bool
    objective: float
    iterations: int
    message: str


def solve_max_entropy_point(
    *,
    A_ub: np.ndarray,
    b_ub: np.ndarray,
    A_eq: np.ndarray,
    b_eq: np.ndarray,
    bounds: Sequence[tuple[float, float]],
    maxiter: int = 500,
    ftol: float = 1e-10,
    log_floor: float = 1e-12,
    feasibility_tolerance: float = 1e-8,
) -> MaximumEntropyResult:
    """Maximize Shannon entropy over an observed linear feasible set."""
    n_variables = len(bounds)
    A_ub = np.asarray(A_ub, dtype=float).reshape(-1, n_variables)
    b_ub = np.asarray(b_ub, dtype=float).reshape(-1)
    A_eq = np.asarray(A_eq, dtype=float).reshape(-1, n_variables)
    b_eq = np.asarray(b_eq, dtype=float).reshape(-1)
    feasible = linprog(
        np.zeros(n_variables, dtype=float),
        A_ub=A_ub if len(A_ub) else None,
        b_ub=b_ub if len(b_ub) else None,
        A_eq=A_eq if len(A_eq) else None,
        b_eq=b_eq if len(b_eq) else None,
        bounds=bounds,
        method="highs",
    )
    if not feasible.success:
        return MaximumEntropyResult(
            point=np.full(n_variables, np.nan),
            feasible=False,
            solver_success=False,
            objective=float("nan"),
            iterations=0,
            message=str(feasible.message),
        )

    def objective(point: np.ndarray) -> float:
        clipped = np.clip(point, log_floor, None)
        return float(np.sum(point * np.log(clipped)))

    def gradient(point: np.ndarray) -> np.ndarray:
        return np.log(np.clip(point, log_floor, None)) + 1.0

    constraints: list[dict[str, object]] = []
    if len(A_eq):
        constraints.append(
            {
                "type": "eq",
                "fun": lambda point: A_eq @ point - b_eq,
                "jac": lambda point: A_eq,
            }
        )
    if len(A_ub):
        constraints.append(
            {
                "type": "ineq",
                "fun": lambda point: b_ub - A_ub @ point,
                "jac": lambda point: -A_ub,
            }
        )
    solved = minimize(
        objective,
        np.asarray(feasible.x, dtype=float),
        jac=gradient,
        bounds=bounds,
        constraints=constraints,
        method="SLSQP",
        options={"maxiter": maxiter, "ftol": ftol, "disp": False},
    )
    point = np.asarray(solved.x, dtype=float)
    inequalities_ok = not len(A_ub) or bool(
        np.all(A_ub @ point <= b_ub + feasibility_tolerance)
    )
    equalities_ok = not len(A_eq) or bool(
        np.all(np.abs(A_eq @ point - b_eq) <= feasibility_tolerance)
    )
    bounds_ok = all(
        lower - feasibility_tolerance <= value <= upper + feasibility_tolerance
        for value, (lower, upper) in zip(point, bounds)
    )
    solver_success = bool(solved.success and inequalities_ok and equalities_ok and bounds_ok)
    return MaximumEntropyResult(
        point=point,
        feasible=True,
        solver_success=solver_success,
        objective=float(solved.fun),
        iterations=int(getattr(solved, "nit", 0)),
        message=str(solved.message),
    )


def maximum_entropy_rank_center(compatible_ranks: np.ndarray) -> np.ndarray:
    """Return the expectation under the finite uniform maximum-entropy law."""
    states = np.asarray(compatible_ranks, dtype=float)
    if states.ndim != 2 or len(states) == 0:
        return np.full(states.shape[1] if states.ndim == 2 else 0, np.nan)
    return states.mean(axis=0)
