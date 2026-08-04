"""Run the preregistered Stage 26X-1 multiseed sensitivity experiment."""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib
import numpy as np
import pandas as pd
from pypdf import PdfReader

matplotlib.use("Agg")
from matplotlib import pyplot as plt

from src.dss_common import generate_percentage_case
from src.external_testbed import (
    PRIMARY_TIE_POLICY,
    TIE_SENSITIVITY_POLICIES,
    _case as generate_external_case,
    _round_metrics,
)
from src.synthetic_benchmark import evaluate_case


SEEDS = tuple(20260716 + 1000 * index for index in range(20))
INTERNAL_GRID = tuple(
    (n_active, noise_probability)
    for n_active in (4, 5, 6)
    for noise_probability in (0.00, 0.05, 0.10, 0.20)
)
EXTERNAL_GRID = ((6, 3), (7, 3), (7, 4))
INTERNAL_REPLICATIONS = 250
EXTERNAL_REPLICATIONS = 120
PREREGISTERED_DESIGN = Path("outputs/stage26X-1/PREREGISTERED_DESIGN.md")
PREREGISTERED_DESIGN_SHA256 = "e437a81b80143b2f03c81b005d463cc489185d7f781214e8446d1e111784257b"
INTERNAL_METHODS = (
    "rule_aware_partial_identification",
    "rule_agnostic_partial_identification",
    "naive_point_estimation",
    "full_disclosure_oracle_synthetic_only",
)
EXTERNAL_METHODS = (
    "rule_aware_discretion",
    "direct_rule_misspecification",
    "rule_agnostic_ordinal",
)
INTERNAL_SUMMARY_METRICS = (
    "coverage_rate",
    "average_feasible_set_width",
    "false_certainty_rate",
    "baseline_error",
    "outcome_consistency_rate",
    "feasible_rate",
)
EXTERNAL_SUMMARY_METRICS = (
    "coverage_rate",
    "average_feasible_set_width",
    "false_certainty_rate",
    "rule_robustness_index",
    "disclosure_uncertainty_reduction",
    "recommendation_stability",
)
INTERNAL_RAW_COLUMNS = {
    "synthesizer",
    "seed",
    "n_active",
    "outcome_noise_probability",
    "replication",
    "observed_outcome_noise",
    "method",
    "coverage",
    "width",
    "false_certainty",
    "baseline_error",
    "outcome_consistent",
    "feasible",
}
EXTERNAL_RAW_COLUMNS = {
    "synthesizer",
    "seed",
    "n_candidates",
    "n_rounds",
    "replication",
    "method",
    "coverage",
    "width",
    "false_certainty",
    "rule_robustness_index",
    "disclosure_uncertainty_reduction",
    "recommendation_stability",
}
STAGE_DIR = Path("outputs/stage26X-1")
RAW_DIR = STAGE_DIR / "raw"
TABLE_DIR = STAGE_DIR / "tables"
TABLE4_PATH = TABLE_DIR / "Table4_multiseed.csv"
TABLE5_PATH = TABLE_DIR / "Table5_multiseed.csv"
ASSESSMENT_PATH = STAGE_DIR / "ROBUSTNESS_ASSESSMENT.md"
FIGURE6_PNG = STAGE_DIR / "Figure_06_multiseed_internal_sensitivity.png"
FIGURE6_PDF = STAGE_DIR / "Figure_06_multiseed_internal_sensitivity.pdf"
FIGURE7_PNG = STAGE_DIR / "Figure_07_multiseed_external_sensitivity.png"
FIGURE7_PDF = STAGE_DIR / "Figure_07_multiseed_external_sensitivity.pdf"
BASELINE_MANUSCRIPT = Path("outputs/stage26W/DSS_submission_draft_STAGE26W_source.md")
BASELINE_MANUSCRIPT_SHA256 = "6f1fc33fcd93e099b0ecf85f3f129e94b4aa00be80a42e8dd162bc3d2db45b76"


def internal_raw_filename(seed: int, n_active: int, noise_probability: float) -> str:
    return f"internal_seed-{seed}_n-{n_active}_noise-{noise_probability:.2f}.csv"


def external_raw_filename(seed: int, n_candidates: int, n_rounds: int) -> str:
    return f"external_seed-{seed}_candidates-{n_candidates}_rounds-{n_rounds}.csv"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_preregistered_design(root: Path) -> str:
    observed = file_sha256(root / PREREGISTERED_DESIGN)
    if observed != PREREGISTERED_DESIGN_SHA256:
        raise RuntimeError(
            "Preregistered design hash mismatch: "
            f"expected {PREREGISTERED_DESIGN_SHA256}, observed {observed}."
        )
    return observed


def run_internal_cell(
    *,
    seed: int,
    n_active: int,
    noise_probability: float,
    n_replications: int,
) -> pd.DataFrame:
    """Return replication-level records for one locked internal cell."""
    if n_replications < 1:
        raise ValueError("n_replications must be positive.")
    rng = np.random.default_rng(seed + int(round(float(noise_probability) * 1_000)))
    records: list[dict[str, object]] = []
    for replication in range(n_replications):
        case = generate_percentage_case(
            rng,
            n_active=n_active,
            outcome_noise_probability=float(noise_probability),
        )
        for result in evaluate_case(case):
            if result["method"] not in INTERNAL_METHODS:
                continue
            row = dict(result)
            row["width"] = row.pop("mean_width")
            records.append(
                {
                    "synthesizer": "internal_percentage",
                    "seed": seed,
                    "n_active": n_active,
                    "outcome_noise_probability": float(noise_probability),
                    "replication": replication,
                    "observed_outcome_noise": case.observed_outcome_noise,
                    **row,
                }
            )
    return pd.DataFrame.from_records(records)


def run_external_cell(
    *,
    seed: int,
    n_candidates: int,
    n_rounds: int,
    n_replications: int,
) -> pd.DataFrame:
    """Return replication-level records for one locked external cell."""
    if n_replications < 1:
        raise ValueError("n_replications must be positive.")
    rng = np.random.default_rng(seed)
    records: list[dict[str, object]] = []
    for replication in range(n_replications):
        case = generate_external_case(rng, n_candidates=n_candidates, n_rounds=n_rounds)
        for method in EXTERNAL_METHODS:
            policy_case_coverage: list[float] = []
            policy_recommendations: list[str] = []
            primary_metrics: list[dict[str, object]] | None = None
            for policy in TIE_SENSITIVITY_POLICIES:
                round_metrics = [
                    _round_metrics(method, round_input, truth, intervention, policy)
                    for round_input, truth, intervention in zip(
                        case.rounds,
                        case.public_ranks,
                        case.intervention_rounds,
                    )
                ]
                policy_case_coverage.append(
                    float(all(bool(item["truth_covered"]) for item in round_metrics))
                )
                mean_width = float(np.nanmean([float(item["width"]) for item in round_metrics]))
                policy_recommendations.append(
                    "add_pairwise_public_disclosure"
                    if mean_width >= 0.67
                    else "retain_current_disclosure_with_audit"
                )
                if policy == PRIMARY_TIE_POLICY:
                    primary_metrics = round_metrics
            if primary_metrics is None:
                raise RuntimeError(f"Primary tie policy {PRIMARY_TIE_POLICY!r} was not evaluated.")
            covered = float(all(bool(item["truth_covered"]) for item in primary_metrics))
            feasible = bool(all(bool(item["feasible"]) for item in primary_metrics))
            modal_recommendation = max(
                set(policy_recommendations),
                key=policy_recommendations.count,
            )
            records.append(
                {
                    "synthesizer": "external_ordinal",
                    "seed": seed,
                    "n_candidates": n_candidates,
                    "n_rounds": n_rounds,
                    "replication": replication,
                    "method": method,
                    "coverage": covered,
                    "width": float(np.nanmean([float(item["width"]) for item in primary_metrics])),
                    "false_certainty": float(feasible and not covered),
                    "rule_robustness_index": float(np.mean(policy_case_coverage)),
                    "disclosure_uncertainty_reduction": float(
                        np.nanmean(
                            [float(item["disclosure_reduction"]) for item in primary_metrics]
                        )
                    ),
                    "recommendation_stability": float(
                        np.mean(
                            [
                                item == modal_recommendation
                                for item in policy_recommendations
                            ]
                        )
                    ),
                }
            )
    return pd.DataFrame.from_records(records)


def summarize_across_seeds(
    seed_level: pd.DataFrame,
    *,
    group_columns: list[str],
    metric_columns: list[str],
) -> pd.DataFrame:
    """Summarize seed-level estimates without treating replications as independent."""
    records: list[dict[str, object]] = []
    grouper: str | list[str] = group_columns[0] if len(group_columns) == 1 else group_columns
    for key, group in seed_level.groupby(grouper, sort=True, dropna=False):
        keys = (key,) if len(group_columns) == 1 else tuple(key)
        row: dict[str, object] = dict(zip(group_columns, keys))
        replication_counts = group["n_replications"].astype(int)
        unique_counts = replication_counts.unique()
        row["n_seeds"] = int(group["seed"].nunique())
        row["replications_per_seed"] = (
            int(unique_counts[0]) if len(unique_counts) == 1 else "varies"
        )
        row["total_replications"] = int(replication_counts.sum())
        for metric in metric_columns:
            values = pd.to_numeric(group[metric], errors="coerce").dropna()
            row[f"{metric}_mean"] = float(values.mean())
            row[f"{metric}_median"] = float(values.median())
            row[f"{metric}_std"] = float(values.std(ddof=1))
            row[f"{metric}_q025"] = float(values.quantile(0.025, interpolation="linear"))
            row[f"{metric}_q975"] = float(values.quantile(0.975, interpolation="linear"))
        records.append(row)
    return pd.DataFrame.from_records(records)


def aggregate_internal_seed(raw: pd.DataFrame) -> pd.DataFrame:
    """Aggregate replication records within each internal seed and cell."""
    return (
        raw.groupby(
            [
                "synthesizer",
                "seed",
                "n_active",
                "outcome_noise_probability",
                "method",
            ],
            as_index=False,
            sort=True,
        )
        .agg(
            n_replications=("replication", "nunique"),
            coverage_rate=("coverage", "mean"),
            average_feasible_set_width=("width", "mean"),
            false_certainty_rate=("false_certainty", "mean"),
            baseline_error=("baseline_error", "mean"),
            outcome_consistency_rate=("outcome_consistent", "mean"),
            feasible_rate=("feasible", "mean"),
        )
    )


def aggregate_external_seed(raw: pd.DataFrame) -> pd.DataFrame:
    """Aggregate replication records within each external seed and cell."""
    return (
        raw.groupby(
            [
                "synthesizer",
                "seed",
                "n_candidates",
                "n_rounds",
                "method",
            ],
            as_index=False,
            sort=True,
        )
        .agg(
            n_replications=("replication", "nunique"),
            coverage_rate=("coverage", "mean"),
            average_feasible_set_width=("width", "mean"),
            false_certainty_rate=("false_certainty", "mean"),
            rule_robustness_index=("rule_robustness_index", "mean"),
            disclosure_uncertainty_reduction=(
                "disclosure_uncertainty_reduction",
                "mean",
            ),
            recommendation_stability=("recommendation_stability", "mean"),
        )
    )


def atomic_write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.stem}.tmp{path.suffix}")
    frame.to_csv(temporary, index=False, float_format="%.15g", lineterminator="\n")
    temporary.replace(path)


def atomic_write_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.stem}.tmp{path.suffix}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _validate_raw_frame(
    frame: pd.DataFrame,
    *,
    path: Path,
    expected_columns: set[str],
    expected_methods: tuple[str, ...],
    expected_replications: int,
) -> None:
    missing = expected_columns - set(frame.columns)
    if missing:
        raise RuntimeError(f"Raw file {path} is missing columns: {sorted(missing)}")
    expected_rows = expected_replications * len(expected_methods)
    if len(frame) != expected_rows:
        raise RuntimeError(
            f"Raw file {path} has {len(frame)} rows; expected {expected_rows}."
        )
    observed_methods = set(frame["method"].astype(str))
    if observed_methods != set(expected_methods):
        raise RuntimeError(
            f"Raw file {path} methods {sorted(observed_methods)} do not match "
            f"{sorted(expected_methods)}."
        )
    replications = sorted(pd.to_numeric(frame["replication"], errors="raise").astype(int).unique())
    if replications != list(range(expected_replications)):
        raise RuntimeError(f"Raw file {path} has incomplete replication identifiers.")


def validate_internal_raw(path: Path, *, seed: int, n_active: int, noise: float) -> pd.DataFrame:
    frame = pd.read_csv(path)
    _validate_raw_frame(
        frame,
        path=path,
        expected_columns=INTERNAL_RAW_COLUMNS,
        expected_methods=INTERNAL_METHODS,
        expected_replications=INTERNAL_REPLICATIONS,
    )
    if not frame["seed"].eq(seed).all() or not frame["n_active"].eq(n_active).all():
        raise RuntimeError(f"Raw file {path} does not match its seed/candidate cell.")
    if not np.allclose(frame["outcome_noise_probability"], noise, atol=0.0, rtol=0.0):
        raise RuntimeError(f"Raw file {path} does not match its noise cell.")
    if "prediction_only_judge_proxy" in set(frame["method"].astype(str)):
        raise RuntimeError(f"Deleted alias remains in raw file {path}.")
    return frame


def validate_external_raw(
    path: Path,
    *,
    seed: int,
    n_candidates: int,
    n_rounds: int,
) -> pd.DataFrame:
    frame = pd.read_csv(path)
    _validate_raw_frame(
        frame,
        path=path,
        expected_columns=EXTERNAL_RAW_COLUMNS,
        expected_methods=EXTERNAL_METHODS,
        expected_replications=EXTERNAL_REPLICATIONS,
    )
    if (
        not frame["seed"].eq(seed).all()
        or not frame["n_candidates"].eq(n_candidates).all()
        or not frame["n_rounds"].eq(n_rounds).all()
    ):
        raise RuntimeError(f"Raw file {path} does not match its registered external cell.")
    return frame


def execute_registered_cells(root: Path) -> tuple[int, int]:
    """Run every missing registered cell sequentially and validate resumed cells."""
    raw_dir = root / RAW_DIR
    raw_dir.mkdir(parents=True, exist_ok=True)
    completed = 0
    reused = 0
    total = len(SEEDS) * (len(INTERNAL_GRID) + len(EXTERNAL_GRID))
    for seed in SEEDS:
        for n_active, noise in INTERNAL_GRID:
            path = raw_dir / internal_raw_filename(seed, n_active, noise)
            if path.exists():
                validate_internal_raw(path, seed=seed, n_active=n_active, noise=noise)
                reused += 1
            else:
                frame = run_internal_cell(
                    seed=seed,
                    n_active=n_active,
                    noise_probability=noise,
                    n_replications=INTERNAL_REPLICATIONS,
                )
                atomic_write_csv(frame, path)
                validate_internal_raw(path, seed=seed, n_active=n_active, noise=noise)
                completed += 1
            print(
                f"[{completed + reused:03d}/{total}] internal seed={seed} "
                f"n_active={n_active} noise={noise:.2f}",
                flush=True,
            )
        for n_candidates, n_rounds in EXTERNAL_GRID:
            path = raw_dir / external_raw_filename(seed, n_candidates, n_rounds)
            if path.exists():
                validate_external_raw(
                    path,
                    seed=seed,
                    n_candidates=n_candidates,
                    n_rounds=n_rounds,
                )
                reused += 1
            else:
                frame = run_external_cell(
                    seed=seed,
                    n_candidates=n_candidates,
                    n_rounds=n_rounds,
                    n_replications=EXTERNAL_REPLICATIONS,
                )
                atomic_write_csv(frame, path)
                validate_external_raw(
                    path,
                    seed=seed,
                    n_candidates=n_candidates,
                    n_rounds=n_rounds,
                )
                completed += 1
            print(
                f"[{completed + reused:03d}/{total}] external seed={seed} "
                f"candidates={n_candidates} rounds={n_rounds}",
                flush=True,
            )
    expected_names = {
        internal_raw_filename(seed, n_active, noise)
        for seed in SEEDS
        for n_active, noise in INTERNAL_GRID
    } | {
        external_raw_filename(seed, n_candidates, n_rounds)
        for seed in SEEDS
        for n_candidates, n_rounds in EXTERNAL_GRID
    }
    observed_names = {path.name for path in raw_dir.glob("*.csv")}
    if observed_names != expected_names:
        raise RuntimeError(
            "Raw directory does not exactly match the preregistered 300-file set: "
            f"missing={sorted(expected_names - observed_names)}, "
            f"unexpected={sorted(observed_names - expected_names)}"
        )
    return completed, reused


def load_seed_level_results(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    internal_parts: list[pd.DataFrame] = []
    external_parts: list[pd.DataFrame] = []
    for seed in SEEDS:
        for n_active, noise in INTERNAL_GRID:
            path = root / RAW_DIR / internal_raw_filename(seed, n_active, noise)
            internal_parts.append(
                aggregate_internal_seed(
                    validate_internal_raw(path, seed=seed, n_active=n_active, noise=noise)
                )
            )
        for n_candidates, n_rounds in EXTERNAL_GRID:
            path = root / RAW_DIR / external_raw_filename(seed, n_candidates, n_rounds)
            external_parts.append(
                aggregate_external_seed(
                    validate_external_raw(
                        path,
                        seed=seed,
                        n_candidates=n_candidates,
                        n_rounds=n_rounds,
                    )
                )
            )
    internal = pd.concat(internal_parts, ignore_index=True)
    external = pd.concat(external_parts, ignore_index=True)
    return internal, external


def create_summary_tables(
    root: Path,
    internal_seed: pd.DataFrame,
    external_seed: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    table4 = summarize_across_seeds(
        internal_seed,
        group_columns=[
            "synthesizer",
            "n_active",
            "outcome_noise_probability",
            "method",
        ],
        metric_columns=list(INTERNAL_SUMMARY_METRICS),
    )
    table5 = summarize_across_seeds(
        external_seed,
        group_columns=[
            "synthesizer",
            "n_candidates",
            "n_rounds",
            "method",
        ],
        metric_columns=list(EXTERNAL_SUMMARY_METRICS),
    )
    atomic_write_csv(table4, root / TABLE4_PATH)
    atomic_write_csv(table5, root / TABLE5_PATH)
    return table4, table5


def _configure_figure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "Times New Roman",
            "font.size": 9,
            "axes.titlesize": 10.5,
            "axes.labelsize": 9.5,
            "legend.fontsize": 8,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _save_figure(fig: Any, png_path: Path, pdf_path: Path) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    temp_png = png_path.with_name(f"{png_path.stem}.tmp.png")
    temp_pdf = pdf_path.with_name(f"{pdf_path.stem}.tmp.pdf")
    fig.savefig(temp_png, dpi=300, bbox_inches="tight", pad_inches=0.12, facecolor="white")
    fig.savefig(temp_pdf, bbox_inches="tight", pad_inches=0.12, facecolor="white")
    temp_png.replace(png_path)
    temp_pdf.replace(pdf_path)
    plt.close(fig)


def _metric_interval(table: pd.DataFrame, metric: str) -> tuple[np.ndarray, np.ndarray]:
    mean = table[f"{metric}_mean"].to_numpy(dtype=float)
    lower = table[f"{metric}_q025"].to_numpy(dtype=float)
    upper = table[f"{metric}_q975"].to_numpy(dtype=float)
    return mean, np.vstack((np.maximum(0.0, mean - lower), np.maximum(0.0, upper - mean)))


def plot_figure6(table4: pd.DataFrame, png_path: Path, pdf_path: Path) -> None:
    _configure_figure_style()
    methods = (
        "naive_point_estimation",
        "rule_agnostic_partial_identification",
        "rule_aware_partial_identification",
    )
    labels = {
        "naive_point_estimation": "Point proxy",
        "rule_agnostic_partial_identification": "Rule-agnostic set",
        "rule_aware_partial_identification": "Rule-aware set",
    }
    coverage_colors = ("#7CB69A", "#4B8D6B", "#2F6B4F")
    width_colors = ("#7FA8BF", "#477D9B", "#1F5A7A")
    markers = ("o", "s", "D")
    fig, axes = plt.subplots(2, 3, figsize=(12.0, 7.0), sharex=True, sharey="row")
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.13, top=0.82, hspace=0.18, wspace=0.16)
    for column, n_active in enumerate((4, 5, 6)):
        for method_index, method in enumerate(methods):
            selected = table4.loc[
                table4["n_active"].eq(n_active) & table4["method"].eq(method)
            ].sort_values("outcome_noise_probability")
            x = 100.0 * selected["outcome_noise_probability"].to_numpy(dtype=float)
            coverage, coverage_error = _metric_interval(selected, "coverage_rate")
            width, width_error = _metric_interval(selected, "average_feasible_set_width")
            axes[0, column].errorbar(
                x,
                coverage,
                yerr=coverage_error,
                color=coverage_colors[method_index],
                marker=markers[method_index],
                linewidth=1.4,
                capsize=2.5,
                label=labels[method],
            )
            axes[1, column].errorbar(
                x,
                width,
                yerr=width_error,
                color=width_colors[method_index],
                marker=markers[method_index],
                linewidth=1.4,
                capsize=2.5,
                label=labels[method],
            )
        axes[0, column].set_title(f"{n_active} active candidates")
        axes[1, column].set_xlabel("Outcome-noise probability (%)")
        axes[1, column].set_xticks((0, 5, 10, 20))
        for row in (0, 1):
            axes[row, column].set_ylim(-0.04, 1.08)
            axes[row, column].grid(axis="y", color="#E4E7EC", linewidth=0.7)
    axes[0, 0].set_ylabel("Known-truth coverage")
    axes[1, 0].set_ylabel("Normalized feasible-set width")
    handles, legend_labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="upper center", bbox_to_anchor=(0.5, 0.91), ncol=3)
    fig.suptitle("Internal synthetic sensitivity across 20 seeds", y=0.975, fontsize=12.5, weight="bold")
    fig.text(
        0.5,
        0.035,
        "Points are seed-level means; bars show empirical 2.5%-97.5% intervals across seeds.",
        ha="center",
        fontsize=8.3,
        color="#667085",
    )
    _save_figure(fig, png_path, pdf_path)


def plot_figure7(table5: pd.DataFrame, png_path: Path, pdf_path: Path) -> None:
    _configure_figure_style()
    methods = EXTERNAL_METHODS
    method_labels = ("Rule-aware\ndiscretion", "Direct-rule\nmisspecification", "Rule-agnostic\nordinal")
    cells = ((6, 3), (7, 3), (7, 4))
    cell_labels = ("6 candidates / 3 rounds", "7 candidates / 3 rounds", "7 candidates / 4 rounds")
    coverage_colors = ("#7CB69A", "#4B8D6B", "#2F6B4F")
    width_colors = ("#7FA8BF", "#477D9B", "#1F5A7A")
    markers = ("o", "s", "D")
    x = np.arange(len(methods), dtype=float)
    offsets = (-0.18, 0.0, 0.18)
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 5.1), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.23, top=0.76, wspace=0.24)
    for cell_index, ((n_candidates, n_rounds), cell_label) in enumerate(zip(cells, cell_labels)):
        selected = (
            table5.loc[
                table5["n_candidates"].eq(n_candidates) & table5["n_rounds"].eq(n_rounds)
            ]
            .set_index("method")
            .loc[list(methods)]
            .reset_index()
        )
        coverage, coverage_error = _metric_interval(selected, "coverage_rate")
        width, width_error = _metric_interval(selected, "average_feasible_set_width")
        axes[0].errorbar(
            x + offsets[cell_index],
            coverage,
            yerr=coverage_error,
            color=coverage_colors[cell_index],
            marker=markers[cell_index],
            linestyle="none",
            capsize=3,
            label=cell_label,
        )
        axes[1].errorbar(
            x + offsets[cell_index],
            width,
            yerr=width_error,
            color=width_colors[cell_index],
            marker=markers[cell_index],
            linestyle="none",
            capsize=3,
            label=cell_label,
        )
    axes[0].set_title("Known-truth coverage")
    axes[1].set_title("Normalized feasible-rank width")
    axes[0].set_ylabel("Seed-level rate")
    axes[1].set_ylabel("Seed-level mean width")
    for axis in axes:
        axis.set_ylim(-0.04, 1.08)
        axis.set_xticks(x, method_labels)
        axis.grid(axis="y", color="#E4E7EC", linewidth=0.7)
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="upper center", bbox_to_anchor=(0.5, 0.89), ncol=3)
    fig.suptitle("External synthetic sensitivity across 20 seeds", y=0.98, fontsize=12.5, weight="bold")
    fig.text(
        0.5,
        0.035,
        "Points are seed-level means; bars show empirical 2.5%-97.5% intervals across seeds.",
        ha="center",
        fontsize=8.3,
        color="#667085",
    )
    _save_figure(fig, png_path, pdf_path)


def embedded_pdf_fonts(path: Path) -> list[str]:
    """Return embedded BaseFont names, raising if any referenced font is unembedded."""
    reader = PdfReader(path)
    embedded: set[str] = set()
    unembedded: set[str] = set()
    for page in reader.pages:
        resources = page.get("/Resources", {}).get_object()
        fonts = resources.get("/Font", {}).get_object()
        for reference in fonts.values():
            font = reference.get_object()
            candidates = [font]
            if "/DescendantFonts" in font:
                candidates.extend(item.get_object() for item in font["/DescendantFonts"])
            for candidate in candidates:
                base_font = str(candidate.get("/BaseFont", font.get("/BaseFont", "UNKNOWN")))
                descriptor_reference = candidate.get("/FontDescriptor")
                if descriptor_reference is None:
                    continue
                descriptor = descriptor_reference.get_object()
                if any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                    embedded.add(base_font)
                else:
                    unembedded.add(base_font)
    if unembedded:
        raise RuntimeError(f"PDF {path} contains unembedded fonts: {sorted(unembedded)}")
    if not embedded:
        raise RuntimeError(f"PDF {path} contains no verifiably embedded font files.")
    return sorted(embedded)


def _paired_results(
    frame: pd.DataFrame,
    *,
    index: list[str],
    aware: str,
    comparator: str,
) -> pd.DataFrame:
    selected = frame.loc[frame["method"].isin((aware, comparator))]
    width = selected.pivot(index=index, columns="method", values="average_feasible_set_width")
    coverage = selected.pivot(index=index, columns="method", values="coverage_rate")
    paired = pd.DataFrame(index=width.index)
    paired["aware_width"] = width[aware]
    paired["comparator_width"] = width[comparator]
    paired["aware_coverage"] = coverage[aware]
    paired["comparator_coverage"] = coverage[comparator]
    paired["width_lower"] = paired["aware_width"] < paired["comparator_width"]
    paired["coverage_lower"] = paired["aware_coverage"] < paired["comparator_coverage"]
    paired["coverage_decline"] = paired["comparator_coverage"] - paired["aware_coverage"]
    return paired.reset_index()


def _position_rows(
    frame: pd.DataFrame,
    *,
    filters: dict[str, int | float],
    methods: tuple[str, ...],
    metrics: tuple[str, ...],
    label: str,
) -> list[dict[str, object]]:
    selected = frame.copy()
    for column, value in filters.items():
        selected = selected.loc[selected[column].eq(value)]
    rows: list[dict[str, object]] = []
    for method in methods:
        method_rows = selected.loc[selected["method"].eq(method)]
        for metric in metrics:
            values = method_rows.set_index("seed")[metric].astype(float)
            original = float(values.loc[SEEDS[0]])
            percentile = float(values.rank(method="average", pct=True).loc[SEEDS[0]])
            ties = int((values.to_numpy() == original).sum())
            rows.append(
                {
                    "cell": label,
                    "method": method,
                    "metric": metric,
                    "original_seed_value": original,
                    "percentile_rank": percentile,
                    "classification": "tail" if percentile <= 0.10 or percentile >= 0.90 else "non-tail",
                    "exact_ties": ties,
                }
            )
    return rows


def _reproduction_checks(
    root: Path,
    internal_seed: pd.DataFrame,
    external_seed: pd.DataFrame,
) -> pd.DataFrame:
    historical_internal = pd.read_csv(root / "outputs/tables/synthetic_coverage_results.csv")
    historical_external = pd.read_csv(root / "outputs/tables/external_testbed_results.csv")
    checks: list[dict[str, object]] = []
    original_internal = internal_seed.loc[
        internal_seed["seed"].eq(SEEDS[0]) & internal_seed["n_active"].eq(5)
    ]
    for noise, historical_condition in ((0.0, "rule_consistent"), (0.1, "outcome_noise_stress_test")):
        for method in INTERNAL_METHODS:
            current = original_internal.loc[
                original_internal["outcome_noise_probability"].eq(noise)
                & original_internal["method"].eq(method)
            ].iloc[0]
            historical = historical_internal.loc[
                historical_internal["condition"].eq(historical_condition)
                & historical_internal["method"].eq(method)
            ].iloc[0]
            for metric in (
                "coverage_rate",
                "average_feasible_set_width",
                "false_certainty_rate",
                "baseline_error",
                "outcome_consistency_rate",
                "feasible_rate",
            ):
                current_value = float(current[metric])
                historical_value = float(historical[metric])
                matches = bool(
                    (np.isnan(current_value) and np.isnan(historical_value))
                    or np.isclose(current_value, historical_value, atol=1e-12, rtol=0.0)
                )
                checks.append(
                    {
                        "cell": f"internal n=5 noise={noise:.2f}",
                        "method": method,
                        "metric": metric,
                        "current": current_value,
                        "historical": historical_value,
                        "matches": matches,
                    }
                )
    original_external = external_seed.loc[
        external_seed["seed"].eq(SEEDS[0])
        & external_seed["n_candidates"].eq(7)
        & external_seed["n_rounds"].eq(4)
    ]
    for method in EXTERNAL_METHODS:
        current = original_external.loc[original_external["method"].eq(method)].iloc[0]
        historical = historical_external.loc[historical_external["method"].eq(method)].iloc[0]
        for metric in EXTERNAL_SUMMARY_METRICS:
            current_value = float(current[metric])
            historical_value = float(historical[metric])
            checks.append(
                {
                    "cell": "external candidates=7 rounds=4",
                    "method": method,
                    "metric": metric,
                    "current": current_value,
                    "historical": historical_value,
                    "matches": bool(np.isclose(current_value, historical_value, atol=1e-12, rtol=0.0)),
                }
            )
    return pd.DataFrame.from_records(checks)


def create_robustness_assessment(
    root: Path,
    internal_seed: pd.DataFrame,
    external_seed: pd.DataFrame,
    *,
    figure6_fonts: list[str],
    figure7_fonts: list[str],
) -> str:
    internal_pairs = _paired_results(
        internal_seed,
        index=["seed", "n_active", "outcome_noise_probability"],
        aware="rule_aware_partial_identification",
        comparator="rule_agnostic_partial_identification",
    )
    external_pairs = _paired_results(
        external_seed,
        index=["seed", "n_candidates", "n_rounds"],
        aware="rule_aware_discretion",
        comparator="rule_agnostic_ordinal",
    )
    internal_region = (
        internal_pairs.groupby(["n_active", "outcome_noise_probability"], as_index=False)
        .agg(
            paired_seeds=("seed", "nunique"),
            width_lower_count=("width_lower", "sum"),
            width_lower_proportion=("width_lower", "mean"),
            coverage_lower_count=("coverage_lower", "sum"),
            coverage_lower_proportion=("coverage_lower", "mean"),
            aware_width_mean=("aware_width", "mean"),
            comparator_width_mean=("comparator_width", "mean"),
        )
    )
    external_region = (
        external_pairs.groupby(["n_candidates", "n_rounds"], as_index=False)
        .agg(
            paired_seeds=("seed", "nunique"),
            width_lower_count=("width_lower", "sum"),
            width_lower_proportion=("width_lower", "mean"),
            coverage_lower_count=("coverage_lower", "sum"),
            coverage_lower_proportion=("coverage_lower", "mean"),
            aware_width_mean=("aware_width", "mean"),
            comparator_width_mean=("comparator_width", "mean"),
        )
    )
    width_lower_count = int(internal_pairs["width_lower"].sum() + external_pairs["width_lower"].sum())
    paired_count = len(internal_pairs) + len(external_pairs)
    width_lower_proportion = width_lower_count / paired_count
    clean = internal_pairs.loc[internal_pairs["outcome_noise_probability"].eq(0.0)]
    noisy = internal_pairs.loc[internal_pairs["outcome_noise_probability"].gt(0.0)]
    declines = noisy["coverage_decline"].astype(float)
    decline_stats = {
        "mean": float(declines.mean()),
        "median": float(declines.median()),
        "std": float(declines.std(ddof=1)),
        "q025": float(declines.quantile(0.025, interpolation="linear")),
        "q975": float(declines.quantile(0.975, interpolation="linear")),
    }
    internal_reversals = internal_region.loc[
        (internal_region["aware_width_mean"] > internal_region["comparator_width_mean"])
        | (internal_region["width_lower_proportion"] < 0.5)
    ]
    external_reversals = external_region.loc[
        (external_region["aware_width_mean"] > external_region["comparator_width_mean"])
        | (external_region["width_lower_proportion"] < 0.5)
    ]
    majority_region_failures = len(internal_reversals) + len(external_reversals)
    clean_coverage_lower = int(clean["coverage_lower"].sum())
    region_count = len(internal_region) + len(external_region)
    direction_region_successes = int(
        (internal_region["width_lower_proportion"] >= 0.5).sum()
        + (external_region["width_lower_proportion"] >= 0.5).sum()
    )
    if (
        width_lower_proportion >= 0.95
        and majority_region_failures == 0
        and clean_coverage_lower == 0
    ):
        ruling = "CONCLUSIONS_ROBUST_ACROSS_SEEDS"
    elif width_lower_proportion >= 0.5 and direction_region_successes > 0:
        ruling = "CONCLUSIONS_PARTIALLY_ROBUST"
    else:
        ruling = "CONCLUSIONS_NOT_ROBUST"
    position_rows: list[dict[str, object]] = []
    for noise in (0.0, 0.1):
        position_rows.extend(
            _position_rows(
                internal_seed,
                filters={"n_active": 5, "outcome_noise_probability": noise},
                methods=(
                    "rule_aware_partial_identification",
                    "rule_agnostic_partial_identification",
                ),
                metrics=("coverage_rate", "average_feasible_set_width"),
                label=f"internal n=5 noise={noise:.2f}",
            )
        )
    position_rows.extend(
        _position_rows(
            external_seed,
            filters={"n_candidates": 7, "n_rounds": 4},
            methods=("rule_aware_discretion", "rule_agnostic_ordinal"),
            metrics=("coverage_rate", "average_feasible_set_width"),
            label="external candidates=7 rounds=4",
        )
    )
    positions = pd.DataFrame.from_records(position_rows)
    reproduction = _reproduction_checks(root, internal_seed, external_seed)
    reproduction_pass = bool(reproduction["matches"].all())
    if not reproduction_pass:
        failures = reproduction.loc[~reproduction["matches"]]
        raise RuntimeError(
            "Original-seed reproduction failed:\n" + failures.to_string(index=False)
        )
    original_hash = file_sha256(root / BASELINE_MANUSCRIPT)
    if original_hash != BASELINE_MANUSCRIPT_SHA256:
        raise RuntimeError(
            f"Stage 26W manuscript hash changed: expected {BASELINE_MANUSCRIPT_SHA256}, "
            f"observed {original_hash}."
        )
    lines = [
        "# Stage 26X-1 Robustness Assessment",
        "",
        "## Execution and evidence scope",
        "",
        f"- Preregistered design SHA256: `{verify_preregistered_design(root)}`.",
        f"- Seeds: `{len(SEEDS)}`; internal raw cells: `{len(SEEDS) * len(INTERNAL_GRID)}`; external raw cells: `{len(SEEDS) * len(EXTERNAL_GRID)}`.",
        f"- Internal simulated cases: `{len(SEEDS) * len(INTERNAL_GRID) * INTERNAL_REPLICATIONS}`; external simulated cases: `{len(SEEDS) * len(EXTERNAL_GRID) * EXTERNAL_REPLICATIONS}`.",
        "- Dispersion and quantiles use seed-level estimates; replications are not treated as independent statistical units.",
        "- `prediction_only_judge_proxy` is absent from all Stage 26X-1 raw files, summaries, and figures.",
        "- These are synthetic-simulator sensitivity results, not user validation or empirical recovery of true public preferences.",
        "",
        "## Width ordering",
        "",
        f"Across internal and external paired seed-parameter cells, rule-aware width is strictly below the rule-agnostic comparator in `{width_lower_count}/{paired_count}` cells (`{width_lower_proportion:.6f}`).",
        f"Internal count: `{int(internal_pairs['width_lower'].sum())}/{len(internal_pairs)}`. External count: `{int(external_pairs['width_lower'].sum())}/{len(external_pairs)}`.",
        "",
        "### Internal parameter regions",
        "",
        internal_region.to_markdown(index=False, floatfmt=".6f"),
        "",
        "### External parameter regions",
        "",
        external_region.to_markdown(index=False, floatfmt=".6f"),
        "",
        "## Coverage tradeoff",
        "",
        f"Clean internal cells with rule-aware coverage below simplex-only coverage: `{clean_coverage_lower}/{len(clean)}`.",
        f"Positive-noise internal cells with rule-aware coverage below simplex-only coverage: `{int(noisy['coverage_lower'].sum())}/{len(noisy)}`.",
        f"Coverage decline (`simplex-only - rule-aware`) across positive-noise seed-parameter cells: mean `{decline_stats['mean']:.6f}`, median `{decline_stats['median']:.6f}`, sample std `{decline_stats['std']:.6f}`, empirical 2.5%-97.5% interval `[{decline_stats['q025']:.6f}, {decline_stats['q975']:.6f}]`.",
        "",
        "## Original seed position",
        "",
        "Percentile rank is average rank divided by 20; values at or below 0.10 or at or above 0.90 are classified as tail.",
        "",
        positions.to_markdown(index=False, floatfmt=".6f"),
        "",
        "## Reversal regions",
        "",
    ]
    if majority_region_failures == 0:
        lines.append("No preregistered parameter region meets the reversal definition.")
    else:
        if not internal_reversals.empty:
            lines.extend(["Internal reversals:", "", internal_reversals.to_markdown(index=False, floatfmt=".6f"), ""])
        if not external_reversals.empty:
            lines.extend(["External reversals:", "", external_reversals.to_markdown(index=False, floatfmt=".6f"), ""])
    lines.extend(
        [
            "",
            "## Original-setting reproduction",
            "",
            f"All `{len(reproduction)}` metric comparisons for seed 20260716 at the original internal and external settings match the historical Table 4/Table 5 source CSV values within absolute tolerance `1e-12`: `{str(reproduction_pass).lower()}`.",
            "",
            reproduction.to_markdown(index=False, floatfmt=".12g"),
            "",
            "## Figure evidence",
            "",
            f"- Figure 6 PNG and PDF were generated from the same Matplotlib canvas; embedded PDF fonts: `{'; '.join(figure6_fonts)}`.",
            f"- Figure 7 PNG and PDF were generated from the same Matplotlib canvas; embedded PDF fonts: `{'; '.join(figure7_fonts)}`.",
            "- Both figures report coverage and width with seed-level empirical 2.5%-97.5% intervals.",
            "",
            "## Ruling",
            "",
            ruling,
            "",
            f"The width ordering holds in `{width_lower_proportion:.6f}` of `{paired_count}` paired cells across `{region_count}` preregistered parameter regions; majority reversal regions: `{majority_region_failures}`; clean internal coverage-lower cells: `{clean_coverage_lower}`.",
        ]
    )
    if ruling != "CONCLUSIONS_ROBUST_ACROSS_SEEDS":
        lines.extend(
            [
                "",
                "## Manuscript claims requiring further narrowing or removal",
                "",
                "- Any claim that rule-aware width ordering holds uniformly across the preregistered seed and parameter grid.",
                "- Any claim that synthetic coverage is preserved outside the parameter regions where the paired results support it.",
                "- Any summary statement that omits the reported parameter regions where the preregistered ordering reverses.",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def generate_outputs(root: Path) -> None:
    internal_seed, external_seed = load_seed_level_results(root)
    table4, table5 = create_summary_tables(root, internal_seed, external_seed)
    plot_figure6(table4, root / FIGURE6_PNG, root / FIGURE6_PDF)
    plot_figure7(table5, root / FIGURE7_PNG, root / FIGURE7_PDF)
    figure6_fonts = embedded_pdf_fonts(root / FIGURE6_PDF)
    figure7_fonts = embedded_pdf_fonts(root / FIGURE7_PDF)
    assessment = create_robustness_assessment(
        root,
        internal_seed,
        external_seed,
        figure6_fonts=figure6_fonts,
        figure7_fonts=figure7_fonts,
    )
    atomic_write_text(assessment, root / ASSESSMENT_PATH)


def smoke_test() -> None:
    """Exercise existing code paths with locked parameters without writing outputs."""
    internal = run_internal_cell(
        seed=SEEDS[0],
        n_active=5,
        noise_probability=0.10,
        n_replications=1,
    )
    external = run_external_cell(
        seed=SEEDS[0],
        n_candidates=7,
        n_rounds=4,
        n_replications=1,
    )
    if len(internal) != len(INTERNAL_METHODS) or len(external) != len(EXTERNAL_METHODS):
        raise RuntimeError("Smoke test did not return every preregistered method.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run and verify the locked, preregistered Stage 26X-1 multiseed "
            "sensitivity experiment."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("run", "smoke", "summarize"),
        default="run",
        help=(
            "run executes/resumes all 300 registered cells and generates outputs; "
            "smoke exercises one locked cell per synthesizer without writing; "
            "summarize regenerates tables, figures, and the assessment from complete raw files."
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Project root (defaults to the parent directory of this script).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    verify_preregistered_design(root)
    manuscript_hash = file_sha256(root / BASELINE_MANUSCRIPT)
    if manuscript_hash != BASELINE_MANUSCRIPT_SHA256:
        raise RuntimeError(
            f"Stage 26W manuscript hash mismatch: expected {BASELINE_MANUSCRIPT_SHA256}, "
            f"observed {manuscript_hash}."
        )
    started = time.perf_counter()
    if args.mode == "smoke":
        smoke_test()
        print(f"Smoke test completed in {time.perf_counter() - started:.3f} seconds.")
        return 0
    if args.mode == "run":
        completed, reused = execute_registered_cells(root)
        print(f"Raw cells completed={completed}, reused={reused}.", flush=True)
    generate_outputs(root)
    print(f"Stage 26X-1 {args.mode} completed in {time.perf_counter() - started:.3f} seconds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
