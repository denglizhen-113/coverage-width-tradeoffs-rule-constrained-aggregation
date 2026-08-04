from __future__ import annotations

import numpy as np
from pathlib import Path

from src.robust_aggregation import pareto_mask


def test_pareto_front_identifies_non_dominated_points() -> None:
    values = np.asarray(
        [
            [0.8, 0.4, 0.7, 0.7],
            [0.4, 0.8, 0.7, 0.7],
            [0.5, 0.5, 0.5, 0.5],
            [0.9, 0.9, 0.9, 0.9],
        ]
    )
    mask = pareto_mask(values)
    assert mask.tolist() == [False, False, False, True]


def test_pareto_fixed_input_is_reproducible() -> None:
    rng = np.random.default_rng(42)
    values = rng.random((20, 4))
    assert np.array_equal(pareto_mask(values), pareto_mask(values))


def test_requested_stage_outputs_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    expected = [
        "data/processed/identification_features_long.csv",
        "data/processed/dynamic_public_appeal.csv",
        "outputs/tables/expert_crowd_divergence.csv",
        "outputs/tables/prediction_results.csv",
        "outputs/tables/counterfactual_results_by_season.csv",
        "outputs/tables/counterfactual_results_by_regime.csv",
        "outputs/tables/controversial_cases_counterfactual.csv",
        "outputs/tables/robust_aggregation_results.csv",
        "outputs/tables/pareto_frontier_points.csv",
        "outputs/figures/pareto_frontier.png",
        "outputs/logs/robust_aggregation_report.md",
    ]
    missing = [path for path in expected if not (root / path).is_file()]
    assert not missing
