#!/usr/bin/env python3
"""Create a source-bounded venue review and high-tier research-upgrade plan.

This planning stage does not execute new experiments, alter frozen results, or
overwrite the general, SEPS, or Decision Analysis submission materials. It
records only venue facts verified on official pages during this stage and
labels inaccessible metrics or scope statements as manual verification needed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ACCESS_DATE = "2026-07-16"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a high-tier venue screen and a non-executing innovation "
            "upgrade plan from the existing reproducible research package."
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
        raise FileNotFoundError("Required planning inputs are missing: " + "; ".join(missing))


def venue_matrix() -> pd.DataFrame:
    """Return only metrics and scope statements observed on official pages."""
    rows = [
        (
            "Proceedings of the ACM on Human-Computer Interaction (PACMHCI) / CSCW route",
            "Association for Computing Machinery",
            "journal with conference-journal routes",
            "https://dl.acm.org/journal/pacmhci",
            "official page browser-verified",
            "manual verification needed",
            "The observed official page announces Emerging Sources Citation Index coverage but did not display a current Journal Impact Factor.",
            "manual verification needed",
            "No JCR quartile was displayed on the observed official page.",
            "manual verification needed",
            "No SJR or CiteScore value was displayed on the observed official page.",
            "PACMHCI states that it covers human factors and computing systems, including individual, group, and societal effects of computer mediation; it welcomes systems, user-experience studies, methodologies, tools, theories, and models.",
            "conditional only after a materially different social-computing contribution",
            "yes, substantially: platform governance, accountability practice, and social-computing evidence must be central",
            "no",
            "yes: external testbed plus HCI/social-computing research framing and evaluation",
            "no",
            "Module 4 plus Module 6, with an HCI/social-computing framing and a defensible account of stakeholder use or governance",
            "A methods paper on one competition record may be judged outside HCI contribution expectations.",
            3,
            "stretch target",
        ),
        (
            "Scientific Reports",
            "Springer Nature, Nature Portfolio",
            "open-access multidisciplinary journal",
            "https://www.nature.com/srep/",
            "official page browser-verified",
            "4.9 (2025)",
            "Official journal homepage states: 2-year impact factor 4.9 (2025), citing the 2025 Journal Citation Reports Science Edition.",
            "manual verification needed",
            "A JCR quartile was not displayed on the observed official page; do not infer one from the impact factor.",
            "manual verification needed",
            "No SJR or CiteScore value was recorded from the observed official page.",
            "The official page describes an open-access Nature Portfolio journal publishing research from natural sciences, psychology, medicine, and engineering, including mathematics and computing and engineering subjects.",
            "conditional fit after a general computational-method and validation upgrade",
            "no",
            "no",
            "yes: synthetic ground truth, baselines, robustness, and cross-regime analysis must be central",
            "no",
            "Module 2, Module 3 as a clearly labeled information scenario, Module 4, and Module 5; Module 6 materially improves credibility",
            "Without synthetic coverage evidence and broader validation, the contribution may appear as one domain-specific method application.",
            1,
            "conditional primary target",
        ),
        (
            "International Journal of Human-Computer Interaction",
            "Taylor & Francis",
            "peer-reviewed journal",
            "https://www.tandfonline.com/journals/hihc20/about-this-journal",
            "official page browser-verified",
            "4.9 (2024)",
            "Official journal metrics page.",
            "Q1 (Impact Factor Best Quartile, 2024)",
            "Official journal metrics page; this is an IF best-quartile label and must not be relabeled as a Chinese Academy of Sciences partition.",
            "SJR 1.175 (2024); CiteScore 8.7 (2024), CiteScore Best Quartile Q1",
            "Official journal metrics page.",
            "The official page emphasizes cognitive, creative, social, health, and ergonomic aspects of interactive computing, including social media, online communities, accessibility, empirical studies, and HCI theories/applications.",
            "weak for the current manuscript; the metric target is met but the contribution target is not",
            "yes, substantially",
            "no",
            "yes: the paper would need a genuine HCI contribution, not only a relabeled institutional method",
            "no",
            "Module 5 plus user-, practitioner-, or platform-governance evidence beyond the current data; Module 6 alone is insufficient unless it supports an HCI question",
            "The current study lacks interactive-system design, user experience, or empirical HCI evidence.",
            6,
            "not recommended for the current research design",
        ),
        (
            "IEEE Transactions on Computational Social Systems",
            "Institute of Electrical and Electronics Engineers",
            "peer-reviewed transactions journal",
            "https://ieee-cis.org/pubs/transactions-on-computational-social-systems",
            "official page attempted; scope text unavailable in current browser session",
            "manual verification needed",
            "The IEEE Computational Intelligence Society page timed out; no current metric is entered.",
            "manual verification needed",
            "No publicly verified JCR quartile was captured in this stage.",
            "manual verification needed",
            "No publicly verified SJR or CiteScore was captured in this stage.",
            "Manual verification needed: the official scope page was inaccessible in this environment, so no scope language is inferred here.",
            "manual verification needed",
            "likely, but scope must be verified before any route decision",
            "no",
            "yes: computational-social-systems framing and stronger general validation would be needed",
            "no",
            "Module 2 and Module 4 at minimum, followed by scope verification and a match to a confirmed special issue or topic area",
            "Scope, metrics, and fit are not sufficiently verified; submission would be premature.",
            5,
            "hold pending official scope verification",
        ),
        (
            "Decision Support Systems",
            "Elsevier",
            "peer-reviewed journal",
            "https://www.sciencedirect.com/journal/decision-support-systems",
            "official journal endpoint blocked by browser policy; prior direct endpoint check was protected",
            "manual verification needed",
            "No current impact factor is entered because the official journal page was not accessible.",
            "manual verification needed",
            "No publicly verified JCR quartile was captured in this stage.",
            "manual verification needed",
            "No publicly verified SJR or CiteScore was captured in this stage.",
            "Manual verification needed: do not rely on an inferred scope summary while the official journal page is inaccessible.",
            "not sufficient in current form",
            "no",
            "yes, substantially: a decision-support artifact, selection workflow, and stakeholder or organizational evaluation are needed",
            "yes, substantially",
            "no",
            "Module 3 and Module 5 must become an implemented and evaluated decision-support workflow; Module 4 and Module 6 supply methodological and empirical support",
            "The current project has no implemented or evaluated decision-support system, organizational deployment, or IS theory contribution.",
            7,
            "stretch only after a research-design expansion",
        ),
        (
            "Social Network Analysis and Mining",
            "Springer Nature",
            "open-access journal",
            "https://link.springer.com/journal/13278",
            "official page browser-verified",
            "3.2 (2025)",
            "Official Springer journal metrics page.",
            "manual verification needed",
            "The observed official page did not display a JCR quartile.",
            "manual verification needed",
            "The observed official page did not display SJR or CiteScore values.",
            "The official page describes a multidisciplinary journal for theoretical and experimental work in social network analysis and mining, integrating techniques across network science and related fields.",
            "weak unless a network object becomes central",
            "no",
            "no",
            "yes: network-aware data/model contribution would be necessary",
            "no",
            "Module 6 using a genuine public interaction network, plus a network-specific research question; the current panel is not a social-network analysis study",
            "The existing data and method do not model a social network or network-mining problem.",
            8,
            "not recommended for the current research design",
        ),
        (
            "Group Decision and Negotiation",
            "Springer Nature, in cooperation with the INFORMS Section on Group Decision and Negotiation",
            "peer-reviewed journal",
            "https://link.springer.com/journal/10726",
            "official page browser-verified",
            "2.8 (2025)",
            "Official Springer journal metrics page.",
            "manual verification needed",
            "The observed official page did not display a JCR quartile.",
            "CiteScore 6.0 (2025)",
            "Official Springer journal update; SJR was not displayed.",
            "The official page states that the journal explores descriptive, normative, and design perspectives on group decision-making and negotiation, including applications, case studies, software, and computer-supported collaborative work.",
            "stronger scope fit than high-tier metric fit",
            "no",
            "moderate",
            "moderate: social-choice/group-decision theory and a broader empirical bridge would strengthen it",
            "conditionally yes after focused manuscript revision",
            "Module 1, Module 2, and Module 5 improve the current line; Module 4 is recommended for rigor",
            "The paper does not study negotiation and has one domain-specific testbed.",
            4,
            "fallback target below the requested IF range",
        ),
        (
            "EPJ Data Science",
            "Springer Nature / EPJ",
            "open-access journal",
            "https://link.springer.com/journal/13688",
            "official page browser-verified",
            "3.1 (2025)",
            "Official Springer journal metrics page.",
            "manual verification needed",
            "The observed official page did not display a JCR quartile.",
            "manual verification needed",
            "The observed official page did not display SJR or CiteScore values.",
            "The official page focuses on new scientific methods for analyzing and synthesizing massive data sets, complex systems, and digital traces of human behavior to generate insights into societal phenomena.",
            "conditional fit after a data-science method and validation upgrade",
            "moderate: a computational-social-systems motivation helps but does not need HCI evidence",
            "no",
            "yes: synthetic coverage, rule robustness, and broader evidence are needed",
            "no",
            "Module 2 and Module 4 are essential; Module 3 and Module 6 strengthen the data-science and societal-systems contribution",
            "The current data scale and one-testbed design may appear too narrow without strong method validation and a second setting.",
            2,
            "conditional secondary target",
        ),
    ]
    columns = [
        "official_name", "publisher_or_society", "venue_type", "official_scope_url", "official_verification_status",
        "latest_impact_factor", "impact_factor_source", "JCR_quartile", "JCR_quartile_source",
        "SJR_or_CiteScore", "SJR_or_CiteScore_source", "aims_and_scope_summary",
        "fit_for_hidden_preference_expert_crowd_partial_identification", "requires_HCI_or_social_computing_framing",
        "requires_decision_support_system_framing", "requires_stronger_computational_method_contribution",
        "current_manuscript_sufficient", "required_new_innovation_modules", "desk_reject_risk", "final_rank", "target_status",
    ]
    return pd.DataFrame(rows, columns=columns)


def venue_scope_audit(matrix: pd.DataFrame) -> str:
    return f"""
# High-Tier Venue Scope Audit

## Evidence standard

- Access date: `{ACCESS_DATE}`.
- Venue names, publisher/society, scope summaries, and metrics were recorded only when visible on an official publisher, society, or journal page in this stage.
- A blocked or timed-out official endpoint is recorded as `manual verification needed`; no cached impact factor, JCR quartile, SJR, CiteScore, or scope claim is substituted.
- JCR Q1, SJR/CiteScore Q1, and Chinese Academy of Sciences partitions are distinct classifications. No Chinese Academy of Sciences partition is asserted in this audit.

## Official source record

- PACMHCI: <https://dl.acm.org/journal/pacmhci>. The observed page describes scope and announces ESCI coverage; it did not display a current JIF or quartile.
- Scientific Reports: <https://www.nature.com/srep/>. The observed page reports a 2-year JIF of 4.9 for 2025.
- International Journal of Human-Computer Interaction: <https://www.tandfonline.com/journals/hihc20/about-this-journal>. The observed metrics panel reports IF 4.9 (2024), IF best quartile Q1, CiteScore 8.7 (2024), CiteScore best quartile Q1, and SJR 1.175 (2024).
- IEEE Transactions on Computational Social Systems: <https://ieee-cis.org/pubs/transactions-on-computational-social-systems>. The official society page timed out; the IEEE Xplore issue endpoint did not expose scope or metric text in the captured page state.
- Decision Support Systems: <https://www.sciencedirect.com/journal/decision-support-systems>. The official journal endpoint was blocked by the browser policy in this stage; no metric or scope was inferred.
- Social Network Analysis and Mining: <https://link.springer.com/journal/13278>. The observed page reports JIF 3.2 (2025) and its network-analysis scope.
- Group Decision and Negotiation: <https://link.springer.com/journal/10726>. The observed page reports JIF 2.8 (2025); a journal update reports CiteScore 6.0 (2025).
- EPJ Data Science: <https://link.springer.com/journal/13688>. The observed page reports JIF 3.1 (2025) and its data-science scope.

## Implication for the requested target profile

On this evidence, International Journal of Human-Computer Interaction is the only screened venue with an official public 3-5 IF and an explicit official Q1 label, but the current manuscript lacks the HCI evidence it requires. Scientific Reports has an official 4.9 JIF but no JCR quartile was verified here. EPJ Data Science and Social Network Analysis and Mining have official 3-5 JIF values but no public JCR quartile captured in this stage. These facts do not justify a claim that any of them meets a Chinese Academy of Sciences partition requirement.

## Matrix

{markdown_table(matrix, list(matrix.columns))}
"""


def target_decision() -> str:
    return """
# High-Tier Target-Journal Decision

## Decision

**Primary target, conditional:** *Scientific Reports*, but only after a substantial validation upgrade centered on a synthetic ground-truth benchmark, rule-robustness analysis, and a transparent accountability layer. Its official page reports a 2025 JIF of 4.9. Its JCR quartile was not verified in this stage, so it must not be described as a confirmed Q1 target.

**Secondary target, conditional:** *EPJ Data Science*, after the same synthetic and robustness work, with a stronger emphasis on general computational method, reproducibility, and a second setting where feasible. Its official page reports a 2025 JIF of 3.1; its JCR quartile remains manual verification needed.

**Stretch target:** the PACMHCI / CSCW route. It is not a relabeling exercise. A credible submission would require a social-computing research contribution about platform governance or accountability, an external testbed, and evidence appropriate to HCI. The current paper is not sufficient.

**Fallback target:** *Group Decision and Negotiation*. It has the clearest current topical connection to aggregation and discretion but its official 2025 JIF is 2.8, below the requested approximate range. It is a pragmatic fallback after a narrower group-decision revision, not the high-tier outcome.

## Venues Not Recommended in the Current Form

- *International Journal of Human-Computer Interaction*: its public 4.9 IF and Q1 label meet the metric screen, but the project has no interactive-system, user-experience, or HCI evidence.
- *IEEE Transactions on Computational Social Systems*: hold until the official scope and metrics can be verified; even then the manuscript needs broader computational-social-systems evidence.
- *Decision Support Systems*: the work lacks a decision-support artifact, stakeholder or organizational evaluation, and IS theory contribution.
- *Social Network Analysis and Mining*: the project does not contain a network object, network method, or social-network research question.

## Why Decision Analysis Is Downgraded

*Decision Analysis* remains a strong topical fit for the existing partially identified aggregation framework, but it is no longer the primary route because the user has changed the target criterion to a higher-tier or approximately 3-5 IF venue. The completed DA package is preserved as a fallback; this decision does not diminish its topical suitability.

## Required Manuscript Identity by Route

| Route | Required identity | Minimum upgrade condition |
| --- | --- | --- |
| Scientific Reports | General computational-method paper on inference under coarse institutional feedback | Synthetic ground truth, baseline comparisons, robustness, and reproducible artifacts |
| EPJ Data Science | Data-science method for complex systems and digital-trace inference | Synthetic ground truth, rule robustness, data-method framing, and preferably a second testbed |
| PACMHCI / CSCW | Social-computing/accountability study of platform governance | External setting plus HCI-relevant evidence and a stakeholder/accountability question |
| Decision Support Systems | Evaluated decision-support system for rule/disclosure choice | Implemented workflow, decision task, and organizational or stakeholder evaluation |
| Group Decision and Negotiation | Group-decision mechanism and discretion analysis | Stronger social-choice/group-decision bridge and transparent limits |
"""


def target_decision_audit() -> str:
    return """
# High-Tier Target Decision Audit

- Primary and secondary routes are explicitly conditional on new validation work; no venue is represented as currently ready.
- The decision differentiates scope fit from metric fit. International Journal of Human-Computer Interaction meets the observed public metric screen but not the present contribution screen.
- Scientific Reports is selected conditionally because its official page reports a 2025 JIF of 4.9 and its broad scope can accommodate a validated general method; JCR Q1 status is not asserted.
- Decision Analysis is downgraded because of the changed target criterion, not because the existing DA framing is invalid.
- Decision Support Systems is not selected merely from title overlap: the missing artifact and evaluation are made explicit.
"""


def gap_matrix() -> pd.DataFrame:
    rows = [
        ("Target-venue fit", "critical", "Current work is a reproducible, one-testbed partial-identification study; high-tier route identity is not yet established.", "Desk rejection for mismatch or domain-specific framing.", "Choose one conditional route and build only its minimum evidence package.", "high", "Scientific Reports, EPJ Data Science, PACMHCI/CSCW, DSS"),
        ("Theoretical contribution", "major", "Cardinal/ordinal identification and weak-set containment are clear, but the institutional design objective is not formalized.", "Viewed as a careful application rather than a general contribution.", "Add propositions, disclosure monotonicity, and a scope-bounded decision objective.", "medium", "Scientific Reports, EPJ Data Science, GDN"),
        ("Methodological novelty", "critical", "Existing method is rule-aware partial identification with LP and ranking enumeration.", "Novelty may appear incremental without a general benchmark or robustness index.", "Implement Modules 1-4; pre-register comparison metrics and baselines.", "high", "Scientific Reports, EPJ Data Science, IEEE TCSS"),
        ("Empirical generalizability", "critical", "One longitudinal empirical setting with rule changes is available.", "Single-testbed concern limits general method claims.", "Add Module 6 or restrict claims to the demonstrated setting.", "high", "PACMHCI/CSCW, EPJ Data Science, Scientific Reports"),
        ("External validation", "critical", "No second public testbed or externally observed collective-preference ground truth.", "Claims may not transfer beyond the testbed.", "Add a permission-compatible external replication or state a narrower scope.", "high", "PACMHCI/CSCW, EPJ Data Science, Scientific Reports"),
        ("Synthetic validation", "critical", "No known-truth data-generating benchmark currently tests coverage and sharpness.", "Cannot show that the method behaves correctly when latent preferences are known.", "Implement Module 4 with reproducible regimes, coverage, sharpness, and baseline tests.", "high", "Scientific Reports, EPJ Data Science, IEEE TCSS"),
        ("Baseline comparison", "major", "Prediction and simple risk baselines exist, but no systematic point-estimation or rule-agnostic inference benchmark exists.", "Method advantage remains hard to interpret.", "Compare rule-aware feasible sets with rule-agnostic, midpoint/point-selection, and prediction-only baselines in synthetic data.", "medium", "Scientific Reports, EPJ Data Science"),
        ("Robustness and sensitivity", "moderate", "Tie-policy and sampling diagnostics exist; cross-rule conclusion stability is not summarized.", "A reviewer may see results as specific to one encoding choice.", "Implement the Rule Robustness Index and disclosure sensitivity plan.", "medium", "All routes"),
        ("Reproducibility package", "moderate", "Scripts, processed data, hashes, fixed seeds, and tests exist; archive, licence, and environment lock are incomplete.", "Replication and data-policy concerns.", "Create a release archive, licence, environment lock/container, and controlled-access note.", "medium", "All routes"),
        ("Literature coverage", "major", "Twelve verified source-map rows support the present manuscript but venue-specific literature remains thin.", "Claims may not be positioned against the target audience.", "Complete a venue-specific full-text literature review after route selection.", "medium", "All routes"),
        ("Ethical/accountability framing", "moderate", "The manuscript discusses interpretability but lacks a structured reporting-cost and accountability analysis.", "HCI and decision-support claims can appear aspirational.", "Implement Module 5 and retain limits on normative recommendations.", "low-medium", "PACMHCI/CSCW, DSS, GDN"),
        ("Overclaiming risk", "minor", "Existing audits exclude point-recovery and causal language and separate cardinal from ordinal quantities.", "New innovation language could accidentally exceed evidence.", "Extend claim audits to every new module and distinguish proof, simulation, and empirical findings.", "low", "All routes"),
        ("Figure/table clarity", "moderate", "Existing figures document bounds and judge-save expansion but do not present a unified decision-design story.", "Readers may not see the practical consequence of uncertainty.", "Create frontier, disclosure-value, synthetic-calibration, and accountability displays with regime-specific captions.", "medium", "Scientific Reports, EPJ Data Science, PACMHCI/CSCW"),
        ("Anonymous submission readiness", "moderate", "Package sources and placeholder declarations exist, but no final formatted PDF or source-term confirmation exists.", "Upload failure or identity leakage.", "Complete declarations, typeset route-specific PDF, and perform a final anonymity review.", "medium", "All journal routes"),
    ]
    return pd.DataFrame(rows, columns=["dimension", "severity", "current_evidence", "risk_if_unfixed", "required_fix", "estimated_effort", "target_venue_relevance"])


def gap_audit(gaps: pd.DataFrame) -> str:
    counts = gaps["severity"].value_counts().to_dict()
    return f"""
# Current Work Gap Audit

## Overall assessment

The existing project is strong on reproducible rule encoding, identification boundaries, and claim restraint. It is not yet a high-tier general-method submission because its strongest gaps are synthetic ground-truth validation, broader empirical generalizability, and route-specific contribution identity. These are research-design gaps, not editorial polish issues.

## Severity summary

- Critical: `{counts.get('critical', 0)}` dimensions.
- Major: `{counts.get('major', 0)}` dimensions.
- Moderate: `{counts.get('moderate', 0)}` dimensions.
- Minor: `{counts.get('minor', 0)}` dimensions.

## Gap Matrix

{markdown_table(gaps, list(gaps.columns))}

## Sequencing judgment

Do not add every proposed module at once. The minimum high-tier scientific-method package is Module 4 (known-truth synthetic validation), Module 2 (rule robustness), and a revised claim/evidence audit. Module 6 is the threshold upgrade for broader generalizability. PACMHCI/CSCW and DSS require a more fundamental change of research identity than these modules alone provide.
"""


def innovation_modules() -> pd.DataFrame:
    rows = [
        (
            "M1", "Discretion-Identifiability Frontier", "high",
            "How does a parameterized family of expert-intervention rules change the size and type of the feasible preference set?",
            "Moves one judge-save comparison into a rule-family frontier that separates flexibility from information loss.",
            "Existing R_plus rule records; optional synthetic regimes for a controlled discretion parameter.",
            "Generalize ranking constraints to a documented intervention-relaxation parameter; compute nested feasible sets, ratios, and frontier summaries.",
            "Frontier figure; proposition on set expansion under rule relaxation; within-regime table.",
            "A principled account of discretion as a mechanism-induced information design choice.",
            "GDN; Scientific Reports; EPJ Data Science; DSS if embedded in a tool.",
            "A single observed judge-save rule does not identify an empirical continuum; unobserved frontier points must be labeled as rule scenarios.",
            "yes", "Module 4 strengthens generality; empirical rule coding must remain documented.",
        ),
        (
            "M2", "Rule Robustness Index", "highest",
            "Which substantive conclusions remain invariant across documented aggregation rules, tie handling, and uncertainty assumptions?",
            "Defines conclusion stability across admissible modeling choices rather than pooling incomparable cardinal and ordinal widths.",
            "Existing processed data and rule variants; synthetic data for stress tests.",
            "Implement a pre-specified configuration grid, conclusion predicates, and an index equal to the share of admissible configurations preserving each predicate; report regime-specific components.",
            "Robustness heatmap; rule-aware versus rule-agnostic baseline table; sensitivity appendix.",
            "Makes robustness an explicit scientific object and prevents cherry-picking one rule encoding.",
            "Scientific Reports; EPJ Data Science; IEEE TCSS; GDN.",
            "The index is meaningful only after conclusions, configuration set, and aggregation of predicates are pre-specified.",
            "yes", "Requires careful design; do not treat raw P/R/R_plus width averages as a common metric.",
        ),
        (
            "M3", "Value of Institutional Disclosure", "high",
            "How much would alternative, explicitly modeled disclosure policies reduce feasible-set uncertainty?",
            "Turns partial identification into an information-design analysis with a monotonicity proposition and reporting-cost discussion.",
            "Existing rule records plus simulated or hypothetical disclosure fields; no new proprietary data.",
            "Add constraints for elimination only; elimination plus judge ranking; top-k collective rank; vote-bin intervals; pairwise majority; and margin intervals. Compute set shrinkage within comparable regime/state spaces.",
            "Disclosure ladder figure; shrinkage table; formal proposition; accountability-cost table.",
            "Links transparency choices to measurable information value without claiming the additional disclosures were historically observed.",
            "DSS; GDN; Scientific Reports; PACMHCI/CSCW when tied to platform governance.",
            "For the current data, added disclosure is a scenario, not an empirical observation. Cost and privacy claims require separate evidence.",
            "yes", "Strongest when paired with synthetic ground truth and explicit disclosure assumptions.",
        ),
        (
            "M4", "Synthetic Ground-Truth Benchmark", "highest",
            "When hidden preferences are known in simulation, do rule-aware feasible sets cover them and improve sharpness over naive alternatives?",
            "Supplies known-truth coverage, sharpness, failure modes, and baseline comparisons that the observational testbed cannot provide.",
            "No external data required: simulated latent preferences, judge signals, tie processes, rule regimes, and coarse outcomes.",
            "Build a fixed-seed simulator; implement P, R, R_plus, disclosure variants, and misspecification scenarios; compare coverage, width/sharpness, computational cost, point-selection, prediction-only, and rule-agnostic baselines.",
            "Coverage-versus-sharpness figure; calibration table; misspecification stress test; reproducibility appendix.",
            "Establishes method validity under controlled truth while preserving the observational study as an empirical testbed.",
            "Scientific Reports; EPJ Data Science; IEEE TCSS; PACMHCI/CSCW as supporting evidence.",
            "Simulation cannot establish external realism; data-generating choices and baselines must be transparent and not tuned to favor the method.",
            "yes", "Minimum new research module for a credible high-tier method route.",
        ),
        (
            "M5", "Decision-Support and Accountability Layer", "medium",
            "How can feasible-set outputs guide reporting, discretion, transparency, and interpretability choices without claiming a universally optimal rule?",
            "Converts identified uncertainty into a structured design aid that makes recommendations conditional on declared objectives and reporting costs.",
            "Existing outputs; metadata on assumed reporting burden; no proprietary data required for the initial analytic table.",
            "Create a decision matrix linking rule/disclosure scenario to transparency, discretion, stability, interpretability, reporting cost, and unresolved uncertainty; optionally expose as a lightweight reproducible report rather than a deployment claim.",
            "Accountability matrix; design checklist; scenario decision table.",
            "Clarifies theory-practice relevance while retaining the non-causal, non-optimality boundary.",
            "DSS; PACMHCI/CSCW; GDN; Scientific Reports.",
            "Without stakeholder research it is a normative framework, not evidence of usability or organizational benefit.",
            "yes", "Must distinguish normative criteria from empirical findings.",
        ),
        (
            "M6", "External Testbed Replication", "highest but optional",
            "Do the rule-aware identification findings and robustness conclusions replicate in another public aggregation setting with documented rules?",
            "Tests transportability and exposes rule-dependent variation beyond one longitudinal record.",
            "A public, permission-compatible dataset with documented aggregation rules, outcomes, and adequate expert/collective observables.",
            "Add an adapter-based ingestion and rule-specification layer; rerun audit, preprocessing, constraints, identification, and reporting; compare only shared, well-defined summaries.",
            "Cross-testbed table; replicated mechanism figures; data-provenance appendix.",
            "Materially improves external validity and makes broad methodological claims more defensible.",
            "Scientific Reports; EPJ Data Science; PACMHCI/CSCW; IEEE TCSS.",
            "Public availability, terms, rule documentation, and comparability may fail; do not claim replication before source audit passes.",
            "yes, subject to source terms", "Do not select a dataset merely because it is convenient; predefine inclusion criteria and provenance checks.",
        ),
    ]
    columns = [
        "module_id", "module", "priority", "research_question", "novelty_claim", "required_data", "required_code_changes",
        "expected_figures_tables", "expected_contribution", "target_venue_fit", "risk", "can_be_done_without_new_proprietary_data", "dependencies_and_boundary",
    ]
    return pd.DataFrame(rows, columns=columns)


def innovation_plan(modules: pd.DataFrame) -> str:
    return f"""
# Innovation Upgrade Plan

## Status and decision rule

All modules below are proposed research work. They are not implemented results, and no claim in the existing paper should be changed until the responsible code, tests, tables, figures, and audits have been generated. The high-tier route should begin with M4 and M2. M1 and M3 then build a coherent institutional-information story. M5 improves translation, while M6 is the primary generalizability upgrade.

## Design principles

1. Keep P cardinal and R/R_plus ordinal. Compare them only through a declared common functional or through qualitative, regime-specific conclusions.
2. Treat modeled disclosure and intervention variants as scenarios unless they were observed in the data.
3. Separate theorem, synthetic result, and empirical result in every caption and claim.
4. Fix random seeds, save configurations, and add focused tests before treating any module as evidence.
5. Benchmark against rule-agnostic, point-selection, and prediction-only alternatives without treating any baseline as a measurement of hidden collective preference.

## Module Table

{markdown_table(modules, list(modules.columns))}

## Minimum viable high-tier method package

- M4: Synthetic Ground-Truth Benchmark.
- M2: Rule Robustness Index.
- A revised claim/evidence audit and an archival reproducibility package.

For *Scientific Reports*, add M1 or M3 and M5. For *EPJ Data Science*, add M3 and strongly prefer M6. PACMHCI/CSCW requires M6 plus a new HCI/social-computing research question, not only these method modules. DSS requires a real decision-support artifact and evaluation beyond M5's analytic table.
"""


def formal_claims() -> pd.DataFrame:
    rows = [
        (
            "P1", "Additional disclosure weakly shrinks feasible preference sets",
            "If added disclosure is truthful and imposes additional constraints on the same latent state space, the feasible set under the richer disclosure is a subset of, or equal to, the feasible set under coarse disclosure.",
            "Every state consistent with the richer record must also be consistent with the coarser record; additional information can rule states out but cannot create compatibility.",
            "Same rule, latent state space, and outcome; added disclosure is correctly encoded and logically conjunctive; no measurement error or contradictory record.",
            "Write the coarse feasible set as states satisfying base constraints and the rich set as base constraints plus disclosure constraints. Set intersection yields containment.",
            "Methods disclosure extension and Appendix proof.",
            "No for proof; yes for numerical shrinkage illustrations.",
        ),
        (
            "P2", "Rule-aware constraints are tighter than rule-agnostic constraints",
            "When the rule-aware constraint set contains every valid rule-agnostic constraint and adds only correct rule-specific constraints, its feasible set is a subset of, or equal to, the rule-agnostic feasible set.",
            "Encoding known institutional detail removes states that a generic outcome-only representation cannot exclude.",
            "Rule-specific constraints are correctly derived; the rule-agnostic model is nested rather than differently misspecified; both use the same latent space.",
            "Compare intersections of the same base state space with a subset and its superset of constraints.",
            "Methods and synthetic benchmark appendix.",
            "No for proof; yes for benchmark magnitude and misspecification checks.",
        ),
        (
            "P3", "Expert-discretion relaxation can expand identifiability uncertainty",
            "If a discretionary rule weakens a direct elimination condition to a logically weaker tie-inclusive bottom-set condition, every direct-feasible state is discretion-feasible; strict expansion occurs whenever an additional state satisfies only the weaker condition.",
            "A relaxation preserves prior compatibility and may admit further hidden rankings.",
            "Same active set and scoring rule; weak condition is a logical relaxation; tie policy is fixed and documented.",
            "Show that direct feasibility implies weak feasibility, then give the strict-expansion condition as existence of a weak-only state.",
            "Methods, results, and Appendix proof; M1 frontier section.",
            "No for containment proof; yes for empirical frequency and frontier estimation.",
        ),
        (
            "P4", "Ordinal and cardinal uncertainty require a common functional for comparison",
            "Raw cardinal interval width and ordinal rank-support width do not define an ordered common uncertainty scale unless an explicit common uncertainty functional and its interpretation are specified.",
            "The objects live on different state spaces and units; a larger number in one representation need not mean more information loss than a smaller number in another.",
            "No fixed, justified mapping from rank configurations to cardinal support vectors has been imposed; regime samples and active-set sizes may differ.",
            "Construct representations with equal reported widths under arbitrary rescaling or rank relabeling but different information content; comparison is undefined without a declared map.",
            "Methods comparability note and Figure 4 caption; M2 design.",
            "No for the conceptual statement; yes if proposing a new common functional.",
        ),
        (
            "P5", "Prediction cannot identify hidden preferences from coarse outcomes alone",
            "Predictive performance for observed institutional outcomes cannot identify hidden preferences unless additional assumptions make the mapping from hidden preferences to the observable distribution injective.",
            "Distinct hidden states can produce the same elimination outcome or the same predictive distribution after aggregation and coarse observation.",
            "Coarse feedback; no observation of the hidden collective input; no independently justified injectivity condition.",
            "Exhibit multiple latent states in a feasible set that imply the same observed outcome; a predictor can be accurate over that outcome without distinguishing them.",
            "Validation section and Appendix proof sketch.",
            "No for non-identification proof; yes for consistency checks against observed outcomes.",
        ),
    ]
    columns = ["proposition_id", "proposition", "statement", "intuition", "assumptions", "proof_sketch", "where_to_insert", "empirical_verification_needed"]
    return pd.DataFrame(rows, columns=columns)


def theory_upgrade_notes(propositions: pd.DataFrame) -> str:
    blocks = []
    for row in propositions.itertuples(index=False):
        blocks.append(
            f"## {row.proposition_id}. {row.proposition}\n\n"
            f"**Statement.** {row.statement}\n\n"
            f"**Intuition.** {row.intuition}\n\n"
            f"**Assumptions.** {row.assumptions}\n\n"
            f"**Proof sketch.** {row.proof_sketch}\n\n"
            f"**Insertion point.** {row.where_to_insert}\n\n"
            f"**Empirical verification.** {row.empirical_verification_needed}"
        )
    return """# Method and Theory Upgrade Notes

These propositions formalize the boundary conditions of the existing framework and the proposed disclosure/robustness extensions. They should be written with exact notation only after the relevant module defines its state space, tie policy, and constraint map. None should be stated as an empirical universal without its listed assumptions.

""" + "\n\n".join(blocks)


def formal_claims_audit(propositions: pd.DataFrame) -> str:
    return f"""
# Formal Claims Audit

## Audit conclusion

The five proposed claims are appropriate as conditional propositions, not as unconditional empirical assertions. P1-P3 are set-containment statements and require exact nesting assumptions. P4 is a comparability boundary, not an empirical rank ordering. P5 is a non-identification boundary that preserves the existing distinction between prediction and latent-state inference.

## Proposition Register

{markdown_table(propositions, list(propositions.columns))}

## Required implementation discipline

- Define the latent state space and all rule/tie assumptions before formal proof.
- Add unit tests for each set-inclusion claim and counterexamples for violated assumptions.
- Report simulations and empirical examples separately from the proposition.
- Do not use a proposition to assert an unobserved disclosure benefit, welfare gain, or stakeholder outcome.
"""


def version_briefs() -> list[dict[str, object]]:
    return [
        {
            "route": "A. PACMHCI / CSCW version",
            "title": "Accountability under Hidden Preferences: Partial Identification in Expert-Crowd Aggregation Systems",
            "abstract": """Collective decision systems increasingly combine visible expert assessments with hidden participation signals, while platforms disclose only coarse outcomes such as eliminations. This opacity complicates accountability: participants and overseers cannot tell which collective-preference states remain compatible with a decision, or how discretionary intervention changes that uncertainty. This proposed paper develops a rule-aware partial-identification framework for expert-crowd aggregation systems. It represents hidden preferences as feasible sets conditioned on documented aggregation rules, visible expert inputs, active participants, and coarse outcome feedback. Percentage rules yield cardinal feasible intervals; ranking rules yield ordinal feasible rankings; discretionary judge-save rules relax the observed implication and expand compatible states. A high-tier social-computing version would pair the longitudinal empirical testbed with a synthetic ground-truth benchmark, a disclosure-value analysis, and an external public platform setting. These additions would allow the paper to examine how reporting policies and discretion affect accountability and interpretability without claiming access to a direct public-vote measure. The contribution would be a transparent method for platform-governance analysis: it makes the information consequences of rule design auditable and distinguishes observed evidence from unresolved collective preference. The work would not claim user benefit without separate stakeholder evidence.""",
            "keywords": "social computing; platform governance; accountability; partial identification; collective decision systems",
            "required_new_sections": "Platform-governance problem; stakeholder/accountability theory; disclosure scenarios; synthetic validation; external testbed; limitations on stakeholder claims.",
            "sections_to_delete_or_rewrite": "Rewrite the introduction, related work, discussion, and conclusion; demote competition-specific operational detail to methods/appendix.",
            "main_risk": "Without an HCI-relevant empirical contribution or stakeholder evidence, the paper remains a methods study outside the route's core expectations.",
            "go_no_go": "No-Go until Module 4, Module 6, and a defensible HCI/social-computing research question are complete.",
        },
        {
            "route": "B. Scientific Reports version",
            "title": "Rule-Aware Partial Identification of Hidden Preferences in Expert-Crowd Aggregation Systems",
            "abstract": """Many expert-crowd systems release visible expert assessments and final eliminations while leaving collective preferences hidden. Coarse feedback makes point estimation inappropriate because multiple latent preference states can produce the same institutional outcome. This proposed paper develops a rule-aware partial-identification method that converts documented aggregation rules, active sets, expert inputs, and eliminations into feasible preference sets. Percentage aggregation produces cardinal feasible intervals, whereas ranking aggregation produces ordinal feasible rankings. A judge-save condition is modeled as a weaker bottom-set implication, making the information consequence of discretion explicit. The revised study would combine a longitudinal empirical testbed with a fixed-seed synthetic ground-truth benchmark. The benchmark would test coverage of known latent states, feasible-set sharpness, sensitivity to ties and rule misspecification, and comparisons with rule-agnostic, point-selection, and prediction-only baselines. A rule robustness index would summarize which conclusion predicates persist across admissible configurations, while a disclosure analysis would quantify modeled information gain under richer reports. The contribution would be a reproducible computational method for reasoning about uncertainty created by institutional observation rules. It would retain strict separation between cardinal and ordinal objects and would not interpret predictive performance as recovery of hidden collective preferences.""",
            "keywords": "partial identification; aggregation mechanisms; synthetic validation; hidden preferences; computational social systems",
            "required_new_sections": "Synthetic benchmark design; baseline comparison; rule robustness index; disclosure scenarios; reproducibility and misspecification appendix.",
            "sections_to_delete_or_rewrite": "Rewrite abstract, introduction, methods, results, and discussion around general method validation; move target-specific submission material out of the manuscript.",
            "main_risk": "A broad journal may regard a single empirical setting and simulation-only expansion as insufficiently general without a second testbed.",
            "go_no_go": "Conditional Go after Module 4, Module 2, full baseline tests, and route-specific literature review; Module 6 is strongly preferred.",
        },
        {
            "route": "C. Decision Support Systems version",
            "title": "A Decision-Support Framework for Evaluating Aggregation Mechanisms under Hidden Preferences",
            "abstract": """Organizations and platforms often choose aggregation rules without observing all preference inputs that contribute to their decisions. When only coarse outcomes are retained, designers need support for evaluating the uncertainty, transparency, and discretion consequences of candidate rules. This proposed paper would build a decision-support framework around rule-aware partial identification. The framework would translate documented rules, expert components, outcome feedback, and optional disclosure policies into feasible preference representations. It would preserve the distinction between cardinal intervals under percentage aggregation and ordinal rankings under rank aggregation, then use scenario analysis to compare information consequences of direct and discretionary rules. A synthetic benchmark would evaluate coverage, sharpness, robustness to tie handling, and performance against rule-agnostic and prediction-only alternatives. A disclosure module would compare elimination-only reporting with richer reporting scenarios, and an accountability layer would expose trade-offs among interpretability, reporting burden, discretion, and unresolved uncertainty. The empirical record would serve as one testbed rather than proof of organizational value. For a viable decision-support submission, the method must be implemented as an inspectable workflow with documented inputs, outputs, and decision tasks. It must also be evaluated with intended users or realistic organizational cases before any usability or decision-quality claim is made.""",
            "keywords": "decision support; partial identification; institutional design; aggregation mechanisms; disclosure policy",
            "required_new_sections": "Decision task and users; artifact architecture; disclosure/rule selection workflow; synthetic benchmark; evaluation protocol; organizational case or practitioner study.",
            "sections_to_delete_or_rewrite": "Rewrite the entire introduction and discussion as an IS/decision-support contribution; replace generic prediction material with artifact evaluation.",
            "main_risk": "No implemented or evaluated decision-support artifact currently exists, so the route would require a research-design expansion.",
            "go_no_go": "No-Go until Modules 3-5 are implemented as a workflow and evaluated with users or an organizational decision case, supported by Module 4 and preferably Module 6.",
        },
    ]


def reframing_plan() -> str:
    briefs = version_briefs()
    sections = ["# High-Tier Reframing Plan", "", "The three versions are alternative research identities, not cosmetic title changes. Select one only after its stated Go/No-Go condition is met."]
    for brief in briefs:
        count = word_count(str(brief["abstract"]))
        sections.extend(
            [
                "", f"## {brief['route']}", "", f"### Title\n\n{brief['title']}",
                f"### Approximately 200-Word Abstract Draft ({count} words)\n\n{brief['abstract']}",
                f"### Keywords\n\n{brief['keywords']}",
                f"### Required New Sections\n\n{brief['required_new_sections']}",
                f"### Sections to Delete or Rewrite\n\n{brief['sections_to_delete_or_rewrite']}",
                f"### Main Risk\n\n{brief['main_risk']}",
                f"### Go/No-Go\n\n{brief['go_no_go']}",
            ]
        )
    return "\n".join(sections)


def strategy_report(matrix: pd.DataFrame, gaps: pd.DataFrame, modules: pd.DataFrame) -> str:
    return f"""
# High-Tier Upgrade Strategy Report

## Recommendation: E. Pause submission and add external validation

Proceed with a conditional *Scientific Reports* route only after the minimum high-tier method package is complete. The appropriate immediate action is not to submit the current manuscript to a more selective venue; it is to add synthetic ground-truth validation and rule-robustness evidence, then decide whether a permission-compatible external testbed can be added. The existing Decision Analysis package remains preserved as the fastest fallback.

## Answers to the Required Questions

1. **Should Decision Analysis remain the primary target?** No. It remains a strong topical fallback, but the user has changed the target criterion to a higher-tier or approximately 3-5 IF route.
2. **Which screened venues meet the requested Q1 and approximately 3-5 IF profile?** On publicly verified evidence, International Journal of Human-Computer Interaction reports IF 4.9 and an IF best-quartile Q1 label, but it is not a fit for the current research design. Scientific Reports reports IF 4.9, EPJ Data Science 3.1, and Social Network Analysis and Mining 3.2, yet this audit did not verify a JCR Q1 label for them. No Chinese Academy of Sciences partition is asserted.
3. **What is missing from the current paper?** The critical gaps are known-truth synthetic validation, systematic rule-robustness and baseline comparison, stronger external generalizability, and a route-specific contribution identity.
4. **What is the most valuable innovation?** Module 4, the Synthetic Ground-Truth Benchmark. It directly tests coverage and sharpness under known latent preferences and permits fair baseline comparisons.
5. **Highest credible route without new data?** After synthetic work that needs no proprietary data, a conditional Scientific Reports route is the highest plausible screened route; without the synthetic work, retain the existing Decision Analysis or Group Decision and Negotiation fallback rather than overreach.
6. **Highest credible route after a synthetic benchmark?** Scientific Reports is the primary conditional target, provided Module 2 and baseline/misspecification analyses are also completed.
7. **Highest credible route after a second external testbed?** Scientific Reports remains the most coherent general-method route; EPJ Data Science becomes a strong secondary. PACMHCI/CSCW is still a stretch because an external testbed alone does not create an HCI contribution.
8. **Most recommended submission route?** E now, followed by C: pause, implement M4 plus M2, and pursue Scientific Reports only when the resulting evidence passes a renewed audit.
9. **Fastest submission route?** The preserved Decision Analysis package, followed by Group Decision and Negotiation, because neither requires inventing a new research artifact. Neither satisfies the revised metric aspiration on this evidence.
10. **Most prudent route?** Complete M4, M2, M1/M3 as appropriate, and M6 if a suitable public source passes provenance audit; then choose Scientific Reports or EPJ Data Science from generated evidence, not reputation alone.

## Scope Comparison: The Three Requested Routes

| Route | Current status | Minimum evidence gap | Decision |
| --- | --- | --- | --- |
| PACMHCI / CSCW | Not sufficient | HCI/social-computing problem, external setting, and HCI-appropriate evidence | Stretch, not a near-term retitle |
| Scientific Reports | Conditionally promising | Synthetic coverage, baseline comparison, robustness, preferably external replication | Primary after upgrade |
| Decision Support Systems | Not sufficient | Implemented decision-support artifact, decision task, and evaluation | Do not pursue without research-design expansion |

## Implementation Priority

1. M4 Synthetic Ground-Truth Benchmark.
2. M2 Rule Robustness Index.
3. Extend formal propositions and focused tests.
4. M1 Discretion-Identifiability Frontier or M3 Value of Institutional Disclosure, depending on the selected narrative.
5. M5 Accountability Layer.
6. M6 External Testbed Replication after source-provenance screening.

## Evidence Boundaries

- The current 2025/2024 metrics in the venue matrix are source-stamped observations, not permanent rankings.
- JCR, SJR/CiteScore, and Chinese Academy of Sciences classifications are not interchangeable.
- No proposed module is represented as already implemented or as a new empirical result.
- The recommendation follows the gap and venue matrices generated in this stage: {len(gaps)} assessed dimensions, {len(modules)} planned modules, and {len(matrix)} screened venues.
"""


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    require(
        root,
        [
            "data/processed/panel_long.csv",
            "data/processed/week_level.csv",
            "outputs/tables/constraint_summary.csv",
            "outputs/tables/identification_comparison_by_regime.csv",
            "outputs/tables/prediction_results.csv",
            "outputs/tables/frozen_outputs_hashes.csv",
            "outputs/logs/frozen_submission_manifest.md",
            "manuscript/submission_main/01_introduction.md",
        ],
    )
    try:
        tables = root / "outputs/tables"
        logs = root / "outputs/logs"
        manuscript = root / "manuscript"

        venues = venue_matrix()
        gaps = gap_matrix()
        modules = innovation_modules()
        propositions = formal_claims()

        venues.to_csv(tables / "high_tier_venue_fit_matrix.csv", index=False)
        gaps.to_csv(tables / "gap_severity_matrix.csv", index=False)
        modules.to_csv(tables / "new_innovation_modules.csv", index=False)

        write_text(logs / "high_tier_venue_scope_audit.md", venue_scope_audit(venues))
        write_text(manuscript / "high_tier_target_journal_decision.md", target_decision())
        write_text(logs / "high_tier_target_decision_audit.md", target_decision_audit())
        write_text(logs / "current_work_gap_audit.md", gap_audit(gaps))
        write_text(manuscript / "innovation_upgrade_plan.md", innovation_plan(modules))
        write_text(manuscript / "method_theory_upgrade_notes.md", theory_upgrade_notes(propositions))
        write_text(logs / "formal_claims_audit.md", formal_claims_audit(propositions))
        write_text(manuscript / "high_tier_reframing_plan.md", reframing_plan())
        write_text(logs / "high_tier_upgrade_strategy_report.md", strategy_report(venues, gaps, modules))
    except (OSError, ValueError, KeyError, IndexError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("High-tier venue and innovation-upgrade planning completed.")
    print(f"Screened venues: {len(venues)}")
    print(f"Gap dimensions: {len(gaps)}")
    print(f"Innovation modules: {len(modules)}")
    print("Recommendation: E. Pause submission and add external validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
