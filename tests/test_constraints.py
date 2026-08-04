"""Tests for percentage-regime constraints and LP behavior."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.constraints import (
    build_judge_save_constraints,
    build_percentage_constraints,
    build_ranking_constraints,
    check_feasibility,
    solve_preference_bounds,
)


def make_week(
    *,
    eliminated: tuple[str, ...] = ("e",),
    withdrawn: tuple[str, ...] = (),
    no_elimination: bool = False,
    finale: bool = False,
) -> pd.DataFrame:
    ids = ["e", "a", "b", "c"]
    placements = [4, 1, 2, 3]
    judge_totals = [10.0, 20.0, 30.0, 40.0]
    total = sum(judge_totals)
    return pd.DataFrame(
        {
            "season": 3,
            "week": 2,
            "contestant_id": ids,
            "contestant_name": ["Eliminated", "A", "B", "C"],
            "judge_total": judge_totals,
            "judge_pct": [value / total for value in judge_totals],
            "active_status": True,
            "eliminated_this_week": [item in eliminated for item in ids],
            "withdrew_this_week": [item in withdrawn for item in ids],
            "no_elimination_week": no_elimination,
            "double_elimination_week": len(eliminated) > 1,
            "finale_week": finale,
            "placement": placements,
            "aggregation_regime": "P",
        }
    )


def test_single_elimination_constraint_direction() -> None:
    constraints = build_percentage_constraints(make_week())
    e = constraints.variable_ids.index("e")
    a = constraints.variable_ids.index("a")
    matching = np.flatnonzero(
        np.isclose(constraints.A_ub[:, e], 1.0)
        & np.isclose(constraints.A_ub[:, a], -1.0)
    )
    assert len(matching) == 1
    row = int(matching[0])
    assert np.isclose(
        constraints.b_ub[row], constraints.judge_pct[a] - constraints.judge_pct[e]
    )


def test_simplex_and_coordinate_bounds() -> None:
    constraints = build_percentage_constraints(make_week())
    assert constraints.A_eq.shape == (1, 4)
    assert np.allclose(constraints.A_eq, 1.0)
    assert np.allclose(constraints.b_eq, 1.0)
    bounds = solve_preference_bounds(
        constraints.A_ub,
        constraints.b_ub,
        constraints.A_eq,
        constraints.b_eq,
        constraints.bounds,
    )
    assert bounds.feasible
    assert np.all(bounds.lower_bounds >= -1e-12)
    assert np.all(bounds.upper_bounds <= 1.0 + 1e-12)
    assert np.all(bounds.lower_bounds <= bounds.upper_bounds + 1e-12)


def test_no_elimination_week_has_no_outcome_inequalities() -> None:
    constraints = build_percentage_constraints(
        make_week(eliminated=(), no_elimination=True)
    )
    assert constraints.event_type == "no_elimination_simplex_only"
    assert constraints.n_inequalities == 0


def test_withdrawal_is_not_an_elimination_constraint() -> None:
    withdrawal_only = build_percentage_constraints(
        make_week(eliminated=(), withdrawn=("e",), no_elimination=False)
    )
    assert withdrawal_only.event_type == "withdrawal_simplex_only"
    assert withdrawal_only.n_inequalities == 0

    elimination_and_withdrawal = build_percentage_constraints(
        make_week(eliminated=("e",), withdrawn=("a",))
    )
    a = elimination_and_withdrawal.variable_ids.index("a")
    assert np.allclose(elimination_and_withdrawal.A_ub[:, a], 0.0)
    assert elimination_and_withdrawal.n_inequalities == 2


def test_multiple_elimination_constraints_are_conservative() -> None:
    constraints = build_percentage_constraints(
        make_week(eliminated=("e", "a"), withdrawn=())
    )
    assert constraints.event_type == "multiple_elimination_conservative"
    assert constraints.n_inequalities == 4
    e = constraints.variable_ids.index("e")
    a = constraints.variable_ids.index("a")
    assert not np.any(
        np.isclose(constraints.A_ub[:, e], 1.0)
        & np.isclose(constraints.A_ub[:, a], -1.0)
    )


def test_infeasible_lp_is_reported_without_exception() -> None:
    result = check_feasibility(
        A_ub=np.asarray([[1.0, 0.0], [-1.0, 0.0]]),
        b_ub=np.asarray([0.0, -1.0]),
        A_eq=np.asarray([[1.0, 1.0]]),
        b_eq=np.asarray([1.0]),
        bounds=((0.0, 1.0), (0.0, 1.0)),
    )
    assert not result.feasible
    bounds = solve_preference_bounds(
        A_ub=np.asarray([[1.0, 0.0], [-1.0, 0.0]]),
        b_ub=np.asarray([0.0, -1.0]),
        A_eq=np.asarray([[1.0, 1.0]]),
        b_eq=np.asarray([1.0]),
        bounds=((0.0, 1.0), (0.0, 1.0)),
    )
    assert not bounds.feasible
    assert np.isnan(bounds.lower_bounds).all()


def test_eliminated_contestant_without_active_score_is_skipped() -> None:
    week = make_week(eliminated=("e", "a"))
    week.loc[week["contestant_id"].eq("e"), "active_status"] = False
    week.loc[week["contestant_id"].eq("e"), ["judge_total", "judge_pct"]] = np.nan
    constraints = build_percentage_constraints(week)
    assert constraints.skipped
    assert constraints.event_type == "eliminated_contestant_without_active_score"
    assert "Eliminated" in constraints.skip_reason


def test_ranking_interfaces_are_implemented() -> None:
    week = make_week().assign(aggregation_regime="R")
    ranking = build_ranking_constraints(week)
    assert ranking["status"] == "implemented"
    assert ranking["implemented"]
    week = week.assign(aggregation_regime="R_plus")
    judge_save = build_judge_save_constraints(week)
    assert judge_save["status"] == "implemented"
    assert judge_save["implemented"]
