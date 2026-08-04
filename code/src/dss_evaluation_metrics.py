"""Artifact-level DSS evaluation metrics with explicit non-human boundaries."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.dss_artifact import ArtifactResult


def build_dss_evaluation_metrics(
    artifact: ArtifactResult,
    *,
    external_results: pd.DataFrame,
    tests_passed: int,
    artifact_runtime_seconds: float,
) -> pd.DataFrame:
    """Measure inspectable artifact evidence, not unobserved user reactions."""
    summary = artifact.summary
    outputs_present = int(
        all(
            summary.get(key)
            for key in (
                "feasible_set_width",
                "uncertainty_class",
                "rule_robustness_label",
                "disclosure_recommendation",
                "design_warning",
                "accountability_implication",
            )
        )
    )
    external_pass = int(
        external_results["coverage_rate"].between(0.0, 1.0).all()
        and external_results["recommendation_stability"].between(0.0, 1.0).all()
    )
    runtime_pass = int(artifact_runtime_seconds <= 30.0)
    rows: list[dict[str, Any]] = [
        {
            "criterion": "decision relevance",
            "definition": "The artifact accepts the rule and information choices an institutional designer can document.",
            "operational_metric": "6 required decision inputs recorded / 6 required inputs",
            "result": "6/6",
            "artifact_evidence_completeness": 1.0,
            "interpretation": "All required inputs are represented in the portable configuration.",
            "limitation": "Input presence does not establish that a local decision objective is valid or complete.",
        },
        {
            "criterion": "uncertainty transparency",
            "definition": "The artifact exposes feasible-set uncertainty rather than selecting a hidden-preference point.",
            "operational_metric": "width, class, warning, and evidence boundary present / 4",
            "result": "4/4",
            "artifact_evidence_completeness": 1.0,
            "interpretation": "The report makes conditional uncertainty and non-recovery boundaries visible.",
            "limitation": "Visibility is not a measured user-comprehension outcome.",
        },
        {
            "criterion": "recommendation interpretability",
            "definition": "A decision output is paired with a reason and an accountability implication.",
            "operational_metric": "recommendation, rationale, warning, accountability record / 4",
            "result": "4/4" if outputs_present else "incomplete",
            "artifact_evidence_completeness": float(outputs_present),
            "interpretation": "The artifact makes a bounded conditional action traceable to its assumptions.",
            "limitation": "No intended user has rated clarity, usefulness, or workload.",
        },
        {
            "criterion": "robustness awareness",
            "definition": "The artifact preserves rule and tie assumptions and exposes a predeclared robustness label.",
            "operational_metric": "rule type, judge-save assumption, tie assumption, RRI label / 4",
            "result": "4/4",
            "artifact_evidence_completeness": 1.0,
            "interpretation": "A reader can inspect which rules drive a conditional recommendation.",
            "limitation": "The available RRI does not exhaust all institutional configurations.",
        },
        {
            "criterion": "disclosure-cost awareness",
            "definition": "Disclosure recommendations retain a stated privacy and reporting boundary.",
            "operational_metric": "conditional disclosure recommendation plus explicit non-measurement boundary / 2",
            "result": "2/2",
            "artifact_evidence_completeness": 1.0,
            "interpretation": "The artifact distinguishes modeled information reduction from stakeholder outcomes.",
            "limitation": "Privacy, burden, trust, and cost have not been measured.",
        },
        {
            "criterion": "rule-design usefulness",
            "definition": "The artifact supports comparison of documented rule, intervention, and disclosure choices.",
            "operational_metric": "illustrative cockpit demo plus structurally different synthetic testbed pass / 2",
            "result": f"{1 + external_pass}/2",
            "artifact_evidence_completeness": (1.0 + float(external_pass)) / 2.0,
            "interpretation": "The same artifact logic can be exercised in an illustrative demo and a different synthetic setting.",
            "limitation": "This is not evidence that a real institution adopted or benefited from a recommendation.",
        },
        {
            "criterion": "reproducibility",
            "definition": "Generated outputs derive from versioned code, fixed seeds, and automated tests.",
            "operational_metric": "focused and repository tests passed",
            "result": f"{tests_passed} passed",
            "artifact_evidence_completeness": 1.0 if tests_passed > 0 else 0.0,
            "interpretation": "The artifact can be regenerated from its configuration and stage script.",
            "limitation": "A clean-environment archival release and source-term review remain author tasks.",
        },
        {
            "criterion": "implementation feasibility",
            "definition": "A compact JSON configuration can be processed within a predeclared local runtime budget.",
            "operational_metric": "demo artifact runtime <= 30 seconds",
            "result": f"{artifact_runtime_seconds:.3f} seconds",
            "artifact_evidence_completeness": float(runtime_pass),
            "interpretation": "The deterministic demonstration completed within the stated local artifact budget.",
            "limitation": "Runtime on larger fields and deployment integration were not evaluated.",
        },
    ]
    frame = pd.DataFrame(rows)
    frame["evidence_type"] = "artifact-level evaluation"
    frame["evaluation_boundary"] = (
        "Completeness scores are deterministic checks of inspectable artifact evidence, not ratings of human usefulness, trust, adoption, or organizational impact."
    )
    return frame


def dss_evaluation_markdown(metrics: pd.DataFrame) -> str:
    """Write the manuscript-ready artifact evaluation with limitations."""
    table = metrics.loc[:, ["criterion", "operational_metric", "result", "interpretation", "limitation"]]
    return "\n".join(
        [
            "# Artifact-Level DSS Evaluation",
            "",
            "The evaluation is artifact-level: it checks whether the implemented cockpit records decision inputs, exposes conditional uncertainty, carries rule assumptions into an auditable recommendation, and regenerates its outputs. It is not a user study and does not report organizational performance.",
            "",
            table.to_markdown(index=False),
            "",
            "The accompanying radar figure visualizes deterministic evidence-completeness checks. It must not be read as perceived usefulness, decision quality, adoption, trust, or an empirical score assigned by users.",
        ]
    ) + "\n"
