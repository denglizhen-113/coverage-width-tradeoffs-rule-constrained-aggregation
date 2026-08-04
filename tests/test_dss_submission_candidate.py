"""Focused tests for the operational DSS submission-candidate stage."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from src.dss_artifact import ArtifactInputError
from src.dss_decision_cockpit import default_demo_payload, evaluate_payload
from src.external_testbed import run_external_testbed


def _ranking_payload(rule: str, judge_save: str) -> dict[str, object]:
    return {
        "artifact_label": "test configuration",
        "observed_elimination_outcomes": [
            {
                "round_id": "round_1",
                "active_candidates": ["A", "B", "C", "D"],
                "eliminated_candidates": ["D"],
                "expert_scores": {"A": 9.0, "B": 8.0, "C": 7.0, "D": 6.0},
                "outcome_type": "elimination",
                "finale_order": [],
            }
        ],
        "aggregation_rule_type": rule,
        "judge_save_assumption": judge_save,
        "tie_handling_assumption": "tie_inclusive",
        "disclosure_regime": "pairwise_majority",
        "decision_objective": "reduce_uncertainty",
    }


def test_percentage_demo_solves_a_bounded_feasible_set() -> None:
    _, result = evaluate_payload(default_demo_payload(), rule_robustness=pd.DataFrame())
    assert result.round_results["feasible"].all()
    assert 0.0 <= result.summary["feasible_set_width"] <= 1.0
    assert result.summary["uncertainty_class"] == "broad_conditional_interval"


def test_weak_judge_save_does_not_shrink_the_direct_ranking_set() -> None:
    _, direct = evaluate_payload(_ranking_payload("ranking", "none"))
    _, weak = evaluate_payload(_ranking_payload("ranking_plus_judge_save", "weak_bottom_set"))
    assert weak.summary["feasible_set_width"] >= direct.summary["feasible_set_width"] - 1e-12


@pytest.mark.parametrize("outcome_type", ["no_elimination", "withdrawal"])
def test_noncomparative_rounds_preserve_simplex_only_width(outcome_type: str) -> None:
    payload = default_demo_payload()
    payload["observed_elimination_outcomes"] = [
        {
            "round_id": outcome_type,
            "active_candidates": ["A", "B", "C"],
            "eliminated_candidates": [],
            "expert_scores": {"A": 8.0, "B": 7.0, "C": 6.0},
            "outcome_type": outcome_type,
            "finale_order": [],
        }
    ]
    _, result = evaluate_payload(payload)
    assert result.round_results.iloc[0]["constraint_count"] == 0
    assert math.isclose(float(result.summary["feasible_set_width"]), 1.0, abs_tol=1e-12)


def test_finale_order_is_supported_only_when_complete() -> None:
    payload = default_demo_payload()
    payload["observed_elimination_outcomes"] = [
        {
            "round_id": "finale",
            "active_candidates": ["A", "B", "C"],
            "eliminated_candidates": [],
            "expert_scores": {"A": 9.0, "B": 8.0, "C": 7.0},
            "outcome_type": "finale",
            "finale_order": ["A", "B", "C"],
        }
    ]
    _, result = evaluate_payload(payload)
    assert result.round_results.iloc[0]["constraint_count"] == 2
    assert result.round_results.iloc[0]["feasible"]


def test_nonfinite_expert_score_is_rejected_without_coercion() -> None:
    payload = default_demo_payload()
    payload["observed_elimination_outcomes"][0]["expert_scores"]["Atlas"] = float("nan")
    with pytest.raises(ArtifactInputError, match="finite"):
        evaluate_payload(payload)


def test_external_testbed_keeps_known_truth_under_the_correct_rule() -> None:
    results = run_external_testbed(n_replications=12, seed=20260716).set_index("method")
    assert results.loc["rule_aware_discretion", "coverage_rate"] == 1.0
    assert results.loc["direct_rule_misspecification", "false_certainty_rate"] > 0.0
    assert results["recommendation_stability"].between(0.0, 1.0).all()
