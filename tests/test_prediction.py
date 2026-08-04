from __future__ import annotations

import numpy as np
import pandas as pd

from src.prediction import (
    build_prediction_frame,
    random_baseline,
)


def synthetic_dynamic() -> pd.DataFrame:
    rows = []
    for week in (1, 2, 3):
        for index, contestant in enumerate(("a", "b", "c")):
            rows.append(
                {
                    "season": 1,
                    "week": week,
                    "contestant_id": contestant,
                    "contestant_name": contestant.upper(),
                    "aggregation_regime": "R",
                    "judge_pct": [0.5, 0.3, 0.2][index],
                    "judge_rank": index + 1,
                    "public_appeal_proxy": 0.8 - 0.2 * index + 0.01 * week,
                    "public_appeal_uncertainty": 0.5,
                    "dynamic_public_appeal": 0.75 - 0.2 * index + 0.01 * week,
                    "eliminated_this_week": week == 2 and contestant == "c",
                    "n_active": 3,
                    "age": 30 + index,
                    "returning_contestant": False,
                }
            )
    return pd.DataFrame(rows)


def synthetic_weeks() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "season": [1, 1, 1],
            "week": [1, 2, 3],
            "eliminated_count": [0, 1, 0],
            "no_elimination_week": [True, False, True],
            "double_elimination_week": [False, False, False],
            "finale_week": [False, False, True],
        }
    )


def test_lag_features_use_only_prior_weeks() -> None:
    frame = build_prediction_frame(synthetic_dynamic(), synthetic_weeks())
    row = frame.loc[frame["week"].eq(2) & frame["contestant_id"].eq("a")].iloc[0]
    prior = frame.loc[frame["week"].eq(1) & frame["contestant_id"].eq("a")].iloc[0]
    assert row.lag_source_week == 1
    assert row.public_appeal_proxy_lag1 == prior.public_appeal_proxy
    assert row.lag_source_week < row.week


def test_prediction_label_matches_single_elimination() -> None:
    frame = build_prediction_frame(synthetic_dynamic(), synthetic_weeks())
    event = frame.loc[frame["eligible_single_elimination"]]
    assert event["prediction_label"].sum() == 1
    assert event.loc[event["prediction_label"].eq(1), "contestant_id"].iloc[0] == "c"


def test_random_baseline_fixed_seed_is_reproducible() -> None:
    frame = build_prediction_frame(synthetic_dynamic(), synthetic_weeks())
    event = frame.loc[frame["week"].eq(2)].reset_index(drop=True)
    first_probability, first_rank = random_baseline(event, 123)
    second_probability, second_rank = random_baseline(event, 123)
    assert np.allclose(first_probability, second_probability)
    assert np.allclose(first_rank, second_rank)
    assert np.isclose(first_probability.sum(), 1.0)
