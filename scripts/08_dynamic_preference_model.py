#!/usr/bin/env python3
"""Construct dynamic latent public-appeal proxy trajectories."""

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

from src.dynamic_preference import (  # noqa: E402
    build_dynamic_public_appeal,
    dynamic_summary,
)


FIGURE_DPI = 300
COLORS = {"raw": "#6B7280", "smooth": "#1F5A7A", "weighted": "#C45A2A"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smooth typed latent public-appeal proxies without treating them as votes."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--features",
        type=Path,
        default=Path("data/processed/identification_features_long.csv"),
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/processed/dynamic_public_appeal.csv")
    )
    parser.add_argument(
        "--summary", type=Path, default=Path("outputs/tables/dynamic_model_summary.csv")
    )
    parser.add_argument(
        "--figure", type=Path, default=Path("outputs/figures/dynamic_public_appeal_examples.png")
    )
    parser.add_argument(
        "--report", type=Path, default=Path("outputs/logs/dynamic_preference_report.md")
    )
    parser.add_argument("--alpha", type=float, default=0.5)
    return parser.parse_args()


def resolve(path: Path, root: Path) -> Path:
    return path if path.is_absolute() else root / path


def markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(v) for v in row) + " |" for row in rows)
    return "\n".join(lines)


def select_examples(dynamic: pd.DataFrame) -> pd.DataFrame:
    targets = [
        ("Jerry Rice", 2),
        ("Billy Ray Cyrus", 4),
        ("Bristol Palin", 11),
        ("Bobby Bones", 27),
    ]
    selected: list[tuple[int, str]] = []
    for name, season in targets:
        match = dynamic.loc[
            dynamic["season"].eq(season)
            & dynamic["contestant_name"].astype(str).str.casefold().eq(name.casefold())
        ]
        if not match.empty:
            selected.append((season, str(match.iloc[0]["contestant_id"])))
    rplus = dynamic.loc[dynamic["aggregation_regime"].eq("R_plus")]
    if not rplus.empty:
        longest = (
            rplus.groupby(["season", "contestant_id"], as_index=False)
            .size()
            .sort_values(["size", "season", "contestant_id"], ascending=[False, True, True])
            .iloc[0]
        )
        selected.append((int(longest.season), str(longest.contestant_id)))
    mask = pd.Series(False, index=dynamic.index)
    for season, contestant_id in selected:
        mask |= dynamic["season"].eq(season) & dynamic["contestant_id"].astype(str).eq(
            contestant_id
        )
    return dynamic.loc[mask].copy()


def plot_examples(dynamic: pd.DataFrame, path: Path) -> list[str]:
    examples = select_examples(dynamic)
    groups = list(examples.groupby(["season", "contestant_id"], sort=False))
    if not groups:
        raise ValueError("No dynamic examples are available for plotting.")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )
    ncols = 3
    nrows = int(np.ceil(len(groups) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(12.0, 3.5 * nrows), sharey=True, constrained_layout=True)
    axes_array = np.atleast_1d(axes).ravel()
    labels: list[str] = []
    for ax, ((season, _), frame) in zip(axes_array, groups):
        frame = frame.sort_values("week")
        name = str(frame.iloc[0]["contestant_name"])
        regime = str(frame.iloc[0]["aggregation_regime"])
        labels.append(f"{name} (S{season}, {regime})")
        lower = np.clip(
            frame["raw_public_appeal_proxy"] - frame["public_appeal_uncertainty"] / 2,
            0,
            1,
        )
        upper = np.clip(
            frame["raw_public_appeal_proxy"] + frame["public_appeal_uncertainty"] / 2,
            0,
            1,
        )
        ax.fill_between(frame["week"], lower, upper, color=COLORS["raw"], alpha=0.12)
        ax.plot(frame["week"], frame["raw_public_appeal_proxy"], "o--", color=COLORS["raw"], linewidth=1, markersize=3.5, label="Raw proxy")
        ax.plot(frame["week"], frame["smoothed_public_appeal_alpha_05"], color=COLORS["smooth"], linewidth=1.6, label="Exponential, alpha=0.5")
        ax.plot(frame["week"], frame["dynamic_public_appeal"], color=COLORS["weighted"], linewidth=1.8, label="Uncertainty-weighted")
        ax.set_title(f"{name} | Season {season} | {regime}", loc="left")
        ax.set_xlabel("Week")
        ax.set_ylim(0, 1)
        ax.grid(axis="y", color="#D1D5DB", linewidth=0.6, alpha=0.7)
    for ax in axes_array[len(groups):]:
        ax.remove()
    for ax in axes_array[: len(groups)]:
        ax.set_ylabel("Inferred latent public appeal proxy")
    axes_array[0].legend(frameon=False, ncol=3, loc="lower left", bbox_to_anchor=(0.0, 1.13))
    fig.suptitle("Dynamic public-appeal proxies (not observed audience votes)", fontsize=12)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    return labels


def build_report(summary: pd.DataFrame, labels: list[str], alpha: float) -> str:
    return "\n".join(
        [
            "# Dynamic Latent Public-Appeal Proxy Report",
            "",
            f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
            "",
            "## Specification",
            "",
            f"The primary exponential smoother uses `alpha={alpha:.2f}`. Sensitivity columns use alpha 0.30 and 0.70. The uncertainty-weighted update uses `effective_alpha = alpha / (1 + uncertainty)`, so less-identified observations move the state less.",
            "",
            "A missing raw proxy does not create a new measurement. If a prior state exists it is carried forward and `dynamic_observation_used=False`; the raw field remains missing.",
            "",
            "## Summary",
            "",
            markdown_table(
                ["Regime", "Rows", "Observed", "Carried", "Contestant-seasons", "Mean raw", "Mean dynamic", "Mean abs change", "Alpha span"],
                (
                    (
                        row.regime,
                        int(row.rows),
                        int(row.observed_proxy_rows),
                        int(row.carried_forward_rows),
                        int(row.contestant_seasons),
                        f"{row.mean_raw_proxy:.6f}",
                        f"{row.mean_dynamic_proxy:.6f}",
                        f"{row.mean_absolute_smoothing_change:.6f}",
                        f"{row.mean_alpha_sensitivity_span:.6f}",
                    )
                    for row in summary.itertuples(index=False)
                ),
            ),
            "",
            "## Figure cases",
            "",
            *[f"- {label}" for label in labels],
            "",
            "## Interpretation",
            "",
            "These trajectories are smoothed versions of mechanism-specific, partially identified proxies. They do not recover true public votes. Cross-regime comparisons require regime controls because cardinal interval midpoints and ordinal rank scores have different measurement meanings.",
            "",
        ]
    )


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    features_path = resolve(args.features, root)
    if not features_path.is_file():
        print(f"ERROR: Missing input: {features_path}", file=sys.stderr)
        print("Run scripts/06_build_identification_features.py first.", file=sys.stderr)
        return 2
    if not 0 < args.alpha <= 1:
        print("ERROR: --alpha must lie in (0, 1].", file=sys.stderr)
        return 2
    output_path = resolve(args.output, root)
    summary_path = resolve(args.summary, root)
    figure_path = resolve(args.figure, root)
    report_path = resolve(args.report, root)
    try:
        features = pd.read_csv(features_path)
        dynamic = build_dynamic_public_appeal(features, alpha=args.alpha)
        summary = dynamic_summary(dynamic)
        labels = plot_examples(dynamic, figure_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        dynamic.to_csv(output_path, index=False, encoding="utf-8", na_rep="", lineterminator="\n", float_format="%.12g")
        summary.to_csv(summary_path, index=False, encoding="utf-8", na_rep="", lineterminator="\n", float_format="%.12g")
        report_path.write_text(build_report(summary, labels, args.alpha), encoding="utf-8", newline="\n")
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"dynamic_public_appeal.csv: {len(dynamic)} rows")
    print(f"Summary: {summary_path}")
    print(f"Figure: {figure_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
