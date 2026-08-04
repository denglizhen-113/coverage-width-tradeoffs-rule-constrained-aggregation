#!/usr/bin/env python3
"""Compare expert evaluation and inferred public-appeal channels."""

from __future__ import annotations

import argparse
import json
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

from src.divergence_models import (  # noqa: E402
    build_divergence_table,
    fit_channel,
    prepare_divergence_data,
    try_mixedlm,
    winsorized_inverse_uncertainty,
)


FIGURE_DPI = 300
BLUE = "#1F5A7A"
ORANGE = "#C45A2A"
GREEN = "#2F6B4F"
GRAY = "#6B7280"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fit interpretable expert and latent-public channel models."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--features", type=Path, default=Path("data/processed/identification_features_long.csv")
    )
    return parser.parse_args()


def plot_coefficients(divergence: pd.DataFrame, path: Path) -> None:
    data = divergence.loc[~divergence["variable"].eq("intercept")].head(16).copy()
    data = data.sort_values("difference", key=lambda s: s.abs())
    y = np.arange(len(data))
    fig, ax = plt.subplots(figsize=(8.5, 6.0), constrained_layout=True)
    for position, row in enumerate(data.itertuples(index=False)):
        ax.plot([row.expert_coef, row.crowd_coef], [position, position], color="#D1D5DB", linewidth=1.2)
    ax.scatter(data["expert_coef"], y, color=BLUE, marker="o", s=34, label="Expert channel")
    ax.scatter(data["crowd_coef"], y, color=ORANGE, marker="D", s=30, label="Weighted public channel")
    ax.axvline(0, color="#333333", linewidth=0.8)
    labels = [value.replace("aggregation_regime_", "regime=").replace("industry_group_", "industry=").replace("partner_group_", "partner=").replace("season_category_", "season=") for value in data["variable"]]
    ax.set_yticks(y, labels)
    ax.set_xlabel("Standardized coefficient")
    ax.set_title("Largest descriptive expert-public coefficient differences")
    ax.grid(axis="x", color="#D1D5DB", linewidth=0.6, alpha=0.7)
    ax.legend(frameon=False, loc="lower right")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def plot_proxy_over_weeks(data: pd.DataFrame, path: Path) -> None:
    colors = {"P": BLUE, "R": ORANGE, "R_plus": GREEN}
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.7), sharey=True, constrained_layout=True)
    for ax, regime in zip(axes, ("P", "R", "R_plus")):
        frame = data.loc[data["aggregation_regime"].eq(regime)]
        grouped = frame.groupby("week")["public_appeal_proxy"]
        summary = grouped.agg(["mean", "count"]).reset_index()
        summary["q25"] = grouped.quantile(0.25).to_numpy()
        summary["q75"] = grouped.quantile(0.75).to_numpy()
        ax.fill_between(summary["week"], summary["q25"], summary["q75"], color=colors[regime], alpha=0.14)
        ax.plot(summary["week"], summary["mean"], color=colors[regime], marker="o", markersize=3.5, linewidth=1.6)
        ax.set_title(regime)
        ax.set_xlabel("Week")
        ax.set_ylim(0, 1)
        ax.grid(axis="y", color="#D1D5DB", linewidth=0.6, alpha=0.7)
    axes[0].set_ylabel("Mean inferred latent public-appeal proxy")
    fig.suptitle("Public-appeal proxy over competition weeks (mechanism-specific scales)", fontsize=11)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def report_text(
    divergence: pd.DataFrame,
    model_summaries: list[dict[str, object]],
    mixed_status: list[dict[str, object]],
    weight_info: dict[str, float],
) -> str:
    sign = divergence.loc[divergence["sign_divergence"] & ~divergence["variable"].eq("intercept")].head(10)
    primary = [item for item in model_summaries if item["model_type"] == "ridge_cv"]
    lines = [
        "# Expert-Crowd Divergence Report",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Design",
        "",
        "Expert and public channels are estimated on the same rows with available typed public-appeal proxies. Outcomes and numeric predictors are standardized. Models include age, returning status, week, active-field size, regime, season, industry, and the twenty most frequent partner categories.",
        "",
        "The primary comparison uses unweighted expert RidgeCV and uncertainty-weighted public RidgeCV. OLS and unweighted public RidgeCV are retained as sensitivity baselines.",
        "",
        "## Primary fit summaries",
        "",
        "| Target | Weighted | N | Features | R-squared | Ridge alpha |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in primary:
        lines.append(f"| {item['target']} | {item['weighted']} | {item['n_observations']} | {item['n_features']} | {item['r_squared']:.6f} | {item['selected_alpha']:.6g} |")
    lines.extend(
        [
            "",
            "## Uncertainty weights",
            "",
            f"Weights use `1/(uncertainty + {weight_info['epsilon']:.3f})`, winsorized at the empirical 5th and 95th percentiles and normalized to mean one. The final range is {weight_info['normalized_min']:.6f} to {weight_info['normalized_max']:.6f}.",
            "",
            "## Largest sign divergences",
            "",
            "| Variable | Expert coefficient | Public coefficient | Difference |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in sign.itertuples(index=False):
        lines.append(f"| {row.variable} | {row.expert_coef:.6f} | {row.crowd_coef:.6f} | {row.difference:.6f} |")
    if sign.empty:
        lines.append("| None above the numerical threshold |  |  |  |")
    lines.extend(["", "## Mixed-effects sensitivity", ""])
    for status in mixed_status:
        lines.append(f"- `{status['target']}`: success={status['success']}, converged={status['converged']}; {status['message']}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Coefficient differences describe how observed covariates align with expert shares versus mechanism-specific inferred public-appeal proxies. They are not causal effects and do not validate a recovered audience vote.",
            "",
            "Evidence for expert-crowd divergence is descriptive and model-dependent. High-cardinality fixed effects, proxy construction, wide identified sets, and unobserved confounding all limit substantive interpretation.",
            "",
            "Model summaries (machine-readable):",
            "",
            "```json",
            json.dumps(model_summaries, indent=2, default=str),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    features_path = args.features if args.features.is_absolute() else root / args.features
    if not features_path.is_file():
        print(f"ERROR: Missing input: {features_path}", file=sys.stderr)
        return 2
    try:
        features = pd.read_csv(features_path)
        data = prepare_divergence_data(features)
        weights, weight_info = winsorized_inverse_uncertainty(data["public_appeal_uncertainty"])
        expert_fits = [
            fit_channel(data, "judge_pct", model_type="ols"),
            fit_channel(data, "judge_pct", model_type="ridge_cv"),
        ]
        crowd_fits = [
            fit_channel(data, "public_appeal_proxy", model_type="ols"),
            fit_channel(data, "public_appeal_proxy", model_type="ridge_cv"),
            fit_channel(data, "public_appeal_proxy", model_type="ridge_cv", sample_weight=weights),
        ]
        expert_mixed, expert_status = try_mixedlm(data, "judge_pct")
        crowd_mixed, crowd_status = try_mixedlm(data, "public_appeal_proxy")
        expert_coefficients = pd.concat([fit.coefficients for fit in expert_fits] + ([expert_mixed] if not expert_mixed.empty else []), ignore_index=True)
        crowd_coefficients = pd.concat([fit.coefficients for fit in crowd_fits] + ([crowd_mixed] if not crowd_mixed.empty else []), ignore_index=True)
        divergence = build_divergence_table(expert_coefficients, crowd_coefficients)
        tables = root / "outputs/tables"
        figures = root / "outputs/figures"
        logs = root / "outputs/logs"
        for directory in (tables, figures, logs):
            directory.mkdir(parents=True, exist_ok=True)
        options = dict(index=False, encoding="utf-8", na_rep="", lineterminator="\n", float_format="%.12g")
        summaries = [fit.summary for fit in expert_fits + crowd_fits]
        expert_coefficients.to_csv(tables / "expert_channel_coefficients.csv", **options)
        crowd_coefficients.to_csv(tables / "crowd_channel_coefficients.csv", **options)
        divergence.to_csv(tables / "expert_crowd_divergence.csv", **options)
        pd.DataFrame(summaries).to_csv(tables / "divergence_model_summary.csv", **options)
        pd.DataFrame([expert_status, crowd_status]).to_csv(
            tables / "divergence_mixedlm_status.csv", **options
        )
        plot_coefficients(divergence, figures / "expert_vs_crowd_coefficients.png")
        plot_proxy_over_weeks(data, figures / "public_appeal_proxy_over_weeks.png")
        (logs / "expert_crowd_divergence_report.md").write_text(
            report_text(divergence, summaries, [expert_status, crowd_status], weight_info),
            encoding="utf-8",
            newline="\n",
        )
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Model rows: {len(data)}")
    print(f"Divergence coefficients: {len(divergence)}")
    print(f"MixedLM expert/crowd: {expert_status['success']}/{crowd_status['success']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
