"""File-facing helpers for the lightweight operational DSS cockpit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from src.dss_artifact import ArtifactConfig, ArtifactResult, config_from_mapping, config_to_mapping, evaluate_artifact_config


def load_config(path: Path) -> ArtifactConfig:
    """Load and validate a portable JSON decision-artifact configuration."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc.msg}.") from exc
    return config_from_mapping(payload)


def default_demo_payload() -> dict[str, Any]:
    """Return a transparent synthetic demonstration, not an empirical replay."""
    return {
        "artifact_label": "illustrative synthetic institutional-design demonstration; not empirical evidence",
        "observed_elimination_outcomes": [
            {
                "round_id": "illustrative_round_1",
                "active_candidates": ["Atlas", "Birch", "Cedar", "Delta", "Ember"],
                "eliminated_candidates": ["Ember"],
                "expert_scores": {"Atlas": 8.9, "Birch": 8.0, "Cedar": 7.6, "Delta": 7.3, "Ember": 6.8},
                "outcome_type": "elimination",
                "finale_order": [],
            },
            {
                "round_id": "illustrative_round_2_multiple_elimination",
                "active_candidates": ["Atlas", "Birch", "Cedar", "Delta"],
                "eliminated_candidates": ["Cedar", "Delta"],
                "expert_scores": {"Atlas": 9.0, "Birch": 8.4, "Cedar": 7.2, "Delta": 7.1},
                "outcome_type": "elimination",
                "finale_order": [],
            },
        ],
        "aggregation_rule_type": "percentage",
        "judge_save_assumption": "not_applicable",
        "tie_handling_assumption": "tie_inclusive",
        "disclosure_regime": "vote_bin_intervals",
        "decision_objective": "reduce_uncertainty",
        "enumeration_cap": 8,
        "sampling_draws": 10000,
        "random_seed": 20260716,
    }


def evaluate_payload(
    payload: Mapping[str, Any],
    *,
    rule_robustness: pd.DataFrame | None = None,
) -> tuple[ArtifactConfig, ArtifactResult]:
    """Validate a cockpit payload and calculate its conditional output."""
    config = config_from_mapping(payload)
    return config, evaluate_artifact_config(config, rule_robustness=rule_robustness)


def markdown_report(config: ArtifactConfig, result: ArtifactResult) -> str:
    """Create a concise, auditable decision report for one cockpit run."""
    summary = result.summary
    table = result.round_results.copy()
    table["feasible_set_width"] = table["feasible_set_width"].map(
        lambda value: "" if pd.isna(value) else f"{float(value):.3f}"
    )
    lines = [
        "# DSS Artifact Demonstration Report",
        "",
        "## Scope",
        "",
        f"`{config.artifact_label}`",
        "",
        "This is an operational, configuration-driven demonstration. The supplied labels and scores are illustrative synthetic inputs, not a replay of the empirical testbed and not evidence of recovered public preferences.",
        "",
        "## Recorded Inputs",
        "",
        f"- Aggregation rule: `{summary['aggregation_rule_type']}`.",
        f"- Judge-save assumption: `{summary['judge_save_assumption']}`.",
        f"- Tie-handling assumption: `{summary['tie_handling_assumption']}`.",
        f"- Disclosure regime: `{summary['disclosure_regime']}`.",
        f"- Decision objective: `{summary['decision_objective']}`.",
        f"- Documented rounds: `{summary['n_documented_rounds']}`; feasible rounds: `{summary['n_feasible_rounds']}`.",
        "",
        "## Conditional Decision Output",
        "",
        f"- Feasible-set width: `{summary['feasible_set_width']:.3f}` (mean across feasible documented rounds; mechanism-specific units).",
        f"- Uncertainty class: `{summary['uncertainty_class']}`.",
        f"- Rule robustness label: `{summary['rule_robustness_label']}`.",
        f"- Disclosure recommendation: {summary['disclosure_recommendation']}",
        f"- Design warning: {summary['design_warning']}",
        f"- Accountability implication: {summary['accountability_implication']}",
        "",
        "## Round-Level Audit",
        "",
        table.to_markdown(index=False),
        "",
        "## Interpretation Boundary",
        "",
        summary["evidence_boundary"],
    ]
    return "\n".join(lines) + "\n"


def config_json(config: ArtifactConfig) -> str:
    """Serialize a configuration with stable, human-readable formatting."""
    return json.dumps(config_to_mapping(config), ensure_ascii=True, indent=2, sort_keys=False) + "\n"
