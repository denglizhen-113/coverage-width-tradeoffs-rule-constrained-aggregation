"""Independent truncated-prior Bayesian latent-preference baselines."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PosteriorIntervalResult:
    lower: np.ndarray
    upper: np.ndarray
    center: np.ndarray
    accepted_count: int
    feasible: bool
    status: str


def _interval_from_states(
    states: np.ndarray,
    *,
    lower_probability: float,
    upper_probability: float,
    min_accepted: int,
) -> PosteriorIntervalResult:
    states = np.asarray(states, dtype=float)
    n_dimensions = states.shape[1] if states.ndim == 2 else 0
    if states.ndim != 2 or len(states) < min_accepted:
        return PosteriorIntervalResult(
            lower=np.full(n_dimensions, np.nan),
            upper=np.full(n_dimensions, np.nan),
            center=np.full(n_dimensions, np.nan),
            accepted_count=int(len(states)) if states.ndim == 2 else 0,
            feasible=False,
            status="insufficient_posterior_draws",
        )
    return PosteriorIntervalResult(
        lower=np.quantile(states, lower_probability, axis=0, method="linear"),
        upper=np.quantile(states, upper_probability, axis=0, method="linear"),
        center=states.mean(axis=0),
        accepted_count=int(len(states)),
        feasible=True,
        status="ok",
    )


def truncated_dirichlet_interval(
    prior_draws: np.ndarray,
    *,
    A_ub: np.ndarray,
    b_ub: np.ndarray,
    lower_probability: float = 0.025,
    upper_probability: float = 0.975,
    min_accepted: int = 100,
    feasibility_tolerance: float = 1e-10,
) -> PosteriorIntervalResult:
    """Filter a fixed Dirichlet draw bank using observed linear constraints."""
    draws = np.asarray(prior_draws, dtype=float)
    if draws.ndim != 2:
        raise ValueError("prior_draws must be a two-dimensional array.")
    A_ub = np.asarray(A_ub, dtype=float).reshape(-1, draws.shape[1])
    b_ub = np.asarray(b_ub, dtype=float).reshape(-1)
    mask = np.ones(len(draws), dtype=bool)
    if len(A_ub):
        mask &= np.all(
            draws @ A_ub.T <= b_ub.reshape(1, -1) + feasibility_tolerance,
            axis=1,
        )
    return _interval_from_states(
        draws[mask],
        lower_probability=lower_probability,
        upper_probability=upper_probability,
        min_accepted=min_accepted,
    )


def exact_rank_posterior_interval(
    compatible_ranks: np.ndarray,
    *,
    lower_probability: float = 0.025,
    upper_probability: float = 0.975,
) -> PosteriorIntervalResult:
    """Compute exact equal-tail intervals under a uniform ranking posterior."""
    return _interval_from_states(
        np.asarray(compatible_ranks, dtype=float),
        lower_probability=lower_probability,
        upper_probability=upper_probability,
        min_accepted=1,
    )
