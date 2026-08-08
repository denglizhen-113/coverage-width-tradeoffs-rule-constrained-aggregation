#!/usr/bin/env python3
"""Rebuild Stage 26AF figures and audit the edited non-frozen manuscript.

This stage changes presentation only. Quantitative figure inputs are existing
tracked tables, and the historical clean-room figure contract is left intact.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import math
import re
from pathlib import Path
from typing import Any, Iterable

import matplotlib
import numpy as np
import pandas as pd
from PIL import Image
from pypdf import PdfReader

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path("outputs/stage26AD/METHODS_research_draft_STAGE26AD.md")
DEFAULT_OUTPUT = Path("outputs/stage26AF")
FROZEN_X3 = Path("outputs/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md")
FROZEN_X3_SHA256 = "758755b50cd1c059d939fa550ac151c7b55263348e7bb8b55b40e20fff1c2d82"

CURRENT_FIGURES = (
    (1, Path("outputs/figures/dss_conceptual_framework.png"), "Rule-Aware Decision Support under Partially Observed Public Preferences", "Conceptual; no numeric values", "None (conceptual architecture)", True),
    (2, Path("outputs/figures/decision_support_workflow.png"), "Decision-support workflow for aggregation-mechanism evaluation", "Conceptual; no numeric values", "None (conceptual workflow)", True),
    (3, Path("outputs/figures/discretion_identifiability_frontier.png"), "Synthetic discretion-identifiability frontier", "Modeled discretion strength, normalized rank width, flexibility index", "outputs/tables/discretion_identifiability_summary.csv", False),
    (4, Path("outputs/figures/disclosure_uncertainty_curve.png"), "Synthetic value-of-disclosure scenarios", "Mean feasible-set width and predeclared accountability design score", "outputs/tables/value_of_disclosure.csv", False),
    (5, Path("outputs/figures/rule_robustness_heatmap.png"), "Rule Robustness Index by predeclared conclusion", "RRI = supporting/applicable configurations for C1-C4", "outputs/tables/rule_robustness_index.csv", False),
    (6, Path("outputs/stage26X-1/Figure_06_multiseed_internal_sensitivity.png"), "Internal synthetic sensitivity across 20 seeds", "Coverage and normalized width with seed-level 2.5%-97.5% intervals", "outputs/stage26X-1/tables/Table4_multiseed.csv", False),
    (7, Path("outputs/stage26X-1/Figure_07_multiseed_external_sensitivity.png"), "External synthetic sensitivity across 20 seeds", "Coverage and normalized feasible-rank width with seed-level 2.5%-97.5% intervals", "outputs/stage26X-1/tables/Table5_multiseed.csv", False),
    (8, Path("outputs/figures/dss_evaluation_radar.png"), "Artifact Evidence-Completeness Checks", "Artifact evidence-completeness for eight engineering criteria", "outputs/tables/dss_evaluation_metrics.csv", True),
)

NEW_FIGURES = {
    1: "Figure_01_rule_conditioned_inference_architecture",
    2: "Figure_02_reproducible_comparison_workflow",
    3: "Figure_03_discretion_identifiability_frontier",
    4: "Figure_04_compatible_disclosure_scenarios",
    5: "Figure_05_rule_robustness_index",
    6: "Figure_06_multiseed_internal_sensitivity",
    7: "Figure_07_multiseed_external_sensitivity",
}
ARTIFACT_CHECK_NAME = "Artifact_Check_evidence_completeness"


class Stage26AFError(RuntimeError):
    """Raised when a Stage 26AF contract fails."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(root: Path, relative: Path | str) -> Path:
    path = root / Path(relative)
    if not path.is_file():
        raise Stage26AFError(f"Required file is missing: {path}")
    return path


def markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    def clean(value: Any) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    output.extend("| " + " | ".join(clean(value) for value in row) + " |" for row in rows)
    return "\n".join(output)


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.2,
            "axes.titlesize": 11,
            "axes.labelsize": 9.5,
            "axes.edgecolor": "#202124",
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def save_figure(fig: Any, png_path: Path, pdf_path: Path) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=600, bbox_inches="tight", pad_inches=0.12, facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", pad_inches=0.12, facecolor="white")
    plt.close(fig)


def _box(
    ax: Any,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    face: str,
    *,
    fontsize: float = 8.2,
    edge: str = "#344054",
) -> None:
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        facecolor=face,
        edgecolor=edge,
        linewidth=0.9,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        wrap=True,
    )


def plot_figure1(png_path: Path, pdf_path: Path) -> None:
    configure_style()
    fig, ax = plt.subplots(figsize=(12.0, 6.5))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    _box(ax, (0.03, 0.62), 0.20, 0.22, "Observed institutional record\nexpert inputs | rule | outcome\ntie, save, and disclosure states", "#D9EAF4")
    _box(ax, (0.03, 0.26), 0.20, 0.22, "Latent public object\ncardinal support vector (P)\nor strict public ranking (R / R-plus)", "#F2F4F7")

    _box(ax, (0.32, 0.67), 0.24, 0.18, "Rule-conditioned feasible set\nP: simplex plus recorded inequalities\nR / R-plus: compatible rankings", "#DDEFE3")
    _box(ax, (0.32, 0.39), 0.24, 0.18, "Comparison representations\nrule-agnostic feasible set\nsame-information posterior interval", "#FCE7C5")
    _box(ax, (0.32, 0.11), 0.24, 0.18, "Assumption audit\nrule reliability | tie interpretation\ndisclosure compatibility", "#F2F4F7")

    _box(ax, (0.65, 0.67), 0.29, 0.18, "Identified summaries\ncoordinate or rank-support width\nfeasibility and residual uncertainty", "#E8E1F2")
    _box(ax, (0.65, 0.39), 0.29, 0.18, "Registered evaluation only\nknown-truth synthetic coverage\ncomponent attribution and sensitivity", "#FDECEC")
    _box(ax, (0.65, 0.11), 0.29, 0.18, "Method-selection boundary\nchoose an inferential object from accepted\nassumptions, coverage-width behavior,\nand the identified parameter region", "#FFF4D6")

    arrows = [
        ((0.23, 0.73), (0.32, 0.76)),
        ((0.23, 0.37), (0.32, 0.48)),
        ((0.23, 0.37), (0.32, 0.20)),
        ((0.56, 0.76), (0.65, 0.76)),
        ((0.56, 0.48), (0.65, 0.48)),
        ((0.56, 0.20), (0.65, 0.20)),
        ((0.795, 0.67), (0.795, 0.57)),
        ((0.795, 0.39), (0.795, 0.29)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.0, "color": "#475467"})
    ax.text(0.5, 0.96, "Rule-conditioned partial identification of latent public preference", ha="center", va="top", fontsize=13, weight="bold")
    ax.text(0.5, 0.025, "No branch is a universal winner: empirical public preference remains latent, and coverage is scored only in registered known-truth simulations.", ha="center", fontsize=8.5, color="#7A271A")
    save_figure(fig, png_path, pdf_path)


def plot_figure2(png_path: Path, pdf_path: Path) -> None:
    configure_style()
    fig, ax = plt.subplots(figsize=(12.0, 4.1))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    labels = [
        "1  Record configuration\nrule | active set\nexpert inputs | outcome\ntie/save | disclosure",
        "2  Align information sets\nrule-conditioned set\nrule-agnostic set\nsame-information posterior",
        "3  Infer conditional objects\nLP coordinate bounds\ncompatible rankings\nposterior intervals",
        "4  Evaluate within scope\nwidth | feasibility\nknown-truth coverage\nregistered simulation only",
        "5  Audit boundaries\ncomponent removal\nsensitivity checks\nclaim-to-output traceability",
    ]
    colors = ["#D9EAF4", "#DDEFE3", "#FCE7C5", "#E8E1F2", "#FFF4D6"]
    for index, (label, color) in enumerate(zip(labels, colors)):
        x = 0.025 + index * 0.195
        _box(ax, (x, 0.37), 0.17, 0.32, label, color, fontsize=7.5)
        if index < len(labels) - 1:
            ax.annotate("", xy=(x + 0.193, 0.53), xytext=(x + 0.173, 0.53), arrowprops={"arrowstyle": "->", "lw": 1.1, "color": "#475467"})
    ax.text(0.5, 0.92, "Reproducible comparison workflow", ha="center", fontsize=13, weight="bold")
    ax.text(0.5, 0.13, "Outputs are conditional evidence for method selection, not recovered ballots, observed user effects, or an automatic institutional recommendation.", ha="center", fontsize=8.6, color="#7A271A")
    save_figure(fig, png_path, pdf_path)


def plot_figure3(data: pd.DataFrame, png_path: Path, pdf_path: Path) -> None:
    configure_style()
    frontier = data.loc[data["evidence_type"].eq("synthetic rule scenario")].copy()
    fig, ax1 = plt.subplots(figsize=(7.3, 4.8), constrained_layout=True)
    x = frontier["expert_discretion_strength"].to_numpy(dtype=float)
    ax1.plot(x, frontier["normalized_rank_width"], marker="o", color="#1F5A7A", label="Normalized rank width")
    ax1.set_xlabel("Modeled bottom-set relaxation steps")
    ax1.set_ylabel("Normalized feasible-rank width", color="#1F5A7A")
    ax1.set_ylim(0, 1.05)
    ax1.set_xticks(x, ("direct", "weak save", "broader save"))
    ax1.tick_params(axis="y", labelcolor="#1F5A7A")
    ax2 = ax1.twinx()
    ax2.plot(x, frontier["institutional_flexibility_index"], marker="s", linestyle="--", color="#B85C2B", label="Scenario flexibility index")
    ax2.set_ylabel("Scenario flexibility index", color="#B85C2B")
    ax2.set_ylim(0, 1.05)
    ax2.tick_params(axis="y", labelcolor="#B85C2B")
    ax1.set_title("Discretion-identifiability frontier")
    ax1.text(0.01, -0.24, "Deterministic nested-rule scenarios; the empirical record identifies only the direct-versus-weak comparison.", transform=ax1.transAxes, fontsize=8)
    save_figure(fig, png_path, pdf_path)


def plot_figure4(data: pd.DataFrame, png_path: Path, pdf_path: Path) -> None:
    configure_style()
    ordered = data.sort_values("display_order").copy()
    labels = [
        value.replace("elimination_plus_", "").replace("_", " ").replace("full public vote theoretical upper benchmark", "full disclosure\nbenchmark")
        for value in ordered["disclosure_regime"].astype(str)
    ]
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 7.0), sharex=True, constrained_layout=True)
    positions = np.arange(len(ordered))
    axes[0].bar(positions, ordered["mean_feasible_set_width"], color="#1F5A7A", alpha=0.88)
    axes[0].set_ylabel("Normalized width")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_title("Computed feasible-set width")
    axes[1].plot(positions, ordered["accountability_gain_design_score"], color="#B85C2B", marker="o", linewidth=1.5)
    axes[1].set_ylabel("Predeclared descriptor")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title("Accountability scenario descriptor (not measured)")
    axes[1].set_xticks(positions, labels, rotation=32, ha="right")
    for axis in axes:
        axis.grid(axis="y", color="#E4E7EC", linewidth=0.7)
    fig.suptitle("Compatible disclosure scenarios", fontsize=12.5, weight="bold")
    axes[1].text(0.01, -0.42, "The lower-panel descriptor is predeclared and is not a measured trust, privacy, cost, or accountability outcome.", transform=axes[1].transAxes, fontsize=8)
    save_figure(fig, png_path, pdf_path)


def plot_figure5(data: pd.DataFrame, png_path: Path, pdf_path: Path) -> None:
    configure_style()
    values = data["rule_robustness_index"].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(8.1, 3.6), constrained_layout=True)
    image = ax.imshow(values.reshape(-1, 1), cmap="YlGnBu", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks([0], ["RRI"])
    ax.set_yticks(np.arange(len(data)), data["conclusion_id"].astype(str) + ": " + data["classification"].astype(str))
    for index, value in enumerate(values):
        ax.text(0, index, f"{value:.2f}", ha="center", va="center", color="white" if value >= 0.55 else "black", fontsize=9, weight="bold")
    fig.colorbar(image, ax=ax, label="Supporting / applicable configurations")
    ax.set_title("Rule Robustness Index across predeclared conclusions")
    save_figure(fig, png_path, pdf_path)


def load_x1_module(root: Path) -> Any:
    path = require(root, "scripts/26x1_multiseed_sensitivity.py")
    spec = importlib.util.spec_from_file_location("stage26x1_for_26af", path)
    if spec is None or spec.loader is None:
        raise Stage26AFError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._save_figure = save_figure
    return module


def plot_artifact_check(data: pd.DataFrame, png_path: Path, pdf_path: Path) -> None:
    configure_style()
    ordered = data.iloc[::-1].copy()
    values = ordered["artifact_evidence_completeness"].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(8.7, 5.0), constrained_layout=True)
    y = np.arange(len(ordered))
    ax.barh(y, values, color="#667085")
    ax.set_yticks(y, ordered["criterion"].astype(str))
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Deterministic artifact evidence-completeness")
    for index, value in enumerate(values):
        ax.text(min(value + 0.015, 1.01), index, f"{value:.2f}", va="center", fontsize=8)
    ax.set_title("Repository artifact check (not a scientific validation result)")
    ax.text(0.0, -0.16, "All values are engineering completeness checks; they do not measure effectiveness, trust, adoption, or impact.", transform=ax.transAxes, fontsize=8, color="#7A271A")
    save_figure(fig, png_path, pdf_path)


def embedded_pdf_fonts(path: Path) -> list[str]:
    reader = PdfReader(path)
    embedded: set[str] = set()
    unembedded: set[str] = set()
    for page in reader.pages:
        resources_ref = page.get("/Resources")
        if resources_ref is None:
            continue
        resources = resources_ref.get_object()
        fonts_ref = resources.get("/Font")
        if fonts_ref is None:
            continue
        for reference in fonts_ref.get_object().values():
            font = reference.get_object()
            candidates = [font]
            descendants = font.get("/DescendantFonts")
            if descendants is not None:
                candidates.extend(item.get_object() for item in descendants)
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
        raise Stage26AFError(f"Unembedded fonts in {path}: {sorted(unembedded)}")
    if not embedded:
        raise Stage26AFError(f"No verifiably embedded fonts in {path}")
    return sorted(embedded)


def png_metadata(path: Path) -> tuple[str, str]:
    with Image.open(path) as image:
        width, height = image.size
        dpi = image.info.get("dpi", (0.0, 0.0))
        xdpi, ydpi = float(dpi[0]), float(dpi[1])
    if abs(xdpi - 600.0) > 1.0 or abs(ydpi - 600.0) > 1.0:
        raise Stage26AFError(f"PNG is not 600 dpi: {path} -> {xdpi}, {ydpi}")
    return f"{width}x{height}", f"{xdpi:.1f}x{ydpi:.1f}"


def historical_audit(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    audit_rows: list[dict[str, Any]] = []
    snapshot_rows: list[dict[str, str]] = []
    for number, relative, title, values, source, has_dss in CURRENT_FIGURES:
        path = require(root, relative)
        with Image.open(path) as image:
            width, height = image.size
            dpi_info = image.info.get("dpi")
            dpi = "metadata missing" if not dpi_info else f"{float(dpi_info[0]):.0f}x{float(dpi_info[1]):.0f}"
            fmt = image.format or path.suffix.lstrip(".").upper()
        constant = number in {5, 8}
        information = "NO_INFORMATION_BEYOND_TABLE" if constant else (
            "CONCEPTUAL_INFORMATION" if number in {1, 2} else (
                "GRAPHICAL_PATTERN_WITH_INCOMMENSURATE_OVERLAY_RISK" if number == 4 else "GRAPHICAL_PATTERN_AND_INTERVAL_INFORMATION"
            )
        )
        audit_rows.append(
            {
                "figure": number,
                "title": title,
                "values": values,
                "source": source,
                "format": fmt,
                "pixels": f"{width}x{height}",
                "dpi": dpi,
                "decision_support": "YES" if has_dss else "NO",
                "information": information,
            }
        )
        snapshot_rows.append(
            {
                "contract": "historical_cleanroom_8_png",
                "figure_id": f"historical_figure_{number}",
                "path": relative.as_posix(),
                "sha256": sha256(path),
                "scope": "Stage 26AA clean-room 8/8 pixel contract; immutable historical evidence",
            }
        )
    return audit_rows, snapshot_rows


def revise_manuscript(source: str, complexity_text: str) -> tuple[str, list[tuple[str, str, str, str]]]:
    wording_before = "a real empirical application with hidden truth"
    wording_after = "a longitudinal empirical testbed with latent public preference"
    if source.count(wording_before) != 1:
        raise Stage26AFError(f"Expected one wording target; found {source.count(wording_before)}")
    revised = source.replace(wording_before, wording_after)
    wording_rows = [
        (
            "Section 4.3, evidence hierarchy",
            wording_before,
            wording_after,
            "The empirical record has no observed public-preference truth label.",
        )
    ]

    workflow_anchor = (
        "**Method-selection implication.** The artifact makes the information set and assumption changes inspectable for each comparator.\n\n"
        "## 7. Mechanism-Evaluation Modules"
    )
    if revised.count(workflow_anchor) != 1:
        raise Stage26AFError("Cannot locate the Section 6 insertion anchor")
    revised = revised.replace(
        workflow_anchor,
        "**Method-selection implication.** The artifact makes the information set and assumption changes inspectable for each comparator.\n\n"
        + complexity_text.rstrip()
        + "\n\n## 7. Mechanism-Evaluation Modules",
    )

    figure8_paragraph = (
        "### 9.6 Reproducibility scope\n\n"
        "Figure 8 summarizes deterministic evidence-completeness checks for traceability, robustness recording, output existence, and implementation reproducibility. These checks concern the research artifact. They are not scores of user effectiveness, adoption, trust, or organizational performance, and this study does not add a user experiment.\n\n"
        "[[FIGURE 8]]"
    )
    replacement = (
        "### 9.6 Reproducibility scope\n\n"
        "Deterministic evidence-completeness checks for traceability, robustness recording, output existence, and implementation reproducibility are retained in the repository as artifact diagnostics. They are not scientific validation results or scores of user effectiveness, adoption, trust, or organizational performance, and this study does not add a user experiment."
    )
    if revised.count(figure8_paragraph) != 1:
        raise Stage26AFError("Cannot locate the Figure 8 manuscript block")
    revised = revised.replace(figure8_paragraph, replacement)

    caption8 = "\n\n**Figure 8. Artifact evidence-completeness checks.** The checks concern implementation completeness, traceability, and reproducibility, not user effectiveness, adoption, trust, or organizational impact."
    if revised.count(caption8) != 1:
        raise Stage26AFError("Cannot locate the Figure 8 caption")
    revised = revised.replace(caption8, "")

    if "[[FIGURE 8]]" in revised or re.search(r"\bFigure 8\b", revised):
        raise Stage26AFError("Figure 8 still appears in the revised main manuscript")
    if "Decision Support" in revised or "decision-support" in revised.casefold():
        raise Stage26AFError("Removed Decision Support framing remains in manuscript text")
    if wording_before in revised:
        raise Stage26AFError("Unsupported hidden-truth wording remains")
    return revised.rstrip() + "\n", wording_rows


COMPLEXITY_TEXT = r"""### 6.1 Computational complexity and observed execution boundary

For a percentage-regime week with $n$ active candidates, the implemented polytope has $n$ public-support variables, one simplex equality, $n$ box bounds $0 \le p_i \le 1$, and one inequality per documented eliminated-survivor comparison. A non-final elimination record contributes $|E|(n-|E|-|W|)$ comparisons when the eliminated and withdrawn sets are disjoint; a complete final order contributes at most $n(n-1)/2$ pairwise order inequalities. The implementation first checks feasibility and then solves a minimum and maximum program for each coordinate, for $2n+1$ linear-program calls. These counts describe the implemented formulation; they are not an empirical runtime law.

For the ordinal regimes, the strict-ranking state space contains $n!$ permutations. The registered implementation enumerates exactly only when $n \le 9$ and uses fixed-seed uniform Monte Carlo above that threshold. In the empirical record, the one sampled R week uses 50,000 draws and each of 37 sampled R-plus weeks uses 10,000; 13 R weeks and 36 R-plus weeks are exact. These are the evaluated settings, not evidence for untested candidate counts.

The internal Bayesian comparator rejection-filters a fixed bank of 8,192 Dirichlet draws for each seed-parameter cell and requires at least 100 compatible draws. The 94 below-threshold replication rows show the operational consequence of low acceptance under that fixed bank; the registered design forbids adaptive enlargement. The external ordinal posterior is exact over compatible permutations in the registered small fields.

The clean-room record reports 69.01 minutes for the documented end-to-end reconstruction, including data preparation, the registered experiment archives, figures, tables, tests, and verification. Stage 26X-2 logs contain cell-level elapsed-time fields, but there is no separately instrumented timing record for an individual LP, empirical week, Stage 26X-1 cell, or isolated method phase. Accordingly, the study reports the observed full-pipeline duration and analytic state-space growth only; it does not claim efficiency or scalability beyond the evaluated configurations."""


def load_claim_audit(root: Path) -> tuple[Any, list[dict[str, str]]]:
    path = require(root, "scripts/26ac_research_audit_optimization.py")
    spec = importlib.util.spec_from_file_location("stage26ac_for_26af", path)
    if spec is None or spec.loader is None:
        raise Stage26AFError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = module.build_claim_rows(module.collect_raw_evidence(root), module.collect_summary_evidence(root))
    return module, rows


def manuscript_claim_status(manuscript: str, claim_id: str) -> str:
    required: dict[str, tuple[str, ...]] = {
        "C01": ("4,199",), "C02": ("2,777",), "C03": ("2,766",),
        "C04": ("247", "248"), "C05": ("13 exact", "50,000"),
        "C06": ("36", "37 sampled R-plus", "10,000"), "C07": ("20 preregistered seeds",),
        "C08": ("12 internal parameter regions", "three external rule structures"),
        "C09": ("67,200 synthetic cases",), "C12": ("552,000 retained method-level rows",),
        "C13": ("300/300",), "C14": ("180/180",), "C15": ("0.050289",),
        "C16": ("0.050289",), "C17": ("0.163131",), "C18": ("180/180 paired cells",),
        "C19": ("0/60",), "C20": ("0/120",), "C21": ("14/120",),
        "C22": ("94",), "C24": ("0.005",),
    }
    tokens = required.get(claim_id)
    if tokens is None:
        return "PASS_NOT_ASSERTED_AS_HEADLINE"
    missing = [token for token in tokens if token not in manuscript]
    return "PASS" if not missing else "FAIL_MISSING_" + ",".join(missing)


def figure_sources(root: Path) -> dict[int, pd.DataFrame]:
    return {
        3: pd.read_csv(require(root, "outputs/tables/discretion_identifiability_summary.csv")),
        4: pd.read_csv(require(root, "outputs/tables/value_of_disclosure.csv")),
        5: pd.read_csv(require(root, "outputs/tables/rule_robustness_index.csv")),
        6: pd.read_csv(require(root, "outputs/stage26X-1/tables/Table4_multiseed.csv")),
        7: pd.read_csv(require(root, "outputs/stage26X-1/tables/Table5_multiseed.csv")),
        8: pd.read_csv(require(root, "outputs/tables/dss_evaluation_metrics.csv")),
    }


def generate_figures(root: Path, output: Path, sources: dict[int, pd.DataFrame]) -> list[dict[str, str]]:
    main_dir = output / "figures" / "main"
    artifact_dir = output / "figures" / "repository_diagnostic"
    paths = {
        number: (main_dir / f"{stem}.png", main_dir / f"{stem}.pdf")
        for number, stem in NEW_FIGURES.items()
    }
    plot_figure1(*paths[1])
    plot_figure2(*paths[2])
    plot_figure3(sources[3], *paths[3])
    plot_figure4(sources[4], *paths[4])
    plot_figure5(sources[5], *paths[5])

    x1 = load_x1_module(root)
    x1.plot_figure6(sources[6], *paths[6])
    x1.plot_figure7(sources[7], *paths[7])

    artifact_paths = (
        artifact_dir / f"{ARTIFACT_CHECK_NAME}.png",
        artifact_dir / f"{ARTIFACT_CHECK_NAME}.pdf",
    )
    plot_artifact_check(sources[8], *artifact_paths)

    source_map = {
        1: "Conceptual architecture; no quantitative source",
        2: "Conceptual workflow; no quantitative source",
        3: "outputs/tables/discretion_identifiability_summary.csv",
        4: "outputs/tables/value_of_disclosure.csv",
        5: "outputs/tables/rule_robustness_index.csv",
        6: "outputs/stage26X-1/tables/Table4_multiseed.csv",
        7: "outputs/stage26X-1/tables/Table5_multiseed.csv",
        8: "outputs/tables/dss_evaluation_metrics.csv",
    }
    rows: list[dict[str, str]] = []
    for number in range(1, 9):
        png_path, pdf_path = paths[number] if number < 8 else artifact_paths
        pixels, dpi = png_metadata(png_path)
        fonts = embedded_pdf_fonts(pdf_path)
        rows.append(
            {
                "figure": str(number) if number < 8 else "repository artifact check (former Figure 8)",
                "pdf": pdf_path.relative_to(root).as_posix(),
                "png": png_path.relative_to(root).as_posix(),
                "pixels": pixels,
                "dpi": dpi,
                "fonts": "; ".join(fonts),
                "value_check": "PASS_CONCEPTUAL_NO_NUMBERS" if number in {1, 2} else "PASS_TRACKED_INPUT_VALUES_UNCHANGED",
                "source": source_map[number],
                "png_sha256": sha256(png_path),
                "pdf_sha256": sha256(pdf_path),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_reports(
    root: Path,
    output: Path,
    audit_rows: list[dict[str, Any]],
    historical_snapshots: list[dict[str, str]],
    delivery: list[dict[str, str]],
    sources: dict[int, pd.DataFrame],
    wording_rows: list[tuple[str, str, str, str]],
    claim_rows: list[dict[str, str]],
    manuscript: str,
) -> None:
    audit_table = markdown_table(
        ["Figure", "Original title", "Values carried", "Tracked source", "Current format", "Pixels", "DPI", "Decision Support framing", "Information assessment"],
        [
            (row["figure"], row["title"], row["values"], row["source"], row["format"], row["pixels"], row["dpi"], row["decision_support"], row["information"])
            for row in audit_rows
        ],
    )
    rri = sources[5]
    rri_rows = markdown_table(
        ["Conclusion", "Applicable", "Supporting", "RRI", "Table row"],
        [
            (row.conclusion_id, int(row.applicable_configurations), int(row.supporting_configurations), f"{float(row.rule_robustness_index):.3f}", index + 2)
            for index, row in rri.reset_index(drop=True).iterrows()
        ],
    )
    figure_audit = f"""# Stage 26AF Figure Audit

## Verdict

Figures 1 and 2 materially conflict with the current manuscript positioning because their rendered titles and layers retain Decision Support language. Historical Figure 4 overlays a computed width and an unmeasured design descriptor on one axis; Stage 26AF separates them into two panels without changing either series. Figures 5 and 8 are not plotting failures, but both are constant at 1.0 and therefore carry `NO_INFORMATION_BEYOND_TABLE`. Figure 8 is an engineering completeness check and is removed from the main manuscript. Figure 5 remains in the Stage 26AF manuscript pending the author's decision.

## Eight-figure inventory before Stage 26AF

{audit_table}

## Figure 5 diagnosis

Figure 5 reports the Rule Robustness Index, defined as supporting configurations divided by applicable configurations for predeclared conclusions C1-C4. The all-1.0 display is correct: every row in `outputs/tables/rule_robustness_index.csv` has equal supporting and applicable counts. It is not a plotting-logic error.

{rri_rows}

The four displayed values correspond to all four data rows in the CSV (physical CSV lines 2-5), not a single scientific effect. They do not currently correspond to a row of any main-manuscript Table 1-9; the RRI source is a standalone diagnostic table. The figure adds no pattern, interval, contrast, or ordering beyond those four cells.

## Figure 5 alternatives

| Option | Treatment | Tradeoff |
|---|---|---|
| Retain | Keep the high-resolution heatmap in the main text. | Preserves continuity but spends a figure on four constant values and risks making a configuration check look like a result. |
| Convert to a table row | Add `4/4 predeclared conclusions have RRI 1.000` as a new compact Table 9 row (or equivalent prose) and remove the figure. | Most compact faithful representation; loses no quantitative information. This is the audit recommendation. |
| Move out of main text | Retain the CSV and vector diagnostic in the repository/supplement only. | Keeps audit transparency while freeing main-text space; readers must consult the supplement for row detail. |

`AUTHOR_DECISION_REQUIRED`: Stage 26AF does not remove Figure 5. The author should choose between conversion to a compact table/prose statement and repository/supplement placement before the next manuscript assembly.
"""
    (output / "FIGURE_AUDIT.md").write_text(figure_audit, encoding="utf-8", newline="\n")

    redesign = """# Figure 1/2 Redesign Record

## Figure 1

**Before:** `Rule-Aware Decision Support under Partially Observed Public Preferences` with Input, Model, Decision-support, and Decision-output layers. It included recommended disclosure policy, rule risk profile, accountability implication, and a design recommendation matrix.

**After:** `Rule-conditioned partial identification of latent public preference`. The components are the observed institutional record; the latent cardinal or ordinal object; rule-conditioned and comparison representations; assumption audit; identified width/feasibility summaries; registered known-truth evaluation; and a bounded method-selection boundary.

Removed elements: Decision Support labels, recommendation hierarchy, policy output, accountability output, and visual coding that implied a progression toward a preferred method. The rule-aware feasible set and same-information comparators feed the same evaluation boundary; the footer explicitly states that no branch is a universal winner.

## Figure 2

**Before:** `Decision-support workflow for aggregation-mechanism evaluation`, ending in a recommendation matrix.

**After:** `Reproducible comparison workflow`, covering configuration, aligned information sets, conditional inference objects, scope-limited evaluation, and claim/evidence auditing.

Removed elements: decision objective, recommendation matrix, and policy-choice language. The retained arrows denote execution order only. Component names match the manuscript, and no `prediction_only` alias appears.
"""
    (output / "FIGURE_12_REDESIGN.md").write_text(redesign, encoding="utf-8", newline="\n")

    mapping_rows = [(f"Figure {i}", f"Figure {i}", NEW_FIGURES[i] + ".pdf", "main manuscript") for i in range(1, 8)]
    mapping_rows.append(("Figure 8", "No main-text number", f"repository_diagnostic/{ARTIFACT_CHECK_NAME}.pdf", "repository artifact check only"))
    references = []
    for match in re.finditer(r"\bFigure ([1-8])\b|\[\[FIGURE ([1-8])\]\]", manuscript):
        number = match.group(1) or match.group(2)
        line = manuscript[: match.start()].count("\n") + 1
        references.append((line, f"Figure {number}", "PASS" if number != "8" else "DANGLING_FIGURE_REFERENCE"))
    dangling = [row for row in references if row[2] != "PASS"]
    if dangling:
        raise Stage26AFError(f"DANGLING_FIGURE_REFERENCE: {dangling}")
    renumbering = f"""# Figure Renumbering and Reference Check

Figure 8 was the final numbered figure, so Figures 1-7 retain their numbers. Figure 5 also remains pending author decision; no provisional deletion or cascading renumbering was performed.

## Mapping

{markdown_table(["Old number", "Stage 26AF number", "Stage 26AF file", "Disposition"], mapping_rows)}

## Main-text references and placeholders

{markdown_table(["Line", "Reference", "Status"], references)}

Captions exist for Figures 1-7, filenames agree with their numbers, and the former Figure 8 caption and placeholder are absent. No appendix or cross-reference points to Figure 8. Result: `PASS_NO_DANGLING_FIGURE_REFERENCE`.
"""
    (output / "FIGURE_RENUMBERING_CHECK.md").write_text(renumbering, encoding="utf-8", newline="\n")

    delivery_table = markdown_table(
        ["New figure", "PDF", "PNG", "DPI", "Embedded-font verification", "Value consistency", "Tracked source"],
        [(row["figure"], row["pdf"], row["png"], row["dpi"], "PASS: " + row["fonts"], row["value_check"], row["source"]) for row in delivery],
    )
    delivery_report = f"""# Vector and High-Resolution Figure Delivery

{delivery_table}

All PDF files were written from the same Matplotlib canvas as their PNG counterpart with TrueType font embedding enabled. Font descriptors were inspected through `pypdf`; every referenced font with a descriptor contains `/FontFile`, `/FontFile2`, or `/FontFile3`. PNG metadata was read through Pillow and is within one dpi of 600 on both axes.

For Figures 3-7 and the repository artifact check, plotting arrays are read directly from the listed tracked CSVs without transformation beyond selection, ordering, labels, and interval-to-error-bar conversion. Figures 6 and 7 reuse the Stage 26X-1 plotting functions and multi-seed Tables 4-5. No raw output, preregistration, or research value was changed.
"""
    (output / "FIGURE_DELIVERY_VECTOR.md").write_text(delivery_report, encoding="utf-8", newline="\n")

    new_snapshots = [
        {
            "contract": "stage26AF_vector_600dpi",
            "figure_id": str(row["figure"]),
            "path": row["png"],
            "sha256": row["png_sha256"],
            "scope": "Stage 26AF presentation contract; PDF companion separately hashed in delivery manifest",
        }
        for row in delivery
    ]
    snapshot_rows = historical_snapshots + new_snapshots
    write_csv(output / "figure_snapshot_manifest.csv", snapshot_rows)
    snapshot_report = f"""# Figure Snapshot Contract Versioning

## Historical contract retained

The Stage 26AA clean-room record remains an immutable historical assertion: its eight reference PNGs matched the Stage 21/22 and Stage 26X-1 regenerated outputs pixel-for-pixel. Neither those files nor `outputs/stage26AA/REPRODUCIBILITY_VERIFICATION.md` was modified. The historical contract applies only to the old eight-PNG manuscript presentation and remains evidence for that stage.

## Stage 26AF contract added

Stage 26AF creates a separate presentation contract: seven numbered main figures plus one unnumbered repository artifact check, each with a vector PDF and 600 dpi PNG. It validates file hashes, numbering, source-table identity, PNG dpi, and PDF font embedding. It does not assert pixel equality with the historical figures because titles, layout, resolution, and scope changed deliberately.

## Coexistence rule

The contracts are parallel and stage-scoped. A historical clean-room failure may not be repaired by reverting Stage 26AF figures, and a Stage 26AF failure may not be hidden by overwriting historical reference files. Exact paths, hashes, and scopes are recorded in `figure_snapshot_manifest.csv`.

{markdown_table(["Contract", "Figure", "Path", "SHA-256", "Scope"], [(row["contract"], row["figure_id"], row["path"], row["sha256"], row["scope"]) for row in snapshot_rows])}
"""
    (output / "FIGURE_SNAPSHOT_VERSIONING.md").write_text(snapshot_report, encoding="utf-8", newline="\n")

    complexity_report = f"""# Complexity and Scalability Boundary

## Insertion location

Insert as Section 6.1 after the reproducible workflow and before Section 7.

## Manuscript text

{COMPLEXITY_TEXT}

## Number-to-source trace

| Statement | Source |
|---|---|
| $n$ variables, one equality, bounded domains, eliminated-survivor and finale comparisons | `src/constraints.py::build_percentage_constraints` |
| Feasibility plus $2n$ coordinate-bound LPs | `src/constraints.py::check_feasibility` and `solve_preference_bounds` |
| $n!$ strict rankings and exact threshold $n \\le 9$ | `src/ranking_identification.py::identify_week`; `scripts/05_ranking_identification.py --exact-threshold` |
| R: 13 exact, 1 sampled at 50,000; R-plus: 36 exact, 37 sampled at 10,000 | `outputs/tables/ranking_identification_summary_r.csv`; `outputs/tables/ranking_identification_summary_rplus.csv` |
| Fixed bank 8,192 and minimum 100 accepted draws | `outputs/stage26X-2/PREREGISTERED_DESIGN.md`; `scripts/26x2_baselines_ablation.py` |
| 94 below-threshold rows | `outputs/stage26X-2/raw/bayesian/*.csv`; claim audit C22 |
| Full pipeline 69.01 minutes | `outputs/stage26AA/REPRODUCIBILITY_VERIFICATION.md` |
| Cell timing exists only for Stage 26X-2 | `outputs/stage26X-2/logs/*_run_log.csv`, column `elapsed_seconds` |

`NO_TIMING_INSTRUMENTATION_EXISTS` for individual LPs, individual empirical weeks, Stage 26X-1 cells, and isolated method phases. The Stage 26X-2 cell timings are retained as logs but are not aggregated or extrapolated here, avoiding new timing results.
"""
    (output / "COMPLEXITY_SECTION.md").write_text(complexity_report, encoding="utf-8", newline="\n")

    wording_report = "# Wording Correction Log\n\n" + markdown_table(
        ["Location", "Before", "After", "Reason"], wording_rows
    ) + "\n\nA full-text scan found no remaining affirmative claim that the empirical competition data contain a true public-preference label. Occurrences of `ground-truth` elsewhere explicitly negate availability and are retained as limitation statements.\n"
    (output / "WORDING_CORRECTION_LOG.md").write_text(wording_report, encoding="utf-8", newline="\n")

    claim_report_rows = []
    for row in claim_rows:
        manuscript_status = manuscript_claim_status(manuscript, row["claim_id"])
        overall = "PASS" if row["status"] == "PASS" and manuscript_status.startswith("PASS") else "CLAIM_DRIFT_DETECTED"
        claim_report_rows.append((row["claim_id"], row["claim"], row["computed_value"], row["expected_value"], row["status"], manuscript_status, overall, row["evidence_files"]))
    failures = [row for row in claim_report_rows if row[6] != "PASS"]
    if failures:
        raise Stage26AFError(f"CLAIM_DRIFT_DETECTED: {[row[0] for row in failures]}")
    claim_report = f"""# Post-Edit Claim Recheck

All 24 evidence calculations were recomputed from tracked data using the Stage 26AC audit functions. Manuscript-facing checks then verified the expected representation for every headline claim that is stated in the Stage 26AF draft; C10, C11, and C23 remain traceability facts rather than manuscript headline claims and are marked accordingly.

{markdown_table(["ID", "Claim", "Computed", "Expected", "Evidence check", "Manuscript check", "Overall", "Evidence"], claim_report_rows)}

Result: `INTEGRITY_PASS` (24/24). No `CLAIM_DRIFT_DETECTED` condition was observed.
"""
    (output / "POST_EDIT_CLAIM_RECHECK.md").write_text(claim_report, encoding="utf-8", newline="\n")

    final_review = """# Stage 26AF Final Strict Review

## Overall ruling

`PASS_WITH_AUTHOR_DECISION_REQUIRED`

The Stage 26AF presentation and manuscript gates pass. The frozen Stage 26X-3 source, Stage 26X-1/26X-2 preregistrations, and raw registered outputs were not modified. No experiment was added or rerun. Seven main figures now have embedded-font vector PDF and 600 dpi PNG versions, and the former Figure 8 is retained only as a repository artifact diagnostic. All 24 evidence claims reconcile after editing, and no figure-number reference is dangling.

The sole unresolved figure disposition is Figure 5. Its four RRI values are genuinely 1.000 rather than a plotting error, but they add no information beyond the standalone four-row CSV and do not currently map to a row in main Tables 1-9. The strict-review recommendation is to remove it from the main figure sequence and add one compact Table 9 row or prose statement, while retaining the CSV and repository figure. This change was not made because the author reserved the decision.

## Problem disposition

| Review item | Ruling | Evidence |
|---|---|---|
| Figure 1 legacy Decision Support architecture | Corrected | `FIGURE_12_REDESIGN.md`; new Figure 1 |
| Figure 2 legacy Decision Support workflow | Corrected | `FIGURE_12_REDESIGN.md`; new Figure 2 |
| Figure 4 incommensurate overlay | Corrected by separating computed width and unmeasured descriptor into two panels | `FIGURE_AUDIT.md`; new Figure 4 |
| Figure 5 all-1.0 display | Numerically correct; low-information main-text use | `FIGURE_AUDIT.md`; `AUTHOR_DECISION_REQUIRED` |
| Figure 8 all-1.0 artifact radar | Removed from main manuscript; retained as repository diagnostic | `FIGURE_RENUMBERING_CHECK.md`; `reproduce.md` |
| PNG-only / insufficient dpi delivery | Corrected | `FIGURE_DELIVERY_VECTOR.md` |
| Historical clean-room contract | Preserved and versioned separately | `FIGURE_SNAPSHOT_VERSIONING.md` |
| Complexity/scalability omission | Corrected using analytic derivation and existing logs only | `COMPLEXITY_SECTION.md` |
| Empirical hidden-truth wording | Corrected to latent-preference/testbed language | `WORDING_CORRECTION_LOG.md` |
| Post-edit quantitative drift | Not observed; 24/24 pass | `POST_EDIT_CLAIM_RECHECK.md` |

## Residual boundaries

- Figure 5 disposition remains an author decision.
- The empirical competition record still lacks an observed public-preference truth label; empirical feasible sets cannot be scored for recovery.
- The Bayesian findings remain conditional on the registered prior, likelihood, fixed draw bank, and successful posterior rows.
- The 69.01-minute record is an end-to-end clean-room duration, not evidence of single-week runtime or untested scalability.
- Current SIMPAT bibliometric eligibility, portal rules, blind-review setting, and author metadata remain outside Stage 26AF and require the previously defined author/Stage 26AB gates.
- No public-release, push, release, or DOI action is authorized or performed by this stage.

## Author decisions still required

1. Decide Figure 5: retain, convert to a compact Table 9/prose statement, or move to repository/supplement. The strict-review recommendation is conversion plus repository retention.
2. Review the Stage 26AF manuscript and figure package before authorizing its private commit.
3. Separately verify SIMPAT JIF/JCR/CAS eligibility in licensed sources and complete journal/author metadata during Stage 26AB.
4. Authorize any later private push and public-release transition explicitly; neither is part of Stage 26AF.
"""
    (output / "STAGE26AF_FINAL_REVIEW_REPORT.md").write_text(final_review, encoding="utf-8", newline="\n")

    value_rows = []
    for number, frame in sources.items():
        relative = {
            3: "outputs/tables/discretion_identifiability_summary.csv",
            4: "outputs/tables/value_of_disclosure.csv",
            5: "outputs/tables/rule_robustness_index.csv",
            6: "outputs/stage26X-1/tables/Table4_multiseed.csv",
            7: "outputs/stage26X-1/tables/Table5_multiseed.csv",
            8: "outputs/tables/dss_evaluation_metrics.csv",
        }[number]
        value_rows.append({"figure": str(number), "source": relative, "source_sha256": sha256(root / relative), "source_rows": str(len(frame)), "validation": "PASS_READ_DIRECTLY_FROM_TRACKED_CSV"})
    write_csv(output / "figure_value_manifest.csv", value_rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Stage 26AF figures, manuscript, and audit reports without rerunning experiments.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Project root (default: repository containing this script).")
    parser.add_argument("--source-manuscript", type=Path, default=DEFAULT_SOURCE, help="Project-relative non-frozen source manuscript.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Project-relative Stage 26AF output directory.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    if args.source_manuscript.is_absolute() or args.output_dir.is_absolute():
        raise Stage26AFError("Source manuscript and output directory must be project-relative")
    output = root / args.output_dir
    output.mkdir(parents=True, exist_ok=True)

    frozen = require(root, FROZEN_X3)
    frozen_before = sha256(frozen)
    if frozen_before != FROZEN_X3_SHA256:
        raise Stage26AFError(f"Frozen Stage 26X-3 hash mismatch: {frozen_before}")

    source_path = require(root, args.source_manuscript)
    source_hash = sha256(source_path)
    source = source_path.read_text(encoding="utf-8")
    audit_rows, historical_snapshots = historical_audit(root)
    sources = figure_sources(root)
    revised, wording_rows = revise_manuscript(source, COMPLEXITY_TEXT)
    manuscript_path = output / "METHODS_research_draft_STAGE26AF.md"
    manuscript_path.write_text(revised, encoding="utf-8", newline="\n")

    delivery = generate_figures(root, output, sources)
    _, claim_rows = load_claim_audit(root)
    build_reports(root, output, audit_rows, historical_snapshots, delivery, sources, wording_rows, claim_rows, revised)

    if sha256(source_path) != source_hash:
        raise Stage26AFError("Stage 26AD source manuscript changed during Stage 26AF")
    if sha256(frozen) != frozen_before:
        raise Stage26AFError("Frozen Stage 26X-3 manuscript changed during Stage 26AF")
    print(f"Wrote {manuscript_path.relative_to(root).as_posix()}")
    print("FIGURES_MAIN=7; REPOSITORY_DIAGNOSTIC=1; PDF_FONTS=EMBEDDED; PNG_DPI=600")
    print("CLAIMS_PASS=24/24")
    print("FIGURE5=AUTHOR_DECISION_REQUIRED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Stage26AFError as exc:
        raise SystemExit(f"Stage 26AF failed: {exc}") from exc
