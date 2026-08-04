from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.ranking_identification import (
    TIE_POLICIES,
    build_week_spec,
    compute_judge_ranks,
    consistency_masks,
    exact_permutation_batches,
    identify_week,
    orders_to_fan_ranks,
    seeded_rng,
    uniform_permutation_batches,
)


def make_week(
    *,
    regime: str = "R",
    judge_totals: tuple[float, ...] = (20.0, 20.0, 20.0),
    eliminated: tuple[int, ...] = (2,),
    finale: bool = False,
    placements: tuple[float, ...] | None = None,
) -> pd.DataFrame:
    n_active = len(judge_totals)
    if placements is None:
        placements = tuple(range(1, n_active + 1))
    return pd.DataFrame(
        {
            "season": [1] * n_active,
            "week": [2] * n_active,
            "contestant_id": [f"c{i}" for i in range(n_active)],
            "contestant_name": [f"Contestant {i}" for i in range(n_active)],
            "judge_total": judge_totals,
            "active_status": [True] * n_active,
            "eliminated_this_week": [i in eliminated for i in range(n_active)],
            "withdrew_this_week": [False] * n_active,
            "no_elimination_week": [not eliminated and not finale] * n_active,
            "double_elimination_week": [len(eliminated) > 1] * n_active,
            "finale_week": [finale] * n_active,
            "placement": placements,
            "aggregation_regime": [regime] * n_active,
        }
    )


def all_fan_ranks(n_active: int) -> np.ndarray:
    orders = np.vstack([batch for _, batch in exact_permutation_batches(n_active)])
    return orders_to_fan_ranks(orders)


def test_judge_rank_direction_is_descending_score() -> None:
    ranks = compute_judge_ranks([10.0, 30.0, 20.0], "average_rank")
    assert ranks.tolist() == [3.0, 1.0, 2.0]


def test_single_elimination_direct_r_constraint() -> None:
    spec = build_week_spec(make_week(), "average_rank")
    fan_ranks = np.asarray([[1, 2, 3], [3, 2, 1]])
    direct, weak = consistency_masks(spec, fan_ranks)
    assert direct.tolist() == [True, False]
    assert weak.tolist() == [True, False]


def test_rplus_bottom_two_is_strictly_weaker_than_direct_r() -> None:
    spec = build_week_spec(make_week(regime="R_plus"), "average_rank")
    direct, weak = consistency_masks(spec, all_fan_ranks(3))
    assert int(direct.sum()) == 2
    assert int(weak.sum()) == 4
    assert np.all(~direct | weak)


def test_rplus_feasible_count_is_not_smaller_than_direct_count() -> None:
    spec = build_week_spec(make_week(regime="R_plus"), "average_rank")
    result = identify_week(spec, detail_limit=0)
    assert result.summary["n_feasible_permutations"] >= result.summary[
        "n_feasible_direct_R_like"
    ]
    assert result.summary["identifiability_loss_ratio"] == pytest.approx(2.0)


def test_double_elimination_is_supported() -> None:
    week = make_week(
        regime="R_plus",
        judge_totals=(20.0, 20.0, 20.0, 20.0),
        eliminated=(2, 3),
    )
    result = identify_week(build_week_spec(week, "average_rank"), detail_limit=20)
    assert result.summary["n_feasible_permutations"] >= result.summary[
        "n_feasible_direct_R_like"
    ]
    assert result.summary["n_feasible_permutations"] > 0


@pytest.mark.parametrize("tie_policy", TIE_POLICIES)
def test_all_tie_policies_are_supported(tie_policy: str) -> None:
    ranks = compute_judge_ranks([30.0, 20.0, 20.0, 10.0], tie_policy)
    assert np.isfinite(ranks).all()
    assert ranks[0] == 1
    assert ranks[1] == ranks[2]


def test_tie_policy_values_match_documented_definitions() -> None:
    values = [30.0, 20.0, 20.0, 10.0]
    assert compute_judge_ranks(values, "average_rank").tolist() == [1, 2.5, 2.5, 4]
    assert compute_judge_ranks(values, "min_rank").tolist() == [1, 2, 2, 4]
    assert compute_judge_ranks(values, "dense_rank").tolist() == [1, 2, 2, 3]
    assert compute_judge_ranks(values, "competition_rank").tolist() == [1, 2, 2, 4]


def test_fixed_seed_sampling_is_reproducible() -> None:
    first = np.vstack(
        [
            batch
            for _, batch in uniform_permutation_batches(
                11, 200, seeded_rng(77, 4, 2, 0), batch_size=37
            )
        ]
    )
    second = np.vstack(
        [
            batch
            for _, batch in uniform_permutation_batches(
                11, 200, seeded_rng(77, 4, 2, 0), batch_size=37
            )
        ]
    )
    assert np.array_equal(first, second)


def test_feasible_fraction_and_normalized_uncertainty_are_bounded() -> None:
    spec = build_week_spec(make_week(regime="R_plus"), "average_rank")
    result = identify_week(spec, detail_limit=0)
    assert 0.0 <= result.summary["feasible_fraction"] <= 1.0
    assert 0.0 <= result.summary["normalized_rank_width"] <= 1.0
    assert 0.0 <= result.summary["normalized_ranking_entropy"] <= 1.0


def test_incomplete_finale_order_is_logged_and_not_forced() -> None:
    week = make_week(
        finale=True,
        eliminated=(),
        placements=(1.0, 2.0, 2.0),
    )
    spec = build_week_spec(week, "average_rank")
    result = identify_week(spec, detail_limit=0)
    assert not spec.finale_order_available
    assert spec.skip_reason == "finale_placement_missing_or_nonunique"
    assert result.summary["n_feasible_permutations"] == 6
