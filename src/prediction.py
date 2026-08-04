"""Leakage-controlled elimination prediction utilities."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterator

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


EVENT_KEYS = ["season", "week"]
MODEL_SPECS = {
    "random_uniform": {"kind": "random", "features": [], "same_week": False},
    "lowest_judge_same_week": {"kind": "judge_heuristic", "features": ["judge_rank"], "same_week": True},
    "judge_only_logistic_same_week": {"kind": "logistic", "features": ["judge_pct", "judge_rank", "week", "n_active", "age", "returning_numeric", "aggregation_regime"], "same_week": True},
    "public_proxy_lag_logistic": {"kind": "logistic", "features": ["public_appeal_proxy_lag1", "week", "n_active", "age", "returning_numeric", "aggregation_regime"], "same_week": False},
    "dynamic_public_lag_logistic": {"kind": "logistic", "features": ["dynamic_public_appeal_lag1", "week", "n_active", "age", "returning_numeric", "aggregation_regime"], "same_week": False},
    "combined_lag_logistic": {"kind": "logistic", "features": ["judge_pct_lag1", "judge_rank_lag1", "dynamic_public_appeal_lag1", "week", "n_active", "age", "returning_numeric", "aggregation_regime"], "same_week": False},
    "uncertainty_aware_lag_logistic": {"kind": "logistic", "features": ["judge_pct_lag1", "judge_rank_lag1", "dynamic_public_appeal_lag1", "public_appeal_uncertainty_lag1", "reliability_adjusted_dynamic_lag", "previous_elimination_risk_proxy", "week", "n_active", "age", "returning_numeric", "aggregation_regime"], "same_week": False},
}


@dataclass(frozen=True)
class Fold:
    name: str
    train_seasons: tuple[int, ...]
    test_season: int


def _as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype(bool)
    return series.astype(str).str.strip().str.casefold().isin({"true", "1", "yes"})


def build_prediction_frame(dynamic: pd.DataFrame, week_level: pd.DataFrame) -> pd.DataFrame:
    required = {
        "season",
        "week",
        "contestant_id",
        "contestant_name",
        "aggregation_regime",
        "judge_pct",
        "judge_rank",
        "public_appeal_proxy",
        "public_appeal_uncertainty",
        "dynamic_public_appeal",
        "eliminated_this_week",
        "n_active",
        "age",
        "returning_contestant",
    }
    missing = sorted(required.difference(dynamic.columns))
    if missing:
        raise ValueError(f"dynamic data are missing required columns: {missing}")
    week_required = {
        "season",
        "week",
        "eliminated_count",
        "no_elimination_week",
        "double_elimination_week",
        "finale_week",
    }
    week_missing = sorted(week_required.difference(week_level.columns))
    if week_missing:
        raise ValueError(f"week_level is missing required columns: {week_missing}")
    data = dynamic.copy().sort_values(["season", "contestant_id", "week"])
    if data.duplicated(["season", "week", "contestant_id"]).any():
        raise ValueError("Dynamic data have duplicate season-week-contestant keys.")
    data["returning_numeric"] = _as_bool(data["returning_contestant"]).astype(float)
    group = data.groupby(["season", "contestant_id"], sort=False)
    lag_map = {
        "judge_pct": "judge_pct_lag1",
        "judge_rank": "judge_rank_lag1",
        "public_appeal_proxy": "public_appeal_proxy_lag1",
        "dynamic_public_appeal": "dynamic_public_appeal_lag1",
        "public_appeal_uncertainty": "public_appeal_uncertainty_lag1",
        "n_active": "n_active_lag1",
        "week": "lag_source_week",
    }
    for source, target in lag_map.items():
        data[target] = group[source].shift(1)
    data["history_available"] = (
        data["lag_source_week"].notna() & data["lag_source_week"].lt(data["week"])
    )
    judge_risk = (data["judge_rank_lag1"] - 1.0) / np.maximum(
        data["n_active_lag1"] - 1.0, 1.0
    )
    public_risk = 1.0 - data["dynamic_public_appeal_lag1"]
    data["previous_elimination_risk_proxy"] = pd.concat(
        [judge_risk.rename("judge"), public_risk.rename("public")], axis=1
    ).mean(axis=1)
    data["reliability_adjusted_dynamic_lag"] = data[
        "dynamic_public_appeal_lag1"
    ] * (1.0 - data["public_appeal_uncertainty_lag1"].clip(0.0, 1.0))

    event_info = week_level[list(week_required)].copy()
    data = data.merge(event_info, on=EVENT_KEYS, how="left", validate="m:1")
    data["prediction_label"] = _as_bool(data["eliminated_this_week"]).astype(int)
    data["eligible_single_elimination"] = (
        data["eliminated_count"].eq(1)
        & ~_as_bool(data["no_elimination_week"])
        & ~_as_bool(data["double_elimination_week"])
        & ~_as_bool(data["finale_week"])
    )
    data["history_complete_event"] = data.groupby(EVENT_KEYS)[
        "history_available"
    ].transform("all")
    eligible = data.loc[data["eligible_single_elimination"]]
    label_counts = eligible.groupby(EVENT_KEYS)["prediction_label"].sum()
    if not label_counts.eq(1).all():
        raise ValueError("Eligible prediction events must contain exactly one label.")
    if (
        data.loc[data["history_available"], "lag_source_week"]
        >= data.loc[data["history_available"], "week"]
    ).any():
        raise ValueError("Lag construction leaked current or future weeks.")
    return data.sort_values(["season", "week", "contestant_id"]).reset_index(drop=True)


def validation_folds(frame: pd.DataFrame, scheme: str) -> Iterator[Fold]:
    seasons = tuple(sorted(int(value) for value in frame["season"].unique()))
    if scheme == "leave_one_season_out":
        for test in seasons:
            train = tuple(value for value in seasons if value != test)
            if train:
                yield Fold(f"holdout_s{test}", train, test)
    elif scheme == "forward_chaining":
        for test in seasons:
            train = tuple(value for value in seasons if value < test)
            if train:
                yield Fold(f"forward_s{test}", train, test)
    else:
        raise ValueError(f"Unknown validation scheme: {scheme}")


def _softmax_by_event(frame: pd.DataFrame, scores: np.ndarray) -> np.ndarray:
    result = np.zeros(len(frame), dtype=float)
    score_series = pd.Series(np.asarray(scores, dtype=float), index=frame.index)
    for _, indices in frame.groupby(EVENT_KEYS, sort=False).groups.items():
        positions = frame.index.get_indexer(indices)
        values = score_series.loc[indices].to_numpy(dtype=float)
        values = values - np.nanmax(values)
        probabilities = np.exp(np.clip(values, -40, 40))
        total = probabilities.sum()
        result[positions] = probabilities / total if total > 0 else 1.0 / len(values)
    return result


def fit_logistic_probabilities(
    train: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    categorical = [column for column in features if column == "aggregation_regime"]
    numeric = [column for column in features if column not in categorical]
    transformers = []
    if numeric:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric,
            )
        )
    if categorical:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            )
        )
    preprocessor = ColumnTransformer(transformers, remainder="drop")
    model = Pipeline(
        [
            ("preprocess", preprocessor),
            (
                "logistic",
                LogisticRegression(
                    max_iter=2_000,
                    class_weight="balanced",
                    random_state=seed,
                    solver="lbfgs",
                ),
            ),
        ]
    )
    model.fit(train[features], train["prediction_label"])
    raw = model.predict_proba(test[features])[:, 1]
    probabilities = _softmax_by_event(test, np.log(np.clip(raw, 1e-12, 1.0)))
    return probabilities, raw


def random_baseline(frame: pd.DataFrame, seed: int) -> tuple[np.ndarray, np.ndarray]:
    probabilities = np.zeros(len(frame), dtype=float)
    rank_scores = np.zeros(len(frame), dtype=float)
    for (season, week), indices in frame.groupby(EVENT_KEYS, sort=False).groups.items():
        positions = frame.index.get_indexer(indices)
        rng = np.random.default_rng(np.random.SeedSequence([seed, int(season), int(week)]))
        probabilities[positions] = 1.0 / len(indices)
        rank_scores[positions] = rng.random(len(indices))
    return probabilities, rank_scores


def judge_heuristic(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    scores = pd.to_numeric(frame["judge_rank"], errors="coerce").to_numpy(dtype=float)
    probabilities = _softmax_by_event(frame, scores)
    return probabilities, scores


def evaluate_prediction_rows(rows: pd.DataFrame) -> dict[str, float | int]:
    if rows.empty:
        return {
            "n_events": 0,
            "n_rows": 0,
            "accuracy": np.nan,
            "top2_accuracy": np.nan,
            "brier_score": np.nan,
            "log_loss": np.nan,
        }
    accuracies = []
    top2 = []
    log_losses = []
    for _, group in rows.groupby(EVENT_KEYS, sort=False):
        ordered = group.sort_values(
            ["prediction_rank_score", "contestant_id"], ascending=[False, True]
        )
        actual = str(group.loc[group["prediction_label"].eq(1), "contestant_id"].iloc[0])
        accuracies.append(str(ordered.iloc[0]["contestant_id"]) == actual)
        top2.append(actual in set(ordered.head(2)["contestant_id"].astype(str)))
        actual_probability = float(
            group.loc[group["prediction_label"].eq(1), "risk_probability"].iloc[0]
        )
        log_losses.append(-math.log(max(actual_probability, 1e-12)))
    brier = float(
        np.mean((rows["risk_probability"] - rows["prediction_label"]) ** 2)
    )
    return {
        "n_events": len(accuracies),
        "n_rows": len(rows),
        "accuracy": float(np.mean(accuracies)),
        "top2_accuracy": float(np.mean(top2)),
        "brier_score": brier,
        "log_loss": float(np.mean(log_losses)),
    }


def run_prediction_validation(
    prediction_frame: pd.DataFrame,
    schemes: tuple[str, ...] = ("leave_one_season_out", "forward_chaining"),
    seed: int = 20260714,
) -> pd.DataFrame:
    evaluation = prediction_frame.loc[
        prediction_frame["eligible_single_elimination"]
        & prediction_frame["history_complete_event"]
    ].copy()
    if evaluation.empty:
        raise ValueError("No history-complete single-elimination events are available.")
    output: list[pd.DataFrame] = []
    for scheme in schemes:
        for fold in validation_folds(evaluation, scheme):
            train = evaluation.loc[evaluation["season"].isin(fold.train_seasons)].copy()
            test = evaluation.loc[evaluation["season"].eq(fold.test_season)].copy()
            if train.empty or test.empty or train["prediction_label"].nunique() < 2:
                continue
            for model_name, spec in MODEL_SPECS.items():
                if spec["kind"] == "random":
                    probabilities, rank_scores = random_baseline(test, seed)
                elif spec["kind"] == "judge_heuristic":
                    probabilities, rank_scores = judge_heuristic(test)
                else:
                    probabilities, rank_scores = fit_logistic_probabilities(
                        train, test, list(spec["features"]), seed
                    )
                result = test[
                    [
                        "season",
                        "week",
                        "contestant_id",
                        "contestant_name",
                        "aggregation_regime",
                        "prediction_label",
                    ]
                ].copy()
                result["validation_scheme"] = scheme
                result["fold"] = fold.name
                result["model"] = model_name
                result["same_week_baseline"] = bool(spec["same_week"])
                result["risk_probability"] = probabilities
                result["prediction_rank_score"] = rank_scores
                output.append(result)
    if not output:
        raise ValueError("No prediction folds were evaluated.")
    return pd.concat(output, ignore_index=True)


def summarize_predictions(predictions: pd.DataFrame, by_regime: bool = False) -> pd.DataFrame:
    group_columns = ["validation_scheme", "model", "same_week_baseline"]
    if by_regime:
        group_columns.append("aggregation_regime")
    rows: list[dict[str, Any]] = []
    for keys, group in predictions.groupby(group_columns, sort=False):
        values = keys if isinstance(keys, tuple) else (keys,)
        base = dict(zip(group_columns, values))
        metrics = evaluate_prediction_rows(group)
        base.update(metrics)
        base["n_folds"] = group["fold"].nunique()
        rows.append(base)
    return pd.DataFrame(rows).sort_values(group_columns).reset_index(drop=True)


def calibration_table(predictions: pd.DataFrame) -> pd.DataFrame:
    bins = np.asarray([0.0, 0.05, 0.10, 0.20, 0.40, 0.60, 1.0000001])
    frame = predictions.copy()
    frame["probability_bin"] = pd.cut(
        frame["risk_probability"], bins=bins, right=False, include_lowest=True
    ).astype(str)
    return (
        frame.groupby(["validation_scheme", "model", "probability_bin"], observed=True)
        .agg(
            n_rows=("prediction_label", "size"),
            mean_predicted_risk=("risk_probability", "mean"),
            observed_elimination_rate=("prediction_label", "mean"),
        )
        .reset_index()
    )
