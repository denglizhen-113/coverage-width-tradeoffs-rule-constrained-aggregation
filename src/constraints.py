"""Rule-aware constraint construction for hidden public preferences.

Percentage-aggregation weeks are represented as bounded linear systems over
public preference shares. Ranking and judge-save regimes are represented by
validated ordinal week specifications that can be enumerated or sampled.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from .ranking_identification import (
    DEFAULT_TIE_POLICY,
    RankingIdentificationResult,
    build_week_spec,
    identify_week,
)


PANEL_REQUIRED_COLUMNS = {
    "season",
    "week",
    "contestant_id",
    "contestant_name",
    "judge_total",
    "judge_pct",
    "active_status",
    "eliminated_this_week",
    "withdrew_this_week",
    "no_elimination_week",
    "double_elimination_week",
    "finale_week",
    "placement",
    "aggregation_regime",
}


@dataclass(frozen=True)
class PercentageConstraintSet:
    """Linear representation of one percentage-aggregation season-week."""

    season: int
    week: int
    variable_ids: tuple[str, ...]
    variable_names: tuple[str, ...]
    judge_pct: np.ndarray
    A_ub: np.ndarray
    b_ub: np.ndarray
    A_eq: np.ndarray
    b_eq: np.ndarray
    bounds: tuple[tuple[float, float], ...]
    event_type: str
    eliminated_ids: tuple[str, ...]
    withdrawn_ids: tuple[str, ...]
    constraint_note: str
    skipped: bool = False
    skip_reason: str = ""

    @property
    def n_variables(self) -> int:
        return len(self.variable_ids)

    @property
    def n_inequalities(self) -> int:
        return int(self.A_ub.shape[0])

    @property
    def n_equalities(self) -> int:
        return int(self.A_eq.shape[0])


@dataclass(frozen=True)
class FeasibilityResult:
    feasible: bool
    status: int
    message: str
    solution: np.ndarray | None


@dataclass(frozen=True)
class PreferenceBoundsResult:
    feasible: bool
    lower_bounds: np.ndarray
    upper_bounds: np.ndarray
    min_statuses: tuple[int, ...]
    max_statuses: tuple[int, ...]
    message: str

    @property
    def widths(self) -> np.ndarray:
        return self.upper_bounds - self.lower_bounds


def _as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype(bool)
    return series.astype(str).str.strip().str.casefold().isin({"true", "1", "yes"})


def _empty_constraint_set(
    *,
    season: int,
    week: int,
    variable_ids: Sequence[str],
    variable_names: Sequence[str],
    event_type: str,
    reason: str,
) -> PercentageConstraintSet:
    n_variables = len(variable_ids)
    return PercentageConstraintSet(
        season=season,
        week=week,
        variable_ids=tuple(variable_ids),
        variable_names=tuple(variable_names),
        judge_pct=np.full(n_variables, np.nan),
        A_ub=np.empty((0, n_variables), dtype=float),
        b_ub=np.empty(0, dtype=float),
        A_eq=np.ones((1, n_variables), dtype=float) if n_variables else np.empty((0, 0)),
        b_eq=np.ones(1, dtype=float) if n_variables else np.empty(0),
        bounds=tuple((0.0, 1.0) for _ in range(n_variables)),
        event_type=event_type,
        eliminated_ids=(),
        withdrawn_ids=(),
        constraint_note=reason,
        skipped=True,
        skip_reason=reason,
    )


def build_percentage_constraints(week_df: pd.DataFrame) -> PercentageConstraintSet:
    """Build ``A_ub F <= b_ub`` and simplex constraints for one P week.

    Withdrawals are excluded from the survivor comparison set. A no-elimination
    or withdrawal-only week therefore contributes only the simplex. For a
    multiple elimination, every eliminated contestant is constrained against
    every non-withdrawn survivor, without ordering eliminated contestants.
    """
    missing = sorted(PANEL_REQUIRED_COLUMNS.difference(week_df.columns))
    if missing:
        raise ValueError(f"week_df is missing required columns: {missing}")
    if week_df.empty:
        raise ValueError("week_df must contain one season-week.")
    keys = week_df[["season", "week"]].drop_duplicates()
    if len(keys) != 1:
        raise ValueError("week_df must contain exactly one season-week.")
    season = int(keys.iloc[0]["season"])
    week = int(keys.iloc[0]["week"])
    regimes = set(week_df["aggregation_regime"].dropna().astype(str))
    if regimes != {"P"}:
        raise ValueError(f"Percentage constraints require regime P, found {regimes}.")

    active_mask_all = _as_bool(week_df["active_status"])
    eliminated_mask_all = _as_bool(week_df["eliminated_this_week"])
    active = week_df.loc[active_mask_all].copy()
    active = active.sort_values("contestant_id", kind="stable").reset_index(drop=True)
    variable_ids = active["contestant_id"].astype(str).tolist()
    variable_names = active["contestant_name"].astype(str).tolist()
    if (eliminated_mask_all & ~active_mask_all).any():
        missing_names = week_df.loc[
            eliminated_mask_all & ~active_mask_all, "contestant_name"
        ].astype(str)
        return _empty_constraint_set(
            season=season,
            week=week,
            variable_ids=variable_ids,
            variable_names=variable_names,
            event_type="eliminated_contestant_without_active_score",
            reason=(
                "eliminated_contestant_missing_active_judge_total: "
                + "; ".join(missing_names)
            ),
        )
    if len(active) < 2:
        return _empty_constraint_set(
            season=season,
            week=week,
            variable_ids=variable_ids,
            variable_names=variable_names,
            event_type="insufficient_active_contestants",
            reason="fewer_than_two_active_contestants",
        )

    judge_total = pd.to_numeric(active["judge_total"], errors="coerce")
    if judge_total.isna().any():
        return _empty_constraint_set(
            season=season,
            week=week,
            variable_ids=variable_ids,
            variable_names=variable_names,
            event_type="missing_judge_total",
            reason="active_judge_total_missing",
        )
    sum_judge = float(judge_total.sum())
    if not np.isfinite(sum_judge) or sum_judge <= 0:
        return _empty_constraint_set(
            season=season,
            week=week,
            variable_ids=variable_ids,
            variable_names=variable_names,
            event_type="nonpositive_judge_total",
            reason="sum_judge_total_nonpositive",
        )

    judge_pct = judge_total.to_numpy(dtype=float) / sum_judge
    supplied_pct = pd.to_numeric(active["judge_pct"], errors="coerce").to_numpy(dtype=float)
    if np.isnan(supplied_pct).any() or not np.allclose(
        supplied_pct, judge_pct, rtol=0, atol=1e-9
    ):
        raise ValueError(
            f"season {season}, week {week}: judge_pct does not reconcile to judge_total."
        )

    eliminated_mask = _as_bool(active["eliminated_this_week"]).to_numpy()
    withdrawn_mask = _as_bool(active["withdrew_this_week"]).to_numpy()
    no_elimination = bool(_as_bool(active["no_elimination_week"]).iloc[0])
    finale = bool(_as_bool(active["finale_week"]).iloc[0])
    eliminated_indices = np.flatnonzero(eliminated_mask).tolist()
    withdrawn_indices = np.flatnonzero(withdrawn_mask).tolist()
    eliminated_ids = tuple(variable_ids[index] for index in eliminated_indices)
    withdrawn_ids = tuple(variable_ids[index] for index in withdrawn_indices)

    inequality_rows: list[np.ndarray] = []
    inequality_rhs: list[float] = []
    constraint_note = ""

    if finale:
        placement = pd.to_numeric(active["placement"], errors="coerce")
        if placement.isna().any() or placement.nunique() != len(active):
            event_type = "finale_simplex_only"
            constraint_note = (
                "Final placement was missing or non-unique among active finalists; "
                "ranking inequalities were not fabricated."
            )
        else:
            event_type = "finale_complete_ranking"
            placements = placement.to_numpy(dtype=float)
            for worse in range(len(active)):
                for better in range(len(active)):
                    if placements[worse] <= placements[better]:
                        continue
                    row = np.zeros(len(active), dtype=float)
                    row[worse] = 1.0
                    row[better] = -1.0
                    inequality_rows.append(row)
                    inequality_rhs.append(judge_pct[better] - judge_pct[worse])
            constraint_note = (
                "All pairwise combined-score order inequalities were added from "
                "the complete active-finalist placement order."
            )
    elif no_elimination:
        event_type = "no_elimination_simplex_only"
        constraint_note = "No elimination inequality is justified for this week."
    elif not eliminated_indices:
        if withdrawn_indices:
            event_type = "withdrawal_simplex_only"
            constraint_note = (
                "Withdrawal is non-comparative and does not identify the lowest "
                "combined score."
            )
        else:
            event_type = "no_observed_elimination_simplex_only"
            constraint_note = "No eliminated contestant was observed."
    else:
        survivors = [
            index
            for index in range(len(active))
            if index not in eliminated_indices and index not in withdrawn_indices
        ]
        if not survivors:
            event_type = "elimination_without_comparator_simplex_only"
            constraint_note = (
                "No non-withdrawn survivor was available for an outcome inequality."
            )
        else:
            event_type = (
                "multiple_elimination_conservative"
                if len(eliminated_indices) > 1
                else "single_elimination"
            )
            for eliminated in eliminated_indices:
                for survivor in survivors:
                    row = np.zeros(len(active), dtype=float)
                    row[eliminated] = 1.0
                    row[survivor] = -1.0
                    inequality_rows.append(row)
                    inequality_rhs.append(
                        judge_pct[survivor] - judge_pct[eliminated]
                    )
            constraint_note = (
                "Each eliminated contestant is weakly below every non-withdrawn "
                "survivor in combined score; eliminated contestants are not ordered."
            )

    A_ub = (
        np.vstack(inequality_rows).astype(float)
        if inequality_rows
        else np.empty((0, len(active)), dtype=float)
    )
    b_ub = np.asarray(inequality_rhs, dtype=float)
    return PercentageConstraintSet(
        season=season,
        week=week,
        variable_ids=tuple(variable_ids),
        variable_names=tuple(variable_names),
        judge_pct=judge_pct,
        A_ub=A_ub,
        b_ub=b_ub,
        A_eq=np.ones((1, len(active)), dtype=float),
        b_eq=np.ones(1, dtype=float),
        bounds=tuple((0.0, 1.0) for _ in range(len(active))),
        event_type=event_type,
        eliminated_ids=eliminated_ids,
        withdrawn_ids=withdrawn_ids,
        constraint_note=constraint_note,
    )


def _linprog_arrays(
    A_ub: np.ndarray,
    b_ub: np.ndarray,
    A_eq: np.ndarray,
    b_eq: np.ndarray,
) -> tuple[np.ndarray | None, np.ndarray | None, np.ndarray | None, np.ndarray | None]:
    aub = np.asarray(A_ub, dtype=float)
    bub = np.asarray(b_ub, dtype=float)
    aeq = np.asarray(A_eq, dtype=float)
    beq = np.asarray(b_eq, dtype=float)
    return (
        aub if aub.size else None,
        bub if bub.size else None,
        aeq if aeq.size else None,
        beq if beq.size else None,
    )


def check_feasibility(
    A_ub: np.ndarray,
    b_ub: np.ndarray,
    A_eq: np.ndarray,
    b_eq: np.ndarray,
    bounds: Sequence[tuple[float, float]],
) -> FeasibilityResult:
    """Check whether a bounded linear preference system has any solution."""
    n_variables = len(bounds)
    if n_variables == 0:
        return FeasibilityResult(False, 2, "No variables supplied.", None)
    aub, bub, aeq, beq = _linprog_arrays(A_ub, b_ub, A_eq, b_eq)
    result = linprog(
        c=np.zeros(n_variables, dtype=float),
        A_ub=aub,
        b_ub=bub,
        A_eq=aeq,
        b_eq=beq,
        bounds=list(bounds),
        method="highs",
    )
    return FeasibilityResult(
        feasible=bool(result.success),
        status=int(result.status),
        message=str(result.message),
        solution=np.asarray(result.x, dtype=float) if result.success else None,
    )


def solve_preference_bounds(
    A_ub: np.ndarray,
    b_ub: np.ndarray,
    A_eq: np.ndarray,
    b_eq: np.ndarray,
    bounds: Sequence[tuple[float, float]],
) -> PreferenceBoundsResult:
    """Compute sharp coordinate-wise LP bounds for every preference share."""
    feasibility = check_feasibility(A_ub, b_ub, A_eq, b_eq, bounds)
    n_variables = len(bounds)
    if not feasibility.feasible:
        nan_values = np.full(n_variables, np.nan)
        return PreferenceBoundsResult(
            feasible=False,
            lower_bounds=nan_values.copy(),
            upper_bounds=nan_values.copy(),
            min_statuses=tuple(feasibility.status for _ in range(n_variables)),
            max_statuses=tuple(feasibility.status for _ in range(n_variables)),
            message=feasibility.message,
        )

    aub, bub, aeq, beq = _linprog_arrays(A_ub, b_ub, A_eq, b_eq)
    lower = np.empty(n_variables, dtype=float)
    upper = np.empty(n_variables, dtype=float)
    min_statuses: list[int] = []
    max_statuses: list[int] = []
    for variable in range(n_variables):
        objective = np.zeros(n_variables, dtype=float)
        objective[variable] = 1.0
        minimum = linprog(
            objective,
            A_ub=aub,
            b_ub=bub,
            A_eq=aeq,
            b_eq=beq,
            bounds=list(bounds),
            method="highs",
        )
        maximum = linprog(
            -objective,
            A_ub=aub,
            b_ub=bub,
            A_eq=aeq,
            b_eq=beq,
            bounds=list(bounds),
            method="highs",
        )
        min_statuses.append(int(minimum.status))
        max_statuses.append(int(maximum.status))
        if not minimum.success or not maximum.success:
            return PreferenceBoundsResult(
                feasible=False,
                lower_bounds=np.full(n_variables, np.nan),
                upper_bounds=np.full(n_variables, np.nan),
                min_statuses=tuple(min_statuses),
                max_statuses=tuple(max_statuses),
                message=(
                    f"Bound LP failed for variable {variable}: "
                    f"min={minimum.message}; max={maximum.message}"
                ),
            )
        lower[variable] = float(np.clip(minimum.fun, 0.0, 1.0))
        upper[variable] = float(np.clip(-maximum.fun, 0.0, 1.0))
    return PreferenceBoundsResult(
        feasible=True,
        lower_bounds=lower,
        upper_bounds=upper,
        min_statuses=tuple(min_statuses),
        max_statuses=tuple(max_statuses),
        message="All coordinate-wise LPs solved successfully.",
    )


def save_constraint_set(constraints: PercentageConstraintSet, path: Path) -> None:
    """Save numeric matrices and explicit variable metadata without pickle."""
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        season=np.asarray([constraints.season], dtype=int),
        week=np.asarray([constraints.week], dtype=int),
        variable_ids=np.asarray(constraints.variable_ids, dtype="U"),
        variable_names=np.asarray(constraints.variable_names, dtype="U"),
        judge_pct=np.asarray(constraints.judge_pct, dtype=float),
        A_ub=np.asarray(constraints.A_ub, dtype=float),
        b_ub=np.asarray(constraints.b_ub, dtype=float),
        A_eq=np.asarray(constraints.A_eq, dtype=float),
        b_eq=np.asarray(constraints.b_eq, dtype=float),
        lower_bounds=np.asarray([bound[0] for bound in constraints.bounds], dtype=float),
        upper_bounds=np.asarray([bound[1] for bound in constraints.bounds], dtype=float),
        event_type=np.asarray([constraints.event_type], dtype="U"),
        eliminated_ids=np.asarray(constraints.eliminated_ids, dtype="U"),
        withdrawn_ids=np.asarray(constraints.withdrawn_ids, dtype="U"),
        constraint_note=np.asarray([constraints.constraint_note], dtype="U"),
    )


def load_constraint_set(path: Path) -> PercentageConstraintSet:
    """Load a saved percentage constraint set with pickle disabled."""
    with np.load(path, allow_pickle=False) as data:
        lower = data["lower_bounds"].astype(float)
        upper = data["upper_bounds"].astype(float)
        return PercentageConstraintSet(
            season=int(data["season"][0]),
            week=int(data["week"][0]),
            variable_ids=tuple(data["variable_ids"].astype(str).tolist()),
            variable_names=tuple(data["variable_names"].astype(str).tolist()),
            judge_pct=data["judge_pct"].astype(float),
            A_ub=data["A_ub"].astype(float),
            b_ub=data["b_ub"].astype(float),
            A_eq=data["A_eq"].astype(float),
            b_eq=data["b_eq"].astype(float),
            bounds=tuple(zip(lower.tolist(), upper.tolist())),
            event_type=str(data["event_type"][0]),
            eliminated_ids=tuple(data["eliminated_ids"].astype(str).tolist()),
            withdrawn_ids=tuple(data["withdrawn_ids"].astype(str).tolist()),
            constraint_note=str(data["constraint_note"][0]),
        )


def build_ranking_constraints(
    week_df: pd.DataFrame, tie_policy: str = DEFAULT_TIE_POLICY
) -> dict[str, Any]:
    """Build the implemented direct-elimination ordinal specification."""
    spec = build_week_spec(week_df, tie_policy)
    if spec.regime != "R":
        raise ValueError(f"Ranking constraints require regime R, found {spec.regime}.")
    return {
        "regime": "R",
        "status": "implemented",
        "implemented": True,
        "n_active": spec.n_active,
        "tie_policy": spec.tie_policy,
        "constraint": "eliminated set belongs to the tie-inclusive worst-k set",
        "week_spec": spec,
    }


def sample_feasible_rankings(
    week_df: pd.DataFrame,
    *,
    tie_policy: str = DEFAULT_TIE_POLICY,
    exact_threshold: int = 9,
    n_samples: int = 10_000,
    base_seed: int = 20260714,
    detail_limit: int | None = 1_000,
) -> RankingIdentificationResult:
    """Enumerate or fixed-seed sample feasible rankings for one ordinal week."""
    spec = build_week_spec(week_df, tie_policy)
    return identify_week(
        spec,
        exact_threshold=exact_threshold,
        n_samples=n_samples,
        base_seed=base_seed,
        detail_limit=detail_limit,
    )


def build_judge_save_constraints(
    week_df: pd.DataFrame, tie_policy: str = DEFAULT_TIE_POLICY
) -> dict[str, Any]:
    """Build the implemented weak bottom-set judge-save specification."""
    spec = build_week_spec(week_df, tie_policy)
    if spec.regime != "R_plus":
        raise ValueError(
            f"Judge-save constraints require regime R_plus, found {spec.regime}."
        )
    return {
        "regime": "R_plus",
        "status": "implemented",
        "implemented": True,
        "n_active": spec.n_active,
        "tie_policy": spec.tie_policy,
        "constraint": (
            "eliminated set belongs to the tie-inclusive bottom-(k+1) set"
        ),
        "week_spec": spec,
    }
