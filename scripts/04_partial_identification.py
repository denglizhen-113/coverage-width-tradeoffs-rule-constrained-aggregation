#!/usr/bin/env python3
"""Compute sharp LP preference bounds and P-regime uncertainty figures."""

from __future__ import annotations

import argparse
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

from src.constraints import load_constraint_set, solve_preference_bounds  # noqa: E402


FIGURE_DPI = 300
BLUE = "#1F5A7A"
ORANGE = "#C45A2A"
GRAY = "#6B7280"
LIGHT_GRAY = "#D1D5DB"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Solve coordinate-wise LP bounds for all percentage-regime weeks."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--panel", type=Path, default=Path("data/processed/panel_long.csv")
    )
    parser.add_argument(
        "--constraint-summary",
        type=Path,
        default=Path("outputs/tables/constraint_summary.csv"),
    )
    parser.add_argument(
        "--bounds-output",
        type=Path,
        default=Path("data/processed/preference_bounds_regime_p.csv"),
    )
    parser.add_argument(
        "--uncertainty-output",
        type=Path,
        default=Path("outputs/tables/uncertainty_by_week_regime_p.csv"),
    )
    parser.add_argument(
        "--figures-dir", type=Path, default=Path("outputs/figures")
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("outputs/logs/partial_identification_report.md"),
    )
    return parser.parse_args()


def resolve(path: Path, root: Path) -> Path:
    return path if path.is_absolute() else root / path


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
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
    output.extend("| " + " | ".join(clean(value) for value in row) + " |" for row in rows)
    return "\n".join(output)


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
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "legend.fontsize": 8.5,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def plot_uncertainty_over_weeks(data: pd.DataFrame, figures_dir: Path) -> None:
    apply_plot_style()
    valid = data.loc[data["feasible"] & data["mean_width"].notna()].copy()
    grouped = valid.groupby("week")["mean_width"]
    trend = grouped.agg(["mean", "count"]).reset_index()
    trend["q25"] = grouped.quantile(0.25).to_numpy()
    trend["q75"] = grouped.quantile(0.75).to_numpy()
    fig, ax = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    ax.scatter(
        valid["week"],
        valid["mean_width"],
        s=18,
        color=GRAY,
        alpha=0.30,
        linewidths=0,
        label="Season-week",
    )
    finale = valid.loc[valid["finale_week"]]
    ax.scatter(
        finale["week"],
        finale["mean_width"],
        s=30,
        marker="^",
        color=ORANGE,
        alpha=0.80,
        linewidths=0,
        label="Finale",
    )
    ax.fill_between(
        trend["week"], trend["q25"], trend["q75"], color=BLUE, alpha=0.12
    )
    ax.plot(
        trend["week"],
        trend["mean"],
        color=BLUE,
        marker="o",
        markersize=4,
        linewidth=1.8,
        label="Cross-season mean",
    )
    ax.set_title("Mean identification width by competition week")
    ax.set_xlabel("Week")
    ax.set_ylabel("Mean interval width")
    ax.set_xticks(sorted(valid["week"].unique()))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color=LIGHT_GRAY, linewidth=0.6, alpha=0.7)
    ax.legend(frameon=False, ncol=3, loc="lower center")
    for name in ("uncertainty_over_weeks_regime_p.png", "uncertainty_over_weeks.png"):
        fig.savefig(figures_dir / name, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def plot_uncertainty_by_active_count(data: pd.DataFrame, figures_dir: Path) -> None:
    apply_plot_style()
    valid = data.loc[data["feasible"] & data["mean_width"].notna()].copy()
    trend = (
        valid.groupby("n_active")["mean_width"]
        .agg(["mean", "median", "count"])
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(7.0, 4.5), constrained_layout=True)
    ax.scatter(
        valid["n_active"],
        valid["mean_width"],
        s=18,
        color=GRAY,
        alpha=0.30,
        linewidths=0,
        label="Season-week",
    )
    ax.plot(
        trend["n_active"],
        trend["mean"],
        color=BLUE,
        marker="o",
        markersize=4,
        linewidth=1.8,
        label="Mean by active field size",
    )
    ax.set_title("Identification width and active field size")
    ax.set_xlabel("Active contestants")
    ax.set_ylabel("Mean interval width")
    ax.set_xticks(sorted(valid["n_active"].unique()))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color=LIGHT_GRAY, linewidth=0.6, alpha=0.7)
    ax.legend(frameon=False, loc="lower right")
    fig.savefig(
        figures_dir / "uncertainty_by_active_count_regime_p.png",
        dpi=FIGURE_DPI,
        bbox_inches="tight",
    )
    plt.close(fig)


def select_example_weeks(uncertainty: pd.DataFrame) -> list[tuple[int, int]]:
    valid = uncertainty.loc[
        uncertainty["feasible"]
        & uncertainty["mean_width"].notna()
        & uncertainty["n_constraints"].gt(0)
    ].copy()
    valid["season_max_week"] = valid.groupby("season")["week"].transform("max")
    valid["progress"] = valid["week"] / valid["season_max_week"]
    chosen: list[tuple[int, int]] = []

    early = valid.loc[(valid["progress"] <= 0.35) & ~valid["finale_week"]].sort_values(
        ["n_active", "n_constraints", "season", "week"],
        ascending=[False, False, True, True],
    )
    if not early.empty:
        chosen.append((int(early.iloc[0]["season"]), int(early.iloc[0]["week"])))

    mid = valid.loc[~valid["finale_week"]].copy()
    if chosen:
        mid = mid.loc[
            ~(
                mid["season"].eq(chosen[0][0])
                & mid["week"].eq(chosen[0][1])
            )
        ]
    mid["mid_distance"] = (mid["progress"] - 0.55).abs()
    mid = mid.sort_values(
        ["mid_distance", "n_constraints", "season", "week"],
        ascending=[True, False, True, True],
    )
    if not mid.empty:
        chosen.append((int(mid.iloc[0]["season"]), int(mid.iloc[0]["week"])))

    late = valid.loc[valid["finale_week"]].sort_values(
        ["n_constraints", "season", "week"], ascending=[False, True, True]
    )
    if not late.empty:
        chosen.append((int(late.iloc[0]["season"]), int(late.iloc[0]["week"])))

    if len(chosen) < 3:
        for row in valid.sort_values(
            ["n_constraints", "n_active", "season", "week"],
            ascending=[False, True, True, True],
        ).itertuples(index=False):
            key = (int(row.season), int(row.week))
            if key not in chosen:
                chosen.append(key)
            if len(chosen) == 3:
                break
    return chosen[:3]


def plot_example_intervals(
    bounds: pd.DataFrame, uncertainty: pd.DataFrame, figures_dir: Path
) -> list[tuple[int, int]]:
    apply_plot_style()
    selected = select_example_weeks(uncertainty)
    fig, axes = plt.subplots(
        len(selected), 1, figsize=(8.0, 12.5), sharex=True, constrained_layout=True
    )
    axes = np.atleast_1d(axes)
    for ax, (season, week) in zip(axes, selected):
        frame = bounds.loc[
            bounds["season"].eq(season) & bounds["week"].eq(week)
        ].copy()
        frame = frame.sort_values(
            ["lower_bound", "upper_bound", "contestant_name"],
            ascending=[False, False, True],
        ).reset_index(drop=True)
        y = np.arange(len(frame))
        colors = np.where(frame["eliminated_this_week"], ORANGE, BLUE)
        for position, row in enumerate(frame.itertuples(index=False)):
            ax.hlines(
                position,
                row.lower_bound,
                row.upper_bound,
                color=colors[position],
                linewidth=2.0,
            )
            ax.plot(row.midpoint, position, "o", color=colors[position], markersize=4)
        labels = [
            f"{name} *" if eliminated else name
            for name, eliminated in zip(
                frame["contestant_name"], frame["eliminated_this_week"]
            )
        ]
        summary = uncertainty.loc[
            uncertainty["season"].eq(season) & uncertainty["week"].eq(week)
        ].iloc[0]
        ax.set_yticks(y, labels=labels)
        ax.invert_yaxis()
        ax.set_xlim(0, 1)
        ax.set_title(
            f"Season {season}, week {week}: {int(summary.n_active)} active, "
            f"{int(summary.n_constraints)} inequalities",
            loc="left",
        )
        ax.grid(axis="x", color=LIGHT_GRAY, linewidth=0.6, alpha=0.7)
    axes[-1].set_xlabel("Feasible public preference share")
    fig.suptitle(
        "Representative partially identified preference intervals "
        "(* observed elimination)",
        fontsize=12,
    )
    fig.savefig(
        figures_dir / "identified_intervals_example_weeks.png",
        dpi=FIGURE_DPI,
        bbox_inches="tight",
    )
    plt.close(fig)
    return selected


def build_report(
    bounds: pd.DataFrame,
    uncertainty: pd.DataFrame,
    selected: list[tuple[int, int]],
) -> str:
    feasible = uncertainty.loc[uncertainty["feasible"]]
    infeasible = uncertainty.loc[~uncertainty["feasible"]]
    lines = [
        "# Partial Identification Report: Percentage Aggregation",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Scope and estimand",
        "",
        "This stage computes sharp coordinate-wise linear-programming bounds for public preference shares that are consistent with the observed P-regime outcome constraints. The output is a feasible preference region and uncertainty intervals, not an estimate or recovery of true audience votes.",
        "",
        "## Coverage",
        "",
        markdown_table(
            ["Metric", "Count"],
            [
                ("P season-weeks evaluated", len(uncertainty)),
                ("Feasible P season-weeks", len(feasible)),
                ("Infeasible or skipped P season-weeks", len(infeasible)),
                ("Contestant-week bound rows", len(bounds)),
                ("Coordinate-wise LPs solved", int(2 * feasible["n_active"].sum())),
            ],
        ),
        "",
        "For each active contestant i, one LP minimizes `F_i` and a second LP maximizes `F_i` over the same week-specific polytope. The reported interval is therefore sharp for that coordinate under the encoded constraints. Coordinate-wise midpoints are descriptive summaries and need not form a jointly feasible vector when assembled across contestants.",
        "",
        "## Identification width",
        "",
        markdown_table(
            ["Statistic", "Value"],
            [
                ("Mean season-week width", f"{feasible['mean_width'].mean():.6f}"),
                ("Median season-week width", f"{feasible['mean_width'].median():.6f}"),
                ("Minimum season-week mean width", f"{feasible['mean_width'].min():.6f}"),
                ("Maximum season-week mean width", f"{feasible['mean_width'].max():.6f}"),
                ("Mean finalist-week width", f"{feasible.loc[feasible['finale_week'], 'mean_width'].mean():.6f}"),
                ("Mean non-finale width", f"{feasible.loc[~feasible['finale_week'], 'mean_width'].mean():.6f}"),
            ],
        ),
        "",
        "No-elimination and withdrawal-only weeks contain only the simplex and consequently provide weak or no outcome-specific identification. Multiple-elimination weeks use conservative eliminated-versus-survivor inequalities. Finale weeks use complete active-finalist placement ordering when available.",
        "",
        "## Representative interval panels",
        "",
        markdown_table(
            ["Role", "Season", "Week"],
            [
                ("Early", selected[0][0], selected[0][1]),
                ("Middle", selected[1][0], selected[1][1]),
                ("Finale/late", selected[2][0], selected[2][1]),
            ],
        ),
        "",
        "The examples are selected deterministically from feasible P weeks: a large early field with outcome constraints, a week near the middle of a season, and a finale with the largest available ranking-constraint set.",
        "",
        "## Limitations",
        "",
        "- Intervals condition on the aggregation rule, active set, expert-score normalization, and observed elimination/placement interpretation.",
        "- They quantify set identification from elimination-only feedback; they are not sampling confidence intervals.",
        "- No stochastic posterior or hit-and-run sampling is used in this stage.",
        "- R and R_plus regimes remain outside this LP analysis until validated ordinal and judge-save implementations are available.",
        "",
        "## Generated artifacts",
        "",
        "- `data/processed/preference_bounds_regime_p.csv`",
        "- `outputs/tables/uncertainty_by_week_regime_p.csv`",
        "- `outputs/figures/uncertainty_over_weeks_regime_p.png`",
        "- `outputs/figures/uncertainty_by_active_count_regime_p.png`",
        "- `outputs/figures/identified_intervals_example_weeks.png`",
        "- `outputs/logs/partial_identification_report.md`",
        "",
    ]
    if not infeasible.empty:
        lines.extend(
            [
                "## Infeasible or skipped weeks",
                "",
                markdown_table(
                    ["Season", "Week", "Reason"],
                    infeasible[["season", "week", "skip_reason"]].itertuples(
                        index=False, name=None
                    ),
                ),
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    panel_path = resolve(args.panel, root)
    summary_path = resolve(args.constraint_summary, root)
    bounds_path = resolve(args.bounds_output, root)
    uncertainty_path = resolve(args.uncertainty_output, root)
    figures_dir = resolve(args.figures_dir, root)
    report_path = resolve(args.report, root)
    missing = [str(path) for path in (panel_path, summary_path) if not path.is_file()]
    if missing:
        print(f"ERROR: Missing required input(s): {', '.join(missing)}", file=sys.stderr)
        print("Run scripts/03_build_constraints.py first.", file=sys.stderr)
        return 2

    try:
        panel = pd.read_csv(panel_path)
        summary = pd.read_csv(summary_path)
        p_summary = summary.loc[summary["regime"].eq("P")].sort_values(
            ["season", "week"]
        )
        bound_rows: list[dict[str, Any]] = []
        uncertainty_rows: list[dict[str, Any]] = []
        for row in p_summary.itertuples(index=False):
            season = int(row.season)
            week = int(row.week)
            active = panel.loc[
                panel["season"].eq(season)
                & panel["week"].eq(week)
                & panel["active_status"].map(as_bool)
            ].sort_values("contestant_id", kind="stable")
            skipped = as_bool(row.skipped)
            feasible = False
            lower = np.full(len(active), np.nan)
            upper = np.full(len(active), np.nan)
            message = str(row.skip_reason) if skipped else ""
            if not skipped:
                model_path = root / str(row.model_path)
                constraints = load_constraint_set(model_path)
                if tuple(active["contestant_id"].astype(str)) != constraints.variable_ids:
                    raise ValueError(
                        f"Variable order mismatch for season {season}, week {week}."
                    )
                solved = solve_preference_bounds(
                    constraints.A_ub,
                    constraints.b_ub,
                    constraints.A_eq,
                    constraints.b_eq,
                    constraints.bounds,
                )
                feasible = solved.feasible
                lower = solved.lower_bounds
                upper = solved.upper_bounds
                message = solved.message

            widths = upper - lower
            for position, contestant in enumerate(active.itertuples(index=False)):
                bound_rows.append(
                    {
                        "season": season,
                        "week": week,
                        "contestant_id": contestant.contestant_id,
                        "contestant_name": contestant.contestant_name,
                        "judge_total": contestant.judge_total,
                        "judge_pct": contestant.judge_pct,
                        "eliminated_this_week": as_bool(
                            contestant.eliminated_this_week
                        ),
                        "withdrew_this_week": as_bool(contestant.withdrew_this_week),
                        "placement": contestant.placement,
                        "lower_bound": lower[position],
                        "upper_bound": upper[position],
                        "interval_width": widths[position],
                        "midpoint": (lower[position] + upper[position]) / 2,
                        "feasible": feasible,
                        "regime": "P",
                    }
                )
            eliminated_widths = [
                widths[position]
                for position, contestant in enumerate(active.itertuples(index=False))
                if as_bool(contestant.eliminated_this_week)
                and np.isfinite(widths[position])
            ]
            finite_widths = widths[np.isfinite(widths)]
            uncertainty_rows.append(
                {
                    "season": season,
                    "week": week,
                    "n_active": len(active),
                    "n_constraints": int(row.n_inequalities),
                    "mean_width": (
                        float(np.mean(finite_widths)) if finite_widths.size else np.nan
                    ),
                    "median_width": (
                        float(np.median(finite_widths)) if finite_widths.size else np.nan
                    ),
                    "max_width": (
                        float(np.max(finite_widths)) if finite_widths.size else np.nan
                    ),
                    "min_width": (
                        float(np.min(finite_widths)) if finite_widths.size else np.nan
                    ),
                    "eliminated_width": (
                        float(np.mean(eliminated_widths))
                        if eliminated_widths
                        else np.nan
                    ),
                    "finale_week": as_bool(row.finale_week),
                    "double_elimination_week": as_bool(
                        row.double_elimination_week
                    ),
                    "constraint_type": row.constraint_type,
                    "feasible": feasible,
                    "skipped": skipped,
                    "skip_reason": message if not feasible else "",
                }
            )

        bounds = pd.DataFrame(bound_rows)
        uncertainty = pd.DataFrame(uncertainty_rows)
        bounds_path.parent.mkdir(parents=True, exist_ok=True)
        uncertainty_path.parent.mkdir(parents=True, exist_ok=True)
        figures_dir.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        csv_options = {
            "index": False,
            "encoding": "utf-8",
            "na_rep": "",
            "lineterminator": "\n",
            "float_format": "%.12g",
        }
        bounds.to_csv(bounds_path, **csv_options)
        uncertainty.to_csv(uncertainty_path, **csv_options)
        uncertainty.to_csv(
            root / "outputs/tables/uncertainty_by_week.csv", **csv_options
        )
        plot_uncertainty_over_weeks(uncertainty, figures_dir)
        plot_uncertainty_by_active_count(uncertainty, figures_dir)
        selected = plot_example_intervals(bounds, uncertainty, figures_dir)
        report_path.write_text(
            build_report(bounds, uncertainty, selected),
            encoding="utf-8",
            newline="\n",
        )
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"preference_bounds_regime_p.csv: {len(bounds)} contestant-weeks")
    print(
        f"uncertainty_by_week_regime_p.csv: {len(uncertainty)} weeks, "
        f"{int(uncertainty['feasible'].sum())} feasible"
    )
    print(f"Figures: {figures_dir}")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
