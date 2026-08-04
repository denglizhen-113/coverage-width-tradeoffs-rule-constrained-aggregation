#!/usr/bin/env python3
"""Identify feasible ordinal rankings for R and R_plus and compare regimes."""

from __future__ import annotations

import argparse
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ranking_identification import (  # noqa: E402
    DEFAULT_TIE_POLICY,
    TIE_POLICIES,
    RankingIdentificationResult,
    build_week_spec,
    evaluate_acceptance_rate,
    identify_week,
    monte_carlo_standard_error,
    plackett_luce_permutation_batches,
    proposal_worths,
    repeated_acceptance_sd,
    seeded_rng,
)


FIGURE_DPI = 300
BASE_SEED = 20260714
REGIME_COLORS = {"P": "#1F5A7A", "R": "#C45A2A", "R_plus": "#2F6B4F"}
GRAY = "#6B7280"
LIGHT_GRAY = "#D1D5DB"
EXPECTED_WEEKS = {"R": 14, "R_plus": 73}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Enumerate or sample feasible public rankings for R and R_plus, "
            "run tie-policy sensitivity, and compare identification by regime."
        )
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--panel", type=Path, default=Path("data/processed/panel_long.csv")
    )
    parser.add_argument(
        "--week-level", type=Path, default=Path("data/processed/week_level.csv")
    )
    parser.add_argument(
        "--contestant-level",
        type=Path,
        default=Path("data/processed/contestant_level.csv"),
    )
    parser.add_argument(
        "--p-bounds",
        type=Path,
        default=Path("data/processed/preference_bounds_regime_p.csv"),
    )
    parser.add_argument(
        "--p-uncertainty",
        type=Path,
        default=Path("outputs/tables/uncertainty_by_week_regime_p.csv"),
    )
    parser.add_argument("--exact-threshold", type=int, default=9)
    parser.add_argument("--r-samples", type=int, default=50_000)
    parser.add_argument("--rplus-samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=BASE_SEED)
    parser.add_argument(
        "--detail-limit",
        type=int,
        default=1_000,
        help=(
            "Maximum feasible permutations retained per week in the long audit "
            "files; full counts and distributions still use all evaluated draws."
        ),
    )
    return parser.parse_args()


def resolve(path: Path, root: Path) -> Path:
    return path if path.is_absolute() else root / path


def as_bool(value: Any) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    return str(value).strip().casefold() in {"true", "1", "yes"}


def markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    def clean(value: Any) -> str:
        if pd.isna(value):
            return ""
        return str(value).replace("|", "\\|").replace("\n", " ")

    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    output.extend(
        "| " + " | ".join(clean(value) for value in row) + " |" for row in rows
    )
    return "\n".join(output)


def csv_options() -> dict[str, Any]:
    return {
        "index": False,
        "encoding": "utf-8",
        "na_rep": "",
        "lineterminator": "\n",
        "float_format": "%.12g",
    }


def write_csv_atomic(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, **csv_options())
    temporary.replace(path)


def apply_plot_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.5,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "axes.edgecolor": "#333333",
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.labelsize": 9,
            "ytick.labelsize": 8.5,
            "legend.fontsize": 8.5,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def contestant_statistics(result: RankingIdentificationResult) -> list[dict[str, Any]]:
    spec = result.spec
    accepted = int(result.summary["n_feasible_permutations"])
    ranks = np.arange(1, spec.n_active + 1, dtype=float)
    rows: list[dict[str, Any]] = []
    for contestant in range(spec.n_active):
        counts = result.rank_counts[contestant]
        if accepted == 0 or counts.sum() == 0:
            mean = minimum = maximum = width = entropy = np.nan
        else:
            probabilities = counts / counts.sum()
            support = ranks[counts > 0]
            positive = probabilities > 0
            mean = float(np.sum(ranks * probabilities))
            minimum = float(support.min())
            maximum = float(support.max())
            width = maximum - minimum
            entropy = float(
                -np.sum(probabilities[positive] * np.log(probabilities[positive]))
            )
        rows.append(
            {
                "season": spec.season,
                "week": spec.week,
                "regime": spec.regime,
                "contestant_id": spec.contestant_ids[contestant],
                "contestant_name": spec.contestant_names[contestant],
                "judge_rank": spec.judge_ranks[contestant],
                "fan_rank_mean": mean,
                "fan_rank_min": minimum,
                "fan_rank_max": maximum,
                "fan_rank_width": width,
                "normalized_fan_rank_width": (
                    width / (spec.n_active - 1)
                    if spec.n_active > 1 and np.isfinite(width)
                    else np.nan
                ),
                "fan_rank_entropy": entropy,
                "normalized_fan_rank_entropy": (
                    entropy / math.log(spec.n_active)
                    if spec.n_active > 1 and np.isfinite(entropy)
                    else np.nan
                ),
                "n_active": spec.n_active,
                "n_feasible_permutations": accepted,
                "tie_policy": spec.tie_policy,
                "enumeration_method": result.summary["enumeration_method"],
            }
        )
    return rows


def append_detail(frame: pd.DataFrame, temporary: Path, header: bool) -> bool:
    if frame.empty:
        return header
    frame.to_csv(
        temporary,
        mode="w" if header else "a",
        header=header,
        **csv_options(),
    )
    return False


def ranking_diagnostics(
    result: RankingIdentificationResult,
    *,
    n_samples: int,
    base_seed: int,
) -> list[dict[str, Any]]:
    spec = result.spec
    repeated_n = min(2_000, n_samples)
    uniform_sd = repeated_acceptance_sd(
        spec,
        spec.regime,
        "uniform",
        base_seed,
        n_samples=repeated_n,
        n_repeats=3,
    )
    uniform_row = {
        "season": spec.season,
        "week": spec.week,
        "regime": spec.regime,
        "n_active": spec.n_active,
        "n_samples": n_samples,
        "acceptance_rate": result.summary["feasible_fraction"],
        "mc_standard_error": result.summary["mc_standard_error"],
        "repeated_run_sd": uniform_sd,
        "sampling_method": "uniform",
    }

    pl_rng = seeded_rng(base_seed, spec.season, spec.week, 1)
    pl_accepted, pl_evaluated = evaluate_acceptance_rate(
        spec,
        spec.regime,
        plackett_luce_permutation_batches(
            proposal_worths(spec, spec.regime), n_samples, pl_rng
        ),
    )
    pl_sd = repeated_acceptance_sd(
        spec,
        spec.regime,
        "plackett_luce_guided",
        base_seed,
        n_samples=repeated_n,
        n_repeats=3,
    )
    pl_row = {
        "season": spec.season,
        "week": spec.week,
        "regime": spec.regime,
        "n_active": spec.n_active,
        "n_samples": pl_evaluated,
        "acceptance_rate": pl_accepted / pl_evaluated,
        "mc_standard_error": monte_carlo_standard_error(pl_accepted, pl_evaluated),
        "repeated_run_sd": pl_sd,
        "sampling_method": "plackett_luce_guided",
    }
    return [uniform_row, pl_row]


def identify_ordinal_regimes(
    panel: pd.DataFrame,
    *,
    root: Path,
    exact_threshold: int,
    r_samples: int,
    rplus_samples: int,
    base_seed: int,
    detail_limit: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    detail_paths = {
        "R": root / "data/processed/feasible_rankings_regime_r.csv",
        "R_plus": root / "data/processed/feasible_rankings_regime_rplus.csv",
    }
    temporary_paths = {
        regime: path.with_suffix(path.suffix + ".tmp")
        for regime, path in detail_paths.items()
    }
    for path in temporary_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.unlink(missing_ok=True)
    detail_headers = {"R": True, "R_plus": True}

    summary_rows: list[dict[str, Any]] = []
    sensitivity_rows: list[dict[str, Any]] = []
    contestant_rows: list[dict[str, Any]] = []
    diagnostic_rows: list[dict[str, Any]] = []
    ordinal = panel.loc[panel["aggregation_regime"].isin(["R", "R_plus"])]
    keys = (
        ordinal[["regime_key", "season", "week"]]
        if "regime_key" in ordinal.columns
        else ordinal[["aggregation_regime", "season", "week"]].rename(
            columns={"aggregation_regime": "regime_key"}
        )
    ).drop_duplicates()
    keys = keys.sort_values(["regime_key", "season", "week"])

    for sequence, key in enumerate(keys.itertuples(index=False), start=1):
        regime = str(key.regime_key)
        week_frame = ordinal.loc[
            ordinal["aggregation_regime"].eq(regime)
            & ordinal["season"].eq(int(key.season))
            & ordinal["week"].eq(int(key.week))
        ]
        n_samples = r_samples if regime == "R" else rplus_samples
        score_tie = bool(
            week_frame.loc[week_frame["active_status"].map(as_bool), "judge_total"]
            .duplicated(keep=False)
            .any()
        )
        for tie_policy in TIE_POLICIES:
            spec = build_week_spec(week_frame, tie_policy)
            result = identify_week(
                spec,
                exact_threshold=exact_threshold,
                n_samples=n_samples,
                base_seed=base_seed,
                detail_limit=detail_limit if tie_policy == DEFAULT_TIE_POLICY else 0,
            )
            sensitivity_row = dict(result.summary)
            sensitivity_row["judge_score_tie_present"] = score_tie
            sensitivity_row["is_default_policy"] = tie_policy == DEFAULT_TIE_POLICY
            sensitivity_rows.append(sensitivity_row)

            if tie_policy != DEFAULT_TIE_POLICY:
                continue
            summary_rows.append(dict(result.summary))
            contestant_rows.extend(contestant_statistics(result))
            detail_headers[regime] = append_detail(
                result.detail, temporary_paths[regime], detail_headers[regime]
            )
            if result.summary["enumeration_method"] == "monte_carlo":
                diagnostic_rows.extend(
                    ranking_diagnostics(
                        result, n_samples=n_samples, base_seed=base_seed
                    )
                )
        if sequence % 10 == 0 or sequence == len(keys):
            print(f"Ordinal weeks completed: {sequence}/{len(keys)}")

    detail_columns = [
        "season",
        "week",
        "permutation_id",
        "contestant_id",
        "contestant_name",
        "judge_rank",
        "fan_rank",
        "combined_rank_score",
        "eliminated_this_week",
        "is_feasible",
        "bottom_two_consistent",
        "direct_elimination_consistent",
        "identifiability_loss_ratio",
        "tie_policy",
        "enumeration_method",
    ]
    for regime, target in detail_paths.items():
        temporary = temporary_paths[regime]
        if detail_headers[regime]:
            pd.DataFrame(columns=detail_columns).to_csv(temporary, **csv_options())
        temporary.replace(target)

    summaries = pd.DataFrame(summary_rows).sort_values(["regime", "season", "week"])
    sensitivity = pd.DataFrame(sensitivity_rows).sort_values(
        ["regime", "season", "week", "tie_policy"]
    )
    contestant_stats = pd.DataFrame(contestant_rows).sort_values(
        ["regime", "season", "week", "contestant_id"]
    )
    diagnostics = pd.DataFrame(diagnostic_rows).sort_values(
        ["regime", "season", "week", "sampling_method"]
    )
    return summaries, sensitivity, contestant_stats, diagnostics


def validate_ordinal_results(
    summaries: pd.DataFrame,
    sensitivity: pd.DataFrame,
    contestant_stats: pd.DataFrame,
) -> None:
    counts = summaries.groupby("regime").size().to_dict()
    if counts != EXPECTED_WEEKS:
        raise ValueError(f"Unexpected ordinal week counts: {counts}")
    if len(sensitivity) != sum(EXPECTED_WEEKS.values()) * len(TIE_POLICIES):
        raise ValueError("Tie-policy sensitivity table has an unexpected row count.")
    if summaries[["season", "week", "regime"]].duplicated().any():
        raise ValueError("Duplicate season-week-regime rows in ranking summaries.")
    for column in (
        "feasible_fraction",
        "normalized_rank_width",
        "normalized_ranking_entropy",
    ):
        valid = summaries[column].dropna()
        if not valid.between(0.0, 1.0).all():
            raise ValueError(f"{column} falls outside [0, 1].")
    rplus = summaries.loc[summaries["regime"].eq("R_plus")]
    finite_ratio = rplus["identifiability_loss_ratio"].dropna()
    if (finite_ratio < 1.0 - 1e-12).any():
        raise ValueError("R_plus feasible set is smaller than direct R-like set.")
    expected_contestants = int(summaries["n_active"].sum())
    if len(contestant_stats) != expected_contestants:
        raise ValueError("Contestant ranking summaries do not reconcile to n_active.")


def summary_column_order() -> list[str]:
    return [
        "season",
        "week",
        "regime",
        "n_active",
        "n_total_permutations",
        "n_evaluated_permutations",
        "n_feasible_permutations",
        "feasible_fraction",
        "ranking_entropy",
        "normalized_ranking_entropy",
        "mean_fan_rank_width",
        "max_fan_rank_width",
        "normalized_rank_width",
        "eliminated_fan_rank_mean",
        "eliminated_fan_rank_min",
        "eliminated_fan_rank_max",
        "n_feasible_direct_R_like",
        "feasible_fraction_direct_R_like",
        "identifiability_loss_ratio",
        "tie_policy",
        "finale_week",
        "double_elimination_week",
        "finale_order_available",
        "skip_reason",
        "enumeration_method",
        "sampling_method",
        "mc_standard_error",
        "feasible_count_type",
        "estimated_n_feasible_permutations",
        "detail_retained_permutations",
        "detail_truncated",
        "detail_retention_method",
    ]


def build_ranking_report(
    regime: str,
    summary: pd.DataFrame,
    sensitivity: pd.DataFrame,
    diagnostics: pd.DataFrame,
    detail_limit: int,
    n_samples: int,
) -> str:
    exact = summary.loc[summary["enumeration_method"].eq("exact")]
    sampled = summary.loc[summary["enumeration_method"].eq("monte_carlo")]
    event_counts = {
        "Finale": int(summary["finale_week"].map(as_bool).sum()),
        "Multiple elimination": int(summary["double_elimination_week"].map(as_bool).sum()),
    }
    sensitivity_agg = (
        sensitivity.groupby("tie_policy", sort=False)
        .agg(
            mean_feasible_fraction=("feasible_fraction", "mean"),
            mean_normalized_rank_width=("normalized_rank_width", "mean"),
            mean_normalized_entropy=("normalized_ranking_entropy", "mean"),
        )
        .reset_index()
    )
    lines = [
        f"# Ranking Identification Report: {regime}",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Scope",
        "",
        (
            "The estimand is the feasible set of strict public rankings induced "
            "by the observed ordinal aggregation outcome. The analysis does not "
            "recover cardinal public vote shares or a true audience vote."
        ),
        "",
        "## Coverage and computation",
        "",
        markdown_table(
            ["Metric", "Value"],
            [
                ("Season-weeks", len(summary)),
                ("Exact enumeration weeks", len(exact)),
                ("Monte Carlo weeks", len(sampled)),
                ("Monte Carlo draws per sampled week", n_samples if len(sampled) else 0),
                ("Finales", event_counts["Finale"]),
                ("Multiple-elimination weeks", event_counts["Multiple elimination"]),
                ("Mean feasible fraction", f"{summary['feasible_fraction'].mean():.6f}"),
                ("Mean normalized rank width", f"{summary['normalized_rank_width'].mean():.6f}"),
                ("Mean normalized entropy", f"{summary['normalized_ranking_entropy'].mean():.6f}"),
            ],
        ),
        "",
        (
            f"Exact weeks use all `n_active!` permutations. Sampled weeks use a "
            f"fixed seed and uniform random permutations. The long feasible-ranking "
            f"file retains at most {detail_limit:,} feasible permutations per week "
            f"using a fixed-seed reservoir sample; "
            "this storage cap does not affect counts, rank distributions, entropy, "
            "or widths, all of which use every evaluated permutation or draw."
        ),
        "",
        "For sampled weeks, `n_feasible_permutations` is the number of accepted Monte Carlo draws, not the unknown exact cardinality of the feasible set. `feasible_fraction` is the uniform Monte Carlo estimate and `estimated_n_feasible_permutations` scales that estimate by `n_active!`.",
        "",
        "## Tie-policy sensitivity",
        "",
        markdown_table(
            ["Tie policy", "Mean feasible fraction", "Mean normalized width", "Mean normalized entropy"],
            (
                (
                    row.tie_policy,
                    f"{row.mean_feasible_fraction:.6f}",
                    f"{row.mean_normalized_rank_width:.6f}",
                    f"{row.mean_normalized_entropy:.6f}",
                )
                for row in sensitivity_agg.itertuples(index=False)
            ),
        ),
        "",
        "The primary output uses `average_rank`. `min_rank` and `competition_rank` are algebraically identical for the static judge-rank calculation and are retained as separately labeled sensitivity rows.",
        "",
    ]
    if regime == "R_plus":
        ratios = summary["identifiability_loss_ratio"].dropna()
        lines.extend(
            [
                "## Judge-save identifiability loss",
                "",
                markdown_table(
                    ["Metric", "Value"],
                    [
                        ("Mean R_plus/direct R-like ratio", f"{ratios.mean():.6f}"),
                        ("Median ratio", f"{ratios.median():.6f}"),
                        ("Weeks with ratio > 1", int((ratios > 1 + 1e-12).sum())),
                        ("Weeks with ratio = 1", int(np.isclose(ratios, 1.0).sum())),
                        ("Weeks with undefined ratio", int(summary["identifiability_loss_ratio"].isna().sum())),
                    ],
                ),
                "",
                "The weak judge-save rule requires the observed eliminated set to lie in the tie-inclusive bottom-(k+1) set. The direct R-like comparison requires bottom-k membership on the same permutations. Because the direct condition is nested in the weak condition, the computed ratio cannot fall below one apart from numerical or implementation error.",
                "",
            ]
        )
    if not diagnostics.empty:
        diagnostic_summary = (
            diagnostics.groupby("sampling_method")
            .agg(
                weeks=("week", "size"),
                mean_acceptance=("acceptance_rate", "mean"),
                max_mc_se=("mc_standard_error", "max"),
                max_repeat_sd=("repeated_run_sd", "max"),
            )
            .reset_index()
        )
        lines.extend(
            [
                "## Sampling diagnostics",
                "",
                markdown_table(
                    ["Method", "Weeks", "Mean acceptance", "Max MC SE", "Max repeated-run SD"],
                    (
                        (
                            row.sampling_method,
                            row.weeks,
                            f"{row.mean_acceptance:.6f}",
                            f"{row.max_mc_se:.6f}",
                            f"{row.max_repeat_sd:.6f}",
                        )
                        for row in diagnostic_summary.itertuples(index=False)
                    ),
                ),
                "",
                "Uniform sampling supplies the reported feasible fractions. The Plackett-Luce-guided acceptance rate is proposal-specific and is used only as a diagnostic baseline; its item worths are not estimates of public appeal.",
                "",
            ]
        )
    top = summary.nlargest(5, "normalized_rank_width")
    lines.extend(
        [
            "## Highest-uncertainty weeks",
            "",
            markdown_table(
                ["Season", "Week", "Active", "Method", "Normalized width", "Feasible fraction"],
                (
                    (
                        int(row.season),
                        int(row.week),
                        int(row.n_active),
                        row.enumeration_method,
                        f"{row.normalized_rank_width:.6f}",
                        f"{row.feasible_fraction:.6f}",
                    )
                    for row in top.itertuples(index=False)
                ),
            ),
            "",
            "## Limitations",
            "",
            "- Strict fan rankings exclude tied public preferences; a weak-order state space would be a separate model.",
            "- Combined-score boundary ties are tie-inclusive modeling assumptions because no tie rule document is available in the workspace.",
            "- Withdrawals are not ranked eliminations and are excluded from the outcome-comparison set.",
            "- Monte Carlo uncertainty describes numerical estimation of feasible fractions, not sampling uncertainty in audience behavior.",
            "",
        ]
    )
    return "\n".join(lines)


def comparison_tables(
    p_uncertainty: pd.DataFrame, ordinal_summary: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    p_valid = p_uncertainty.loc[
        p_uncertainty["feasible"].map(as_bool) & p_uncertainty["mean_width"].notna()
    ].copy()
    p_week = pd.DataFrame(
        {
            "season": p_valid["season"],
            "week": p_valid["week"],
            "regime": "P",
            "n_active": p_valid["n_active"],
            "normalized_uncertainty": p_valid["mean_width"],
            "normalized_entropy": np.nan,
            "feasible_fraction": np.nan,
            "finale_week": p_valid["finale_week"].map(as_bool),
            "enumeration_method": "linear_programming",
        }
    )
    ordinal_week = ordinal_summary.rename(
        columns={
            "normalized_rank_width": "normalized_uncertainty",
            "normalized_ranking_entropy": "normalized_entropy",
        }
    )[
        [
            "season",
            "week",
            "regime",
            "n_active",
            "normalized_uncertainty",
            "normalized_entropy",
            "feasible_fraction",
            "finale_week",
            "enumeration_method",
        ]
    ].copy()
    week_comparison = pd.concat([p_week, ordinal_week], ignore_index=True)
    rows: list[dict[str, Any]] = []
    for regime in ("P", "R", "R_plus"):
        frame = week_comparison.loc[week_comparison["regime"].eq(regime)]
        rows.append(
            {
                "regime": regime,
                "n_weeks": len(frame),
                "mean_normalized_uncertainty": frame[
                    "normalized_uncertainty"
                ].mean(),
                "median_normalized_uncertainty": frame[
                    "normalized_uncertainty"
                ].median(),
                "mean_entropy": frame["normalized_entropy"].mean(),
                "median_entropy": frame["normalized_entropy"].median(),
                "mean_feasible_fraction": frame["feasible_fraction"].mean(),
                "mean_n_active": frame["n_active"].mean(),
                "notes": (
                    "Mean coordinate-wise feasible-share interval width; entropy and feasible fraction are not defined for the continuous polytope."
                    if regime == "P"
                    else "Mean fan-rank support width divided by n_active-1; entropy is normalized by log(n_active)."
                ),
            }
        )
    return pd.DataFrame(rows), week_comparison


def plot_identification_width(week_data: pd.DataFrame, path: Path) -> None:
    apply_plot_style()
    regimes = ["P", "R", "R_plus"]
    values = [
        week_data.loc[week_data["regime"].eq(regime), "normalized_uncertainty"]
        .dropna()
        .to_numpy()
        for regime in regimes
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)
    box = ax.boxplot(
        values,
        positions=np.arange(len(regimes)),
        widths=0.52,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#222222", "linewidth": 1.4},
        whiskerprops={"color": GRAY},
        capprops={"color": GRAY},
        boxprops={"edgecolor": GRAY, "linewidth": 0.9},
    )
    rng = np.random.default_rng(913)
    for position, (regime, data, patch) in enumerate(zip(regimes, values, box["boxes"])):
        patch.set_facecolor(REGIME_COLORS[regime])
        patch.set_alpha(0.20)
        jitter = rng.uniform(-0.16, 0.16, size=len(data))
        ax.scatter(
            position + jitter,
            data,
            s=16 if regime == "P" else 22,
            color=REGIME_COLORS[regime],
            alpha=0.38 if regime == "P" else 0.58,
            linewidths=0,
        )
        ax.plot(position, np.mean(data), marker="D", color="#222222", markersize=5)
    ax.set_xticks(np.arange(len(regimes)), ["Percentage (P)", "Ranking (R)", "Ranking + save (R_plus)"])
    ax.set_ylabel("Normalized identification uncertainty")
    ax.set_title("Mechanism-specific normalized uncertainty by regime")
    ax.set_ylim(0, 1.04)
    ax.grid(axis="y", color=LIGHT_GRAY, linewidth=0.6, alpha=0.75)
    ax.text(
        0.01,
        0.02,
        "Diamonds show means; P uses share-interval width, R regimes use normalized rank width.",
        transform=ax.transAxes,
        color=GRAY,
        fontsize=8,
    )
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def plot_feasible_fraction(week_data: pd.DataFrame, path: Path) -> None:
    apply_plot_style()
    ordinal = week_data.loc[week_data["regime"].isin(["R", "R_plus"])].copy()
    regimes = ["R", "R_plus"]
    values = [
        ordinal.loc[ordinal["regime"].eq(regime), "feasible_fraction"]
        .dropna()
        .to_numpy()
        for regime in regimes
    ]
    fig, ax = plt.subplots(figsize=(6.6, 4.5), constrained_layout=True)
    box = ax.boxplot(
        values,
        positions=[0, 1],
        widths=0.5,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#222222", "linewidth": 1.4},
        whiskerprops={"color": GRAY},
        capprops={"color": GRAY},
        boxprops={"edgecolor": GRAY, "linewidth": 0.9},
    )
    for regime, patch in zip(regimes, box["boxes"]):
        patch.set_facecolor(REGIME_COLORS[regime])
        patch.set_alpha(0.20)
    rng = np.random.default_rng(914)
    for position, regime in enumerate(regimes):
        frame = ordinal.loc[ordinal["regime"].eq(regime)]
        for method, marker, label in (
            ("exact", "o", "Exact"),
            ("monte_carlo", "^", "Monte Carlo"),
        ):
            subset = frame.loc[frame["enumeration_method"].eq(method)]
            jitter = rng.uniform(-0.15, 0.15, size=len(subset))
            ax.scatter(
                position + jitter,
                subset["feasible_fraction"],
                s=28,
                marker=marker,
                color=REGIME_COLORS[regime],
                alpha=0.68,
                linewidths=0,
                label=label if position == 0 else None,
            )
    ax.set_xticks([0, 1], ["Ranking (R)", "Ranking + save (R_plus)"])
    ax.set_ylabel("Feasible fraction of evaluated rankings")
    ax.set_title("Ordinal feasible-set fraction by regime")
    ax.set_ylim(0, 1.04)
    ax.grid(axis="y", color=LIGHT_GRAY, linewidth=0.6, alpha=0.75)
    ax.legend(frameon=False, loc="upper right")
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def plot_judge_save_loss(rplus: pd.DataFrame, path: Path) -> None:
    apply_plot_style()
    frame = rplus.sort_values(["season", "week"]).copy()
    frame["sequence"] = np.arange(len(frame))
    finite = frame.loc[frame["identifiability_loss_ratio"].notna()].copy()
    fig, ax = plt.subplots(figsize=(8.0, 4.7), constrained_layout=True)
    for season, season_frame in finite.groupby("season"):
        ax.plot(
            season_frame["sequence"],
            season_frame["identifiability_loss_ratio"],
            color=LIGHT_GRAY,
            linewidth=0.9,
            zorder=1,
        )
    for method, marker, label in (
        ("exact", "o", "Exact enumeration"),
        ("monte_carlo", "^", "Monte Carlo"),
    ):
        subset = finite.loc[finite["enumeration_method"].eq(method)]
        ax.scatter(
            subset["sequence"],
            subset["identifiability_loss_ratio"],
            s=32,
            marker=marker,
            color=REGIME_COLORS["R_plus"],
            alpha=0.78,
            linewidths=0,
            label=label,
            zorder=2,
        )
    ax.axhline(1.0, color="#222222", linewidth=1.0, linestyle="--", label="No expansion")
    season_ticks = (
        frame.groupby("season")["sequence"].mean().reset_index().sort_values("season")
    )
    ax.set_xticks(season_ticks["sequence"], [f"S{int(s)}" for s in season_ticks["season"]])
    ax.set_xlabel("Season (weeks ordered within season)")
    ax.set_ylabel("Feasible-set ratio: R_plus / direct R-like")
    ax.set_title("Judge-save mechanism-induced identifiability loss")
    maximum = float(finite["identifiability_loss_ratio"].max())
    ax.set_yscale("log")
    ticks = [value for value in (1, 2, 5, 10, 20, 50, 100) if value <= maximum * 1.2]
    ax.set_yticks(ticks, [str(value) for value in ticks])
    ax.set_ylim(0.95, maximum * 1.25)
    outlier = finite.nlargest(1, "identifiability_loss_ratio").iloc[0]
    ax.annotate(
        f"S{int(outlier.season)} W{int(outlier.week)}: "
        f"{outlier.identifiability_loss_ratio:.2f}x",
        xy=(outlier.sequence, outlier.identifiability_loss_ratio),
        xytext=(10, -12),
        textcoords="offset points",
        color=GRAY,
        fontsize=8,
    )
    ax.grid(axis="y", which="major", color=LIGHT_GRAY, linewidth=0.6, alpha=0.75)
    ax.legend(frameon=False, ncol=3, loc="upper center")
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def build_regime_report(
    comparison: pd.DataFrame,
    week_data: pd.DataFrame,
    rplus: pd.DataFrame,
) -> str:
    display = comparison.copy()
    ratios = rplus["identifiability_loss_ratio"].dropna()
    week_data = week_data.copy()
    week_data["season_max_week"] = week_data.groupby(["regime", "season"])[
        "week"
    ].transform("max")
    week_data["progress"] = week_data["week"] / week_data["season_max_week"]
    phase_rows = []
    for regime in ("P", "R", "R_plus"):
        frame = week_data.loc[week_data["regime"].eq(regime)]
        early = frame.loc[frame["progress"] <= 1 / 3, "normalized_uncertainty"]
        late = frame.loc[frame["progress"] >= 2 / 3, "normalized_uncertainty"]
        finale = frame.loc[frame["finale_week"].map(as_bool), "normalized_uncertainty"]
        nonfinale = frame.loc[~frame["finale_week"].map(as_bool), "normalized_uncertainty"]
        phase_rows.append(
            (
                regime,
                f"{early.mean():.6f}",
                f"{late.mean():.6f}",
                f"{finale.mean():.6f}",
                f"{nonfinale.mean():.6f}",
            )
        )
    p_mean = float(
        display.loc[display["regime"].eq("P"), "mean_normalized_uncertainty"].iloc[0]
    )
    r_mean = float(
        display.loc[display["regime"].eq("R"), "mean_normalized_uncertainty"].iloc[0]
    )
    rp_mean = float(
        display.loc[
            display["regime"].eq("R_plus"), "mean_normalized_uncertainty"
        ].iloc[0]
    )
    lines = [
        "# Cross-Regime Identification Comparison",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Standardized comparison",
        "",
        markdown_table(
            ["Regime", "Weeks", "Mean uncertainty", "Median uncertainty", "Mean entropy", "Mean feasible fraction", "Mean active"],
            (
                (
                    row.regime,
                    int(row.n_weeks),
                    f"{row.mean_normalized_uncertainty:.6f}",
                    f"{row.median_normalized_uncertainty:.6f}",
                    "" if pd.isna(row.mean_entropy) else f"{row.mean_entropy:.6f}",
                    "" if pd.isna(row.mean_feasible_fraction) else f"{row.mean_feasible_fraction:.6f}",
                    f"{row.mean_n_active:.3f}",
                )
                for row in display.itertuples(index=False)
            ),
        ),
        "",
        "P uncertainty is the mean coordinate-wise feasible-share interval width. R and R_plus uncertainty is the mean fan-rank support width divided by `n_active - 1`. Both lie in [0,1], but they are mechanism-specific standardized summaries rather than a shared cardinal estimand. Entropy and feasible fraction are therefore left undefined for P.",
        "",
        "## Results",
        "",
        f"- P has mean normalized uncertainty {p_mean:.6f}, compared with {r_mean:.6f} for R. The numerical ordering is descriptive evidence about mechanism-specific identification and is not an equality of units.",
        f"- R_plus has mean normalized rank uncertainty {rp_mean:.6f}, compared with {r_mean:.6f} for R.",
        f"- Within the same R_plus weeks and evaluated permutations, the mean weak/direct feasible-set ratio is {ratios.mean():.6f}; {int((ratios > 1 + 1e-12).sum())} of {len(ratios)} defined weeks strictly expand and no defined week contracts.",
        "",
        "## Competition phase and finales",
        "",
        markdown_table(
            ["Regime", "Early mean", "Late mean", "Finale mean", "Non-finale mean"],
            phase_rows,
        ),
        "",
        "Early means use the first third of within-season week progress and late means use the final third. Finale comparisons condition on the mechanism-specific outcome encoding; complete final placements can be substantially more informative than elimination-only observations.",
        "",
        "## Interpretation boundary",
        "",
        "The judge-save inclusion result is the clean within-week mechanism comparison: the direct R-like feasible set is a subset of the weak bottom-two set. Cross-regime averages also differ in seasons, active-field sizes, event mixes, and score patterns, so they are descriptive rather than causal estimates of a rule change.",
        "",
    ]
    return "\n".join(lines)


def controversial_case_audit(
    panel: pd.DataFrame,
    contestant_level: pd.DataFrame,
    p_bounds: pd.DataFrame,
    contestant_rank_stats: pd.DataFrame,
) -> pd.DataFrame:
    targets = ["Jerry Rice", "Billy Ray Cyrus", "Bristol Palin", "Bobby Bones"]
    rows: list[dict[str, Any]] = []
    for target in targets:
        matches = contestant_level.loc[
            contestant_level["contestant_name"].astype(str).str.casefold().eq(
                target.casefold()
            )
        ].sort_values("season")
        if matches.empty:
            rows.append(
                {
                    "contestant_name": target,
                    "matched_name": "",
                    "season": np.nan,
                    "placement": np.nan,
                    "regime": "",
                    "weeks_active": 0,
                    "mean_judge_pct": np.nan,
                    "mean_inferred_public_support_midpoint_if_P": np.nan,
                    "mean_fan_rank_if_R_or_Rplus": np.nan,
                    "uncertainty_width_or_rank_width": np.nan,
                    "notes": "No case-insensitive exact-name match in contestant_level.csv.",
                }
            )
            continue
        for match in matches.itertuples(index=False):
            season = int(match.season)
            contestant_id = str(match.contestant_id)
            active = panel.loc[
                panel["season"].eq(season)
                & panel["contestant_id"].astype(str).eq(contestant_id)
                & panel["active_status"].map(as_bool)
            ]
            judge_mean = pd.to_numeric(active["judge_pct"], errors="coerce").mean()
            support_midpoint = np.nan
            mean_rank = np.nan
            uncertainty = np.nan
            if match.aggregation_regime == "P":
                identified = p_bounds.loc[
                    p_bounds["season"].eq(season)
                    & p_bounds["contestant_id"].astype(str).eq(contestant_id)
                    & p_bounds["feasible"].map(as_bool)
                ]
                support_midpoint = pd.to_numeric(
                    identified["midpoint"], errors="coerce"
                ).mean()
                uncertainty = pd.to_numeric(
                    identified["interval_width"], errors="coerce"
                ).mean()
                notes = (
                    "P-regime coordinate midpoints and interval widths are "
                    "descriptive feasible-support summaries, not recovered votes."
                )
            else:
                identified = contestant_rank_stats.loc[
                    contestant_rank_stats["season"].eq(season)
                    & contestant_rank_stats["contestant_id"].astype(str).eq(
                        contestant_id
                    )
                ]
                mean_rank = pd.to_numeric(
                    identified["fan_rank_mean"], errors="coerce"
                ).mean()
                uncertainty = pd.to_numeric(
                    identified["fan_rank_width"], errors="coerce"
                ).mean()
                methods = ", ".join(sorted(identified["enumeration_method"].unique()))
                notes = (
                    "Ordinal feasible fan-rank summaries; no cardinal support "
                    f"interval is assigned. Week methods: {methods}."
                )
            rows.append(
                {
                    "contestant_name": target,
                    "matched_name": match.contestant_name,
                    "season": season,
                    "placement": int(match.placement),
                    "regime": match.aggregation_regime,
                    "weeks_active": len(active),
                    "mean_judge_pct": judge_mean,
                    "mean_inferred_public_support_midpoint_if_P": support_midpoint,
                    "mean_fan_rank_if_R_or_Rplus": mean_rank,
                    "uncertainty_width_or_rank_width": uncertainty,
                    "notes": notes,
                }
            )
    return pd.DataFrame(rows)


def build_case_report(cases: pd.DataFrame) -> str:
    return "\n".join(
        [
            "# Controversial Cases: Identification-Level Audit",
            "",
            f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
            "",
            "This preliminary audit reports only mechanism-appropriate identification summaries. It does not estimate a counterfactual placement and does not recover a true public vote.",
            "",
            markdown_table(
                ["Case", "Season", "Placement", "Regime", "Active weeks", "Mean judge share", "P midpoint", "Ordinal mean rank", "Uncertainty"],
                (
                    (
                        row.matched_name or row.contestant_name,
                        "" if pd.isna(row.season) else int(row.season),
                        "" if pd.isna(row.placement) else int(row.placement),
                        row.regime,
                        int(row.weeks_active),
                        "" if pd.isna(row.mean_judge_pct) else f"{row.mean_judge_pct:.6f}",
                        "" if pd.isna(row.mean_inferred_public_support_midpoint_if_P) else f"{row.mean_inferred_public_support_midpoint_if_P:.6f}",
                        "" if pd.isna(row.mean_fan_rank_if_R_or_Rplus) else f"{row.mean_fan_rank_if_R_or_Rplus:.6f}",
                        "" if pd.isna(row.uncertainty_width_or_rank_width) else f"{row.uncertainty_width_or_rank_width:.6f}",
                    )
                    for row in cases.itertuples(index=False)
                ),
            ),
            "",
            "Jerry Rice is evaluated under R using feasible fan-rank distributions. Billy Ray Cyrus, Bristol Palin, and Bobby Bones are evaluated under P using feasible public-support intervals. Bristol Palin appears in two seasons and is retained as two contestant-season observations. No case is forced into an incompatible mechanism-specific estimand.",
            "",
            "The next counterfactual stage should condition on these identified sets rather than substitute point estimates for the hidden public signal.",
            "",
        ]
    )


def validate_figures(paths: list[Path]) -> None:
    from PIL import Image

    for path in paths:
        with Image.open(path) as image:
            array = np.asarray(image.convert("RGB"))
            if image.width < 1_500 or image.height < 900:
                raise ValueError(f"Figure resolution is too small: {path}")
            if float(array.std()) < 2.0:
                raise ValueError(f"Figure appears blank: {path}")


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    if args.exact_threshold < 1 or args.r_samples < 1 or args.rplus_samples < 1:
        print("ERROR: thresholds and sample counts must be positive.", file=sys.stderr)
        return 2
    if args.detail_limit < 0:
        print("ERROR: --detail-limit must be nonnegative.", file=sys.stderr)
        return 2

    paths = {
        "panel": resolve(args.panel, root),
        "week": resolve(args.week_level, root),
        "contestant": resolve(args.contestant_level, root),
        "p_bounds": resolve(args.p_bounds, root),
        "p_uncertainty": resolve(args.p_uncertainty, root),
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        print(f"ERROR: Missing required input(s): {', '.join(missing)}", file=sys.stderr)
        print("Run the preprocessing and P-regime stages first.", file=sys.stderr)
        return 2

    try:
        panel = pd.read_csv(paths["panel"])
        week_level = pd.read_csv(paths["week"])
        contestant_level = pd.read_csv(paths["contestant"])
        p_bounds = pd.read_csv(paths["p_bounds"])
        p_uncertainty = pd.read_csv(paths["p_uncertainty"])
        summaries, sensitivity, contestant_stats, diagnostics = (
            identify_ordinal_regimes(
                panel,
                root=root,
                exact_threshold=args.exact_threshold,
                r_samples=args.r_samples,
                rplus_samples=args.rplus_samples,
                base_seed=args.seed,
                detail_limit=args.detail_limit,
            )
        )
        validate_ordinal_results(summaries, sensitivity, contestant_stats)

        tables_dir = root / "outputs/tables"
        logs_dir = root / "outputs/logs"
        figures_dir = root / "outputs/figures"
        tables_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)
        figures_dir.mkdir(parents=True, exist_ok=True)

        ordered_columns = summary_column_order()
        r_summary = summaries.loc[summaries["regime"].eq("R"), ordered_columns]
        rplus_summary = summaries.loc[
            summaries["regime"].eq("R_plus"), ordered_columns
        ]
        write_csv_atomic(
            r_summary, tables_dir / "ranking_identification_summary_r.csv"
        )
        write_csv_atomic(
            rplus_summary, tables_dir / "ranking_identification_summary_rplus.csv"
        )
        write_csv_atomic(
            sensitivity, tables_dir / "ranking_tie_policy_sensitivity.csv"
        )
        write_csv_atomic(
            contestant_stats, tables_dir / "ranking_contestant_identification.csv"
        )
        write_csv_atomic(
            diagnostics, tables_dir / "ranking_sampling_diagnostics.csv"
        )

        r_sensitivity = sensitivity.loc[sensitivity["regime"].eq("R")]
        rp_sensitivity = sensitivity.loc[sensitivity["regime"].eq("R_plus")]
        logs_dir.joinpath("ranking_identification_report_r.md").write_text(
            build_ranking_report(
                "R",
                r_summary,
                r_sensitivity,
                diagnostics.loc[diagnostics["regime"].eq("R")],
                args.detail_limit,
                args.r_samples,
            ),
            encoding="utf-8",
            newline="\n",
        )
        logs_dir.joinpath("ranking_identification_report_rplus.md").write_text(
            build_ranking_report(
                "R_plus",
                rplus_summary,
                rp_sensitivity,
                diagnostics.loc[diagnostics["regime"].eq("R_plus")],
                args.detail_limit,
                args.rplus_samples,
            ),
            encoding="utf-8",
            newline="\n",
        )

        comparison, week_comparison = comparison_tables(p_uncertainty, summaries)
        write_csv_atomic(
            comparison, tables_dir / "identification_comparison_by_regime.csv"
        )
        figure_paths = [
            figures_dir / "identification_width_by_regime.png",
            figures_dir / "feasible_fraction_by_regime.png",
            figures_dir / "judge_save_identifiability_loss.png",
        ]
        plot_identification_width(week_comparison, figure_paths[0])
        plot_feasible_fraction(week_comparison, figure_paths[1])
        plot_judge_save_loss(rplus_summary, figure_paths[2])
        validate_figures(figure_paths)
        logs_dir.joinpath("regime_comparison_report.md").write_text(
            build_regime_report(comparison, week_comparison, rplus_summary),
            encoding="utf-8",
            newline="\n",
        )

        cases = controversial_case_audit(
            panel, contestant_level, p_bounds, contestant_stats
        )
        write_csv_atomic(
            cases, tables_dir / "controversial_cases_identification_audit.csv"
        )
        logs_dir.joinpath("controversial_cases_identification_audit.md").write_text(
            build_case_report(cases), encoding="utf-8", newline="\n"
        )

        expected_week_rows = int(
            week_level["aggregation_regime"].isin(["R", "R_plus"]).sum()
        )
        if expected_week_rows != len(summaries):
            raise ValueError("Ranking summaries do not reconcile to week_level.csv.")
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    exact_counts = (
        summaries.loc[summaries["enumeration_method"].eq("exact")]
        .groupby("regime")
        .size()
        .to_dict()
    )
    sampled_counts = (
        summaries.loc[summaries["enumeration_method"].eq("monte_carlo")]
        .groupby("regime")
        .size()
        .to_dict()
    )
    print(f"R weeks: {len(r_summary)} ({exact_counts.get('R', 0)} exact, {sampled_counts.get('R', 0)} sampled)")
    print(f"R_plus weeks: {len(rplus_summary)} ({exact_counts.get('R_plus', 0)} exact, {sampled_counts.get('R_plus', 0)} sampled)")
    print(f"Tables: {root / 'outputs/tables'}")
    print(f"Figures: {root / 'outputs/figures'}")
    print(f"Reports: {root / 'outputs/logs'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
