#!/usr/bin/env python3
"""Build a reproducible DSS upgrade package without touching frozen results.

All new quantitative outputs are either (1) summaries of existing empirical
identification artifacts or (2) fixed-seed synthetic/scenario analyses. The
script never treats synthetic latent preferences as empirical observations.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.baseline_comparison import build_baseline_comparison  # noqa: E402
from src.discretion_identifiability import (  # noqa: E402
    observed_rplus_summary,
    synthetic_discretion_frontier,
)
from src.robustness_sensitivity import build_robustness_sensitivity  # noqa: E402
from src.rule_robustness_index import build_rule_robustness_index  # noqa: E402
from src.synthetic_benchmark import run_synthetic_benchmark  # noqa: E402
from src.value_of_disclosure import run_value_of_disclosure  # noqa: E402


FIGURE_DPI = 250
SEED = 20260716


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate deterministic DSS decision-support modules, synthetic "
            "validation, scenario outputs, figures, and manuscript sections."
        )
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--synthetic-replications", type=int, default=250)
    parser.add_argument("--disclosure-cases", type=int, default=100)
    parser.add_argument("--seed", type=int, default=SEED)
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8", lineterminator="\n", float_format="%.12g")
    temporary.replace(path)


def require(root: Path, relative_paths: list[str]) -> None:
    missing = [path for path in relative_paths if not (root / path).is_file()]
    if missing:
        raise FileNotFoundError("Required DSS inputs are missing: " + "; ".join(missing))


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for _, row in frame.loc[:, columns].fillna("").iterrows():
        values = [str(row[column]).replace("|", "\\|").replace("\n", " ") for column in columns]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, divider, *rows])


def apply_plot_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)


def _box(ax: plt.Axes, xy: tuple[float, float], text: str, color: str) -> None:
    patch = FancyBboxPatch(
        xy, 0.18, 0.18, boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor=color, edgecolor="#3a3a3a", linewidth=0.8,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + 0.09, xy[1] + 0.09, text, ha="center", va="center", fontsize=8, wrap=True)


def plot_conceptual_framework(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.0, 6.6))
    ax.set_axis_off()
    input_boxes = [
        ("Observed\neliminations", (0.03, 0.75)),
        ("Institutional\nrule descriptions", (0.03, 0.51)),
        ("Expert interventions\nand available signals", (0.03, 0.27)),
        ("Hidden public\npreferences", (0.03, 0.03)),
    ]
    model_boxes = [
        ("Rule-aware\nconstraints", (0.30, 0.72)),
        ("Partial-identification\nengine", (0.30, 0.48)),
        ("Uncertainty\nquantification", (0.30, 0.24)),
        ("Scenario simulator\nand robustness evaluator", (0.30, 0.00)),
    ]
    support_boxes = [
        ("Rule comparison", (0.57, 0.72)),
        ("Discretion-identifiability\nevaluation", (0.57, 0.48)),
        ("Value-of-disclosure\nanalysis", (0.57, 0.24)),
        ("Design recommendation\nmatrix", (0.57, 0.00)),
    ]
    output_boxes = [
        ("Recommended disclosure\npolicy", (0.81, 0.75)),
        ("Aggregation-rule\nrisk profile", (0.81, 0.51)),
        ("Uncertainty and\naccountability implication", (0.81, 0.27)),
        ("Sensitivity warning", (0.81, 0.03)),
    ]
    for text, xy in input_boxes:
        _box(ax, xy, text, "#DCEAF7")
    for text, xy in model_boxes:
        _box(ax, xy, text, "#DDF1E3")
    for text, xy in support_boxes:
        _box(ax, xy, text, "#FCE8C6")
    for text, xy in output_boxes:
        _box(ax, xy, text, "#E9DFF4")
    for y in [0.12, 0.36, 0.60, 0.84]:
        for start, end in [(0.21, 0.30), (0.48, 0.57), (0.75, 0.81)]:
            ax.annotate("", xy=(end, y), xytext=(start, y), arrowprops={"arrowstyle": "->", "lw": 1.0, "color": "#4a4a4a"})
    ax.text(0.12, 0.97, "Input layer", ha="center", va="top", fontsize=11, weight="bold")
    ax.text(0.39, 0.97, "Model layer", ha="center", va="top", fontsize=11, weight="bold")
    ax.text(0.66, 0.97, "Decision-support layer", ha="center", va="top", fontsize=11, weight="bold")
    ax.text(0.90, 0.97, "Decision outputs", ha="center", va="top", fontsize=11, weight="bold")
    fig.suptitle("Rule-Aware Decision Support under Partially Observed Public Preferences", y=1.02, fontsize=13, weight="bold")
    save_figure(fig, path)


def plot_discretion_frontier(frontier: pd.DataFrame, path: Path) -> None:
    fig, ax1 = plt.subplots(figsize=(7.3, 4.8), constrained_layout=True)
    x = frontier["expert_discretion_strength"]
    ax1.plot(x, frontier["normalized_rank_width"], marker="o", color="#1F5A7A", label="Normalized rank width")
    ax1.set_xlabel("Synthetic discretion strength (bottom-set relaxation steps)")
    ax1.set_ylabel("Normalized feasible-rank width", color="#1F5A7A")
    ax1.set_ylim(0, 1.05)
    ax1.tick_params(axis="y", labelcolor="#1F5A7A")
    ax2 = ax1.twinx()
    ax2.plot(x, frontier["institutional_flexibility_index"], marker="s", linestyle="--", color="#B85C2B", label="Flexibility index")
    ax2.set_ylabel("Scenario flexibility index", color="#B85C2B")
    ax2.set_ylim(0, 1.05)
    ax2.tick_params(axis="y", labelcolor="#B85C2B")
    ax1.set_title("Synthetic discretion-identifiability frontier")
    ax1.text(0.01, -0.24, "Illustrative nested rule scenarios; the empirical data identify a direct-versus-weak comparison, not this continuum.", transform=ax1.transAxes, fontsize=8)
    save_figure(fig, path)


def plot_disclosure_curve(disclosure: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.2), constrained_layout=True)
    data = disclosure.sort_values("display_order")
    labels = [label.replace("elimination_plus_", "").replace("_", " ").replace("full public vote theoretical upper benchmark", "full disclosure\nbenchmark") for label in data["disclosure_regime"]]
    ax.bar(np.arange(len(data)), data["mean_feasible_set_width"], color="#1F5A7A", alpha=0.85, label="Feasible-set width")
    ax.plot(np.arange(len(data)), data["accountability_gain_design_score"], color="#B85C2B", marker="o", linewidth=1.5, label="Accountability design score")
    ax.set_xticks(np.arange(len(data)), labels, rotation=32, ha="right")
    ax.set_ylabel("Width or predeclared design score")
    ax.set_ylim(0, 1.05)
    ax.set_title("Synthetic value-of-disclosure scenarios")
    ax.legend(frameon=False, loc="upper right")
    ax.text(0.01, -0.32, "Costs, privacy, interpretability, and accountability values are design-scenario descriptors, not measured stakeholder outcomes.", transform=ax.transAxes, fontsize=8)
    save_figure(fig, path)


def plot_rri_heatmap(rri: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.1, 3.4), constrained_layout=True)
    values = rri[["rule_robustness_index"]].to_numpy(dtype=float)
    image = ax.imshow(values, cmap="YlGnBu", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks([0], ["RRI"])
    ax.set_yticks(np.arange(len(rri)), rri["conclusion_id"] + ": " + rri["classification"])
    for index, row in rri.reset_index(drop=True).iterrows():
        ax.text(0, index, f"{row.rule_robustness_index:.2f}", ha="center", va="center", color="black", fontsize=9, weight="bold")
    fig.colorbar(image, ax=ax, label="Share of applicable configurations supporting conclusion")
    ax.set_title("Rule Robustness Index by predeclared conclusion")
    save_figure(fig, path)


def plot_synthetic_coverage(benchmark: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.5), constrained_layout=True)
    data = benchmark.loc[benchmark["condition"].eq("rule_consistent")].copy()
    labels = data["method"].str.replace("_", " ").str.replace("full disclosure oracle synthetic only", "oracle")
    axes[0].bar(np.arange(len(data)), data["coverage_rate"], color="#2F6B4F")
    axes[0].set_xticks(np.arange(len(data)), labels, rotation=35, ha="right")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel("Synthetic truth coverage rate")
    axes[0].set_title("Known-truth coverage")
    axes[1].bar(np.arange(len(data)), data["false_certainty_rate"], color="#B85C2B")
    axes[1].set_xticks(np.arange(len(data)), labels, rotation=35, ha="right")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_ylabel("False certainty rate")
    axes[1].set_title("False precision diagnostic")
    fig.suptitle("Synthetic benchmark: calibration under known latent preferences", y=1.03, fontsize=12, weight="bold")
    save_figure(fig, path)


def plot_baselines(baselines: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.7, 4.8), constrained_layout=True)
    data = baselines.copy()
    x = np.arange(len(data))
    width = 0.36
    ax.bar(x - width / 2, data["coverage_rate"], width=width, label="Coverage", color="#2F6B4F")
    ax.bar(x + width / 2, data["false_certainty_rate"], width=width, label="False certainty", color="#B85C2B")
    ax.set_xticks(x, data["method"].str.replace("_", " "), rotation=30, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Rate in synthetic benchmark")
    ax.set_title("Rule-aware feasible sets versus synthetic baselines")
    ax.legend(frameon=False)
    save_figure(fig, path)


def plot_robustness(sensitivity: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.6, 5.2), constrained_layout=True)
    data = sensitivity.copy()
    numeric = pd.to_numeric(data["relative_change_or_gap"], errors="coerce").fillna(0.0)
    colors = data["classification"].map({"stable": "#2F6B4F", "moderately sensitive": "#D28A2D", "highly sensitive": "#B84B4B"})
    ax.barh(np.arange(len(data)), numeric.abs(), color=colors)
    ax.set_yticks(np.arange(len(data)), data["sensitivity_dimension"])
    ax.set_xlabel("Absolute relative change or gap (not comparable where formal boundary applies)")
    ax.set_title("Robustness and sensitivity package")
    ax.invert_yaxis()
    ax.text(0.01, -0.13, "Ordinal/cardinal mapping is shown as a formal non-comparability warning, not as a numeric sensitivity estimate.", transform=ax.transAxes, fontsize=8)
    save_figure(fig, path)


def plot_workflow(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.0, 3.2))
    ax.set_axis_off()
    labels = ["Specify objective\nand rule alternatives", "Encode observed\ninformation and gaps", "Compute feasible sets\nand scenarios", "Compare disclosure,\ndiscretion, robustness", "Use recommendation\nmatrix with warnings"]
    colors = ["#DCEAF7", "#DDF1E3", "#FCE8C6", "#E9DFF4", "#F6D7D7"]
    for index, (label, color) in enumerate(zip(labels, colors)):
        x = 0.02 + index * 0.195
        patch = FancyBboxPatch((x, 0.32), 0.16, 0.34, boxstyle="round,pad=0.02,rounding_size=0.02", facecolor=color, edgecolor="#3a3a3a")
        ax.add_patch(patch)
        ax.text(x + 0.08, 0.49, label, ha="center", va="center", fontsize=8.5, wrap=True)
        if index < len(labels) - 1:
            ax.annotate("", xy=(x + 0.19, 0.49), xytext=(x + 0.165, 0.49), arrowprops={"arrowstyle": "->", "lw": 1.1})
    ax.text(0.5, 0.93, "Decision-support workflow for aggregation-mechanism evaluation", ha="center", fontsize=12, weight="bold")
    ax.text(0.5, 0.08, "Outputs are conditional on documented rules and disclosure assumptions; they support judgment rather than replacing it.", ha="center", fontsize=8.5)
    save_figure(fig, path)


def decision_alternatives_criteria() -> pd.DataFrame:
    alternatives = [
        ("Maintain current aggregation rule", "baseline governance option", "institutional designer", "Use when current rule is documented and uncertainty is acceptable."),
        ("Reduce expert discretion", "narrow discretionary override eligibility", "institutional designer", "Use when identifiability and auditability outweigh flexibility."),
        ("Keep discretion with disclosed rationale", "retain override with reason record", "platform organizer", "Use when exceptional-case flexibility is required."),
        ("Publish top-k public ranking", "ordinal public disclosure", "contest governance body", "Use when rank transparency is acceptable."),
        ("Publish vote-bin intervals", "coarsened cardinal disclosure", "contest governance body", "Use when precision disclosure must be limited."),
        ("Publish pairwise majority information", "comparative public disclosure", "expert-panel coordinator", "Use when ordering is useful and cardinal disclosure is not."),
        ("Publish margin intervals", "bounded comparative disclosure", "platform organizer", "Use when auditability needs strength-of-preference information."),
        ("Change tie-handling protocol", "strict or relaxed rank policy", "institutional designer", "Use when tie frequency and procedural consistency are material."),
        ("Switch cardinal versus ordinal aggregation", "change aggregation representation", "institutional designer", "Use only after objective, privacy, and comparability review."),
    ]
    criteria = "transparency; preference identifiability; institutional flexibility; public trust; stability of outcomes; privacy protection; reporting cost; interpretability; robustness to assumptions"
    return pd.DataFrame(alternatives, columns=["decision_alternative", "design_action", "decision_maker", "use_condition"]).assign(evaluation_criteria=criteria, evidence_boundary="Matrix is a decision-design template; trust, cost, and privacy require local stakeholder evidence.")


def recommendation_matrix() -> pd.DataFrame:
    rows = [
        ("maximize transparency", "publish top-k rank plus margin intervals", "top-k ranking; bounded margins; intervention rationale", "more auditable information", "privacy and reporting burden", "medium-high", "enables external review of information limits", "when privacy or strategic manipulation dominates"),
        ("preserve expert discretion", "retain save/override with disclosed eligibility and rationale", "intervention trigger and rationale", "flexibility for exceptional cases", "weaker identifiability without disclosure", "medium", "records why outcome implication was relaxed", "when rationale cannot be documented"),
        ("reduce uncertainty", "add the smallest disclosure channel that materially shrinks the feasible set", "rank, bins, pairwise, or margins selected by scenario", "narrower compatible-state set", "may increase privacy exposure", "variable", "makes residual ambiguity explicit", "when additional disclosure violates policy or privacy"),
        ("protect public-vote privacy", "use vote bins or pairwise majority rather than exact shares", "coarsened bins or pairwise relation", "privacy-preserving transparency", "less information gain than exact disclosure", "medium", "documents controlled information release", "when even coarse preferences are sensitive"),
        ("improve outcome stability", "pre-specify tie protocol and override rule", "tie rule and override record", "procedural consistency", "may constrain flexibility", "low-medium", "allows audit of rule changes", "when adaptive intervention is essential"),
        ("improve interpretability", "separate cardinal and ordinal reports and explain feasible sets", "regime-specific uncertainty summaries", "clearer limits of inference", "additional communication effort", "low", "prevents false precision", "when users require a single score despite incompatible objects"),
        ("reduce reporting burden", "publish a documented minimum disclosure package", "rule description plus selected coarse signal", "lower implementation cost", "remaining uncertainty may be large", "low", "states what cannot be audited", "when a decision requires higher accountability"),
        ("improve external auditability", "release rule code, checksums, and scenario configuration", "provenance and reproducibility materials", "independent verification", "maintenance and source-term cost", "medium", "makes assumptions inspectable", "when data terms prevent controlled verification"),
    ]
    return pd.DataFrame(rows, columns=["decision_objective", "recommended_institutional_design", "required_disclosure", "expected_benefit", "major_risk", "implementation_cost", "accountability_implication", "when_not_to_use"])


def dss_gap_matrix() -> pd.DataFrame:
    rows = [
        ("Clear decision-support problem", "partial", "Existing paper emphasizes identification more than a designer choice.", "DSS editor may see no decision task.", "Add decision-problem formulation and workflow.", "manuscript/sections/decision_problem_formulation.md", "critical"),
        ("Explicit decision maker", "partial", "Institutional designers are mentioned but not operationalized.", "No user of outputs is defined.", "Specify designer, organizer, governance body, and expert-panel coordinator roles.", "manuscript/sections/decision_problem_formulation.md", "critical"),
        ("Decision alternatives", "missing", "No formal choice set currently links rules/disclosure to outputs.", "Framework reads as retrospective analysis.", "Create alternatives-criteria matrix and recommendation layer.", "outputs/tables/decision_alternatives_criteria.csv", "critical"),
        ("Evaluation criteria", "partial", "Uncertainty and robustness exist; transparency, privacy, cost, and flexibility are not structured.", "No multi-criterion decision support.", "Use predeclared qualitative design criteria with explicit evidence boundaries.", "outputs/tables/design_recommendation_matrix.csv", "critical"),
        ("Decision-support workflow", "missing", "No end-to-end workflow currently connects data to a design choice.", "No DSS artifact identity.", "Add conceptual model and workflow figure.", "outputs/figures/decision_support_workflow.png", "critical"),
        ("Technical method contribution", "partial", "LP/ordinal feasible-set engine exists.", "May appear as a case-specific method application.", "Add disclosure, robustness, and synthetic modules.", "src/value_of_disclosure.py; src/rule_robustness_index.py; src/synthetic_benchmark.py", "critical"),
        ("Interface or usage scenario", "partial", "No deployed interface or user study.", "DSS usability/impact claims would be unsupported.", "Provide conceptual workflow only; do not claim usability without a future evaluation.", "manuscript/sections/dss_conceptual_model.md", "major"),
        ("Impact and evaluation layer", "missing", "Existing counterfactuals are not an institutional recommendation layer.", "No decision consequence interpretation.", "Add recommendation matrix and scenario tradeoffs.", "manuscript/sections/decision_support_recommendations.md", "critical"),
        ("Baseline comparison", "partial", "Prediction baseline exists but not a known-truth method comparison.", "No evidence of avoiding false precision.", "Add synthetic rule-agnostic, point, prediction, and oracle baselines.", "src/baseline_comparison.py", "critical"),
        ("Robustness analysis", "partial", "Tie sensitivity and sampling diagnostics exist.", "No unified conclusion-stability view.", "Add RRI and sensitivity package.", "src/rule_robustness_index.py; src/robustness_sensitivity.py", "major"),
        ("Reproducibility", "partial", "Pipeline, tests, seeds, and hashes exist; archive/lock remain incomplete.", "Release reproducibility risk.", "Add module seeds/tests now; complete archive and environment lock before submission.", "outputs/logs/dss_full_attack_readiness_report.md", "major"),
        ("Practical implications", "partial", "Discussion has general design implications.", "DSS relevance may remain abstract.", "Map objectives to institutional designs and non-use conditions.", "manuscript/sections/decision_support_recommendations.md", "major"),
        ("Avoidance of overclaiming hidden preferences", "strong", "Existing audits preserve feasible-set language.", "New DSS framing could introduce false claims.", "Retain explicit claim-control section in every new manuscript module.", "manuscript/limitations_claim_control.md", "moderate"),
    ]
    return pd.DataFrame(rows, columns=["DSS_requirement", "current_status", "deficiency", "risk_for_DSS", "required_fix", "file_to_modify_or_create", "priority"])


def four_contributions() -> str:
    return """
# DSS Contributions

## Contribution 1

We develop a rule-aware partial-identification framework for decision support under hidden public preferences. It maps documented aggregation rules, visible expert inputs, and coarse outcomes to feasible preference representations rather than selecting an unobserved point estimate.

## Contribution 2

We add a mechanism-evaluation module that compares aggregation rules, expert-discretion regimes, tie-handling assumptions, and modeled disclosure policies while preserving the distinction between cardinal and ordinal state spaces.

## Contribution 3

We provide a decision-support evaluation layer that translates feasible-set uncertainty into conditional institutional design recommendations concerning transparency, discretion, stability, interpretability, and reporting burden.

## Contribution 4

We supply a reproducible validation package combining fixed-seed synthetic ground-truth benchmarking, baseline comparison, and robustness analysis. These tests assess logical calibration and conclusion stability; they do not recover empirical hidden public preferences.
"""


def decision_problem_text() -> str:
    return """
# Decision-Support Problem Formulation

## Decision maker and information structure

The decision maker is an institutional designer, platform organizer, contest governance body, or expert-panel coordinator. The designer observes institutional rules, elimination outcomes, expert scores or ranks when released, intervention records, and selected public signals. Public preferences remain partly hidden. The central task is therefore not to infer one latent public score, but to determine which rule and disclosure choices are defensible given the uncertainty that the observed record leaves unresolved.

## Decision alternatives and criteria

The framework evaluates maintaining or changing an aggregation rule, modifying expert discretion, documenting intervention rationale, changing tie handling, and choosing a minimum disclosure policy. It reports feasible-set uncertainty alongside predeclared design criteria: transparency, preference identifiability, institutional flexibility, public trust, outcome stability, privacy protection, reporting cost, interpretability, and robustness to assumptions.

## Workflow boundary

The framework supports structured institutional judgment. It does not estimate an exact hidden public vote, prove public trust, determine an optimal policy, or replace the objective-setting responsibility of the institution. Disclosure costs, privacy risks, and accountability gains are scenario descriptors unless supported by local stakeholder evidence.
"""


def conceptual_model_text() -> str:
    return """
# DSS Conceptual Model

The framework has four linked layers. The input layer records observed eliminations, rule descriptions, expert interventions, available public signals, and explicit missing-preference states. The model layer builds rule-aware constraints, computes feasible preference sets, quantifies uncertainty, simulates documented scenarios, and evaluates robustness. The decision-support layer compares rules, assesses the discretion-identifiability trade-off, evaluates modeled disclosure policies, and maps results into a design-recommendation matrix. The output layer reports a conditional disclosure recommendation, aggregation-rule risk profile, uncertainty classification, accountability implication, and sensitivity warning.

The corresponding figure is `outputs/figures/dss_conceptual_framework.png`. It is a conceptual workflow, not a deployed software interface or a claim of stakeholder validation.
"""


def formal_propositions_text() -> str:
    propositions = [
        ("Proposition 1", "Additional disclosure weakly shrinks the feasible preference set.", "The latent state space and base rule are fixed; the extra disclosure is truthful, correctly encoded, and adds conjunctive constraints.", "Every state compatible with richer disclosure is also compatible with the coarser record.", "The richer feasible set is the base feasible set intersected with extra constraints, so it is a subset or equal set.", "Synthetic disclosure scenarios should show nonnegative shrinkage; historical disclosure is not asserted.", "Methods disclosure module and appendix."),
        ("Proposition 2", "Correct rule-aware constraints produce feasible sets no larger than rule-agnostic constraints.", "Both models share a latent state space and every rule-aware constraint is valid; the rule-agnostic constraints are nested.", "Known rule detail removes states that a simplex-only representation cannot exclude.", "Intersect the common state space with the larger rule-agnostic constraint set and its rule-aware superset.", "Synthetic baseline comparison should show width no larger for the rule-aware set under correct specification.", "Methods and synthetic benchmark appendix."),
        ("Proposition 3", "Undisclosed expert-discretion relaxations can increase identifiability uncertainty relative to direct aggregation.", "Same active set and score rule; direct feasibility logically implies weak feasibility; tie policy is fixed.", "A relaxed bottom-set condition admits every direct state and may admit weak-only states.", "Direct feasibility implies weak feasibility. Strict expansion follows whenever at least one weak-only state exists.", "Observed R_plus containment is a binary rule comparison; multi-level frontiers are synthetic scenarios.", "Discretion module, results, and appendix."),
        ("Proposition 4", "Ordinal and cardinal regimes cannot be compared directly without a common uncertainty functional.", "No justified mapping from ordinal ranks to cardinal shares is imposed and samples/state spaces differ.", "Rank-support width and share-interval width have different units and semantics.", "A rescaling or rank relabeling counterexample changes raw width without preserving a common information interpretation.", "Report regime-specific summaries or define and validate a common functional before comparison.", "Methods comparability note and RRI section."),
        ("Proposition 5", "Prediction accuracy on observed outcomes is not evidence of hidden preference recovery.", "Feedback is coarse, hidden preference is unobserved, and no injective latent-to-observable mapping is justified.", "Different latent states can generate the same elimination outcome.", "Any feasible set with more than one state gives a counterexample: an outcome predictor need not distinguish those states.", "Prediction may be used as outcome-consistency evidence only.", "Validation section and limitations."),
    ]
    parts = ["# Formal Propositions"]
    for name, statement, assumptions, intuition, proof, implication, insertion in propositions:
        parts.extend([f"\n## {name}", f"\n**Statement.** {statement}", f"\n**Assumptions.** {assumptions}", f"\n**Intuition.** {intuition}", f"\n**Proof sketch.** {proof}", f"\n**Empirical implication.** {implication}", f"\n**Manuscript insertion point.** {insertion}"])
    return "\n".join(parts)


def dss_abstract() -> str:
    return """
# DSS Abstract Draft

Institutional and platform designers often combine expert judgment with public input while disclosing only coarse outcomes. When public preferences are partly hidden, designers cannot determine whether an observed outcome reflects collective signals, expert discretion, or artifacts of an aggregation rule. We develop a rule-aware decision-support framework that represents this information problem through partial identification. Documented rules, expert inputs, active sets, and outcomes define feasible preference sets rather than a single recovered public score. The framework compares cardinal percentage rules, ordinal ranking rules, discretionary judge-save conditions, tie handling, and modeled disclosure policies. It translates feasible-set uncertainty into conditional design guidance concerning transparency, flexibility, stability, interpretability, reporting cost, and accountability. A fixed-seed synthetic benchmark with known latent preferences evaluates coverage, false certainty, rule-aware versus rule-agnostic bounds, point-selection baselines, and outcome-prediction baselines. A longitudinal empirical application demonstrates the workflow under documented rule changes, while remaining a testbed rather than universal proof. Results are interpreted as mechanism-specific uncertainty and scenario evidence: they do not establish exact hidden public preferences, stakeholder trust, or a universally optimal institutional rule. The contribution is a reproducible framework for evaluating aggregation mechanisms and disclosure designs when decision makers must act under partially observed collective input.
"""


def dss_introduction() -> str:
    return """
# DSS Introduction Draft

Institutional and platform decisions increasingly combine public input with expert judgment. Their procedures may use scores, ranks, eliminations, tie rules, and discretionary interventions, creating systems in which several decision channels contribute to one visible outcome.

In many expert-crowd systems, public preferences are not fully disclosed. Institutional designers are consequently unable to determine from an elimination alone whether the record is consistent with many public signals, whether expert discretion relaxed the outcome implication, or whether a rule artifact drives apparent agreement.

This is a decision-support problem, not merely an estimation problem. The designer must compare rule and disclosure alternatives while retaining the uncertainty that hidden preferences create, rather than silently selecting one latent explanation.

Prediction, unconstrained rank aggregation, and ex post outcome analysis can be useful descriptive tools, but they can create false precision when the observation process is coarse. Accurate prediction of an elimination does not make the hidden collective input observable.

We propose a rule-aware partial-identification decision-support framework. It converts documented institutional rules, visible expert inputs, active sets, intervention records, and observed outcomes into feasible preference representations that state what the record supports and what it leaves unresolved.

The framework adds a discretion-identifiability frontier, modeled value-of-disclosure scenarios, a Rule Robustness Index, a fixed-seed synthetic ground-truth benchmark, and a conditional recommendation matrix. These modules evaluate aggregation mechanisms without pooling cardinal and ordinal quantities or treating scenario assumptions as historical facts.

The paper makes exactly four contributions: rule-aware partial identification for decision support; mechanism evaluation across rules, discretion, ties, and disclosure; a conditional institutional recommendation layer; and a reproducible validation package with synthetic benchmarks, baselines, and robustness diagnostics.
"""


def related_work_text() -> str:
    return """
# DSS Related Work Upgrade

## Decision support systems and institutional decision making

The DSS framing requires literature on decision tasks, artifact evaluation, and institutional use. The present source map does not yet contain a completed, full-text-verified DSS literature review. This section is therefore a revision scaffold, not a claim that the existing citations establish DSS artifact effectiveness. Before submission, authors must add and read venue-specific sources that support the chosen decision task and evaluation design.

## Expert-crowd aggregation and collective intelligence

Existing verified sources support the general observation that collective and expert inputs can interact, while not making the empirical testbed a direct measure of public preference (Lorenz et al., 2011). The new contribution concerns the institutional information consequences of aggregation and disclosure rules.

## Preference learning, rank aggregation, and hidden preferences

Social-choice and rank-aggregation sources explain why aggregation rules and ordinal representations matter (Arrow, 1950; Young, 1988; Dwork et al., 2001). Liang (2019) motivates the boundary that preference inference depends on the observed choice process.

## Partial identification and uncertainty-aware inference

Manski (2000), Imbens and Manski (2004), and Manski (2007) motivate feasible-set reasoning and decisions under incomplete identification. The framework uses this logic to support conditional rule and disclosure evaluation rather than select a latent preference point.

## Transparency, accountability, and information disclosure

The disclosure module is a formal information scenario, not an empirical study of trust, privacy, or accountability. A DSS submission requires a completed literature review and, if practical implications are expanded, stakeholder or organizational evidence appropriate to those claims.

## Gap

Existing work rarely provides a decision-support framework for evaluating aggregation mechanisms when public preferences are hidden and expert intervention is rule-dependent. The revised paper addresses that gap conditionally through feasible-set uncertainty, disclosure scenarios, robustness analysis, and an explicit recommendation workflow.
"""


def limitations_text() -> str:
    return """
# Limitations and Claim Control

1. The method does not recover exact hidden public votes. It reports feasible preference sets and scenario summaries conditional on documented rules and assumptions.
2. The empirical application is a longitudinal testbed, not universal proof about institutions, platforms, or public behavior.
3. Rule specification quality matters. Incorrect rule, tie, intervention, or disclosure encoding can invalidate the relevant scenario.
4. Synthetic validation tests logical calibration when simulated latent preferences are known. It does not establish empirical truth in the application data.
5. Disclosure recommendations involve tradeoffs among modeled information gain, reporting burden, and privacy; their governance scores are not measured stakeholder outcomes.
6. Expert discretion is not inherently undesirable. The framework identifies a potential flexibility-identifiability tradeoff under stated conditions.
7. The framework supports decision analysis and structured institutional judgment; it does not replace objective setting, legal review, privacy assessment, or local governance expertise.
"""


def dss_restructure_plan() -> str:
    return """
# DSS Manuscript Restructure Plan

1. Introduction: rewrite using `manuscript/introduction_DSS_full_attack.md`.
2. Decision-support problem and institutional context: add `manuscript/sections/decision_problem_formulation.md`.
3. Related work: replace the generic framing with `manuscript/related_work_DSS_upgrade.md` after full-text venue-specific citation review.
4. Framework overview: add `manuscript/sections/dss_conceptual_model.md` and Figure DSS-1.
5. Rule-aware partial-identification model: merge existing data/rule and methods sections; preserve P/R/R_plus distinction.
6. Mechanism evaluation modules: add discretion-identifiability, disclosure, and RRI sections.
7. Synthetic benchmark: add coverage, baseline, and misspecification evidence.
8. Empirical application: retain current testbed results and identify it explicitly as an application.
9. Robustness and sensitivity: merge existing tie/sampling checks with the new sensitivity package.
10. Decision-support recommendations: add the objective-to-design matrix and usage boundary.
11. Discussion: rewrite around institutional rule evaluation rather than entertainment analytics.
12. Limitations: replace with `manuscript/limitations_claim_control.md`.
13. Conclusion: retain only claims supported by generated outputs.

## Existing material disposition

- Merge existing data/rule and methods sections into Sections 4-5.
- Rewrite the introduction, related work, discussion, and conclusion for DSS identity.
- Move detailed prediction, parameter grids, controversial cases, and sampling diagnostics to appendices.
- Do not delete original, general, SEPS, DA, or high-tier manuscript files; construct a new DSS branch after route-specific citation review.
"""


def synthetic_validation_text(benchmark: pd.DataFrame) -> str:
    clean = benchmark.loc[(benchmark["condition"] == "rule_consistent") & (benchmark["method"] == "rule_aware_partial_identification")].iloc[0]
    noisy = benchmark.loc[(benchmark["condition"] == "outcome_noise_stress_test") & (benchmark["method"] == "rule_aware_partial_identification")].iloc[0]
    return f"""
# Synthetic Validation

The fixed-seed synthetic benchmark generates latent public preference shares, expert shares, percentage-aggregation outcomes, and coarse observed eliminations. It then hides the synthetic truth from the inference stage and evaluates whether the rule-aware feasible set covers that truth. Under rule-consistent simulated outcomes, the rule-aware feasible-set coverage rate is {clean.coverage_rate:.3f}; this is a logical-calibration result under the stated simulator. Under the intentional outcome-noise stress condition, coverage is {noisy.coverage_rate:.3f}, illustrating that incompatible or misspecified coarse outcomes can invalidate the assumed constraints.

The benchmark compares rule-aware partial identification with a simplex-only rule-agnostic set, naive judge-share point selection, a prediction-only proxy, and a full-disclosure oracle available only in simulation. It reports coverage, feasible-set width, false-certainty rate, baseline error, and outcome consistency. It does not claim that the empirical hidden preferences are recovered exactly.
"""


def baseline_text(baselines: pd.DataFrame) -> str:
    proposed = baselines.loc[baselines["method"].eq("rule_aware_partial_identification")].iloc[0]
    agnostic = baselines.loc[baselines["method"].eq("rule_agnostic_partial_identification")].iloc[0]
    point = baselines.loc[baselines["method"].eq("naive_point_estimation")].iloc[0]
    return f"""
# Baseline Comparison

In the rule-consistent synthetic benchmark, the rule-aware feasible set has coverage {proposed.coverage_rate:.3f} and mean width {proposed.average_feasible_set_width:.3f}. The rule-agnostic simplex-only set has mean width {agnostic.average_feasible_set_width:.3f}, demonstrating the information cost of omitting correctly specified institutional constraints. The naive point baseline has false-certainty rate {point.false_certainty_rate:.3f} under exact synthetic-truth matching and is not interpreted as a hidden-preference estimate.

The decision-support advantage is not a claim of a universally smaller uncertainty number. It is the preservation of rule-relevant feasible structure while avoiding false precision. Oracle results are retained solely as a synthetic full-disclosure upper benchmark.
"""


def discretion_text(frontier: pd.DataFrame, observed: pd.DataFrame) -> str:
    last = frontier.sort_values("expert_discretion_strength").iloc[-1]
    observed_ratio = observed.loc[observed["expert_discretion_strength"].eq(1), "mean_identifiability_loss_ratio"].iloc[0]
    return f"""
# Discretion-Identifiability Frontier

Expert discretion strength is defined here as the degree to which a direct bottom-set implication is relaxed in a documented rule scenario. A feasible preference set is the collection of ordinal public rankings compatible with the rule and observed outcome. Feasible-set width summarizes rank-support uncertainty, and identifiability loss is the feasible-ranking count relative to the direct condition.

The frontier figure is a deterministic synthetic ranking scenario. At its strongest modeled relaxation, normalized rank width is {last.normalized_rank_width:.3f} and the feasible-count ratio relative to the direct condition is {last.identifiability_loss_ratio_vs_direct:.3f}. This illustrates a governance tradeoff: stronger intervention can preserve modeled institutional flexibility while making collective preference less identifiable unless intervention criteria are disclosed.

The empirical record separately supports a direct-versus-weak R_plus comparison with mean weak/direct ratio {observed_ratio:.6f}. It does not identify a continuous historical discretion scale. Expert intervention is not treated as bad; the result makes its information consequence auditable under the stated rule.
"""


def disclosure_text(disclosure: pd.DataFrame) -> str:
    topk = disclosure.loc[disclosure["disclosure_regime"].eq("elimination_plus_top_k_public_rank")].iloc[0]
    full = disclosure.loc[disclosure["disclosure_regime"].eq("full_public_vote_theoretical_upper_benchmark")].iloc[0]
    return f"""
# Value of Institutional Disclosure

The disclosure module compares seven synthetic policy scenarios: elimination only; elimination plus judge ranking; top-k public rank; vote-bin intervals; pairwise majority; margin intervals; and a full-public-preference upper benchmark. All scenarios preserve the same simulated rule and latent state space. Proposition 1 implies that truthful additional constraints weakly shrink the feasible set.

In the generated scenario average, top-k public-rank disclosure reduces uncertainty by {topk.relative_uncertainty_reduction:.3f} relative to elimination only. The full-disclosure benchmark has mean feasible-set width {full.mean_feasible_set_width:.3f}, but is included only as a theoretical upper-information reference. Interpretability, cost, privacy, and accountability values in the table are predeclared design descriptors rather than measured social outcomes.

The output helps a designer identify the minimum modeled disclosure that meets a stated information objective while retaining an explicit privacy and reporting-cost warning. It does not claim that the empirical institution historically disclosed or should disclose any particular signal.
"""


def rri_text(rri: pd.DataFrame) -> str:
    return "# Rule Robustness Index\n\nRRI is the share of applicable, predeclared configurations that support a conclusion predicate. It classifies conclusions as robust at 0.95 or above, assumption-sensitive from 0.60 to below 0.95, and non-identifiable below 0.60. The index avoids pooling cardinal and ordinal widths.\n\n" + markdown_table(rri, list(rri.columns)) + "\n\nA high RRI does not prove institutional optimality. It indicates that a stated conclusion persists across the evaluated configuration family."


def robustness_text(sensitivity: pd.DataFrame) -> str:
    return "# Robustness and Sensitivity\n\n" + markdown_table(sensitivity, list(sensitivity.columns)) + "\n\nEach row is labeled by evidence type. Synthetic stress tests diagnose behavior under known assumptions; empirical rows describe existing rule/tie sensitivity; formal boundaries are not converted to artificial numerical comparisons."


def recommendations_text(recommendations: pd.DataFrame) -> str:
    return "# Decision-Support Recommendations\n\nThe recommendation layer maps an institutional objective to a conditional design action, required disclosure, expected benefit, major risk, cost, accountability implication, and non-use condition. It supports deliberation; it does not select a rule automatically or make causal claims about trust or welfare.\n\n" + markdown_table(recommendations, list(recommendations.columns))


def dss_gap_audit(gaps: pd.DataFrame) -> str:
    return "# DSS-Specific Gap Audit\n\nThe table distinguishes implemented evidence, conceptual additions, and remaining external-evaluation gaps. The workflow and recommendation materials create DSS relevance, but a deployed artifact, stakeholder study, organizational case, and completed DSS literature review remain outside the current evidence.\n\n" + markdown_table(gaps, list(gaps.columns))


def formal_audit() -> str:
    return """
# Formal Claims Audit: DSS Extension

The propositions in `manuscript/sections/formal_propositions.md` are conditional set-theoretic or non-identification claims. They are not presented as universal empirical claims. The implementation tests containment and clean-synthetic coverage; it labels discretionary continua and disclosure policies as scenarios where the empirical record does not observe them.

Before submission, authors must review each proposition against final notation, tie policy, rule encoding, and any added empirical testbed. No proposition establishes public trust, privacy benefit, or rule optimality.
"""


def readiness_report(gaps: pd.DataFrame) -> str:
    critical = int(gaps["priority"].eq("critical").sum())
    return f"""
# DSS Full-Attack Readiness Report

## Final label: DSS-conditionally-ready

## Is DSS now the primary target?

Yes as a strategic research target under the user's instruction, but not as an upload-ready destination. The manuscript now has a DSS decision problem, alternatives, criteria, conceptual workflow, synthetic calibration, baseline comparison, robustness outputs, and conditional recommendation layer.

## What changed for DSS fit?

- The frame now begins with institutional rule and disclosure choices.
- A conceptual decision-support workflow connects observed inputs to feasible-set outputs and warnings.
- New modules cover discretion, modeled disclosure, conclusion robustness, synthetic calibration, baselines, sensitivity, and recommendation criteria.
- New claim controls prohibit interpreting hidden public preferences as exact recovered quantities.

## Strongest new contributions

1. Known-truth synthetic coverage and false-certainty diagnostics.
2. Rule Robustness Index based on predeclared conclusion predicates.
3. Explicit disclosure and discretion scenarios tied to institutional decisions.
4. A reproducible recommendation matrix with non-use warnings.

## Remaining desk-reject risks

1. No deployed or user-evaluated DSS artifact exists.
2. The empirical application remains one testbed.
3. Privacy, trust, reporting cost, and accountability scores are scenario descriptors rather than stakeholder measurements.
4. DSS-specific literature review and final citation verification are incomplete.
5. Decision Support Systems scope and current requirements still require live official verification before upload.

## Remaining methodological weaknesses

- Synthetic calibration is not external validation.
- The multi-level discretion frontier is illustrative rather than a historical intervention scale.
- Disclosure policies are modeled constraints, not records of what the empirical institution released.
- A second permission-compatible external testbed would materially strengthen generalizability.

## Mandatory checks before submission

1. Complete DSS literature review, artifact framing, and decision-task justification.
2. Decide whether a real decision-support prototype and user/organizational evaluation are feasible.
3. Add external testbed replication or reduce generality claims.
4. Archive code, configurations, source terms, environment lock, and data-access route.
5. Recheck official DSS scope, article type, data/code policy, AI policy, and formatting.
6. Compile a final anonymous manuscript and complete declarations.

## Fallback path

If DSS rejects, submit the preserved Decision Analysis package or a Group Decision and Negotiation branch, with the new synthetic/robustness modules retained only after a venue-specific fit and citation review.

## Readiness basis

The new package resolves several of the {critical} previously critical DSS design gaps at the conceptual and synthetic-evaluation level. It is conditionally ready for a full DSS manuscript rewrite and further validation, not ready for immediate submission.
"""


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    require(root, [
        "outputs/tables/identification_comparison_by_regime.csv",
        "outputs/tables/ranking_identification_summary_rplus.csv",
        "outputs/tables/ranking_tie_policy_sensitivity.csv",
        "outputs/tables/uncertainty_by_week_regime_p.csv",
        "outputs/tables/frozen_outputs_hashes.csv",
    ])
    if args.synthetic_replications < 50 or args.disclosure_cases < 25:
        print("ERROR: use at least 50 synthetic replications and 25 disclosure cases.", file=sys.stderr)
        return 2
    try:
        apply_plot_style()
        tables = root / "outputs/tables"
        figures = root / "outputs/figures"
        logs = root / "outputs/logs"
        sections = root / "manuscript/sections"
        manuscript = root / "manuscript"

        identification = pd.read_csv(tables / "identification_comparison_by_regime.csv")
        rplus = pd.read_csv(tables / "ranking_identification_summary_rplus.csv")
        ties = pd.read_csv(tables / "ranking_tie_policy_sensitivity.csv")
        p_uncertainty = pd.read_csv(tables / "uncertainty_by_week_regime_p.csv")

        frontier = synthetic_discretion_frontier()
        observed = observed_rplus_summary(rplus)
        discretion = pd.concat([frontier, observed], ignore_index=True, sort=False)
        disclosure = run_value_of_disclosure(seed=args.seed, n_cases=args.disclosure_cases)
        benchmark = run_synthetic_benchmark(seed=args.seed, n_replications=args.synthetic_replications)
        baselines = build_baseline_comparison(seed=args.seed, n_replications=args.synthetic_replications)
        rri = build_rule_robustness_index(identification, ties)
        sensitivity = build_robustness_sensitivity(benchmark, disclosure, ties, p_uncertainty)
        alternatives = decision_alternatives_criteria()
        recommendations = recommendation_matrix()
        gaps = dss_gap_matrix()

        write_csv(discretion, tables / "discretion_identifiability_summary.csv")
        write_csv(disclosure, tables / "value_of_disclosure.csv")
        write_csv(rri, tables / "rule_robustness_index.csv")
        write_csv(benchmark, tables / "synthetic_coverage_results.csv")
        write_csv(baselines, tables / "baseline_comparison.csv")
        write_csv(sensitivity, tables / "robustness_sensitivity.csv")
        write_csv(alternatives, tables / "decision_alternatives_criteria.csv")
        write_csv(recommendations, tables / "design_recommendation_matrix.csv")
        write_csv(gaps, tables / "dss_gap_matrix.csv")

        plot_conceptual_framework(figures / "dss_conceptual_framework.png")
        plot_discretion_frontier(frontier, figures / "discretion_identifiability_frontier.png")
        plot_disclosure_curve(disclosure, figures / "disclosure_uncertainty_curve.png")
        plot_rri_heatmap(rri, figures / "rule_robustness_heatmap.png")
        plot_synthetic_coverage(benchmark, figures / "synthetic_benchmark_coverage.png")
        plot_baselines(baselines, figures / "baseline_comparison.png")
        plot_robustness(sensitivity, figures / "robustness_sensitivity_panel.png")
        plot_workflow(figures / "decision_support_workflow.png")

        write_text(sections / "dss_contributions.md", four_contributions())
        write_text(sections / "dss_conceptual_model.md", conceptual_model_text())
        write_text(sections / "decision_problem_formulation.md", decision_problem_text())
        write_text(sections / "discretion_identifiability_frontier.md", discretion_text(frontier, observed))
        write_text(sections / "value_of_disclosure.md", disclosure_text(disclosure))
        write_text(sections / "rule_robustness_index.md", rri_text(rri))
        write_text(sections / "synthetic_validation.md", synthetic_validation_text(benchmark))
        write_text(sections / "decision_support_recommendations.md", recommendations_text(recommendations))
        write_text(sections / "formal_propositions.md", formal_propositions_text())
        write_text(sections / "baseline_comparison.md", baseline_text(baselines))
        write_text(sections / "robustness_sensitivity.md", robustness_text(sensitivity))
        write_text(manuscript / "dss_restructure_plan.md", dss_restructure_plan())
        write_text(manuscript / "abstract_DSS_full_attack.md", dss_abstract())
        write_text(manuscript / "introduction_DSS_full_attack.md", dss_introduction())
        write_text(manuscript / "related_work_DSS_upgrade.md", related_work_text())
        write_text(manuscript / "limitations_claim_control.md", limitations_text())

        write_text(logs / "dss_gap_audit.md", dss_gap_audit(gaps))
        write_text(logs / "synthetic_benchmark_audit.md", synthetic_validation_text(benchmark) + "\n\n## Audit Boundary\n\nAll stochastic operations use fixed seed " + str(args.seed) + ".")
        write_text(logs / "formal_claims_audit.md", formal_audit())
        write_text(logs / "dss_full_attack_readiness_report.md", readiness_report(gaps))
    except (OSError, ValueError, KeyError, IndexError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("DSS full-attack package completed.")
    print(f"Synthetic benchmark rows: {len(benchmark)}")
    print(f"Disclosure scenarios: {len(disclosure)}")
    print(f"RRI conclusions: {len(rri)}")
    print("Readiness: DSS-conditionally-ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
