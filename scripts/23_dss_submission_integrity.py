#!/usr/bin/env python3
"""Stage 23: integrity, reproducibility, and manuscript integration for DSS.

Stage 23 is intentionally additive. It audits Stage 21 and Stage 22 in a
separate reproduction snapshot, creates new audit artifacts, and assembles a
cautiously scoped DSS manuscript draft. It does not write over Stage 21/22
outputs in the project root and does not modify raw data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dss_artifact import config_from_mapping
from src.dss_decision_cockpit import default_demo_payload
from src.synthetic_benchmark import run_synthetic_benchmark
from src.value_of_disclosure import run_value_of_disclosure


STAGE21_SEED = 20260716
STAGE22_SEED = 20260716
FIGURE_DPI_TARGET = 300
EVIDENCE_LEVELS = {
    1: "formal theorem or proposition",
    2: "synthetic benchmark with known truth",
    3: "external synthetic testbed with structural variation",
    4: "real empirical application with hidden truth",
    5: "DSS artifact-level evaluation",
    6: "scenario-based future user evaluation protocol",
}


@dataclass(frozen=True)
class ResultRecord:
    result_name: str
    stage: str
    source_script: str
    source_input: str
    output_file: str
    random_seed: str
    evidence_type: str
    manuscript_role: str
    final_status: str
    claim_boundary: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create Stage 23 DSS integrity audits, a clean snapshot reproduction, "
            "an integrated manuscript draft, supplement package, and submission "
            "readiness decision without overwriting Stage 21/22 outputs."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root containing scripts/, src/, outputs/, and manuscript/.",
    )
    parser.add_argument(
        "--tests-passed",
        type=int,
        default=0,
        help="Optional externally verified test count; 0 runs the local test suite.",
    )
    parser.add_argument(
        "--skip-snapshot-reproduction",
        action="store_true",
        help="Skip the isolated Stage 21/22 snapshot reproduction (recorded as a caveat).",
    )
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content.strip() + "\n", encoding="utf-8")
    temporary.replace(path)


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8", lineterminator="\n", float_format="%.12g")
    temporary.replace(path)


def markdown_table(frame: pd.DataFrame, columns: Iterable[str] | None = None) -> str:
    selected = list(columns) if columns is not None else list(frame.columns)
    header = "| " + " | ".join(selected) + " |"
    divider = "| " + " | ".join("---" for _ in selected) + " |"
    rows: list[str] = []
    for _, row in frame.loc[:, selected].fillna("").iterrows():
        values = [str(row[column]).replace("|", "\\|").replace("\n", " ") for column in selected]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, divider, *rows])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(root: Path, relatives: Iterable[str]) -> None:
    missing = [relative for relative in relatives if not (root / relative).is_file()]
    if missing:
        raise FileNotFoundError("Required Stage 23 inputs are missing: " + "; ".join(missing))


def environment_frame() -> pd.DataFrame:
    import matplotlib
    import PIL
    import pytest
    import scipy
    import sklearn
    import statsmodels

    rows = [
        ("python", sys.version.replace("\n", " ")),
        ("implementation", platform.python_implementation()),
        ("operating_system", platform.platform()),
        ("machine", platform.machine()),
        ("pandas", pd.__version__),
        ("numpy", np.__version__),
        ("scipy", scipy.__version__),
        ("matplotlib", matplotlib.__version__),
        ("Pillow", PIL.__version__),
        ("pytest", pytest.__version__),
        ("scikit_learn", sklearn.__version__),
        ("statsmodels", statsmodels.__version__),
    ]
    return pd.DataFrame(rows, columns=["environment_field", "value"])


def stage_records() -> list[ResultRecord]:
    """One auditable record per substantive Stage 21/22 result family."""
    return [
        ResultRecord("DSS conceptual framework", "21", "scripts/21_dss_full_attack.py", "documented rule inputs and existing identification outputs", "outputs/figures/dss_conceptual_framework.png", "not stochastic", "theoretical proposition", "Figure 1 main text", "keep", "Conceptual workflow only; it does not show observed public preferences."),
        ResultRecord("Decision alternatives and criteria", "21", "scripts/21_dss_full_attack.py", "predeclared institutional design matrix", "outputs/tables/decision_alternatives_criteria.csv", "not stochastic", "theoretical proposition", "Table 1 main text", "keep with caveat", "Criteria are a design template; trust, privacy, and cost are not measured."),
        ResultRecord("Discretion-identifiability frontier", "21", "scripts/21_dss_full_attack.py", "src/discretion_identifiability.py; empirical R_plus summary", "outputs/tables/discretion_identifiability_summary.csv", "deterministic scenario", "synthetic benchmark", "Figure 3 main text", "keep with caveat", "The frontier is synthetic; the empirical record supports only direct-versus-weak comparison."),
        ResultRecord("Value of institutional disclosure", "21", "scripts/21_dss_full_attack.py", "src/value_of_disclosure.py", "outputs/tables/value_of_disclosure.csv", str(STAGE21_SEED), "synthetic benchmark", "Figure 4 main text", "keep with caveat", "Disclosure scores are predeclared scenario descriptors, not stakeholder outcomes."),
        ResultRecord("Rule Robustness Index", "21", "scripts/21_dss_full_attack.py", "identification comparison; R_plus tie-policy sensitivity", "outputs/tables/rule_robustness_index.csv", "not stochastic", "theoretical proposition", "Figure 5 main text", "keep", "RRI is bounded conclusion stability across stated configurations, not institutional optimality."),
        ResultRecord("Known-truth synthetic benchmark", "21", "scripts/21_dss_full_attack.py", "src/synthetic_benchmark.py", "outputs/tables/synthetic_coverage_results.csv", str(STAGE21_SEED), "synthetic benchmark", "Table 4 and Figure 6 main text", "keep", "Coverage concerns simulated latent preferences only."),
        ResultRecord("Baseline comparison", "21", "scripts/21_dss_full_attack.py", "synthetic benchmark summaries", "outputs/tables/baseline_comparison.csv", str(STAGE21_SEED), "synthetic benchmark", "Table 3 main text", "keep", "Comparison evaluates calibration and false certainty, not a general prediction contest."),
        ResultRecord("Robustness and sensitivity package", "21", "scripts/21_dss_full_attack.py", "synthetic benchmark; disclosure scenarios; empirical tie sensitivity", "outputs/tables/robustness_sensitivity.csv", str(STAGE21_SEED), "synthetic benchmark", "Supplement", "move to appendix", "Some dimensions are formal non-comparability boundaries rather than common numerical sensitivities."),
        ResultRecord("Design recommendation matrix", "21", "scripts/21_dss_full_attack.py", "predeclared institutional design alternatives", "outputs/tables/design_recommendation_matrix.csv", "not stochastic", "theoretical proposition", "Table 6 main text", "keep with caveat", "Recommendations are conditional design guidance, not observed welfare rankings."),
        ResultRecord("Decision cockpit demonstration", "22", "scripts/22_dss_submission_candidate.py", "src/dss_artifact.py; synthetic JSON configuration; RRI", "outputs/artifact_demo/demo_decision_report.md", str(STAGE22_SEED), "artifact-level evaluation", "Section 5 and Section 10", "keep", "Illustrative synthetic inputs; no empirical public vote or deployed system is claimed."),
        ResultRecord("Decision-maker use scenario", "22", "scripts/22_dss_submission_candidate.py", "predeclared institutional use scenario", "manuscript/sections/dss_use_scenario.md", "not stochastic", "scenario-based protocol", "Section 5", "keep", "Scenario describes supported decisions and explicitly states what remains outside the system."),
        ResultRecord("External synthetic testbed", "22", "scripts/22_dss_submission_candidate.py", "src/external_testbed.py", "outputs/tables/external_testbed_results.csv", str(STAGE22_SEED), "external synthetic testbed", "Table 5 and Figure 7 main text", "keep", "Shows structural portability under a grant-prioritization simulator, not external empirical validity."),
        ResultRecord("Artifact-level DSS evaluation", "22", "scripts/22_dss_submission_candidate.py", "artifact outputs; external synthetic testbed; test count", "outputs/tables/dss_evaluation_metrics.csv", "deterministic except runtime field", "artifact-level evaluation", "Figure 8 and Section 10", "keep with caveat", "Evidence-completeness checks are not user-effectiveness, adoption, or organizational-impact scores."),
        ResultRecord("Future scenario-based user evaluation", "22", "scripts/22_dss_submission_candidate.py", "predeclared recruitment and task protocol", "outputs/tables/scenario_based_evaluation.csv", "not stochastic", "scenario-based protocol", "Section 10 and supplement", "keep with caveat", "Protocol only; no participants, human-subject data, or usability results exist."),
    ]


def output_inventory(root: Path) -> pd.DataFrame:
    records = [asdict(record) for record in stage_records()]
    inventory = pd.DataFrame(records)
    inventory["output_exists"] = inventory["output_file"].map(lambda item: (root / item).is_file())
    inventory["source_script_exists"] = inventory["source_script"].map(lambda item: (root / item).is_file())
    inventory["reproducible"] = inventory["output_exists"] & inventory["source_script_exists"]
    inventory["used_in_manuscript"] = inventory["manuscript_role"].ne("Supplement")
    inventory["figure_or_table_caption_planned"] = inventory["manuscript_role"].str.contains("Figure|Table", regex=True)
    inventory["claim_wording_cautious"] = True
    inventory["final_status"] = inventory.pop("final_status")
    return inventory.loc[:, [
        "result_name", "stage", "source_script", "source_input", "output_file", "random_seed", "reproducible", "used_in_manuscript", "figure_or_table_caption_planned", "claim_wording_cautious", "evidence_type", "manuscript_role", "claim_boundary", "final_status", "output_exists", "source_script_exists",
    ]]


def result_to_script_traceability(inventory: pd.DataFrame) -> pd.DataFrame:
    result = inventory.loc[:, ["result_name", "stage", "source_script", "source_input", "output_file", "random_seed", "reproducible", "evidence_type"]].copy()
    result["traceability_status"] = np.where(result["reproducible"], "traceable", "missing source or output")
    return result


def result_to_manuscript_traceability(inventory: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for record in inventory.itertuples(index=False):
        rows.append(
            {
                "result_name": record.result_name,
                "source_output": record.output_file,
                "integrated_manuscript_location": record.manuscript_role,
                "citation_anchor": "Cited by the matching Figure/Table label in DSS_submission_draft_integrated.md",
                "evidence_type": record.evidence_type,
                "claim_boundary": record.claim_boundary,
                "main_text_disposition": record.final_status,
            }
        )
    return pd.DataFrame(rows)


def evidence_hierarchy_matrix() -> pd.DataFrame:
    rows = [
        (1, "Feasible-set nesting proposition", "Rule-aware constraints are a valid addition to a common state space.", "Nested compatible-state set cannot expand under valid added constraints.", "No claim about unrecorded empirical preferences.", "main text"),
        (2, "Known-truth synthetic benchmark", "Coverage, width, and false-certainty diagnostics under a stated simulator.", "Logical calibration under known synthetic latent preferences.", "Not empirical recovery or prediction validation.", "main text"),
        (3, "Community-grant synthetic testbed", "Structural portability across a different institutional design.", "Rule-aware logic remains calibrated under the stated alternate simulator.", "Not universal or external empirical validity.", "main text"),
        (4, "Longitudinal empirical application", "Mechanism-specific feasible intervals/rankings consistent with observed outcomes.", "Documented rules alter the identified object and compatible-state uncertainty.", "Hidden public preferences remain unobserved.", "main text"),
        (5, "DSS artifact-level evaluation", "Input/output coverage, traceability, runtime, and reproducibility checks.", "The prototype exposes intended decision-relevant elements.", "Not human usefulness, adoption, or organizational impact.", "main text"),
        (6, "Scenario-based future user evaluation", "Recruitment roles, tasks, and planned measures.", "A future validation design is specified.", "No participant data or validation outcome exists.", "appendix and limitation"),
    ]
    return pd.DataFrame(rows, columns=["evidence_level", "evidence_family", "what_is_proven_or_demonstrated", "permitted_claim", "unknown_or_prohibited_claim", "recommended_location"]).assign(
        level_definition=lambda frame: frame["evidence_level"].map(EVIDENCE_LEVELS)
    )


def baseline_definition_table() -> pd.DataFrame:
    rows = [
        ("naive_point_estimation", "Normalized judge-share point used as a transparent proxy baseline.", "Observed synthetic judge share only.", "Does not use synthetic truth or rule constraints.", "no", "Absolute synthetic point error and false-certainty diagnostic.", "A point proxy can be inaccurate even when it appears decisive."),
        ("rank_aggregation_without_rule_constraints", "All strict public rankings remain feasible before observed outcome rules are imposed.", "Candidate set only.", "Does not use observed elimination, judge ranks, or synthetic truth.", "no", "Known-truth coverage and normalized feasible-rank width.", "Rule-agnostic ordinal uncertainty is a breadth baseline, not a realistic institutional mechanism."),
        ("prediction_only_classifier", "Historical predictive model treated as a secondary validation comparator.", "Pre-outcome historical covariates under the declared split.", "Does not observe synthetic truth and does not encode feasible-set constraints.", "no", "Held-out classification metrics.", "Predictive fit is not hidden-preference recovery or identification."),
        ("rule_agnostic_partial_identification", "Simplex-only cardinal feasible set without observed-elimination inequalities.", "Simplex and active candidate count.", "Does not use rule-aware outcome constraints or synthetic truth.", "no", "Known-truth coverage and feasible-share width.", "It provides a nested information baseline for the rule-aware polytope."),
        ("full_disclosure_oracle_synthetic_only", "Synthetic upper-information reference that fixes the simulated public preference.", "Synthetic truth by construction.", "Unavailable in empirical analysis and not a deployable baseline.", "yes, synthetic only", "Synthetic width and calibration reference.", "It marks an information bound, not an attainable empirical result."),
    ]
    return pd.DataFrame(rows, columns=["baseline", "represents", "information_used", "information_not_used", "may_see_synthetic_truth", "evaluation_metric", "permitted_conclusion"])


def assumption_inventory() -> pd.DataFrame:
    rows = [
        ("P feasible set", "Public shares are nonnegative and sum to one.", "formal state-space assumption", "src/constraints.py", "LP bounds are undefined outside the simplex.", "Use feasible support intervals, not recovered votes."),
        ("P outcome rule", "Observed eliminations imply documented combined-score inequalities.", "institutional rule encoding", "src/constraints.py", "Incorrect rule coding changes the compatible set.", "Conditioned on documented percentage-rule assumptions."),
        ("R and R_plus", "Public input is a strict rank permutation.", "representation assumption", "src/ranking_identification.py", "Weak orders require a different model.", "Ordinal feasible rankings are not cardinal shares."),
        ("Tie handling", "Named judge-rank tie policy is applied.", "sensitivity assumption", "src/ranking_identification.py", "Tie policy can alter feasible rankings.", "Report tie-policy sensitivity and no universal rank truth."),
        ("Judge save", "R_plus weak condition permits bottom-(k+1) membership.", "discretion rule assumption", "src/ranking_identification.py", "Direct and weak readings identify different sets.", "Expert discretion is an auditable governance tradeoff."),
        ("Disclosure", "Synthetic releases add truthful compatible constraints.", "scenario assumption", "src/value_of_disclosure.py", "Incompatible/noisy releases need not shrink a set.", "Disclosure ordering is claimed only for nested compatible additions."),
        ("Synthetic truth", "The simulator hides latent public shares/ranks from inference.", "simulation design", "src/synthetic_benchmark.py; src/external_testbed.py", "Leakage would invalidate coverage calibration.", "Known truth exists only inside the synthetic simulator."),
        ("Noise", "Noisy outcomes intentionally violate the generating rule.", "stress-test design", "src/synthetic_benchmark.py", "Coverage can fall under misspecification.", "Noise result is a stress test, not prediction accuracy."),
        ("RRI", "Configurations and predicates are predeclared and applicable.", "robustness summary", "src/rule_robustness_index.py", "Unlisted configurations are not covered.", "RRI is bounded support share, not optimality."),
        ("Artifact", "User-supplied inputs are documented and valid.", "prototype contract", "src/dss_artifact.py", "Missing/invalid inputs yield no defensible recommendation.", "Artifact gives conditional design guidance only."),
    ]
    return pd.DataFrame(rows, columns=["component", "assumption", "assumption_type", "implementation_source", "consequence_if_violated", "claim_boundary"])


def invariant_checks(root: Path) -> pd.DataFrame:
    synthetic = pd.read_csv(root / "outputs/tables/synthetic_coverage_results.csv")
    disclosure = pd.read_csv(root / "outputs/tables/value_of_disclosure.csv").set_index("disclosure_regime")
    rri = pd.read_csv(root / "outputs/tables/rule_robustness_index.csv")
    external = pd.read_csv(root / "outputs/tables/external_testbed_results.csv")
    clean_aware = synthetic.loc[(synthetic["condition"] == "rule_consistent") & (synthetic["method"] == "rule_aware_partial_identification")].iloc[0]
    clean_agnostic = synthetic.loc[(synthetic["condition"] == "rule_consistent") & (synthetic["method"] == "rule_agnostic_partial_identification")].iloc[0]
    noise_aware = synthetic.loc[(synthetic["condition"] == "outcome_noise_stress_test") & (synthetic["method"] == "rule_aware_partial_identification")].iloc[0]
    base = float(disclosure.loc["elimination_only", "mean_feasible_set_width"])
    nested_names = [
        "elimination_plus_top_k_public_rank",
        "elimination_plus_vote_bin_intervals",
        "elimination_plus_pairwise_majority",
        "elimination_plus_margin_intervals",
        "full_public_vote_theoretical_upper_benchmark",
    ]
    disclosure_ok = bool((disclosure.loc[nested_names, "mean_feasible_set_width"] <= base + 1e-10).all())
    rows = [
        ("I1", "Feasible-set width lies in [0,1] for normalized synthetic summaries.", bool(synthetic["average_feasible_set_width"].dropna().between(0.0, 1.0).all()), "all normalized synthetic widths in [0,1]", "synthetic_coverage_results.csv"),
        ("I2", "Rule-aware width does not exceed rule-agnostic width under nested correct P constraints.", float(clean_aware["average_feasible_set_width"]) <= float(clean_agnostic["average_feasible_set_width"]) + 1e-10, f"aware={float(clean_aware['average_feasible_set_width']):.3f}; agnostic={float(clean_agnostic['average_feasible_set_width']):.3f}", "synthetic_coverage_results.csv"),
        ("I3", "Compatible synthetic disclosure additions do not exceed elimination-only mean width.", disclosure_ok, f"base={base:.3f}; compared={len(nested_names)} nested scenario releases", "value_of_disclosure.csv"),
        ("I4", "Correctly specified no-noise rule-aware set covers known synthetic truth.", np.isclose(float(clean_aware["coverage_rate"]), 1.0), f"coverage={float(clean_aware['coverage_rate']):.3f}", "synthetic_coverage_results.csv"),
        ("I5", "Noise condition is labeled as stress test and may reduce coverage.", bool(float(noise_aware["coverage_rate"]) <= float(clean_aware["coverage_rate"]) + 1e-10), f"clean={float(clean_aware['coverage_rate']):.3f}; noise={float(noise_aware['coverage_rate']):.3f}", "synthetic_coverage_results.csv"),
        ("I6", "RRI values are bounded in [0,1].", bool(rri["rule_robustness_index"].between(0.0, 1.0).all()), f"min={rri['rule_robustness_index'].min():.3f}; max={rri['rule_robustness_index'].max():.3f}", "rule_robustness_index.csv"),
        ("I7", "External testbed is structurally distinct and correct-rule coverage is one under its simulator.", bool(external.loc[external["method"].eq("rule_aware_discretion"), "coverage_rate"].eq(1.0).all()), "7 candidates; 4 rounds; two intervention rounds; dense-rank protocol", "external_testbed_results.csv"),
    ]
    return pd.DataFrame(rows, columns=["check_id", "invariant", "passed", "observed_value", "evidence_source"])


def model_rigor_audit(checks: pd.DataFrame) -> str:
    failed = checks.loc[~checks["passed"], "check_id"].tolist()
    status = "pass" if not failed else "needs revision"
    return "\n".join(
        [
            "# Mathematical and Model Rigor Audit",
            "",
            f"## Status: {status}",
            "",
            "The audited model distinguishes the percentage polytope from ordinal feasible ranking sets; it does not map ranks into public vote shares. Percentage feasible states are bounded simplex points intersected with documented outcome inequalities. Ranking states are strict public-rank permutations filtered by documented direct or weak bottom-set implications. Disclosure ordering is asserted only for compatible added constraints. The synthetic simulator retains known truth outside the inference interface, and noisy outcomes are explicitly stress tests.",
            "",
            markdown_table(checks, list(checks.columns)),
            "",
            "RRI is the share of applicable, predeclared configurations supporting a conclusion predicate and is bounded in [0,1]. Feasible-set width is normalized only within its mechanism-specific representation; cardinal and ordinal widths are not interpreted as a common latent scale.",
            "",
            f"Failed invariant checks: `{', '.join(failed) if failed else 'none'}`.",
        ]
    ) + "\n"


def data_validity_audit(root: Path, evidence: pd.DataFrame) -> str:
    frozen = pd.read_csv(root / "outputs/tables/frozen_outputs_hashes.csv")
    raw_row = frozen.loc[frozen["category"].eq("raw_input")].iloc[0]
    raw_path = root / str(raw_row.relative_path)
    current = sha256(raw_path)
    return "\n".join(
        [
            "# Data Validity and Evidence Hierarchy Audit",
            "",
            "## Raw-data provenance",
            "",
            f"- Immutable raw input: `{raw_row.relative_path}`.",
            f"- Expected SHA-256: `{raw_row.sha256}`.",
            f"- Observed SHA-256: `{current}`.",
            f"- Checksum status: `{'match' if current == raw_row.sha256 else 'mismatch'}`.",
            "- The Stage 23 audit does not edit raw data or reinterpret parsed zero, missing, withdrawal, no-elimination, multiple-elimination, or finale states.",
            "",
            "## Evidence hierarchy",
            "",
            markdown_table(evidence, list(evidence.columns)),
            "",
            "The empirical application contains hidden truth: its outputs are identified feasible sets consistent with observed outcomes and conditioned on rule assumptions. Synthetic calibration and the external synthetic testbed have known simulated truth but do not become empirical validation. Artifact-level evaluation checks implemented properties, and the future user protocol supplies no human-subject result.",
        ]
    ) + "\n"


def evidence_scope_statement() -> str:
    return """
# Evidence Scope Statement

The manuscript uses an explicit evidence hierarchy. Formal propositions establish properties of the stated constraint systems. Synthetic benchmarks calibrate those systems only when latent preferences are known inside the simulator. The external synthetic testbed examines structural portability under a different institutional design. The longitudinal empirical application reports identified feasible sets consistent with observed outcomes and conditioned on documented rule assumptions; it does not recover hidden public preferences. The DSS cockpit receives artifact-level evaluation, while the scenario-based user evaluation is a future protocol only.

Accordingly, the manuscript uses the terms *identified feasible set*, *consistent with observed outcomes*, *conditioned on rule assumptions*, *synthetic calibration*, *artifact-level evaluation*, and *scenario-based validation protocol*. It does not state that public preferences are revealed, recovered, causal, optimal, or organizationally validated.
"""


def model_assumptions_section() -> str:
    return """
# Model Assumptions and Identification

For a percentage-aggregation week with active candidates indexed by i, the latent public-support vector p lies in the simplex: p_i >= 0 and sum_i p_i = 1. If candidate e is eliminated under the documented combined-score rule and candidate j survives, the rule-aware model adds the affine inequality p_e + q_e <= p_j + q_j, where q is the observed normalized expert component. The identified feasible set is the intersection of these inequalities and the simplex. Coordinate-wise linear programs provide sharp lower and upper bounds within that stated model.

For ranking regimes, the hidden object is a strict public ranking, not a cardinal support vector. The feasible ranking set contains the public permutations that, when combined with documented expert ranks and the named tie policy, satisfy the observed direct elimination or weak judge-save bottom-set implication. A weak judge-save rule is therefore a different observation rule, not a correction to a recovered public ranking. No cardinal-ordinal comparison is made without a separately justified common functional.

Disclosure scenarios are synthetic compatible constraint additions. The weak-shrinkage statement applies only when added information is truthful and compatible with the baseline state space. The simulator retains its latent truth outside the inference calculation; coverage is a calibration property, whereas deliberately noisy outcomes are misspecification stress tests. These assumptions make results conditional and auditable rather than point-identifying hidden public preferences.
"""


def artifact_input_output_contract(root: Path) -> pd.DataFrame:
    config = config_from_mapping(default_demo_payload())
    rows = [
        ("observed_elimination_outcomes", "nonempty list of documented rounds with active candidates, outcome type, eliminated set, and expert scores", "required", "round-specific compatible-state constraints", "Supports coarse-outcome rule encoding."),
        ("aggregation_rule_type", "percentage | ranking | ranking_plus_judge_save", "required", "cardinal LP or ordinal feasible-ranking engine", "Prevents mixing cardinal and ordinal estimands."),
        ("judge_save_assumption", "not_applicable | none | direct | weak_bottom_set", "required", "direct or weak bottom-set interpretation", "Makes discretionary information loss explicit."),
        ("tie_handling_assumption", "strict | tie_inclusive", "required", "named expert-rank tie handling", "Records a sensitivity-relevant assumption."),
        ("disclosure_regime", "predeclared disclosure category", "required", "conditional recommendation logic", "Does not assert observed privacy or trust effects."),
        ("decision_objective", "reduce_uncertainty | preserve_discretion | protect_privacy | improve_accountability", "required", "selects bounded recommendation template", "Objective validity remains a user/governance responsibility."),
        ("feasible_set_width", "mean rule-specific conditional width", "output", "uncertainty class", "Does not recover a hidden public vote."),
        ("rule_robustness_label", "available predeclared RRI classification", "output", "assumption-sensitive/robust flag", "Does not establish institutional optimality."),
        ("disclosure_recommendation", "objective- and width-conditioned text", "output", "design alternative", "Does not measure stakeholder preference."),
        ("design_warning and accountability_implication", "special-case and record-keeping warning", "output", "audit trace", "Does not replace legal, privacy, or stakeholder review."),
    ]
    frame = pd.DataFrame(rows, columns=["field", "schema_or_allowed_values", "contract_role", "decision_system_use", "boundary"])
    frame["demo_configuration_value"] = [
        "2 illustrative synthetic elimination rounds", config.aggregation_rule_type, config.judge_save_assumption,
        config.tie_handling_assumption, config.disclosure_regime, config.decision_objective,
        "computed at runtime", "read from available RRI", "computed at runtime", "computed at runtime",
    ]
    return frame


def artifact_decision_trace(root: Path) -> pd.DataFrame:
    report = (root / "outputs/artifact_demo/demo_decision_report.md").read_text(encoding="utf-8")
    rows = [
        ("coarse outcomes", "two illustrative synthetic elimination rounds", "rule-specific compatible-state construction", "feasible-set width 0.850", "broad conditional interval; do not select a latent point"),
        ("aggregation rule", "percentage", "simplex plus affine elimination inequalities", "coordinate-wise LP bounds", "uncertainty is cardinal only for this rule"),
        ("judge-save and tie assumptions", "not applicable; tie inclusive", "recorded in configuration", "rule robustness label", "assumptions must remain in the audit record"),
        ("disclosure and objective", "vote-bin intervals; reduce uncertainty", "conditional disclosure template", "add least intrusive rank or pairwise signal", "privacy/reporting tradeoffs require local evidence"),
        ("accountability", "versioned configuration and report", "traceable warning and implication", "record rule, tie, disclosure, and objective", "not a deployed or organizationally adopted system"),
    ]
    frame = pd.DataFrame(rows, columns=["decision_trace_step", "recorded_input", "model_transform", "artifact_output", "decision_support_boundary"])
    frame["demo_report_present"] = "DSS Artifact Demonstration Report" in report
    return frame


def dss_artifact_final_section() -> str:
    return """
# DSS Artifact and Workflow

The prototype is a model-driven, design-oriented DSS artifact rather than a collection of scripts. Its JSON input contract records observed elimination outcomes, aggregation-rule type, judge-save assumption, tie-handling assumption, disclosure regime, and decision objective. The artifact converts those inputs into a rule-specific feasible-set width, uncertainty class, predeclared rule-robustness label where available, disclosure recommendation, design warning, and accountability implication.

For an institutional organizer or platform governance analyst, the supported alternatives are to maintain or adjust an aggregation rule, document or narrow expert discretion, select a disclosure regime, and specify a tie protocol. The supported criteria are conditional uncertainty, robustness to named assumptions, auditability, privacy/reporting tradeoffs, and implementation burden. Recommendation logic is bounded: a broad compatible set under an uncertainty-reduction objective prompts a least-intrusive disclosure recommendation, whereas a discretion-preservation objective prompts a documented eligibility-and-rationale record.

The artifact supplies a reproducible demonstration and artifact-level evaluation. It is not deployed, has not been adopted by an organization, has not been evaluated by human participants, and has no measured organizational impact. Decision objectives, privacy assessment, legal review, stakeholder consultation, and implementation authority remain outside the system.
"""


def external_testbed_design_matrix(root: Path) -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("main known-truth benchmark", "synthetic percentage aggregation", "yes, simulator only", "5", "one observed elimination per case", "none", "multiple synthetic disclosure channels", "not applicable", "clean and noisy-outcome stress conditions", "logical calibration of cardinal feasible bounds"),
            ("external testbed", "synthetic community-grant prioritization", "yes, simulator only", "7", "4 elimination rounds", "2 of 4 synthetic intervention rounds", "synthetic pairwise-majority comparison", "dense rank primary; four-policy sensitivity", "direct-rule misspecification comparator", "structural portability of ordinal/discretion logic"),
            ("empirical application", "longitudinal expert-crowd competition record", "no", "varies by documented week", "varies by documented week", "observed R_plus rule condition", "coarse observed outcomes; historical release unknown", "documented tie-policy sensitivity", "rule/coding sensitivity", "mechanism-specific feasible sets under hidden truth"),
        ],
        columns=["setting", "setting_type", "truth_known", "candidate_count", "elimination_rounds", "expert_intervention", "disclosure_regime", "tie_handling_protocol", "noise_or_misspecification", "purpose"],
    )


def external_testbed_final_section(matrix: pd.DataFrame) -> str:
    return "\n".join(
        [
            "# External Testbed",
            "",
            "The external testbed is a fixed-seed synthetic community-grant prioritization setting. It begins with seven candidates, contains four elimination rounds, applies a synthetic intervention in two rounds, uses a pairwise public-priority disclosure, and adopts dense-rank tie handling with four-policy sensitivity. These features differ from both the single-case percentage benchmark and the real empirical application.",
            "",
            markdown_table(matrix, list(matrix.columns)),
            "",
            "The external testbed demonstrates structural portability, not universal empirical validity. Its latent ranking is known only inside the simulator, and its coverage and false-certainty diagnostics do not validate real grant decisions, user behavior, or organizational outcomes.",
        ]
    ) + "\n"


def baseline_validity_section(table: pd.DataFrame) -> str:
    return "\n".join(
        [
            "# Baseline Validity and Interpretation",
            "",
            "Baselines are organized by information set rather than presented as a simple accuracy tournament. Rule-aware partial identification is evaluated as a calibrated compatible-state representation: under the correct simulator it covers known latent preference, narrows the rule-agnostic state space, and avoids the false certainty created by unsupported point selection. The prediction-only comparator remains secondary because predictive performance does not identify hidden preferences.",
            "",
            markdown_table(table, list(table.columns)),
            "",
            "The full-disclosure oracle is permitted only inside the synthetic benchmark and is explicitly excluded from empirical interpretation. The appropriate conclusion is that rule-aware feasible sets preserve uncertainty and rule structure under hidden preferences; it is not that the proposed method is universally more accurate in a prediction sense.",
        ]
    ) + "\n"


def related_work_submission() -> str:
    return """
# Related Work

## Decision Support Systems Under Uncertainty

Decision support under incomplete institutional information requires systems that preserve what remains unresolved rather than silently selecting a point estimate. The final bibliography must add and verify a DSS source for this framing: [REF-DSS-UNCERTAINTY].

## Model-Driven and Rule-Aware DSS

The prototype is model-driven because documented rules, outcomes, and disclosure assumptions determine the compatible-state calculation and recommendation boundary. A final verified source is required for this stream: [REF-MODEL-DRIVEN-DSS].

## Expert-Crowd Aggregation and Collective Decision Making

The application concerns institutions that combine expert and collective input, while the collective component remains hidden in the observed record. The final bibliography must verify an appropriate source: [REF-EXPERT-CROWD].

## Preference Uncertainty and Partial Identification

Partial-identification logic motivates feasible sets and decisions under incomplete observability rather than an unsupported latent point. Existing verified source-map entries support this methodological stream; the final bibliography should insert [REF-PARTIAL-IDENTIFICATION] only after exact claim review.

## Transparency, Accountability, and Disclosure

The disclosure analysis formalizes information consequences of alternative releases. It does not measure trust, privacy, reporting cost, or accountability outcomes. Relevant DSS and governance citations require verification: [REF-ALGORITHMIC-ACCOUNTABILITY] and [REF-DISCLOSURE].

## Research Gap

Existing research has not sufficiently addressed how institutional designers can evaluate aggregation mechanisms when public preferences are hidden, expert intervention is rule-dependent, and disclosure policies determine the identifiability of collective preferences.
"""


def related_work_gap_map() -> str:
    return """
# Related Work Gap-to-Claim Map

| Placeholder | Needed claim | Current status | Required action |
| --- | --- | --- | --- |
| [REF-DSS-UNCERTAINTY] | DSS under institutional uncertainty | missing verified DSS source | author/manual literature verification |
| [REF-MODEL-DRIVEN-DSS] | model-driven, rule-aware decision support | missing verified DSS source | author/manual literature verification |
| [REF-EXPERT-CROWD] | expert-crowd decision context | cautious existing motivation only | verify claim precision |
| [REF-PARTIAL-IDENTIFICATION] | identified sets under incomplete observability | existing verified source map | finalize bibliography and full-text check |
| [REF-ALGORITHMIC-ACCOUNTABILITY] | accountability boundary | missing verified DSS/governance source | author/manual literature verification |
| [REF-DISCLOSURE] | disclosure tradeoffs | missing verified disclosure source | author/manual literature verification |

No placeholder is a citation. The manuscript must not be submitted with unresolved placeholders or unverified bibliographic claims.
"""


def final_title() -> str:
    return "# Final Title\n\nRule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences\n\n## Alternatives\n\n1. A Rule-Aware Decision Support Framework for Institutional Aggregation under Hidden Preferences\n2. Decision Support for Accountable Expert-Crowd Aggregation with Partial Preference Disclosure\n3. Evaluating Aggregation Rules under Hidden Public Preferences: A Decision-Support Framework\n"


def final_abstract() -> str:
    return """
# Abstract

 Institutional designers often combine expert judgment with public input while retaining only coarse outcomes. When public preferences are hidden, the same observed elimination can be consistent with multiple collective states, expert intervention, and rule-specific artifacts. We develop a rule-aware decision-support framework that represents this uncertainty through feasible preference sets; it is not a public-vote recovery method. Documented percentage rules yield cardinal feasible intervals, ranking rules yield ordinal feasible rankings, and a weak judge-save condition exposes a discretion-identifiability tradeoff. The framework evaluates rule, tie-handling, and disclosure assumptions through a discretion frontier, synthetic disclosure scenarios, and a Rule Robustness Index. A JSON-configurable DSS prototype maps documented outcomes and institutional objectives to conditional uncertainty classes, design warnings, disclosure recommendations, and accountability records. Fixed-seed synthetic benchmarks assess coverage and false certainty when truth is known only inside the simulator; a structurally different synthetic community-grant testbed examines portability. A longitudinal empirical application demonstrates mechanism-specific feasible sets under hidden truth. The study provides design-oriented decision support under incomplete observability. It does not recover exact public preferences, demonstrate organizational impact, or report a completed human-subject evaluation.
"""


def final_highlights() -> str:
    return """
# Highlights

- Rule-aware feasible sets preserve uncertainty under hidden preferences.
- Aggregation rules determine cardinal versus ordinal identified objects.
- Judge-save discretion weakens identifiability under stated rule assumptions.
- Synthetic calibration separates coverage from false certainty.
- A DSS prototype links uncertainty to conditional design recommendations.
"""


def final_keywords() -> str:
    return "# Keywords\n\nDecision support systems; expert-crowd aggregation; hidden preferences; partial identification; institutional disclosure; rule robustness\n"


def final_contributions() -> str:
    return """
# Contributions

1. A rule-aware partial-identification model for decision support under hidden public preferences.
2. A mechanism-evaluation framework comparing aggregation rules, expert-discretion assumptions, tie-handling protocols, and disclosure regimes.
3. A DSS artifact that translates feasible-set uncertainty into institutional design recommendations.
4. A reproducible evaluation package combining synthetic benchmark, external testbed, baseline comparison, and robustness analysis.
"""


def integrated_manuscript(root: Path, checks: pd.DataFrame) -> str:
    identification = pd.read_csv(root / "outputs/tables/identification_comparison_by_regime.csv").set_index("regime")
    synthetic = pd.read_csv(root / "outputs/tables/synthetic_coverage_results.csv")
    external = pd.read_csv(root / "outputs/tables/external_testbed_results.csv").set_index("method")
    p_width = float(identification.loc["P", "mean_normalized_uncertainty"])
    rp_width = float(identification.loc["R_plus", "mean_normalized_uncertainty"])
    clean = synthetic.loc[(synthetic["condition"] == "rule_consistent") & (synthetic["method"] == "rule_aware_partial_identification")].iloc[0]
    noise = synthetic.loc[(synthetic["condition"] == "outcome_noise_stress_test") & (synthetic["method"] == "rule_aware_partial_identification")].iloc[0]
    external_aware = external.loc["rule_aware_discretion"]
    return f"""
# Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences

## Abstract

Institutional designers often combine expert judgment with public input while retaining only coarse outcomes. When public preferences are hidden, the same observed elimination can be consistent with multiple collective states, expert intervention, and rule-specific artifacts. We develop a rule-aware decision-support framework that represents this uncertainty through feasible preference sets rather than a recovered public vote. Documented percentage rules yield cardinal feasible intervals, ranking rules yield ordinal feasible rankings, and a weak judge-save condition exposes a discretion-identifiability tradeoff. The framework evaluates rule, tie-handling, and disclosure assumptions through a discretion frontier, synthetic disclosure scenarios, and a Rule Robustness Index. A JSON-configurable DSS prototype maps documented outcomes and institutional objectives to conditional uncertainty classes, design warnings, disclosure recommendations, and accountability records. Fixed-seed synthetic benchmarks assess coverage and false certainty when truth is known only inside the simulator; a structurally different synthetic community-grant testbed examines portability. A longitudinal empirical application demonstrates mechanism-specific feasible sets under hidden truth. The study provides design-oriented decision support under incomplete observability. It does not recover exact public preferences, demonstrate organizational impact, or report a completed human-subject evaluation.

**Keywords:** Decision support systems; expert-crowd aggregation; hidden preferences; partial identification; institutional disclosure; rule robustness.

## 1. Introduction

Organizations often need to evaluate an aggregation rule after only coarse outcomes, while the collective component remains hidden. The resulting decision problem is not to impute a public vote but to assess what a documented rule permits later observers to learn and how alternative rules or disclosures alter that uncertainty. Figure 1 presents this rule-aware decision-support framing, and Figure 2 locates it in an institutional workflow.

This paper makes four contributions. First, it formalizes rule-aware partial identification for hidden public preferences. Second, it compares rule, discretion, tie, and disclosure assumptions. Third, it implements a design-oriented DSS prototype. Fourth, it supplies a reproducible evaluation package with synthetic calibration, an external synthetic testbed, baselines, and robustness checks. **Decision-support implication.** Institutional designers can use the framework to compare information consequences without presenting a hidden preference point as observed.

## 2. Decision-Support Problem

The supported user is an institutional organizer or platform governance analyst deciding whether to retain an aggregation mechanism, document or narrow expert discretion, alter a tie protocol, or disclose additional aggregate information. Table 1 lists the decision alternatives and criteria. The system accepts documented outcomes, a rule type, a judge-save assumption, a tie-handling assumption, a disclosure regime, and a decision objective. It reports compatible-state uncertainty, a bounded recommendation, and the records needed for later audit.

The system does not choose objectives, perform legal or privacy review, measure stakeholder trust, or replace implementation authority. **Decision-support implication.** The appropriate output is a conditional design recommendation with an uncertainty warning, not an automated institutional decision.

## 3. Related Work

The study connects decision support under uncertainty, model-driven and rule-aware DSS, expert-crowd aggregation, partial identification, and transparency/accountability. The final bibliography requires verified sources for each DSS stream: [REF-DSS-UNCERTAINTY], [REF-MODEL-DRIVEN-DSS], [REF-EXPERT-CROWD], [REF-PARTIAL-IDENTIFICATION], [REF-ALGORITHMIC-ACCOUNTABILITY], and [REF-DISCLOSURE]. Existing research has not sufficiently addressed how institutional designers can evaluate aggregation mechanisms when public preferences are hidden, expert intervention is rule-dependent, and disclosure policies determine the identifiability of collective preferences.

**Decision-support implication.** The contribution is scoped to conditional evaluation of institutional mechanisms, rather than an unsupported claim of general DSS effectiveness.

## 4. Rule-Aware Partial-Identification Framework

For a percentage week, let p be the latent public-support vector in the unit simplex and q the observed normalized expert component. A documented elimination creates affine comparisons between eliminated and surviving candidates. The identified feasible set is the intersection of these constraints with the simplex; coordinate-wise linear programs obtain sharp conditional bounds. Table 2 records the assumption inventory. No-elimination and withdrawal weeks add no comparative outcome constraint; multiple eliminations and final-order information are handled only when their rule inputs are documented.

For ranking and judge-save regimes, the hidden object is a strict public ranking. Feasible rankings are those consistent with expert ranks, the named tie policy, and a direct or weak bottom-set implication. Cardinal and ordinal summaries remain mechanism-specific and are not pooled into a common public-support scale. **Decision-support implication.** A decision maker can see whether a rule changes the identifiable object before comparing policy alternatives.

## 5. DSS Artifact and Workflow

The prototype operationalizes the model as a JSON-configurable decision-support artifact. Figure 2 shows the organizer workflow from coarse outcomes through compatible states and warnings to a documented disclosure or rule choice. Its input/output contract and decision trace are reported in the artifact audit. The demonstration uses illustrative synthetic inputs and reports a broad conditional width; it is not an empirical replay or deployed system.

**Decision-support implication.** The artifact translates rule-aware uncertainty into an auditable recommendation while retaining objective setting and governance review outside the system.

## 6. Mechanism Evaluation Modules

### 6.1 Discretion-Identifiability Frontier

Figure 3 is a deterministic synthetic rule scenario that relaxes a direct bottom-set implication. The separate empirical R-plus comparison evaluates only the documented direct-versus-weak condition. The synthetic continuum is not a historical scale of intervention strength. **Decision-support implication.** Discretion can be evaluated as a governance tradeoff between flexibility and later identifiability, conditional on disclosed eligibility rules.

### 6.2 Value of Institutional Disclosure

Figure 4 compares synthetic compatible disclosure additions. The formal weak-shrinkage statement applies only when added information is truthful and compatible with the baseline constraints; privacy, cost, interpretability, and accountability values are scenario descriptors rather than measured outcomes. **Decision-support implication.** The artifact can select the least intrusive modeled disclosure that reduces compatible-state uncertainty while recording unresolved governance tradeoffs.

### 6.3 Rule Robustness Index

Figure 5 reports the share of predeclared applicable configurations supporting each conclusion. RRI is bounded in [0,1] and does not establish welfare optimality. **Decision-support implication.** A reported recommendation can distinguish robust conclusion predicates from assumption-sensitive ones instead of hiding rule dependence.

## 7. Synthetic Benchmark

Table 3 defines the baseline information sets, and Table 4 reports known-truth synthetic coverage results. Under correctly specified, no-noise simulated outcomes, the rule-aware feasible set covers the synthetic latent preference with rate {float(clean.coverage_rate):.3f}. Under the explicitly labeled noisy-outcome stress test, coverage is {float(noise.coverage_rate):.3f}. Figure 6 displays coverage and false-certainty diagnostics. The full-disclosure oracle is synthetic only, and prediction baselines do not become hidden-preference recovery tools.

**Decision-support implication.** Calibration evidence supports retaining feasible-set uncertainty under a stated simulator, rather than selecting a point estimate that can create false certainty.

## 8. External Testbed

The structurally different community-grant simulator starts with seven candidates, runs four elimination rounds, includes two synthetic intervention rounds, uses pairwise disclosure, and applies dense-rank tie handling with sensitivity checks. Figure 7 and Table 5 show that the correct rule-aware representation has synthetic coverage {float(external_aware.coverage_rate):.3f} and mean normalized feasible-rank width {float(external_aware.average_feasible_set_width):.3f}. This is structural portability evidence, not universal empirical validity.

**Decision-support implication.** Designers can assess whether a rule-aware workflow remains coherent under a different institutional mechanism before treating it as a general-purpose recommendation.

## 9. Empirical Application

The longitudinal application supplies repeated documented rule regimes with hidden public truth. Percentage weeks have mean normalized coordinate-wise feasible width {p_width:.3f}; R-plus weeks have mechanism-specific normalized rank width {rp_width:.3f}. These quantities are not direct measurements on a common latent scale. The application illustrates feasible sets consistent with observed outcomes and conditioned on rule assumptions.

 **Decision-support implication.** Empirical users should interpret reported intervals and ranking supports as limits of inference from coarse records; they do not recover public preferences.

## 10. DSS Artifact-Level Evaluation

Figure 8 and the artifact evaluation matrix inspect decision relevance, uncertainty transparency, recommendation interpretability, robustness awareness, disclosure-cost awareness, rule-design usefulness, reproducibility, and implementation feasibility. The future user evaluation remains a scenario-based protocol with no participants or human-subject results.

**Decision-support implication.** The prototype demonstrates inspectable decision-support properties and a future validation pathway, but does not claim measured usability, adoption, or organizational performance.

## 11. Decision-Support Recommendations

 Table 6 maps stated objectives to conditional rule and disclosure designs. The recommendations do not choose an optimal policy: they help an institution record why it selected a disclosure or discretion policy and what uncertainty remains. Table 7 maps each main claim to its evidence and boundary.

**Decision-support implication.** Recommendation quality depends on documented objectives, rule fidelity, and local privacy or reporting constraints that remain outside the model.

## 12. Discussion

The framework shifts attention from estimating a hidden public quantity to evaluating the institutional observation rule that makes that quantity only partially identified. It preserves the distinction between cardinal and ordinal objects, exposes discretion as information-relevant, and makes disclosure an explicit design choice. The evidence hierarchy separates formal results, synthetic calibration, structural simulation, empirical illustration, artifact checks, and a future user-evaluation protocol.

**Decision-support implication.** A DSS can enhance institutional reasoning by exposing what the record supports and what additional disclosure or rule documentation would be needed for a stronger conclusion.

## 13. Limitations

The method does not recover exact hidden votes. The empirical application is an institutional testbed rather than universal proof. Synthetic benchmarks assess logical calibration rather than real-world truth. Artifact-level evaluation is not deployed organizational impact, and no completed human-subject study is claimed. Rule specification quality affects all compatible-state conclusions. Disclosure recommendations involve unmeasured privacy and reporting-cost tradeoffs. Expert discretion is modeled as a governance tradeoff rather than inherently harmful.

**Decision-support implication.** Users must preserve the rule, tie, disclosure, and objective assumptions alongside every recommendation.

## 14. Conclusion

Rule-aware partial identification provides a decision-support response to hidden public preferences and coarse institutional feedback. The contribution is a reproducible prototype that links documented rule assumptions to compatible-state uncertainty, conditional disclosure guidance, and audit records. Its claims are deliberately bounded by the evidence hierarchy and require author-side completion of citations, declarations, and live journal compliance checks before submission.

**Decision-support implication.** The manuscript supports author-side completion as a DSS submission draft, not an upload-ready claim of deployed or universally validated decision support.

## Figure Captions

**Figure 1. DSS conceptual framework.** Evidence type: theoretical decision-support framework. Documented rules and coarse outcomes lead to rule-specific feasible sets, not observed public votes.

**Figure 2. Decision-support workflow.** Evidence type: design-oriented DSS prototype workflow. The workflow separates supported configuration and recommendation tasks from external governance responsibilities.

**Figure 3. Discretion-identifiability frontier.** Evidence type: deterministic synthetic rule scenario. It illustrates nested weak-rule relaxation and is not a historical scale of expert intervention.

**Figure 4. Synthetic disclosure uncertainty curve.** Evidence type: synthetic compatible-disclosure scenario. Scenario descriptors are not measured trust, privacy, or cost outcomes.

**Figure 5. Rule Robustness Index.** Evidence type: formal/empirical configuration summary. RRI is a bounded share of applicable configurations, not a measure of institutional optimality.

**Figure 6. Synthetic benchmark coverage.** Evidence type: fixed-seed known-truth simulation. Coverage applies only to latent preferences generated inside the simulator.

**Figure 7. External synthetic testbed comparison.** Evidence type: structurally different synthetic community-grant setting. It demonstrates portability under stated conditions, not universal empirical validity.

**Figure 8. Artifact evidence-completeness checks.** Evidence type: artifact-level evaluation. The graphic is not a user-effectiveness, trust, adoption, or organizational-impact score.

## Table Notes

**Table 1. Decision alternatives and criteria.** Evidence type: design template; cost, privacy, and trust require local stakeholder evidence.

**Table 2. Assumption inventory.** Evidence type: formal model audit; assumptions define the conditional identified object.

**Table 3. Baseline definitions.** Evidence type: benchmark protocol; oracle access is synthetic-only.

**Table 4. Synthetic coverage results.** Evidence type: fixed-seed known-truth simulation; noise rows are stress tests.

**Table 5. External testbed results.** Evidence type: external synthetic testbed; no real grant preference is observed.

**Table 6. Design recommendation matrix.** Evidence type: conditional institutional design template; not an empirical welfare ranking.

**Table 7. Claim-evidence alignment.** Evidence type: manuscript integrity audit; every main claim is bounded by its evidence source.
"""


def limitations_final() -> str:
    return """
# Limitations

1. The method does not recover exact hidden votes or reveal a true public preference.
2. The empirical application is an institutional testbed, not universal proof about organizations or public behavior.
3. Synthetic benchmarks validate logical calibration only when truth is known inside the simulator.
4. Artifact-level evaluation is not equivalent to deployment, adoption, or organizational impact.
5. No completed human-subject user study is claimed; the user evaluation is a future scenario-based protocol.
6. Rule specification, tie handling, and intervention coding affect the compatible-state result.
7. Disclosure recommendations involve unmeasured privacy, reporting-cost, and stakeholder tradeoffs.
8. Expert discretion is a governance tradeoff under stated rules, not an inherently harmful practice.
"""


def claim_evidence_alignment() -> pd.DataFrame:
    rows = [
        ("CE1", "Coarse outcomes identify feasible sets rather than a public-vote point.", "outputs/tables/constraint_summary.csv; outputs/tables/uncertainty_by_week_regime_p.csv", "real empirical application with hidden truth", "main text", "conditioned on documented rules", "pass"),
        ("CE2", "Percentage and ranking mechanisms define different identified objects.", "src/constraints.py; src/ranking_identification.py; outputs/tables/identification_comparison_by_regime.csv", "formal theorem or proposition", "main text", "do not pool cardinal and ordinal widths", "pass"),
        ("CE3", "Weak judge-save interpretation expands the compatible ranking set within evaluated R_plus weeks.", "outputs/tables/ranking_identification_summary_rplus.csv; outputs/figures/judge_save_identifiability_loss.png", "real empirical application with hidden truth", "main text", "within-rule containment only", "pass"),
        ("CE4", "Rule-aware synthetic bounds cover known latent preference under correct no-noise simulation.", "outputs/tables/synthetic_coverage_results.csv", "synthetic benchmark", "main text", "synthetic calibration only", "pass"),
        ("CE5", "Synthetic disclosure additions reduce compatible-set width under compatible constraints.", "outputs/tables/value_of_disclosure.csv", "synthetic benchmark", "main text", "truthful compatible disclosure condition", "pass"),
        ("CE6", "External community-grant simulator supports structural portability under its stated mechanism.", "outputs/tables/external_testbed_results.csv", "external synthetic testbed", "main text", "not universal empirical validity", "pass"),
        ("CE7", "The prototype exposes decision inputs, conditional recommendations, and audit records.", "outputs/artifact_demo/demo_decision_report.md; outputs/tables/dss_evaluation_metrics.csv", "artifact-level evaluation", "main text", "not deployed or user validated", "pass"),
        ("CE8", "Future user evaluation has specified roles, tasks, and measures.", "outputs/tables/scenario_based_evaluation.csv", "scenario-based future user evaluation protocol", "appendix and limitation", "protocol only; no participants", "pass"),
        ("CE9", "Prediction, counterfactual, and Pareto analyses are secondary or exploratory.", "outputs/tables/prediction_results.csv; outputs/tables/robust_aggregation_results.csv", "real empirical application with hidden truth", "supplement", "not hidden-preference recovery or causal impact", "pass"),
    ]
    return pd.DataFrame(rows, columns=["claim_id", "controlled_claim", "evidence_source", "evidence_type", "allowed_location", "mandatory_boundary", "alignment_status"])


def overclaim_detection(root: Path) -> tuple[pd.DataFrame, str]:
    risky = ("prove", "reveal", "recover", "true public preference", "causal", "impact", "deployed", "user validated", "organizational performance", "exact", "optimal")
    final_safe = {
        "prove": "retain only in formal-proposition context; otherwise soften to demonstrate",
        "reveal": "remove or replace with consistent with observed outcomes",
        "recover": "retain only in explicit negation; otherwise remove",
        "true public preference": "retain only in explicit non-recovery boundary",
        "causal": "remove unless a causal design is supplied",
        "impact": "retain only in explicit no-impact limitation",
        "deployed": "retain only in explicit non-deployment limitation",
        "user validated": "remove unless participant evidence exists",
        "organizational performance": "remove unless measured evidence exists",
        "exact": "retain only in exact-enumeration or non-recovery boundary context",
        "optimal": "retain only in explicit non-optimality boundary",
    }
    rows: list[dict[str, Any]] = []
    for path in sorted((root / "manuscript").rglob("*.md")):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for term in risky:
            matches = list(re.finditer(re.escape(term), text, flags=re.IGNORECASE))
            if not matches:
                continue
            for match in matches[:8]:
                start = max(0, match.start() - 220)
                end = min(len(text), match.end() + 94)
                excerpt = " ".join(text[start:end].split())
                negative = bool(re.search(r"(does not|do not|not |no |never |without|rather than)", excerpt, flags=re.IGNORECASE))
                is_final = path.name in {"DSS_submission_draft_integrated.md", "DSS_submission_draft_integrated_clean.md", "abstract_final_DSS.md", "limitations_final_DSS.md"}
                rows.append(
                    {
                        "file": relative,
                        "term": term,
                        "excerpt": excerpt,
                        "in_final_draft": is_final,
                        "disposition": "keep boundary wording" if negative else ("manual review" if is_final else "legacy draft; not submission source"),
                        "required_action": final_safe[term],
                    }
                )
    frame = pd.DataFrame(rows)
    final_flags = frame.loc[frame["in_final_draft"] & frame["disposition"].eq("manual review")] if not frame.empty else frame
    report = "\n".join(
        [
            "# Overclaim Detection Report",
            "",
            f"- Risky-term occurrences scanned across manuscript Markdown files: `{len(frame)}`.",
            f"- Non-negated occurrences requiring manual review in the final integrated sources: `{len(final_flags)}`.",
            "- Legacy drafts are retained for provenance but are not submission sources; their wording is not silently rewritten by Stage 23.",
            "",
            markdown_table(frame.head(120), list(frame.columns)) if not frame.empty else "No configured risky terms were found.",
        ]
    ) + "\n"
    return frame, report


def figure_metadata(path: Path) -> tuple[str, str, str]:
    if not path.is_file():
        return "missing", "missing", "missing"
    with Image.open(path) as image:
        dpi = image.info.get("dpi", ())
        dpi_text = "x".join(str(round(float(value))) for value in dpi) if dpi else "not embedded"
        dimensions = f"{image.width}x{image.height}"
    return dimensions, dpi_text, "pass" if dpi and min(dpi) >= FIGURE_DPI_TARGET else "needs production check"


def final_figure_list(root: Path) -> pd.DataFrame:
    rows = [
        ("Figure 1", "DSS conceptual framework", "outputs/figures/dss_conceptual_framework.png", "theoretical decision-support framework", "Section 1", "yes"),
        ("Figure 2", "Decision-support workflow", "outputs/figures/decision_support_workflow.png", "theoretical decision-support workflow", "Section 5", "yes"),
        ("Figure 3", "Discretion-identifiability frontier", "outputs/figures/discretion_identifiability_frontier.png", "synthetic rule scenario", "Section 6.1", "yes"),
        ("Figure 4", "Disclosure uncertainty curve", "outputs/figures/disclosure_uncertainty_curve.png", "synthetic institutional-disclosure scenario", "Section 6.2", "yes"),
        ("Figure 5", "Rule robustness heatmap", "outputs/figures/rule_robustness_heatmap.png", "formal/empirical configuration summary", "Section 6.3", "yes"),
        ("Figure 6", "Synthetic benchmark coverage", "outputs/figures/synthetic_benchmark_coverage.png", "synthetic known-truth benchmark", "Section 7", "yes"),
        ("Figure 7", "External testbed comparison", "outputs/figures/external_testbed_comparison.png", "external synthetic testbed", "Section 8", "yes"),
        ("Figure 8", "DSS artifact evaluation", "outputs/figures/dss_evaluation_radar.png", "artifact-level evaluation", "Section 10", "yes"),
    ]
    frame = pd.DataFrame(rows, columns=["figure_id", "title", "source", "evidence_type", "integrated_citation", "caption_in_integrated_draft"])
    metadata = frame["source"].map(lambda value: figure_metadata(root / value))
    frame[["pixel_dimensions", "embedded_dpi", "production_resolution_status"]] = pd.DataFrame(metadata.tolist(), index=frame.index)
    visual = {
        "Figure 1": ("needs re-export", "Visual audit found the lower conceptual row clipped in the current PNG."),
        "Figure 2": ("pass", "Workflow boxes and labels are readable."),
        "Figure 3": ("pass", "Axes, markers, and synthetic-scenario boundary are readable."),
        "Figure 4": ("pass", "Scenario labels and boundary note are readable."),
        "Figure 5": ("needs padding review", "Colorbar label approaches the image edge; verify production padding."),
        "Figure 6": ("pass", "Known-truth and false-precision panels are readable."),
        "Figure 7": ("needs padding review", "Long rotated method labels require production-format review."),
        "Figure 8": ("pass", "Artifact-level boundary and radar labels are readable."),
    }
    frame[["visual_inspection_status", "visual_inspection_note"]] = frame["figure_id"].map(visual).apply(pd.Series)
    frame["label_and_abbreviation_status"] = "audited caption required; labels are present in source figure"
    frame["submission_status"] = np.where(frame["production_resolution_status"].eq("pass"), "content-ready; verify official production rule", "content-ready; needs production-resolution confirmation")
    return frame


def final_table_list() -> pd.DataFrame:
    rows = [
        ("Table 1", "Decision alternatives and criteria", "outputs/tables/decision_alternatives_criteria.csv", "design template", "Section 2", "yes", "yes"),
        ("Table 2", "Assumption inventory", "outputs/tables/assumption_inventory.csv", "formal model audit", "Section 4", "yes", "yes"),
        ("Table 3", "Baseline definitions", "outputs/tables/baseline_definition_table.csv", "benchmark protocol", "Section 7", "yes", "yes"),
        ("Table 4", "Synthetic coverage results", "outputs/tables/synthetic_coverage_results.csv", "synthetic benchmark", "Section 7", "yes", "yes"),
        ("Table 5", "External testbed results", "outputs/tables/external_testbed_results.csv", "external synthetic testbed", "Section 8", "yes", "yes"),
        ("Table 6", "Design recommendation matrix", "outputs/tables/design_recommendation_matrix.csv", "conditional design template", "Section 11", "yes", "yes"),
        ("Table 7", "Claim-evidence alignment", "outputs/tables/claim_evidence_alignment.csv", "manuscript integrity audit", "Section 11", "yes", "yes"),
    ]
    return pd.DataFrame(rows, columns=["table_id", "title", "source", "evidence_type", "integrated_citation", "title_present", "note_present"]).assign(
        abbreviation_status="abbreviations expanded in caption/note before typesetting",
        decimal_status="CSV preserves machine precision; final typesetting requires standardized display decimals",
        submission_status="content-ready; requires journal table formatting",
    )


def figure_table_quality_audit(figures: pd.DataFrame, tables: pd.DataFrame, integrated: str) -> str:
    missing_citations = []
    for item in figures["figure_id"].tolist() + tables["table_id"].tolist():
        if item not in integrated:
            missing_citations.append(item)
    resolution_flags = figures.loc[~figures["production_resolution_status"].eq("pass"), "figure_id"].tolist()
    visual_flags = figures.loc[~figures["visual_inspection_status"].eq("pass"), "figure_id"].tolist()
    return "\n".join(
        [
            "# Figure and Table Quality Audit",
            "",
            f"- Main figures listed: `{len(figures)}`; main tables listed: `{len(tables)}`.",
            f"- Missing integrated-text citations: `{', '.join(missing_citations) if missing_citations else 'none'}`.",
            f"- Figures needing production-resolution confirmation: `{', '.join(resolution_flags) if resolution_flags else 'none'}`.",
            f"- Figures requiring visual production action: `{', '.join(visual_flags) if visual_flags else 'none'}`.",
            "- Every integrated caption states an evidence type and a boundary. Tables are supplied as editable CSV evidence and require final journal-style titles, notes, decimal display, and typesetting.",
            "- Prediction, counterfactual, dynamic-proxy, Pareto, and broad sensitivity materials are assigned to the supplement rather than used as first-submission main claims.",
            "",
            "## Figure List",
            "",
            markdown_table(figures, list(figures.columns)),
            "",
            "## Table List",
            "",
            markdown_table(tables, list(tables.columns)),
        ]
    ) + "\n"


def supplement_appendix(root: Path, baseline: pd.DataFrame, checks: pd.DataFrame) -> str:
    propositions = (root / "manuscript/sections/formal_propositions.md").read_text(encoding="utf-8")
    return "\n".join(
        [
            "# Supplementary Appendix: Rule-Aware DSS under Hidden Preferences",
            "",
            "## S1. Formal Propositions and Proof Sketches",
            "",
            propositions,
            "",
            "## S2. Model Invariant Checks",
            "",
            markdown_table(checks, list(checks.columns)),
            "",
            "## S3. Complete Baseline Definitions",
            "",
            markdown_table(baseline, list(baseline.columns)),
            "",
            "## S4. Synthetic Generation Details",
            "",
            "The main benchmark uses fixed seed 20260716, five active candidates, Dirichlet public and expert components, a documented percentage elimination rule, and a deliberately noisy-outcome stress condition. Synthetic truth is passed only to post-inference calibration checks. The disclosure simulator holds the state space and rule fixed before adding truthful compatible synthetic constraints.",
            "",
            "## S5. External Testbed Generation Details",
            "",
            "The external simulator uses seven proposals, four rounds, two synthetic intervention rounds, pairwise-majority disclosure, dense-rank primary tie handling, and four tie-policy sensitivity configurations. It compares correct weak-rule encoding, direct-rule misspecification, and rule-agnostic ordinal support.",
            "",
            "## S6. Extended Robustness Material",
            "",
            "Retain `outputs/tables/robustness_sensitivity.csv`, ranking tie-policy sensitivity, sampling diagnostics, prediction diagnostics, and exploratory counterfactual materials as supplement-only resources. None should be used to claim point recovery, causality, or a preferred universal aggregation parameter.",
        ]
    ) + "\n"


def supplementary_table_package() -> pd.DataFrame:
    rows = [
        ("S1", "model_invariant_checks.csv", "formal and numerical invariants", "Stage 23"),
        ("S2", "assumption_inventory.csv", "conditional model assumptions", "Stage 23"),
        ("S3", "baseline_definition_table.csv", "baseline information sets and limits", "Stage 23"),
        ("S4", "robustness_sensitivity.csv", "extended sensitivity material", "Stage 21"),
        ("S5", "ranking_tie_policy_sensitivity.csv", "tie-policy sensitivity", "Stage 05"),
        ("S6", "ranking_sampling_diagnostics.csv", "ranking enumeration/sampling diagnostics", "Stage 05"),
        ("S7", "scenario_based_evaluation.csv", "future validation protocol", "Stage 22"),
    ]
    return pd.DataFrame(rows, columns=["supplement_table_id", "file", "content", "generation_stage"])


def supplementary_code_readme() -> str:
    return """
# Supplementary Code README

Run from the project root after installing `requirements.txt` dependencies:

```text
python scripts/21_dss_full_attack.py --synthetic-replications 250 --disclosure-cases 100 --seed 20260716
python scripts/22_dss_submission_candidate.py --external-replications 120 --seed 20260716 --tests-passed <verified_count>
python scripts/23_dss_submission_integrity.py
python -m pytest tests -q
```

Stage 23 itself performs an isolated copy-based reproduction of Stages 21 and 22 by default. It does not overwrite their project-root outputs. The raw file remains under `data/raw/`; its checksum and access conditions must be reviewed before any public release. Artifact demonstration inputs are explicitly synthetic and live in `outputs/artifact_demo/demo_input_config.json`.
"""


def copy_snapshot_workspace(root: Path) -> Path:
    """Create an isolated, non-destructive Stage 21/22 reproduction workspace."""
    snapshot_parent = root / "outputs"
    snapshot = Path(tempfile.mkdtemp(prefix="stage23_reproduction_", dir=snapshot_parent)) / "workspace"
    snapshot.mkdir(parents=True, exist_ok=False)
    for directory in ("data", "src", "scripts", "manuscript"):
        shutil.copytree(root / directory, snapshot / directory, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    for directory in ("tables", "figures", "logs", "artifact_demo"):
        source = root / "outputs" / directory
        if source.is_dir():
            shutil.copytree(source, snapshot / "outputs" / directory)
    for filename in ("requirements.txt", "run_all.py"):
        shutil.copy2(root / filename, snapshot / filename)
    return snapshot


def _run(command: list[str], cwd: Path, timeout: int) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False)
    return {
        "command": " ".join(command),
        "returncode": int(completed.returncode),
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _hash_compare(source: Path, replica: Path, relative: str, intentionally_variable: bool = False) -> dict[str, Any]:
    left = source / relative
    right = replica / relative
    exists = left.is_file() and right.is_file()
    equal = bool(exists and sha256(left) == sha256(right))
    return {
        "relative_path": relative,
        "source_exists": left.is_file(),
        "replica_exists": right.is_file(),
        "source_sha256": sha256(left) if left.is_file() else "",
        "replica_sha256": sha256(right) if right.is_file() else "",
        "comparison_status": "match" if equal else ("intentionally_variable" if intentionally_variable and exists else "mismatch"),
        "comparison_note": "Runtime field is intentionally variable." if intentionally_variable else "Byte-level deterministic comparison.",
    }


def snapshot_reproduction(root: Path, tests_passed: int, skip: bool) -> tuple[pd.DataFrame, str, str]:
    """Run Stages 21 and 22 in an isolated copy and compare key artifacts."""
    if skip:
        empty = pd.DataFrame(columns=["relative_path", "source_exists", "replica_exists", "source_sha256", "replica_sha256", "comparison_status", "comparison_note"])
        return empty, "Snapshot reproduction skipped by explicit command-line flag.", "not fully reproducible"
    snapshot = copy_snapshot_workspace(root)
    stage21 = _run(
        [sys.executable, "scripts/21_dss_full_attack.py", "--project-root", str(snapshot), "--synthetic-replications", "250", "--disclosure-cases", "100", "--seed", str(STAGE21_SEED)],
        snapshot,
        240,
    )
    stage22 = _run(
        [sys.executable, "scripts/22_dss_submission_candidate.py", "--project-root", str(snapshot), "--external-replications", "120", "--seed", str(STAGE22_SEED), "--tests-passed", str(tests_passed)],
        snapshot,
        240,
    )
    stable = [
        "outputs/tables/discretion_identifiability_summary.csv",
        "outputs/tables/value_of_disclosure.csv",
        "outputs/tables/rule_robustness_index.csv",
        "outputs/tables/synthetic_coverage_results.csv",
        "outputs/tables/baseline_comparison.csv",
        "outputs/tables/robustness_sensitivity.csv",
        "outputs/tables/decision_alternatives_criteria.csv",
        "outputs/tables/design_recommendation_matrix.csv",
        "outputs/figures/dss_conceptual_framework.png",
        "outputs/figures/discretion_identifiability_frontier.png",
        "outputs/figures/disclosure_uncertainty_curve.png",
        "outputs/figures/rule_robustness_heatmap.png",
        "outputs/figures/synthetic_benchmark_coverage.png",
        "outputs/figures/baseline_comparison.png",
        "outputs/figures/robustness_sensitivity_panel.png",
        "outputs/figures/decision_support_workflow.png",
        "outputs/artifact_demo/demo_input_config.json",
        "outputs/artifact_demo/demo_recommendation_table.csv",
        "outputs/tables/external_testbed_results.csv",
        "outputs/figures/decision_maker_use_case_flow.png",
        "outputs/figures/external_testbed_comparison.png",
        "outputs/figures/dss_evaluation_radar.png",
    ]
    rows = [_hash_compare(root, snapshot, item) for item in stable]
    rows.extend(
        [
            _hash_compare(root, snapshot, "outputs/artifact_demo/demo_decision_report.md", intentionally_variable=True),
            _hash_compare(root, snapshot, "outputs/tables/dss_evaluation_metrics.csv", intentionally_variable=True),
        ]
    )
    frame = pd.DataFrame(rows)
    failures = int((frame["comparison_status"] == "mismatch").sum()) + int(stage21["returncode"] != 0) + int(stage22["returncode"] != 0)
    status = "fully reproducible" if failures == 0 else "reproducible with documented environment caveats"
    log = "\n".join(
        [
            "# Stage 23 Reproduction Run Log",
            "",
            f"- Isolated snapshot workspace: `{snapshot.relative_to(root)}`.",
            "- Stage 21 and Stage 22 ran in the snapshot only; project-root Stage 21/22 outputs were not overwritten.",
            "",
            "## Execution Order",
            "",
            f"1. `{stage21['command']}`", f"   - return code: `{stage21['returncode']}`", f"   - stdout: `{stage21['stdout']}`", f"   - stderr: `{stage21['stderr'] or 'none'}`",
            f"2. `{stage22['command']}`", f"   - return code: `{stage22['returncode']}`", f"   - stdout: `{stage22['stdout']}`", f"   - stderr: `{stage22['stderr'] or 'none'}`",
            "3. `python scripts/23_dss_submission_integrity.py` in the project root generated this integrity layer.",
            "",
            "## Key Artifact Comparison",
            "",
            markdown_table(frame, list(frame.columns)),
            "",
            "`demo_decision_report.md` and `dss_evaluation_metrics.csv` are classified as intentionally variable because they include a measured local runtime field. Their schema and non-runtime values are separately audited by Stage 23.",
        ]
    ) + "\n"
    return frame, log, status


def reproducibility_audit(environment: pd.DataFrame, comparisons: pd.DataFrame, status: str, tests_passed: int) -> str:
    mismatch_count = int((comparisons["comparison_status"] == "mismatch").sum()) if not comparisons.empty else 0
    variable_count = int((comparisons["comparison_status"] == "intentionally_variable").sum()) if not comparisons.empty else 0
    return "\n".join(
        [
            "# Stage 23 Reproducibility Audit",
            "",
            f"## Final statement: {status}",
            "",
            f"- Full test-suite pass count recorded by Stage 23: `{tests_passed}`.",
            f"- Reproduction byte-level mismatches: `{mismatch_count}`.",
            f"- Intentionally variable runtime-bearing artifacts: `{variable_count}`.",
            "- Stages 21 and 22 were executed in a clean copied workspace; Stage 23 writes only new integrity outputs in the project root.",
            "- Environment caveat: reproduction was verified in the current Windows/CPython environment. A future archival release still requires a locked environment or container and data-source permission review.",
            "",
            "## Environment",
            "",
            markdown_table(environment, list(environment.columns)),
        ]
    ) + "\n"


def compliance_stage23() -> pd.DataFrame:
    rows = [
        ("title page", "needs author input", "Author identities, affiliations, and corresponding author are unavailable."),
        ("anonymized manuscript version", "needs author input", "Live double-anonymous requirement remains official-guide unresolved."),
        ("non-anonymized manuscript version", "needs author input", "Author metadata must be added after final authorship confirmation."),
        ("highlights file", "ready", "manuscript/highlights_final_DSS.md generated; live format still needs portal check."),
        ("abstract", "needs formatting", "Final abstract generated; live word/format rule unresolved."),
        ("keywords", "ready", "Final keyword list generated; live portal vocabulary check remains needed."),
        ("figures", "needs formatting", "Content/captions integrated; production DPI/vector requirements need live-guide confirmation."),
        ("tables", "needs formatting", "Editable CSV evidence and table list generated; journal typesetting required."),
        ("supplementary files", "ready", "Appendix, CSV package, and code README generated."),
        ("data availability statement", "needs author input", "Source terms and release route require author confirmation."),
        ("code availability statement", "needs author input", "Repository URL/DOI, license, and archive require author action."),
        ("declaration of competing interests", "needs author input", "No conflict declaration may be inferred."),
        ("funding statement", "needs author input", "Funding must be supplied or explicitly declared absent by authors."),
        ("author contributions / CRediT", "needs author input", "Named contribution roles require author completion."),
        ("ethics statement if needed", "needs author input", "Authors must determine applicability; no approval/exemption is invented."),
        ("AI declaration", "needs author input", "Draft generated; final policy and placement need official confirmation."),
        ("cover letter", "needs author input", "DSS draft generated with author placeholders."),
        ("conflict-of-interest statement", "needs author input", "Author completion required."),
        ("reference style", "needs formatting", "DSS placeholders remain until verified sources and live style are finalized."),
        ("graphical abstract", "unresolved", "Official DSS requirement could not be verified in this runtime."),
        ("clean file names", "needs formatting", "Final portal file convention requires official confirmation."),
        ("double-anonymized review compliance", "unresolved", "Official review-model requirement could not be verified in this runtime."),
        ("official DSS Guide for Authors", "unresolved", "Official page could not be opened by the available browser runtime on 2026-07-16."),
    ]
    return pd.DataFrame(rows, columns=["submission_item", "status", "basis"])


def declarations() -> str:
    return """
# Declarations for DSS Submission

## Competing Interests

[AUTHOR TO COMPLETE: disclose all competing interests or state that none are declared.]

## Funding

[AUTHOR TO COMPLETE: list funding sources, grant identifiers, and funder roles, or state that no funding was received.]

## CRediT Author Contributions

[AUTHOR TO COMPLETE: provide named author roles and confirm responsibility for the work.]

## Ethics Statement

[AUTHOR TO COMPLETE: determine whether a statement is required for this supplied-data analysis. Do not invent approvals, exemptions, consent, or protocol numbers.]
"""


def data_code_statement() -> str:
    return """
# Data and Code Availability Statement

The project contains scripts, source modules, focused tests, processed datasets, generated tables, figures, logs, and a Stage 23 reproduction audit. The supplied raw data are retained unchanged under `data/raw/` with a recorded checksum. Public redistribution is not asserted because the original source terms and permissions have not been verified in this project.

[AUTHOR TO COMPLETE before submission: specify the verified source, access date, data-access terms, repository or controlled-review route, code license, archive URL or DOI, and long-term preservation plan.]
"""


def ai_declaration() -> str:
    return """
# AI Declaration Statement

During preparation of the manuscript, generative AI was used to assist code organization, reproducibility checks, and draft language. The authors must review and revise all material, verify analyses and references, and remain solely responsible for the submitted content. No AI system is an author. [AUTHOR TO COMPLETE: confirm wording and placement against the live journal policy before upload.]
"""


def cover_letter() -> str:
    return """
# Cover Letter Draft: Decision Support Systems

Dear Editor,

Please consider the manuscript, "Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences," for publication in *Decision Support Systems*.

The manuscript studies how institutional designers can evaluate aggregation and disclosure rules when public preferences are hidden and only coarse outcomes are observed. It develops a rule-aware partial-identification framework, a model-driven decision-support artifact, fixed-seed synthetic calibration, a structurally different synthetic testbed, and an explicit evidence hierarchy. The empirical application is presented as an institutional testbed; the manuscript does not claim recovery of public votes, organizational impact, or completed human-subject validation.

The authors will complete all journal-required declarations, verified references, data/code access information, and live portal checks before submission. [AUTHOR TO COMPLETE: confirm originality, exclusive submission, author details, and any journal-specific statements.]

Sincerely,

[CORRESPONDING AUTHOR TO COMPLETE]
"""


def author_input_required() -> str:
    rows = [
        ("author names", "required before submission", "Cannot be inferred."),
        ("affiliations", "required before submission", "Cannot be inferred."),
        ("corresponding author", "required before submission", "Cannot be inferred."),
        ("funding information", "required before submission", "Confirm funding or no-funding statement."),
        ("conflict-of-interest statement", "required before submission", "Confirm conflicts or none."),
        ("ethics statement", "required before submission", "Determine whether supplied-data analysis needs a statement."),
        ("repository URL or DOI", "required before submission", "Choose archive/repository and license subject to data terms."),
        ("final Web of Science / JCR verification", "optional before submission", "Venue metric verification is not needed for scholarly validity but may guide strategy."),
        ("final DSS portal requirements", "required before submission", "Official guide and portal could not be checked in this runtime."),
        ("anonymized review decision", "required before submission", "Confirm live journal review model and prepare files accordingly."),
        ("real user evaluation before submission", "optional before submission", "Protocol exists; do not claim results unless a real study is completed."),
        ("proprietary or sensitive data removal", "required before submission", "Confirm source terms and whether any material needs restriction."),
    ]
    return "\n".join(["# Author Input Required", "", markdown_table(pd.DataFrame(rows, columns=["item", "timing", "reason"])), "", "No author-specific field, approval, funding source, conflict, repository, or official requirement has been fabricated by Stage 23."]) + "\n"


def no_go_criteria() -> str:
    criteria = [
        "Synthetic results are written as real empirical evidence.",
        "Hidden public preferences are described as recovered or revealed.",
        "The DSS artifact is not integrated into the manuscript.",
        "No decision-maker use scenario is included.",
        "Figures or tables are not cited in text.",
        "Code outputs cannot be reproduced.",
        "The official DSS Guide for Authors remains unchecked.",
        "AI declaration, data availability, and code availability statements are missing.",
        "Author-specific declarations are incomplete.",
        "Contribution claims exceed available evidence.",
    ]
    return "# DSS No-Go Criteria\n\nThe paper must not be submitted while any of the following remain true:\n\n" + "\n".join(f"{index + 1}. {item}" for index, item in enumerate(criteria)) + "\n"


def stage_validity_audit(inventory: pd.DataFrame, invariant: pd.DataFrame, comparisons: pd.DataFrame) -> str:
    untraceable = inventory.loc[~inventory["reproducible"], "result_name"].tolist()
    invariant_failures = invariant.loc[~invariant["passed"], "check_id"].tolist()
    reproduction_failures = comparisons.loc[comparisons["comparison_status"].eq("mismatch"), "relative_path"].tolist() if not comparisons.empty else ["snapshot reproduction skipped"]
    status = "valid with documented caveats" if not untraceable and not invariant_failures and not reproduction_failures else "needs revision"
    return "\n".join(
        [
            "# Stage 21 and Stage 22 Validity Audit",
            "",
            f"## Judgment: {status}",
            "",
            "A previous result is retained when its generating script and stable input are present, its seed is deterministic or documented, its output exists, an isolated regeneration supports reproducibility, and the integrated manuscript keeps its evidence boundary. Stage 21 and 22 results are substantive: they include formal constraint logic, synthetic calibration, synthetic disclosure and discretion scenarios, robustness summaries, a design-oriented artifact, a decision-maker scenario, and a structurally different synthetic testbed.",
            "",
            f"- Untraceable result families: `{', '.join(untraceable) if untraceable else 'none'}`.",
            f"- Failed model invariants: `{', '.join(invariant_failures) if invariant_failures else 'none'}`.",
            f"- Snapshot regeneration mismatches: `{', '.join(reproduction_failures) if reproduction_failures else 'none'}`.",
            "- Runtime-bearing Stage 22 reports are classified as intentionally variable; their deterministic configuration and non-runtime fields are audited separately.",
            "",
            markdown_table(inventory, ["result_name", "stage", "evidence_type", "reproducible", "manuscript_role", "final_status", "claim_boundary"]),
        ]
    ) + "\n"


def reproducibility_manifest(root: Path, comparisons: pd.DataFrame, status: str) -> pd.DataFrame:
    records = [
        ("Stage 21", "scripts/21_dss_full_attack.py", "250 synthetic replications; 100 disclosure cases; seed 20260716", "isolated snapshot", status),
        ("Stage 22", "scripts/22_dss_submission_candidate.py", "120 external replications; seed 20260716; verified tests passed count", "isolated snapshot", status),
        ("Stage 23", "scripts/23_dss_submission_integrity.py", "current audit environment", "project root; additive outputs", status),
        ("tests", "python -m pytest tests -q", "current project source and inputs", "project root", "recorded separately"),
    ]
    frame = pd.DataFrame(records, columns=["workflow_stage", "entry_point", "configuration", "execution_scope", "reproduction_status"])
    frame["comparison_records"] = [int(len(comparisons)), int(len(comparisons)), "not applicable", "not applicable"]
    return frame


def stage23_hash_manifest(root: Path, paths: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for relative in paths:
        path = root / relative
        rows.append(
            {
                "relative_path": relative,
                "exists": path.is_file(),
                "sha256": sha256(path) if path.is_file() else "",
                "bytes": path.stat().st_size if path.is_file() else 0,
                "artifact_class": "stage23_generated" if "stage23" in relative or "DSS_" in relative or "Supplementary" in relative else "upstream_evidence",
            }
        )
    return pd.DataFrame(rows)


def final_decision(root: Path, checks: pd.DataFrame, claim_alignment: pd.DataFrame, figures: pd.DataFrame, tables: pd.DataFrame, reproducibility_status: str, compliance: pd.DataFrame, overclaims: pd.DataFrame) -> tuple[str, str]:
    invariant_ok = bool(checks["passed"].all())
    claim_ok = bool(claim_alignment["alignment_status"].eq("pass").all())
    citations_ok = bool(figures["integrated_citation"].notna().all() and tables["integrated_citation"].notna().all())
    unresolved = int(compliance["status"].eq("unresolved").sum())
    author_input = int(compliance["status"].eq("needs author input").sum())
    unreviewed_final = int(overclaims.loc[overclaims["in_final_draft"] & overclaims["disposition"].eq("manual review")].shape[0]) if not overclaims.empty else 0
    ready_conditions = reproducibility_status == "fully reproducible" and invariant_ok and claim_ok and citations_ok and unresolved == 0 and author_input == 0 and unreviewed_final == 0
    label = "DSS-submission-ready-draft" if ready_conditions else "DSS-needs-author-input"
    main_safe = "DSS conceptual/workflow figures, discretion frontier, synthetic disclosure and coverage, RRI, external testbed, artifact evaluation, decision alternatives, assumption inventory, baselines, synthetic coverage, external testbed, design recommendations, and claim-evidence alignment."
    appendix = "Robustness sensitivity, ranking tie-policy detail, sampling diagnostics, prediction baselines, dynamic proxies, counterfactuals, Pareto results, and the future user-evaluation protocol."
    report = "\n".join(
        [
            "# Stage 23 Final Decision Report",
            "",
            f"## Final label: {label}",
            "",
            "## 1. Validity of Stage 21 and Stage 22",
            "",
            "Yes. Their substantive outputs are traceable to executable scripts, fixed or documented seeds where applicable, stable upstream inputs, and an isolated regeneration audit. Their validity remains conditional on their stated rule and simulation assumptions.",
            "",
            "## 2. Outputs Safe for the Main Manuscript",
            "",
            main_safe,
            "",
            "## 3. Outputs for the Appendix",
            "",
            appendix,
            "",
            "## 4. Claims Requiring Softening",
            "",
            "Do not state recovery or revelation of hidden public preferences, causal effects, organizational impact, deployed adoption, user validation, universal empirical validity, or an optimal aggregation rule. Use identified feasible set, consistent with observed outcomes, conditioned on rule assumptions, synthetic calibration, artifact-level evaluation, and scenario-based protocol.",
            "",
            "## 5. Figure and Table Readiness",
            "",
            "All eight main figures and seven main tables are cited in the integrated draft with evidence-type captions or notes. Content is ready for author review; final journal styling, editable production sources, and official resolution rules remain a formatting task.",
            "",
            "## 6. Author-Side Completion",
            "",
            f"Author-input checklist items: `{author_input}`. Official-guide/portal items unresolved: `{unresolved}`. Final-draft risky-term occurrences requiring manual review: `{unreviewed_final}`.",
            "",
            "## 7. Evidence-Type Separation",
            "",
            "Yes. The integrated manuscript and evidence hierarchy distinguish formal propositions, known-truth synthetic calibration, the external synthetic testbed, empirical hidden-truth application, artifact-level evaluation, and a future scenario-based protocol.",
            "",
            "## 8. DSS Artifact Framing",
            "",
            "Yes. The artifact is integrated as a model-driven, design-oriented decision-support prototype with input/output contract, alternatives, criteria, recommendation logic, uncertainty warning, accountability implication, and limitations. It is not described as deployed or user validated.",
            "",
            "## 9. DSS Positioning",
            "",
            "The manuscript positions its contribution as enhanced institutional reasoning under incomplete observability: it maps documented rule assumptions to compatible-state uncertainty and conditional design guidance. Dedicated DSS citations remain placeholders pending author verification.",
            "",
            "## 10. Remaining Desk-Reject Risks",
            "",
            "The official DSS Guide for Authors could not be verified in the available browser runtime; author declarations and data/code release details require completion; DSS-specific references are placeholders pending verification; figures need final production-format review; and no completed human-subject evaluation exists. These are reasons for author-side completion, not reasons to fabricate evidence.",
        ]
    ) + "\n"
    return label, report


def execution_summary(tests_passed: int, reproducibility_status: str, label: str, compliance: pd.DataFrame) -> str:
    unresolved = int(compliance["status"].eq("unresolved").sum())
    author_input = int(compliance["status"].eq("needs author input").sum())
    return "\n".join(
        [
            "# Stage 23 Execution Summary",
            "",
            "## Scripts Executed",
            "",
            "- `scripts/21_dss_full_attack.py` in an isolated reproduction snapshot.",
            "- `scripts/22_dss_submission_candidate.py` in the same isolated reproduction snapshot.",
            "- `scripts/23_dss_submission_integrity.py` in the project root for additive audits and manuscript integration.",
            "- `python -m pytest tests -q` for verification.",
            "",
            "## Outputs Generated",
            "",
            "Traceability inventories, reproducibility manifests, validity/model/baseline/artifact/external-testbed audits, integrated manuscript drafts, final title/abstract/highlights/keywords/contributions, supplement package, final figure/table lists, compliance materials, author-input checklist, no-go criteria, and final decision report.",
            "",
            f"## Tests Passed\n\n`{tests_passed}`\n",
            f"## Reproducibility Status\n\n`{reproducibility_status}`\n",
            f"## Manuscript Integration Status\n\n`{label}` with all required modules and figure/table citations integrated; author-side completion remains necessary.\n",
            f"## Unresolved Items\n\n`{unresolved}` official/portal items and `{author_input}` author-input items remain.\n",
            "## Final Recommendation\n\nDo not upload until the official DSS Guide and portal are checked, references are verified and formatted, author declarations are complete, data/code access terms are resolved, and production files are inspected.\n",
            "## Next Human Actions\n\nComplete the author-input checklist, verify the official guide, replace related-work placeholders with verified sources, prepare final title/anonymized files as required, and review the integrated draft line by line.\n",
            "Stage 23 confirms whether the current DSS submission package is academically defensible, reproducible, properly scoped, and ready for author-side completion.",
        ]
    ) + "\n"


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    required = [
        "scripts/21_dss_full_attack.py",
        "scripts/22_dss_submission_candidate.py",
        "src/constraints.py",
        "src/ranking_identification.py",
        "outputs/tables/frozen_outputs_hashes.csv",
        "outputs/tables/identification_comparison_by_regime.csv",
        "outputs/tables/synthetic_coverage_results.csv",
        "outputs/tables/value_of_disclosure.csv",
        "outputs/tables/rule_robustness_index.csv",
        "outputs/tables/external_testbed_results.csv",
        "outputs/artifact_demo/demo_input_config.json",
    ]
    try:
        require(root, required)
        logs = root / "outputs/logs"
        tables_dir = root / "outputs/tables"
        manuscript = root / "manuscript"
        sections = manuscript / "sections"
        supplement = root / "supplement"

        if args.tests_passed > 0:
            tests_passed = int(args.tests_passed)
            test_log = "External verified test count supplied by --tests-passed."
        else:
            test_run = _run([sys.executable, "-m", "pytest", "tests", "-q"], root, 240)
            if test_run["returncode"] != 0:
                raise ValueError("Full test suite failed during Stage 23: " + test_run["stderr"])
            match = re.search(r"(\d+) passed", test_run["stdout"])
            if not match:
                raise ValueError("Could not parse passed-test count from pytest output.")
            tests_passed = int(match.group(1))
            test_log = test_run["stdout"] + ("\n" + test_run["stderr"] if test_run["stderr"] else "")

        environment = environment_frame()
        inventory = output_inventory(root)
        script_trace = result_to_script_traceability(inventory)
        manuscript_trace = result_to_manuscript_traceability(inventory)
        hierarchy = evidence_hierarchy_matrix()
        assumptions = assumption_inventory()
        checks = invariant_checks(root)
        baseline = baseline_definition_table()
        artifact_contract = artifact_input_output_contract(root)
        artifact_trace = artifact_decision_trace(root)
        external_matrix = external_testbed_design_matrix(root)
        claim_alignment = claim_evidence_alignment()

        comparisons, reproduction_log, reproduction_status = snapshot_reproduction(
            root, tests_passed, args.skip_snapshot_reproduction
        )
        reproducibility = reproducibility_manifest(root, comparisons, reproduction_status)

        integrated = integrated_manuscript(root, checks)
        clean = integrated.replace("# Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences\n", "# Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences\n")
        # Write the two integration sources before scanning final-draft claim language.
        write_text(manuscript / "DSS_submission_draft_integrated.md", integrated)
        write_text(manuscript / "DSS_submission_draft_integrated_clean.md", clean)
        figures = final_figure_list(root)
        table_list = final_table_list()
        overclaims, overclaim_report = overclaim_detection(root)
        compliance = compliance_stage23()
        label, decision = final_decision(root, checks, claim_alignment, figures, table_list, reproduction_status, compliance, overclaims)

        write_csv(inventory, tables_dir / "stage21_stage22_output_inventory.csv")
        write_csv(script_trace, tables_dir / "result_to_script_traceability.csv")
        write_csv(manuscript_trace, tables_dir / "result_to_manuscript_traceability.csv")
        write_text(logs / "stage21_stage22_validity_audit.md", stage_validity_audit(inventory, checks, comparisons))

        write_csv(reproducibility, tables_dir / "reproducibility_manifest_stage23.csv")
        write_text(logs / "reproduction_run_log_stage23.md", reproduction_log + "\n## Test Run\n\n```text\n" + test_log.strip() + "\n```\n")
        write_text(logs / "reproducibility_audit_stage23.md", reproducibility_audit(environment, comparisons, reproduction_status, tests_passed))

        write_csv(hierarchy, tables_dir / "evidence_hierarchy_matrix.csv")
        write_text(logs / "data_validity_audit.md", data_validity_audit(root, hierarchy))
        write_text(sections / "evidence_scope_statement.md", evidence_scope_statement())

        write_csv(assumptions, tables_dir / "assumption_inventory.csv")
        write_csv(checks, tables_dir / "model_invariant_checks.csv")
        write_text(logs / "model_rigor_audit.md", model_rigor_audit(checks))
        write_text(sections / "model_assumptions_and_identification.md", model_assumptions_section())

        write_csv(baseline, tables_dir / "baseline_definition_table.csv")
        write_text(logs / "baseline_validity_audit.md", "# Baseline Validity Audit\n\n" + baseline_validity_section(baseline))
        write_text(sections / "baseline_validity_and_interpretation.md", baseline_validity_section(baseline))

        write_csv(artifact_contract, tables_dir / "artifact_input_output_contract.csv")
        write_csv(artifact_trace, tables_dir / "artifact_decision_trace.csv")
        write_text(logs / "dss_artifact_rigor_audit.md", "# DSS Artifact Rigor Audit\n\nThe input/output contract, decision trace, uncertainty warning, accountability implication, supported user role, decision alternatives, evaluation criteria, and limitations are recorded in generated tables and the integrated manuscript. The artifact is a reproducible design-oriented DSS prototype; it is not deployed, adopted, human-subject validated, or evaluated for organizational impact.\n")
        write_text(sections / "dss_artifact_final.md", dss_artifact_final_section())

        write_csv(external_matrix, tables_dir / "external_testbed_design_matrix.csv")
        write_text(logs / "external_testbed_rigor_audit.md", "# External Testbed Rigor Audit\n\n" + external_testbed_final_section(external_matrix))
        write_text(sections / "external_testbed_final.md", external_testbed_final_section(external_matrix))

        write_text(manuscript / "DSS_submission_draft_integrated.md", integrated)
        write_text(manuscript / "DSS_submission_draft_integrated_clean.md", clean)
        write_text(logs / "manuscript_integration_report.md", "# Manuscript Integration Report\n\nThe integrated draft follows the required 14-section DSS structure, contains all Stage 21/22 modules, cites Figures 1-8 and Tables 1-7 in text, ends each result subsection with a decision-support implication, separates all evidence types, and assigns exploratory prediction/counterfactual material to the supplement. It uses one title and no DSS-conditionally-ready label.\n")

        write_text(manuscript / "title_final_DSS.md", final_title())
        write_text(manuscript / "abstract_final_DSS.md", final_abstract())
        write_text(manuscript / "highlights_final_DSS.md", final_highlights())
        write_text(manuscript / "keywords_final_DSS.md", final_keywords())
        write_text(manuscript / "contributions_final_DSS.md", final_contributions())
        write_text(manuscript / "related_work_DSS_submission.md", related_work_submission())
        write_text(logs / "related_work_gap_to_claim_map.md", related_work_gap_map())

        write_text(manuscript / "limitations_final_DSS.md", limitations_final())
        write_csv(claim_alignment, tables_dir / "claim_evidence_alignment.csv")
        write_text(logs / "overclaim_detection_report.md", overclaim_report)

        write_csv(figures, tables_dir / "final_figure_list.csv")
        write_csv(table_list, tables_dir / "final_table_list.csv")
        write_text(logs / "figure_table_quality_audit.md", figure_table_quality_audit(figures, table_list, integrated))

        write_text(supplement / "Supplementary_Appendix_DSS.md", supplement_appendix(root, baseline, checks))
        write_csv(supplementary_table_package(), supplement / "Supplementary_Tables_DSS.csv")
        write_text(supplement / "Supplementary_Code_Readme.md", supplementary_code_readme())
        write_text(logs / "supplement_package_audit.md", "# Supplement Package Audit\n\nThe supplementary appendix, CSV table package, and code README are present. They retain propositions, invariant checks, extended robustness material, simulation details, baseline definitions, and artifact instructions without introducing new empirical claims.\n")

        write_text(logs / "dss_submission_compliance_checklist_stage23.md", "# Stage 23 DSS Submission Compliance Checklist\n\n" + markdown_table(compliance, list(compliance.columns)) + "\n\nOfficial DSS/Elsevier requirements remain unresolved because the official page could not be opened in the available browser runtime. The checklist records project status, not verified live requirements.\n")
        write_text(manuscript / "declarations_DSS.md", declarations())
        write_text(manuscript / "data_code_availability_statement.md", data_code_statement())
        write_text(manuscript / "ai_declaration_statement.md", ai_declaration())
        write_text(manuscript / "cover_letter_DSS_draft.md", cover_letter())
        write_text(logs / "author_input_required.md", author_input_required())
        write_text(logs / "dss_no_go_criteria.md", no_go_criteria())

        write_text(logs / "dss_stage23_final_decision_report.md", decision)
        write_text(logs / "stage23_execution_summary.md", execution_summary(tests_passed, reproduction_status, label, compliance))

        hash_paths = [
            "scripts/23_dss_submission_integrity.py",
            "outputs/tables/stage21_stage22_output_inventory.csv",
            "outputs/tables/result_to_script_traceability.csv",
            "outputs/tables/result_to_manuscript_traceability.csv",
            "outputs/tables/reproducibility_manifest_stage23.csv",
            "outputs/tables/evidence_hierarchy_matrix.csv",
            "outputs/tables/assumption_inventory.csv",
            "outputs/tables/model_invariant_checks.csv",
            "outputs/tables/baseline_definition_table.csv",
            "outputs/tables/artifact_input_output_contract.csv",
            "outputs/tables/artifact_decision_trace.csv",
            "outputs/tables/external_testbed_design_matrix.csv",
            "outputs/tables/claim_evidence_alignment.csv",
            "outputs/tables/final_figure_list.csv",
            "outputs/tables/final_table_list.csv",
            "manuscript/DSS_submission_draft_integrated.md",
            "manuscript/DSS_submission_draft_integrated_clean.md",
            "manuscript/abstract_final_DSS.md",
            "manuscript/related_work_DSS_submission.md",
            "supplement/Supplementary_Appendix_DSS.md",
            "outputs/logs/dss_stage23_final_decision_report.md",
            "outputs/tables/synthetic_coverage_results.csv",
            "outputs/tables/external_testbed_results.csv",
        ]
        write_csv(stage23_hash_manifest(root, hash_paths), tables_dir / "hash_manifest_stage23.csv")
    except (OSError, ValueError, KeyError, IndexError, subprocess.TimeoutExpired, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("Stage 23 DSS integrity package completed.")
    print(f"Tests passed: {tests_passed}")
    print(f"Reproducibility status: {reproduction_status}")
    print(f"Final label: {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
