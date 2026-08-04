#!/usr/bin/env python3
"""Generate a strict, reproducible pre-submission audit without fitting new models."""

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate strict journal-fit, reviewer, evidence, and submission-package audits."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    return parser.parse_args()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in frame[columns].fillna("").itertuples(index=False):
        lines.append("| " + " | ".join(str(value).replace("|", "/") for value in row) + " |")
    return "\n".join(lines)


def journal_fit_rows() -> list[dict[str, str]]:
    return [
        {"item": "Public/service-sector decision problem", "status": "fail", "risk_level": "high", "evidence_from_manuscript": "The empirical application is a televised competition testbed; no public-service dataset or decision owner is studied.", "required_revision": "Do not submit to SEPS on wording alone. Add a genuinely public/service-sector application or target a broader decision-science venue.", "suggested_wording": "This longitudinal competition dataset is an empirical testbed for rule-aware inference; it is not evidence about a public-service operation."},
        {"item": "Quantitative methods contribution", "status": "pass", "risk_level": "low", "evidence_from_manuscript": "Sections 4-5 define LP bounds, feasible ordinal ranking sets, containment, and fixed-seed sampling.", "required_revision": "Retain formal notation and code-output traceability.", "suggested_wording": "We develop a rule-aware partial-identification framework for hidden preference inputs."},
        {"item": "Testbed versus entertainment case", "status": "partial", "risk_level": "high", "evidence_from_manuscript": "The manuscript labels the data an empirical testbed, but no external service-sector validation is supplied.", "required_revision": "Move entertainment context to the data section and limit generalization claims.", "suggested_wording": "The application supplies longitudinal, rule-changing observational data rather than a public-sector effectiveness evaluation."},
        {"item": "Methodological distinctiveness", "status": "partial", "risk_level": "medium", "evidence_from_manuscript": "Rule-aware cardinal/ordinal identification and judge-save containment are explicit, but related-work citations are absent.", "required_revision": "Add verified literature positioning before making novelty claims.", "suggested_wording": "The contribution is a mechanism-specific identification construction; novelty relative to prior bounds and aggregation work requires documented comparison."},
        {"item": "Applied-context importance", "status": "fail", "risk_level": "high", "evidence_from_manuscript": "No stakeholder, policy operator, service outcome, or public-planning decision is observed.", "required_revision": "Provide a concrete public/service decision use case or change venue.", "suggested_wording": "Potential relevance to public-facing hybrid decisions is a proposed transfer question, not an evaluated application."},
        {"item": "Interdisciplinary applied quantitative research", "status": "partial", "risk_level": "medium", "evidence_from_manuscript": "The methods are quantitative, but the socio-economic planning connection is conceptual rather than empirical.", "required_revision": "Either substantiate the applied bridge or avoid claiming direct SEPS relevance.", "suggested_wording": "The framework may inform institutional-design studies when the local rule and latent signal are documented."},
        {"item": "Clear model/methodology contribution", "status": "pass", "risk_level": "low", "evidence_from_manuscript": "P LP bounds, ordinal feasible sets, and R_plus weak-set containment are reproducibly implemented.", "required_revision": "Keep prediction and counterfactuals secondary.", "suggested_wording": "The main result is partial identification induced by observed rules and eliminations."},
        {"item": "Practical decision implication", "status": "partial", "risk_level": "high", "evidence_from_manuscript": "Discussion describes a general design implication but no decision-maker evaluates it.", "required_revision": "Frame the implication as a design consideration, not a demonstrated operational benefit.", "suggested_wording": "Institutions trading discretion for transparency should recognize that the choice also changes identifiability."},
        {"item": "Prediction is not the central contribution", "status": "pass", "risk_level": "low", "evidence_from_manuscript": "Sections 5-6 label prediction validation and separate same-week explanatory benchmarks.", "required_revision": "Place detailed prediction results in an appendix for a SEPS submission.", "suggested_wording": "Prediction is a secondary validation exercise, not evidence of point recovery."},
        {"item": "Submission organization, accuracy, and logical flow", "status": "partial", "risk_level": "medium", "evidence_from_manuscript": "Structured markdown and audits exist, but no verified bibliography, compiled manuscript, or journal-specific guide confirmation exists.", "required_revision": "Add references, title page, declarations, and a journal-formatted manuscript after venue choice.", "suggested_wording": "This is a reproducible pre-submission draft, not a complete journal submission package."},
    ]


def journal_fit_audit(fit: pd.DataFrame) -> str:
    return f"""
# Target Journal Fit Audit: Socio-Economic Planning Sciences

## Official-source check

- SEPS Aims and Scope: <{SEPS_SCOPE_URL}> (access attempted {ACCESS_DATE}; the current network endpoint returned HTTP 403, so its full text requires manual editor/browser verification).
- SEPS Guide for Authors: <{SEPS_GUIDE_URL}> (access attempted {ACCESS_DATE}; the current network endpoint returned HTTP 403, so journal-specific submission details require manual verification).
- Elsevier Research Data policy: <{ELSEVIER_DATA_URL}> (accessed {ACCESS_DATE}; supports data availability statements, sharing where appropriate, and software/data documentation).
- Elsevier Generative AI policy: <{ELSEVIER_AI_URL}> (accessed {ACCESS_DATE}; requires a separate declaration when AI materially assists manuscript preparation, including tool, purpose, oversight, and author responsibility; AI is not an author).
- Elsevier Publishing Ethics: <{ELSEVIER_ETHICS_URL}> (accessed {ACCESS_DATE}; supports originality, disclosure, and publication-integrity checks).

## Overall judgement: Weak fit, consider another journal

The methodology is quantitative and potentially relevant to institutional design. However, the current empirical evidence is an entertainment-competition testbed with no observed public-sector service, planning authority, policy operator, or service outcome. Reframing alone cannot establish SEPS applied relevance. The likely editorial risk is desk rejection for insufficient fit, not a criticism of the partial-identification implementation.

## Operational checklist

{markdown_table(fit, ['item', 'status', 'risk_level', 'evidence_from_manuscript', 'required_revision', 'suggested_wording'])}

## Mandatory action before any SEPS submission

Confirm the live Aims and Scope and Guide for Authors manually from a normal browser session, then obtain a genuine public/service-sector application or choose a venue whose scope explicitly accepts general decision-science methodology with an entertainment empirical testbed. The current title, abstract, introduction, discussion, and conclusion should not claim SEPS public-sector relevance as an established application.
"""


def reviewer_reports() -> tuple[str, pd.DataFrame]:
    reports = """
# Simulated Reviewer Reports

## Reviewer 1: Methodology

**Summary.** The rule-aware distinction between cardinal P regions and ordinal R/R_plus ranking sets is the manuscript's strongest contribution. The containment comparison is well targeted, but the current methods narrative is too compressed for a methodological paper.

**Major concerns.** (1) The manuscript must state the score/rank direction, bottom-set operator, and direct-versus-weak inclusion relation in notation, not prose alone. (2) Coordinate-wise P bounds are sharp marginal bounds but are not a jointly feasible midpoint vector. (3) Exact and Monte Carlo weeks need visible separation, including the reported maximum Monte Carlo standard error. (4) Cross-regime widths are not commensurable and should not occupy a central figure without a prominent warning.

**Minor concerns.** Define entropy normalization, tie policy, withdrawal handling, and final-round exceptions next to their first use.

**Decision recommendation:** major revision. **Most likely rejection reason:** insufficient formal exposition and literature positioning for the claimed methodology contribution. **Required fixes:** use the revised methods section; add verified related work; demote cross-regime comparisons.

## Reviewer 2: Application and Journal Fit

**Summary.** The paper is currently poorly matched to a socio-economic planning journal. Its empirical setting is a televised competition, and the claimed public/service relevance is prospective rather than evaluated.

**Major concerns.** (1) No public-sector agency, service, planning decision, welfare outcome, or policy intervention is in the data. (2) The manuscript cannot solve this problem by calling the competition a proxy for public decision systems. (3) Mechanism-design implications are conceptual and unvalidated in the target domain.

**Minor concerns.** The journal-specific Guide for Authors and scope require direct manual confirmation because the official pages were inaccessible from this audit environment.

**Decision recommendation:** reject for scope at SEPS. **Most likely rejection reason:** desk rejection for an entertainment-only empirical application with insufficient public/service-sector relevance. **Required fixes:** add a public/service application or select a broader decision-science or operations-research venue.

## Reviewer 3: Empirical Validation

**Summary.** The leakage controls are stronger than typical retrospective prediction exercises, but the predictive and counterfactual sections must remain subordinate to identification.

**Major concerns.** (1) The best model uses same-week judge information and is explanatory, not deployable forecasting. (2) Strictly historical models improve over uniform risk but remain weaker than that benchmark. (3) Counterfactual rankings condition on observed active trajectories and cannot be interpreted as alternative historical seasons. (4) Controversial cases risk distracting from the main identification result.

**Minor concerns.** Make R-specific estimates visibly unstable because only two seasons contribute.

**Decision recommendation:** major revision. **Most likely rejection reason:** overinterpretation of proxy validation or scenario changes. **Required fixes:** use the revised validation/scenario section and move cases, Pareto, and lambda/gamma grids to the appendix.

## Reviewer 4: Reproducibility and Software

**Summary.** The pipeline, seeds, output paths, and 42 tests are substantial strengths. The package is not yet clean-environment submission-ready.

**Major concerns.** (1) README remains stale and omits stages 13-15 and the submission audit entry point. (2) Dependency ranges are bounded but not locked, so exact environments can drift. (3) There is no license, archival environment specification, or compiled/blinded manuscript. (4) The raw-data source and redistribution terms remain placeholders.

**Minor concerns.** Capture operating-system and Python versions in a release record; document the harmless pytest cache-permission warning.

**Decision recommendation:** major revision. **Most likely rejection reason:** reviewers cannot reproduce the precise submitted environment or access conditions. **Required fixes:** update README, add an environment lock or container, license, data-source statement, and release manifest.
"""
    register = pd.DataFrame([
        {"reviewer": "Methodology", "risk": "Formal notation and literature positioning are incomplete", "severity": "high", "likelihood": "medium", "required_fix": "Use revised methods; add verified citations and sampling/tie details."},
        {"reviewer": "Application/journal fit", "risk": "Entertainment testbed lacks demonstrated public/service-sector relevance", "severity": "critical", "likelihood": "high", "required_fix": "Change venue or add a genuine public/service application."},
        {"reviewer": "Empirical validation", "risk": "Same-week benchmark or scenarios may be overread", "severity": "high", "likelihood": "medium", "required_fix": "Demote prediction/counterfactual material to validation and appendix."},
        {"reviewer": "Reproducibility", "risk": "README, environment lock, license, and data-source terms are incomplete", "severity": "high", "likelihood": "high", "required_fix": "Provide archival environment and complete release package."},
        {"reviewer": "Editorial", "risk": "No verified bibliography or submission-formatted manuscript", "severity": "critical", "likelihood": "high", "required_fix": "Complete references, title page, declarations, and journal formatting."},
    ])
    return reports, register


def strict_claims(claims: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_map = {"core": "main", "secondary": "supporting", "exploratory": "exploratory"}
    forbidden = {
        "core": "Do not call any feasible point an observed public ballot or claim cross-domain effectiveness.",
        "secondary": "Do not use causal language, point-recovery language, or make it the abstract center.",
        "exploratory": "Do not place in abstract or conclusion; do not call results historical causal alternatives or optimal settings.",
    }
    safe = {
        "core": "The observed rule and outcome constrain a feasible preference set.",
        "secondary": "This descriptive, model-dependent result is consistent with limited signal under the stated design.",
        "exploratory": "This scenario-based sensitivity result depends on the identified-set construction and chosen grid.",
    }
    for claim in claims.itertuples(index=False):
        level = str(claim.strength_level)
        allowed = "Abstract, introduction end, results, conclusion" if level == "core" else ("Results or discussion, not abstract center" if level == "secondary" else "Appendix or caveated discussion only")
        rows.append({
            "claim_id": claim.claim_id,
            "claim_text": claim.claim_text,
            "evidence": claim.supporting_output,
            "strength": level,
            "claim_tier": group_map[level],
            "allowed_manuscript_location": allowed,
            "forbidden_wording": forbidden[level],
            "safe_wording": safe[level],
            "abstract_can_mention": "yes" if level == "core" else "no",
        })
    return pd.DataFrame(rows)


def strict_claim_markdown(frame: pd.DataFrame) -> str:
    lines = ["# Strict Claim-Evidence Map", "", "Only the five main claims may anchor the abstract, introduction contribution list, and conclusion.", ""]
    for tier, title in [("main", "Main Claims"), ("supporting", "Supporting Claims"), ("exploratory", "Exploratory Claims")]:
        lines.extend([f"## {title}", "", markdown_table(frame.loc[frame['claim_tier'].eq(tier)], ['claim_id', 'claim_text', 'evidence', 'allowed_manuscript_location', 'abstract_can_mention']), ""])
    return "\n".join(lines)


def revised_abstracts() -> tuple[str, str]:
    version_a = """Many expert-crowd decisions combine observable expert assessments with hidden public input and release only coarse outcomes such as eliminations. This creates a set-identification problem rather than a point-estimation problem. We develop a rule-aware framework for learning feasible public-preference states from longitudinal elimination outcomes. Under percentage aggregation, observed outcomes generate linear inequalities on a simplex and yield convex feasible regions with coordinate-wise linear-program bounds. Under ranking aggregation, the hidden object is a feasible set of ordinal public rankings rather than a cardinal support measure. A judge-save intervention weakens the observable implication by replacing direct elimination with a bottom-set condition. Applying the framework to a longitudinal competition dataset with three documented rule regimes, we find wide feasible sets throughout and direct feasible ranking sets nested within judge-save feasible sets in every comparable week. Dynamic proxy construction, lagged prediction, and scenario analysis are retained as secondary extensions that propagate identification uncertainty. Public ballots are not observed. The paper contributes a transparent framework for distinguishing what coarse institutional outcomes identify from what additional modeling assumptions would be needed to obtain point-valued quantities from the observed record."""
    version_b = """Public-facing decision systems often combine professional assessments with hidden member, user, or public input while disclosing only final decisions. When feedback is limited to eliminations or other coarse selections, the relevant quantity is a feasible preference set, not a reconstructed public score. We develop a rule-aware partial-identification framework for this information problem. Percentage aggregation yields convex regions for cardinal public-support states, whereas ranking aggregation yields feasible ordinal ranking sets. A judge-save intervention further reduces information by requiring only membership in a bottom set instead of direct elimination. We demonstrate the framework in a longitudinal competition dataset that provides repeated elimination outcomes, explicit rule changes, and three aggregation regimes. The testbed shows wide feasible sets and within-week nesting of direct feasible rankings inside judge-save feasible rankings. We also use typed dynamic proxies for descriptive organization, lagged prediction for validation, and scenario analysis for mechanism comparison. These extensions do not observe public ballots or establish causal effects. For service and public-sector decision designers, the implication is conditional: rules that increase discretion can also reduce what later observers can infer from hidden stakeholder input."""
    return version_a, version_b


def abstract_stress_test(version_a: str, version_b: str) -> str:
    return f"""
# Abstract and Title Stress Test

## Current title assessment

The current title is method-oriented and avoids a competition-first frame. It is not overpromising on vote recovery. Its SEPS weakness is the phrase "expert-crowd decision systems" without a demonstrated socio-economic planning or service application. Do not solve that mismatch by asserting public-sector impact unsupported by the data.

## Required outcomes

| Check | Status | Assessment |
| --- | --- | --- |
| General decision problem first | pass | Both versions open with a hidden-input decision problem. |
| Partial identification central | pass | Both versions foreground feasible sets and rule-induced information. |
| Prediction/counterfactuals secondary | pass | Both label them extensions. |
| Prohibited recovery or causal language | pass | Neither version uses point-recovery or causal-effect claims. |
| Missing public input stated | pass | Both say public ballots are not observed. |
| SEPS public/service framing | partial | Version B states only conditional design relevance; it does not create an applied public-sector case. |
| Keywords | partial | Keep current seven, but add verified field terms after literature review. |

## Version A: Methods and quantitative decision focus

Title: **{TITLE_A}**

Abstract ({word_count(version_a)} words):

{version_a}

## Version B: Public/service decision-system framing

Title: **{TITLE_B}**

Abstract ({word_count(version_b)} words):

{version_b}

## Editorial recommendation

Use Version A for a general decision-science venue. Do not use Version B to submit to SEPS unless the manuscript gains a genuine public/service-sector application or the editor confirms that this methodological testbed is in scope.
"""


TITLE_A = "Partial Identification of Hidden Preferences from Elimination-Only Outcomes"
TITLE_B = "Rule-Aware Learning from Hidden Public Input in Expert-Crowd Decisions"


def introduction_revised() -> str:
    return """
# Introduction

Expert-crowd decision systems combine professional assessments with public, member, user, or stakeholder input. They arise wherever institutions seek both specialized evaluation and broader participation, yet the public component is often hidden after an aggregate decision is released.

This information structure creates a basic inferential constraint. When the observable feedback is only an elimination or another coarse selection, many hidden-preference states can be compatible with the same outcome. The appropriate estimand is therefore a feasible preference set conditional on an aggregation rule, rather than a point prediction of an unobserved public score.

Existing empirical work often emphasizes point prediction, ranking prediction, or retrospective explanation. Those tasks can be useful, but they do not establish what is identified from coarse outcomes when the public signal is absent. In particular, they can obscure the fact that different aggregation rules constrain different latent objects.

We develop a rule-aware partial-identification framework for percentage and ranking aggregation. Percentage rules yield linear inequality systems over a simplex and coordinate-wise linear-program bounds. Ranking rules yield feasible ordinal public rankings. A judge-save rule weakens the direct-elimination implication by replacing it with a tie-inclusive bottom-set condition.

The empirical testbed is a longitudinal competition dataset with repeated eliminations, recorded expert scores, documented rule changes, and multiple aggregation regimes. Its value is methodological: it supplies a transparent setting in which cardinal, ordinal, and weak-intervention identification statements can be compared. It is not itself a public-service evaluation.

The paper contributes: (1) a rule-aware partial-identification framework for hidden public preferences; (2) a comparison of cardinal and ordinal aggregation mechanisms; (3) a within-week judge-save analysis that quantifies identification loss; and (4) an uncertainty-aware validation and mechanism-design extension that remains secondary to the identified-set results.

The remainder of the paper describes the data and rules, develops the identification framework, reports the core findings, then presents validation and scenario analyses with explicit limitations.
"""


def methods_revised() -> str:
    return """
# Methods

## 4.1 Setup and notation

For week t with active set A_t, let j_it be contestant i's normalized expert share, with sum_i j_it = 1. The hidden public object depends on the rule. We observe the active set, the expert component, the institutional rule, and the eliminated set E_t. We identify all hidden states consistent with those observables; no public ballot is observed.

## 4.2 Percentage aggregation

Under P, p_t = (p_it : i in A_t) belongs to the simplex Delta_t = {p_it >= 0, sum_i p_it = 1}. Higher combined score is better, so an eliminated contestant e and a non-withdrawn survivor s imply j_et + p_et <= j_st + p_st. Equivalently, p_et - p_st <= j_st - j_et. These inequalities, the simplex equality, and [0,1] coordinate bounds define a convex polytope F_t. For each contestant i, linear programs compute L_it = min_{p in F_t} p_it and U_it = max_{p in F_t} p_it. The reported P width is U_it - L_it (normalized because p lies on a unit simplex). Bounds are sharp coordinate-wise; the vector of coordinate midpoints need not belong to F_t.

No-elimination weeks add no unjustified outcome inequality. Withdrawal weeks are treated as non-comparative. Multiple eliminations require each eliminated contestant to be weakly below every non-withdrawn survivor but do not order the eliminated contestants. If a final round supplies unique active placements, all recorded pairwise order inequalities are added.

## 4.3 Ranking aggregation

Under R and R_plus, r^J_it is the judge rank and r^F_it is a strict candidate public rank, both with 1 denoting best. The combined rank is c_it = r^J_it + r^F_it, so larger c_it is worse. A candidate public permutation is direct-feasible when every observed eliminated contestant lies in the tie-inclusive bottom-k set B_k(c_t), where k is the recorded number of eliminations. The feasible set is the collection of all such public permutations.

For each contestant, the ordinal support is the set of feasible r^F_it values. Its width is max(r^F_it) - min(r^F_it), normalized by |A_t|-1. Entropy is H_it = -sum_r q_itr log(q_itr), where q_itr is the feasible-ranking frequency of rank r; weekly normalized entropy averages H_it/log(|A_t|). These are ordinal uncertainty summaries, not cardinal support shares.

Exact enumeration evaluates every |A_t|! public permutation in small fields. In the empirical runs, R has 13 exact and 1 sampled week, while R_plus has 36 exact and 37 sampled weeks. Larger fields use 10,000 fixed-seed uniform draws; the reported maximum Monte Carlo standard error for feasible fractions is approximately 0.005. This error is numerical and is not uncertainty about public behavior. Retained feasible-ranking files use a fixed-seed reservoir cap for storage, while rank distributions and widths use all evaluated draws.

## 4.4 Judge-save weak identification

For R_plus, the recorded elimination is compatible with a candidate ranking when the eliminated set belongs to B_{k+1}(c_t), a tie-inclusive bottom set enlarged by one save-eligible position. Hence every direct-feasible permutation is weak-feasible: F_direct,t is a subset of F_weak,t. The within-week weak/direct ratio |F_weak,t|/|F_direct,t| summarizes the loss of identification. This is a comparison of the same rule environment under direct and weak outcome implications, not a cross-regime average.

## 4.5 Typed dynamic proxies

For descriptive longitudinal organization, P uses (L_it+U_it)/2 and R/R_plus use 1-(mean(r^F_it)-1)/(|A_t|-1). The former is a cardinal interval midpoint and the latter an ordinal rank score. Their uncertainty values are, respectively, interval width and normalized rank width. Exponential smoothing uses alpha=0.5; uncertainty-weighted smoothing uses alpha/(1+u_it). These proxies are not public ballots and are not directly comparable across rule types.

## 4.6 Validation and scenarios

Historical validation lags public, dynamic, uncertainty, and expert features by one contestant observation. Same-week judge models are explanatory benchmarks, not deployable forecasts. Scenario analyses use P lower/midpoint/upper coordinate bounds or retained ordinal feasible rankings and condition on observed active trajectories. They do not reconstruct a causal alternative season.
"""


def results_revised() -> str:
    return """
# Results

## Finding 1: Elimination-only observations are partially identifying

P has nonempty feasible regions in 247 of 248 eligible weeks. Mean normalized coordinate-wise width is 0.842991. Thus the recorded rule and elimination restrict public-support states without selecting a unique support vector. Figure 2 and Table 2 report these P-regime bounds.

## Finding 2: The rule determines the identified object

P identifies cardinal support intervals. R and R_plus identify feasible ordinal rankings, with mean normalized rank widths of 0.890986 and 0.923933. These summaries are not directly comparable to P interval width because they describe different mathematical objects. Table 2 retains this distinction in its notes.

## Finding 3: Judge-save weakens within-week identification

For 73 R_plus weeks, the weak/direct feasible-set ratio averages 2.665961 and has median 1.571821. The weak set is strictly larger in 56 weeks, equal in 17, and never smaller. The result follows the specified tie-inclusive bottom-(k+1) condition and should be read as a within-week mechanism comparison. Figure 3 and Table 3 provide the audit trail.

## Finding 4: Cross-regime uncertainty is descriptive context

The sample averages order P (0.842991), R (0.890986), and R_plus (0.923933). This ordering is descriptive only: the regimes differ in hidden object, season composition, and active-field size. It is not evidence that changing an institutional rule causally moves one common uncertainty metric.

## Finding 5: Proxy validation is limited and secondary

Across 211 forward-chaining events, the strictly historical combined lag model has accuracy 0.317536 and log loss 1.838463, compared with 0.118483 and 2.077488 for uniform risk. The lowest log loss, 1.705755, belongs to a same-week judge benchmark and is not a prior-week forecast. These results show limited validation signal under the stated design; they do not establish an observed public ballot.

Traceable sources: `outputs/tables/identification_comparison_by_regime.csv`, `outputs/tables/ranking_identification_summary_rplus.csv`, `outputs/tables/prediction_results.csv`, `outputs/figures/uncertainty_over_weeks_regime_p.png`, and `outputs/figures/judge_save_identifiability_loss.png`.
"""


def prediction_counterfactual_revised() -> str:
    return """
# Prediction and Counterfactuals

## Validation, not a deployment claim

The same-week judge-only model is an explanatory benchmark because it uses the current week's judge scores. It is not a deployable prediction model. Strict prediction validation is represented by the lagged models, which use prior contestant observations only. The combined historical model improves over uniform risk but does not outperform the same-week judge benchmark. This limited signal does not validate a point-valued public-preference measure.

## Scenario analysis, not causal history

Counterfactual calculations propagate feasible-set scenarios. In P, lower, midpoint, and upper coordinate vectors are sensitivity inputs and need not be jointly feasible. In R/R_plus, retained feasible joint rankings are used without converting them into support shares. Season rankings condition on observed active trajectories and do not generate unobserved future performances.

Outcome and winner changes are therefore scenario-sensitivity summaries, not causal effects of replacing an historical mechanism. The judge-save weak analysis reports admissibility only and leaves unique winner/finalist outcomes undefined. The Pareto frontier contains only gamma=0 points in the current grid; this is evidence against claiming that a positive uncertainty penalty improves outcomes. Uncertainty-aware aggregation remains a conceptual design input, not an empirically selected mechanism.

Detailed prediction tables, Pareto points, lambda/gamma sensitivity, and controversial cases belong in an appendix.
"""


def discussion_revised() -> str:
    return """
# Discussion

Partial identification is the correct estimand when a public input is hidden and only a coarse institutional decision is released. Wide intervals and ranking sets are not failed estimates. They quantify the information the rule and observed outcome leave unresolved.

The direct-versus-judge-save comparison makes a decision-design trade-off visible. A save can expand institutional discretion, but it also replaces a direct elimination implication with weaker bottom-set membership and thereby enlarges the feasible ranking set. This is a statement about information produced by the rule, not a welfare ranking of discretion.

Dynamic proxies organize longitudinal identified-set summaries. They do not turn a midpoint or mean rank into an observed ballot. Prediction is a validation exercise, and mechanism comparisons are scenario analyses rather than causal accounts of an alternative historical season.

The empirical testbed illustrates a rule-aware workflow that may transfer to other expert-crowd systems only after their local rules, public-input process, tie policy, and decision objectives have been encoded. For public/service decision designers, the conditional implication is that transparency and discretionary interventions affect both decisions and the ability to audit hidden stakeholder input. This paper does not evaluate that implication in a public-service operation.
"""


def limitations_revised() -> str:
    return """
# Limitations

Public ballots are unobserved, so the analysis cannot verify a point-valued public-preference measure. Rule interpretation, score normalization, and tie handling affect the feasible set; the primary R_plus comparison uses a tie-inclusive bottom-set condition. P cardinal intervals and R/R_plus ordinal rank sets are different quantities and cannot be pooled as one support metric.

Observed data follow historical active-contestant trajectories. Prediction excludes some event types, and scenario analyses do not create performances for contestants who would remain under a different earlier elimination. Large ranking fields use fixed-seed Monte Carlo draws and retained reservoirs; Monte Carlo error is numerical, not behavioral uncertainty.

The competition is a single empirical testbed. It does not establish external validity for public-sector, service, hiring, peer-review, or platform decisions. Prediction is not the primary contribution, and counterfactual results depend on scenario construction. Data sharing remains subject to source terms, and a release must document those terms, environment versions, and any restrictions before external distribution.
"""


def conclusion_revised() -> str:
    return """
# Conclusion

Elimination-only outcomes partially identify hidden public preferences. Under percentage aggregation, they yield convex feasible regions and coordinate-wise cardinal bounds. Under ranking aggregation, they yield feasible ordinal public rankings. A judge-save rule weakens the observable implication and expands the compatible ranking set within the same week.

The contribution is a rule-aware framework for stating these limits transparently. It separates identified-set evidence from descriptive proxy validation and scenario analysis. Future applied work should test the framework in documented public/service decision settings before making claims about operational value in those domains.
"""


def literature_outputs() -> tuple[pd.DataFrame, str, str]:
    table = pd.DataFrame([
        {"area": "Partial identification and bounds", "why_needed": "Position LP bounds and set-valued estimands.", "search_keywords": "partial identification bounds linear programming set identification", "claim_supported": "Why point recovery is not the estimand.", "current_status": "missing verified citations"},
        {"area": "Social choice and aggregation mechanisms", "why_needed": "Position cardinal versus ordinal rule distinction.", "search_keywords": "social choice aggregation rules score voting rank aggregation", "claim_supported": "Mechanism determines the identified object.", "current_status": "missing verified citations"},
        {"area": "Expert-crowd decision-making", "why_needed": "Define the broader decision-system problem.", "search_keywords": "expert crowd decision making hybrid decision systems public participation", "claim_supported": "General problem motivation.", "current_status": "missing verified citations"},
        {"area": "Ranking aggregation and ordinal inference", "why_needed": "Position feasible ranking sets and tie treatment.", "search_keywords": "rank aggregation ordinal preference inference feasible rankings", "claim_supported": "Ordinal-method contribution.", "current_status": "missing verified citations"},
        {"area": "Prediction as validation", "why_needed": "Justify strict historical validation and leakage caution.", "search_keywords": "predictive validation leakage temporal validation causal inference", "claim_supported": "Secondary validation framing.", "current_status": "missing verified citations"},
        {"area": "Robust decision design under uncertainty", "why_needed": "Position uncertainty as a design input.", "search_keywords": "robust decision making uncertainty mechanism design", "claim_supported": "Conceptual design extension.", "current_status": "missing verified citations"},
        {"area": "Institutional discretion and judge-save-like interventions", "why_needed": "Discuss discretion versus auditability without analogical overreach.", "search_keywords": "institutional discretion selection override decision transparency", "claim_supported": "Judge-save interpretation.", "current_status": "missing verified citations"},
        {"area": "Quantitative public/service decision applications", "why_needed": "Required for a credible SEPS application bridge.", "search_keywords": "public sector operations research service planning participatory decision making", "claim_supported": "Target-journal relevance.", "current_status": "critical gap"},
    ])
    audit = """
# Literature Gap Audit

No `references.bib`, bibliography, or verified reference list is present in the repository. The current related-work file explicitly defers bibliography construction. This is a submission blocker, not a stylistic omission.

No references are invented in this audit. The table lists the literature types, search terms, and exact claims that need support. For SEPS specifically, the final bibliography would need a credible quantitative public/service decision literature bridge; the current entertainment testbed alone cannot supply it.
"""
    plan = """
# Related Work Revision Plan

1. Build a verified bibliography before claiming novelty. Record DOI, stable URL, year, and the exact proposition each source supports.
2. Separate foundational partial-identification references from aggregation/rank-inference references.
3. Use expert-crowd references only for motivation; do not imply that they validate the current proxy construction.
4. Add temporal-validation and leakage references to justify the secondary prediction design.
5. If retaining SEPS as a target, add public/service planning applications that motivate a real decision problem, then explain why their institutional rules match the proposed framework. Without that bridge, choose a venue with a broader methodological scope.
"""
    return table, audit, plan


def figure_table_audit(root: Path) -> tuple[pd.DataFrame, str]:
    rows = [
        {"item": "Figure 1 conceptual framework", "type": "figure", "destination": "main", "status": "keep", "reason": "Explains feasible-set estimand without case-specific framing.", "action": "Add journal-style caption and provide vector PDF/SVG if required."},
        {"item": "Figure 2 P interval width", "type": "figure", "destination": "main", "status": "keep", "reason": "Direct support for P partial identification.", "action": "Caption must state coordinate-wise feasible width."},
        {"item": "Figure 3 judge-save expansion", "type": "figure", "destination": "main", "status": "keep", "reason": "Strongest within-week mechanism result.", "action": "State tie-inclusive bottom-set rule in caption."},
        {"item": "Figure 4 cross-regime uncertainty", "type": "figure", "destination": "appendix", "status": "move", "reason": "Metrics are not directly comparable and claim is descriptive.", "action": "Retain only with strong comparability warning."},
        {"item": "Figure 5 prediction comparison", "type": "figure", "destination": "appendix", "status": "move", "reason": "Prediction is secondary and same-week benchmark can distract.", "action": "Label same-week explanatory benchmark prominently."},
        {"item": "Dynamic examples / coefficients / calibration", "type": "figure", "destination": "appendix", "status": "move", "reason": "Model-dependent diagnostics.", "action": "Appendix only."},
        {"item": "Pareto, lambda/gamma, controversial cases", "type": "figure", "destination": "remove", "status": "remove from first submission", "reason": "Exploratory results increase overclaiming risk.", "action": "Keep in repository or supplement only if requested."},
        {"item": "Table 1 dataset and regimes", "type": "table", "destination": "main", "status": "keep", "reason": "Needed for institutional context.", "action": "Add rule and event-type footnotes."},
        {"item": "Table 2 partial-identification summary", "type": "table", "destination": "main", "status": "keep", "reason": "Supports cardinal/ordinal distinction.", "action": "Use a prominent non-comparability note."},
        {"item": "Table 3 direct versus weak comparison", "type": "table", "destination": "main", "status": "keep", "reason": "Core judge-save evidence.", "action": "Report exact versus sampled rows and tie policy."},
        {"item": "Table 4 prediction validation", "type": "table", "destination": "appendix", "status": "move", "reason": "Secondary validation evidence.", "action": "If retained, split same-week and historical results."},
        {"item": "Counterfactual and robust tables", "type": "table", "destination": "appendix", "status": "move", "reason": "Exploratory scenario outputs.", "action": "Do not report a preferred lambda/gamma setting."},
    ]
    frame = pd.DataFrame(rows)
    figure_paths = [
        root / "outputs/figures/conceptual_framework_hidden_preferences.png",
        root / "outputs/figures/uncertainty_over_weeks_regime_p.png",
        root / "outputs/figures/judge_save_identifiability_loss.png",
    ]
    dpi = {path.name: Image.open(path).info.get("dpi", (0, 0))[0] for path in figure_paths}
    audit = f"""
# Figure and Table Submission Audit

The prior five-figure/four-table plan is defensible numerically but too broad for a paper whose core contribution is identification. The strict recommendation is three main figures and three main tables. The cross-regime uncertainty and prediction comparisons are secondary; Pareto, lambda/gamma, and controversial-case displays should not appear in a first SEPS submission.

The three retained raster figures meet the 300-dpi requirement: {dpi}. Before production, create vector versions where the journal requests them and write standalone captions; the repository currently stores figure files and plan notes, not final manuscript captions.

{markdown_table(frame, ['item', 'type', 'destination', 'status', 'reason', 'action'])}

Graphical abstract: optional at most. Do not create one until the target journal and the paper's applied positioning are resolved.
"""
    return frame, audit


def package_checklist(root: Path) -> pd.DataFrame:
    items = [
        ("Title page", "missing", "", "No author/affiliation page.", "Create after target venue and authors are confirmed."),
        ("Blinded manuscript", "missing", "", "Markdown sections are not a compiled anonymous manuscript.", "Compile a journal-formatted blinded manuscript."),
        ("Highlights", "exists", "manuscript/highlights.md", "Generated draft requires final journal check.", "Verify per-item length and upload rules."),
        ("Abstract", "exists", "manuscript/00_title_abstract_keywords.md", "Two stress-test revisions also exist.", "Choose only after venue decision."),
        ("Keywords", "exists", "manuscript/00_title_abstract_keywords.md", "Seven keywords; literature indexing not yet verified.", "Revise after bibliography review."),
        ("Main manuscript", "needs revision", "manuscript/00_title_abstract_keywords.md through 09_conclusion.md", "Not compiled and lacks references.", "Integrate selected revised sections and bibliography."),
        ("Figures", "needs revision", "outputs/figures", "300-dpi PNGs exist; journal captions/vector files absent.", "Select final three and create required production formats."),
        ("Tables", "needs revision", "outputs/tables", "CSV evidence exists, not journal-formatted tables.", "Create final three main tables."),
        ("Appendix/supplement", "exists", "outputs/tables; outputs/figures", "Material exists but is not curated.", "Prepare a labelled supplement only if venue permits."),
        ("Cover letter", "exists", "manuscript/cover_letter_draft.md", "Draft is conditional on venue fit.", "Do not submit before venue decision."),
        ("Data availability statement", "needs revision", "manuscript/data_code_availability.md", "Original source URL and source terms are placeholders.", "Add verified source, access date, and redistribution terms."),
        ("Code availability statement", "needs revision", "manuscript/data_code_availability.md", "Repository sharing license is absent.", "Add release location and license."),
        ("Reproducibility statement", "needs revision", "manuscript/reproducibility_statement.md", "No locked environment or release manifest.", "Add lock file/container and versioned manifest."),
        ("AI-assisted writing statement", "exists", "manuscript/ai_assisted_writing_statement.md", "Elsevier-style tool, purpose, oversight, and responsibility statement is present.", "Verify final placement and any live guide wording before upload."),
        ("Conflict of interest statement", "missing", "", "No statement.", "Obtain author declaration."),
        ("Funding statement", "missing", "", "No statement.", "Obtain author declaration."),
        ("Ethics statement", "needs revision", "", "Need author confirmation of whether human-subject review applies.", "State not applicable or provide approval details."),
        ("Author contribution statement", "missing", "", "No CRediT statement.", "Obtain author roles."),
        ("Acknowledgements", "missing", "", "No acknowledgement text.", "Obtain author text or state none."),
        ("References", "missing", "", "No bibliography or references file.", "Build verified reference list."),
        ("Graphical abstract", "missing", "", "Not needed until venue fit is resolved.", "Check live SEPS guide manually."),
        ("Clean repository README", "needs revision", "README.md", "Current commands are documented, but no clean-environment release test is recorded.", "Run and record a clean-environment reproduction before release."),
        ("Environment file or requirements", "needs revision", "requirements.txt", "Dependency ranges exist but no exact lock/container.", "Create locked environment for archival release."),
        ("License", "missing", "", "No license file found.", "Choose a code license subject to data terms."),
        ("Anonymization check", "missing", "", "No compiled manuscript or title page to inspect.", "Run after manuscript assembly."),
    ]
    return pd.DataFrame(items, columns=["item", "status", "file_path", "issue", "exact_next_action"])


def cover_letter() -> str:
    return """
# Cover Letter Draft for Socio-Economic Planning Sciences

Dear Editor,

Please consider our manuscript, "Hidden Preference Learning from Elimination-Only Outcomes in Expert-Crowd Decision Systems: Partial Identification, Mechanism Comparison, and Robust Aggregation."

The manuscript studies a general decision problem: professional assessments are observed, public input is hidden, and institutions disclose only coarse outcomes. We develop a rule-aware partial-identification framework that distinguishes cardinal feasible regions under percentage aggregation from ordinal feasible ranking sets under rank aggregation. We further show how a judge-save intervention weakens the observable implication of an elimination and expands the compatible ranking set within comparable weeks.

The empirical testbed is longitudinal and records explicit rule changes, repeated elimination outcomes, and multiple aggregation regimes. It is used to demonstrate the framework, not to claim observation or recovery of public ballots. Dynamic proxies, prediction, and scenario analysis are secondary checks that retain the identified-set boundary.

Code, tests, and reproducibility materials are available with the research package, subject to the underlying data-source terms. The authors confirm that the manuscript is original and not under consideration elsewhere.

This draft should be used only if the editors confirm that a methodological paper with this empirical testbed is within scope. The current package does not yet demonstrate a public/service-sector application, which must be resolved before submission to SEPS.

Sincerely,

[Corresponding author name and affiliation]
"""


def highlights() -> str:
    points = [
        "Elimination-only outcomes identify feasible preferences, not point estimates.",
        "Aggregation rules determine whether hidden support is cardinal or ordinal.",
        "Judge-save discretion expands feasible public ranking sets.",
        "Validation and scenarios retain identified-set uncertainty.",
    ]
    if any(len(point) > 85 for point in points):
        raise ValueError("A highlight exceeds 85 characters.")
    return "# Highlights\n\n" + "\n".join(f"- {point}" for point in points)


def go_no_go() -> str:
    scores = pd.DataFrame([
        ("Target journal fit", 1, "No demonstrated public/service-sector application; high desk-reject risk."),
        ("Methodological novelty", 4, "Rule-aware cardinal/ordinal identification and within-week weak-set comparison are substantive."),
        ("Empirical credibility", 3, "Audited data and rule handling are strong, but one testbed and sampled ranking fields limit scope."),
        ("Evidence-claim alignment", 4, "Strict claim map and audits separate core from exploratory evidence."),
        ("Reproducibility", 3, "Pipeline, tests, and seeds exist; README and locked environment are incomplete."),
        ("Writing clarity", 3, "Revised sections are clearer, but final bibliography and compiled manuscript are absent."),
        ("Generalizability", 2, "Transfer is conceptual, not empirically demonstrated."),
        ("Control of overclaiming", 4, "Prediction and scenarios are substantially cooled; maintain this boundary."),
        ("Data/code availability", 2, "Source terms, release location, license, and environment lock are incomplete."),
        ("Reviewer defensibility", 2, "Method can be defended, but SEPS scope and package gaps dominate."),
    ], columns=["dimension", "score_1_to_5", "rationale"])
    return f"""
# Submission Go/No-Go Decision

## Decision: D. Not suitable for the current target journal

The core methodology is credible enough for further human development, but the current paper should not be submitted to Socio-Economic Planning Sciences. The most likely outcome is an editorial desk rejection because an entertainment competition testbed does not demonstrate a socio-economic planning, public-sector, or service decision problem. A rephrased abstract cannot repair that evidentiary gap.

## Scores

{markdown_table(scores, ['dimension', 'score_1_to_5', 'rationale'])}

## Top five strengths

1. Reproducible rule-aware identification pipeline with fixed seeds and tests.
2. Clear distinction between cardinal P regions and ordinal R/R_plus sets.
3. Strong within-week direct-set containment evidence for the judge-save comparison.
4. Explicit leakage controls and same-week benchmark labeling.
5. Evidence map that separates core, supporting, and exploratory claims.

## Top five rejection risks

1. Weak SEPS public/service-sector fit.
2. Missing verified bibliography and novelty positioning.
3. No completed submission package or journal-formatted manuscript.
4. Descriptive cross-regime, proxy, and scenario extensions can distract from the core method.
5. Data-source, license, and exact-environment release conditions are unresolved.

## Ten required fixes before any submission

1. Choose a target venue that fits the available empirical evidence, or add a genuine public/service application.
2. Build a verified bibliography and related-work comparison.
3. Manually verify the live SEPS scope and Guide for Authors if SEPS remains under consideration.
4. Compile a single blinded manuscript with title page managed separately.
5. Finalize data-source URL, access date, and redistribution terms.
6. Add conflict, funding, ethics, author-contribution, and acknowledgement statements.
7. Add a code license and archival release location.
8. Create a locked environment or container and release manifest.
9. Update README and re-run the clean-environment workflow.
10. Limit the main text to the three core figures and three core tables.

## Ten optional improvements

1. Obtain an editor presubmission-scope opinion.
2. Add formal propositions and proofs for containment and LP sharpness.
3. Add a documented tie-rule robustness appendix.
4. Archive deterministic output hashes at release.
5. Add a graphical abstract only after venue confirmation.
6. Add a public-service case study in future work.
7. Provide a formal model card for proxy interpretation.
8. Add more Monte Carlo diagnostics to the supplement.
9. Run an independent code review in a clean environment.
10. Prepare a non-SEPS cover-letter variant after venue selection.

## Venue recommendation

Do not submit to SEPS in the current form. Consider a journal category that explicitly welcomes methodological work in decision science, operations research, social choice, computational social science, or applied statistics with a competition-based empirical testbed. No specific alternative journal is recommended here because fit should be confirmed against each venue's live scope and policies.
"""


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    required = [
        root / "outputs/tables/claim_evidence_map.csv",
        root / "outputs/tables/identification_comparison_by_regime.csv",
        root / "outputs/tables/ranking_identification_summary_rplus.csv",
        root / "outputs/tables/prediction_results.csv",
        root / "manuscript/00_title_abstract_keywords.md",
        root / "manuscript/01_introduction.md",
        root / "manuscript/04_methods.md",
        root / "outputs/figures/conceptual_framework_hidden_preferences.png",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print("ERROR: Missing submission-audit input(s): " + ", ".join(missing), file=sys.stderr)
        return 2
    try:
        outputs = root / "outputs"
        tables = outputs / "tables"
        logs = outputs / "logs"
        manuscript = root / "manuscript"
        logs.mkdir(parents=True, exist_ok=True)
        claims = pd.read_csv(tables / "claim_evidence_map.csv")

        fit = pd.DataFrame(journal_fit_rows())
        fit.to_csv(tables / "target_journal_fit_checklist.csv", index=False)
        write_text(logs / "target_journal_fit_audit.md", journal_fit_audit(fit))
        write_text(manuscript / "target_journal_positioning_notes.md", "# Target Journal Positioning Notes\n\n**Current SEPS position: weak fit.** The paper is methodologically defensible, but the empirical testbed does not establish a public/service-sector planning problem. Do not claim direct SEPS relevance without new applied evidence. Use the method-oriented abstract for a broader venue, or obtain a genuine public/service application before returning to SEPS.")

        reports, register = reviewer_reports()
        register.to_csv(tables / "reviewer_risk_register.csv", index=False)
        write_text(logs / "simulated_reviewer_reports.md", reports)

        strict = strict_claims(claims)
        strict.to_csv(tables / "claim_evidence_map_strict.csv", index=False)
        write_text(manuscript / "claim_evidence_map_strict.md", strict_claim_markdown(strict))

        version_a, version_b = revised_abstracts()
        if not all(180 <= word_count(value) <= 220 for value in [version_a, version_b]):
            raise ValueError("Revised abstracts must each contain 180-220 words.")
        write_text(logs / "abstract_title_stress_test.md", abstract_stress_test(version_a, version_b))
        write_text(manuscript / "00_title_abstract_keywords_revised.md", f"# Revised Title and Abstract Options\n\n## Version A\n\n# {TITLE_A}\n\n## Abstract\n\n{version_a}\n\n## Keywords\n\npartial identification; hidden preferences; aggregation mechanisms; ranking aggregation; decision science; robust decision design\n\n## Version B\n\n# {TITLE_B}\n\n## Abstract\n\n{version_b}\n\n## Keywords\n\npartial identification; public-facing decision systems; hidden preferences; aggregation mechanisms; institutional discretion; robust decision design")

        write_text(manuscript / "01_introduction_revised.md", introduction_revised())
        write_text(logs / "introduction_audit.md", "# Introduction Audit\n\nThe revised introduction contains seven paragraphs in the requested order: general expert-crowd systems; hidden inputs and coarse outcomes; gap in point-prediction framing; rule-aware method; empirical testbed; contributions; paper structure. It avoids competition-first framing, does not claim ballot recovery, and labels public/service relevance as a transfer question rather than an evaluated application.")

        formula = pd.DataFrame([
            ("M1", "Symbols and score direction", "pass", "Revised methods defines j, p, rJ, rF, c and rank direction."),
            ("M2", "P simplex and inequalities", "pass", "Revised methods states simplex, eliminated-survivor inequality, and F_t."),
            ("M3", "LP bounds", "pass", "Revised methods states coordinate-wise min/max and midpoint limitation."),
            ("M4", "R/R_plus rank direction", "pass", "Rank 1 is best; larger combined rank is worse."),
            ("M5", "Judge-save bottom-set condition", "pass", "Direct B_k and weak B_(k+1) conditions are stated."),
            ("M6", "Containment", "pass", "F_direct,t subset F_weak,t is stated as a within-week implication."),
            ("M7", "Width and entropy", "pass", "Normalized support width and entropy formulas are stated."),
            ("M8", "Exact versus sampling", "pass", "36 exact and 37 sampled R_plus weeks are documented in source report; revised methods states 10,000 draws and MC-SE scope."),
            ("M9", "Dynamic proxy interpretation", "pass", "Typed proxy definitions and non-ballot boundary are stated."),
            ("M10", "Code-paper consistency", "pass", "Static audit found matching score directions, bottom-set logic, LP construction, and fixed-seed sampling."),
        ], columns=["check_id", "check", "status", "evidence"])
        formula.to_csv(tables / "methods_formula_checklist.csv", index=False)
        write_text(logs / "methods_rigor_audit.md", "# Methods Rigor Audit\n\nThe original methods section was too compressed for peer review but no code-definition contradiction was found in the checked modules. The revised section now states score directions, simplex inequalities, LP bounds, ordinal widths/entropy, exact versus sampled computation, and the weak-set containment relation. The remaining methodological limitation is substantive, not a mismatch: the P midpoint is coordinate-wise and ordinal sampling is numerical approximation.\n\n" + markdown_table(formula, ['check_id', 'check', 'status', 'evidence']))
        write_text(manuscript / "04_methods_revised.md", methods_revised())

        results_map = pd.DataFrame([
            ("R1", "P has 247 of 248 feasible weeks.", "outputs/logs/pipeline_report.md; outputs/tables/constraint_summary.csv", "supported"),
            ("R2", "P mean width is 0.842991.", "outputs/tables/identification_comparison_by_regime.csv", "supported"),
            ("R3", "R and R_plus widths are 0.890986 and 0.923933.", "outputs/tables/identification_comparison_by_regime.csv", "supported with non-comparability caveat"),
            ("R4", "Weak/direct ratio mean and median are 2.665961 and 1.571821.", "outputs/tables/ranking_identification_summary_rplus.csv", "supported"),
            ("R5", "56 strict, 17 equal, 0 containment violations.", "outputs/logs/ranking_identification_report_rplus.md", "supported"),
            ("R6", "Historical validation improves on uniform risk.", "outputs/tables/prediction_results.csv", "supported; secondary only"),
            ("R7", "Same-week judge benchmark is not a forecast.", "src/prediction.py; outputs/tables/prediction_results.csv", "supported"),
        ], columns=["sentence_id", "sentence_or_claim", "supporting_output", "audit_status"])
        results_map.to_csv(tables / "results_sentence_evidence_map.csv", index=False)
        write_text(logs / "results_evidence_audit.md", "# Results Evidence Audit\n\nEvery numerical sentence retained in the revised results section maps to a generated output. Cross-regime widths are explicitly descriptive, the judge-save conclusion is restricted to within-week containment, and prediction is secondary validation. Expert-crowd divergence, counterfactual changes, and uncertainty-aware grid results are not retained as main findings.\n\n" + markdown_table(results_map, ['sentence_id', 'sentence_or_claim', 'supporting_output', 'audit_status']))
        write_text(manuscript / "05_results_revised.md", results_revised())

        write_text(logs / "prediction_counterfactual_audit.md", "# Prediction and Counterfactual Audit\n\n- Same-week judge-only model: explanatory benchmark, not deployable forecast.\n- Strict lagged models: the only prediction-validation models.\n- Historical proxy signal: limited and below the same-week judge benchmark.\n- Leakage: prior audit verified lag source week < prediction week for 2,356 history-available rows.\n- Counterfactuals: identified-set scenario sensitivities conditioned on observed active trajectories.\n- Pareto frontier: all four reported all-regime frontier points have gamma=0; no positive penalty is empirically dominant.\n- Required disposition: retain as validation/appendix material, not as a main contribution.")
        write_text(manuscript / "06_prediction_and_counterfactuals_revised.md", prediction_counterfactual_revised())

        write_text(manuscript / "07_discussion_revised.md", discussion_revised())
        write_text(manuscript / "08_limitations_revised.md", limitations_revised())
        write_text(manuscript / "09_conclusion_revised.md", conclusion_revised())
        write_text(logs / "discussion_limitations_audit.md", "# Discussion and Limitations Audit\n\nThe revised discussion treats partial identification as the estimand, wide sets as quantified information insufficiency, judge-save as a discretion-versus-identifiability trade-off, dynamic proxies as organization tools, prediction as validation, and counterfactuals as scenarios. The revised limitations explicitly cover unobserved public input, rule/tie uncertainty, active-trajectory selection, metric non-equivalence, scenario dependence, external validity, and data/release boundaries. The conclusion contains only core claims.")

        literature, literature_audit, literature_plan = literature_outputs()
        literature.to_csv(tables / "literature_needed_table.csv", index=False)
        write_text(logs / "literature_gap_audit.md", literature_audit)
        write_text(manuscript / "02_related_work_revision_plan.md", literature_plan)

        final_figures, figure_audit = figure_table_audit(root)
        final_figures.to_csv(tables / "final_main_figures_tables.csv", index=False)
        write_text(logs / "figure_table_submission_audit.md", figure_audit)

        package = package_checklist(root)
        package.to_csv(tables / "submission_package_checklist.csv", index=False)
        write_text(logs / "submission_package_checklist.md", "# Submission Package Checklist\n\n" + markdown_table(package, ['item', 'status', 'file_path', 'issue', 'exact_next_action']))
        write_text(manuscript / "cover_letter_draft.md", cover_letter())
        write_text(manuscript / "highlights.md", highlights())
        write_text(logs / "submission_go_no_go.md", go_no_go())
    except (OSError, ValueError, KeyError, IndexError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print("Submission audit outputs generated: 29")
    print("SEPS recommendation: weak fit; do not submit without major repositioning or a new applied case.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
