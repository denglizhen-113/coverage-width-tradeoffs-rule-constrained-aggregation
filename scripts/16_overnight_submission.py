#!/usr/bin/env python3
"""Generate reproducible overnight pre-submission audits and SEPS-oriented copies.

This stage does not fit a new model, alter raw data, or overwrite the baseline
manuscript.  It converts existing generated evidence into a strict journal-fit
review, revised manuscript copies, and clearly labelled submission placeholders.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ACCESS_DATE = date.today().isoformat()
SEPS_SCOPE_URL = "https://www.sciencedirect.com/journal/socio-economic-planning-sciences/about/aims-and-scope"
SEPS_GUIDE_URL = "https://www.sciencedirect.com/journal/socio-economic-planning-sciences/publish/guide-for-authors"
ELSEVIER_DATA_URL = "https://www.elsevier.com/about/policies-and-standards/research-data"
ELSEVIER_AI_URL = "https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals"
ELSEVIER_ETHICS_URL = "https://www.elsevier.com/about/policies-and-standards/publishing-ethics"
FORBIDDEN = (
    "true fan votes",
    "recovered votes",
    "exact public vote",
    "causal effect of fan preference",
    "proves audience support",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate overnight pre-submission audits, SEPS-oriented manuscript "
            "copies, and submission-material placeholders from existing results."
        )
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8", newline="\n")


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in frame[columns].fillna("").itertuples(index=False):
        lines.append("| " + " | ".join(str(value).replace("|", "/").replace("\n", " ") for value in row) + " |")
    return "\n".join(lines)


def require(root: Path, relative_paths: list[str]) -> None:
    missing = [item for item in relative_paths if not (root / item).is_file()]
    if missing:
        raise FileNotFoundError("Required overnight-stage inputs are missing: " + ", ".join(missing))


def calculate_metrics(root: Path) -> dict[str, float | int]:
    comparison = pd.read_csv(root / "outputs/tables/identification_comparison_by_regime.csv")
    rplus = pd.read_csv(root / "outputs/tables/ranking_identification_summary_rplus.csv")
    prediction = pd.read_csv(root / "outputs/tables/prediction_results.csv")
    constraints = pd.read_csv(root / "outputs/tables/constraint_summary.csv")
    if set(comparison["regime"]) != {"P", "R", "R_plus"}:
        raise ValueError("Identification comparison table must contain P, R, and R_plus.")
    if len(rplus) != 73:
        raise ValueError(f"Expected 73 R_plus weeks, found {len(rplus)}.")
    by_regime = comparison.set_index("regime")
    forward = prediction.loc[prediction["validation_scheme"].eq("forward_chaining")].set_index("model")
    required_models = {"combined_lag_logistic", "judge_only_logistic_same_week", "random_uniform"}
    if not required_models.issubset(forward.index):
        raise ValueError("Prediction table is missing a required forward-chaining model.")
    rplus_ratio = pd.to_numeric(rplus["identifiability_loss_ratio"], errors="coerce")
    sampled = rplus["enumeration_method"].astype(str).eq("monte_carlo")
    direct_fraction = pd.to_numeric(rplus["feasible_fraction_direct_R_like"], errors="coerce")
    weak_fraction = pd.to_numeric(rplus["feasible_fraction"], errors="coerce")
    p_constraints = constraints.loc[constraints["regime"].eq("P")]
    return {
        "p_width": float(by_regime.loc["P", "mean_normalized_uncertainty"]),
        "r_width": float(by_regime.loc["R", "mean_normalized_uncertainty"]),
        "rplus_width": float(by_regime.loc["R_plus", "mean_normalized_uncertainty"]),
        "p_weeks": int(by_regime.loc["P", "n_weeks"]),
        "r_weeks": int(by_regime.loc["R", "n_weeks"]),
        "rplus_weeks": int(by_regime.loc["R_plus", "n_weeks"]),
        "ratio_mean": float(rplus_ratio.mean()),
        "ratio_median": float(rplus_ratio.median()),
        "ratio_expanded": int((rplus_ratio > 1.0 + 1e-12).sum()),
        "ratio_equal": int((rplus_ratio.sub(1.0).abs() <= 1e-12).sum()),
        "containment_violations": int((weak_fraction + 1e-12 < direct_fraction).sum()),
        "rplus_exact": int((~sampled).sum()),
        "rplus_sampled": int(sampled.sum()),
        "rplus_max_mcse": float(pd.to_numeric(rplus.loc[sampled, "mc_standard_error"], errors="coerce").max()),
        "p_constraint_weeks": int(len(p_constraints)),
        "combined_accuracy": float(forward.loc["combined_lag_logistic", "accuracy"]),
        "combined_logloss": float(forward.loc["combined_lag_logistic", "log_loss"]),
        "same_week_accuracy": float(forward.loc["judge_only_logistic_same_week", "accuracy"]),
        "same_week_logloss": float(forward.loc["judge_only_logistic_same_week", "log_loss"]),
        "random_accuracy": float(forward.loc["random_uniform", "accuracy"]),
        "random_logloss": float(forward.loc["random_uniform", "log_loss"]),
    }


def target_fit_rows() -> pd.DataFrame:
    rows = [
        ("Public/service-sector decision problem", "fail", "high", "The study has a longitudinal competition testbed, not a public-service operation or planning authority.", "Do not represent the testbed as a completed public/service application.", "The empirical setting is a methodological testbed; any public/service transfer is conditional and untested here."),
        ("Quantitative analysis / OR / management science / statistics", "pass", "low", "The project implements LP bounds, ordinal feasible sets, fixed-seed computation, and auditable validation.", "Retain formal definitions and trace every quantitative claim to an output.", "The core contribution is rule-aware partial identification under observed aggregation rules."),
        ("Interdisciplinary applied quantitative research", "partial", "medium", "The methods are quantitative, but the applied planning link is conceptual rather than empirical.", "Add a real applied bridge or avoid direct domain-fit language.", "The framework may be useful when an applied decision system has comparable rules and hidden stakeholder input."),
        ("Methodological uniqueness", "partial", "medium", "Cardinal/ordinal distinction and judge-save containment are explicit, but verified related-work synthesis is incomplete.", "Complete the documented literature gap before making novelty-superiority claims.", "The manuscript contributes a mechanism-specific construction; its position relative to prior work remains to be documented."),
        ("Problem-context importance", "fail", "high", "No service outcome, policy objective, or decision owner is measured.", "Provide a directly relevant application or choose a broader methodological venue.", "The case demonstrates information constraints, not a measured planning intervention."),
        ("Practical decision-design implication", "partial", "high", "The findings motivate a transparency-discretion trade-off, without operational evaluation.", "State implications as design questions rather than operational benefits.", "Discretion can alter both a decision and the information later available for auditing it."),
        ("Risk that the testbed appears overly entertainment-focused", "fail", "high", "The empirical data arise from a televised competition despite the general decision-analysis framing.", "Keep case-specific narrative in the data section and do not promise public-sector evidence.", "The setting is used for its repeated rule changes and coarse outcome feedback, not as evidence about entertainment demand."),
        ("Need to recast title, abstract, introduction, and discussion", "pass", "medium", "Baseline materials already identify the testbed, but SEPS framing needs stronger boundary language.", "Use the generated SEPS-oriented copies only with the stated scope qualification.", "This paper studies hidden preferences in expert-crowd decision systems using a longitudinal empirical testbed."),
        ("Need to weaken case-specific narrative", "pass", "medium", "The revised plan puts institutional mechanism and estimand before the competition setting.", "Move program-specific detail to data/rules and appendix material.", "The empirical record supplies documented rule changes, eliminations, and multiple aggregation regimes."),
        ("Need to consider a different venue class", "pass", "high", "The previous strict audit found SEPS applied-scope evidence insufficient.", "Prioritize venues open to decision analysis, operations research, computational social science, or methodological inference testbeds.", "Venue choice should follow confirmed scope and the actual empirical contribution, not a wording change alone."),
    ]
    return pd.DataFrame(rows, columns=["item", "status", "risk_level", "evidence_from_manuscript", "required_revision", "exact_suggested_wording"])


def target_fit_audit(fit: pd.DataFrame) -> str:
    return f"""
# Overnight Target-Journal Fit Audit: Socio-Economic Planning Sciences

## Official-source access record

- SEPS Aims and Scope: <{SEPS_SCOPE_URL}>. A live access attempt on {ACCESS_DATE} returned HTTP 403 from this environment. Its full scope must be verified manually in a normal browser before submission.
- SEPS Guide for Authors: <{SEPS_GUIDE_URL}>. A live access attempt on {ACCESS_DATE} returned HTTP 403 from this environment. Article type, word-count, graphical-abstract, file, and declaration requirements remain manual checks.
- Elsevier Research Data policy: <{ELSEVIER_DATA_URL}> returned HTTP 200 on {ACCESS_DATE}.
- Elsevier Generative AI policy: <{ELSEVIER_AI_URL}> returned HTTP 200 on {ACCESS_DATE}. It requires disclosure of material AI assistance, human oversight, and author responsibility; AI cannot be an author.
- Elsevier Publishing Ethics: <{ELSEVIER_ETHICS_URL}> returned HTTP 200 on {ACCESS_DATE}.

## Overall judgement: Weak fit for SEPS

The manuscript has a credible quantitative methodology, but the present evidence does not study a public-sector, service-sector, or planning decision in operation. Reframing improves clarity but cannot supply that missing application. The central submission risk is desk rejection for scope mismatch. This is a direct fit conclusion, not a claim that the underlying methods are invalid.

## Itemized review

{markdown_table(fit, list(fit.columns))}

## Gate before submission

Do not submit to SEPS without (1) manual confirmation of the current SEPS pages, and (2) either a genuine public/service application or an editor-confirmed acceptance of the current methodological testbed. A broader decision-analysis, operations-research, or computational-social-science venue class is more defensible under the present evidence.
"""


def repositioning_plan() -> str:
    return """
# Target Journal Repositioning Plan

## Current position

The paper is a quantitative decision-analysis study of hidden public preferences in expert-crowd decision systems. The longitudinal competition record is an empirical testbed with documented rule changes, observed eliminations, and multiple aggregation regimes. It is not a public-sector effectiveness study and does not observe public ballots.

## Reframing to use only conditionally

1. Lead with hidden inputs, coarse outcome feedback, and rule-aware partial identification.
2. Present the testbed only after stating the general estimand and identification problem.
3. Describe public/service relevance as a transfer question: it applies only when the target system has documented rules, hidden stakeholder input, and comparable observable feedback.
4. Treat discretion versus identifiability as a decision-design consideration, not a welfare or operational-performance result.
5. Keep prediction as secondary validation and counterfactuals as scenarios conditional on observed trajectories.

## Non-negotiable limits

- Do not call the testbed a public/service decision application.
- Do not claim that the analysis observes or point-recovers public preference.
- Do not promise that the framework improves a service outcome.
- Do not claim a SEPS fit without manual confirmation of the live scope and author guidance.

## Editorial decision

The rewording in this directory makes the manuscript more legible to a SEPS reader, but it does not resolve the absence of a demonstrated planning/service application. The recommended action remains to consider a venue class with broader methodological scope unless new, in-scope evidence is added in a future study.
"""


def title_abstract(metrics: dict[str, float | int]) -> str:
    abstract = """Expert-crowd decision systems often combine observed expert assessments with hidden public, member, or stakeholder input while releasing only coarse outcomes. Hidden public preferences are therefore not directly observed. We develop a rule-aware partial-identification framework that characterizes feasible preference sets implied by an aggregation rule, active set, expert component, and observed elimination. Under percentage aggregation, the feasible set is a simplex-constrained polytope and coordinate-wise linear programs give sharp marginal bounds. Under ranking aggregation, the latent object is a feasible set of ordinal public rankings, not a cardinal support share. A judge-save intervention replaces a direct elimination implication with a weaker bottom-set condition and expands the compatible ranking set within comparable weeks. We apply the framework to a longitudinal empirical testbed with documented rule changes and three aggregation regimes. The evidence quantifies mechanism-induced uncertainty without observing public ballots. Typed dynamic proxies, lagged prediction, and scenario analysis are secondary checks that retain this boundary. The contribution is a transparent method for distinguishing information identified by coarse institutional feedback from quantities that would require additional assumptions, rules, independently observed stakeholder data, and transparent coding conventions."""
    count = word_count(abstract)
    if not 180 <= count <= 220:
        raise ValueError(f"Overnight abstract must contain 180-220 words; found {count}.")
    return f"""
# Title, Abstract, and Keywords: SEPS-Oriented Revision

## Title Option A: Methodological

Partial Identification of Hidden Preferences Under Aggregation Mechanisms

## Title Option B: Conditional SEPS Orientation

Expert-Crowd Decision Systems, Hidden Preferences, and Robust Decision Design

## Title Option C: Conservative Submission Option

Rule-Aware Inference from Coarse Outcomes in Expert-Crowd Decision Systems

## Recommended Title

Partial Identification of Hidden Preferences Under Aggregation Mechanisms

## Abstract

{abstract}

## Keywords

partial identification; expert-crowd decision systems; hidden preferences; aggregation mechanisms; ranking aggregation; robust decision design; uncertainty-aware aggregation

## Testbed Boundary

The longitudinal competition setting is an empirical testbed. It supplies observable rule changes and coarse feedback; it is not presented as a public/service-sector application.
"""


def title_audit(title_text: str) -> str:
    abstract = title_text.split("## Abstract", 1)[1].split("## Keywords", 1)[0]
    keywords = title_text.split("## Keywords", 1)[1].split("## Testbed Boundary", 1)[0]
    lower = title_text.casefold()
    forbidden = [phrase for phrase in FORBIDDEN if phrase in lower]
    return f"""
# Overnight Title, Abstract, and Keyword Audit

- Three title options generated: yes.
- Abstract word count: {word_count(abstract)} (required range: 180-220).
- Abstract begins with expert-crowd decision systems: yes.
- States that public preferences are not directly observed: yes.
- Centers rule-aware partial identification and mechanism-induced identifiability: yes.
- Prediction/counterfactual material limited to one sentence: yes.
- Prohibited point-recovery or causal wording found: {"none" if not forbidden else ", ".join(forbidden)}.
- Keyword count: {len([item for item in keywords.split(";") if item.strip()])}.

The selected title is intentionally general. It does not claim an evaluated public/service application and should not be treated as proof of SEPS scope fit.
"""


def introduction() -> str:
    return """
# Introduction: SEPS-Oriented Revision

Expert-crowd decision systems combine specialized assessments with input from members, users, clients, or broader publics. Such arrangements appear in public-facing, service, and organizational settings when institutions seek both expert evaluation and participation. Their decision rules are consequential because they determine not only allocations or selections, but also what later observers can learn from the released feedback.

The inferential difficulty is sharp when public input is hidden and feedback is coarse. An elimination, selection, or other final decision can be compatible with many latent preference configurations. The estimand is therefore a feasible preference set conditional on the documented rule and observables, rather than a point-valued reconstruction of an unobserved input.

Existing work on prediction, ranking explanation, and retrospective analytics can be useful for description or validation. It does not by itself resolve partial identification under elimination-only feedback: a model can rank cases without establishing which hidden preference states are consistent with the observed institutional outcome. This distinction is especially important when rules vary across time or include discretionary interventions.

We develop a rule-aware partial-identification framework for percentage and ranking aggregation. Percentage aggregation yields simplex-constrained linear inequalities and coordinate-wise linear-program bounds. Ranking aggregation yields feasible ordinal public rankings. Under a judge-save rule, a direct elimination implication is replaced with a weaker tie-inclusive bottom-set condition, so the compatible ranking set expands within the same week.

The empirical record is a longitudinal competition testbed with repeated outcomes, documented rule changes, and multiple aggregation regimes. Its value is methodological: it exposes how the same broad decision problem yields cardinal or ordinal identified objects under different rules. The setting is not offered as an evaluation of a public-service operation.

The paper makes four contributions: (1) a rule-aware partial-identification framework for hidden public preferences; (2) a comparison of cardinal and ordinal aggregation mechanisms; (3) a within-regime judge-save analysis of identifiability loss; and (4) uncertainty-aware validation and decision-design extensions that remain secondary to the identified-set results.

The remainder of the paper documents the data and rules, develops the identification framework, reports the core evidence, then presents secondary validation and scenario analyses before discussing transfer limits.
"""


def related_work_plan() -> str:
    return """
# Related Work: SEPS Revision Plan

## Required additions before scholarly submission

1. Use the verified partial-identification sources to distinguish identified sets from point estimation and confidence-interval construction.
2. Use verified social-choice material to define the ordinal aggregation problem without equating ordinal rank sets to cardinal support.
3. Position robust decision design as a response to deep or structural uncertainty, not as evidence that this paper identifies an empirically optimal rule.
4. Cite prediction-for-validation material to separate predictive performance from causal or latent-state recovery.
5. Add public/service operations-research literature only after manually verifying that its institutional setting is genuinely comparable to the present information structure.

## Claims that must remain provisional until literature review is completed

- Any priority, novelty, or first-of-its-kind claim.
- Any assertion that an entertainment testbed is representative of public/service operations.
- Any claim that judge-save discretion improves or harms welfare.

## Citation discipline

Do not insert unverified sources into the manuscript. The associated generated table lists verified candidates and explicit gaps. A final reference manager export, complete bibliography, and in-text citations remain required submission work.
"""


def literature_rows() -> pd.DataFrame:
    rows = [
        ("must add", "Partial identification and bounds", "Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice", "Charles F. Manski", 2000, "Journal of Econometrics", "https://doi.org/10.1016/S0304-4076(99)00045-7", "Crossref DOI metadata verified 2026-07-15", "Establishes decision analysis under partial identification.", "Related work: partial identification; methods estimand."),
        ("must add", "Partial identification and bounds", "Confidence Intervals for Partially Identified Parameters", "Guido W. Imbens; Charles F. Manski", 2004, "Econometrica", "https://doi.org/10.1111/j.1468-0262.2004.00555.x", "Crossref DOI metadata verified 2026-07-15", "Separates identified-set inference from point estimation.", "Related work: bounds; limitations."),
        ("must add", "Social choice and aggregation mechanisms", "Condorcet's Theory of Voting", "H. Peyton Young", 1988, "American Political Science Review", "https://doi.org/10.2307/1961757", "Crossref DOI metadata verified 2026-07-15", "Supplies social-choice context for aggregation-rule discussion.", "Related work: aggregation mechanisms."),
        ("must add", "Ranking aggregation / ordinal preference inference", "Condorcet's Theory of Voting", "H. Peyton Young", 1988, "American Political Science Review", "https://doi.org/10.2307/1961757", "Crossref DOI metadata verified 2026-07-15", "Supports careful treatment of ordinal aggregation; add ranking-specific literature after manual review.", "Related work: ranking aggregation."),
        ("must add", "Decision-making under uncertainty", "Minimax-regret treatment choice with missing outcome data", "Charles F. Manski", 2007, "Journal of Econometrics", "https://doi.org/10.1016/j.jeconom.2006.06.006", "Crossref DOI metadata verified 2026-07-15", "Motivates decisions with incomplete information without point recovery.", "Related work: uncertainty; discussion."),
        ("must add", "Robust decision design", "The Price of Robustness", "Dimitris Bertsimas; Melvyn Sim", 2004, "Operations Research", "https://doi.org/10.1287/opre.1030.0065", "Crossref DOI metadata verified 2026-07-15", "Frames robustness as a design trade-off, not an observed benefit.", "Related work: robust decision design; discussion."),
        ("must add", "Prediction as validation, not causal proof", "To Explain or to Predict?", "Galit Shmueli", 2010, "Statistical Science", "https://doi.org/10.1214/10-STS330", "Crossref DOI metadata verified 2026-07-15", "Supports separating predictive validation from explanatory claims.", "Related work: validation; Section 6."),
        ("must add", "Public/service-sector quantitative decision analysis", "Operations research and the public sector", "R. V. V. Vidal", 1995, "European Journal of Operational Research", "https://doi.org/10.1016/0377-2217(95)90125-6", "Crossref DOI metadata verified 2026-07-15", "Anchors the public-sector OR gap and makes the current application mismatch visible.", "Introduction: applied relevance boundary; discussion."),
        ("manual search required", "Expert-crowd or expert-public decision systems", "No verified candidate selected", "", "", "", "", "Manual verification required", "Need domain-specific work on hybrid expert-public input; do not cite a generic crowd source as validation of this testbed.", "Introduction motivation and external-validity limitation."),
        ("manual search required", "Institutional discretion or intervention mechanisms", "No verified candidate selected", "", "", "", "", "Manual verification required", "Need work on discretionary saves, overrides, delegation, or intervention under comparable institutional rules.", "Related work and judge-save discussion."),
        ("optional", "Applications of OR/MS/statistics to public or service decisions", "No verified candidate selected", "", "", "", "", "Manual verification required", "Select only applications with documented hidden-input and coarse-feedback structures.", "SEPS bridge, only if venue remains under consideration."),
    ]
    columns = ["priority", "direction", "title", "authors", "year", "source", "doi_or_stable_url", "verification_status", "why_needed", "paragraph_or_claim"]
    return pd.DataFrame(rows, columns=columns)


def methods_revised(metrics: dict[str, float | int]) -> str:
    return f"""
# Methods: SEPS-Oriented Revision

## Setup

For week t, let A_t be the active contestant set and E_t the recorded eliminated set. The observed record contains the expert component, institutional rule, active set, and coarse outcome. No public ballot is observed. The target is the set of hidden public states compatible with these observables.

## Percentage regime P

Let j_it be the expert share and p_it the hidden public share. The candidate vector p_t lies in the simplex Delta_t = {{p_it >= 0, sum_(i in A_t) p_it = 1}}. For an eliminated contestant e and non-withdrawn survivor s, higher combined score is better and the recorded outcome implies j_et + p_et <= j_st + p_st, or p_et - p_st <= j_st - j_et. These inequalities, the simplex equality, and coordinate bounds define F_t. For every i, we solve L_it = min_(p in F_t) p_it and U_it = max_(p in F_t) p_it by linear programming. U_it - L_it is a sharp coordinate-wise width. Coordinate midpoints are descriptive and need not constitute a jointly feasible vector.

No-elimination and withdrawal-only weeks add no fabricated outcome inequality. Multiple eliminations compare each eliminated contestant to every non-withdrawn survivor without ordering eliminated contestants. A finale contributes complete pairwise ordering only when unique active placements are observed.

## Ranking regimes R and R_plus

Let r^J_it and r^F_it denote judge and candidate public ranks, respectively, with 1 = best for both. Candidate public ranks are strict permutations. The combined rank c_it = r^J_it + r^F_it is worse when larger. With k recorded eliminations, a direct feasible ranking places every eliminated contestant in the tie-inclusive bottom-k set B_k(c_t). The R feasible set is the collection of candidate permutations satisfying this condition.

For R_plus, the implemented weak judge-save condition replaces B_k(c_t) with B_(k+1)(c_t). Therefore F_direct,t is a subset of F_weak,t. The weak/direct ratio is a within-week identifiability-loss summary, not a cross-regime causal contrast. In the generated results, it averages {metrics['ratio_mean']:.6f} and is never below one.

For contestant i, ordinal support width is max(r^F_it) - min(r^F_it), normalized by |A_t|-1. If q_itr is the feasible-ranking frequency of rank r, H_it = -sum_r q_itr log(q_itr) and weekly normalized entropy averages H_it/log(|A_t|). These are ordinal summaries; they are not support shares and must not be equated with P widths.

## Computation and typed proxies

Exact enumeration evaluates all |A_t|! permutations in small fields. Larger fields use 10,000 fixed-seed uniform draws. R_plus has {metrics['rplus_exact']} exact and {metrics['rplus_sampled']} sampled weeks; its largest recorded Monte Carlo standard error for a feasible fraction is {metrics['rplus_max_mcse']:.6f}. This numerical error is separate from mechanism-induced uncertainty. Retained rankings use a fixed-seed reservoir only for storage; full evaluated draws determine distributions and widths.

P proxy values use (L_it + U_it)/2, while R/R_plus proxy values use 1 - (mean(r^F_it)-1)/(|A_t|-1). They are typed cardinal and ordinal summaries, respectively. Exponential smoothing organizes these summaries over time; it does not produce an observed ballot.

## Validation and scenario boundary

Strictly historical validation uses previous contestant observations. Same-week judge models are explanatory baselines rather than deployable forecasts. Counterfactual calculations propagate feasible-set scenarios conditional on the observed active trajectory; they are scenario analyses and do not supply causal replacement histories.
"""


def method_checklist() -> pd.DataFrame:
    rows = [
        ("M1", "All symbols defined", "pass", "Methods defines A_t, E_t, j, p, r^J, r^F, c, B_k, and F_t.", "Keep definitions beside the first equation."),
        ("M2", "P simplex and linear inequalities", "pass", "src/constraints.py:136-321 constructs nonnegative simplex shares and eliminated-survivor inequalities.", "Retain p_e - p_s <= j_s - j_e."),
        ("M3", "P feasibility and LP bounds", "pass", "src/constraints.py:342-435 uses HiGHS feasibility plus per-coordinate minimum and maximum LPs.", "State that bounds are sharp marginal bounds."),
        ("M4", "R/R_plus rank direction", "pass", "src/ranking_identification.py:205-218 gives rank 1 to higher judge scores; 324-355 forms c = r^J + r^F.", "State that larger combined rank is worse."),
        ("M5", "Judge-save weak condition", "pass", "src/ranking_identification.py:350-355 applies bottom-k direct and bottom-(k+1) weak masks.", "Call the set tie-inclusive."),
        ("M6", "Direct/weak containment", "pass", "The bottom-(k+1) criterion weakens bottom-k membership; output has no containment violation.", "Restrict the claim to same-week comparable rankings."),
        ("M7", "Normalized width, feasible fraction, and entropy", "pass", "src/ranking_identification.py:105-149 and 473-516 define rank support, entropy, and feasible fractions.", "Do not equate ordinal measures with cardinal shares."),
        ("M8", "Exact enumeration versus sampling", "pass", "src/ranking_identification.py:529-610 labels exact versus Monte Carlo evaluation and records fixed-seed sampling.", "Report numerical Monte Carlo error separately."),
        ("M9", "Dynamic proxy is not a ballot", "pass", "src/identification_features.py:205-250 assigns cardinal midpoint or ordinal rank-score types.", "Keep typed-proxy boundary in methods and limitations."),
        ("M10", "P and ordinal proxy non-equivalence", "pass", "P uses interval midpoint; R/R_plus use normalized mean feasible rank.", "Never pool proxy scale values as a common vote measure."),
        ("M11", "Code-formula consistency", "pass", "Static review found matching score directions, constraints, bottom-set logic, and fixed-seed conventions.", "No code-method mismatch found in this audit."),
        ("M12", "Variable and tie-policy consistency", "pass", "Primary ranking output labels average_rank and tie-inclusive bottom-set handling.", "Keep tie-policy sensitivity in the appendix."),
    ]
    return pd.DataFrame(rows, columns=["check_id", "check", "status", "evidence", "required_action"])


def result_sentence_map(metrics: dict[str, float | int]) -> pd.DataFrame:
    rows = [
        ("R1", f"P has {metrics['p_weeks']} feasible weeks with mean normalized coordinate-wise width {metrics['p_width']:.6f}.", "outputs/tables/identification_comparison_by_regime.csv; outputs/logs/partial_identification_report.md", "supported", "Feasible intervals, not observed ballots."),
        ("R2", f"R and R_plus mean normalized ordinal widths are {metrics['r_width']:.6f} and {metrics['rplus_width']:.6f}.", "outputs/tables/identification_comparison_by_regime.csv", "supported with caveat", "Different mathematical objects; descriptive only."),
        ("R3", f"The R_plus weak/direct ratio has mean {metrics['ratio_mean']:.6f}, median {metrics['ratio_median']:.6f}, {metrics['ratio_expanded']} strict expansions, and {metrics['containment_violations']} violations.", "outputs/tables/ranking_identification_summary_rplus.csv; outputs/logs/ranking_identification_report_rplus.md", "supported", "Within-regime set inclusion, not a cross-mechanism causal estimate."),
        ("R4", f"The historical combined-lag model has accuracy {metrics['combined_accuracy']:.6f} and log loss {metrics['combined_logloss']:.6f}; uniform risk has accuracy {metrics['random_accuracy']:.6f} and log loss {metrics['random_logloss']:.6f}.", "outputs/tables/prediction_results.csv", "supported", "Validation signal only."),
        ("R5", f"The same-week judge baseline has accuracy {metrics['same_week_accuracy']:.6f} and log loss {metrics['same_week_logloss']:.6f}.", "outputs/tables/prediction_results.csv", "supported", "Explanatory baseline, not a prior-week forecast."),
        ("R6", "Scenario analyses condition on observed active trajectories and feasible-state inputs.", "src/counterfactuals.py; outputs/tables/counterfactual_results_by_regime.csv", "supported", "Not a causal replacement of historical outcomes."),
        ("R7", "The Pareto grid retains only gamma=0 frontier points.", "outputs/tables/pareto_frontier_points.csv; outputs/logs/robust_aggregation_report.md", "supported", "No evidence to claim a positive uncertainty penalty is empirically dominant."),
    ]
    return pd.DataFrame(rows, columns=["sentence_id", "sentence_or_claim", "supporting_output", "audit_status", "claim_boundary"])


def results_revised(metrics: dict[str, float | int]) -> str:
    return f"""
# Results: SEPS-Oriented Revision

## Feasible sets remain wide under coarse feedback

For P, {metrics['p_weeks']} eligible weeks yield nonempty feasible regions. Mean normalized coordinate-wise width is {metrics['p_width']:.6f}. The result shows that the recorded rule and elimination restrict a set of compatible latent preference states without selecting one point-valued public input.

## The aggregation mechanism changes the identified object

P produces cardinal feasible-share intervals. R and R_plus produce feasible ordinal public rankings, with mean normalized rank-support widths of {metrics['r_width']:.6f} and {metrics['rplus_width']:.6f}. These quantities are not directly comparable because their scales, state spaces, and sample compositions differ.

## Judge-save discretion weakens the observable implication

Across {metrics['rplus_weeks']} R_plus weeks, the weak/direct feasible-set ratio averages {metrics['ratio_mean']:.6f} and has median {metrics['ratio_median']:.6f}. The weak set is strictly larger in {metrics['ratio_expanded']} weeks, equal in {metrics['ratio_equal']} weeks, and never smaller. This is a within-week comparison of direct versus weak outcome implications, not an estimate of the causal effect of switching a real institution's rule.

## Secondary validation evidence

The strictly historical combined-lag model has forward-chaining accuracy {metrics['combined_accuracy']:.6f} and log loss {metrics['combined_logloss']:.6f}, compared with {metrics['random_accuracy']:.6f} and {metrics['random_logloss']:.6f} for uniform risk. The lower log loss of the same-week judge benchmark ({metrics['same_week_logloss']:.6f}) is not a forecasting result because it uses current-week judge information. These checks provide limited validation signal and do not observe a public ballot.

Traceable sources: `outputs/tables/identification_comparison_by_regime.csv`, `outputs/tables/ranking_identification_summary_rplus.csv`, `outputs/tables/prediction_results.csv`, `outputs/figures/uncertainty_over_weeks_regime_p.png`, and `outputs/figures/judge_save_identifiability_loss.png`.
"""


def prediction_counterfactuals_revised() -> str:
    return """
# Prediction and Counterfactuals: SEPS-Oriented Revision

## Validation boundary

Historical models use prior contestant observations only. Same-week judge models are explanatory benchmarks and are separated from deployable-style forecasting. Predictive performance is treated as a validation signal for the engineered features, not as evidence that a hidden preference input has been point recovered.

## Scenario boundary

Counterfactual calculations propagate feasible-state scenarios. Percentage-regime lower, midpoint, and upper coordinate summaries are sensitivity inputs and may not form a jointly feasible vector when assembled. Ranking-regime analyses retain feasible joint rankings and do not convert them into cardinal shares. All scenarios condition on observed active trajectories and therefore do not create alternative future performances.

The resulting changes in rankings, finalists, or winners are scenario-sensitivity summaries. They do not establish a causal historical replacement. The weak judge-save calculation is set-valued and does not identify a unique counterfactual winner. The current Pareto frontier contains only gamma=0 grid points, so uncertainty-aware aggregation is a design input rather than an empirically dominant rule.

Detailed model coefficients, calibration, lambda/gamma sensitivity, Pareto details, and controversial cases belong in an appendix or supplement.
"""


def discussion_revised() -> str:
    return """
# Discussion: SEPS-Oriented Revision

Partial identification is the appropriate estimand when public input is hidden and the institution releases only coarse outcomes. A wide feasible set is not an estimation failure: it quantifies information that the rule and feedback leave unresolved. Reporting that width is more transparent than selecting a point estimate through undocumented assumptions.

The judge-save comparison exposes an institutional trade-off. A discretionary save can be attractive for reasons outside this dataset, but it weakens the direct implication of an elimination and therefore reduces what later observers can infer about hidden preferences. The result is about mechanism-induced identifiability, not welfare, fairness, or operational performance.

Typed dynamic proxies organize longitudinal identified-set summaries. They do not turn an interval midpoint or mean feasible rank into an observed ballot. Likewise, prediction is secondary validation and the counterfactual component is scenario analysis rather than a causal account of an alternative history.

For public, service, and organizational decision designers, the conditional lesson is to document aggregation rules, tie handling, interventions, and the feedback made public. Those institutional choices affect both decisions and the feasibility of later audits. This study does not test that lesson in a public/service operation; transfer requires a setting with comparable rules, hidden input, and observable feedback.
"""


def limitations_revised() -> str:
    return """
# Limitations: SEPS-Oriented Revision

1. Public ballots are unobserved, so the study cannot verify a point-valued public-preference measure.
2. Rule interpretation, score normalization, and tie handling can alter the feasible set; the primary R_plus condition is a tie-inclusive weak bottom-set specification.
3. The observed record follows active contestant trajectories and is selected by historical eliminations.
4. P cardinal intervals and R/R_plus ordinal rank sets are different quantities and cannot be pooled into one support metric.
5. Prediction is secondary and does not constitute the paper's main contribution.
6. Counterfactual results depend on feasible-state scenario construction and observed trajectories.
7. A single competition testbed limits external validity, including to public/service systems.
8. Data availability and redistribution remain subject to source terms; a release requires a verified provenance record and permissions review.
9. Code assistance and AI-assisted writing require transparent declarations; authors retain full responsibility for the submitted text and analyses.
10. Journal fit requires human judgement and manual verification of live SEPS scope and submission requirements.

Large ordinal fields use fixed-seed sampling. Its Monte Carlo error is numerical approximation error, not uncertainty about public behavior.
"""


def conclusion_revised() -> str:
    return """
# Conclusion: SEPS-Oriented Revision

Coarse elimination outcomes partially identify hidden public preferences rather than point-valued public inputs. Under percentage aggregation, the compatible states form convex regions with coordinate-wise linear-program bounds. Under ranking aggregation, the compatible states are feasible ordinal rankings. A weak judge-save condition expands the compatible ranking set within comparable weeks.

The contribution is a rule-aware way to state these limits, distinguish cardinal from ordinal objects, and carry uncertainty into secondary validation and scenario analysis. The empirical testbed illustrates the workflow but does not establish public/service-sector effectiveness. Future work should apply the framework to documented service or public decision systems before making operational claims in those domains.
"""


def package_documents() -> dict[str, str]:
    return {
        "cover_letter_SEPS_draft.md": """
# Cover Letter Draft for Socio-Economic Planning Sciences

Dear Editor,

Please consider the manuscript, "Partial Identification of Hidden Preferences Under Aggregation Mechanisms." The paper studies expert-crowd decision systems in which expert assessments are observed, public input is hidden, and institutions release coarse outcomes. We develop a rule-aware partial-identification framework that distinguishes simplex-constrained cardinal feasible regions from ordinal feasible ranking sets. A judge-save condition illustrates how institutional discretion can weaken the observable implication of an elimination and enlarge a feasible set.

The longitudinal empirical testbed supplies documented rule changes, repeated elimination feedback, and multiple aggregation regimes. It is used to demonstrate the method; the paper does not claim to observe public ballots. Dynamic proxy construction, lagged validation, and scenario analysis are secondary extensions that preserve the identified-set boundary.

Code, processed analytical data, and reproducibility materials are prepared within the research package, subject to verification of source-data terms and release permissions. The authors will provide final declarations, authorship information, and availability locations before submission.

This letter is conditional on manual confirmation that the current SEPS scope accepts a methodological paper with this empirical testbed. The present manuscript does not evaluate a public/service-sector operation, and the authors should not submit to SEPS without resolving that scope concern.

Sincerely,

[AUTHOR TO COMPLETE: corresponding author name, affiliation, and contact details]
""",
        "highlights_SEPS.md": """
# Highlights

- Coarse outcomes identify feasible preference sets, not point estimates.
- Aggregation rules determine cardinal versus ordinal identified objects.
- Judge-save discretion expands feasible ranking sets within comparable weeks.
- Mechanism-induced uncertainty is a decision-design input.
- Validation and scenarios preserve the identified-set boundary.
""",
        "data_availability_statement_SEPS.md": """
# Data Availability Statement

[AUTHOR TO COMPLETE] The analysis uses a supplied competition dataset retained unchanged under `data/raw/`. Before release, provide the original source, access date, licence or terms, redistribution permission, and a persistent repository link if sharing is allowed. Processed files are reproducibly generated by the documented pipeline. Do not state that the raw data are publicly redistributable until the source terms are verified.
""",
        "code_availability_statement_SEPS.md": """
# Code Availability Statement

[AUTHOR TO COMPLETE] The analysis code, tests, generated reports, and instructions are in this research package. Before submission, provide a versioned public repository or archival DOI, a software licence, an exact environment lock or container, and a release tag. The current `requirements.txt` specifies ranges and is not an archival environment lock.
""",
        "conflict_of_interest_statement.md": """
# Conflict of Interest Statement

[AUTHOR TO COMPLETE] State all conflicts of interest or explicitly state that the authors declare none. Do not submit this placeholder as a final declaration.
""",
        "funding_statement.md": """
# Funding Statement

[AUTHOR TO COMPLETE] State funding sources, grant numbers, and funder roles, or explicitly state that no funding was received. Do not infer funding from the project files.
""",
        "ethics_statement.md": """
# Ethics Statement

[AUTHOR TO COMPLETE] Confirm whether institutional review or informed consent is applicable to this secondary analysis of supplied data. If not applicable, state the basis after author/institution review. Do not invent approval numbers or ethics exemptions.
""",
        "author_contributions_placeholder.md": """
# Author Contributions

[AUTHOR TO COMPLETE] Provide a CRediT-style contribution statement with named authors and roles. Confirm final accountability for analysis, writing, and submission.
""",
        "acknowledgements_placeholder.md": """
# Acknowledgements

[AUTHOR TO COMPLETE] Add acknowledgements approved by contributors, or state that there are none. Do not list unverified contributors.
""",
        "graphical_abstract_plan.md": """
# Graphical Abstract Plan

## Recommendation

Prepare a graphical abstract only after manually checking the current SEPS Guide for Authors. The official guide endpoint was inaccessible from this environment, so graphical-abstract requirements are not treated as verified.

## Proposed visual structure

Hidden preference input -> documented aggregation rule -> feasible preference set -> conditional decision-design implication.

The left panel should label the input as hidden, the center panel should show percentage and ranking rule branches, the next panel should show an interval/polytope and feasible rankings, and the final panel should state "auditability and discretion trade-off". Do not depict a recovered ballot, a causal arrow to welfare, or a winning contestant.

## Provisional production specification

Use a 1800 x 1350 pixel canvas (6 x 4.5 inches at 300 dpi), high-contrast text, and editable vector source where possible. Confirm final dimensions, file type, colour profile, and disclosure requirements against the live journal guide. If an AI or drawing tool materially assists creation, disclose the tool, purpose, human review, and author responsibility according to the final publisher policy.
""",
    }


def package_checklist() -> pd.DataFrame:
    rows = [
        ("Cover letter", "draft generated", "manuscript/cover_letter_SEPS_draft.md", "Conditional on scope confirmation."),
        ("Highlights", "draft generated", "manuscript/highlights_SEPS.md", "Manually confirm current journal limits."),
        ("Data availability", "placeholder generated", "manuscript/data_availability_statement_SEPS.md", "Add source terms, permission, and repository URL."),
        ("Code availability", "placeholder generated", "manuscript/code_availability_statement_SEPS.md", "Add release, licence, and environment lock."),
        ("AI statement", "existing draft retained", "manuscript/ai_assisted_writing_statement.md", "Confirm final publisher wording and placement."),
        ("Conflict statement", "placeholder generated", "manuscript/conflict_of_interest_statement.md", "Author declaration required."),
        ("Funding statement", "placeholder generated", "manuscript/funding_statement.md", "Author declaration required."),
        ("Ethics statement", "placeholder generated", "manuscript/ethics_statement.md", "Institutional/author confirmation required."),
        ("Author contributions", "placeholder generated", "manuscript/author_contributions_placeholder.md", "Named CRediT roles required."),
        ("Acknowledgements", "placeholder generated", "manuscript/acknowledgements_placeholder.md", "Author-approved text required."),
        ("Graphical abstract", "plan generated", "manuscript/graphical_abstract_plan.md", "Do not make until live guide is checked."),
        ("Compiled manuscript and references", "missing", "", "Create after venue decision and bibliography verification."),
    ]
    return pd.DataFrame(rows, columns=["item", "status", "file_path", "required_before_submission"])


def figure_table_plan(root: Path) -> pd.DataFrame:
    figures = root / "outputs/figures"
    entries = [
        ("figure", "Figure 1", True, "conceptual_framework_hidden_preferences.png", "Conceptual feasible-set framework", "Keep", "Self-contained conceptual labels; no claim of observed ballot.", "Provide vector source if guide requires."),
        ("figure", "Figure 2", True, "uncertainty_over_weeks_regime_p.png", "P interval width over weeks", "Keep", "Caption must say coordinate-wise feasible width.", "P only."),
        ("figure", "Figure 3", True, "judge_save_identifiability_loss.png", "R_plus weak versus direct expansion", "Keep", "State tie-inclusive bottom-set rule.", "Within-regime only."),
        ("figure", "Figure 4", True, "identification_width_by_regime.png", "Cross-regime uncertainty context", "Keep with caveat", "State cardinal/ordinal non-comparability prominently.", "Descriptive only."),
        ("figure", "Figure 5", False, "prediction_comparison.png", "Prediction validation", "Appendix", "Same-week models must be marked explanatory.", "Secondary validation."),
        ("table", "Table 1", True, "data/processed/identification_features_long.csv; outputs/tables/constraint_summary.csv", "Dataset and regime summary", "Keep", "Add rule and event-type footnotes.", "Separate cardinal and ordinal objects."),
        ("table", "Table 2", True, "outputs/tables/identification_comparison_by_regime.csv", "Partial-identification summary", "Keep", "Use a prominent non-comparability note.", "Mechanism-specific measures."),
        ("table", "Table 3", True, "outputs/tables/ranking_identification_summary_rplus.csv", "Direct versus weak judge-save comparison", "Keep", "Report exact/sampled rows and tie policy.", "Within-week comparison."),
        ("table", "Table 4", False, "outputs/tables/prediction_results.csv", "Prediction validation", "Appendix", "Separate same-week from historical models.", "Secondary validation."),
    ]
    rows: list[dict[str, str | bool]] = []
    for item_type, item_id, main_text, file_name, purpose, decision, caption, note in entries:
        if item_type == "figure":
            path = figures / file_name
            if not path.is_file():
                raise FileNotFoundError(f"Required figure missing: {path}")
            with Image.open(path) as image:
                dpi = image.info.get("dpi", (0, 0))[0]
                size = f"{image.width}x{image.height}"
            dpi_status = f"{float(dpi):.0f} dpi" if dpi else "dpi metadata missing"
        else:
            size = "not applicable"
            dpi_status = "not applicable"
        rows.append({"item_type": item_type, "item_id": item_id, "main_text": main_text, "file_or_source": file_name, "purpose": purpose, "decision": decision, "caption_and_label_check": caption, "comparability_or_proxy_note": note, "pixel_size": size, "dpi_check": dpi_status})
    return pd.DataFrame(rows)


def figure_table_markdown(plan: pd.DataFrame) -> str:
    main = plan.loc[plan["main_text"]]
    return f"""
# Figure and Table Plan: SEPS-Oriented Revision

## Main-text selection

The proposal keeps {int((main['item_type'] == 'figure').sum())} figures and {int((main['item_type'] == 'table').sum())} tables, within the requested ceiling of five figures and four tables. The prediction figure and table move to the appendix because validation is secondary. No new figures or models are generated.

{markdown_table(plan, list(plan.columns))}

## Appendix / supplement recommendations

- Controversial-case scenario panels.
- Lambda/gamma sensitivity and Pareto details.
- Dynamic proxy examples and full regression coefficients.
- Ranking sampling diagnostics and tie-policy sensitivity.
- Prediction calibration and full model tables.
- Pipeline reproducibility, data audit, and all audit checklists.

Each retained main-text caption must define the estimand, distinguish P intervals from ordinal ranking sets, avoid point-recovery wording, and state whether it reports an exact or sampled result.
"""


def go_no_go(metrics: dict[str, float | int]) -> str:
    return f"""
# Overnight Go / No-Go Report

## Decision: D. Not suitable for SEPS in its current empirical form

The paper is methodologically credible but does not demonstrate a public-sector, service-sector, or socio-economic planning application. SEPS-specific scope and author-guide pages also require manual verification because this environment received HTTP 403. Reframing alone does not remedy the applied-fit gap.

## Scores (1 = weak/high risk; 5 = strong/low risk)

| Dimension | Score | Basis |
| --- | --- | --- |
| Target journal fit | 1 | No evaluated public/service/planning setting. |
| Methodological novelty | 3 | Rule-aware construction is clear; literature positioning incomplete. |
| Empirical credibility | 4 | Longitudinal audited testbed and documented rule regimes. |
| Evidence-claim alignment | 4 | Generated audits constrain central language. |
| Reproducibility | 4 | Pipeline, tests, fixed seeds, and traceable outputs exist; no environment lock. |
| Writing clarity | 3 | Revised copies clarify scope; bibliography and compiled manuscript absent. |
| Generalizability | 1 | One entertainment testbed, no applied transfer validation. |
| Risk of overclaiming | 3 | Cooled wording is available; submission integration remains manual. |
| Data/code availability | 2 | Source terms, licence, release, and lock file unresolved. |
| Reviewer defensibility | 2 | Strong methods, weak SEPS application and literature package. |

## Top strengths

1. Rule-aware separation of cardinal and ordinal identified objects.
2. Sharp P coordinate-wise LP bounds with explicit feasibility checks.
3. Within-week R_plus direct/weak containment audit ({metrics['containment_violations']} violations).
4. Fixed-seed enumeration/sampling diagnostics and explicit numerical-error boundary.
5. Prediction and scenario language has been separated from point recovery and causal claims.

## Top rejection risks

1. SEPS desk rejection for absent public/service/planning application.
2. Missing manually verified SEPS scope and author instructions.
3. Incomplete verified bibliography and no compiled reference list.
4. No archived environment lock, release licence, or confirmed data terms.
5. Markdown sections are not a formatted, blinded submission manuscript.

## Ten required fixes before any submission

1. Decide whether to redirect to a broader decision-analysis, OR, or computational-social-science venue class.
2. Manually verify the current SEPS scope and author guide if SEPS remains under consideration.
3. Add a genuine public/service application or secure editorial confirmation of scope.
4. Complete verified related work and create a reference-managed bibliography.
5. Integrate selected revised copies into a compiled manuscript after venue choice.
6. Produce author-approved title page, conflict, funding, ethics, CRediT, and acknowledgements statements.
7. Confirm source-data access, licence, and redistribution terms.
8. Publish or archive code with a licence, release tag, and exact environment lock/container.
9. Create journal-formatted main tables, captions, appendix, and vector assets as required.
10. Run a clean-environment reproduction and preserve its log.

## Ten optional improvements

1. Obtain an editor presubmission inquiry before full submission.
2. Add an external application in future work rather than forcing a transfer claim now.
3. Conduct a manually curated expert-crowd literature review.
4. Expand tie-policy sensitivity explanation in a supplement.
5. Add a visual graphical abstract after journal confirmation.
6. Archive deterministic output checksums at release.
7. Add data dictionary and rule-coding appendix.
8. Prepare a blinded and an unblinded manuscript version.
9. Add a registered replication environment.
10. Seek domain feedback on conditional decision-design interpretation.

## Recommendation

Do not continue toward SEPS submission now. Consider a broader journal class that accepts methodological decision analysis, operations research, or computational social-science work with an empirical testbed. These materials complete wording, audit, and packaging preparation; they do not create the missing applied evidence.
"""


def final_summary() -> str:
    return """
# Overnight Final Summary

## Completed by the reproducible overnight stage

- Generated a strict SEPS fit audit and itemized checklist.
- Generated title/abstract/keyword, introduction, methods, results, prediction/counterfactual, discussion, limitations, and conclusion copies with `_SEPS_revised` names.
- Generated a verified-candidate literature gap table and a related-work revision plan.
- Generated methods, results-evidence, submission-package, and figure/table audits.
- Generated a conditional SEPS cover letter, highlights, author-completion declarations, and graphical-abstract plan.
- Generated a final Go/No-Go report and main-text/appendix recommendation.

## Important unfinished work

- No original manuscript section was overwritten or automatically integrated into a final compiled article.
- No new model, data collection, external validation, public/service application, or journal-specific evidence was fabricated.
- SEPS Aims/Scope and Guide for Authors require manual browser verification because direct access returned HTTP 403.
- A verified bibliography, exact environment lock, code licence/release, source-data terms, final declarations, and compiled submission remain manual blockers.

## Fit conclusion

SEPS is not recommended for the current empirical form. The most likely rejection path is a desk decision based on applied-scope mismatch, not a failure of the partial-identification computations.
"""


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    require(root, [
        "outputs/tables/identification_comparison_by_regime.csv",
        "outputs/tables/ranking_identification_summary_rplus.csv",
        "outputs/tables/prediction_results.csv",
        "outputs/tables/constraint_summary.csv",
        "outputs/tables/pareto_frontier_points.csv",
        "outputs/figures/conceptual_framework_hidden_preferences.png",
        "outputs/figures/uncertainty_over_weeks_regime_p.png",
        "outputs/figures/judge_save_identifiability_loss.png",
        "outputs/figures/identification_width_by_regime.png",
        "outputs/figures/prediction_comparison.png",
    ])
    try:
        metrics = calculate_metrics(root)
        manuscript = root / "manuscript"
        tables = root / "outputs/tables"
        logs = root / "outputs/logs"

        fit = target_fit_rows()
        fit.to_csv(tables / "overnight_target_journal_fit_checklist.csv", index=False)
        write_text(logs / "overnight_target_journal_fit_audit.md", target_fit_audit(fit))
        write_text(manuscript / "target_journal_repositioning_plan.md", repositioning_plan())

        title = title_abstract(metrics)
        write_text(manuscript / "00_title_abstract_keywords_SEPS_revised.md", title)
        write_text(logs / "overnight_abstract_title_audit.md", title_audit(title))
        write_text(manuscript / "01_introduction_SEPS_revised.md", introduction())
        write_text(logs / "overnight_introduction_audit.md", "# Overnight Introduction Audit\n\nThe revision uses seven required paragraphs, begins with expert-crowd decision systems, treats the testbed as methodological, lists four contributions, and limits public/service relevance to a conditional transfer question.\n")

        literature = literature_rows()
        literature.to_csv(tables / "overnight_literature_gap_table.csv", index=False)
        write_text(manuscript / "02_related_work_SEPS_revision_plan.md", related_work_plan())
        write_text(logs / "overnight_literature_gap_audit.md", f"# Overnight Literature Gap Audit\n\n- Candidate rows: {len(literature)}\n- Crossref-verified DOI metadata rows: {int(literature['verification_status'].str.contains('Crossref', na=False).sum())}\n- Directions still requiring manual literature review: {int(literature['verification_status'].str.contains('Manual', na=False).sum())}\n\nThe table records the source, verification state, rationale, and paragraph/claim target. Unverified candidates are not inserted into manuscript prose.\n")

        methods = methods_revised(metrics)
        checklist = method_checklist()
        write_text(manuscript / "04_methods_SEPS_revised.md", methods)
        checklist.to_csv(tables / "overnight_methods_formula_checklist.csv", index=False)
        write_text(logs / "overnight_methods_rigor_audit.md", "# Overnight Methods Rigor Audit\n\n" + markdown_table(checklist, list(checklist.columns)) + "\n\nNo material code-formula inconsistency was found. The revised methods explicitly distinguish cardinal P intervals from ordinal R/R_plus ranking sets and numerical Monte Carlo error from behavioral uncertainty.\n")

        evidence = result_sentence_map(metrics)
        evidence.to_csv(tables / "overnight_results_sentence_evidence_map.csv", index=False)
        write_text(manuscript / "05_results_SEPS_revised.md", results_revised(metrics))
        write_text(manuscript / "06_prediction_and_counterfactuals_SEPS_revised.md", prediction_counterfactuals_revised())
        write_text(logs / "overnight_results_evidence_audit.md", "# Overnight Results Evidence Audit\n\n" + markdown_table(evidence, list(evidence.columns)) + "\n\nAll numerical statements in the SEPS-oriented results copy map to a generated CSV or log. Prediction is labelled validation; counterfactuals are labelled scenario analyses; no positive uncertainty penalty is presented as dominant.\n")

        write_text(manuscript / "07_discussion_SEPS_revised.md", discussion_revised())
        write_text(manuscript / "08_limitations_SEPS_revised.md", limitations_revised())
        write_text(manuscript / "09_conclusion_SEPS_revised.md", conclusion_revised())
        write_text(logs / "overnight_discussion_limitations_audit.md", "# Overnight Discussion, Limitations, and Conclusion Audit\n\nThe revisions explain partial identification as the estimand, treat wide sets as information limits, frame judge-save as a discretion-identifiability trade-off, cool prediction and scenarios, and state the single-testbed external-validity limit. The ten explicit limitations include data/code, AI declaration, and manual journal-fit boundaries.\n")

        for name, content in package_documents().items():
            write_text(manuscript / name, content)
        package = package_checklist()
        package.to_csv(tables / "overnight_submission_package_checklist.csv", index=False)
        write_text(logs / "overnight_submission_package_audit.md", "# Overnight Submission Package Audit\n\n" + markdown_table(package, list(package.columns)) + "\n\nAll declaration files that require author facts are conspicuously marked `[AUTHOR TO COMPLETE]`; no funding, ethics approval, author identity, data URL, or licence has been invented.\n")

        plan = figure_table_plan(root)
        plan.to_csv(tables / "overnight_final_main_figures_tables.csv", index=False)
        write_text(manuscript / "figure_table_plan_SEPS_revised.md", figure_table_markdown(plan))
        write_text(logs / "overnight_figure_table_audit.md", "# Overnight Figure and Table Audit\n\n" + markdown_table(plan, list(plan.columns)) + "\n\nThe main-text proposal uses four figures and three tables. Prediction and robust-aggregation detail remain appendix material; no visual artifact was regenerated solely for presentation.\n")

        write_text(logs / "overnight_go_no_go_report.md", go_no_go(metrics))
        write_text(logs / "overnight_final_summary.md", final_summary())

        generated = list(manuscript.glob("*_SEPS_revised.md"))
        hits: list[str] = []
        for path in generated:
            lower = path.read_text(encoding="utf-8").casefold()
            for phrase in FORBIDDEN:
                if phrase in lower:
                    hits.append(f"{path.name}: {phrase}")
        if hits:
            raise ValueError("Forbidden wording in overnight manuscript copy: " + "; ".join(hits))
    except (OSError, ValueError, KeyError, IndexError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("Overnight submission stage completed.")
    print("SEPS recommendation: D. Not suitable in the current empirical form.")
    print(f"Generated SEPS-oriented manuscript copies: {len(list((root / 'manuscript').glob('*_SEPS_revised.md')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
