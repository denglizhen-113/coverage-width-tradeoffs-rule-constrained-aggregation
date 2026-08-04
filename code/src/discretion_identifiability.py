"""Discretion-identifiability frontier utilities.

Observed R_plus data identify one weak judge-save condition.  The multi-level
frontier below is a deterministic synthetic rule-scenario analysis, not an
estimate of unobserved historical intervention strength.
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd


def _fan_ranks_from_orders(orders: np.ndarray) -> np.ndarray:
    ranks = np.empty_like(orders, dtype=float)
    positions = np.arange(1, orders.shape[1] + 1, dtype=float)
    rows = np.arange(len(orders))[:, None]
    ranks[rows, orders] = positions
    return ranks


def _bottom_feasible(combined: np.ndarray, eliminated_index: int, bottom_size: int) -> np.ndarray:
    size = min(max(int(bottom_size), 1), combined.shape[1])
    threshold_index = combined.shape[1] - size
    threshold = np.partition(combined, threshold_index, axis=1)[:, threshold_index]
    return combined[:, eliminated_index] >= threshold - 1e-12


def synthetic_discretion_frontier(
    *, n_active: int = 6,
    judge_ranks: np.ndarray | None = None,
    eliminated_index: int = 0,
) -> pd.DataFrame:
    """Enumerate a small synthetic ranking case over nested intervention rules."""
    if n_active < 3 or n_active > 8:
        raise ValueError("synthetic frontier supports 3-8 active contestants.")
    if judge_ranks is None:
        judge_ranks = np.arange(1, n_active + 1, dtype=float)
    judge = np.asarray(judge_ranks, dtype=float)
    if judge.shape != (n_active,):
        raise ValueError("judge_ranks must have one rank per active contestant.")
    orders = np.asarray(list(itertools.permutations(range(n_active))), dtype=int)
    fan = _fan_ranks_from_orders(orders)
    combined = fan + judge[None, :]
    rows = []
    direct_count = None
    for strength in range(3):
        feasible = _bottom_feasible(combined, eliminated_index, 1 + strength)
        accepted = fan[feasible]
        supports = []
        for contestant in range(n_active):
            values = accepted[:, contestant]
            supports.append(float(values.max() - values.min()) if values.size else np.nan)
        width = float(np.nanmean(supports) / (n_active - 1))
        count = int(feasible.sum())
        if direct_count is None:
            direct_count = count
        rows.append(
            {
                "evidence_type": "synthetic rule scenario",
                "n_active": n_active,
                "expert_discretion_strength": strength,
                "bottom_set_size": 1 + strength,
                "institutional_flexibility_index": strength / 2.0,
                "n_feasible_rankings": count,
                "feasible_fraction": count / len(fan),
                "normalized_rank_width": width,
                "identifiability_loss_ratio_vs_direct": count / max(int(direct_count), 1),
                "interpretation": "Nested relaxation scenario; not a historical estimate of intervention strength.",
            }
        )
    return pd.DataFrame(rows)


def observed_rplus_summary(rplus: pd.DataFrame) -> pd.DataFrame:
    """Summarize observed direct-versus-weak quantities without inventing a continuum."""
    data = rplus.copy()
    if "is_default_policy" in data.columns:
        data = data.loc[data["is_default_policy"].astype(bool)]
    data = data.loc[data["regime"].eq("R_plus")].copy()
    if data.empty:
        return pd.DataFrame()
    rows = []
    for strength, count_column, fraction_column, label in [
        (0, "n_feasible_direct_R_like", "feasible_fraction_direct_R_like", "direct outcome implication"),
        (1, "n_feasible_permutations", "feasible_fraction", "observed weak judge-save implication"),
    ]:
        rows.append(
            {
                "evidence_type": "empirical observed R_plus summary",
                "n_weeks": int(len(data)),
                "expert_discretion_strength": strength,
                "mechanism_label": label,
                "mean_feasible_rankings_or_estimate": float(pd.to_numeric(data[count_column], errors="coerce").mean()),
                "mean_feasible_fraction": float(pd.to_numeric(data[fraction_column], errors="coerce").mean()),
                "mean_identifiability_loss_ratio": (
                    1.0 if strength == 0 else float(pd.to_numeric(data["identifiability_loss_ratio"], errors="coerce").mean())
                ),
                "interpretation": "Observed binary direct-versus-weak comparison; no continuum is inferred from the empirical record.",
            }
        )
    return pd.DataFrame(rows)
