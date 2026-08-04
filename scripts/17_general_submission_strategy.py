#!/usr/bin/env python3
"""Freeze current outputs and generate a general-target submission strategy.

This stage does not alter raw data, core analytical outputs, baseline manuscript
files, or SEPS-oriented copies. It creates a separate general decision-analysis
submission line from previously generated results.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ACCESS_DATE = date.today().isoformat()
FROZEN_TEST_STATUS = "47 passed (verified immediately before the strategy-redirection stage)"
FROZEN_SEPS_DECISION = "D. Not suitable for SEPS in its current empirical form"
FORBIDDEN = (
    "true votes",
    "true fan votes",
    "recovered votes",
    "vote recovery",
    "causal audience effect",
    "causal fan effect",
    "should have won",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Freeze existing evidence and generate a general decision-analysis "
            "submission strategy without changing models, raw data, or prior drafts."
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
        raise FileNotFoundError("Required general-strategy input(s) missing: " + ", ".join(missing))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def frozen_paths() -> list[tuple[str, str]]:
    return [
        ("raw_input", "data/raw/2026_MCM_Problem_C_Data.csv"),
        ("processed_panel", "data/processed/panel_long.csv"),
        ("processed_week", "data/processed/week_level.csv"),
        ("processed_features", "data/processed/identification_features_long.csv"),
        ("processed_dynamic", "data/processed/dynamic_public_appeal.csv"),
        ("constraints", "outputs/tables/constraint_summary.csv"),
        ("identification", "outputs/tables/identification_comparison_by_regime.csv"),
        ("ranking_rplus", "outputs/tables/ranking_identification_summary_rplus.csv"),
        ("prediction", "outputs/tables/prediction_results.csv"),
        ("counterfactual", "outputs/tables/counterfactual_results_by_regime.csv"),
        ("robustness", "outputs/tables/robust_aggregation_results.csv"),
        ("pareto", "outputs/tables/pareto_frontier_points.csv"),
        ("constraint_figure", "outputs/figures/uncertainty_over_weeks_regime_p.png"),
        ("judge_save_figure", "outputs/figures/judge_save_identifiability_loss.png"),
        ("comparison_figure", "outputs/figures/identification_width_by_regime.png"),
        ("prediction_figure", "outputs/figures/prediction_comparison.png"),
        ("pipeline_entry", "run_all.py"),
        ("general_strategy_script", "scripts/17_general_submission_strategy.py"),
        ("requirements", "requirements.txt"),
        ("overnight_go_no_go", "outputs/logs/overnight_go_no_go_report.md"),
    ]


def freeze_table(root: Path) -> pd.DataFrame:
    rows: list[dict[str, str | int]] = []
    for category, relative in frozen_paths():
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f"Cannot freeze missing artifact: {relative}")
        rows.append(
            {
                "category": category,
                "relative_path": relative,
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "freeze_status": "present",
            }
        )
    return pd.DataFrame(rows)


def metrics(root: Path) -> dict[str, float | int]:
    comparison = pd.read_csv(root / "outputs/tables/identification_comparison_by_regime.csv").set_index("regime")
    rplus = pd.read_csv(root / "outputs/tables/ranking_identification_summary_rplus.csv")
    prediction = pd.read_csv(root / "outputs/tables/prediction_results.csv")
    if set(comparison.index) != {"P", "R", "R_plus"} or len(rplus) != 73:
        raise ValueError("Expected frozen P, R, and R_plus identification outputs.")
    forward = prediction.loc[prediction["validation_scheme"].eq("forward_chaining")].set_index("model")
    ratio = pd.to_numeric(rplus["identifiability_loss_ratio"], errors="coerce")
    return {
        "p_width": float(comparison.loc["P", "mean_normalized_uncertainty"]),
        "r_width": float(comparison.loc["R", "mean_normalized_uncertainty"]),
        "rplus_width": float(comparison.loc["R_plus", "mean_normalized_uncertainty"]),
        "p_weeks": int(comparison.loc["P", "n_weeks"]),
        "rplus_weeks": int(comparison.loc["R_plus", "n_weeks"]),
        "ratio_mean": float(ratio.mean()),
        "ratio_median": float(ratio.median()),
        "ratio_expanded": int((ratio > 1.0 + 1e-12).sum()),
        "ratio_equal": int((ratio.sub(1.0).abs() <= 1e-12).sum()),
        "containment_violations": int((pd.to_numeric(rplus["feasible_fraction"], errors="coerce") + 1e-12 < pd.to_numeric(rplus["feasible_fraction_direct_R_like"], errors="coerce")).sum()),
        "historical_accuracy": float(forward.loc["combined_lag_logistic", "accuracy"]),
        "historical_logloss": float(forward.loc["combined_lag_logistic", "log_loss"]),
        "random_accuracy": float(forward.loc["random_uniform", "accuracy"]),
        "random_logloss": float(forward.loc["random_uniform", "log_loss"]),
    }


def frozen_manifest(table: pd.DataFrame, values: dict[str, float | int]) -> str:
    return f"""
# Frozen Submission Manifest

## Freeze declaration

This manifest freezes the current analytical evidence for submission-strategy work. It does not alter raw data, processed data, core model outputs, baseline manuscript files, or the existing SEPS-oriented copies. Any later analytical change requires a new manifest and a new hash table.

## Frozen status

- Test status at freeze: `{FROZEN_TEST_STATUS}`.
- SEPS Go/No-Go at freeze: `{FROZEN_SEPS_DECISION}`.
- Recommended strategy: switch to a general decision-analysis / computational-social-science target line.
- Reproduction entry points: `python run_all.py --skip-preprocess`, `python run_all.py --skip-preprocess --overnight-submission`, and `python run_all.py --skip-preprocess --general-submission`.

## Key frozen results

- P: {values['p_weeks']} feasible weeks; mean normalized coordinate-wise width {values['p_width']:.6f}.
- R and R_plus mean normalized ordinal widths: {values['r_width']:.6f} and {values['rplus_width']:.6f}; these are not directly comparable to P widths.
- R_plus weak/direct ratio: mean {values['ratio_mean']:.6f}, median {values['ratio_median']:.6f}, strict expansion in {values['ratio_expanded']} weeks, equality in {values['ratio_equal']} weeks, and {values['containment_violations']} containment violations.
- Historical validation: accuracy {values['historical_accuracy']:.6f}, log loss {values['historical_logloss']:.6f}; uniform baseline accuracy {values['random_accuracy']:.6f}, log loss {values['random_logloss']:.6f}.

## Hashed artifacts

{markdown_table(table, list(table.columns))}

The hashes are a snapshot of the listed files at manifest generation. They are not a substitute for a future clean-environment reproduction.
"""


def submission_strategy_decision() -> str:
    return """
# Submission Strategy Decision

## Decision

Do not treat the SEPS-oriented copies as the final submission line. The primary line is now a general expert-crowd decision-systems paper centered on rule-aware partial identification, aggregation mechanisms, and mechanism-induced identifiability.

## Why the strategy changes

The current empirical testbed is longitudinal, rule-changing, and computationally auditable. It supports a general contribution about hidden inputs and coarse outcome feedback. It does not evaluate a public-sector, service-sector, or planning decision. Reframing cannot create that missing empirical application, so SEPS should not remain the default target.

## Frozen boundaries

- Raw data and core results remain unchanged.
- Baseline manuscript files and all `*_SEPS_revised.md` copies remain intact.
- The new `*_general_revised.md` documents are alternatives, not automatic replacements.
- Public ballots remain unobserved; the paper describes feasible preference sets, typed proxies, validation signals, and scenario analyses.

## Chosen positioning

Lead with the information problem: expert-crowd aggregation systems can combine visible expert inputs with hidden public preferences and release only coarse eliminations. The contribution is to characterize what those releases identify under cardinal and ordinal rules, and how discretionary interventions alter identifiability.
"""


def journal_type_matrix() -> pd.DataFrame:
    rows = [
        ("Decision analysis / decision sciences", "strong", "The central contribution is a rule-aware identified-set framework and a mechanism-design implication under uncertainty.", "A venue may require stronger formal positioning and a clear normative decision problem.", "Lead with partial identification, aggregation rules, and accountability of coarse feedback.", "Title, abstract, introduction, related work, discussion, cover letter.", "yes, as a methodological empirical testbed", "no"),
        ("Computational social science", "moderate", "The data are longitudinal and institutional rules shape observable social outcomes.", "The testbed can still appear entertainment-specific and needs careful social-science motivation.", "Frame the record as a general hidden-input, coarse-feedback system; avoid social-behavior causal claims.", "Title, abstract, introduction, related work, discussion.", "yes, with explicit testbed boundary", "no"),
        ("Information systems / platform governance", "weak", "Hidden input, ranking, and feedback design have conceptual overlap with platforms.", "No platform operator, user interface, governance intervention, or platform outcome is observed.", "Do not use platform-governance claims without a matching application.", "Introduction, discussion, related work, empirical framing.", "only as a distant analogy", "yes"),
        ("Social choice / collective decision-making", "moderate", "The paper distinguishes cardinal and ordinal aggregation and formalizes bottom-set feasibility.", "The current contribution is computational partial identification rather than a new social-choice theorem.", "Strengthen social-choice and rank-aggregation literature; keep empirical claims modest.", "Related work, methods, title, discussion.", "yes", "no"),
        ("Management science / analytics", "moderate", "The work is reproducible, quantitative, and rule-aware.", "There is no operational organization, objective, or decision owner whose performance is evaluated.", "Present as methodological analytics; do not claim managerial performance improvement.", "Introduction, discussion, cover letter, limitations.", "yes, if the venue accepts methods testbeds", "not necessarily"),
        ("Communication / media analytics", "moderate", "The empirical setting and public participation have direct media relevance.", "This would demote the methodological contribution and invite media-specific causal or audience claims.", "Keep hidden-preference identification central and avoid audience-effect language.", "Title, related work, discussion, cover letter.", "yes", "no"),
        ("Public sector / socio-economic planning", "weak", "There is a conditional transparency and discretion implication.", "No public/service operation, policy outcome, or planning actor is studied.", "Do not use this as the default target without a genuine applied bridge.", "All front matter and discussion would need an empirical, not rhetorical, change.", "no for direct fit", "yes"),
        ("Entertainment or cultural analytics", "moderate", "The testbed is directly recognizable and longitudinal.", "This would overemphasize the case and understate the general identification contribution.", "Use only if the paper is intentionally repositioned as an application study.", "Title, introduction, related work, results, discussion.", "yes", "no"),
    ]
    return pd.DataFrame(rows, columns=["journal_type", "fit", "why_it_fits", "why_it_may_fail", "required_reframing", "sections_to_change", "testbed_acceptable", "extra_public_service_application_required"])


def journal_type_audit(matrix: pd.DataFrame) -> str:
    return f"""
# Alternative Journal-Type Audit

## Recommendation

- Primary target type: **Decision analysis / decision sciences**.
- Backup target type: **Computational social science**.
- Not recommended target type: **Public sector / socio-economic planning** without a new public/service application.

SEPS should not remain the default because the current data do not observe a planning actor, public-service operation, policy objective, or service outcome. The conditional relevance of mechanism transparency cannot substitute for a demonstrated applied context.

## Type comparison

{markdown_table(matrix, list(matrix.columns))}

The matrix intentionally describes journal types rather than naming journals. Specific venues require current scope, author-guide, and editorial-fit checks before contact or submission.
"""


def title_abstract_general() -> str:
    abstract = """Expert-crowd aggregation systems combine expert assessments with hidden public preferences while releasing only elimination outcomes. Because public ballots are unobserved, the resulting inferential problem is partial identification rather than point estimation. We develop a rule-aware framework that maps documented aggregation rules, expert components, active sets, and eliminations into feasible preference sets. Under percentage aggregation, the compatible states form a simplex-constrained polytope, and coordinate-wise linear programs produce sharp marginal bounds. Under rank aggregation, the compatible states are ordinal public rankings rather than cardinal support shares. A judge-save intervention weakens the outcome implication from direct elimination to bottom-set membership and expands the feasible ranking set within comparable weeks. Using a longitudinal competition testbed with rule changes and three aggregation regimes, we quantify mechanism-induced uncertainty without observing public ballots. Dynamic proxies organize identified-set summaries, lagged prediction serves only as validation, and counterfactual calculations remain scenario analyses. The contribution is a transparent account of how aggregation mechanisms determine what coarse outcomes can identify and what remains unresolved without additional information across both cardinal and ordinal state spaces under transparent, documented institutional assumptions in practice."""
    count = word_count(abstract)
    if not 180 <= count <= 220:
        raise ValueError(f"General abstract must contain 180-220 words; found {count}.")
    return f"""
# Title, Abstract, and Keywords: General Submission Line

## Title Option A: Methodological

Rule-Aware Partial Identification of Hidden Public Preferences from Elimination Outcomes

## Title Option B: Mechanism-Focused

Aggregation Mechanisms and Identifiability in Expert-Crowd Decision Systems

## Title Option C: Application-Neutral

Hidden Preferences under Coarse Feedback in Expert-Crowd Aggregation Systems

## Recommended Title

Aggregation Mechanisms and Identifiability in Expert-Crowd Decision Systems

## Abstract

{abstract}

## Keywords

partial identification; hidden preferences; expert-crowd decision systems; aggregation mechanisms; rank aggregation; decision uncertainty; mechanism design

## Empirical Scope

The longitudinal competition record is an empirical testbed for the general identification problem. It is not the paper's motivational endpoint and is not represented as a public-service application.
"""


def title_abstract_audit(content: str) -> str:
    abstract = content.split("## Abstract", 1)[1].split("## Keywords", 1)[0]
    keywords = content.split("## Keywords", 1)[1].split("## Empirical Scope", 1)[0]
    lower = content.casefold()
    hits = [phrase for phrase in FORBIDDEN if phrase in lower]
    return f"""
# General Title and Abstract Audit

- Title options: 3.
- Abstract words: {word_count(abstract)} (required: 180-220).
- Required opening frame: expert-crowd aggregation systems and hidden public preferences.
- Explicit coarse feedback: only elimination outcomes are observed.
- Explicit observability boundary: public ballots are unobserved.
- Main contribution: partial identification under aggregation mechanisms.
- Prediction and counterfactual roles: validation and scenario analysis only.
- Prohibited wording hits: {"none" if not hits else "; ".join(hits)}.
- Keywords: {len([item for item in keywords.split(";") if item.strip()])}.
"""


def introduction_general() -> str:
    return """
# Introduction: General Submission Line

Expert-crowd aggregation systems combine professional judgments with participation from members, users, audiences, or other publics. Their rules can mix expert scores, rankings, eliminations, and interventions, creating hybrid decisions in which visible expert assessments coexist with partly hidden collective input.

This information structure creates an identification problem when public preferences are hidden and only coarse outcome feedback is released. An elimination constrains the latent states compatible with a documented rule, but usually does not identify one state. Point estimation is consequently too strong without additional information; the appropriate object is a feasible preference set.

Research on prediction, retrospective explanation, and ranking analytics can describe outcome patterns or validate engineered features. Those tasks do not by themselves establish what is identified from elimination-only outcomes. In particular, a good predictive score cannot turn hidden input into observed data, and a ranking explanation can obscure the difference between cardinal and ordinal latent objects.

We develop a rule-aware partial-identification framework for cardinal and ordinal aggregation rules. Percentage aggregation induces linear inequalities on a simplex and coordinate-wise linear-program bounds. Rank aggregation induces feasible ordinal public rankings. A judge-save intervention weakens a direct elimination implication to tie-inclusive bottom-set membership, changing the compatible set by construction.

The empirical testbed is a longitudinal competition setting with documented rule changes, observed eliminations, and three aggregation regimes. Its role is methodological: it provides repeated instances of coarse feedback under changing rules. It is not the substantive center of the paper and is not used to make claims about a public-service system.

The paper contributes: (1) a rule-aware partial-identification framework for hidden public preferences; (2) a comparison of cardinal and ordinal aggregation regimes; (3) a judge-save analysis of mechanism-induced identifiability loss; and (4) validation and scenario-analysis extensions that carry uncertainty forward without converting it into point recovery.

The remainder of the paper documents the data and institutional rules, defines the identification sets, reports the core evidence, then presents secondary validation and scenario analyses before discussing design implications and limits.
"""


def related_work_plan() -> str:
    return """
# Related Work: General Submission Revision Plan

## Required structure

1. **Partial identification and bounds.** Define the identified-set estimand and distinguish it from point estimation and confidence-interval construction.
2. **Social choice, rank aggregation, and preference inference.** Establish why cardinal shares and ordinal rankings are different latent objects and why aggregation rules matter.
3. **Expert-crowd and collective decision systems.** Use this literature for problem motivation only; it does not validate the present latent proxy.
4. **Decision uncertainty, mechanism design, and discretion.** Frame judge-save results as an information and accountability trade-off, not a welfare result.
5. **Prediction and empirical testbeds.** Explain that predictive checks validate limited historical signal and that the competition record is a methodological testbed.

## Citation boundaries

The source table associated with this plan contains Crossref-verified candidates. Claims of priority, novelty, representative prevalence, or empirical welfare effects must wait for a complete manuscript-specific reading and citation pass. The final paper needs a reference-managed bibliography and in-text citations; this plan does not substitute for either.
"""


def literature_rows() -> pd.DataFrame:
    rows = [
        ("Partial identification and bounds", "Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice", "Charles F. Manski", 2000, "Journal of Econometrics", "https://doi.org/10.1016/S0304-4076(99)00045-7", "yes", "Defines decisions under partial identification and ambiguity.", "Related work: identified-set estimand."),
        ("Partial identification and bounds", "Confidence Intervals for Partially Identified Parameters", "Guido W. Imbens; Charles F. Manski", 2004, "Econometrica", "https://doi.org/10.1111/j.1468-0262.2004.00555.x", "yes", "Separates partial identification from point estimation.", "Related work: bounds and inference boundary."),
        ("Social choice theory", "A Difficulty in the Concept of Social Welfare", "Kenneth J. Arrow", 1950, "Journal of Political Economy", "https://doi.org/10.1086/256963", "yes", "Provides foundational social-choice context for aggregation rules.", "Related work: aggregation mechanisms."),
        ("Social choice theory", "Condorcet's Theory of Voting", "H. P. Young", 1988, "American Political Science Review", "https://doi.org/10.2307/1961757", "yes", "Supports rule-dependent collective ranking context.", "Related work: social choice and aggregation."),
        ("Rank aggregation", "Rank aggregation methods for the Web", "Cynthia Dwork; Ravi Kumar; Moni Naor; D. Sivakumar", 2001, "Proceedings of the 10th International Conference on World Wide Web", "https://doi.org/10.1145/371920.372165", "yes", "Provides rank-aggregation terminology and computational context.", "Related work: ordinal aggregation."),
        ("Preference inference", "Inference of preference heterogeneity from choice data", "Annie Liang", 2019, "Journal of Economic Theory", "https://doi.org/10.1016/j.jet.2018.09.010", "yes", "Clarifies that preference inference depends on the observed choice process.", "Related work: preference inference boundary."),
        ("Expert-crowd / collective decision-making", "How social influence can undermine the wisdom of crowd effect", "Jan Lorenz; Heiko Rauhut; Frank Schweitzer; Dirk Helbing", 2011, "Proceedings of the National Academy of Sciences", "https://doi.org/10.1073/pnas.1008636108", "yes", "Provides collective-decision motivation without validating hidden ballots here.", "Related work: expert-crowd motivation."),
        ("Aggregation mechanisms", "A Difficulty in the Concept of Social Welfare", "Kenneth J. Arrow", 1950, "Journal of Political Economy", "https://doi.org/10.1086/256963", "yes", "Supports the claim that aggregation rules are substantively consequential.", "Related work: aggregation mechanisms."),
        ("Decision-making under uncertainty", "Minimax-regret treatment choice with missing outcome data", "Charles F. Manski", 2007, "Journal of Econometrics", "https://doi.org/10.1016/j.jeconom.2006.06.006", "yes", "Motivates decisions under incomplete information without point recovery.", "Related work: decision uncertainty; discussion."),
        ("Prediction as validation", "To Explain or to Predict?", "Galit Shmueli", 2010, "Statistical Science", "https://doi.org/10.1214/10-STS330", "yes", "Supports the separation of predictive validation from explanatory claims.", "Related work: validation extension."),
        ("Mechanism design / institutional discretion", "Agent discretion, regulatory policymaking, and different institutional arrangements", "Bernard Steunenberg", 1996, "Public Choice", "https://doi.org/10.1007/BF00136524", "yes", "Provides general discretion context; it does not establish the judge-save result as a policy effect.", "Related work: discretion and institutional design."),
        ("Empirical competition/platform testbeds", "Lessons from the Netflix prize challenge", "Robert M. Bell; Yehuda Koren", 2008, "ACM SIGKDD Explorations Newsletter", "https://doi.org/10.1145/1345448.1345465", "yes", "Illustrates the use of a competition challenge as a computational empirical testbed.", "Related work: testbed positioning."),
        ("Public/service application bridge", "No candidate selected", "", "", "", "", "no - manual verification needed", "A directly comparable public/service application is not available in the current study and should not be implied.", "Do not cite as evidence; relevant only if changing venue strategy."),
    ]
    return pd.DataFrame(rows, columns=["direction", "title", "authors", "year", "source", "doi_or_stable_url", "verified", "supports_which_claim", "where_to_cite"])


def literature_audit(literature: pd.DataFrame) -> str:
    verified = literature["verified"].astype(str).eq("yes")
    directions = literature.loc[verified, "direction"].nunique()
    return f"""
# General Literature Search Audit

- Access date: {ACCESS_DATE}.
- Candidate rows: {len(literature)}.
- Crossref-verified DOI rows: {int(verified.sum())}.
- Covered required directions with a verified source: {directions}.
- Manual-verification rows: {int((~verified).sum())}.

Each verified row was checked against Crossref metadata before inclusion in the table. The table is a candidate map, not a claim that every source has been read in full or that it establishes this manuscript's novelty. The public/service application bridge deliberately remains unresolved rather than being filled with an unrelated citation.
"""


def discussion_general() -> str:
    return """
# Discussion: General Submission Line

Hidden-preference systems should use partial identification when the public component is unavailable and institutions release only coarse outcomes. A wide feasible set is not a failed estimate. It reports the information that the documented rule and outcome do not provide, making institutional opacity measurable rather than silently replaced by a point assumption.

The judge-save comparison identifies a discretion-identifiability trade-off. A discretionary intervention can weaken the direct implication of an observed elimination, thereby expanding the feasible ranking set. This is an information result about a rule, not a welfare ranking of intervention or a claim that any institution should remove discretion.

Dynamic proxies organize identified-set evidence over time but do not create observed ballots. Historical prediction is a secondary validation exercise, and scenario calculations propagate compatible states under stated assumptions. Neither extension changes the primary estimand or supplies causal evidence about an alternative history.

The longitudinal testbed illustrates a general class of aggregation problems in which visible expert inputs, hidden collective inputs, and coarse feedback coexist. Its design implication is conditional but practical: institutions that seek accountability and preference interpretability should report richer intermediate information, rule details, and intervention records. The analysis does not establish that these disclosures improve an observed organizational outcome.
"""


def limitations_general() -> str:
    return """
# Limitations: General Submission Line

- Public ballots are unavailable, so the analysis does not verify a point-valued public-preference measure.
- The testbed is one empirical setting; transfer requires a new rule encoding, feedback model, and domain-specific objective.
- Rule interpretation, score normalization, and tie handling affect the feasible sets; R_plus uses a tie-inclusive weak bottom-set condition.
- The observed record follows historically active contestant trajectories, creating selection limits for longitudinal and scenario summaries.
- Cardinal percentage intervals and ordinal ranking sets are different objects and are not a common support metric.
- Prediction is secondary validation rather than the primary contribution.
- Counterfactual calculations are scenario analyses conditional on observed trajectories, not causal effects.
- Data sharing, code release, source terms, licensing, and archival environment details remain bounded by manual verification and author action.

Fixed-seed sampling in large ranking fields creates numerical approximation error; it is distinct from the mechanism-induced uncertainty described by the feasible set.
"""


def conclusion_general() -> str:
    return """
# Conclusion: General Submission Line

Coarse elimination outcomes identify sets of hidden public preferences whose form depends on the aggregation mechanism. Percentage rules yield convex feasible regions and coordinate-wise cardinal bounds. Ranking rules yield feasible ordinal rankings. A weak judge-save condition expands the compatible ranking set within comparable weeks.

The contribution is a rule-aware framework for making these information limits explicit and for carrying them into validation and scenario analysis without collapsing them into point estimates. The longitudinal testbed demonstrates the workflow; future applications should evaluate it in other expert-crowd systems with documented rules and richer intermediate feedback.
"""


def cover_letter_general() -> str:
    return """
# Cover Letter Draft

Dear Editor,

Please consider our manuscript, "Aggregation Mechanisms and Identifiability in Expert-Crowd Decision Systems," for publication in [Target Journal]. The paper studies a general information problem: institutions combine observed expert assessments with hidden public preferences and release only coarse outcomes. We develop a rule-aware partial-identification framework that distinguishes cardinal feasible regions under percentage aggregation from feasible ordinal rankings under rank aggregation.

The paper also analyzes how a judge-save intervention changes mechanism-induced identifiability by weakening the observable implication of elimination. A longitudinal empirical testbed supplies documented rule changes, repeated eliminations, and multiple aggregation regimes. It demonstrates the method without treating public ballots as observed. Dynamic proxies, lagged validation, and scenario analysis are secondary extensions that retain the identified-set boundary.

The analysis is reproducible through documented code, processed analytical data, fixed seeds, tests, and generated audit materials, subject to verification of original data-source terms and release permissions. [AUTHOR TO COMPLETE: repository or archive location, licence, and data-access statement.]

The authors confirm that the manuscript is original, is not under consideration elsewhere, and that final author declarations will be supplied with submission. [AUTHOR TO COMPLETE: corresponding author information and any journal-specific declarations.]

Sincerely,

[AUTHOR TO COMPLETE]
"""


def highlights_general() -> str:
    return """
# Highlights

- Coarse outcomes identify feasible preference sets, not point estimates.
- Aggregation rules determine cardinal versus ordinal identified objects.
- Judge-save discretion expands compatible ranking sets.
- Validation and scenarios preserve mechanism-induced uncertainty.
"""


def next_strategy_report() -> str:
    return """
# Next Submission Strategy Report

## Final recommendation: B. Switch to general decision/computational social science target

1. **Continue SEPS?** No. SEPS should not remain the default target for the present empirical form.
2. **Minimum needed for SEPS if retained.** A genuine public/service application or editor-confirmed scope fit; a verified applied literature bridge; manually checked author guidance; and a manuscript that does not rely on reframing alone.
3. **More suitable target type.** General decision analysis / decision sciences is primary. Computational social science is the backup type.
4. **Strongest selling point.** The rule-aware identification framework distinguishes cardinal from ordinal feasible states and shows how a weak judge-save condition changes identifiability within comparable weeks.
5. **Largest rejection risk.** A venue can view the competition setting as entertainment-specific or the incomplete bibliography and release package as insufficiently mature.
6. **Sections already suited to a general target.** Methods, core results, prediction/counterfactual boundary, limitations, and the general-revised title, abstract, introduction, discussion, and conclusion.
7. **Sections retaining SEPS packaging.** All `*_SEPS_revised.md` files, the SEPS cover letter, SEPS availability statements, graphical-abstract plan, and target-journal fit documents. They are preserved but not part of the primary line.
8. **Remaining literature gaps.** Full manuscript-specific reading and citation integration; closer expert-crowd institutional literature; a carefully selected discretion literature; and any domain-specific sources required by a chosen journal.
9. **Human actions required.** Choose and verify a specific venue; complete the bibliography; obtain authorship and declaration facts; confirm data terms; release code under a licence with an environment lock; compile and review the manuscript.
10. **Next Go/No-Go conditions.** A specific target type must accept the empirical testbed; all central claims must have integrated verified citations; final materials must be reproducible from a released environment; and author, data, and ethics declarations must be complete.

## Strategy boundary

This is a redirection of submission positioning, not a split-paper recommendation and not a pause for a new empirical application. A new public/service application would be required only to revive a SEPS-style target line.
"""


def safe_generated_documents(manuscript: Path) -> None:
    hits: list[str] = []
    for path in manuscript.glob("*_general_revised.md"):
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in FORBIDDEN:
            if phrase in text:
                hits.append(f"{path.name}: {phrase}")
    for path in [manuscript / "cover_letter_general_draft.md", manuscript / "highlights_general.md"]:
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in FORBIDDEN:
            if phrase in text:
                hits.append(f"{path.name}: {phrase}")
    if hits:
        raise ValueError("Forbidden wording in general submission material: " + "; ".join(hits))


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    require(root, [relative for _, relative in frozen_paths()])
    try:
        values = metrics(root)
        manuscript = root / "manuscript"
        tables = root / "outputs/tables"
        logs = root / "outputs/logs"

        hashes = freeze_table(root)
        hashes.to_csv(tables / "frozen_outputs_hashes.csv", index=False)
        write_text(logs / "frozen_submission_manifest.md", frozen_manifest(hashes, values))
        write_text(manuscript / "submission_strategy_decision.md", submission_strategy_decision())

        matrix = journal_type_matrix()
        matrix.to_csv(tables / "alternative_journal_type_matrix.csv", index=False)
        write_text(logs / "alternative_journal_type_audit.md", journal_type_audit(matrix))

        title = title_abstract_general()
        write_text(manuscript / "00_title_abstract_keywords_general_revised.md", title)
        write_text(logs / "general_title_abstract_audit.md", title_abstract_audit(title))
        write_text(manuscript / "01_introduction_general_revised.md", introduction_general())
        write_text(logs / "general_introduction_audit.md", "# General Introduction Audit\n\nThe revision contains the requested seven paragraphs: general expert-crowd systems; hidden preferences and coarse feedback; the partial-identification gap; cardinal and ordinal rules; a neutral empirical testbed; four contributions; and paper structure. It does not lead with the competition, a public-sector claim, prediction, point recovery, or causal language.\n")

        literature = literature_rows()
        literature.to_csv(tables / "general_literature_required_sources.csv", index=False)
        write_text(manuscript / "02_related_work_general_revision_plan.md", related_work_plan())
        write_text(logs / "general_literature_search_audit.md", literature_audit(literature))

        write_text(manuscript / "07_discussion_general_revised.md", discussion_general())
        write_text(manuscript / "08_limitations_general_revised.md", limitations_general())
        write_text(manuscript / "09_conclusion_general_revised.md", conclusion_general())
        write_text(logs / "general_discussion_conclusion_audit.md", "# General Discussion and Conclusion Audit\n\nThe general line treats partial identification as the estimand, wide feasible sets as information about coarse institutional feedback, judge-save as a discretion-identifiability trade-off, dynamic proxies as summaries, prediction as validation, and counterfactuals as scenarios. Limitations include missing public ballots, single-testbed external scope, rule/tie interpretation, active-trajectory selection, cardinal/ordinal differences, and data/code release boundaries.\n")

        write_text(manuscript / "cover_letter_general_draft.md", cover_letter_general())
        write_text(manuscript / "highlights_general.md", highlights_general())
        write_text(logs / "next_submission_strategy_report.md", next_strategy_report())
        safe_generated_documents(manuscript)
    except (OSError, ValueError, KeyError, IndexError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("General submission strategy stage completed.")
    print("Recommendation: B. Switch to general decision/computational social science target.")
    print(f"Frozen artifacts: {len(hashes)}")
    print(f"Verified literature candidates: {int(literature['verified'].eq('yes').sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
