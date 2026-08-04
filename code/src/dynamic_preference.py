"""Dynamic smoothing for partially identified public-appeal proxies."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


def exponential_smooth(values: Sequence[float], alpha: float) -> tuple[np.ndarray, np.ndarray]:
    """Smooth observed values and carry the prior state over missing weeks."""
    if not 0 < alpha <= 1:
        raise ValueError("alpha must lie in (0, 1].")
    values_array = np.asarray(values, dtype=float)
    output = np.full(len(values_array), np.nan, dtype=float)
    used = np.zeros(len(values_array), dtype=bool)
    state = np.nan
    for index, value in enumerate(values_array):
        if np.isfinite(value):
            state = value if not np.isfinite(state) else alpha * value + (1 - alpha) * state
            used[index] = True
        output[index] = state
    return output, used


def uncertainty_weighted_smooth(
    values: Sequence[float], uncertainties: Sequence[float], alpha: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Reduce the update weight as identification uncertainty increases."""
    if not 0 < alpha <= 1:
        raise ValueError("alpha must lie in (0, 1].")
    values_array = np.asarray(values, dtype=float)
    uncertainty_array = np.asarray(uncertainties, dtype=float)
    if values_array.shape != uncertainty_array.shape:
        raise ValueError("values and uncertainties must have the same shape.")
    output = np.full(len(values_array), np.nan, dtype=float)
    effective_alpha = np.full(len(values_array), np.nan, dtype=float)
    used = np.zeros(len(values_array), dtype=bool)
    state = np.nan
    for index, (value, uncertainty) in enumerate(zip(values_array, uncertainty_array)):
        if np.isfinite(value):
            bounded = float(np.clip(uncertainty, 0.0, 1.0)) if np.isfinite(uncertainty) else 1.0
            current_alpha = alpha / (1.0 + bounded)
            effective_alpha[index] = current_alpha
            state = value if not np.isfinite(state) else current_alpha * value + (1 - current_alpha) * state
            used[index] = True
        output[index] = state
    return output, used, effective_alpha


def build_dynamic_public_appeal(
    features: pd.DataFrame, alpha: float = 0.5
) -> pd.DataFrame:
    required = {
        "season",
        "week",
        "contestant_id",
        "contestant_season_id",
        "contestant_name",
        "aggregation_regime",
        "public_appeal_proxy",
        "public_appeal_uncertainty",
    }
    missing = sorted(required.difference(features.columns))
    if missing:
        raise ValueError(f"features are missing required columns: {missing}")
    if features.duplicated(["season", "week", "contestant_id"]).any():
        raise ValueError("features contain duplicate season-week-contestant keys.")

    output_frames: list[pd.DataFrame] = []
    ordered = features.sort_values(["season", "contestant_id", "week"]).copy()
    for _, group in ordered.groupby(["season", "contestant_id"], sort=False):
        frame = group.copy()
        raw = pd.to_numeric(frame["public_appeal_proxy"], errors="coerce").to_numpy()
        uncertainty = pd.to_numeric(
            frame["public_appeal_uncertainty"], errors="coerce"
        ).to_numpy()
        smooth_05, used = exponential_smooth(raw, alpha)
        smooth_03, _ = exponential_smooth(raw, 0.3)
        smooth_07, _ = exponential_smooth(raw, 0.7)
        weighted, weighted_used, effective = uncertainty_weighted_smooth(
            raw, uncertainty, alpha
        )
        frame["raw_public_appeal_proxy"] = raw
        frame["smoothed_public_appeal_alpha_05"] = smooth_05
        frame["smoothed_public_appeal_alpha_03"] = smooth_03
        frame["smoothed_public_appeal_alpha_07"] = smooth_07
        frame["uncertainty_weighted_public_appeal"] = weighted
        frame["dynamic_public_appeal"] = weighted
        frame["dynamic_observation_used"] = used & weighted_used
        frame["effective_alpha"] = effective
        output_frames.append(frame)
    output = pd.concat(output_frames, ignore_index=True).sort_values(
        ["season", "week", "contestant_id"]
    )
    dynamic = output["dynamic_public_appeal"].dropna()
    if not dynamic.between(0.0, 1.0).all():
        raise ValueError("dynamic_public_appeal falls outside [0, 1].")
    return output.reset_index(drop=True)


def dynamic_summary(dynamic: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for regime, frame in dynamic.groupby("aggregation_regime", sort=False):
        observed = frame["raw_public_appeal_proxy"].notna()
        rows.append(
            {
                "regime": regime,
                "rows": len(frame),
                "observed_proxy_rows": int(observed.sum()),
                "carried_forward_rows": int(
                    (frame["dynamic_public_appeal"].notna() & ~observed).sum()
                ),
                "contestant_seasons": frame["contestant_season_id"].nunique(),
                "mean_raw_proxy": frame["raw_public_appeal_proxy"].mean(),
                "mean_dynamic_proxy": frame["dynamic_public_appeal"].mean(),
                "mean_absolute_smoothing_change": (
                    frame["dynamic_public_appeal"]
                    - frame["raw_public_appeal_proxy"]
                ).abs().mean(),
                "mean_alpha_sensitivity_span": (
                    frame["smoothed_public_appeal_alpha_07"]
                    - frame["smoothed_public_appeal_alpha_03"]
                ).abs().mean(),
            }
        )
    return pd.DataFrame(rows)
