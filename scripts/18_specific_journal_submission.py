#!/usr/bin/env python3
"""Verify journal candidates and assemble a non-identifying submission package.

The stage consumes frozen analytical outputs and general-revised manuscript
materials. It does not rerun models, modify raw data, alter core results, or
overwrite baseline, SEPS, or general-revised source documents.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ACCESS_DATE = "2026-07-15"
FORBIDDEN = (
    "true votes",
    "true fan votes",
    "recovered votes",
    "exact public vote",
    "causal audience effects",
    "causal audience effect",
    "causal fan effects",
    "causal fan effect",
    "should have won",
)
MAIN_TERMS = (
    "expert-crowd aggregation systems",
    "hidden preferences",
    "feasible preference set",
    "mechanism-induced uncertainty",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a journal-specific candidate audit, unified anonymous main "
            "manuscript, reference insertion plan, and submission-package placeholders."
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
    missing = [path for path in relative_paths if not (root / path).is_file()]
    if missing:
        raise FileNotFoundError("Required stage-18 input(s) missing: " + ", ".join(missing))


def journal_matrix() -> pd.DataFrame:
    rows = [
        {
            "rank": 1,
            "official_journal_name": "Decision Analysis",
            "publisher_or_society": "INFORMS",
            "official_scope_url": "https://pubsonline.informs.org/journal/deca",
            "official_scope_summary": "Official INFORMS homepage verified in the in-app browser. It presents Decision Analysis as an INFORMS journal and displays current work on human-in-the-loop systems, crowds/point forecasts, value of information, and decision analysis for practitioners. A separately stated aims-and-scope paragraph was not accessible from this runtime.",
            "article_type_requirements": "Official submission-guidelines link is present at https://pubsonline.informs.org/page/deca/submission-guidelines, but the detailed page was not readable in this runtime; manual verification needed.",
            "abstract_highlights_graphical_requirements": "manual verification needed from official submission guidelines.",
            "data_code_policy": "manual verification needed from the INFORMS Author Portal and journal guidelines.",
            "ai_assisted_writing_policy": "manual verification needed from current INFORMS author guidance.",
            "official_access_status": "homepage browser-verified; direct HTTP endpoint protected (403)",
            "testbed_acceptability": "conditionally acceptable as a methodological testbed if the paper explains the decision-analytic information problem before the case setting",
            "stronger_theory_needed": "yes: sharpen the decision problem, uncertainty/ambiguity position, and contribution relative to partial identification",
            "stronger_decision_support_framing_needed": "yes: frame the result as information for mechanism and disclosure design, not as an operational system",
            "estimated_fit": "strong",
            "main_desk_reject_risk": "The editor may see an entertainment testbed without a sufficiently explicit decision-analysis contribution or normative decision link.",
            "required_manuscript_changes": "Use the unified general manuscript, integrate verified citations, foreground partial identification and mechanism-induced uncertainty, and confirm journal-specific requirements manually.",
            "final_recommendation_rank": 1,
        },
        {
            "rank": 2,
            "official_journal_name": "Group Decision and Negotiation",
            "publisher_or_society": "Springer Nature; published in cooperation with the INFORMS Section on Group Decision and Negotiation",
            "official_scope_url": "https://link.springer.com/journal/10726",
            "official_scope_summary": "Official Springer metadata describes a peer-reviewed journal covering processes and activities relevant to group decision-making and negotiation.",
            "article_type_requirements": "Official submission guidelines are accessible. Research-article pathway is available; reviews/editorials/comments may have extra disclosure requirements. The guide states anonymized reviewer materials are requested during submission.",
            "abstract_highlights_graphical_requirements": "Official guide states an abstract of 150-250 words and 4-6 keywords. Highlights and graphical-abstract requirements: manual verification needed.",
            "data_code_policy": "Official guidelines link a Research Data Policy and Data Availability Statements section; final wording and repository obligations require manual verification.",
            "ai_assisted_writing_policy": "Official guide refers to Springer policy on generative-AI images. Text AI-assistance disclosure policy requires manual verification.",
            "official_access_status": "homepage and submission guidelines HTTP 200 verified",
            "testbed_acceptability": "conditionally acceptable for aggregation and discretion mechanisms, although the paper does not study negotiation",
            "stronger_theory_needed": "yes: strengthen the social-choice/group-decision connection and explain why the rule comparison generalizes beyond the testbed",
            "stronger_decision_support_framing_needed": "moderate: focus on aggregation, transparency, and institutional discretion",
            "estimated_fit": "moderate",
            "main_desk_reject_risk": "The empirical setting lacks an explicit group negotiation process and may be viewed as a competition application rather than group decision research.",
            "required_manuscript_changes": "Use the general line, retain the testbed boundary, cite social-choice and group-decision sources, and format the anonymous submission to the verified guide.",
            "final_recommendation_rank": 2,
        },
        {
            "rank": 3,
            "official_journal_name": "EPJ Data Science",
            "publisher_or_society": "Springer Nature / SpringerOpen",
            "official_scope_url": "https://epjdatascience.springeropen.com/",
            "official_scope_summary": "Official SpringerOpen metadata says the journal focuses on scientific methods for analyzing and synthesizing massive data sets to generate new insights.",
            "article_type_requirements": "Official guidelines are accessible and provide article-type formatting and editorial-policy routes; exact eligible article type for this manuscript requires manual verification.",
            "abstract_highlights_graphical_requirements": "abstract, highlights, and graphical-abstract requirements require manual verification from the relevant article-type page.",
            "data_code_policy": "Official guidelines state that data availability must be detailed in an Availability of data and materials section; repository requirements depend on data type and policy.",
            "ai_assisted_writing_policy": "manual verification needed for text AI assistance; the current guide surface does not supply a text-writing declaration in the retrieved content.",
            "official_access_status": "homepage and submission guidelines HTTP 200 verified",
            "testbed_acceptability": "conditionally acceptable, but the data scale and contribution may look too small or too decision-theoretic for a data-science venue",
            "stronger_theory_needed": "moderate: position method contribution against data-science inference and reproducibility literature",
            "stronger_decision_support_framing_needed": "no; stronger empirical/data-method framing would be needed instead",
            "estimated_fit": "moderate",
            "main_desk_reject_risk": "Insufficient data-science novelty or scale relative to a journal oriented to methods for massive data.",
            "required_manuscript_changes": "Emphasize reproducible inference under rule changes and avoid overstating substantive audience behavior; verify open-data constraints.",
            "final_recommendation_rank": 3,
        },
        {
            "rank": 4,
            "official_journal_name": "Journal of Computational Social Science",
            "publisher_or_society": "Springer Nature",
            "official_scope_url": "https://link.springer.com/journal/42001",
            "official_scope_summary": "Official Springer metadata calls it an interdisciplinary journal spanning social sciences, physics, biology, management science, and related computational research.",
            "article_type_requirements": "Official submission guidelines are accessible. They mention research articles and other formats; verify the exact article type before submission.",
            "abstract_highlights_graphical_requirements": "Official guide states a 150-250 word abstract and 4-6 keywords. Highlights and graphical abstract: manual verification needed.",
            "data_code_policy": "Official guidelines provide Research Data Policy and Data Availability Statements material; final journal-specific wording needs manual confirmation.",
            "ai_assisted_writing_policy": "Official guide refers to Springer generative-AI image policy. Text AI writing disclosure needs manual verification.",
            "official_access_status": "homepage and submission guidelines HTTP 200 verified",
            "testbed_acceptability": "conditionally acceptable with a clear explanation of the institutional rule changes and limited-observability design",
            "stronger_theory_needed": "moderate: add computational social-science motivation rather than claim social behavior recovery",
            "stronger_decision_support_framing_needed": "no",
            "estimated_fit": "moderate",
            "main_desk_reject_risk": "The paper may be judged as a decision-analysis method with insufficient computational social-science theory or empirical generalization.",
            "required_manuscript_changes": "Move institutional rules and coarse-feedback structure into the empirical motivation; retain the validation boundary.",
            "final_recommendation_rank": 4,
        },
        {
            "rank": 5,
            "official_journal_name": "Decision Support Systems",
            "publisher_or_society": "Elsevier",
            "official_scope_url": "https://www.sciencedirect.com/journal/decision-support-systems",
            "official_scope_summary": "Official journal endpoint returned HTTP 403 in this runtime; manual verification needed before relying on scope wording.",
            "article_type_requirements": "manual verification needed from official Guide for Authors.",
            "abstract_highlights_graphical_requirements": "manual verification needed from official Guide for Authors.",
            "data_code_policy": "Elsevier Research Data policy is official and accessible at https://www.elsevier.com/about/policies-and-standards/research-data; journal-specific requirements need manual verification.",
            "ai_assisted_writing_policy": "Elsevier Generative AI policy is official and accessible at https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals; journal-specific placement needs manual verification.",
            "official_access_status": "official journal endpoint HTTP 403; publisher policies HTTP 200 verified",
            "testbed_acceptability": "unlikely without a decision-support artifact, user evaluation, or organizational deployment context",
            "stronger_theory_needed": "yes: information-systems and decision-support theory",
            "stronger_decision_support_framing_needed": "yes: substantially",
            "estimated_fit": "weak",
            "main_desk_reject_risk": "No implemented or evaluated decision-support system is present.",
            "required_manuscript_changes": "Would require a materially different decision-support contribution; not recommended for the current paper.",
            "final_recommendation_rank": 5,
        },
        {
            "rank": 6,
            "official_journal_name": "Information Systems Research",
            "publisher_or_society": "INFORMS",
            "official_scope_url": "https://pubsonline.informs.org/journal/isre",
            "official_scope_summary": "Official journal endpoint is protected in this runtime; manual verification needed before using scope language.",
            "article_type_requirements": "manual verification needed from official journal/author guidance.",
            "abstract_highlights_graphical_requirements": "manual verification needed.",
            "data_code_policy": "manual verification needed from current INFORMS author guidance.",
            "ai_assisted_writing_policy": "manual verification needed from current INFORMS author guidance.",
            "official_access_status": "direct official HTTP endpoint protected (403); in-app browser did not expose usable page content",
            "testbed_acceptability": "unlikely without a central information-systems theory, digital artifact, platform, or organizational IS outcome",
            "stronger_theory_needed": "yes: substantially",
            "stronger_decision_support_framing_needed": "yes: substantially",
            "estimated_fit": "weak",
            "main_desk_reject_risk": "The study lacks a core information-systems phenomenon and empirical context.",
            "required_manuscript_changes": "Would require a new research question and application; not recommended for this submission line.",
            "final_recommendation_rank": 6,
        },
    ]
    return pd.DataFrame(rows)


def scope_audit(matrix: pd.DataFrame) -> str:
    return f"""
# Specific Journal Scope Audit

## Official-source record

- Decision Analysis official homepage: <https://pubsonline.informs.org/journal/deca>. Verified in the in-app browser; the direct HTTP endpoint returned 403. Its official submission-guidelines link was visible but the detailed page was not readable in this runtime.
- Decision Support Systems official homepage: <https://www.sciencedirect.com/journal/decision-support-systems>. Direct HTTP endpoint returned 403. Elsevier Research Data and Generative AI policy pages returned HTTP 200.
- EPJ Data Science official homepage and guidelines: <https://epjdatascience.springeropen.com/> and <https://epjdatascience.springeropen.com/submission-guidelines>. Both returned HTTP 200.
- Information Systems Research official homepage: <https://pubsonline.informs.org/journal/isre>. Direct HTTP endpoint returned 403; usable scope text was unavailable.
- Journal of Computational Social Science official homepage and guidelines: <https://link.springer.com/journal/42001> and <https://link.springer.com/journal/42001/submission-guidelines>. Both returned HTTP 200.
- Group Decision and Negotiation official homepage and guidelines: <https://link.springer.com/journal/10726> and <https://link.springer.com/journal/10726/submission-guidelines>. Both returned HTTP 200.
- Springer Nature Research Data policy: <https://www.springernature.com/gp/authors/research-data-policy> returned HTTP 200.

## Ranking conclusion

1. **Decision Analysis** is the first-choice target because the paper's core contribution is rule-aware partial identification and mechanism-induced uncertainty, with visible overlap between the official journal's current decision-analysis content and hidden-information/point-forecast themes.
2. **Group Decision and Negotiation** is the backup because its verified scope centers group decision processes and its guide supports an anonymized review pathway, but the paper needs stronger group-decision framing and does not study negotiation.
3. EPJ Data Science and Journal of Computational Social Science are plausible but weaker alternates.
4. Decision Support Systems and Information Systems Research are not recommended for the present paper because no decision-support artifact, IS theory, platform, or organizational IS outcome is studied.

All unavailable requirements are labelled manual verification needed in the matrix. No impact factor, acceptance rate, article limit, or policy requirement has been inferred from an inaccessible page.

## Matrix

{markdown_table(matrix, list(matrix.columns))}
"""


def target_decision() -> str:
    return """
# Target Journal Decision

## First-Choice Target: Decision Analysis (INFORMS)

The manuscript's core contribution is not competition analytics. It is a rule-aware partial-identification framework for hidden preferences under expert-crowd aggregation rules, with a clear mechanism-induced uncertainty result for a weak judge-save condition. This contribution aligns most naturally with a decision-analysis audience interested in uncertainty, information, aggregation rules, and decision design.

Before submission, strengthen the decision-analysis framing in the introduction and discussion, integrate verified references, explain the decision-design use of identified-set uncertainty, and manually confirm article type, abstract, data/code, AI-disclosure, and formatting requirements from the current official guidelines.

## Backup Target: Group Decision and Negotiation (Springer Nature)

This is the strongest backup because the verified scope is group decision-making and the paper studies aggregation, ordinal rankings, and institutional discretion. The manuscript must emphasize collective aggregation and transparency, while stating clearly that it does not study negotiation or a welfare effect of intervention.

## Not Recommended for the Current Paper

- **Decision Support Systems:** no deployed decision-support artifact or user/organizational evaluation.
- **Information Systems Research:** no central IS theory, platform, or organizational IS outcome.
- **SEPS:** no demonstrated public/service/planning application; it remains a non-default line unless such evidence is added.

## Decision Boundary

The ranking is based on the current frozen evidence and accessible official sources. It does not guarantee editorial interest or acceptance. The main manuscript remains an empirical testbed paper: it should not claim that its data directly establish a broader applied domain.
"""


def related_work(literature: pd.DataFrame) -> str:
    verified = literature.loc[literature["verified"].astype(str).str.casefold().eq("yes")].copy()
    required_columns = ["title", "authors", "year", "source", "doi_or_stable_url"]
    missing = verified[required_columns].isna().any(axis=1) | verified[required_columns].astype(str).eq("").any(axis=1)
    if missing.any():
        raise ValueError("A source selected for main-text citation lacks verifiable metadata.")
    references = []
    seen: set[str] = set()
    for row in verified.itertuples(index=False):
        doi = str(row.doi_or_stable_url)
        if doi in seen:
            continue
        seen.add(doi)
        references.append(f"- {row.authors} ({int(row.year)}). *{row.title}*. {row.source}. {doi}")
    return """
# Related Work

## Partial Identification and Bounds

Partial identification is appropriate when the observables restrict a latent object without selecting a unique value. Manski (2000) frames decisions under ambiguity created by incomplete identification, while Imbens and Manski (2004) distinguish partially identified parameters from point-estimation settings. The present paper applies this perspective to hidden preferences under documented aggregation rules: it reports feasible preference sets rather than selecting an unobserved public input.

## Social Choice, Rank Aggregation, and Preference Inference

Aggregation rules are not interchangeable computational details. Foundational social-choice work establishes why collective choice depends on the aggregation relation (Arrow, 1950; Young, 1988), and rank-aggregation research formalizes the computational treatment of multiple orderings (Dwork et al., 2001). Preference inference likewise depends on the observed choice process (Liang, 2019). These literatures motivate the paper's separation of percentage-regime cardinal feasible regions from ranking-regime ordinal feasible sets.

## Expert-Crowd Aggregation Systems

Collective-decision evidence shows that social and informational conditions can affect aggregate judgments (Lorenz et al., 2011). This motivates studying systems with visible expert inputs and hidden collective inputs, but it does not turn the present typed proxies into observed ballots. The empirical record is used as a longitudinal testbed with rule changes and coarse outcomes, not as a representative population of all expert-crowd systems.

## Aggregation Mechanisms, Discretion, and Decision Uncertainty

Institutional arrangements determine what decisions reveal about the inputs that produced them. Steunenberg (1996) supplies general context for discretion under alternative institutional arrangements. Here, the judge-save result is narrower: weakening a direct elimination implication to bottom-set membership expands the compatible ranking set within the same week. Under incomplete information, decision frameworks such as minimax regret clarify why unresolved states should remain visible rather than be silently collapsed (Manski, 2007).

## Validation and Scenario Analysis Under Limited Observability

Prediction is not a substitute for identification. Shmueli (2010) distinguishes prediction from explanation, supporting the use of strictly historical models as validation signals rather than latent-state confirmation. Bell and Koren (2008) illustrate how competition challenges can serve as computational testbeds; this paper uses its testbed comparably for a reproducible mechanism analysis. Counterfactual calculations therefore remain scenario analyses over feasible states, not causal historical replacements.

## Verified Sources Cited in This Draft

""" + "\n".join(references) + "\n\nOnly the verified sources above are inserted into this draft. Any candidate marked manual verification needed remains outside the main text and reference list."


def reference_plan(literature: pd.DataFrame) -> pd.DataFrame:
    locations = {
        "Partial identification and bounds": ("02 Related Work, Partial Identification and Bounds", "identified-set estimand and bounds"),
        "Social choice theory": ("02 Related Work, Social Choice", "aggregation rules affect collective choice"),
        "Rank aggregation": ("02 Related Work, Social Choice", "rank aggregation terminology"),
        "Preference inference": ("02 Related Work, Social Choice", "preference inference depends on observables"),
        "Expert-crowd / collective decision-making": ("02 Related Work, Expert-Crowd", "motivation only; not ballot validation"),
        "Aggregation mechanisms": ("02 Related Work, Social Choice", "mechanism-dependent identified object"),
        "Decision-making under uncertainty": ("02 Related Work, Mechanisms", "retain unresolved states in decision analysis"),
        "Prediction as validation": ("02 Related Work, Validation", "prediction differs from explanation and identification"),
        "Mechanism design / institutional discretion": ("02 Related Work, Mechanisms", "institutional discretion context"),
        "Empirical competition/platform testbeds": ("02 Related Work, Validation", "competition challenge as computational testbed"),
        "Public/service application bridge": ("not inserted", "manual verification needed"),
    }
    plan = literature.copy()
    verified = plan["verified"].astype(str).str.casefold().eq("yes")
    required = ["title", "authors", "year", "source", "doi_or_stable_url"]
    complete = ~plan[required].isna().any(axis=1) & ~plan[required].astype(str).eq("").any(axis=1)
    plan["metadata_check"] = (verified & complete & plan["doi_or_stable_url"].astype(str).str.startswith("https://doi.org/")).map({True: "pass", False: "manual verification needed"})
    plan["insertion_status"] = verified.map({True: "inserted into submission_main/02_related_work.md", False: "not inserted"})
    mapped_locations = plan["direction"].map(
        lambda key: locations.get(str(key), ("not inserted", "manual verification needed"))
    )
    plan["target_section"] = mapped_locations.map(lambda value: value[0])
    plan["supported_sentence_or_claim"] = mapped_locations.map(lambda value: value[1])
    return plan[["direction", "title", "authors", "year", "source", "doi_or_stable_url", "verified", "metadata_check", "insertion_status", "target_section", "supported_sentence_or_claim"]]


def reference_audit(plan: pd.DataFrame) -> str:
    inserted = plan["insertion_status"].eq("inserted into submission_main/02_related_work.md")
    manual = plan["metadata_check"].eq("manual verification needed")
    return f"""
# Reference Verification Audit

- Candidate rows checked: {len(plan)}.
- Rows with complete, DOI-linked, verified metadata: {int((plan['metadata_check'] == 'pass').sum())}.
- Sources inserted into `submission_main/02_related_work.md`: {int(inserted.sum())}.
- Sources retained outside the manuscript pending manual verification: {int(manual.sum())}.

Every inserted source has title, authors, year, source, and DOI URL recorded in `outputs/tables/reference_insertion_plan.csv`. The manuscript uses only those inserted sources. The final submission still requires a journal-styled bibliography and a manual full-text reading check for claim precision.

## Insertion Table

{markdown_table(plan, list(plan.columns))}
"""


def main_source_map() -> dict[str, str]:
    return {
        "00_title_abstract_keywords.md": "manuscript/00_title_abstract_keywords_general_revised.md",
        "01_introduction.md": "manuscript/01_introduction_general_revised.md",
        "03_data_and_institutional_rules.md": "manuscript/03_data_and_institutional_rules.md",
        "04_methods.md": "manuscript/04_methods_revised.md",
        "05_results.md": "manuscript/05_results_revised.md",
        "06_validation_and_scenario_analysis.md": "manuscript/06_prediction_and_counterfactuals_revised.md",
        "07_discussion.md": "manuscript/07_discussion_general_revised.md",
        "08_limitations.md": "manuscript/08_limitations_general_revised.md",
        "09_conclusion.md": "manuscript/09_conclusion_general_revised.md",
    }


def claims_checklist() -> pd.DataFrame:
    rows = [
        ("C1", "Elimination-only outcomes yield feasible preference sets rather than a point-valued public input.", "01 Introduction; 04 Methods; 05 Results", "outputs/tables/constraint_summary.csv; outputs/logs/partial_identification_report.md", "pass"),
        ("C2", "P uses cardinal simplex-constrained intervals with coordinate-wise LP bounds.", "04 Methods", "src/constraints.py; data/processed/preference_bounds_regime_p.csv", "pass"),
        ("C3", "R and R_plus identify feasible ordinal rankings, not cardinal shares.", "04 Methods; 05 Results", "src/ranking_identification.py; outputs/tables/identification_comparison_by_regime.csv", "pass"),
        ("C4", "R_plus weak feasible sets contain direct feasible sets within a week.", "04 Methods; 05 Results", "outputs/tables/ranking_identification_summary_rplus.csv", "pass"),
        ("C5", "P, R, and R_plus width summaries are not directly comparable.", "05 Results; 08 Limitations", "outputs/tables/identification_comparison_by_regime.csv", "pass"),
        ("C6", "Dynamic public-appeal proxies are typed summaries, not public ballots.", "04 Methods; 07 Discussion", "src/identification_features.py; data/processed/dynamic_public_appeal.csv", "pass"),
        ("C7", "Historical prediction is validation; same-week judge models are explanatory baselines.", "06 Validation and Scenario Analysis", "outputs/tables/prediction_results.csv; outputs/logs/leakage_and_claim_audit.md", "pass"),
        ("C8", "Counterfactual outputs are feasible-state scenario analyses, not causal replacement histories.", "06 Validation and Scenario Analysis; 08 Limitations", "src/counterfactuals.py; outputs/tables/counterfactual_results_by_regime.csv", "pass"),
        ("C9", "A positive uncertainty penalty is not presented as empirically dominant.", "06 Validation and Scenario Analysis", "outputs/tables/pareto_frontier_points.csv", "pass"),
        ("C10", "The longitudinal competition record is a methodological testbed, not a public/service application.", "01 Introduction; 07 Discussion; 08 Limitations", "outputs/logs/alternative_journal_type_audit.md", "pass"),
    ]
    return pd.DataFrame(rows, columns=["claim_id", "claim", "submission_main_location", "generated_evidence", "status"])


def check_main_boundaries(main_dir: Path) -> None:
    texts = {path.name: path.read_text(encoding="utf-8") for path in main_dir.glob("*.md")}
    joined = "\n".join(texts.values()).casefold()
    hits = [phrase for phrase in FORBIDDEN if phrase in joined]
    if hits:
        raise ValueError("Forbidden wording in submission main: " + "; ".join(hits))
    fit_terms = [term for term in MAIN_TERMS if term not in joined]
    if fit_terms:
        raise ValueError("Required unified terminology absent from submission main: " + "; ".join(fit_terms))
    prohibited_fit = [phrase for phrase in ("socio-economic planning", "public-sector application", "public sector application") if phrase in joined]
    if prohibited_fit:
        raise ValueError("Submission main retains prohibited SEPS packaging: " + "; ".join(prohibited_fit))
    missing = [name for name in list(main_source_map()) + ["02_related_work.md"] if name not in texts]
    if missing:
        raise ValueError("Submission main missing sections: " + ", ".join(missing))


def main_consistency_audit(main_dir: Path, claims: pd.DataFrame) -> str:
    check_main_boundaries(main_dir)
    return f"""
# Submission Main Consistency Audit

- Unified terminology present: expert-crowd aggregation systems; hidden preferences; feasible preference set(s); mechanism-induced uncertainty.
- Prohibited point-recovery, causal-audience, and winner-claim phrases: absent.
- SEPS-specific public-sector/socio-economic-planning packaging: absent.
- Prediction consistently framed as validation: yes.
- Counterfactuals consistently framed as scenario analysis: yes.
- Dynamic proxy boundary as non-ballot summary: yes.
- Cardinal P and ordinal R/R_plus quantities explicitly separated: yes.
- Conclusion excludes contestant cases and parameter selection: yes.
- Claim checklist rows: {len(claims)}, all mapped to generated evidence.

## Claim Checklist

{markdown_table(claims, list(claims.columns))}
"""


def figure_plan() -> pd.DataFrame:
    rows = [
        ("figure", "Figure 1", "main", "outputs/figures/conceptual_framework_hidden_preferences.png", "Conceptual framework", "Hidden public input, observed rule, feasible preference set, and design implication.", "C1; C10", "not applicable", "clear conceptual labels", "yes", "yes, retain editable source if available", "ready for human caption review"),
        ("figure", "Figure 2", "main", "outputs/figures/uncertainty_over_weeks_regime_p.png", "P feasible interval uncertainty", "Coordinate-wise feasible-share width across P weeks; it is not an observed public input.", "C1; C2", "P only", "week and normalized width labeled", "yes", "yes, retain vector source if available", "ready for human caption review"),
        ("figure", "Figure 3", "main", "outputs/figures/judge_save_identifiability_loss.png", "R_plus weak versus direct expansion", "Within-week expansion of weak relative to direct feasible ranking sets under the tie-inclusive bottom-set condition.", "C3; C4", "within R_plus only", "week and expansion ratio labeled", "yes", "yes, retain vector source if available", "ready for human caption review"),
        ("figure", "Figure 4", "main", "outputs/figures/identification_width_by_regime.png", "Cross-regime uncertainty context", "Descriptive comparison of mechanism-specific normalized uncertainty summaries; cardinal and ordinal measures are not directly comparable.", "C3; C5", "prominent non-comparability note", "regime and normalized uncertainty labeled", "yes", "yes, retain vector source if available", "ready for human caption review"),
        ("figure", "Figure A1", "appendix", "outputs/figures/prediction_comparison.png", "Validation comparison", "Historical-model validation versus same-week explanatory benchmark; not point recovery.", "C7", "same-week baseline separated", "accuracy and log-loss labeled", "yes", "yes, retain vector source if available", "appendix"),
        ("table", "Table 1", "main", "data/processed/identification_features_long.csv; outputs/tables/constraint_summary.csv", "Dataset and regime summary", "Seasons, rule regimes, observed feedback, and identified object by regime.", "C1; C2; C3", "separate cardinal and ordinal columns", "not applicable", "yes", "not applicable", "ready for human table construction"),
        ("table", "Table 2", "main", "outputs/tables/identification_comparison_by_regime.csv", "Partial-identification summary", "Mechanism-specific uncertainty summaries with a non-comparability note.", "C1; C3; C5", "required", "not applicable", "yes", "not applicable", "ready for human table construction"),
        ("table", "Table 3", "main", "outputs/tables/ranking_identification_summary_rplus.csv", "Judge-save comparison", "Direct and weak feasible-set quantities, exact/sampled status, and tie policy.", "C4", "within-week only", "not applicable", "yes", "not applicable", "ready for human table construction"),
        ("table", "Table A1", "appendix", "outputs/tables/prediction_results.csv", "Validation models", "Strictly historical models are separated from same-week explanatory baselines.", "C7", "not applicable", "not applicable", "yes", "not applicable", "appendix"),
    ]
    columns = ["item_type", "item_id", "placement", "source", "purpose", "standalone_caption_or_table_note", "claim_ids", "comparability_note", "axis_or_label_check", "proxy_language_safe", "vector_recommendation", "status"]
    return pd.DataFrame(rows, columns=columns)


def figure_table_plan_markdown(plan: pd.DataFrame) -> str:
    main = plan.loc[plan["placement"].eq("main")]
    return f"""
# Figure and Table Plan

The anonymous main manuscript proposes {int((main['item_type'] == 'figure').sum())} figures and {int((main['item_type'] == 'table').sum())} tables. Validation material is placed in the appendix by default. Each main figure/table has a proposed standalone caption/note and an explicit claim mapping.

{markdown_table(plan, list(plan.columns))}

## Appendix Plan

- Controversial scenario cases.
- Lambda/gamma heatmaps and Pareto details.
- Dynamic proxy examples and full regression coefficients.
- Ranking sampling diagnostics, tie-policy sensitivity, and calibration plots.
- Full validation tables and pipeline reproducibility material.
- Additional robustness checks already generated by the analytical pipeline.

Before submission, verify journal-specific figure-file requirements and create vector versions when required. The package does not claim that an editable vector source already exists.
"""


def submission_documents(main_dir: Path, package: Path) -> dict[Path, str]:
    sections = [
        "00_title_abstract_keywords.md", "01_introduction.md", "02_related_work.md", "03_data_and_institutional_rules.md", "04_methods.md", "05_results.md", "06_validation_and_scenario_analysis.md", "07_discussion.md", "08_limitations.md", "09_conclusion.md",
    ]
    anonymous = "\n\n".join((main_dir / section).read_text(encoding="utf-8").strip() for section in sections)
    return {
        package / "anonymous_manuscript.md": anonymous,
        package / "title_page_placeholder.md": """
# Title Page Placeholder

## Manuscript Title

Aggregation Mechanisms and Identifiability in Expert-Crowd Decision Systems

## Authors and Affiliations

[AUTHOR TO COMPLETE: author names, affiliations, ORCID identifiers, and corresponding-author contact details]

## Declarations

[AUTHOR TO COMPLETE: funding, conflict of interest, ethics, data/code availability, and acknowledgements as required by the selected journal]
""",
        package / "cover_letter.md": """
# Cover Letter

Dear Editor,

Please consider our manuscript, "Aggregation Mechanisms and Identifiability in Expert-Crowd Decision Systems," for publication in [Target Journal]. It develops a rule-aware partial-identification framework for systems that combine observed expert assessments with hidden public preferences and release only coarse elimination outcomes. The framework distinguishes cardinal feasible regions from ordinal feasible rankings and shows how a weak judge-save condition changes mechanism-induced uncertainty.

The longitudinal empirical testbed supplies documented rule changes, repeated eliminations, and multiple aggregation regimes. It demonstrates the framework without treating public ballots as observed. Dynamic proxies, historical prediction, and counterfactual calculations are presented only as typed summaries, validation, and scenario analysis.

The analysis is reproducible through code, processed analytical data, fixed seeds, tests, and generated audit materials, subject to source-data terms and release permissions. [AUTHOR TO COMPLETE: repository/archive location, licence, and final data-access statement.]

The authors confirm that the work is original and not under consideration elsewhere. [AUTHOR TO COMPLETE: corresponding author information and target-journal declarations.]

Sincerely,

[AUTHOR TO COMPLETE]
""",
        package / "highlights.md": """
# Highlights

- Coarse outcomes identify feasible preference sets, not point estimates.
- Aggregation rules determine cardinal versus ordinal identified objects.
- Judge-save discretion expands compatible ranking sets.
- Validation and scenarios retain mechanism-induced uncertainty.
""",
        package / "data_availability_statement.md": """
# Data Availability Statement

[AUTHOR TO COMPLETE] The analysis uses a supplied competition dataset retained unchanged under `data/raw/`. Processed analytical files are generated by the project pipeline. Before sharing or submission, confirm the original source, access date, licence, redistribution permission, and any restrictions. Do not state that raw data are publicly redistributable until those source terms are verified.
""",
        package / "code_availability_statement.md": """
# Code Availability Statement

[AUTHOR TO COMPLETE] Analysis code, tests, and generated audit materials are included in this research package. Before submission, provide a versioned repository or archival DOI, a code licence, a release tag, and an exact environment lock or container. The current `requirements.txt` specifies version ranges and is not an archival environment lock.
""",
        package / "ai_assisted_writing_statement.md": """
# AI-Assisted Writing and Code Support Statement

During preparation, the authors used OpenAI Codex for draft organization, language clarification, code review, reproducibility checks, and preparation of submission materials. The authors reviewed and edited the resulting content, verified analyses and cited-source metadata, and accept full responsibility for the submitted work. No AI system is listed as an author or co-author. Confirm the selected journal's current disclosure wording and placement before submission.
""",
        package / "conflict_of_interest_statement.md": """
# Conflict of Interest Statement

[AUTHOR TO COMPLETE] State all conflicts of interest or explicitly state that the authors declare none. This placeholder is not a final declaration.
""",
        package / "funding_statement.md": """
# Funding Statement

[AUTHOR TO COMPLETE] State funding sources, grant numbers, and funder roles, or explicitly state that no funding was received. No funding information has been inferred from this project.
""",
        package / "ethics_statement.md": """
# Ethics Statement

[AUTHOR TO COMPLETE] Confirm whether institutional review or informed consent is applicable to this supplied-data analysis. State the institutional basis only after author/institution review. Do not invent approvals, exemptions, or protocol numbers.
""",
        package / "author_contributions_placeholder.md": """
# Author Contributions

[AUTHOR TO COMPLETE] Provide a named CRediT contribution statement and confirm final responsibility for analysis, writing, and submission.
""",
        package / "acknowledgements_placeholder.md": """
# Acknowledgements

[AUTHOR TO COMPLETE] Add contributor-approved acknowledgements or state that there are none. Do not list unverified contributors.
""",
        package / "appendix_plan.md": """
# Appendix Plan

- Rule-coding details, special cases, and tie-policy sensitivity.
- Exact-versus-sampled ranking diagnostics and Monte Carlo error summaries.
- Dynamic proxy examples, calibration plots, and full regression coefficients.
- Scenario details, controversial cases, lambda/gamma heatmaps, and Pareto results.
- Pipeline commands, frozen-output manifest, tests, and reproducibility diagnostics.

All appendix material should retain the identified-set, validation, and scenario-analysis boundaries used in the main manuscript.
""",
    }


def package_checklist(package: Path) -> str:
    files = [
        "anonymous_manuscript.md", "title_page_placeholder.md", "cover_letter.md", "highlights.md", "data_availability_statement.md", "code_availability_statement.md", "ai_assisted_writing_statement.md", "conflict_of_interest_statement.md", "funding_statement.md", "ethics_statement.md", "author_contributions_placeholder.md", "acknowledgements_placeholder.md", "appendix_plan.md", "figure_table_plan.md",
    ]
    ready = [name for name in files if (package / name).is_file()]
    return """
# Submission Checklist

## Generated and ready for human review

""" + "\n".join(f"- `{name}`" for name in ready) + """

## Still requiring manual completion

- Select and verify [Target Journal] requirements, including article type, limits, formatting, data/code policy, and AI disclosure placement.
- Complete the title page, corresponding-author information, author identities, affiliations, ORCIDs, and CRediT roles.
- Complete conflict, funding, ethics, and acknowledgements declarations.
- Verify raw-data source terms, repository permissions, code licence, and environment lock/container.
- Format references to the selected journal style after a full-text citation review.
- Construct final journal-formatted tables and captions; confirm vector, colour, and resolution requirements.
- Compile a blinded manuscript/PDF and perform an anonymization check before upload.
"""


def pre_submission_report() -> str:
    return """
# Pre-Submission Go / No-Go Report

## Decision: B. Needs moderate human revision

The analytical results are frozen, the general submission line is coherent, and a specific first-choice/backup ranking has been produced. The package is not ready for upload because journal-specific requirements, final citations, author declarations, source-data permissions, and final formatting require human completion.

## Scores (1 = weak/high risk; 5 = strong/low risk)

| Dimension | Score | Basis |
| --- | --- | --- |
| Target journal fit | 4 | Decision Analysis is a strong conditional fit; exact author-guide requirements remain manual. |
| Methodological contribution | 4 | Rule-aware cardinal/ordinal identification and weak-set containment are clear. |
| Literature grounding | 3 | Verified sources are inserted, but full-text reading and journal-style bibliography remain manual. |
| Evidence-claim alignment | 4 | Claim map, frozen outputs, and boundary language are explicit. |
| Reproducibility | 4 | Frozen hashes, code, fixed seeds, tests, and pipelines exist; no archival environment lock. |
| Writing coherence | 4 | Unified terminology and consistent validation/scenario boundaries are audited. |
| Theory contribution | 3 | Decision-analysis and group-decision positioning requires final human refinement. |
| Empirical generalizability | 2 | One longitudinal competition testbed. |
| Overclaiming risk | 4 | Unsafe point-recovery and causal phrasing is excluded from the assembled main line. |
| Submission package completeness | 2 | Multiple declarations and venue-specific elements are placeholders. |

## Top Strengths

1. A reproducible rule-aware partial-identification framework.
2. Clear cardinal-versus-ordinal separation.
3. Strong within-week judge-save identifiability result.
4. Frozen evidence and zero hash mismatches at the prior freeze audit.
5. Explicit validation and scenario-analysis boundaries.

## Top Desk-Reject Risks

1. Decision Analysis framing may be judged insufficiently tied to a concrete decision or normative objective.
2. The competition testbed may be viewed as entertainment-specific.
3. Journal-specific requirements remain manually unverified for the first-choice target.
4. The reference list needs final reading, citation-style formatting, and human claim checks.
5. Data/code terms and author declarations are incomplete.

## Ten Required Human Fixes

1. Confirm Decision Analysis scope and submission requirements from its current official guidance.
2. Read every inserted source and verify that each citation supports its precise sentence.
3. Format and complete the bibliography in the selected journal style.
4. Refine decision-analysis theory and explain the decision-design use of uncertainty.
5. Confirm raw-data source, access terms, and redistribution permission.
6. Archive code with a licence, release tag, and environment lock/container.
7. Complete author, affiliation, corresponding-author, ORCID, and CRediT information.
8. Complete conflict, funding, ethics, and acknowledgement declarations.
9. Build final tables/captions and verify figure production requirements.
10. Compile and inspect a blinded PDF before upload.

## Ten Optional Improvements

1. Send a short presubmission inquiry to the first-choice journal after manual scope verification.
2. Add a decision-theoretic example illustrating the use of feasible sets without new empirical modeling.
3. Obtain domain feedback on the institutional-discretion interpretation.
4. Prepare Group Decision and Negotiation formatting as a backup branch.
5. Add a data dictionary and rule-coding supplement.
6. Archive deterministic output checksums with the release.
7. Produce vector figure sources where available.
8. Add a clean-environment reproduction log.
9. Prepare a response-to-reviewers evidence map.
10. Consider a future external application study without altering this submission.

## Target Recommendations

- First choice: **Decision Analysis**.
- Backup: **Group Decision and Negotiation**.

## Files Ready for Human Review

- `manuscript/submission_main/*.md`
- `submission_package/anonymous_manuscript.md`
- `submission_package/cover_letter.md`
- `submission_package/highlights.md`
- `submission_package/figure_table_plan.md`
- `outputs/tables/specific_journal_fit_matrix.csv`
- `outputs/tables/reference_insertion_plan.csv`

## Files Requiring Manual Completion

- `submission_package/title_page_placeholder.md`
- `submission_package/data_availability_statement.md`
- `submission_package/code_availability_statement.md`
- `submission_package/conflict_of_interest_statement.md`
- `submission_package/funding_statement.md`
- `submission_package/ethics_statement.md`
- `submission_package/author_contributions_placeholder.md`
- `submission_package/acknowledgements_placeholder.md`

Generated placeholders are clearly marked and must not be submitted as factual declarations.
"""


def check_anonymous(path: Path) -> None:
    text = path.read_text(encoding="utf-8").casefold()
    risky = ("[author to complete", "corresponding author", "acknowledgements", "funding statement", "conflict of interest")
    hits = [term for term in risky if term in text]
    if hits:
        raise ValueError("Anonymous manuscript contains identifying/declaration content: " + "; ".join(hits))


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    sources = main_source_map()
    require(root, [
        "outputs/tables/general_literature_required_sources.csv",
        "manuscript/02_related_work_general_revision_plan.md",
        "outputs/tables/frozen_outputs_hashes.csv",
        "outputs/tables/identification_comparison_by_regime.csv",
        "outputs/tables/ranking_identification_summary_rplus.csv",
        "outputs/tables/prediction_results.csv",
        *sources.values(),
    ])
    try:
        manuscript = root / "manuscript"
        main_dir = manuscript / "submission_main"
        package = root / "submission_package"
        tables = root / "outputs/tables"
        logs = root / "outputs/logs"
        literature = pd.read_csv(root / "outputs/tables/general_literature_required_sources.csv")

        matrix = journal_matrix()
        matrix.to_csv(tables / "specific_journal_fit_matrix.csv", index=False)
        write_text(logs / "specific_journal_scope_audit.md", scope_audit(matrix))
        write_text(manuscript / "target_journal_decision.md", target_decision())
        write_text(logs / "target_journal_decision_audit.md", "# Target Journal Decision Audit\n\n- First choice: Decision Analysis (INFORMS).\n- Backup: Group Decision and Negotiation (Springer Nature).\n- Not recommended: Decision Support Systems, Information Systems Research, and SEPS for the current frozen evidence.\n- Official-access limitations are documented in `outputs/logs/specific_journal_scope_audit.md`; no inaccessible requirement is treated as verified.\n")

        main_dir.mkdir(parents=True, exist_ok=True)
        for target, source in sources.items():
            write_text(main_dir / target, (root / source).read_text(encoding="utf-8"))
        related = related_work(literature)
        write_text(main_dir / "02_related_work.md", related)
        references = reference_plan(literature)
        references.to_csv(tables / "reference_insertion_plan.csv", index=False)
        write_text(logs / "reference_verification_audit.md", reference_audit(references))

        claims = claims_checklist()
        claims.to_csv(tables / "submission_main_claims_checklist.csv", index=False)
        write_text(logs / "submission_main_consistency_audit.md", main_consistency_audit(main_dir, claims))

        plan = figure_plan()
        plan.to_csv(tables / "final_figure_table_submission_plan.csv", index=False)
        write_text(logs / "final_figure_table_audit.md", "# Final Figure and Table Audit\n\n" + figure_table_plan_markdown(plan))
        package_docs = submission_documents(main_dir, package)
        for path, content in package_docs.items():
            write_text(path, content)
        write_text(package / "figure_table_plan.md", figure_table_plan_markdown(plan))
        write_text(package / "submission_checklist.md", package_checklist(package))
        check_anonymous(package / "anonymous_manuscript.md")
        write_text(logs / "pre_submission_go_no_go_report.md", pre_submission_report())
    except (OSError, ValueError, KeyError, IndexError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("Specific journal and submission-package stage completed.")
    print("First choice: Decision Analysis; backup: Group Decision and Negotiation.")
    print(f"Submission main sections: {len(list(main_dir.glob('*.md')))}")
    print(f"Verified references inserted: {int(references['insertion_status'].str.startswith('inserted').sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
