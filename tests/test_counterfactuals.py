from __future__ import annotations

import numpy as np
import pandas as pd

from src.counterfactuals import (
    eliminated_set_consistent,
    parameter_grid,
    public_scenarios_for_week,
    strict_descending_ranks,
    uncertainty_aware_scores,
)


def test_counterfactual_ranking_direction_is_consistent() -> None:
    scores = uncertainty_aware_scores([0.8, 0.2], [0.6, 0.4], [0.1, 0.1], 0.5, 0.0)
    ranks = strict_descending_ranks(scores, ["a", "b"])
    assert scores[0] > scores[1]
    assert ranks.tolist() == [1, 2]
    assert eliminated_set_consistent(scores, [1], 1)
    assert not eliminated_set_consistent(scores, [0], 1)


def test_lambda_gamma_grid_is_complete() -> None:
    grid = parameter_grid()
    assert len(grid) == 20
    assert (0.0, 0.0) in grid
    assert (1.0, 1.0) in grid


def test_uncertainty_penalty_lowers_score() -> None:
    no_penalty = uncertainty_aware_scores([0.5], [0.5], [0.8], 0.5, 0.0)
    penalty = uncertainty_aware_scores([0.5], [0.5], [0.8], 0.5, 1.0)
    assert penalty[0] < no_penalty[0]


def test_strict_rank_tie_break_is_reproducible() -> None:
    first = strict_descending_ranks([0.5, 0.5, 0.2], ["b", "a", "c"])
    second = strict_descending_ranks([0.5, 0.5, 0.2], ["b", "a", "c"])
    assert np.array_equal(first, second)
    assert first.tolist() == [2, 1, 3]


def test_feasible_ranking_scenarios_use_fixed_seed() -> None:
    week = pd.DataFrame(
        {
            "season": [28, 28, 28],
            "week": [2, 2, 2],
            "contestant_id": ["a", "b", "c"],
            "aggregation_regime": ["R_plus"] * 3,
            "mean_fan_rank": [1.5, 2.0, 2.5],
            "dynamic_public_appeal": [0.8, 0.5, 0.2],
        }
    )
    detail_rows = []
    for permutation_id, ranks in ((1, [1, 2, 3]), (2, [2, 1, 3]), (3, [1, 3, 2])):
        for contestant_id, rank in zip(("a", "b", "c"), ranks):
            detail_rows.append(
                {
                    "permutation_id": permutation_id,
                    "contestant_id": contestant_id,
                    "fan_rank": rank,
                    "is_feasible": True,
                }
            )
    detail = pd.DataFrame(detail_rows)
    first = public_scenarios_for_week(week, detail, seed=77, max_sampled=2)
    second = public_scenarios_for_week(week, detail, seed=77, max_sampled=2)
    assert [item.scenario_id for item in first] == [item.scenario_id for item in second]
    assert all(
        np.array_equal(left.fan_rank, right.fan_rank)
        for left, right in zip(first, second)
    )
