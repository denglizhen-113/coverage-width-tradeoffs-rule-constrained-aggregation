#!/usr/bin/env python3
"""Run set-aware aggregation mechanism counterfactuals."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.counterfactuals import (  # noqa: E402
    aggregate_counterfactuals_by_regime,
    controversial_case_results,
    simulate_counterfactuals,
    summarize_counterfactuals,
)


FIGURE_DPI = 300
COLORS = {
    "P": "#1F5A7A",
    "R": "#C45A2A",
    "R_plus": "#2F6B4F",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare observed, ranking, percentage, judge-save, and uncertainty-aware mechanisms."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--dynamic", type=Path, default=Path("data/processed/dynamic_public_appeal.csv")
    )
    parser.add_argument(
        "--week-level", type=Path, default=Path("data/processed/week_level.csv")
    )
    parser.add_argument(
        "--feasible-r", type=Path, default=Path("data/processed/feasible_rankings_regime_r.csv")
    )
    parser.add_argument(
        "--feasible-rplus", type=Path, default=Path("data/processed/feasible_rankings_regime_rplus.csv")
    )
    parser.add_argument(
        "--case-audit", type=Path, default=Path("outputs/tables/controversial_cases_identification_audit.csv")
    )
    parser.add_argument("--seed", type=int, default=20260714)
    parser.add_argument("--max-ranking-samples", type=int, default=20)
    return parser.parse_args()


def resolve(path: Path, root: Path) -> Path:
    return path if path.is_absolute() else root / path


def selected_mechanisms(frame: pd.DataFrame) -> pd.DataFrame:
    base = frame.loc[frame["mechanism"].isin(
        ["original_observed", "percentage_aggregation", "direct_ranking", "ranking_plus_judge_save_weak"]
    )]
    ua = frame.loc[
        frame["mechanism"].eq("uncertainty_aware")
        & frame["lambda"].eq(0.5)
        & frame["gamma"].eq(0.5)
    ]
    return pd.concat([base, ua], ignore_index=True)


def plot_outcome_changes(by_regime: pd.DataFrame, path: Path) -> None:
    frame = selected_mechanisms(by_regime).copy()
    frame["display"] = frame["mechanism"].replace(
        {
            "original_observed": "Observed",
            "percentage_aggregation": "Percentage",
            "direct_ranking": "Direct ranking",
            "ranking_plus_judge_save_weak": "Judge-save admissibility",
            "uncertainty_aware": "Uncertainty-aware\n(lambda=.5, gamma=.5)",
        }
    )
    order = ["Observed", "Percentage", "Direct ranking", "Judge-save admissibility", "Uncertainty-aware\n(lambda=.5, gamma=.5)"]
    x = np.arange(len(order))
    width = 0.24
    fig, ax = plt.subplots(figsize=(9.0, 4.8), constrained_layout=True)
    for offset, regime in zip((-width, 0, width), ("P", "R", "R_plus")):
        subset = frame.loc[frame["regime"].eq(regime)].set_index("display")
        values = [subset.loc[label, "outcome_change_rate"] if label in subset.index else np.nan for label in order]
        ax.bar(x + offset, values, width=width, color=COLORS[regime], alpha=0.82, label=regime)
    ax.set_xticks(x, order)
    ax.set_ylabel("Outcome-change / inadmissibility rate")
    ax.set_title("Observed elimination changes under alternative mechanisms")
    ax.set_ylim(0, 1)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.6, alpha=0.7)
    ax.legend(frameon=False, ncol=3)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def plot_case_results(cases: pd.DataFrame, path: Path) -> None:
    frame = cases.loc[
        cases["mechanism"].isin(["original_observed", "percentage_aggregation", "direct_ranking"])
        | (
            cases["mechanism"].eq("uncertainty_aware")
            & cases["lambda"].eq(0.5)
            & cases["gamma"].eq(0.5)
        )
    ].copy()
    frame["case"] = frame["matched_name"] + " S" + frame["season"].astype(int).astype(str)
    frame["display"] = frame["mechanism"].replace(
        {
            "original_observed": "Observed",
            "percentage_aggregation": "Percentage",
            "direct_ranking": "Direct ranking",
            "uncertainty_aware": "Uncertainty-aware",
        }
    )
    cases_order = list(dict.fromkeys(frame["case"]))
    mechanisms = ["Observed", "Percentage", "Direct ranking", "Uncertainty-aware"]
    x = np.arange(len(cases_order))
    width = 0.19
    palette = ["#6B7280", "#1F5A7A", "#C45A2A", "#2F6B4F"]
    fig, ax = plt.subplots(figsize=(9.0, 4.8), constrained_layout=True)
    for index, (mechanism, color) in enumerate(zip(mechanisms, palette)):
        subset = frame.loc[frame["display"].eq(mechanism)].set_index("case")
        values = [subset.loc[label, "mean_rank_shift"] if label in subset.index else np.nan for label in cases_order]
        ax.bar(x + (index - 1.5) * width, values, width=width, color=color, alpha=0.82, label=mechanism)
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_xticks(x, cases_order, rotation=20, ha="right")
    ax.set_ylabel("Mean counterfactual rank shift (+ = worse)")
    ax.set_title("Controversial cases across identified-set scenarios")
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.6, alpha=0.7)
    ax.legend(frameon=False, ncol=4, fontsize=8)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def plot_lambda_gamma(by_regime: pd.DataFrame, path: Path) -> None:
    ua = by_regime.loc[by_regime["mechanism"].eq("uncertainty_aware")]
    lambdas = sorted(ua["lambda"].dropna().unique())
    gammas = sorted(ua["gamma"].dropna().unique())
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.8), sharex=True, sharey=True, constrained_layout=True)
    image = None
    for ax, regime in zip(axes, ("P", "R", "R_plus")):
        pivot = ua.loc[ua["regime"].eq(regime)].pivot(index="gamma", columns="lambda", values="outcome_change_rate").reindex(index=gammas, columns=lambdas)
        image = ax.imshow(pivot.to_numpy(dtype=float), vmin=0, vmax=1, cmap="viridis", aspect="auto", origin="lower")
        for row in range(len(gammas)):
            for col in range(len(lambdas)):
                value = pivot.iloc[row, col]
                ax.text(col, row, f"{value:.2f}" if pd.notna(value) else "", ha="center", va="center", color="white" if pd.notna(value) and value < 0.55 else "#222222", fontsize=7.5)
        ax.set_xticks(range(len(lambdas)), [f"{value:g}" for value in lambdas])
        ax.set_yticks(range(len(gammas)), [f"{value:g}" for value in gammas])
        ax.set_title(regime)
        ax.set_xlabel("lambda: expert weight")
    axes[0].set_ylabel("gamma: uncertainty penalty")
    if image is not None:
        fig.colorbar(image, ax=axes, label="Outcome-change rate", shrink=0.82)
    fig.suptitle("Uncertainty-aware mechanism sensitivity", fontsize=11)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def build_report(
    season_summary: pd.DataFrame,
    by_regime: pd.DataFrame,
    cases: pd.DataFrame,
    max_rankings: int,
) -> str:
    selected = selected_mechanisms(by_regime)
    lines = [
        "# Counterfactual Aggregation Mechanism Report",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Scenario construction",
        "",
        "- P uses pessimistic/lower, midpoint, and optimistic/upper coordinate scenarios. These coordinate vectors are sensitivity bounds and need not be jointly feasible polytope points.",
        f"- R/R_plus use a feasible-ranking medoid, feasible rankings with high/low alignment to the dynamic proxy, and up to {max_rankings} fixed-seed feasible-ranking draws per week. They are not converted to vote shares.",
        "- The stage-05 capped ranking detail is a fixed-seed reservoir sample from the evaluated feasible set.",
        "- Season rankings aggregate mechanism scores over each contestant's observed active weeks. They do not recursively create unobserved future performances after a counterfactual early elimination.",
        "",
        "## Selected regime-level results",
        "",
        "| Regime | Mechanism | Lambda | Gamma | Outcome change | Winner change | Finalist change | Mean rank shift |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for _, row in selected.sort_values(["regime", "mechanism"]).iterrows():
        lambda_text = "" if pd.isna(row["lambda"]) else f"{row['lambda']:.2f}"
        gamma_text = "" if pd.isna(row["gamma"]) else f"{row['gamma']:.2f}"
        outcome_text = "" if pd.isna(row["outcome_change_rate"]) else f"{row['outcome_change_rate']:.6f}"
        winner_text = "" if pd.isna(row["winner_change_rate"]) else f"{row['winner_change_rate']:.6f}"
        finalist_text = "" if pd.isna(row["finalist_set_change_rate"]) else f"{row['finalist_set_change_rate']:.6f}"
        shift_text = "" if pd.isna(row["average_rank_shift"]) else f"{row['average_rank_shift']:.6f}"
        lines.append(
            f"| {row['regime']} | {row['mechanism']} | {lambda_text} | {gamma_text} | {outcome_text} | {winner_text} | {finalist_text} | {shift_text} |"
        )
    lines.extend(
        [
            "",
            "## Mechanism boundaries",
            "",
            "Percentage aggregation is marked not applicable in R/R_plus because cardinal public shares are not identified there. The judge-save weak mechanism reports only whether the observed elimination remains inside the admissible bottom set. Winner, finalist, and unique rank outcomes are intentionally missing because the unobserved save decision does not identify them.",
            "",
            "For uncertainty-aware aggregation, higher scores are better and the lowest score is eliminated: `Score = lambda * judge_pct + (1-lambda) * PublicProxy - gamma * Uncertainty`.",
            "",
            "## Controversial cases",
            "",
            "The case table reports scenario ranges and probabilities of rank improvement or worsening. These are identified-set sensitivity calculations, not causal estimates of where a contestant would have placed under another real-world rule.",
            "",
            "## Limitations",
            "",
            "- P lower/midpoint/upper coordinate vectors do not preserve cross-coordinate polytope dependence.",
            "- Retained ordinal rankings approximate the feasible set when detail is capped or Monte Carlo sampled.",
            "- Season outcome summaries condition on observed active trajectories and available weekly scores.",
            "- Mechanism comparisons are descriptive design experiments and do not recover hidden votes.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    paths = {
        "dynamic": resolve(args.dynamic, root),
        "week": resolve(args.week_level, root),
        "r": resolve(args.feasible_r, root),
        "rplus": resolve(args.feasible_rplus, root),
        "audit": resolve(args.case_audit, root),
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        print(f"ERROR: Missing required input(s): {', '.join(missing)}", file=sys.stderr)
        return 2
    if args.max_ranking_samples < 0:
        print("ERROR: --max-ranking-samples must be nonnegative.", file=sys.stderr)
        return 2
    try:
        dynamic = pd.read_csv(paths["dynamic"])
        week_level = pd.read_csv(paths["week"])
        ranking_detail = pd.concat([pd.read_csv(paths["r"]), pd.read_csv(paths["rplus"])], ignore_index=True)
        audit = pd.read_csv(paths["audit"])
        scenarios, contestant_scenarios = simulate_counterfactuals(
            dynamic,
            week_level,
            ranking_detail,
            seed=args.seed,
            max_sampled_rankings=args.max_ranking_samples,
        )
        season_summary = summarize_counterfactuals(scenarios)
        by_regime = aggregate_counterfactuals_by_regime(season_summary)
        cases = controversial_case_results(audit, dynamic, contestant_scenarios)
        rate_columns = ["outcome_change_rate", "winner_change_rate", "finalist_set_change_rate"]
        for column in rate_columns:
            valid = pd.to_numeric(season_summary[column], errors="coerce").dropna()
            if not valid.between(0, 1).all():
                raise ValueError(f"{column} falls outside [0, 1].")
        tables = root / "outputs/tables"
        figures = root / "outputs/figures"
        logs = root / "outputs/logs"
        for directory in (tables, figures, logs):
            directory.mkdir(parents=True, exist_ok=True)
        options = dict(index=False, encoding="utf-8", na_rep="", lineterminator="\n", float_format="%.12g")
        season_summary.to_csv(tables / "counterfactual_results_by_season.csv", **options)
        by_regime.to_csv(tables / "counterfactual_results_by_regime.csv", **options)
        cases.to_csv(tables / "controversial_cases_counterfactual.csv", **options)
        plot_outcome_changes(by_regime, figures / "mechanism_outcome_changes.png")
        plot_case_results(cases, figures / "controversial_cases_counterfactual.png")
        plot_lambda_gamma(by_regime, figures / "lambda_gamma_sensitivity.png")
        (logs / "counterfactual_report.md").write_text(
            build_report(season_summary, by_regime, cases, args.max_ranking_samples),
            encoding="utf-8",
            newline="\n",
        )
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Counterfactual season rows: {len(season_summary)}")
    print(f"Counterfactual regime rows: {len(by_regime)}")
    print(f"Controversial-case rows: {len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
