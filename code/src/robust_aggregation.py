"""Evaluation and Pareto analysis for uncertainty-aware aggregation."""

from __future__ import annotations

import numpy as np
import pandas as pd


OBJECTIVES = [
    "expert_merit_alignment",
    "crowd_responsiveness",
    "robustness",
    "stability",
]


def pareto_mask(values: np.ndarray) -> np.ndarray:
    """Return non-dominated rows when every objective is maximized."""
    array = np.asarray(values, dtype=float)
    if array.ndim != 2:
        raise ValueError("Pareto values must be a two-dimensional array.")
    if not np.isfinite(array).all():
        raise ValueError("Pareto values must be finite.")
    keep = np.ones(len(array), dtype=bool)
    for index in range(len(array)):
        dominated = np.any(
            np.all(array >= array[index], axis=1)
            & np.any(array > array[index], axis=1)
        )
        keep[index] = not dominated
    return keep


def _season_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.loc[
        frame["mechanism"].eq("uncertainty_aware") & frame["applicable"].astype(bool)
    ].copy()
    if data.empty:
        raise ValueError("No applicable uncertainty-aware counterfactual rows.")
    data["expert_merit_alignment"] = (
        pd.to_numeric(data["expert_alignment"], errors="coerce") + 1.0
    ) / 2.0
    data["crowd_responsiveness"] = (
        pd.to_numeric(data["public_responsiveness"], errors="coerce") + 1.0
    ) / 2.0
    denominator = np.maximum(pd.to_numeric(data["n_contestants"], errors="coerce") - 1.0, 1.0)
    data["robustness"] = 1.0 - np.clip(
        pd.to_numeric(data["rank_shift_uncertainty"], errors="coerce") / denominator,
        0.0,
        1.0,
    )
    winner_stability = 1.0 - pd.to_numeric(data["winner_change_rate"], errors="coerce")
    finalist_stability = 1.0 - pd.to_numeric(
        data["finalist_set_change_rate"], errors="coerce"
    )
    data["stability"] = pd.concat(
        [winner_stability.rename("winner"), finalist_stability.rename("finalist")], axis=1
    ).mean(axis=1)
    for column in OBJECTIVES:
        data[column] = data[column].clip(0.0, 1.0)
    return data


def build_robust_aggregation_results(season_summary: pd.DataFrame) -> pd.DataFrame:
    data = _season_metrics(season_summary)
    rows = []
    for regime_label, frame in [("ALL", data), *list(data.groupby("regime", sort=False))]:
        for (lambda_value, gamma), group in frame.groupby(["lambda", "gamma"], sort=True):
            metrics = {column: float(group[column].mean()) for column in OBJECTIVES}
            vector = np.asarray(list(metrics.values()), dtype=float)
            harmonic = (
                float(len(vector) / np.sum(1.0 / np.clip(vector, 1e-6, None)))
                if np.isfinite(vector).all()
                else np.nan
            )
            rows.append(
                {
                    "regime": regime_label,
                    "lambda": float(lambda_value),
                    "gamma": float(gamma),
                    "n_seasons": group["season"].nunique(),
                    **metrics,
                    "outcome_change_rate": group["outcome_change_rate"].mean(),
                    "winner_change_rate": group["winner_change_rate"].mean(),
                    "finalist_set_change_rate": group["finalist_set_change_rate"].mean(),
                    "average_rank_shift": group["average_rank_shift"].mean(),
                    "rank_shift_uncertainty": group["rank_shift_uncertainty"].mean(),
                    "tradeoff_harmonic_mean": harmonic,
                    "notes": "All objectives scaled so higher is better; harmonic mean is descriptive, not a normative welfare function.",
                }
            )
    results = pd.DataFrame(rows)
    all_rows = results.loc[results["regime"].eq("ALL")].copy()
    valid = all_rows[OBJECTIVES].notna().all(axis=1)
    frontier = np.zeros(len(all_rows), dtype=bool)
    frontier[valid.to_numpy()] = pareto_mask(all_rows.loc[valid, OBJECTIVES].to_numpy())
    frontier_keys = set(
        zip(
            all_rows.loc[frontier, "lambda"],
            all_rows.loc[frontier, "gamma"],
        )
    )
    results["pareto_frontier_all_regimes"] = [
        (row.lambda_value, row.gamma) in frontier_keys
        for row in results.rename(columns={"lambda": "lambda_value"}).itertuples(index=False)
    ]
    return results.sort_values(["regime", "lambda", "gamma"]).reset_index(drop=True)


def frontier_points(results: pd.DataFrame) -> pd.DataFrame:
    return results.loc[
        results["regime"].eq("ALL") & results["pareto_frontier_all_regimes"]
    ].sort_values(["expert_merit_alignment", "crowd_responsiveness"]).reset_index(drop=True)
