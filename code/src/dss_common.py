"""Shared deterministic primitives for DSS synthetic and disclosure scenarios.

The functions in this module operate only on simulated latent preferences.
They are not used to interpret empirical public preferences as observed truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from src.constraints import solve_preference_bounds


@dataclass(frozen=True)
class SyntheticPreferenceCase:
    """A one-week percentage-aggregation case with known synthetic truth."""

    public_preference: np.ndarray
    judge_share: np.ndarray
    eliminated_index: int
    observed_outcome_noise: bool

    @property
    def n_active(self) -> int:
        return len(self.public_preference)


def generate_percentage_case(
    rng: np.random.Generator,
    *,
    n_active: int = 5,
    public_concentration: float = 1.2,
    judge_public_correlation: float = 0.35,
    outcome_noise_probability: float = 0.0,
) -> SyntheticPreferenceCase:
    """Generate a rule-consistent synthetic percentage-aggregation case.

    The public vector is latent only inside this simulator.  An optional noisy
    outcome deliberately violates the generating aggregate and is used solely
    as a misspecification stress test.
    """
    if n_active < 3:
        raise ValueError("n_active must be at least three.")
    if not 0.0 <= judge_public_correlation <= 1.0:
        raise ValueError("judge_public_correlation must lie in [0, 1].")
    if not 0.0 <= outcome_noise_probability <= 1.0:
        raise ValueError("outcome_noise_probability must lie in [0, 1].")
    public = rng.dirichlet(np.full(n_active, public_concentration, dtype=float))
    independent_judge = rng.dirichlet(np.full(n_active, 1.4, dtype=float))
    judge = judge_public_correlation * public + (1.0 - judge_public_correlation) * independent_judge
    judge = judge / judge.sum()
    combined = public + judge
    eliminated = int(np.argmin(combined))
    noisy = bool(rng.random() < outcome_noise_probability)
    if noisy:
        order = np.argsort(combined, kind="stable")
        eliminated = int(order[1])
    return SyntheticPreferenceCase(
        public_preference=public,
        judge_share=judge,
        eliminated_index=eliminated,
        observed_outcome_noise=noisy,
    )


def base_percentage_constraints(
    case: SyntheticPreferenceCase,
    *,
    include_elimination_constraint: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, tuple[tuple[float, float], ...]]:
    """Create the simplex and optional observed-elimination constraints."""
    n_active = case.n_active
    rows: list[np.ndarray] = []
    rhs: list[float] = []
    if include_elimination_constraint:
        for survivor in range(n_active):
            if survivor == case.eliminated_index:
                continue
            row = np.zeros(n_active, dtype=float)
            row[case.eliminated_index] = 1.0
            row[survivor] = -1.0
            rows.append(row)
            rhs.append(float(case.judge_share[survivor] - case.judge_share[case.eliminated_index]))
    return (
        np.vstack(rows) if rows else np.empty((0, n_active), dtype=float),
        np.asarray(rhs, dtype=float),
        np.ones((1, n_active), dtype=float),
        np.asarray([1.0], dtype=float),
        tuple((0.0, 1.0) for _ in range(n_active)),
    )


def append_inequalities(
    A_ub: np.ndarray,
    b_ub: np.ndarray,
    rows: Sequence[np.ndarray],
    rhs: Sequence[float],
) -> tuple[np.ndarray, np.ndarray]:
    """Append valid linear inequalities without mutating the base matrices."""
    if not rows:
        return A_ub.copy(), b_ub.copy()
    extra = np.vstack([np.asarray(row, dtype=float) for row in rows])
    return np.vstack([A_ub, extra]), np.concatenate([b_ub, np.asarray(rhs, dtype=float)])


def solve_case_bounds(
    A_ub: np.ndarray,
    b_ub: np.ndarray,
    A_eq: np.ndarray,
    b_eq: np.ndarray,
    bounds: Sequence[tuple[float, float]],
) -> tuple[np.ndarray, np.ndarray, bool]:
    solved = solve_preference_bounds(A_ub, b_ub, A_eq, b_eq, bounds)
    return solved.lower_bounds, solved.upper_bounds, bool(solved.feasible)


def mean_normalized_width(lower: np.ndarray, upper: np.ndarray) -> float:
    widths = np.asarray(upper, dtype=float) - np.asarray(lower, dtype=float)
    return float(np.nanmean(widths)) if widths.size else float("nan")


def covers_truth(lower: np.ndarray, upper: np.ndarray, truth: np.ndarray, *, tol: float = 1e-8) -> bool:
    return bool(np.all(np.asarray(truth) >= np.asarray(lower) - tol) and np.all(np.asarray(truth) <= np.asarray(upper) + tol))


def point_is_outcome_consistent(point: np.ndarray, case: SyntheticPreferenceCase, *, tol: float = 1e-10) -> bool:
    combined = np.asarray(point, dtype=float) + case.judge_share
    return bool(np.all(combined[case.eliminated_index] <= combined + tol))


def normalized_judge_point(case: SyntheticPreferenceCase) -> np.ndarray:
    """A transparent naive point baseline based only on observed judge shares."""
    point = np.asarray(case.judge_share, dtype=float).copy()
    return point / point.sum()
