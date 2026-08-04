from __future__ import annotations

import numpy as np
import pandas as pd

from src.identification_features import build_identification_features


def test_proxy_types_ranges_and_uncertainty() -> None:
    panel = pd.DataFrame(
        {
            "season": [3, 28, 28],
            "week": [1, 1, 1],
            "contestant_id": ["p", "r1", "r2"],
            "contestant_season_id": ["s3-p", "s28-r1", "s28-r2"],
            "contestant_name": ["P", "R1", "R2"],
            "partner_clean": ["A", "B", "C"],
            "age": [30, 40, 50],
            "industry_profession": ["x", "y", "z"],
            "returning_contestant": [False, False, True],
            "aggregation_regime": ["P", "R_plus", "R_plus"],
            "judge_total": [20.0, 30.0, 10.0],
            "judge_pct": [1.0, 0.75, 0.25],
            "active_status": [True, True, True],
            "eliminated_this_week": [False, False, True],
            "placement": [1, 1, 2],
        }
    )
    bounds = pd.DataFrame(
        {
            "season": [3],
            "week": [1],
            "contestant_id": ["p"],
            "lower_bound": [0.2],
            "upper_bound": [0.8],
            "midpoint": [0.5],
            "interval_width": [0.6],
            "feasible": [True],
        }
    )
    ranking = pd.DataFrame(
        {
            "season": [28, 28],
            "week": [1, 1],
            "regime": ["R_plus", "R_plus"],
            "contestant_id": ["r1", "r2"],
            "fan_rank_mean": [1.25, 1.75],
            "fan_rank_min": [1, 1],
            "fan_rank_max": [2, 2],
            "fan_rank_width": [1, 1],
            "normalized_fan_rank_width": [1.0, 1.0],
        }
    )
    summary = pd.DataFrame(
        {
            "season": [28],
            "week": [1],
            "regime": ["R_plus"],
            "ranking_entropy": [0.5],
            "normalized_ranking_entropy": [0.7],
            "feasible_fraction": [0.5],
        }
    )
    result = build_identification_features(panel, bounds, ranking, summary)
    assert result["public_appeal_proxy"].between(0, 1).all()
    assert (result["public_appeal_uncertainty"] >= 0).all()
    assert result.loc[result["contestant_id"].eq("p"), "public_appeal_type"].iloc[0] == "cardinal_interval_midpoint"
    assert set(result.loc[result["aggregation_regime"].eq("R_plus"), "public_appeal_type"]) == {"ordinal_rank_score"}
    r1 = result.loc[result["contestant_id"].eq("r1")].iloc[0]
    assert np.isclose(r1.public_appeal_proxy, 0.75)


def test_unavailable_p_set_is_not_imputed() -> None:
    panel = pd.DataFrame(
        {
            "season": [3], "week": [1], "contestant_id": ["p"],
            "contestant_season_id": ["s3-p"], "contestant_name": ["P"],
            "partner_clean": ["A"], "age": [30], "industry_profession": ["x"],
            "returning_contestant": [False], "aggregation_regime": ["P"],
            "judge_total": [20.0], "judge_pct": [1.0], "active_status": [True],
            "eliminated_this_week": [False], "placement": [1],
        }
    )
    bounds = pd.DataFrame(
        {"season": [3], "week": [1], "contestant_id": ["p"], "lower_bound": [np.nan],
         "upper_bound": [np.nan], "midpoint": [np.nan], "interval_width": [np.nan], "feasible": [False]}
    )
    ranking = pd.DataFrame(columns=["season","week","regime","contestant_id","fan_rank_mean","fan_rank_min","fan_rank_max","fan_rank_width","normalized_fan_rank_width"])
    summary = pd.DataFrame(columns=["season","week","regime","ranking_entropy","normalized_ranking_entropy","feasible_fraction"])
    result = build_identification_features(panel, bounds, ranking, summary)
    assert pd.isna(result.iloc[0].public_appeal_proxy)
    assert result.iloc[0].proxy_missing_reason == "p_identified_set_unavailable"
