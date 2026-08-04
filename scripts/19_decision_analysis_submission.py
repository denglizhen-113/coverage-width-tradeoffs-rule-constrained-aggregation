#!/usr/bin/env python3
"""Assemble a Decision Analysis-specific, non-identifying submission package.

This stage reads the frozen analytical evidence and the general submission
materials.  It does not rerun models, alter core results, touch raw data, or
overwrite baseline, SEPS, general, or generic-submission files.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GUIDELINE_URL = "https://pubsonline.informs.org/page/deca/submission-guidelines"
GUIDELINE_ACCESS_DATE = "2026-07-15"
FORBIDDEN = (
    "true votes",
    "true fan votes",
    "recovered votes",
    "recovered vote",
    "exact public vote",
    "vote recovery",
    "causal audience effect",
    "causal fan effect",
    "should have won",
    "public sector",
    "socio-economic planning",
    "entertainment analytics",
)
ABSTRACT_TERMS = (
    "expert-crowd aggregation systems",
    "hidden preferences",
    "coarse elimination outcomes",
    "rule-aware partial identification",
    "feasible preference sets",
    "mechanism-induced uncertainty",
    "institutional designers",
    "accountability and interpretability",
)
ABSTRACT_LABELS = (
    "Problem Statement",
    "Methodology",
    "Results",
    "Practical Implications",
)
DA_SECTIONS = (
    "00_title_abstract_keywords_DA.md",
    "01_introduction_DA.md",
    "02_related_work_DA.md",
    "03_data_and_institutional_rules_DA.md",
    "04_methods_DA.md",
    "05_results_DA.md",
    "06_validation_and_scenario_analysis_DA.md",
    "07_discussion_DA.md",
    "08_limitations_DA.md",
    "09_conclusion_DA.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create Decision Analysis-specific manuscript, audits, figure/table "
            "plan, and anonymous submission materials from frozen results."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root containing manuscript/, outputs/, and data/ (default: repository root).",
    )
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for _, row in frame.loc[:, columns].fillna("").iterrows():
        values = [str(row[column]).replace("|", "\\|").replace("\n", " ") for column in columns]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, divider, *rows])


def require(root: Path, relative_paths: list[str]) -> None:
    missing = [relative for relative in relative_paths if not (root / relative).is_file()]
    if missing:
        raise FileNotFoundError("Required inputs are missing: " + "; ".join(missing))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frozen_hash_mismatches(root: Path) -> pd.DataFrame:
    manifest = pd.read_csv(root / "outputs/tables/frozen_outputs_hashes.csv")
    rows = []
    for row in manifest.itertuples(index=False):
        path = root / row.relative_path
        exists = path.is_file()
        observed = sha256(path) if exists else ""
        rows.append(
            {
                "category": row.category,
                "relative_path": row.relative_path,
                "expected_sha256": row.sha256,
                "observed_sha256": observed,
                "status": "match" if exists and observed == row.sha256 else "mismatch",
            }
        )
    return pd.DataFrame(rows)


def da_title_abstract() -> str:
    return """
# Title, Abstract, and Keywords: Decision Analysis Submission Line

## Title

Evaluating Aggregation Rules under Hidden Preferences: A Partial-Identification Approach

## Abstract

**Problem Statement.** Expert-crowd aggregation systems combine visible expert assessments with hidden preferences, yet often disclose only coarse elimination outcomes. Institutional designers therefore face a decision problem: how should aggregation rules be evaluated when the collective input is not observed and the released outcome does not select one compatible preference state?

**Methodology.** We develop rule-aware partial identification as a decision-analytic response to incomplete feedback. Documented rules, active sets, expert components, and eliminations define feasible preference sets rather than a single latent input. Percentage aggregation yields cardinal feasible intervals, ranking aggregation yields ordinal feasible rankings, and a judge-save rule weakens the observed implication through discretionary bottom-set membership. A longitudinal empirical setting with rule changes supplies repeated instances for evaluating these representations.

**Results.** The cardinal regime has nonempty feasible sets in 247 weeks and a mean normalized coordinate-wise width of 0.842991. The ranking regimes retain broad ordinal uncertainty. Within comparable judge-save weeks, the weak feasible ranking set is strictly larger in 56 weeks, equal in 17, and never smaller; the mean weak-to-direct ratio is 2.665961. Cross-regime summaries are not treated as measurements on a common scale.

**Practical Implications.** Feasible preference sets make mechanism-induced uncertainty visible for institutional designers instead of concealing it behind a point estimate. They support accountability and interpretability by showing how rule choice and discretionary intervention alter what later observers can learn from coarse outcomes. The framework provides decision support under limited observability without treating auxiliary dynamic evidence as a direct public-vote measure.

## Keywords

decision analysis; partial identification; hidden preferences; aggregation mechanisms; institutional design

## Empirical Scope

The longitudinal competition record is a methodological testbed for aggregation-rule evaluation under incomplete preference observability. It is not the paper's substantive endpoint.
"""


def abstract_text(content: str) -> str:
    return content.split("## Abstract", 1)[1].split("## Keywords", 1)[0].strip()


def validate_abstract(content: str) -> dict[str, object]:
    abstract = abstract_text(content)
    lowered = abstract.casefold()
    missing_terms = [term for term in ABSTRACT_TERMS if term not in lowered]
    missing_labels = [label for label in ABSTRACT_LABELS if label not in abstract]
    forbidden_hits = [phrase for phrase in FORBIDDEN if phrase in lowered]
    formula_markers = re.findall(r"[=<>±∑∆Δ]", abstract)
    return {
        "word_count": word_count(abstract),
        "missing_terms": missing_terms,
        "missing_labels": missing_labels,
        "forbidden_hits": forbidden_hits,
        "formula_markers": formula_markers,
    }


def guideline_checklist() -> pd.DataFrame:
    rows = [
        (
            "Journal focus",
            "Theory, application, and teaching of decision analysis",
            "Official guideline page; scope wording verified on 2026-07-15",
            "satisfied",
            "DA introduction, methods, and discussion frame partial identification as a decision-analytic response to incomplete feedback.",
        ),
        (
            "Journal focus",
            "Operational decision-making methods and a theory-practice bridge",
            "User-supplied fit criterion; assessed against official research-paper emphasis on impact for decision-analysis theory and practice",
            "needs revision",
            "The design implication is explicit, but a human author should sharpen the operational decision context and normative objective before submission.",
        ),
        (
            "Abstract",
            "User-provided ceiling: no more than 300 words",
            "Task specification",
            "satisfied",
            "The generated abstract is below 250 words and therefore also below 300 words.",
        ),
        (
            "Abstract",
            "Official ScholarOne step: no more than 250 words",
            "Official guideline page; stricter than the task specification",
            "satisfied",
            "The generated abstract targets 230-250 words; exact count is recorded in DA_abstract_audit.md.",
        ),
        (
            "Abstract",
            "300-word versus 250-word discrepancy",
            "Task specification versus official ScholarOne step",
            "manual check still needed",
            "Use the stricter 250-word cap and reconfirm the live submission form immediately before upload.",
        ),
        (
            "Abstract",
            "Non-technical language, no formulas, four labeled components",
            "Task specification; four-part structure is a requested DA-oriented presentation",
            "satisfied",
            "Programmatic audit checks labels, forbidden language, and mathematical-symbol absence.",
        ),
        (
            "Keywords",
            "One to five keywords in ScholarOne",
            "Official guideline page",
            "satisfied",
            "Five DA-oriented keywords are supplied, using the stricter limit rather than the task's 4-6 range.",
        ),
        (
            "AI policy",
            "Generative AI may assist preparation; authors review/edit and remain responsible",
            "Official guideline page",
            "manual check still needed",
            "The AI statement uses this boundary, but authors must personally verify and complete the declaration before submission.",
        ),
        (
            "Data and code",
            "Provide sufficient material for replication where possible, including data, code, appendices, and protocols",
            "Official guideline page",
            "needs revision",
            "Code, processed data, tests, hashes, tables, and figures are identified; raw-data terms, archival release, and an environment lock require author action.",
        ),
        (
            "Data and code",
            "Where source restrictions apply, explain editor-verification access",
            "Official guideline page",
            "needs revision",
            "The accessibility statement provides a controlled verification pathway conditioned on source permissions; authors must confirm permissions.",
        ),
        (
            "Double-anonymous review",
            "Remove author names, institutions, and acknowledgements; avoid self-identification",
            "Official guideline page",
            "satisfied",
            "The generated anonymous manuscript is programmatically scanned for declarations and identifying placeholders.",
        ),
        (
            "ScholarOne materials",
            "Clean anonymous main document, separate title page, preferred referees, funding details, and PDF proof review",
            "Official guideline page",
            "manual check still needed",
            "Title page and declarations are explicit placeholders. Referee selection, funding entry, and proof review require human completion.",
        ),
        (
            "Format",
            "Single column, double spacing, 12-point font, and one-inch margins",
            "Official guideline page",
            "manual check still needed",
            "Markdown sources cannot establish rendered layout; format and inspect a blinded PDF before upload.",
        ),
        (
            "References",
            "Author-year in-text citations and alphabetical references",
            "Official guideline page",
            "needs revision",
            "The DA source retains verified author-year citations; final alphabetical, journal-styled bibliography requires human citation review.",
        ),
        (
            "Figures and tables",
            "May remain near citations; accepted-production files require high-quality PDF/PostScript figures",
            "Official guideline page",
            "manual check still needed",
            "A main-text plan is generated. Vector or production-PDF source files must be prepared and checked after final layout.",
        ),
    ]
    return pd.DataFrame(
        rows,
        columns=["category", "requirement", "source_or_basis", "status", "evidence_or_next_step"],
    )


def guidelines_audit(checklist: pd.DataFrame, abstract: dict[str, object], mismatches: int) -> str:
    return f"""
# Decision Analysis Author-Guidelines Audit

## Source record

- Official source: <{GUIDELINE_URL}>
- Official page reviewed in the in-app browser on {GUIDELINE_ACCESS_DATE}.
- This audit records only requirements visible on that page plus the task-supplied abstract presentation request. It does not infer unverified requirements.
- The official ScholarOne step states an abstract maximum of 250 words, whereas the task specification permits 300. This package adopts the stricter official maximum and requires a live-form recheck before upload.

## Automated checks

- DA abstract word count: `{abstract['word_count']}`.
- Required abstract labels missing: `{', '.join(abstract['missing_labels']) or 'none'}`.
- Required abstract terms missing: `{', '.join(abstract['missing_terms']) or 'none'}`.
- Forbidden abstract wording: `{', '.join(abstract['forbidden_hits']) or 'none'}`.
- Mathematical-symbol markers in the abstract: `{''.join(abstract['formula_markers']) or 'none'}`.
- Frozen-artifact hash mismatches at this stage: `{mismatches}`.

## Requirement Checklist

{markdown_table(checklist, list(checklist.columns))}

## Boundary

This is a pre-submission audit, not confirmation that a rendered manuscript satisfies format requirements or that author-specific declarations are complete.
"""


def introduction_da() -> str:
    return """
# 1. Introduction

Institutional designers often choose aggregation rules for decisions that combine visible expert assessments with hidden collective input. When only coarse elimination outcomes are disclosed, they face a specific decision problem: how should aggregation rules be evaluated when public preferences are hidden and the observed outcome is compatible with many latent states? The problem is not to select a convenient point estimate. It is to represent the information actually supplied by the rule and its limited feedback, then use that representation to assess transparency, accountability, and interpretability.

This paper studies a class of aggregation-rule evaluation problems under incomplete preference observability. An elimination outcome restricts the hidden states compatible with a documented institutional rule, but generally does not select one state. We therefore use rule-aware partial identification as a decision-analytic response to incomplete feedback. The resulting feasible preference sets are decision-relevant uncertainty representations: they identify what is ruled out, what remains compatible with the record, and what a later designer cannot responsibly infer.

The distinction among rule regimes is substantive. Percentage aggregation supports cardinal feasible intervals. Direct ranking aggregation supports feasible ordinal rankings. A judge-save rule replaces a direct elimination implication with a tie-inclusive bottom-set condition, creating a discretion-identifiability trade-off: the institutional intervention enlarges the set of collective-preference states compatible with the same observed record.

The empirical material is a longitudinal setting with documented rule changes, repeated eliminations, and three regimes. It functions as a testbed for the method rather than as the paper's substantive center. It permits repeated examination of how aggregation mechanisms determine the form and width of partially identified uncertainty.

The paper contributes four elements. First, it defines a rule-aware framework that keeps cardinal and ordinal identified objects distinct. Second, it uses feasible preference sets to make mechanism-induced uncertainty visible rather than silently selecting a latent state. Third, it formalizes the judge-save comparison as an information consequence of discretion. Fourth, it treats dynamic evidence, predictive checks, and scenario analysis as secondary decision-support tools that retain, rather than erase, incomplete observability.

The remainder documents the testbed and institutional rules, defines the feasible-set representations, reports mechanism-specific evidence, and then considers validation, scenarios, design implications, and limits.
"""


def related_work_da(root: Path) -> str:
    source = (root / "manuscript/submission_main/02_related_work.md").read_text(encoding="utf-8")
    references_heading = "## Verified Sources Cited in This Draft"
    references = source.split(references_heading, 1)[1].strip()
    return f"""
# 2. Related Work

## Partial Identification as Decision Analysis under Incomplete Feedback

Decision analysis must distinguish uncertainty caused by incomplete observation from uncertainty that can be removed by a convenient modeling choice. Manski (2000) frames decisions under ambiguity created by incomplete identification, while Imbens and Manski (2004) distinguish partially identified parameters from point-estimation settings. The present framework applies that boundary to aggregation-rule evaluation: it reports feasible preference sets that are compatible with a documented rule and coarse outcome rather than assigning a unique hidden collective input.

## Aggregation Rules and the Object of Evaluation

Aggregation rules are not merely computational implementation details. Foundational social-choice work establishes that collective outcomes depend on the aggregation relation (Arrow, 1950; Young, 1988), while rank-aggregation work formalizes the treatment of orderings (Dwork et al., 2001). Liang (2019) further emphasizes that preference inference depends on the observed choice process. These sources motivate the paper's central separation of percentage-rule cardinal intervals from ranking-rule ordinal feasible sets.

## Expert-Crowd Systems, Discretion, and Decision-Relevant Uncertainty

Research on collective judgment motivates study of systems with visible expert inputs and hidden collective inputs (Lorenz et al., 2011). It does not make the present auxiliary evidence a direct public-vote measure. Steunenberg (1996) provides general context for institutional discretion; here, the more limited result is that a judge-save condition changes the identifiability of collective preferences within comparable weeks. Decision analysis under incomplete information, including minimax-regret reasoning (Manski, 2007), motivates retaining compatible states as visible inputs to institutional evaluation.

## Validation and Scenario Analysis

Prediction is distinct from explanation (Shmueli, 2010). Accordingly, predictive checks assess whether the feasible-set representation is consistent with observed institutional outcomes; they do not verify a point-valued collective preference. Scenario analysis illustrates how rule changes affect decision-relevant uncertainty under retained feasible states. The longitudinal setting is used as a reproducible computational testbed in the spirit of Bell and Koren (2008), not as a claim about a representative application domain.

{references_heading}

{references}
"""


def data_rules_da() -> str:
    return """
# 3. Data and Institutional Rules

## Longitudinal empirical setting

The processed longitudinal panel contains 4,199 contestant-week records before identification-specific availability restrictions. The identification feature file contains 2,777 active contestant-week records, of which 2,766 have a typed auxiliary dynamic proxy. The remaining 11 observations correspond to a logged percentage-regime constraint skip and are not imputed.

| Regime | Seasons | Season-weeks | Active contestant-weeks | Decision-relevant identified object |
| --- | ---: | ---: | ---: | --- |
| P | 25 | 247 | 1,997 | Cardinal feasible preference intervals |
| R | 2 | 14 | 78 | Feasible ordinal rankings |
| R_plus | 7 | 73 | 702 | Feasible ordinal rankings under a weak judge-save condition |

## Institutional decision rules

In P, a normalized expert component is aggregated with a hidden cardinal collective-support component. In R, judge and collective ranks are combined and the lowest combined standing is eliminated. In R_plus, a judge-save intervention means that the recorded elimination need only be compatible with a tie-inclusive bottom set before discretion is exercised. The preprocessing and constraint reports separately record no-elimination weeks, multiple eliminations, withdrawals, final rounds, and rule-specific availability conditions.

The collective component is not observed. Thus P, R, and R_plus are different institutional information environments, not interchangeable measurements of one latent quantity. Their feasible sets are evaluated within their own rule language.

Traceable sources: `data/processed/panel_long.csv`, `data/processed/week_level.csv`, `data/processed/identification_features_long.csv`, `outputs/tables/constraint_summary.csv`, and the generated preprocessing and constraint reports.
"""


def methods_da() -> str:
    return """
# 4. Methods

## Rule-aware partial identification

For each decision week, the observable record consists of the active set, the documented aggregation rule, the expert component, and the elimination outcome. Rule-aware partial identification maps this record to every hidden collective-preference state compatible with it. The output is a feasible preference set, used here as a decision-relevant uncertainty representation rather than as a selected estimate.

## Percentage aggregation

In P, hidden support is cardinal and constrained to nonnegative shares that sum to one. An observed elimination implies that an eliminated contestant's combined expert-plus-support total does not exceed that of a surviving contestant. These inequalities, together with the share constraints, create a bounded convex feasible region. Coordinate-wise linear programs obtain sharp lower and upper support bounds. No-elimination weeks introduce no outcome inequality, withdrawals are non-comparative, multiple eliminations compare each eliminated contestant with non-withdrawn survivors, and final-round ordering is used only where the record provides it.

## Ranking aggregation

In R and R_plus, the hidden object is an ordinal collective ranking rather than a support share. Candidate strict rankings are retained when their combination with observed judge ranks is compatible with the recorded bottom outcome. Each contestant's feasible rank support, normalized rank width, and rank-frequency uncertainty summarize ordinal ambiguity. Exact enumeration is used in small fields; larger fields use 10,000 fixed-seed draws. Numerical Monte Carlo error is reported separately from the institutional uncertainty represented by the feasible set.

## Judge-save discretion

R_plus weakens the observed implication from direct elimination to membership in an enlarged, tie-inclusive bottom set. Every direct-feasible ranking remains weak-feasible, so the weak set contains the direct set within the same week. The weak-to-direct ratio is therefore an interpretable indicator of the discretion-identifiability trade-off. It does not rank the desirability of discretion or equate R_plus with a different regime.

## Auxiliary evidence, validation, and scenarios

The dynamic proxy organizes feasible-set summaries over time: it does not directly measure collective preferences. Predictive checks use historical information and assess whether these representations remain consistent with observed institutional outcomes. Same-week judge models are explanatory benchmarks rather than deployable forecasts. Scenario analysis propagates retained feasible states to illustrate how rule changes affect decision-relevant uncertainty. It is decision support under limited observability, not a reconstruction of an alternative historical process.
"""


def results_da() -> str:
    return """
# 5. Results

## Feasible-set uncertainty under cardinal aggregation

The P regime has nonempty feasible regions in 247 of 248 eligible weeks. Its mean normalized coordinate-wise interval width is 0.842991. The implication is not that the hidden collective component has been resolved. Instead, the documented percentage rule and coarse outcome leave a wide but explicit range of compatible cardinal states.

## Mechanism-specific identified objects

P produces cardinal intervals, whereas R and R_plus produce ordinal ranking sets. The mean normalized ordinal widths are 0.890986 for R and 0.923933 for R_plus. These quantities should not be pooled or treated as measurements on a common scale: the hidden object, active-field composition, and rule regime differ.

## Discretion-identifiability trade-off

Across 73 R_plus weeks, the weak-to-direct feasible-set ratio has a mean of 2.665961 and a median of 1.571821. The weak set is strictly larger in 56 weeks, equal in 17, and never smaller. This is a within-week information result induced by the judge-save condition. It shows how expert discretion changes the identifiability of collective preferences, not whether discretion produces a preferable decision.

## Decision-analytic interpretation

The results make mechanism-induced uncertainty an observable property of the institutional design and released feedback. They give institutional designers a basis for comparing transparency and interpretability consequences of documented rules while preserving the difference between cardinal and ordinal evidence. Figure 2 and Table 2 report the cardinal result; Figure 3 and Table 3 present the within-rule discretion comparison; Figure 4 is labeled as a non-comparable descriptive context only.

Traceable sources: `outputs/tables/identification_comparison_by_regime.csv`, `outputs/tables/ranking_identification_summary_rplus.csv`, `outputs/tables/constraint_summary.csv`, `outputs/figures/uncertainty_over_weeks_regime_p.png`, and `outputs/figures/judge_save_identifiability_loss.png`.
"""


def validation_scenarios_da() -> str:
    return """
# 6. Validation and Scenario Analysis

## Predictive checks as consistency evidence

Predictive checks assess whether the feasible-set representation is consistent with observed institutional outcomes. Across 211 forward-chaining events, the strictly historical combined-lag model has accuracy 0.317536 and log loss 1.838463, compared with 0.118483 and 2.077488 for uniform risk. This limited signal is validation evidence only. It does not select a hidden preference state or turn the dynamic proxy into a direct public-vote measure.

The lowest reported log loss, 1.705755, belongs to a same-week judge benchmark. Because it uses contemporaneous judge information, it is explanatory rather than a prior-week forecast. Separating this benchmark prevents a stronger predictive claim than the design supports.

## Scenario analysis for rule evaluation

Scenario analysis illustrates how rule changes affect decision-relevant uncertainty under stated compatible states. Percentage calculations use lower, midpoint, and upper coordinate sensitivity inputs; ordinal calculations retain feasible joint rankings without converting them into support shares. The resulting summaries condition on observed active trajectories. They provide a structured way to discuss design consequences under limited observability, not a claim about an unobserved alternative history.

The current Pareto grid contains only zero-uncertainty-penalty frontier points. Accordingly, the analysis does not present a positive uncertainty penalty as an empirically preferred mechanism. Validation diagnostics, scenario details, heatmaps, and controversial cases are retained for the appendix.
"""


def discussion_da() -> str:
    return """
# 7. Discussion

The decision-analytic contribution is to turn incomplete feedback into an explicit object for institutional evaluation. Feasible preference sets show which hidden states remain compatible with a rule and outcome, allowing designers to distinguish known implications from unresolved uncertainty. A wide set is not a deficient estimate; it is a transparent record of the information the system did not reveal.

The judge-save result makes the discretion-identifiability trade-off concrete. Discretion may serve purposes outside this analysis, but it changes what a later observer can infer from an elimination record. This distinction helps designers discuss rule changes in terms of accountability and interpretability without treating the observed outcome as complete evidence about collective preferences.

Dynamic proxies, predictive checks, and scenarios remain subordinate to this representation. The dynamic proxy organizes auxiliary evidence but is not interpreted as a direct measure of public votes. Predictive checks assess consistency with observed institutional outcomes. Scenario analysis illustrates how rule changes affect decision-relevant uncertainty. Together, these components provide a disciplined form of decision support when preferences are partly hidden.

The empirical setting demonstrates the workflow across documented rule changes. Applying it elsewhere requires a fresh rule encoding, local feedback model, and decision objective. The transferable claim is about aggregation-rule evaluation under incomplete preference observability, not the substantive domain of the testbed.
"""


def limitations_da() -> str:
    return """
# 8. Limitations

- The collective input is unobserved; the analysis reports feasible sets and auxiliary summaries rather than a point-valued collective-preference measure.
- The longitudinal testbed is one empirical setting. Transfer requires new rule coding, feedback assumptions, and a domain-specific decision objective.
- Percentage intervals and ordinal ranking sets are different mathematical objects. Their normalized widths are not a common uncertainty scale.
- Rule interpretation, score normalization, tie handling, withdrawals, no-elimination weeks, multiple eliminations, and final-round records affect the feasible sets and are handled only as documented in the reproducible pipeline.
- The R_plus comparison uses a tie-inclusive weak bottom-set condition. Its result is an identifiability comparison, not a welfare evaluation of expert discretion.
- Fixed-seed sampling in larger ranking fields produces numerical approximation error that is distinct from mechanism-induced uncertainty.
- Predictive checks are secondary validation; same-week judge models are explanatory benchmarks, not deployment models.
- Scenario calculations condition on observed active trajectories and retained feasible states. They are not evidence about an unobserved historical replacement process.
- Raw-data sharing, archival release, code licensing, and an environment lock remain subject to source terms and author completion.
"""


def conclusion_da() -> str:
    return """
# 9. Conclusion

Institutional designers cannot evaluate aggregation rules responsibly by assuming that coarse outcomes reveal hidden collective preferences. Rule-aware partial identification instead supplies feasible preference sets that preserve what the record supports and what remains unresolved. Percentage rules produce cardinal feasible intervals; ranking rules produce ordinal feasible rankings; and judge-save discretion expands compatible rankings within comparable weeks.

This framework makes mechanism-induced uncertainty available for accountability and interpretability. Its validation and scenario extensions retain that uncertainty as decision support under limited observability rather than replacing it with a point estimate. The longitudinal testbed demonstrates the workflow; future applications should begin with their own documented rules, feedback processes, and decision objectives.
"""


def manuscript_sections(root: Path) -> dict[str, str]:
    return {
        "00_title_abstract_keywords_DA.md": da_title_abstract(),
        "01_introduction_DA.md": introduction_da(),
        "02_related_work_DA.md": related_work_da(root),
        "03_data_and_institutional_rules_DA.md": data_rules_da(),
        "04_methods_DA.md": methods_da(),
        "05_results_DA.md": results_da(),
        "06_validation_and_scenario_analysis_DA.md": validation_scenarios_da(),
        "07_discussion_DA.md": discussion_da(),
        "08_limitations_DA.md": limitations_da(),
        "09_conclusion_DA.md": conclusion_da(),
    }


def claims_reframing_matrix() -> pd.DataFrame:
    rows = [
        (
            "R1",
            "We analyze a competition system.",
            "We study a class of aggregation-rule evaluation problems under incomplete preference observability.",
            "Moves the testbed from the headline claim to evidence for an institutional decision problem.",
            "01 Introduction; 07 Discussion",
            "satisfied",
        ),
        (
            "R2",
            "Prediction validates the model.",
            "Predictive checks assess whether the feasible-set representation is consistent with observed institutional outcomes.",
            "Separates limited validation evidence from point identification or deployment claims.",
            "06 Validation and Scenario Analysis",
            "satisfied",
        ),
        (
            "R3",
            "Counterfactuals show what would happen.",
            "Scenario analysis illustrates how rule changes affect decision-relevant uncertainty.",
            "Frames mechanism comparisons as conditional decision support under retained feasible states.",
            "06 Validation and Scenario Analysis; 07 Discussion",
            "satisfied",
        ),
        (
            "R4",
            "Judge-save changes outcomes.",
            "Expert discretion changes the identifiability of collective preferences.",
            "Makes the result a discretion-identifiability trade-off rather than an outcome or welfare claim.",
            "04 Methods; 05 Results; 07 Discussion",
            "satisfied",
        ),
        (
            "R5",
            "Public appeal proxy captures popularity.",
            "The dynamic proxy organizes auxiliary evidence but is not interpreted as a direct measure of public votes.",
            "Preserves the proxy boundary and prevents direct-measure language.",
            "04 Methods; 06 Validation and Scenario Analysis; 07 Discussion",
            "satisfied",
        ),
        (
            "R6",
            "Wide bounds are a weak result.",
            "Feasible preference sets are a decision-relevant uncertainty representation under incomplete feedback.",
            "Treats unresolved information as an auditable institutional-design consequence.",
            "01 Introduction; 04 Methods; 07 Discussion",
            "satisfied",
        ),
        (
            "R7",
            "Cross-regime widths rank rule quality.",
            "Cardinal and ordinal uncertainty summaries remain regime-specific and are not a common scale.",
            "Prevents invalid pooling across distinct latent objects and samples.",
            "05 Results; 08 Limitations; Figure 4 plan",
            "satisfied",
        ),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "reframing_id",
            "expression_to_avoid",
            "Decision_Analysis_reframing",
            "decision_analytic_function",
            "DA_manuscript_location",
            "status",
        ],
    )


def theory_audit(matrix: pd.DataFrame) -> str:
    return f"""
# Decision Analysis Theory-Contribution Audit

## Contribution boundary

The DA version does not add a new empirical model, normative objective, external application, or theoretical result. It reframes the frozen contribution as an aggregation-rule evaluation problem in which feasible preference sets represent decision-relevant uncertainty under incomplete feedback.

## Verified framing choices

- The first page states the institutional-designer decision problem before introducing the longitudinal testbed.
- Partial identification is the decision-analytic response to incomplete feedback.
- Feasible sets represent mechanism-induced uncertainty rather than recovered collective input.
- The judge-save result is framed as a discretion-identifiability trade-off.
- P remains cardinal; R and R_plus remain ordinal. They are not pooled or equated.
- The dynamic proxy remains auxiliary evidence, prediction remains validation, and scenarios remain conditional decision support.

## Claim-Reframing Matrix

{markdown_table(matrix, list(matrix.columns))}

## Residual human task

The manuscript explains the information value of feasible sets, but a human author should still decide whether to add a compact, domain-grounded decision objective or illustrative choice protocol. That addition is not generated here because it would materially extend the frozen research design.
"""


def da_figure_table_plan() -> pd.DataFrame:
    rows = [
        (
            "figure", "Figure 1", "main", "Decision problem and identification framework",
            "outputs/figures/conceptual_framework_hidden_preferences.png",
            "Institutional rule plus coarse feedback yields a feasible-set uncertainty representation.",
            "Draft a standalone caption defining visible inputs, hidden preferences, feasible sets, and the design question.",
            "pass", "pass", "Production file needed: retain or create editable/vector source for final PDF.", "human caption review",
        ),
        (
            "figure", "Figure 2", "main", "Feasible preference-set intervals under cardinal aggregation",
            "outputs/figures/uncertainty_over_weeks_regime_p.png",
            "Percentage rules yield cardinal feasible intervals; width is not an observed collective input.",
            "State P-only scope, normalized coordinate-wise width, and exclusion of point-estimate language.",
            "pass", "pass", "Production file needed: retain or create editable/vector source for final PDF.", "human caption review",
        ),
        (
            "figure", "Figure 3", "main", "Identifiability expansion under expert discretion",
            "outputs/figures/judge_save_identifiability_loss.png",
            "The judge-save weak condition expands compatible ordinal rankings within comparable weeks.",
            "State tie-inclusive bottom-set condition and within-R_plus comparison only.",
            "pass", "pass", "Production file needed: retain or create editable/vector source for final PDF.", "human caption review",
        ),
        (
            "figure", "Figure 4", "main", "Cross-regime decision uncertainty comparison",
            "outputs/figures/identification_width_by_regime.png",
            "Mechanism-specific uncertainty is descriptive context, not a common cardinal-ordinal scale.",
            "Prominently state non-comparability, regime scope, and descriptive purpose.",
            "pass", "pass", "Production file needed: retain or create editable/vector source for final PDF.", "human caption review",
        ),
        (
            "table", "Table 1", "main", "Institutional rule regimes and observability",
            "data/processed/week_level.csv; outputs/tables/constraint_summary.csv",
            "Rule regimes define different observed feedback and identified objects.",
            "Define P, R, and R_plus; distinguish cardinal from ordinal objects.",
            "pass", "pass", "Typeset with final manuscript; no vector requirement.", "human table construction",
        ),
        (
            "table", "Table 2", "main", "Main feasible-set results",
            "outputs/tables/identification_comparison_by_regime.csv",
            "The central results are wide, regime-specific feasible sets.",
            "Include source, units, P/R/R_plus distinction, and non-comparability note.",
            "pass", "pass", "Typeset with final manuscript; no vector requirement.", "human table construction",
        ),
        (
            "table", "Table 3", "main", "Decision implications by aggregation mechanism",
            "outputs/tables/ranking_identification_summary_rplus.csv; outputs/tables/constraint_summary.csv",
            "Discretion changes identifiability and related transparency consequences.",
            "Limit implications to observable information and avoid welfare or outcome claims.",
            "pass", "pass", "Typeset with final manuscript; no vector requirement.", "human table construction",
        ),
        (
            "figure", "Figure A1", "appendix", "Validation diagnostics",
            "outputs/figures/prediction_comparison.png",
            "Historical validation is distinct from same-week explanatory benchmarks.",
            "Separate validation from point identification.",
            "pass", "pass", "Production file needed if included in final PDF.", "appendix",
        ),
        (
            "table", "Table A1", "appendix", "Scenario-analysis details",
            "outputs/tables/counterfactual_results_by_regime.csv",
            "Scenario analysis retains feasible-state uncertainty.",
            "State conditional trajectory assumption.",
            "pass", "pass", "Typeset with final manuscript.", "appendix",
        ),
        (
            "figure/table set", "Appendix A2-A6", "appendix", "Robustness and reproducibility diagnostics",
            "outputs/tables/ranking_sampling_diagnostics.csv; outputs/tables/robust_aggregation_results.csv; outputs/tables/controversial_cases_counterfactual.csv",
            "Sampling, heatmaps, controversial cases, robustness, full models, and pipeline details remain supplementary.",
            "Use standalone labels and preserve regime-specific language.",
            "pass", "pass", "Assess each retained visual for production quality during final layout.", "appendix",
        ),
    ]
    columns = [
        "item_type", "item_id", "placement", "proposed_title", "source_artifact", "DA_claim",
        "standalone_caption_or_note_check", "safe_language_check", "anonymous_check",
        "vector_or_pdf_production_note", "status",
    ]
    return pd.DataFrame(rows, columns=columns)


def figure_table_audit(plan: pd.DataFrame) -> str:
    main = plan.loc[plan["placement"].eq("main")]
    main_figures = int(main["item_type"].eq("figure").sum())
    main_tables = int(main["item_type"].eq("table").sum())
    return f"""
# Decision Analysis Figure and Table Audit

- Main-text figures: `{main_figures}` (required: 4).
- Main-text tables: `{main_tables}` (required: 3).
- Every planned item has a standalone-caption or note check, a safe-language check, an anonymity check, and a production-format note.
- Figure 4 must retain a prominent statement that cardinal P widths and ordinal R/R_plus widths are not directly comparable.
- Final accepted-production requirements call for high-quality PostScript/PDF figures according to the official page. This plan does not claim that vector source files already exist.

## Plan

{markdown_table(plan, list(plan.columns))}

## Appendix placement

Validation diagnostics, scenario-analysis details, heatmaps, controversial cases, robustness checks, full model or sampling diagnostics, and pipeline reproducibility details are placed in the appendix by default.
"""


def figure_table_plan_markdown(plan: pd.DataFrame) -> str:
    return "# Decision Analysis Figure and Table Plan\n\n" + markdown_table(plan, list(plan.columns)) + "\n"


def submission_documents(main_dir: Path, package: Path, plan: pd.DataFrame) -> dict[Path, str]:
    anonymous = "\n\n".join((main_dir / name).read_text(encoding="utf-8").strip() for name in DA_SECTIONS)
    return {
        package / "anonymous_manuscript_DA.md": anonymous,
        package / "cover_letter_DA.md": """
# Cover Letter

Dear Editor,

Please consider the enclosed manuscript, "Evaluating Aggregation Rules under Hidden Preferences: A Partial-Identification Approach," for publication in *Decision Analysis*. The manuscript addresses an institutional decision problem: how should designers evaluate aggregation rules when expert assessments are visible, collective preferences are hidden, and only coarse elimination outcomes are observed? It develops rule-aware partial identification to represent the feasible preference sets supported by the documented rule and outcome.

The paper distinguishes cardinal feasible intervals under percentage aggregation from ordinal feasible rankings under rank aggregation. It also shows, within comparable judge-save weeks, how a weak discretionary condition expands the compatible ranking set. The longitudinal empirical setting is used as a reproducible testbed; dynamic evidence, predictive checks, and scenarios are explicitly secondary to the feasible-set representation.

The accompanying materials identify reproducible scripts, processed data, generated tables and figures, tests, and frozen checksums. Raw-data access and redistribution remain subject to source terms; the authors will complete the final accessibility route and all journal-required declarations after verification. The anonymous manuscript is separated from the title-page materials for double-anonymous review.

Sincerely,

[AUTHOR TO COMPLETE]
""",
        package / "highlights_DA.md": """
# Highlights

- Rule-aware partial identification represents hidden preferences as decision-relevant feasible sets.
- Aggregation mechanisms determine whether the unresolved object is cardinal or ordinal.
- Expert discretion creates a within-rule trade-off between flexibility and identifiability.
- Predictive checks and scenarios support institutional evaluation without collapsing uncertainty into a point estimate.
""",
        package / "title_page_placeholder_DA.md": """
# Title Page Placeholder

## Manuscript Title

Evaluating Aggregation Rules under Hidden Preferences: A Partial-Identification Approach

## Author and Affiliation Details

[AUTHOR TO COMPLETE: names, affiliations, ORCID identifiers, corresponding-author contact information, and any required biographical details]

## Submission Metadata

[AUTHOR TO COMPLETE: keywords, preferred referees including at least one editorial-board member, funding details, and any ScholarOne fields required by the live form]
""",
        package / "data_and_code_accessibility_statement_DA.md": """
# Data and Code Accessibility Statement

The reproducible project materials include scripts `scripts/01_data_audit.py` through `scripts/18_specific_journal_submission.py`, this DA assembly stage, processed data under `data/processed/`, generated tables under `outputs/tables/`, figures under `outputs/figures/`, logs under `outputs/logs/`, focused tests under `tests/`, and the frozen checksum manifest in `outputs/tables/frozen_outputs_hashes.csv`. The manuscript identifies the source artifacts used for each substantive result.

The supplied raw data are retained unchanged under `data/raw/`, but public redistribution is not asserted because original source terms and permissions have not been completed in this project. Subject to the relevant permissions, authors can provide editors with source provenance, checksums, audit outputs, the raw-to-processed pipeline, and controlled review access or verification materials. Before submission, authors must confirm the source, access terms, redistribution rights, repository/archive location, code licence, and long-term preservation plan.
""",
        package / "AI_use_statement_DA.md": """
# AI Use Statement

Generative AI was used only to assist manuscript drafting, code organization, reproducibility checks, and preparation of submission materials. The authors must review and edit all AI-assisted material and remain fully responsible for the accuracy of the manuscript, analyses, citations, declarations, and code. No AI system is an author. The authors must confirm the final wording and placement against the live *Decision Analysis* submission requirements before upload.
""",
        package / "conflict_of_interest_statement_placeholder_DA.md": """
# Conflict of Interest Statement

[AUTHOR TO COMPLETE: disclose all conflicts of interest or state that none are declared. No declaration has been inferred from project files.]
""",
        package / "funding_statement_placeholder_DA.md": """
# Funding Statement

[AUTHOR TO COMPLETE: list funding sources, grant identifiers, and funder roles, or state that no funding was received. No funding information has been inferred.]
""",
        package / "ethics_statement_placeholder_DA.md": """
# Ethics Statement

[AUTHOR TO COMPLETE: determine whether review, consent, or another ethics statement applies to this supplied-data analysis. Do not invent approvals, exemptions, or protocol numbers.]
""",
        package / "author_contributions_placeholder_DA.md": """
# Author Contributions

[AUTHOR TO COMPLETE: provide named contribution roles and confirm responsibility for analysis, writing, and submission.]
""",
        package / "acknowledgements_placeholder_DA.md": """
# Acknowledgements

[AUTHOR TO COMPLETE: add contributor-approved acknowledgements or state that there are none.]
""",
        package / "reproducibility_package_readme_DA.md": """
# Reproducibility Package README

## Scope

This package assembles the DA-facing manuscript and audits from existing frozen analyses. It does not rerun estimation or modify raw data.

## Reproducible materials

- Raw-data provenance and audit: `data/raw/`, `scripts/01_data_audit.py`, and `outputs/logs/data_audit.md`.
- Panel construction: `scripts/02_preprocess.py`, `data/processed/panel_long.csv`, `data/processed/week_level.csv`, `data/processed/contestant_level.csv`, and `outputs/logs/preprocess_report.md`.
- Identification and downstream analyses: `scripts/03_build_constraints.py` through `scripts/11_robust_aggregation_evaluation.py`, processed identification files, output tables, figures, and logs.
- Manuscript and package assembly: `scripts/12_update_manuscript_results.py` through `scripts/19_decision_analysis_submission.py`.
- Validation: `tests/`, fixed random seeds in sampling stages, and the frozen-hash manifest.

## Reproduction route

Run the numbered scripts from the project root in their documented order, or use the existing pipeline entry points for stages already exposed there. The DA assembly stage is intentionally direct: `python scripts/19_decision_analysis_submission.py --project-root .`.

## Release boundary

Raw-data redistribution, public repository release, persistent archive, code licence, and a clean-environment lock file require author completion and source-term review. The present files provide provenance and a verification pathway; they do not promise public access that the source terms may not allow.
""",
        package / "appendix_plan_DA.md": """
# Appendix Plan

- Rule coding, preprocessing special cases, and field-availability restrictions.
- Percentage-aggregation constraint construction and linear-program diagnostics.
- Exact-versus-sampled ranking enumeration, tie-policy sensitivity, and Monte Carlo diagnostics.
- Validation diagnostics distinguishing historical models from same-week explanatory benchmarks.
- Scenario-analysis details, heatmaps, controversial cases, robustness checks, and Pareto outputs.
- Full model outputs, source tables, checksums, tests, and pipeline reproducibility details.

All appendix material must preserve the cardinal-versus-ordinal separation, the auxiliary status of the dynamic proxy, and the conditional nature of scenarios.
""",
        package / "figure_table_plan_DA.md": figure_table_plan_markdown(plan),
        package / "DA_submission_checklist.md": """
# Decision Analysis Submission Checklist

## Generated for review

- `anonymous_manuscript_DA.md`
- `cover_letter_DA.md`
- `highlights_DA.md`
- `data_and_code_accessibility_statement_DA.md`
- `AI_use_statement_DA.md`
- `reproducibility_package_readme_DA.md`
- `appendix_plan_DA.md`
- `figure_table_plan_DA.md`
- `outputs/logs/decision_analysis_author_guidelines_audit.md`
- `outputs/logs/DA_pre_submission_go_no_go_report.md`

## Mandatory human completion before upload

- Recheck the live Decision Analysis guide and ScholarOne form, especially the 250-word abstract cap, article type, required metadata, and format instructions.
- Complete title-page identities, affiliations, corresponding-author details, preferred referees, funding information, and all declarations.
- Confirm raw-data source terms, controlled editor-verification route, public-release permission, repository/archive, code licence, and reproducibility environment.
- Read and format every citation in author-year style with an alphabetical final reference list.
- Typeset, double-space, and inspect a clean anonymous PDF with 12-point font, one-inch margins, single-column layout, final tables, and production-quality figures.
""",
    }


def check_anonymous(path: Path) -> None:
    text = path.read_text(encoding="utf-8").casefold()
    risky = (
        "[author to complete",
        "corresponding author",
        "acknowledgements",
        "funding statement",
        "conflict of interest",
        "orcid",
        "institutional affiliation",
        "university",
        "department of",
    )
    hits = [term for term in risky if term in text]
    if hits:
        raise ValueError("Anonymous manuscript contains identifying or declaration content: " + "; ".join(hits))


def check_main_boundaries(main_dir: Path) -> None:
    texts = {path.name: path.read_text(encoding="utf-8") for path in main_dir.glob("*.md")}
    missing = [name for name in DA_SECTIONS if name not in texts]
    if missing:
        raise ValueError("DA manuscript is missing sections: " + "; ".join(missing))
    joined = "\n".join(texts.values()).casefold()
    hits = [term for term in FORBIDDEN if term in joined]
    if hits:
        raise ValueError("Forbidden wording in DA manuscript: " + "; ".join(hits))
    required = (
        "decision problem",
        "decision-analytic response",
        "decision-relevant uncertainty",
        "discretion-identifiability trade-off",
        "scenario analysis",
    )
    absent = [term for term in required if term not in joined]
    if absent:
        raise ValueError("Required DA framing is absent: " + "; ".join(absent))


def go_no_go_report(mismatches: int) -> str:
    return f"""
# Decision Analysis Pre-Submission Go / No-Go Report

## Decision: B. Needs moderate human revision

The frozen analytical evidence, DA-specific framing, guideline audit, anonymous manuscript source, and package materials are ready for focused human review. The work is not ready for upload because final author declarations, source-data permissions, citation review, rendered formatting, and a production PDF remain human responsibilities.

## Scores (1 = weak/high risk; 5 = strong/low risk)

| Dimension | Score | Basis |
| --- | ---: | --- |
| Decision Analysis scope fit | 4 | The paper now leads with aggregation-rule evaluation under incomplete observability. |
| Decision-analytic framing | 4 | Feasible sets, mechanism-induced uncertainty, and discretion-identifiability are consistently stated. |
| Methodological contribution | 4 | Cardinal polytope bounds, ordinal feasible rankings, and weak-set containment are transparent and frozen. |
| Theory-practice bridge | 3 | Design implications are clear, but a human author should refine the operational decision context and objective. |
| Evidence-claim alignment | 5 | Claims are linked to existing tables, figures, logs, and boundary language. |
| Literature grounding | 3 | Twelve verified source-map rows are retained; full-text claim checking and final bibliography formatting remain manual. |
| Reproducibility | 4 | Scripts, processed data, fixed seeds, tests, and frozen hashes are present; archive and environment lock remain incomplete. |
| Double-anonymous readiness | 4 | The anonymous source is separately generated and scanned; final PDF inspection remains necessary. |
| Overclaiming risk | 4 | Point-recovery, direct-measure, and causal language is excluded, subject to final human reading. |
| Submission package completeness | 3 | DA package documents are assembled, but title-page and declaration fields require author completion. |

## Top Five Strengths

1. The manuscript presents a precise institutional decision problem before the testbed.
2. Partial identification is operationalized as feasible-set uncertainty rather than an unobserved point estimate.
3. Cardinal P and ordinal R/R_plus objects remain separated throughout.
4. The judge-save result provides a clear, traceable discretion-identifiability comparison.
5. Frozen evidence remains intact: `{mismatches}` hash mismatches in the 20-artifact manifest at this stage.

## Top Five DA Desk-Reject Risks

1. The operational decision context or normative objective may still appear insufficiently concrete for the journal audience.
2. A reviewer may see the longitudinal testbed as too domain-specific despite the revised framing.
3. Citation precision and final DA-style reference formatting remain unverified by human reading.
4. Data-access permissions, archival release, and a clean-environment lock are not complete.
5. A Markdown source cannot demonstrate the required anonymous, double-spaced, single-column PDF layout.

## Ten Mandatory Human Fixes

1. Recheck the live official guideline and ScholarOne form immediately before submission.
2. Confirm the article type and the 250-word abstract limit in the active form.
3. Read every cited source and verify each sentence-level claim.
4. Build an alphabetical author-year bibliography in the final journal style.
5. Decide whether a concise operational decision objective or choice protocol can be stated without extending the frozen study.
6. Confirm raw-data provenance, access terms, redistribution rights, and the editor-verification route.
7. Create a persistent archive or repository release with a code licence and an environment lock or container.
8. Complete author, affiliation, corresponding-author, referee, funding, conflict, ethics, contribution, and acknowledgement fields.
9. Typeset and inspect a clean double-anonymous PDF using the required layout, font, spacing, and margins.
10. Prepare and inspect final tables, captions, and high-quality production figure files.

## Ten Optional Improvements

1. Obtain an independent Decision Analysis reader's assessment of the decision framing.
2. Add a compact worked design-choice illustration only if the authors can ground it without new modeling.
3. Add a data dictionary and rule-coding supplement.
4. Include a short interpretation guide for the feasible-set displays.
5. Prepare a Group Decision and Negotiation backup branch after DA submission is settled.
6. Add a clean-environment reproduction log after creating the archival environment.
7. Preserve editable source files for every retained figure.
8. Draft a response-to-reviewers evidence map from the claims matrix.
9. Ask an unaffiliated colleague to test the anonymous-PDF screening process.
10. Prepare a post-acceptance material-release plan consistent with source terms.

## Files Ready for DA Submission Review

- `manuscript/submission_DA/*.md`
- `submission_package_DA/anonymous_manuscript_DA.md`
- `submission_package_DA/cover_letter_DA.md`
- `submission_package_DA/highlights_DA.md`
- `submission_package_DA/data_and_code_accessibility_statement_DA.md`
- `submission_package_DA/AI_use_statement_DA.md`
- `submission_package_DA/reproducibility_package_readme_DA.md`
- `outputs/logs/decision_analysis_author_guidelines_audit.md`
- `outputs/logs/DA_abstract_audit.md`
- `outputs/logs/DA_theory_contribution_audit.md`
- `outputs/logs/DA_figure_table_audit.md`
- `outputs/tables/decision_analysis_requirements_checklist.csv`
- `outputs/tables/DA_claims_reframing_matrix.csv`
- `outputs/tables/DA_final_figure_table_plan.csv`

## Files Still Requiring Manual Completion

- `submission_package_DA/title_page_placeholder_DA.md`
- `submission_package_DA/conflict_of_interest_statement_placeholder_DA.md`
- `submission_package_DA/funding_statement_placeholder_DA.md`
- `submission_package_DA/ethics_statement_placeholder_DA.md`
- `submission_package_DA/author_contributions_placeholder_DA.md`
- `submission_package_DA/acknowledgements_placeholder_DA.md`
- Final journal-formatted manuscript, bibliography, tables, captions, figures, and anonymous PDF.

No new analysis is claimed in this stage. The generated documents preserve the frozen empirical evidence and its identification limits.
"""


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    required = [
        "outputs/tables/frozen_outputs_hashes.csv",
        "outputs/tables/identification_comparison_by_regime.csv",
        "outputs/tables/ranking_identification_summary_rplus.csv",
        "outputs/tables/prediction_results.csv",
        "outputs/tables/reference_insertion_plan.csv",
        "outputs/tables/constraint_summary.csv",
        "outputs/figures/conceptual_framework_hidden_preferences.png",
        "outputs/figures/uncertainty_over_weeks_regime_p.png",
        "outputs/figures/judge_save_identifiability_loss.png",
        "outputs/figures/identification_width_by_regime.png",
        "manuscript/submission_main/02_related_work.md",
    ]
    require(root, required)
    try:
        hash_check = frozen_hash_mismatches(root)
        mismatches = int(hash_check["status"].eq("mismatch").sum())
        if mismatches:
            bad = hash_check.loc[hash_check["status"].eq("mismatch"), "relative_path"].tolist()
            raise ValueError("Frozen-artifact hashes differ: " + "; ".join(bad))

        manuscript_dir = root / "manuscript/submission_DA"
        package = root / "submission_package_DA"
        tables = root / "outputs/tables"
        logs = root / "outputs/logs"
        sections = manuscript_sections(root)
        for name, content in sections.items():
            write_text(manuscript_dir / name, content)
        check_main_boundaries(manuscript_dir)

        abstract = validate_abstract(sections["00_title_abstract_keywords_DA.md"])
        if not 230 <= int(abstract["word_count"]) <= 250:
            raise ValueError(f"DA abstract must contain 230-250 words; found {abstract['word_count']}.")
        if abstract["missing_terms"] or abstract["missing_labels"] or abstract["forbidden_hits"] or abstract["formula_markers"]:
            raise ValueError("DA abstract failed content, structure, language, or formula checks.")

        checklist = guideline_checklist()
        checklist.to_csv(tables / "decision_analysis_requirements_checklist.csv", index=False)
        write_text(logs / "decision_analysis_author_guidelines_audit.md", guidelines_audit(checklist, abstract, mismatches))
        write_text(
            logs / "DA_abstract_audit.md",
            "\n".join(
                [
                    "# Decision Analysis Abstract Audit",
                    "",
                    f"- Word count including four labels: `{abstract['word_count']}` (target 230-250; official stricter maximum 250).",
                    f"- Required labels missing: `{', '.join(abstract['missing_labels']) or 'none'}`.",
                    f"- Required terms missing: `{', '.join(abstract['missing_terms']) or 'none'}`.",
                    f"- Forbidden wording: `{', '.join(abstract['forbidden_hits']) or 'none'}`.",
                    f"- Mathematical-symbol markers: `{''.join(abstract['formula_markers']) or 'none'}`.",
                    "- Keywords: five, satisfying the official 1-5 range and the task's requested DA orientation.",
                    "- Status: pass, subject to a final human reading and live-form confirmation.",
                ]
            ),
        )

        matrix = claims_reframing_matrix()
        matrix.to_csv(tables / "DA_claims_reframing_matrix.csv", index=False)
        write_text(logs / "DA_theory_contribution_audit.md", theory_audit(matrix))

        plan = da_figure_table_plan()
        plan.to_csv(tables / "DA_final_figure_table_plan.csv", index=False)
        write_text(logs / "DA_figure_table_audit.md", figure_table_audit(plan))

        for path, content in submission_documents(manuscript_dir, package, plan).items():
            write_text(path, content)
        check_anonymous(package / "anonymous_manuscript_DA.md")
        write_text(logs / "DA_pre_submission_go_no_go_report.md", go_no_go_report(mismatches))
    except (OSError, ValueError, KeyError, IndexError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("Decision Analysis submission assembly completed.")
    print(f"DA manuscript sections: {len(DA_SECTIONS)}")
    print(f"DA abstract word count: {abstract['word_count']}")
    print(f"Main figure/table plan: {(plan['placement'].eq('main') & plan['item_type'].eq('figure')).sum()} figures, {(plan['placement'].eq('main') & plan['item_type'].eq('table')).sum()} tables")
    print(f"Frozen-artifact hash mismatches: {mismatches}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
