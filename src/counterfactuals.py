"""Set-aware aggregation mechanism counterfactuals."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


LAMBDA_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
GAMMA_GRID = (0.0, 0.25, 0.5, 1.0)


@dataclass(frozen=True)
class PublicScenario:
    scenario_id: str
    scenario_type: str
    public_score: np.ndarray
    fan_rank: np.ndarray | None
    source: str


def strict_descending_ranks(values: Sequence[float], ids: Sequence[str]) -> np.ndarray:
    """Return strict rank 1=best with contestant id as deterministic tie-break."""
    values_array = np.asarray(values, dtype=float)
    ids_array = np.asarray(ids, dtype=str)
    if len(values_array) != len(ids_array) or not np.isfinite(values_array).all():
        raise ValueError("values and ids must be finite and have equal length.")
    order = np.lexsort((ids_array, -values_array))
    ranks = np.empty(len(order), dtype=int)
    ranks[order] = np.arange(1, len(order) + 1)
    return ranks


def uncertainty_aware_scores(
    expert: Sequence[float],
    public: Sequence[float],
    uncertainty: Sequence[float],
    lambda_value: float,
    gamma: float,
) -> np.ndarray:
    if not 0 <= lambda_value <= 1 or gamma < 0:
        raise ValueError("lambda must be in [0, 1] and gamma must be nonnegative.")
    expert_array = np.asarray(expert, dtype=float)
    public_array = np.asarray(public, dtype=float)
    uncertainty_array = np.asarray(uncertainty, dtype=float)
    if not (expert_array.shape == public_array.shape == uncertainty_array.shape):
        raise ValueError("expert, public, and uncertainty arrays must align.")
    return (
        lambda_value * expert_array
        + (1.0 - lambda_value) * public_array
        - gamma * uncertainty_array
    )


def eliminated_set_consistent(
    scores: Sequence[float], eliminated_indices: Sequence[int], bottom_size: int
) -> bool:
    """Check tie-inclusive bottom membership when higher scores are better."""
    if not eliminated_indices:
        return True
    values = np.asarray(scores, dtype=float)
    size = min(max(int(bottom_size), 1), len(values))
    threshold = np.partition(values, size - 1)[size - 1]
    return bool(np.all(values[list(eliminated_indices)] <= threshold + 1e-12))


def parameter_grid() -> list[tuple[float, float]]:
    return [(lambda_value, gamma) for lambda_value in LAMBDA_GRID for gamma in GAMMA_GRID]


def _ordinal_scenarios(
    week: pd.DataFrame,
    detail: pd.DataFrame,
    seed: int,
    max_sampled: int,
) -> list[PublicScenario]:
    ids = week["contestant_id"].astype(str).tolist()
    usable = detail.loc[
        detail["contestant_id"].astype(str).isin(ids)
        & detail["is_feasible"].astype(str).str.casefold().isin({"true", "1"})
    ]
    if usable.empty:
        return []
    pivot = usable.pivot_table(
        index="permutation_id", columns="contestant_id", values="fan_rank", aggfunc="first"
    )
    if not set(ids).issubset(pivot.columns):
        return []
    pivot = pivot[ids].dropna().sort_index()
    if pivot.empty:
        return []
    ranks = pivot.to_numpy(dtype=float)
    n_active = len(ids)
    scores = 1.0 - (ranks - 1.0) / max(n_active - 1.0, 1.0)
    mean_ranks = pd.to_numeric(week["mean_fan_rank"], errors="coerce").to_numpy(dtype=float)
    medoid_index = int(np.argmin(np.sum((ranks - mean_ranks[None, :]) ** 2, axis=1)))
    dynamic = pd.to_numeric(week["dynamic_public_appeal"], errors="coerce").fillna(0.5).to_numpy(dtype=float)
    centered = dynamic - dynamic.mean()
    alignment = scores @ centered
    optimistic_index = int(np.argmax(alignment))
    pessimistic_index = int(np.argmin(alignment))
    chosen = {
        "mean_feasible": medoid_index,
        "optimistic_feasible": optimistic_index,
        "pessimistic_feasible": pessimistic_index,
    }
    scenarios = [
        PublicScenario(name, name, scores[index].copy(), ranks[index].copy(), "retained_feasible_ranking")
        for name, index in chosen.items()
    ]
    remaining = np.asarray([index for index in range(len(pivot)) if index not in set(chosen.values())], dtype=int)
    rng = np.random.default_rng(
        np.random.SeedSequence([seed, int(week.iloc[0]["season"]), int(week.iloc[0]["week"])])
    )
    if len(remaining):
        selected = rng.choice(remaining, size=min(max_sampled, len(remaining)), replace=False)
        for number, index in enumerate(selected):
            scenarios.append(
                PublicScenario(
                    f"sample_{number:03d}",
                    "sampled_feasible",
                    scores[int(index)].copy(),
                    ranks[int(index)].copy(),
                    "fixed_seed_retained_feasible_ranking",
                )
            )
    return scenarios


def public_scenarios_for_week(
    week: pd.DataFrame,
    ranking_detail: pd.DataFrame,
    seed: int,
    max_sampled: int = 20,
) -> list[PublicScenario]:
    regime = str(week.iloc[0]["aggregation_regime"])
    if regime == "P":
        columns = {
            "pessimistic": "public_support_lower",
            "midpoint": "public_support_midpoint",
            "optimistic": "public_support_upper",
        }
        scenarios = []
        for name, column in columns.items():
            values = pd.to_numeric(week[column], errors="coerce").to_numpy(dtype=float)
            if np.isfinite(values).all():
                scenarios.append(PublicScenario(name, name, values, None, "p_coordinate_bounds"))
        return scenarios
    return _ordinal_scenarios(week, ranking_detail, seed, max_sampled)


def _safe_spearman(rank_values: np.ndarray, score_values: np.ndarray) -> float:
    if len(rank_values) < 3 or np.std(rank_values) == 0 or np.std(score_values) == 0:
        return np.nan
    return float(spearmanr(-rank_values, score_values).statistic)


def _scenario_metrics(
    season: int,
    regime: str,
    mechanism: str,
    lambda_value: float | None,
    gamma: float | None,
    scenario_id: str,
    scores_by_contestant: dict[str, list[float]],
    changes: list[bool],
    season_data: pd.DataFrame,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    contestant = (
        season_data.groupby(["contestant_id", "contestant_name"], as_index=False)
        .agg(
            observed_placement=("placement", "first"),
            mean_judge_pct=("judge_pct", "mean"),
            mean_dynamic_public_appeal=("dynamic_public_appeal", "mean"),
        )
    )
    contestant["mechanism_score"] = contestant["contestant_id"].astype(str).map(
        lambda key: float(np.mean(scores_by_contestant.get(key, [np.nan])))
    )
    contestant = contestant.loc[contestant["mechanism_score"].notna()].copy()
    contestant["counterfactual_rank"] = strict_descending_ranks(
        contestant["mechanism_score"], contestant["contestant_id"].astype(str)
    )
    observed_winner = set(
        contestant.loc[contestant["observed_placement"].eq(1), "contestant_id"].astype(str)
    )
    counterfactual_winner = set(
        contestant.loc[contestant["counterfactual_rank"].eq(1), "contestant_id"].astype(str)
    )
    finalist_count = min(3, len(contestant))
    observed_finalists = set(
        contestant.nsmallest(finalist_count, "observed_placement")["contestant_id"].astype(str)
    )
    counterfactual_finalists = set(
        contestant.nsmallest(finalist_count, "counterfactual_rank")["contestant_id"].astype(str)
    )
    rank_shift = np.abs(
        contestant["counterfactual_rank"].to_numpy(dtype=float)
        - contestant["observed_placement"].to_numpy(dtype=float)
    )
    row = {
        "season": season,
        "regime": regime,
        "mechanism": mechanism,
        "lambda": lambda_value,
        "gamma": gamma,
        "scenario_id": scenario_id,
        "applicable": True,
        "n_contestants": len(contestant),
        "n_outcome_events": len(changes),
        "outcome_change_rate": float(np.mean(changes)) if changes else np.nan,
        "winner_changed": observed_winner != counterfactual_winner,
        "finalist_set_changed": observed_finalists != counterfactual_finalists,
        "average_rank_shift": float(np.mean(rank_shift)),
        "expert_alignment": _safe_spearman(
            contestant["counterfactual_rank"].to_numpy(dtype=float),
            contestant["mean_judge_pct"].to_numpy(dtype=float),
        ),
        "public_responsiveness": _safe_spearman(
            contestant["counterfactual_rank"].to_numpy(dtype=float),
            contestant["mean_dynamic_public_appeal"].to_numpy(dtype=float),
        ),
        "notes": "Season ranking uses mean mechanism score over observed active weeks.",
    }
    contestant_rows = []
    for item in contestant.itertuples(index=False):
        contestant_rows.append(
            {
                "season": season,
                "regime": regime,
                "mechanism": mechanism,
                "lambda": lambda_value,
                "gamma": gamma,
                "scenario_id": scenario_id,
                "contestant_id": item.contestant_id,
                "contestant_name": item.contestant_name,
                "observed_placement": item.observed_placement,
                "counterfactual_rank": item.counterfactual_rank,
                "rank_shift": item.counterfactual_rank - item.observed_placement,
            }
        )
    return row, contestant_rows


def simulate_counterfactuals(
    dynamic: pd.DataFrame,
    week_level: pd.DataFrame,
    ranking_detail: pd.DataFrame,
    seed: int = 20260714,
    max_sampled_rankings: int = 20,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {
        "season", "week", "contestant_id", "contestant_name", "aggregation_regime",
        "judge_pct", "judge_rank", "placement", "eliminated_this_week", "n_active",
        "public_support_lower", "public_support_midpoint", "public_support_upper",
        "mean_fan_rank", "public_appeal_uncertainty", "dynamic_public_appeal",
    }
    missing = sorted(required.difference(dynamic.columns))
    if missing:
        raise ValueError(f"dynamic data are missing required columns: {missing}")
    week_flags = week_level.set_index(["season", "week"])
    scenario_rows: list[dict[str, Any]] = []
    contestant_rows: list[dict[str, Any]] = []
    for season, season_data in dynamic.groupby("season", sort=True):
        season = int(season)
        regime = str(season_data.iloc[0]["aggregation_regime"])
        observed_event_count = 0
        accumulators: dict[tuple[str, float | None, float | None, str], dict[str, Any]] = defaultdict(
            lambda: {"scores": defaultdict(list), "changes": []}
        )
        for week, week_data in season_data.groupby("week", sort=True):
            week = int(week)
            ordered = week_data.sort_values("contestant_id").reset_index(drop=True)
            detail = ranking_detail.loc[
                ranking_detail["season"].eq(season) & ranking_detail["week"].eq(week)
            ]
            scenarios = public_scenarios_for_week(
                ordered, detail, seed=seed, max_sampled=max_sampled_rankings
            )
            if not scenarios:
                continue
            flags = week_flags.loc[(season, week)]
            eliminated_indices = tuple(
                np.flatnonzero(
                    ordered["eliminated_this_week"].astype(str).str.casefold().isin({"true", "1"})
                ).tolist()
            )
            evaluate_outcome = bool(
                len(eliminated_indices)
                and not bool(flags["finale_week"])
                and not bool(flags["no_elimination_week"])
            )
            if evaluate_outcome:
                observed_event_count += 1
            ids = ordered["contestant_id"].astype(str).tolist()
            judge_pct = pd.to_numeric(ordered["judge_pct"], errors="coerce").to_numpy(dtype=float)
            judge_rank = pd.to_numeric(ordered["judge_rank"], errors="coerce").to_numpy(dtype=float)
            uncertainty = pd.to_numeric(
                ordered["public_appeal_uncertainty"], errors="coerce"
            ).fillna(1.0).to_numpy(dtype=float)
            k = len(eliminated_indices)
            for scenario in scenarios:
                fan_rank = scenario.fan_rank
                if fan_rank is None:
                    fan_rank = strict_descending_ranks(scenario.public_score, ids).astype(float)
                direct_score = -(judge_rank + fan_rank)
                key = ("direct_ranking", None, None, scenario.scenario_id)
                for contestant_id, score in zip(ids, direct_score):
                    accumulators[key]["scores"][contestant_id].append(float(score))
                if evaluate_outcome:
                    accumulators[key]["changes"].append(
                        not eliminated_set_consistent(direct_score, eliminated_indices, k)
                    )

                weak_key = ("ranking_plus_judge_save_weak", None, None, scenario.scenario_id)
                if evaluate_outcome:
                    accumulators[weak_key]["changes"].append(
                        not eliminated_set_consistent(direct_score, eliminated_indices, k + 1)
                    )

                if regime == "P":
                    percentage_score = judge_pct + scenario.public_score
                    percentage_key = ("percentage_aggregation", None, None, scenario.scenario_id)
                    for contestant_id, score in zip(ids, percentage_score):
                        accumulators[percentage_key]["scores"][contestant_id].append(float(score))
                    if evaluate_outcome:
                        accumulators[percentage_key]["changes"].append(
                            not eliminated_set_consistent(percentage_score, eliminated_indices, k)
                        )

                for lambda_value, gamma in parameter_grid():
                    ua_score = uncertainty_aware_scores(
                        judge_pct, scenario.public_score, uncertainty, lambda_value, gamma
                    )
                    ua_key = (
                        "uncertainty_aware",
                        float(lambda_value),
                        float(gamma),
                        scenario.scenario_id,
                    )
                    for contestant_id, score in zip(ids, ua_score):
                        accumulators[ua_key]["scores"][contestant_id].append(float(score))
                    if evaluate_outcome:
                        accumulators[ua_key]["changes"].append(
                            not eliminated_set_consistent(ua_score, eliminated_indices, k)
                        )

        observed = (
            season_data.groupby(["contestant_id", "contestant_name"], as_index=False)
            .agg(
                observed_placement=("placement", "first"),
                mean_judge_pct=("judge_pct", "mean"),
                mean_dynamic_public_appeal=("dynamic_public_appeal", "mean"),
            )
        )
        observed_ranks = observed["observed_placement"].to_numpy(dtype=float)
        original = {
            "season": season,
            "regime": regime,
            "mechanism": "original_observed",
            "lambda": np.nan,
            "gamma": np.nan,
            "scenario_id": "observed",
            "applicable": True,
            "n_contestants": len(observed),
            "n_outcome_events": observed_event_count,
            "outcome_change_rate": 0.0,
            "winner_changed": False,
            "finalist_set_changed": False,
            "average_rank_shift": 0.0,
            "expert_alignment": _safe_spearman(
                observed_ranks, observed["mean_judge_pct"].to_numpy(dtype=float)
            ),
            "public_responsiveness": _safe_spearman(
                observed_ranks,
                observed["mean_dynamic_public_appeal"].to_numpy(dtype=float),
            ),
            "notes": "Observed placement is retained exactly, including tied placements.",
        }
        original_contestants = [
            {
                "season": season,
                "regime": regime,
                "mechanism": "original_observed",
                "lambda": np.nan,
                "gamma": np.nan,
                "scenario_id": "observed",
                "contestant_id": row.contestant_id,
                "contestant_name": row.contestant_name,
                "observed_placement": row.observed_placement,
                "counterfactual_rank": row.observed_placement,
                "rank_shift": 0.0,
            }
            for row in observed.itertuples(index=False)
        ]
        scenario_rows.append(original)
        contestant_rows.extend(original_contestants)
        for (mechanism, lambda_value, gamma, scenario_id), accumulator in accumulators.items():
            if mechanism == "ranking_plus_judge_save_weak":
                scenario_rows.append(
                    {
                        "season": season,
                        "regime": regime,
                        "mechanism": mechanism,
                        "lambda": lambda_value,
                        "gamma": gamma,
                        "scenario_id": scenario_id,
                        "applicable": True,
                        "n_contestants": season_data["contestant_id"].nunique(),
                        "n_outcome_events": len(accumulator["changes"]),
                        "outcome_change_rate": float(np.mean(accumulator["changes"])) if accumulator["changes"] else np.nan,
                        "winner_changed": np.nan,
                        "finalist_set_changed": np.nan,
                        "average_rank_shift": np.nan,
                        "expert_alignment": np.nan,
                        "public_responsiveness": np.nan,
                        "notes": "Set-valued bottom-set admissibility only; judge save does not identify a unique final ranking.",
                    }
                )
                continue
            row, ranks = _scenario_metrics(
                season,
                regime,
                mechanism,
                lambda_value,
                gamma,
                scenario_id,
                accumulator["scores"],
                accumulator["changes"],
                season_data,
            )
            scenario_rows.append(row)
            contestant_rows.extend(ranks)
        if regime != "P":
            scenario_rows.append(
                {
                    "season": season,
                    "regime": regime,
                    "mechanism": "percentage_aggregation",
                    "lambda": np.nan,
                    "gamma": np.nan,
                    "scenario_id": "not_applicable",
                    "applicable": False,
                    "n_contestants": season_data["contestant_id"].nunique(),
                    "n_outcome_events": 0,
                    "outcome_change_rate": np.nan,
                    "winner_changed": np.nan,
                    "finalist_set_changed": np.nan,
                    "average_rank_shift": np.nan,
                    "expert_alignment": np.nan,
                    "public_responsiveness": np.nan,
                    "notes": "Cardinal public shares are not identified in ordinal regimes.",
                }
            )
    return pd.DataFrame(scenario_rows), pd.DataFrame(contestant_rows)


def summarize_counterfactuals(scenarios: pd.DataFrame) -> pd.DataFrame:
    group_columns = ["season", "regime", "mechanism", "lambda", "gamma", "applicable"]
    frame = scenarios.copy()
    frame["lambda_group"] = frame["lambda"].fillna(-1.0)
    frame["gamma_group"] = frame["gamma"].fillna(-1.0)
    rows = []
    for keys, group in frame.groupby(
        ["season", "regime", "mechanism", "lambda_group", "gamma_group", "applicable"],
        dropna=False,
        sort=False,
    ):
        season, regime, mechanism, lambda_group, gamma_group, applicable = keys
        rows.append(
            {
                "season": int(season),
                "regime": regime,
                "mechanism": mechanism,
                "lambda": np.nan if lambda_group == -1 else lambda_group,
                "gamma": np.nan if gamma_group == -1 else gamma_group,
                "applicable": bool(applicable),
                "n_scenarios": len(group),
                "n_contestants": int(group["n_contestants"].max()),
                "n_outcome_events": int(group["n_outcome_events"].max()),
                "outcome_change_rate": group["outcome_change_rate"].mean(),
                "winner_change_rate": pd.to_numeric(group["winner_changed"], errors="coerce").mean(),
                "finalist_set_change_rate": pd.to_numeric(group["finalist_set_changed"], errors="coerce").mean(),
                "average_rank_shift": group["average_rank_shift"].mean(),
                "rank_shift_uncertainty": group["average_rank_shift"].std(ddof=0),
                "expert_alignment": group["expert_alignment"].mean(),
                "public_responsiveness": group["public_responsiveness"].mean(),
                "uncertainty_penalty_effect": np.nan,
                "notes": "; ".join(sorted(set(group["notes"].dropna().astype(str)))),
            }
        )
    summary = pd.DataFrame(rows)
    ua = summary.loc[summary["mechanism"].eq("uncertainty_aware")].copy()
    baseline = ua.loc[ua["gamma"].eq(0), ["season", "lambda", "outcome_change_rate"]].rename(
        columns={"outcome_change_rate": "gamma_zero_change_rate"}
    )
    summary = summary.merge(baseline, on=["season", "lambda"], how="left")
    mask = summary["mechanism"].eq("uncertainty_aware")
    summary.loc[mask, "uncertainty_penalty_effect"] = (
        summary.loc[mask, "outcome_change_rate"]
        - summary.loc[mask, "gamma_zero_change_rate"]
    )
    return summary.drop(columns="gamma_zero_change_rate").sort_values(
        ["season", "mechanism", "lambda", "gamma"], na_position="first"
    ).reset_index(drop=True)


def aggregate_counterfactuals_by_regime(season_summary: pd.DataFrame) -> pd.DataFrame:
    applicable = season_summary.loc[season_summary["applicable"]].copy()
    group_columns = ["regime", "mechanism", "lambda", "gamma"]
    return (
        applicable.groupby(group_columns, dropna=False)
        .agg(
            n_seasons=("season", "nunique"),
            mean_n_scenarios=("n_scenarios", "mean"),
            mean_n_contestants=("n_contestants", "mean"),
            outcome_change_rate=("outcome_change_rate", "mean"),
            winner_change_rate=("winner_change_rate", "mean"),
            finalist_set_change_rate=("finalist_set_change_rate", "mean"),
            average_rank_shift=("average_rank_shift", "mean"),
            rank_shift_uncertainty=("rank_shift_uncertainty", "mean"),
            expert_alignment=("expert_alignment", "mean"),
            public_responsiveness=("public_responsiveness", "mean"),
            uncertainty_penalty_effect=("uncertainty_penalty_effect", "mean"),
        )
        .reset_index()
    )


def controversial_case_results(
    audit: pd.DataFrame,
    dynamic: pd.DataFrame,
    contestant_scenarios: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for case in audit.itertuples(index=False):
        if not case.matched_name or pd.isna(case.season):
            continue
        season = int(case.season)
        matches = dynamic.loc[
            dynamic["season"].eq(season)
            & dynamic["contestant_name"].astype(str).str.casefold().eq(
                str(case.matched_name).casefold()
            )
        ]
        if matches.empty:
            continue
        contestant_id = str(matches.iloc[0]["contestant_id"])
        frame = contestant_scenarios.loc[
            contestant_scenarios["season"].eq(season)
            & contestant_scenarios["contestant_id"].astype(str).eq(contestant_id)
        ]
        for keys, group in frame.groupby(["mechanism", "lambda", "gamma"], dropna=False):
            mechanism, lambda_value, gamma = keys
            rows.append(
                {
                    "contestant_name": case.contestant_name,
                    "matched_name": case.matched_name,
                    "season": season,
                    "regime": case.regime,
                    "observed_placement": float(case.placement),
                    "mechanism": mechanism,
                    "lambda": lambda_value,
                    "gamma": gamma,
                    "n_scenarios": len(group),
                    "mean_counterfactual_rank": group["counterfactual_rank"].mean(),
                    "min_counterfactual_rank": group["counterfactual_rank"].min(),
                    "max_counterfactual_rank": group["counterfactual_rank"].max(),
                    "mean_rank_shift": group["rank_shift"].mean(),
                    "probability_rank_improves": float((group["rank_shift"] < 0).mean()),
                    "probability_rank_worsens": float((group["rank_shift"] > 0).mean()),
                    "notes": "Scenario sensitivity over identified support; not a causal placement estimate.",
                }
            )
    return pd.DataFrame(rows)
