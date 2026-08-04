"""Focused tests for DSS synthetic/scenario upgrade modules."""

from __future__ import annotations

import numpy as np

from src.discretion_identifiability import synthetic_discretion_frontier
from src.dss_common import generate_percentage_case
from src.synthetic_benchmark import run_synthetic_benchmark
from src.value_of_disclosure import evaluate_disclosure_case


def test_clean_synthetic_rule_aware_set_covers_known_truth() -> None:
    results = run_synthetic_benchmark(n_replications=60, n_active=5, noise_levels=(0.0,))
    row = results.loc[results["method"].eq("rule_aware_partial_identification")].iloc[0]
    assert row["coverage_rate"] == 1.0
    assert 0.0 <= row["average_feasible_set_width"] <= 1.0


def test_disclosure_scenarios_do_not_expand_beyond_elimination_only_in_one_case() -> None:
    case = generate_percentage_case(np.random.default_rng(31), n_active=5)
    result = evaluate_disclosure_case(case).set_index("disclosure_regime")
    base = result.loc["elimination_only", "mean_feasible_set_width"]
    assert result.loc["elimination_plus_top_k_public_rank", "mean_feasible_set_width"] <= base + 1e-10
    assert result.loc["full_public_vote_theoretical_upper_benchmark", "mean_feasible_set_width"] <= 1e-10


def test_synthetic_discretion_relaxation_is_nested() -> None:
    frontier = synthetic_discretion_frontier(n_active=6)
    counts = frontier["n_feasible_rankings"].to_numpy()
    widths = frontier["normalized_rank_width"].to_numpy()
    assert np.all(np.diff(counts) >= 0)
    assert np.all(np.diff(widths) >= -1e-12)
