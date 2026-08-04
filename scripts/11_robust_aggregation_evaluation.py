#!/usr/bin/env python3
"""Evaluate uncertainty-aware aggregation trade-offs and Pareto points."""

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

from src.robust_aggregation import (  # noqa: E402
    build_robust_aggregation_results,
    frontier_points,
)


FIGURE_DPI = 300


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate expert alignment, crowd responsiveness, robustness, and stability."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--counterfactual",
        type=Path,
        default=Path("outputs/tables/counterfactual_results_by_season.csv"),
    )
    return parser.parse_args()


def plot_frontier(results: pd.DataFrame, frontier: pd.DataFrame, path: Path) -> None:
    data = results.loc[results["regime"].eq("ALL")]
    sizes = 45 + 180 * data["robustness"]
    fig, ax = plt.subplots(figsize=(7.0, 5.2), constrained_layout=True)
    scatter = ax.scatter(
        data["expert_merit_alignment"],
        data["crowd_responsiveness"],
        s=sizes,
        c=data["gamma"],
        cmap="viridis",
        alpha=0.68,
        edgecolors=np.where(data["pareto_frontier_all_regimes"], "#222222", "none"),
        linewidths=np.where(data["pareto_frontier_all_regimes"], 1.2, 0.0),
    )
    ordered = frontier.sort_values("expert_merit_alignment")
    ax.plot(ordered["expert_merit_alignment"], ordered["crowd_responsiveness"], color="#333333", linewidth=1, linestyle="--")
    offsets = {
        0.25: (-42, 12),
        0.5: (-28, -20),
        0.75: (8, 10),
        1.0: (8, -12),
    }
    for row in frontier.rename(columns={"lambda": "lambda_value"}).itertuples(index=False):
        ax.annotate(
            f"lambda={row.lambda_value:.2g}, gamma={row.gamma:.2g}",
            (row.expert_merit_alignment, row.crowd_responsiveness),
            xytext=offsets.get(round(row.lambda_value, 2), (5, 5)),
            textcoords="offset points",
            fontsize=7,
        )
    ax.set_xlabel("Expert merit alignment (scaled Spearman)")
    ax.set_ylabel("Crowd responsiveness (scaled Spearman)")
    ax.set_title("Uncertainty-aware aggregation trade-off frontier")
    ax.set_xlim(0.15, 1.04)
    ax.set_ylim(0.05, 0.96)
    ax.grid(color="#D1D5DB", linewidth=0.6, alpha=0.7)
    fig.colorbar(scatter, ax=ax, label="Uncertainty penalty gamma")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def plot_robustness_stability(results: pd.DataFrame, path: Path) -> None:
    data = results.loc[results["regime"].eq("ALL")]
    colors = ["#1F5A7A", "#C45A2A", "#2F6B4F", "#7C3E66", "#6B7280"]
    markers = ["o", "D", "^", "s", "P"]
    fig, ax = plt.subplots(figsize=(7.0, 5.0), constrained_layout=True)
    for (lambda_value, group), color, marker in zip(data.groupby("lambda", sort=True), colors, markers):
        group = group.sort_values("gamma")
        ax.plot(group["robustness"], group["stability"], color=color, marker=marker, linewidth=1.5, label=f"lambda={lambda_value:g}")
    ax.set_xlabel("Robustness to identified-set perturbations")
    ax.set_ylabel("Winner/finalist stability")
    ax.set_title("Robustness-stability trade-off across parameter grid")
    ax.set_xlim(max(0.0, data["robustness"].min() - 0.03), 1.01)
    ax.set_ylim(0, min(1.0, data["stability"].max() + 0.08))
    ax.grid(color="#D1D5DB", linewidth=0.6, alpha=0.7)
    ax.legend(frameon=False, ncol=2, fontsize=8)
    ax.text(
        0.02,
        0.04,
        "Within each line, gamma increases from 0 to 1.",
        transform=ax.transAxes,
        color="#555555",
        fontsize=8,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def build_report(results: pd.DataFrame, frontier: pd.DataFrame) -> str:
    best = results.loc[results["regime"].eq("ALL")].nlargest(1, "tradeoff_harmonic_mean").iloc[0]
    lines = [
        "# Robust Aggregation Evaluation Report",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Evaluation dimensions",
        "",
        "1. Expert merit alignment is the season-level Spearman association between counterfactual final rank and mean judge share, scaled from [-1,1] to [0,1].",
        "2. Crowd responsiveness uses the analogous association with dynamic latent public appeal.",
        "3. Robustness is one minus scenario rank-shift dispersion normalized by season field size.",
        "4. Stability averages winner and finalist-set stability across identified-set scenarios.",
        "",
        "## All-regime Pareto frontier",
        "",
        "| Lambda | Gamma | Expert alignment | Crowd responsiveness | Robustness | Stability |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in frontier.rename(columns={"lambda": "lambda_value"}).itertuples(index=False):
        lines.append(f"| {row.lambda_value:.2f} | {row.gamma:.2f} | {row.expert_merit_alignment:.6f} | {row.crowd_responsiveness:.6f} | {row.robustness:.6f} | {row.stability:.6f} |")
    lines.extend(
        [
            "",
            f"The largest descriptive harmonic mean occurs at lambda={best['lambda']:.2f}, gamma={best['gamma']:.2f}. This scalar summary is not a welfare theorem and does not supersede the Pareto set.",
            "",
            "## Interpretation",
            "",
            "The proposed mechanism does not claim to recover hidden votes; instead, it uses identification uncertainty as a design input.",
            "",
            "Results condition on proxy construction, observed active trajectories, scenario sampling, and the chosen robustness normalization. They support a transparent trade-off analysis, not a universally optimal aggregation rule.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    input_path = args.counterfactual if args.counterfactual.is_absolute() else root / args.counterfactual
    if not input_path.is_file():
        print(f"ERROR: Missing input: {input_path}", file=sys.stderr)
        return 2
    try:
        season_summary = pd.read_csv(input_path)
        results = build_robust_aggregation_results(season_summary)
        frontier = frontier_points(results)
        if frontier.empty:
            raise ValueError("Pareto frontier is empty.")
        tables = root / "outputs/tables"
        figures = root / "outputs/figures"
        logs = root / "outputs/logs"
        for directory in (tables, figures, logs):
            directory.mkdir(parents=True, exist_ok=True)
        options = dict(index=False, encoding="utf-8", na_rep="", lineterminator="\n", float_format="%.12g")
        results.to_csv(tables / "robust_aggregation_results.csv", **options)
        frontier.to_csv(tables / "pareto_frontier_points.csv", **options)
        plot_frontier(results, frontier, figures / "pareto_frontier.png")
        plot_robustness_stability(results, figures / "robustness_stability_tradeoff.png")
        (logs / "robust_aggregation_report.md").write_text(
            build_report(results, frontier), encoding="utf-8", newline="\n"
        )
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Robust aggregation grid rows: {len(results)}")
    print(f"Pareto frontier points: {len(frontier)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
