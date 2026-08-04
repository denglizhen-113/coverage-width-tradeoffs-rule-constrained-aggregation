"""Unified features from cardinal and ordinal identified sets."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


REGIMES = ("P", "R", "R_plus")


def as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype(bool)
    return series.astype(str).str.strip().str.casefold().isin({"true", "1", "yes"})


def _require(frame: pd.DataFrame, columns: set[str], name: str) -> None:
    missing = sorted(columns.difference(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def build_identification_features(
    panel: pd.DataFrame,
    p_bounds: pd.DataFrame,
    ranking_contestant: pd.DataFrame,
    ranking_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Build one row per active season-week-contestant with typed proxies."""
    _require(
        panel,
        {
            "season",
            "week",
            "contestant_id",
            "contestant_season_id",
            "contestant_name",
            "partner_clean",
            "age",
            "industry_profession",
            "returning_contestant",
            "aggregation_regime",
            "judge_total",
            "judge_pct",
            "active_status",
            "eliminated_this_week",
            "placement",
        },
        "panel",
    )
    _require(
        p_bounds,
        {
            "season",
            "week",
            "contestant_id",
            "lower_bound",
            "upper_bound",
            "midpoint",
            "interval_width",
            "feasible",
        },
        "p_bounds",
    )
    _require(
        ranking_contestant,
        {
            "season",
            "week",
            "regime",
            "contestant_id",
            "fan_rank_mean",
            "fan_rank_min",
            "fan_rank_max",
            "fan_rank_width",
            "normalized_fan_rank_width",
        },
        "ranking_contestant",
    )
    _require(
        ranking_summary,
        {
            "season",
            "week",
            "regime",
            "ranking_entropy",
            "normalized_ranking_entropy",
            "feasible_fraction",
        },
        "ranking_summary",
    )

    active = panel.loc[as_bool(panel["active_status"])].copy()
    active = active.sort_values(["season", "week", "contestant_id"]).reset_index(
        drop=True
    )
    if active.duplicated(["season", "week", "contestant_id"]).any():
        raise ValueError("Active panel has duplicate season-week-contestant keys.")
    active["n_active"] = active.groupby(["season", "week"])[
        "contestant_id"
    ].transform("size")
    active["judge_rank"] = active.groupby(["season", "week"])["judge_total"].rank(
        ascending=False, method="average"
    )

    base_columns = [
        "season",
        "week",
        "contestant_id",
        "contestant_season_id",
        "contestant_name",
        "partner_clean",
        "age",
        "industry_profession",
        "returning_contestant",
        "aggregation_regime",
        "judge_total",
        "judge_pct",
        "judge_rank",
        "eliminated_this_week",
        "placement",
        "n_active",
    ]
    features = active[base_columns].copy()

    cardinal = p_bounds[
        [
            "season",
            "week",
            "contestant_id",
            "lower_bound",
            "upper_bound",
            "midpoint",
            "interval_width",
            "feasible",
        ]
    ].rename(
        columns={
            "lower_bound": "public_support_lower",
            "upper_bound": "public_support_upper",
            "midpoint": "public_support_midpoint",
            "interval_width": "public_support_width",
            "feasible": "p_week_feasible",
        }
    )
    if cardinal.duplicated(["season", "week", "contestant_id"]).any():
        raise ValueError("P bounds have duplicate season-week-contestant keys.")
    features = features.merge(
        cardinal, on=["season", "week", "contestant_id"], how="left", validate="1:1"
    )

    ordinal = ranking_contestant[
        [
            "season",
            "week",
            "regime",
            "contestant_id",
            "fan_rank_mean",
            "fan_rank_min",
            "fan_rank_max",
            "fan_rank_width",
            "normalized_fan_rank_width",
        ]
    ].rename(
        columns={
            "fan_rank_mean": "mean_fan_rank",
            "fan_rank_min": "min_fan_rank",
            "fan_rank_max": "max_fan_rank",
        }
    )
    if ordinal.duplicated(["season", "week", "contestant_id"]).any():
        raise ValueError("Ordinal contestant summaries have duplicate keys.")
    features = features.merge(
        ordinal.drop(columns="regime"),
        on=["season", "week", "contestant_id"],
        how="left",
        validate="1:1",
    )

    week_ordinal = ranking_summary[
        [
            "season",
            "week",
            "regime",
            "ranking_entropy",
            "normalized_ranking_entropy",
            "feasible_fraction",
        ]
    ]
    if week_ordinal.duplicated(["season", "week"]).any():
        raise ValueError("Ordinal weekly summaries have duplicate season-week keys.")
    features = features.merge(
        week_ordinal.drop(columns="regime"),
        on=["season", "week"],
        how="left",
        validate="m:1",
    )

    is_p = features["aggregation_regime"].eq("P")
    is_ordinal = features["aggregation_regime"].isin(["R", "R_plus"])
    finite_cardinal = features[
        ["public_support_lower", "public_support_upper", "public_support_midpoint"]
    ].notna().all(axis=1)
    features["public_support_available"] = (
        is_p & as_bool(features["p_week_feasible"]) & finite_cardinal
    )
    features["ordinal_support_available"] = (
        is_ordinal
        & features["mean_fan_rank"].notna()
        & features["normalized_fan_rank_width"].notna()
    )

    features["public_appeal_proxy"] = np.nan
    features.loc[
        features["public_support_available"], "public_appeal_proxy"
    ] = features.loc[
        features["public_support_available"], "public_support_midpoint"
    ]
    ordinal_mask = features["ordinal_support_available"]
    mean_fan_rank = pd.to_numeric(features["mean_fan_rank"], errors="coerce")
    active_count = pd.to_numeric(features["n_active"], errors="coerce")
    features.loc[ordinal_mask, "public_appeal_proxy"] = 1.0 - (
        mean_fan_rank.loc[ordinal_mask] - 1.0
    ) / (active_count.loc[ordinal_mask] - 1.0)

    features["public_appeal_uncertainty"] = np.nan
    features.loc[
        features["public_support_available"], "public_appeal_uncertainty"
    ] = features.loc[
        features["public_support_available"], "public_support_width"
    ]
    features.loc[ordinal_mask, "public_appeal_uncertainty"] = features.loc[
        ordinal_mask, "normalized_fan_rank_width"
    ].astype(float)

    features["public_appeal_type"] = "unavailable"
    features.loc[
        features["public_support_available"], "public_appeal_type"
    ] = "cardinal_interval_midpoint"
    features.loc[ordinal_mask, "public_appeal_type"] = "ordinal_rank_score"
    features["proxy_missing_reason"] = ""
    features.loc[
        is_p & ~features["public_support_available"], "proxy_missing_reason"
    ] = "p_identified_set_unavailable"
    features.loc[
        is_ordinal & ~features["ordinal_support_available"], "proxy_missing_reason"
    ] = "ordinal_identification_unavailable"

    features = features.drop(columns="p_week_feasible")
    validate_identification_features(features)
    return features


def validate_identification_features(features: pd.DataFrame) -> None:
    if features.empty:
        raise ValueError("Identification feature table is empty.")
    if features.duplicated(["season", "week", "contestant_id"]).any():
        raise ValueError("Identification features have duplicate keys.")
    if not set(features["aggregation_regime"].dropna()).issubset(REGIMES):
        raise ValueError("Identification features contain an unknown regime.")
    proxy = pd.to_numeric(features["public_appeal_proxy"], errors="coerce").dropna()
    if not proxy.between(0.0, 1.0).all():
        raise ValueError("public_appeal_proxy falls outside [0, 1].")
    uncertainty = pd.to_numeric(
        features["public_appeal_uncertainty"], errors="coerce"
    ).dropna()
    if (uncertainty < 0).any() or not uncertainty.between(0.0, 1.0).all():
        raise ValueError("public_appeal_uncertainty falls outside [0, 1].")
    p_types = set(
        features.loc[
            features["public_support_available"], "public_appeal_type"
        ].unique()
    )
    ordinal_types = set(
        features.loc[
            features["ordinal_support_available"], "public_appeal_type"
        ].unique()
    )
    if p_types.difference({"cardinal_interval_midpoint"}):
        raise ValueError("P proxy types are inconsistent.")
    if ordinal_types.difference({"ordinal_rank_score"}):
        raise ValueError("Ordinal proxy types are inconsistent.")


def feature_coverage(features: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for regime, frame in features.groupby("aggregation_regime", sort=False):
        available = frame["public_appeal_proxy"].notna()
        rows.append(
            {
                "regime": regime,
                "active_rows": len(frame),
                "proxy_available_rows": int(available.sum()),
                "proxy_missing_rows": int((~available).sum()),
                "contestant_seasons": frame["contestant_season_id"].nunique(),
                "mean_proxy": frame["public_appeal_proxy"].mean(),
                "mean_uncertainty": frame["public_appeal_uncertainty"].mean(),
            }
        )
    return pd.DataFrame(rows)
