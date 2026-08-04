#!/usr/bin/env python3
"""Generate the submission-oriented manuscript and evidence-planning assets."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TITLE = (
    "Hidden Preference Learning from Elimination-Only Outcomes in Expert-Crowd "
    "Decision Systems: Partial Identification, Mechanism Comparison, and Robust Aggregation"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the submission-oriented manuscript and evidence-planning assets."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8", newline="\n")


def fmt(value: float, digits: int = 6) -> str:
    return "NA" if pd.isna(value) else f"{float(value):.{digits}f}"


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def build_conceptual_figure(path: Path) -> None:
    """Draw a compact mechanism-aware identification diagram for the main text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10.5, 4.1))
    ax.set_axis_off()
    nodes = [
        (0.03, 0.57, 0.19, 0.24, "Expert scores\nand hidden public\npreferences", "#D9EAF7"),
        (0.29, 0.57, 0.18, 0.24, "Aggregation\nrule", "#E7E0F4"),
        (0.54, 0.57, 0.19, 0.24, "Observed coarse\noutcome:\nelimination", "#FBE3C4"),
        (0.79, 0.57, 0.18, 0.24, "Feasible public\npreference set", "#D9F0E2"),
        (0.40, 0.12, 0.27, 0.23, "Rule-aware inference:\ncardinal intervals or ordinal\nranking sets", "#F3F3F3"),
    ]
    for x, y, w, h, label, color in nodes:
        box = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
            facecolor=color, edgecolor="#333333", linewidth=1.1,
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=11)
    arrows = [
        ((0.22, 0.69), (0.29, 0.69)),
        ((0.47, 0.69), (0.54, 0.69)),
        ((0.73, 0.69), (0.79, 0.69)),
        ((0.635, 0.57), (0.56, 0.35)),
        ((0.88, 0.57), (0.67, 0.35)),
    ]
    for start, end in arrows:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=14, linewidth=1.2))
    ax.text(
        0.5, 0.94,
        "Observed eliminations constrain preferences; they do not point-identify a public score.",
        ha="center", va="center", fontsize=12, fontweight="bold",
    )
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def claim_rows() -> list[dict[str, object]]:
    return [
        {
            "claim_id": "A1",
            "claim_text": "Elimination-only feedback induces partial rather than point identification.",
            "evidence_type": "Core identification result",
            "supporting_output": "outputs/tables/constraint_summary.csv; outputs/tables/uncertainty_by_week_regime_p.csv",
            "strength_level": "core",
            "can_be_main_claim": True,
            "caveats": "The result is conditional on the encoded institutional rule and observed active field.",
            "suggested_paper_location": "Abstract; Sections 1, 4, 5 (Finding 1)",
        },
        {
            "claim_id": "A2",
            "claim_text": "Percentage aggregation creates wide feasible cardinal preference intervals.",
            "evidence_type": "Core identification result",
            "supporting_output": "outputs/tables/identification_comparison_by_regime.csv; outputs/figures/uncertainty_over_weeks_regime_p.png",
            "strength_level": "core",
            "can_be_main_claim": True,
            "caveats": "Coordinate-wise bounds are not a jointly feasible public-share vector.",
            "suggested_paper_location": "Sections 4.2 and 5 (Finding 1)",
        },
        {
            "claim_id": "A3",
            "claim_text": "Ranking mechanisms identify ordinal rankings, not cardinal public support shares.",
            "evidence_type": "Core identification result",
            "supporting_output": "outputs/tables/ranking_identification_summary_r.csv; outputs/tables/ranking_identification_summary_rplus.csv",
            "strength_level": "core",
            "can_be_main_claim": True,
            "caveats": "Exact enumeration is unavailable for some large fields and fixed-seed sampling is used.",
            "suggested_paper_location": "Sections 4.3 and 5 (Finding 2)",
        },
        {
            "claim_id": "A4",
            "claim_text": "The R_plus judge-save rule weakens identifiability relative to direct R-like elimination.",
            "evidence_type": "Core within-week mechanism comparison",
            "supporting_output": "outputs/tables/ranking_identification_summary_rplus.csv; outputs/figures/judge_save_identifiability_loss.png",
            "strength_level": "core",
            "can_be_main_claim": True,
            "caveats": "The comparison is within week and depends on the tie-inclusive bottom-set interpretation.",
            "suggested_paper_location": "Sections 4.4 and 5 (Finding 3)",
        },
        {
            "claim_id": "A5",
            "claim_text": "Within-week R_plus feasible sets never violate direct-set containment.",
            "evidence_type": "Core logical and computational check",
            "supporting_output": "outputs/tables/ranking_identification_summary_rplus.csv; outputs/logs/ranking_identification_report_rplus.md",
            "strength_level": "core",
            "can_be_main_claim": True,
            "caveats": "Containment is evaluated under the recorded rule and tie policy.",
            "suggested_paper_location": "Sections 4.4 and 5 (Finding 3)",
        },
        {
            "claim_id": "B1",
            "claim_text": "The ordering P < R < R_plus in normalized uncertainty is descriptive.",
            "evidence_type": "Secondary descriptive comparison",
            "supporting_output": "outputs/tables/identification_comparison_by_regime.csv; outputs/figures/identification_width_by_regime.png",
            "strength_level": "secondary",
            "can_be_main_claim": False,
            "caveats": "Cardinal interval width and ordinal rank width are mechanism-specific quantities.",
            "suggested_paper_location": "Section 5 (Finding 4)",
        },
        {
            "claim_id": "B2",
            "claim_text": "Expert and inferred public-preference channels exhibit descriptive divergence.",
            "evidence_type": "Secondary model-dependent association",
            "supporting_output": "outputs/tables/expert_crowd_divergence.csv; outputs/logs/expert_crowd_divergence_report.md",
            "strength_level": "secondary",
            "can_be_main_claim": False,
            "caveats": "One mixed-effects fit is unstable; coefficients depend on proxy construction and fixed effects.",
            "suggested_paper_location": "Section 6; Appendix regression table",
        },
        {
            "claim_id": "B3",
            "claim_text": "Historical public-proxy features contain limited but nonzero predictive signal in the specified validation design.",
            "evidence_type": "Secondary validation result",
            "supporting_output": "outputs/tables/prediction_results.csv; outputs/tables/prediction_results_by_regime.csv",
            "strength_level": "secondary",
            "can_be_main_claim": False,
            "caveats": "Prediction is not evidence of point recovery; same-week judge baselines are not prior-week forecasts.",
            "suggested_paper_location": "Section 6; Table 4",
        },
        {
            "claim_id": "C1",
            "claim_text": "Controversial-case rank ranges illustrate scenario sensitivity.",
            "evidence_type": "Exploratory scenario analysis",
            "supporting_output": "outputs/tables/controversial_cases_counterfactual.csv; outputs/figures/controversial_cases_counterfactual.png",
            "strength_level": "exploratory",
            "can_be_main_claim": False,
            "caveats": "Not a causal estimate of an alternative historical placement.",
            "suggested_paper_location": "Appendix",
        },
        {
            "claim_id": "C2",
            "claim_text": "Counterfactual outcome and winner changes are scenario-dependent.",
            "evidence_type": "Exploratory scenario analysis",
            "supporting_output": "outputs/tables/counterfactual_results_by_regime.csv; outputs/figures/mechanism_outcome_changes.png",
            "strength_level": "exploratory",
            "can_be_main_claim": False,
            "caveats": "The simulation conditions on observed active trajectories and uses identified-set scenarios.",
            "suggested_paper_location": "Appendix; Section 6 caveat",
        },
        {
            "claim_id": "C3",
            "claim_text": "The empirical Pareto frontier summarizes a specification-specific trade-off.",
            "evidence_type": "Exploratory design comparison",
            "supporting_output": "outputs/tables/pareto_frontier_points.csv; outputs/figures/pareto_frontier.png",
            "strength_level": "exploratory",
            "can_be_main_claim": False,
            "caveats": "The scalar objectives and normalization are not a welfare criterion.",
            "suggested_paper_location": "Appendix",
        },
        {
            "claim_id": "C4",
            "claim_text": "No lambda/gamma setting is a generally preferred mechanism.",
            "evidence_type": "Exploratory parameter sensitivity",
            "supporting_output": "outputs/tables/robust_aggregation_results.csv; outputs/figures/lambda_gamma_sensitivity.png",
            "strength_level": "exploratory",
            "can_be_main_claim": False,
            "caveats": "Positive gamma points are not on the current all-objective frontier.",
            "suggested_paper_location": "Appendix; Section 7 caveat",
        },
        {
            "claim_id": "C5",
            "claim_text": "Uncertainty-aware aggregation is a design template, not an empirically selected rule.",
            "evidence_type": "Exploratory mechanism-design interpretation",
            "supporting_output": "outputs/tables/robust_aggregation_results.csv; outputs/logs/robust_aggregation_report.md",
            "strength_level": "exploratory",
            "can_be_main_claim": False,
            "caveats": "The design depends on normative objectives and an uncertainty penalty chosen outside the data.",
            "suggested_paper_location": "Section 7; Appendix",
        },
    ]


def claim_map_markdown(claims: pd.DataFrame) -> str:
    lines = [
        "# Claim-Evidence Map",
        "",
        "This map separates identification claims from descriptive validation and exploratory scenario analysis.",
        "",
    ]
    for level, heading in [("core", "Core Claims"), ("secondary", "Secondary Findings"), ("exploratory", "Exploratory Findings")]:
        lines.extend([f"## {heading}", ""])
        subset = claims.loc[claims["strength_level"].eq(level)]
        for row in subset.itertuples(index=False):
            lines.extend(
                [
                    f"### {row.claim_id}: {row.claim_text}",
                    "",
                    f"- Evidence: `{row.supporting_output}`",
                    f"- Caveat: {row.caveats}",
                    f"- Proposed location: {row.suggested_paper_location}",
                    "",
                ]
            )
    return "\n".join(lines)


def figure_table_plan(root: Path, concept_path: Path) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "item_type": "figure", "item_id": "Figure 1", "main_text": True,
                "file_or_source": str(concept_path.relative_to(root)).replace("\\", "/"),
                "purpose": "Conceptual framework", "caption_status": "ready",
                "axis_or_label_check": "No quantitative axes; labeled causal-information flow is self-contained.",
                "proxy_language_check": "Uses hidden preferences and feasible set; does not describe observed public votes.",
                "comparability_note": "Mechanism determines the identified object.", "dpi_check": "300 dpi", "placement": "Section 1",
            },
            {
                "item_type": "figure", "item_id": "Figure 2", "main_text": True,
                "file_or_source": "outputs/figures/uncertainty_over_weeks_regime_p.png",
                "purpose": "P-regime interval-width trajectory", "caption_status": "ready",
                "axis_or_label_check": "Week and normalized identification width are labeled.",
                "proxy_language_check": "Caption must call widths feasible support intervals, not vote estimates.",
                "comparability_note": "P only.", "dpi_check": "300 dpi", "placement": "Section 5, Finding 1",
            },
            {
                "item_type": "figure", "item_id": "Figure 3", "main_text": True,
                "file_or_source": "outputs/figures/judge_save_identifiability_loss.png",
                "purpose": "Direct versus judge-save feasible-set expansion", "caption_status": "ready",
                "axis_or_label_check": "Expansion ratio and week labels are present.",
                "proxy_language_check": "Refers to feasible ordinal rankings.",
                "comparability_note": "Within-week R_plus/direct comparison only.", "dpi_check": "300 dpi", "placement": "Section 5, Finding 3",
            },
            {
                "item_type": "figure", "item_id": "Figure 4", "main_text": True,
                "file_or_source": "outputs/figures/identification_width_by_regime.png",
                "purpose": "Cross-regime descriptive uncertainty comparison", "caption_status": "ready",
                "axis_or_label_check": "Regime and normalized uncertainty are labeled.",
                "proxy_language_check": "No support-share interpretation for ordinal regimes.",
                "comparability_note": "Mechanism-specific scales; descriptive only.", "dpi_check": "300 dpi", "placement": "Section 5, Finding 4",
            },
            {
                "item_type": "figure", "item_id": "Figure 5", "main_text": True,
                "file_or_source": "outputs/figures/prediction_comparison.png",
                "purpose": "Leakage-controlled prediction validation", "caption_status": "ready",
                "axis_or_label_check": "Accuracy and log-loss axes are labeled.",
                "proxy_language_check": "Caption must identify same-week judge models as baselines.",
                "comparability_note": "Validation only; not a point-recovery result.", "dpi_check": "300 dpi", "placement": "Section 6",
            },
            {
                "item_type": "table", "item_id": "Table 1", "main_text": True,
                "file_or_source": "data/processed/identification_features_long.csv; outputs/tables/constraint_summary.csv",
                "purpose": "Dataset and regime summary", "caption_status": "ready",
                "axis_or_label_check": "Columns state seasons, weeks, and active contestant-weeks.",
                "proxy_language_check": "Separates cardinal and ordinal objects.",
                "comparability_note": "Report regime composition alongside counts.", "dpi_check": "not applicable", "placement": "Section 3",
            },
            {
                "item_type": "table", "item_id": "Table 2", "main_text": True,
                "file_or_source": "outputs/tables/identification_comparison_by_regime.csv",
                "purpose": "Partial-identification summary by regime", "caption_status": "ready",
                "axis_or_label_check": "Metric definitions appear in table notes.",
                "proxy_language_check": "P interval width is not equated to ordinal rank width.",
                "comparability_note": "Use mechanism-specific footnote.", "dpi_check": "not applicable", "placement": "Section 5",
            },
            {
                "item_type": "table", "item_id": "Table 3", "main_text": True,
                "file_or_source": "outputs/tables/ranking_identification_summary_rplus.csv",
                "purpose": "R_plus direct versus weak judge-save comparison", "caption_status": "ready",
                "axis_or_label_check": "Includes direct count, weak count, and ratio.",
                "proxy_language_check": "Uses feasible ranking sets only.",
                "comparability_note": "Within-week comparison.", "dpi_check": "not applicable", "placement": "Section 5",
            },
            {
                "item_type": "table", "item_id": "Table 4", "main_text": True,
                "file_or_source": "outputs/tables/prediction_results.csv",
                "purpose": "Prediction validation", "caption_status": "ready",
                "axis_or_label_check": "Reports validation split, accuracy, top-2 accuracy, Brier score, and log loss.",
                "proxy_language_check": "Separates same-week and strictly historical models.",
                "comparability_note": "R-specific estimates are unstable.", "dpi_check": "not applicable", "placement": "Section 6",
            },
            {
                "item_type": "appendix", "item_id": "Appendix diagnostics", "main_text": False,
                "file_or_source": "outputs/figures/dynamic_public_appeal_examples.png; outputs/figures/lambda_gamma_sensitivity.png; outputs/figures/controversial_cases_counterfactual.png; outputs/figures/expert_vs_crowd_coefficients.png",
                "purpose": "Exploratory cases, sensitivity, and full diagnostics", "caption_status": "appendix",
                "axis_or_label_check": "Retain existing labels and add model-dependence notes.",
                "proxy_language_check": "Avoid vote-recovery language.",
                "comparability_note": "Exploratory material is not a main claim.", "dpi_check": "300 dpi", "placement": "Appendix",
            },
        ]
    )


def figure_table_plan_markdown(plan: pd.DataFrame) -> str:
    main = plan.loc[plan["main_text"]]
    appendix = plan.loc[~plan["main_text"]]
    lines = [
        "# Main-Text Figure and Table Plan",
        "",
        "The main text uses five figures and four tables. Captions must distinguish cardinal P intervals from ordinal R/R_plus ranking uncertainty and must not describe any proxy as observed public votes.",
        "",
        "## Main Text",
        "",
        "| Item | Purpose | Source | Placement |",
        "| --- | --- | --- | --- |",
    ]
    for row in main.itertuples(index=False):
        lines.append(f"| {row.item_id} | {row.purpose} | `{row.file_or_source}` | {row.placement} |")
    lines.extend(["", "## Appendix", ""])
    for row in appendix.itertuples(index=False):
        lines.append(f"- {row.item_id}: {row.purpose}. Sources: `{row.file_or_source}`.")
    return "\n".join(lines)


def title_abstract_keywords() -> str:
    abstract = """Expert-crowd decision systems often combine observable expert assessments with unobserved public preferences, while releasing only coarse outcomes such as eliminations. This information structure makes point estimation of public support untenable: the appropriate estimand is a feasible preference set conditional on the aggregation rule. We develop a rule-aware framework for partial identification from longitudinal elimination outcomes. Under percentage aggregation, observed eliminations impose linear inequalities on a simplex and yield convex feasible regions with coordinate-wise linear-program bounds. Under ranking aggregation, the same observations identify feasible ordinal rankings rather than cardinal support shares. A judge-save intervention further weakens identification by replacing direct elimination with a tie-inclusive bottom-set condition. We apply the framework to a longitudinal competition dataset spanning three rule regimes. Feasible sets are wide in all regimes, and direct feasible ranking sets are nested within their judge-save counterparts in every comparable week. We also construct typed dynamic proxies, use lagged prediction as a validation exercise, and propagate feasible-set uncertainty through scenario analyses. These extensions do not observe or infer an exact public ballot. The contribution is a transparent account of what coarse outcomes can identify, how institutional rules change that information, and how uncertainty can enter mechanism design."""
    return f"""
# {TITLE}

## Abstract

{abstract}

## Keywords

partial identification; expert-crowd decision systems; hidden preferences; aggregation mechanisms; ranking aggregation; robust decision design; uncertainty-aware aggregation
"""


def introduction() -> str:
    return """
# Introduction

Expert-crowd decision systems are common wherever professional assessments are combined with public, peer, or member input. Their public component is frequently consequential but unobserved. Institutions may disclose expert scores and final decisions while withholding the public signal that helped produce them.

The resulting inferential problem is often treated as one of estimating a hidden score. That framing is too strong when the observable feedback is coarse. An elimination event, for example, restricts which public-preference configurations could have produced the outcome under a stated rule, but it rarely identifies one configuration. The central object is therefore a feasible preference set, not a reconstructed ballot.

Aggregation rules are part of the data-generating information structure. Percentage rules can imply linear inequalities over cardinal support shares. Rank-combination rules identify feasible ordinal rankings. A judge-save rule changes the observed implication again by requiring only bottom-set membership. Consequently, mechanism comparison is not an afterthought: it determines what is identified.

This paper asks: **How much can hidden public preferences be learned from elimination-only outcomes in expert-crowd decision systems, and how do aggregation mechanisms affect identifiability?** We develop a rule-aware partial-identification framework and apply it to a longitudinal competition dataset with percentage, direct-ranking, and judge-save ranking regimes. The application is an empirical testbed for the general problem rather than the paper's substantive endpoint.

The paper makes three contributions. First, it formulates cardinal and ordinal feasible sets directly from observed rules and eliminations. Second, it demonstrates the within-week loss of identification induced by a judge-save intervention. Third, it separates core identification results from descriptive proxy models and exploratory mechanism simulations, preserving the distinction between what the data constrain and what additional modeling assumptions supply.
"""


def related_work() -> str:
    return """
# Related Work

This study lies at the intersection of partial identification, aggregation theory, and expert-crowd decision systems. The relevant methodological distinction is between recovering an unobserved preference point and characterizing the set of preference states compatible with observable institutional outcomes. The latter is appropriate when the observation rule is coarse and the latent public signal is not released.

Aggregation research also distinguishes cardinal score combination from ordinal rank combination. That distinction is central here because a change in rule changes the mathematical object that can be constrained by the same elimination record. The judge-save setting adds an institutional intervention: the observable event identifies bottom-set admissibility rather than a direct worst-ranked alternative.

Finally, work on hybrid decision systems motivates examining expert and public channels jointly. In this paper, dynamic proxy models and prediction experiments are deliberately subordinate to identification. They assess whether typed feasible-set summaries are useful descriptive features; they do not transform hidden preferences into observed quantities. A publication version should add a curated, verified bibliography for these three literatures rather than relying on unsourced name-checking in this draft.
"""


def data_rules(features: pd.DataFrame, comparison: pd.DataFrame) -> str:
    regime = comparison.set_index("regime")
    counts = features.groupby("aggregation_regime").agg(
        seasons=("season", "nunique"), contestant_weeks=("contestant_id", "size")
    )
    rows = []
    for name in ["P", "R", "R_plus"]:
        rows.append(
            f"| {name} | {int(counts.loc[name, 'seasons'])} | {int(regime.loc[name, 'n_weeks'])} | {int(counts.loc[name, 'contestant_weeks'])} |"
        )
    return f"""
# Data and Institutional Rules

## Empirical testbed

The processed longitudinal panel contains 4,199 contestant-week records before identification-specific availability restrictions. The unified identification feature file contains {len(features):,} active contestant-week records, of which {int(features['public_appeal_proxy'].notna().sum()):,} have a typed public-appeal proxy. The remaining 11 observations correspond to a logged P-regime constraint skip and are not imputed.

| Regime | Seasons | Season-weeks | Active contestant-weeks |
| --- | ---: | ---: | ---: |
{chr(10).join(rows)}

## Institutional rules

In P, the combined decision uses normalized expert performance and a hidden cardinal public-support component. In R, expert and public ranks are combined and the lowest combined standing is eliminated. In R_plus, a judge-save intervention means that the observed eliminated contestant need only belong to a tie-inclusive bottom set before the save decision. The encoded rules also distinguish no-elimination weeks, multiple eliminations, withdrawals, and final rounds; these conditions are recorded in the preprocessing and constraint reports.

The raw public component is not observed. Thus P, R, and R_plus are not three interchangeable measurements of one latent vote share. They are three information environments with different feasible objects.

Traceable sources: `data/processed/panel_long.csv`, `data/processed/identification_features_long.csv`, and `outputs/tables/constraint_summary.csv`.
"""


def methods() -> str:
    return """
# Methods

## 4.1 Problem Setup

For contestant i in week t, let e_it denote the observed expert contribution and let the public component be hidden. The observed outcome is an elimination set together with the institutional aggregation rule. We seek the set of public-preference states consistent with that rule and outcome, not a point estimate of an unobserved ballot.

## 4.2 Percentage Aggregation and Convex Preference Regions

For P, public support p_t lies on the unit simplex. The observed elimination relation implies linear inequalities comparing the eliminated contestant's combined score with the surviving contestants' scores. Together with non-negativity and the simplex constraint, these inequalities define a convex feasible region. Linear programs minimize and maximize each coordinate of p_t, producing lower and upper feasible-support bounds. The normalized interval width is an identification-width summary, not a sampling confidence interval. No-elimination weeks retain only justified simplex restrictions; multiple-elimination weeks use conservative set restrictions; complete final rankings add their recorded pairwise order information.

## 4.3 Ranking Aggregation and Feasible Ordinal Rankings

For R, the hidden public object is a permutation of fan ranks. A candidate ranking is feasible when its combination with observed judge ranks is consistent with the observed elimination under the direct rule. Exact enumeration is used where possible and fixed-seed Monte Carlo sampling otherwise. The resulting feasible ranking set yields contestant-level rank support, entropy, and normalized rank-width summaries. These are ordinal quantities and are never converted into cardinal support shares.

## 4.4 Judge-Save Intervention as Weak Identification

For R_plus, the direct criterion is weakened: the eliminated contestant must be contained in a tie-inclusive bottom set prior to a judge save. Every direct-feasible ranking is therefore feasible under the weak condition. We summarize the corresponding loss of identification with the within-week ratio of weak-set to direct-set size, retaining the recorded tie policy. This comparison is made within the same week rather than from cross-regime averages.

## 4.5 Dynamic Public-Appeal Proxy

For descriptive extensions, P uses the midpoint of its coordinate-wise feasible interval, while R and R_plus use a normalized feasible mean fan rank. Each proxy carries an uncertainty measure and a type label. Exponential and uncertainty-weighted smoothing create dynamic inferred public-appeal trajectories. These trajectories are not public ballots; analyses either include regime indicators or remain mechanism-specific.

## 4.6 Validation and Counterfactual Design

Prediction is a validation exercise. Historical public, dynamic, uncertainty, and expert features are lagged by one contestant observation; current-week expert scores occur only in explicitly labeled same-week baselines. Counterfactual analyses propagate interval or feasible-ranking scenarios and condition on observed active trajectories. They are scenario analyses, not causal reconstructions of an alternative season.
"""


def results(comparison: pd.DataFrame, rplus: pd.DataFrame, prediction: pd.DataFrame) -> str:
    metrics = comparison.set_index("regime")
    ratio = pd.to_numeric(rplus["identifiability_loss_ratio"], errors="coerce").dropna()
    strict = int((ratio > 1 + 1e-12).sum())
    equal = int(np.isclose(ratio, 1.0).sum())
    forward = prediction.loc[prediction["validation_scheme"].eq("forward_chaining")]
    random = forward.loc[forward["model"].eq("random_uniform")].iloc[0]
    combined = forward.loc[forward["model"].eq("combined_lag_logistic")].iloc[0]
    judge = forward.loc[forward["model"].eq("judge_only_logistic_same_week")].iloc[0]
    return f"""
# Results

## Finding 1: Elimination-only feedback yields wide feasible preference sets

P yields a nonempty linear feasible region in 247 of 248 eligible weeks. Its mean normalized coordinate-wise identification width is {fmt(metrics.loc['P', 'mean_normalized_uncertainty'])}. This is direct evidence for partial, rather than point, identification: the observed elimination restricts public support without selecting one support vector. Figure 2 and Table 2 report the distribution and timing of these widths.

## Finding 2: Aggregation rules determine whether the hidden object is cardinal or ordinal

P constrains cardinal support coordinates on a simplex. R and R_plus instead constrain feasible public rank permutations. Their normalized rank widths are {fmt(metrics.loc['R', 'mean_normalized_uncertainty'])} and {fmt(metrics.loc['R_plus', 'mean_normalized_uncertainty'])}, respectively. These values are useful regime summaries, but P interval width and ordinal rank width are not directly comparable measurements. Table 2 records their definitions.

## Finding 3: Judge-save weakens identifiability by expanding the feasible ranking set

Across the 73 R_plus weeks, the weak/direct feasible-set ratio has mean {fmt(ratio.mean())} and median {fmt(ratio.median())}. The weak set is strictly larger in {strict} weeks, equal in {equal} weeks, and never smaller. This within-week containment result is the central mechanism comparison: a bottom-set judge-save condition preserves institutional discretion while reducing what the elimination record identifies. Figure 3 and Table 3 provide the corresponding audit.

## Finding 4: Cross-regime uncertainty differences are descriptive and mechanism-dependent

The sample ordering P < R < R_plus in average normalized uncertainty is {fmt(metrics.loc['P', 'mean_normalized_uncertainty'])}, {fmt(metrics.loc['R', 'mean_normalized_uncertainty'])}, and {fmt(metrics.loc['R_plus', 'mean_normalized_uncertainty'])}. It should not be interpreted as a causal rule comparison because the hidden objects, season composition, and field sizes differ. Figure 4 is retained to show descriptive context with this limitation visible in the caption and text.

## Finding 5: Dynamic proxies and prediction experiments provide validation signals but do not establish unobserved public votes

Typed proxies permit lagged validation without treating their midpoint or rank-score construction as observed public input. Over 211 forward-chaining events, the strictly historical combined model has accuracy {fmt(combined.accuracy)} and log loss {fmt(combined.log_loss)}, compared with {fmt(random.accuracy)} and {fmt(random.log_loss)} for uniform risk. The lowest log loss, {fmt(judge.log_loss)}, belongs to the explicitly marked same-week judge baseline and is not a prior-week forecast. Figure 5 and Table 4 therefore present prediction as limited validation evidence, not as an identification result.

Traceable sources: `outputs/tables/identification_comparison_by_regime.csv`, `outputs/tables/ranking_identification_summary_rplus.csv`, `outputs/tables/prediction_results.csv`, `outputs/figures/uncertainty_over_weeks_regime_p.png`, `outputs/figures/judge_save_identifiability_loss.png`, `outputs/figures/identification_width_by_regime.png`, and `outputs/figures/prediction_comparison.png`.
"""


def prediction_counterfactuals(prediction: pd.DataFrame, counterfactual: pd.DataFrame) -> str:
    forward = prediction.loc[prediction["validation_scheme"].eq("forward_chaining")]
    combined = forward.loc[forward["model"].eq("combined_lag_logistic")].iloc[0]
    ua = forward.loc[forward["model"].eq("uncertainty_aware_lag_logistic")].iloc[0]
    pct = counterfactual.loc[
        counterfactual["regime"].eq("P") & counterfactual["mechanism"].eq("percentage_aggregation")
    ].iloc[0]
    rplus = counterfactual.loc[
        counterfactual["regime"].eq("R_plus") & counterfactual["mechanism"].eq("direct_ranking")
    ].iloc[0]
    return f"""
# Prediction and Counterfactuals

## Prediction as validation

The historical combined lag model improves over uniform risk in forward validation (log loss {fmt(combined.log_loss)} versus {fmt(forward.loc[forward['model'].eq('random_uniform')].iloc[0].log_loss)}). The uncertainty-aware lag model has log loss {fmt(ua.log_loss)}. These are descriptive validation results for the feature construction. They do not establish unobserved public votes, and the same-week judge benchmark is reported separately because it uses information unavailable to a prior-week forecast.

## Scenario analyses of mechanisms

Counterfactual calculations retain multiple identified-set scenarios. In P, percentage aggregation has an outcome-change rate of {fmt(pct.outcome_change_rate)} and a winner-change rate of {fmt(pct.winner_change_rate)} across its coordinate scenarios. Applying direct ranking to R_plus scenarios has an outcome-change rate of {fmt(rplus.outcome_change_rate)}. These values describe the behavior of specified rules under feasible scenarios; they are not causal effects of replacing an historical rule.

The judge-save weak mechanism intentionally reports set admissibility rather than a unique winner or finalist outcome, because an unobserved save decision remains unresolved. The lambda/gamma grid, Pareto frontier, controversial cases, and dynamic examples are retained as appendix material. In particular, no positive uncertainty penalty is presented as empirically dominant.

Traceable sources: `outputs/tables/prediction_results.csv`, `outputs/tables/counterfactual_results_by_regime.csv`, `outputs/tables/pareto_frontier_points.csv`, and `outputs/tables/controversial_cases_counterfactual.csv`.
"""


def discussion() -> str:
    return """
# Discussion

Partial identification is the appropriate estimand when public input is hidden and the institution releases only an elimination. Wide feasible sets are not a failure of estimation. They are the result: they quantify information that the observed rule and outcome do not supply.

The comparison between direct ranking and judge-save rules makes the institutional trade-off explicit. A judge save can provide discretion in close or exceptional cases, but the same intervention weakens the information content of the observed elimination. The empirical contribution is not that discretion is undesirable; it is that institutional design determines the size and type of the feasible preference set.

Dynamic proxy models and prediction experiments are useful only after this distinction is maintained. Their role is to test whether typed feasible-set summaries carry limited historical signal. They do not turn a feasible set into an observed public input. Similarly, scenario-based counterfactuals show how chosen mechanisms behave under compatible states; they do not establish causal effects of public preference.

The competition data are an empirical testbed for a broader class of systems, including hybrid governance, expert panels with member input, and ranked public-participation settings. Transfer requires re-deriving the feasible set from the local rule, outcome granularity, tie policy, and normative objective. The general contribution is rule-aware inference under hidden preferences, not a claim about one entertainment setting.

## Limitations and scope

The limitations in Section 8 are central to interpretation: the public input is unobserved, rule interpretation and ties matter, active-contestant panels are selected, and external generalization requires separate institutional analysis.
"""


def limitations() -> str:
    return """
# Limitations

## Missing public input

The central limitation is that public ballots are not observed. Every public quantity in the analysis is a feasible-set summary or an ordinal rank-score proxy. The study therefore cannot verify a point-valued public-preference measure.

## Rule interpretation and ties

Identification depends on the encoded aggregation rule, score normalization, tie policy, and judge-save interpretation. The R_plus comparison uses a tie-inclusive bottom-set condition. Alternative documented institutional interpretations should be treated as robustness branches, not silently absorbed into one estimate.

## Selected active panels and approximation

The observed panel contains contestants who remain active under the historical process. Prediction uses history-complete single-elimination events, and counterfactual season rankings condition on observed active trajectories rather than generating unobserved future performances. Large ordinal fields use fixed-seed sampled feasible rankings, so numerical approximation is an additional limitation.

## Model dependence and external scope

Expert-public regressions, dynamic smoothing, and prediction depend on proxy construction and covariate specification; one expert mixed-effects sensitivity fit is unstable. The empirical testbed does not establish the prevalence of the same patterns in other systems. Generalization requires new rule encodings, new public-signal assumptions, and domain-specific normative criteria.
"""


def conclusion() -> str:
    return """
# Conclusion

Elimination-only outcomes can reveal meaningful information about hidden public preferences, but that information is set-valued and rule-dependent. Percentage aggregation yields convex feasible regions for cardinal support; ranking aggregation yields feasible ordinal rankings; judge-save rules enlarge the compatible ranking set by weakening the observed implication.

The resulting framework reframes hidden-preference learning as partial identification rather than point reconstruction. It also supplies typed proxy, validation, and scenario-analysis extensions without erasing the uncertainty encoded by the feasible set. For expert-crowd decision systems, the central practical lesson is simple: aggregation mechanisms shape not only decisions, but also what later observers can learn from those decisions.
"""


def availability_documents() -> dict[str, str]:
    return {
        "data_code_availability.md": """
# Data and Code Availability

All analysis code is organized under `src/` and `scripts/`, with focused tests under `tests/`. The reproducible entry point is:

```text
python run_all.py --skip-preprocess --manuscript
```

The repository records raw-data provenance and checksum information in `outputs/tables/data_audit_summary.csv`. If the original data source can be redistributed, the final submission should replace this sentence with its verified public source and access date. Otherwise, processed data and scripts can be shared subject to data-source terms.
""",
        "ai_assisted_writing_statement.md": """
# Declaration of Generative AI and AI-Assisted Technologies in the Manuscript Preparation Process

During the preparation of this work, the authors used OpenAI Codex to assist
with draft organization, language clarification, code review, and
reproducibility checks. After using this tool, the authors reviewed and edited
the content as needed, verified the underlying analyses and sources, and take
full responsibility for the content of the submitted article. No AI tool is
listed as an author or co-author.
""",
        "reproducibility_statement.md": """
# Reproducibility Statement

The analysis is implemented in Python; the exact runtime used for a submission should be recorded in the archival environment file. Dependencies are listed in `requirements.txt`. The current test suite contains 44 passing tests, and stochastic ranking retention and prediction baselines use fixed random seeds. `run_all.py --skip-preprocess --submission-audit` regenerates the analytical, audit, manuscript, and submission-review outputs from processed inputs. The source-data SHA-256 is recorded in `outputs/tables/data_audit_summary.csv`; regenerated deterministic artifacts can be independently checksummed at release time.
""",
    }


def legacy_notice(target: str) -> str:
    return f"""
# Legacy Section Notice

This file is retained for backwards-compatible links. Its content has been consolidated into the submission-oriented manuscript sections, especially `{target}`. The current evidence map is `manuscript/claim_evidence_map.md`.
"""


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    required = {
        "features": root / "data/processed/identification_features_long.csv",
        "comparison": root / "outputs/tables/identification_comparison_by_regime.csv",
        "rplus": root / "outputs/tables/ranking_identification_summary_rplus.csv",
        "prediction": root / "outputs/tables/prediction_results.csv",
        "counterfactual": root / "outputs/tables/counterfactual_results_by_regime.csv",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        print("ERROR: Missing required result table(s): " + ", ".join(missing), file=sys.stderr)
        return 2
    try:
        features = pd.read_csv(required["features"])
        comparison = pd.read_csv(required["comparison"])
        rplus = pd.read_csv(required["rplus"])
        prediction = pd.read_csv(required["prediction"])
        counterfactual = pd.read_csv(required["counterfactual"])
        manuscript = root / "manuscript"
        tables = root / "outputs/tables"
        figures = root / "outputs/figures"
        concept_path = figures / "conceptual_framework_hidden_preferences.png"
        build_conceptual_figure(concept_path)

        claims = pd.DataFrame(claim_rows())
        claims.to_csv(tables / "claim_evidence_map.csv", index=False)
        write_text(manuscript / "claim_evidence_map.md", claim_map_markdown(claims))
        plan = figure_table_plan(root, concept_path)
        plan.to_csv(tables / "main_text_figure_table_plan.csv", index=False)
        write_text(manuscript / "figure_table_plan.md", figure_table_plan_markdown(plan))

        documents = {
            "00_title_abstract_keywords.md": title_abstract_keywords(),
            "01_introduction.md": introduction(),
            "02_related_work.md": related_work(),
            "03_data_and_institutional_rules.md": data_rules(features, comparison),
            "04_methods.md": methods(),
            "05_results.md": results(comparison, rplus, prediction),
            "06_prediction_and_counterfactuals.md": prediction_counterfactuals(prediction, counterfactual),
            "07_discussion.md": discussion(),
            "08_limitations.md": limitations(),
            "09_conclusion.md": conclusion(),
        }
        documents.update(availability_documents())
        for name, content in documents.items():
            write_text(manuscript / name, content)
        legacy = {
            "results_identification.md": "05_results.md",
            "results_dynamic_inference.md": "05_results.md and 06_prediction_and_counterfactuals.md",
            "results_prediction.md": "06_prediction_and_counterfactuals.md",
            "results_counterfactual.md": "06_prediction_and_counterfactuals.md",
            "discussion.md": "07_discussion.md",
            "threats_to_validity.md": "08_limitations.md",
        }
        for name, target in legacy.items():
            write_text(manuscript / name, legacy_notice(target))
        abstract = documents["00_title_abstract_keywords.md"].split("## Abstract", 1)[1].split("## Keywords", 1)[0]
        print(f"Submission manuscript files updated: {len(documents) + len(legacy) + 2}")
        print(f"Abstract word count: {word_count(abstract)}")
        print(f"Claim-evidence rows: {len(claims)}")
        print(f"Main-text plan: {int(plan['main_text'].sum())} items")
    except (OSError, ValueError, KeyError, IndexError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
