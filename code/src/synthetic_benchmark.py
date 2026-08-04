"""Known-truth synthetic benchmark for rule-aware partial identification."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from src.dss_common import (
    SyntheticPreferenceCase,
    base_percentage_constraints,
    covers_truth,
    generate_percentage_case,
    mean_normalized_width,
    normalized_judge_point,
    point_is_outcome_consistent,
    solve_case_bounds,
)


BASE_SEED = 20260716


def _point_metrics(point: np.ndarray, case: SyntheticPreferenceCase) -> dict[str, float | bool]:
    error = float(np.abs(point - case.public_preference).mean())
    covered = bool(np.allclose(point, case.public_preference, atol=1e-8, rtol=0.0))
    return {
        "coverage": float(covered),
        "mean_width": 0.0,
        "false_certainty": float(not covered),
        "baseline_error": error,
        "outcome_consistent": float(point_is_outcome_consistent(point, case)),
    }


def evaluate_case(case: SyntheticPreferenceCase) -> list[dict[str, float | str | bool]]:
    """Evaluate rule-aware, rule-agnostic, point, and oracle baselines."""
    rows: list[dict[str, float | str | bool]] = []
    methods = {
        "rule_aware_partial_identification": True,
        "rule_agnostic_partial_identification": False,
    }
    for method, include_rule in methods.items():
        args = base_percentage_constraints(case, include_elimination_constraint=include_rule)
        lower, upper, feasible = solve_case_bounds(*args)
        rows.append(
            {
                "method": method,
                "coverage": float(feasible and covers_truth(lower, upper, case.public_preference)),
                "mean_width": mean_normalized_width(lower, upper) if feasible else np.nan,
                "false_certainty": 0.0,
                "baseline_error": np.nan,
                "outcome_consistent": float(feasible),
                "feasible": feasible,
            }
        )
    judge_point = normalized_judge_point(case)
    for name, point in {
        "naive_point_estimation": judge_point,
        "prediction_only_judge_proxy": judge_point,
        "full_disclosure_oracle_synthetic_only": case.public_preference,
    }.items():
        metrics = _point_metrics(point, case)
        rows.append({"method": name, "feasible": True, **metrics})
    return rows


def run_synthetic_benchmark(
    *,
    n_replications: int = 250,
    n_active: int = 5,
    seed: int = BASE_SEED,
    noise_levels: Iterable[float] = (0.0, 0.1),
) -> pd.DataFrame:
    """Run deterministic clean and noisy-outcome synthetic benchmark conditions."""
    if n_replications < 1:
        raise ValueError("n_replications must be positive.")
    rows: list[dict[str, float | str | int | bool]] = []
    for noise_probability in noise_levels:
        rng = np.random.default_rng(seed + int(round(float(noise_probability) * 1_000)))
        condition = "rule_consistent" if float(noise_probability) == 0.0 else "outcome_noise_stress_test"
        for replication in range(n_replications):
            case = generate_percentage_case(
                rng,
                n_active=n_active,
                outcome_noise_probability=float(noise_probability),
            )
            for result in evaluate_case(case):
                rows.append(
                    {
                        "condition": condition,
                        "outcome_noise_probability": float(noise_probability),
                        "replication": replication,
                        "n_active": n_active,
                        "observed_outcome_noise": case.observed_outcome_noise,
                        **result,
                    }
                )
    detailed = pd.DataFrame(rows)
    grouped = detailed.groupby(["condition", "outcome_noise_probability", "method"], as_index=False).agg(
        n_replications=("replication", "nunique"),
        coverage_rate=("coverage", "mean"),
        average_feasible_set_width=("mean_width", "mean"),
        false_certainty_rate=("false_certainty", "mean"),
        baseline_error=("baseline_error", "mean"),
        outcome_consistency_rate=("outcome_consistent", "mean"),
        feasible_rate=("feasible", "mean"),
    )
    grouped["evidence_type"] = "synthetic known-truth benchmark"
    grouped["interpretation_boundary"] = (
        "Coverage concerns simulated latent preferences only; it does not establish empirical preference recovery."
    )
    return grouped.sort_values(["condition", "method"], kind="stable").reset_index(drop=True)
