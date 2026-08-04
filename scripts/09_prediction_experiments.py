#!/usr/bin/env python3
"""Run leakage-controlled elimination prediction validation."""

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

from src.prediction import (  # noqa: E402
    build_prediction_frame,
    calibration_table,
    run_prediction_validation,
    summarize_predictions,
)


FIGURE_DPI = 300
COLORS = {"accuracy": "#1F5A7A", "top2": "#2F6B4F", "logloss": "#C45A2A"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate whether partially identified preference features predict elimination."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--dynamic", type=Path, default=Path("data/processed/dynamic_public_appeal.csv")
    )
    parser.add_argument(
        "--week-level", type=Path, default=Path("data/processed/week_level.csv")
    )
    parser.add_argument("--seed", type=int, default=20260714)
    return parser.parse_args()


def plot_comparison(results: pd.DataFrame, path: Path) -> None:
    frame = results.loc[results["validation_scheme"].eq("forward_chaining")].copy()
    frame = frame.sort_values("log_loss", ascending=False)
    labels = frame["model"].str.replace("_", " ")
    y = np.arange(len(frame))
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 5.2), constrained_layout=True)
    axes[0].barh(y, frame["accuracy"], color=COLORS["accuracy"], alpha=0.82)
    axes[1].barh(y, frame["top2_accuracy"], color=COLORS["top2"], alpha=0.82)
    axes[2].barh(y, frame["log_loss"], color=COLORS["logloss"], alpha=0.82)
    for ax, title, limit in zip(axes, ("Top-1 accuracy", "Top-2 accuracy", "Log loss (lower is better)"), ((0, 1), (0, 1), None)):
        ax.set_title(title)
        ax.set_yticks(y, labels if ax is axes[0] else [])
        if limit:
            ax.set_xlim(*limit)
        ax.grid(axis="x", color="#D1D5DB", linewidth=0.6, alpha=0.7)
    fig.suptitle("Forward-chaining elimination prediction on history-complete events", fontsize=11)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def plot_calibration(calibration: pd.DataFrame, results: pd.DataFrame, path: Path) -> list[str]:
    forward = results.loc[results["validation_scheme"].eq("forward_chaining")].nsmallest(3, "log_loss")
    models = list(dict.fromkeys(["random_uniform", *forward["model"].tolist()]))[:4]
    data = calibration.loc[
        calibration["validation_scheme"].eq("forward_chaining")
        & calibration["model"].isin(models)
    ]
    palette = ["#6B7280", "#1F5A7A", "#C45A2A", "#2F6B4F"]
    markers = ["o", "D", "^", "s"]
    fig, ax = plt.subplots(figsize=(6.2, 5.0), constrained_layout=True)
    ax.plot([0, 0.6], [0, 0.6], color="#333333", linestyle="--", linewidth=1, label="Ideal")
    for model, color, marker in zip(models, palette, markers):
        frame = data.loc[data["model"].eq(model)].sort_values("mean_predicted_risk")
        ax.plot(frame["mean_predicted_risk"], frame["observed_elimination_rate"], marker=marker, color=color, linewidth=1.4, label=model.replace("_", " "))
    ax.set_xlabel("Mean predicted elimination risk")
    ax.set_ylabel("Observed elimination rate")
    ax.set_title("Forward-chaining calibration summary")
    ax.set_xlim(0, 0.6)
    ax.set_ylim(0, 0.6)
    ax.grid(color="#D1D5DB", linewidth=0.6, alpha=0.7)
    ax.legend(frameon=False, fontsize=7.5)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    return models


def build_report(
    frame: pd.DataFrame,
    results: pd.DataFrame,
    by_regime: pd.DataFrame,
    calibration_models: list[str],
) -> str:
    forward = results.loc[results["validation_scheme"].eq("forward_chaining")].sort_values("log_loss")
    best = forward.iloc[0]
    random = forward.loc[forward["model"].eq("random_uniform")].iloc[0]
    return "\n".join(
        [
            "# Elimination Prediction Validation Report",
            "",
            f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
            "",
            "## Leakage controls",
            "",
            "- The evaluation contains only non-finale weeks with exactly one observed elimination.",
            "- Every evaluated event is history-complete: all active contestants have an observation from a strictly earlier week.",
            "- Public appeal, dynamic appeal, uncertainty, and historical judge features are lagged by one contestant observation.",
            "- Current-week judge fields are used only by models whose names end in `same_week` and are flagged in the output.",
            "- Placement and finale outcomes are never used as predictors.",
            "",
            f"The modeling frame contains {int(frame['eligible_single_elimination'].sum())} contestant rows in eligible events; {int((frame['eligible_single_elimination'] & frame['history_complete_event']).sum())} rows remain in the common history-complete evaluation set.",
            "",
            "## Forward-chaining results",
            "",
            "| Model | Events | Accuracy | Top-2 accuracy | Brier | Log loss | Same-week baseline |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            *[
                f"| {row.model} | {int(row.n_events)} | {row.accuracy:.6f} | {row.top2_accuracy:.6f} | {row.brier_score:.6f} | {row.log_loss:.6f} | {row.same_week_baseline} |"
                for row in forward.itertuples(index=False)
            ],
            "",
            f"The lowest forward-chaining log loss is obtained by `{best.model}` ({best.log_loss:.6f}), compared with {random.log_loss:.6f} for uniform random risk. Model rankings vary across accuracy, top-2 accuracy, Brier score, and log loss.",
            "",
            "## Regime-specific caution",
            "",
            "Regime-specific rows are reported for both validation designs. R contains only two seasons, so forward-chaining R estimates rely on a very small historical training set and should be treated as unstable. Cross-regime differences are not evidence of recovered public votes.",
            "",
            "## Calibration",
            "",
            "The calibration figure displays: " + ", ".join(f"`{model}`" for model in calibration_models) + ". Bins with few contestant rows are descriptive only.",
            "",
            "## Interpretation",
            "",
            "Prediction performance is a validation experiment for whether partially identified preference features contain useful historical signal. It is not proof that true audience votes were recovered. The proxy, event selection, season split, and calibration choices remain model-dependent.",
            "",
        ]
    )


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    dynamic_path = args.dynamic if args.dynamic.is_absolute() else root / args.dynamic
    week_path = args.week_level if args.week_level.is_absolute() else root / args.week_level
    missing = [str(path) for path in (dynamic_path, week_path) if not path.is_file()]
    if missing:
        print(f"ERROR: Missing required input(s): {', '.join(missing)}", file=sys.stderr)
        return 2
    try:
        dynamic = pd.read_csv(dynamic_path)
        week_level = pd.read_csv(week_path)
        frame = build_prediction_frame(dynamic, week_level)
        predictions = run_prediction_validation(frame, seed=args.seed)
        results = summarize_predictions(predictions)
        by_regime = summarize_predictions(predictions, by_regime=True)
        calibration = calibration_table(predictions)
        tables = root / "outputs/tables"
        figures = root / "outputs/figures"
        logs = root / "outputs/logs"
        for directory in (tables, figures, logs):
            directory.mkdir(parents=True, exist_ok=True)
        options = dict(index=False, encoding="utf-8", na_rep="", lineterminator="\n", float_format="%.12g")
        results.to_csv(tables / "prediction_results.csv", **options)
        by_regime.to_csv(tables / "prediction_results_by_regime.csv", **options)
        calibration.to_csv(tables / "prediction_calibration.csv", **options)
        plot_comparison(results, figures / "prediction_comparison.png")
        calibration_models = plot_calibration(calibration, results, figures / "prediction_calibration.png")
        (logs / "prediction_report.md").write_text(
            build_report(frame, results, by_regime, calibration_models), encoding="utf-8", newline="\n"
        )
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    best = results.loc[results["validation_scheme"].eq("forward_chaining")].nsmallest(1, "log_loss").iloc[0]
    print(f"Prediction models: {results['model'].nunique()}")
    print(f"Best forward model by log loss: {best.model} ({best.log_loss:.6f})")
    print(f"Prediction report: {logs / 'prediction_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
