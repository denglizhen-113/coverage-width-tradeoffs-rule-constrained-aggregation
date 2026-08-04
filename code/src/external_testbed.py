"""A structurally different synthetic institutional testbed for the DSS artifact.

This module simulates a multi-round community-grant prioritization setting.
It is intentionally not an additional empirical dataset.  Known synthetic
latent rankings are used only to audit calibration under the stated mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Any

import numpy as np
import pandas as pd

from src.dss_artifact import ArtifactRound, _ordinal_mask
from src.ranking_identification import compute_judge_ranks, orders_to_fan_ranks


EXTERNAL_SETTING = "synthetic community-grant prioritization panel"
PRIMARY_TIE_POLICY = "dense_rank"
TIE_SENSITIVITY_POLICIES = ("average_rank", "min_rank", "dense_rank", "competition_rank")


@dataclass(frozen=True)
class ExternalCase:
    """One synthetic multi-round institutional decision process."""

    rounds: tuple[ArtifactRound, ...]
    public_ranks: tuple[np.ndarray, ...]
    intervention_rounds: tuple[bool, ...]


def _case(rng: np.random.Generator, *, n_candidates: int = 7, n_rounds: int = 4) -> ExternalCase:
    """Generate a known-truth, intervention-aware ordinal decision process."""
    if n_candidates < n_rounds + 3:
        raise ValueError("n_candidates must leave at least three candidates after the final simulated round.")
    labels = [f"Proposal_{index + 1}" for index in range(n_candidates)]
    public = rng.dirichlet(np.full(n_candidates, 1.4, dtype=float))
    active_indices = list(range(n_candidates))
    rounds: list[ArtifactRound] = []
    public_ranks: list[np.ndarray] = []
    interventions: list[bool] = []
    for round_index in range(n_rounds):
        active_public = public[active_indices]
        active_labels = [labels[index] for index in active_indices]
        independent_expert = rng.dirichlet(np.full(len(active_indices), 1.1, dtype=float))
        expert = 0.42 * (active_public / active_public.sum()) + 0.58 * independent_expert
        # Rounding creates documented score ties in a subset of simulations.
        expert_scores = np.round(100.0 * expert, 0)
        judge_ranks = compute_judge_ranks(expert_scores, PRIMARY_TIE_POLICY)
        public_order = np.argsort(-active_public, kind="stable").reshape(1, -1)
        true_ranks = orders_to_fan_ranks(public_order).astype(float)[0]
        combined = true_ranks + judge_ranks
        intervention = round_index in {1, 3}
        ordered_worst_first = np.argsort(-combined, kind="stable")
        eliminated_position = 1 if intervention else 0
        eliminated_index = int(ordered_worst_first[eliminated_position])
        eliminated_label = active_labels[eliminated_index]
        rounds.append(
            ArtifactRound(
                round_id=f"grant_round_{round_index + 1}",
                active_candidates=tuple(active_labels),
                eliminated_candidates=(eliminated_label,),
                expert_scores={name: float(score) for name, score in zip(active_labels, expert_scores)},
                outcome_type="elimination",
                finale_order=(),
            )
        )
        public_ranks.append(true_ranks)
        interventions.append(intervention)
        del active_indices[eliminated_index]
    return ExternalCase(tuple(rounds), tuple(public_ranks), tuple(interventions))


def _all_fan_ranks(n_active: int) -> np.ndarray:
    orders = np.asarray(list(permutations(range(n_active))), dtype=np.int16)
    return orders_to_fan_ranks(orders).astype(float)


def _width(fan_ranks: np.ndarray) -> float:
    if len(fan_ranks) == 0:
        return float("nan")
    n_active = fan_ranks.shape[1]
    widths = [float(fan_ranks[:, column].max() - fan_ranks[:, column].min()) for column in range(n_active)]
    return float(np.mean(widths) / (n_active - 1)) if n_active > 1 else 0.0


def _method_mask(
    method: str,
    fan_ranks: np.ndarray,
    judge_ranks: np.ndarray,
    round_input: ArtifactRound,
    intervention: bool,
) -> np.ndarray:
    if method == "rule_agnostic_ordinal":
        return np.ones(len(fan_ranks), dtype=bool)
    if method == "rule_aware_discretion":
        return _ordinal_mask(fan_ranks, judge_ranks, round_input, weak=intervention)
    if method == "direct_rule_misspecification":
        return _ordinal_mask(fan_ranks, judge_ranks, round_input, weak=False)
    raise ValueError(f"Unknown external-testbed method: {method}")


def _disclosure_mask(fan_ranks: np.ndarray, true_ranks: np.ndarray) -> np.ndarray:
    """Apply a synthetic pairwise-majority disclosure between top two priorities."""
    ordered = np.argsort(true_ranks, kind="stable")
    top, runner_up = int(ordered[0]), int(ordered[1])
    return fan_ranks[:, top] < fan_ranks[:, runner_up]


def _round_metrics(
    method: str,
    round_input: ArtifactRound,
    true_ranks: np.ndarray,
    intervention: bool,
    tie_policy: str,
) -> dict[str, Any]:
    score_values = np.asarray([round_input.expert_scores[name] for name in round_input.active_candidates], dtype=float)
    judge_ranks = compute_judge_ranks(score_values, tie_policy)
    fan_ranks = _all_fan_ranks(len(round_input.active_candidates))
    mask = _method_mask(method, fan_ranks, judge_ranks, round_input, intervention)
    accepted = fan_ranks[mask]
    compatible_truth = bool(_method_mask(method, true_ranks.reshape(1, -1), judge_ranks, round_input, intervention)[0])
    disclosed = accepted[_disclosure_mask(accepted, true_ranks)] if len(accepted) else accepted
    width = _width(accepted)
    disclosed_width = _width(disclosed)
    recommendation = "add_pairwise_public_disclosure" if np.isfinite(width) and width >= 0.67 else "retain_current_disclosure_with_audit"
    return {
        "truth_covered": compatible_truth,
        "width": width,
        "disclosure_reduction": width - disclosed_width if np.isfinite(disclosed_width) else np.nan,
        "feasible": bool(len(accepted)),
        "recommendation": recommendation,
    }


def run_external_testbed(*, n_replications: int = 120, seed: int = 20260716) -> pd.DataFrame:
    """Run the fixed-seed, structurally different external synthetic testbed."""
    if n_replications < 1:
        raise ValueError("n_replications must be positive.")
    rng = np.random.default_rng(seed)
    records: list[dict[str, Any]] = []
    methods = ("rule_aware_discretion", "direct_rule_misspecification", "rule_agnostic_ordinal")
    for replication in range(n_replications):
        case = _case(rng)
        for method in methods:
            policy_case_coverage: list[float] = []
            policy_recommendations: list[str] = []
            primary_metrics: list[dict[str, Any]] | None = None
            for policy in TIE_SENSITIVITY_POLICIES:
                round_metrics = [
                    _round_metrics(method, round_input, truth, intervention, policy)
                    for round_input, truth, intervention in zip(case.rounds, case.public_ranks, case.intervention_rounds)
                ]
                policy_case_coverage.append(float(all(item["truth_covered"] for item in round_metrics)))
                mean_width = float(np.nanmean([item["width"] for item in round_metrics]))
                policy_recommendations.append(
                    "add_pairwise_public_disclosure" if mean_width >= 0.67 else "retain_current_disclosure_with_audit"
                )
                if policy == PRIMARY_TIE_POLICY:
                    primary_metrics = round_metrics
            assert primary_metrics is not None
            primary_covered = float(all(item["truth_covered"] for item in primary_metrics))
            primary_feasible = bool(all(item["feasible"] for item in primary_metrics))
            modal_recommendation = max(set(policy_recommendations), key=policy_recommendations.count)
            records.append(
                {
                    "replication": replication,
                    "method": method,
                    "coverage": primary_covered,
                    "mean_feasible_set_width": float(np.nanmean([item["width"] for item in primary_metrics])),
                    "false_certainty": float(primary_feasible and not primary_covered),
                    "rule_robustness_index": float(np.mean(policy_case_coverage)),
                    "disclosure_uncertainty_reduction": float(np.nanmean([item["disclosure_reduction"] for item in primary_metrics])),
                    "recommendation_stability": float(np.mean([item == modal_recommendation for item in policy_recommendations])),
                }
            )
    detailed = pd.DataFrame(records)
    summary = detailed.groupby("method", as_index=False).agg(
        n_replications=("replication", "nunique"),
        coverage_rate=("coverage", "mean"),
        average_feasible_set_width=("mean_feasible_set_width", "mean"),
        false_certainty_rate=("false_certainty", "mean"),
        rule_robustness_index=("rule_robustness_index", "mean"),
        disclosure_uncertainty_reduction=("disclosure_uncertainty_reduction", "mean"),
        recommendation_stability=("recommendation_stability", "mean"),
    )
    summary.insert(0, "setting", EXTERNAL_SETTING)
    summary["n_candidates_at_start"] = 7
    summary["n_elimination_rounds"] = 4
    summary["expert_intervention_frequency"] = "2 of 4 rounds (synthetic judge-save override)"
    summary["disclosure_level"] = "synthetic pairwise-majority comparison between top two latent priorities"
    summary["primary_tie_protocol"] = PRIMARY_TIE_POLICY
    summary["sensitivity_tie_protocols"] = "; ".join(TIE_SENSITIVITY_POLICIES)
    summary["evidence_type"] = "synthetic structurally different institutional testbed"
    summary["interpretation_boundary"] = (
        "Known latent rankings exist only inside this simulator. Results show structural portability under the stated grant-prioritization mechanism, not universal empirical validity."
    )
    return summary.sort_values("method", kind="stable").reset_index(drop=True)


def external_testbed_audit(results: pd.DataFrame, *, seed: int) -> str:
    """Document the simulator, metrics, and evidence boundaries for audit."""
    table = results.loc[:, [
        "method",
        "coverage_rate",
        "average_feasible_set_width",
        "false_certainty_rate",
        "rule_robustness_index",
        "disclosure_uncertainty_reduction",
        "recommendation_stability",
    ]].copy()
    for column in table.columns[1:]:
        table[column] = table[column].map(lambda value: f"{float(value):.3f}")
    return "\n".join(
        [
            "# External Testbed Audit",
            "",
            "## Testbed",
            "",
            "The additional setting is a fixed-seed synthetic community-grant prioritization panel. It begins with seven proposals, runs four one-proposal elimination rounds, applies a synthetic expert intervention in rounds two and four, discloses one synthetic pairwise public-priority relation, and uses dense-rank expert tie handling as the primary protocol. This structure differs from the single-case percentage benchmark and the longitudinal empirical testbed.",
            "",
            f"- Fixed random seed: `{seed}`.",
            "- Tie sensitivity protocols: `average_rank`, `min_rank`, `dense_rank`, and `competition_rank`.",
            "- `coverage_rate`: a complete known synthetic public ranking remains compatible in every simulated round.",
            "- `false_certainty_rate`: a nonempty constrained set excludes the known synthetic ranking under a misspecified direct-rule reading.",
            "- `rule_robustness_index`: share of the four predeclared tie protocols that retain the known synthetic ranking.",
            "- `disclosure_uncertainty_reduction`: decrease in normalized rank-support width after the synthetic pairwise disclosure.",
            "- `recommendation_stability`: share of tie protocols agreeing with the modal conditional disclosure recommendation.",
            "",
            "## Results",
            "",
            table.to_markdown(index=False),
            "",
            "## Boundary",
            "",
            "This is a structurally different synthetic testbed, not an external empirical validation, user study, or organizational impact evaluation. It does not establish the true preferences of participants in any real institution.",
        ]
    ) + "\n"
