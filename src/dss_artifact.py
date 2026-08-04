"""Input validation and rule-aware computations for the DSS decision artifact.

The artifact operates on user-supplied, documented rule inputs.  It produces
conditional feasible-set summaries; it never interprets an artifact input as
an observed public vote or as an empirical recovery of hidden preferences.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from math import factorial
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from src.constraints import solve_preference_bounds
from src.ranking_identification import compute_judge_ranks, orders_to_fan_ranks


RULE_TYPES = ("percentage", "ranking", "ranking_plus_judge_save")
JUDGE_SAVE_ASSUMPTIONS = ("not_applicable", "none", "direct", "weak_bottom_set")
TIE_HANDLING_ASSUMPTIONS = ("strict", "tie_inclusive")
DISCLOSURE_REGIMES = (
    "elimination_only",
    "top_k_public_rank",
    "vote_bin_intervals",
    "pairwise_majority",
    "margin_intervals",
)
DECISION_OBJECTIVES = (
    "reduce_uncertainty",
    "preserve_discretion",
    "protect_privacy",
    "improve_accountability",
)
OUTCOME_TYPES = ("elimination", "no_elimination", "withdrawal", "finale")


class ArtifactInputError(ValueError):
    """Raised when a decision-artifact configuration is not auditable."""


@dataclass(frozen=True)
class ArtifactRound:
    """One documented decision round supplied to the artifact."""

    round_id: str
    active_candidates: tuple[str, ...]
    eliminated_candidates: tuple[str, ...]
    expert_scores: dict[str, float]
    outcome_type: str
    finale_order: tuple[str, ...]


@dataclass(frozen=True)
class ArtifactConfig:
    """Validated, JSON-serializable decision-artifact inputs."""

    artifact_label: str
    observed_elimination_outcomes: tuple[ArtifactRound, ...]
    aggregation_rule_type: str
    judge_save_assumption: str
    tie_handling_assumption: str
    disclosure_regime: str
    decision_objective: str
    enumeration_cap: int = 8
    sampling_draws: int = 10_000
    random_seed: int = 20260716


@dataclass(frozen=True)
class ArtifactResult:
    """Structured result returned by the decision cockpit."""

    summary: dict[str, Any]
    round_results: pd.DataFrame
    recommendation_table: pd.DataFrame


def _text(value: Any, field: str) -> str:
    text = str(value).strip()
    if not text:
        raise ArtifactInputError(f"{field} must be a nonempty string.")
    return text


def _number(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ArtifactInputError(f"{field} must be numeric.") from exc
    if not np.isfinite(number):
        raise ArtifactInputError(f"{field} must be finite; NaN and infinity are not valid artifact inputs.")
    return number


def _choice(value: Any, choices: Sequence[str], field: str) -> str:
    selected = _text(value, field)
    if selected not in choices:
        raise ArtifactInputError(f"{field} must be one of: {', '.join(choices)}.")
    return selected


def _round_from_mapping(value: Mapping[str, Any], index: int) -> ArtifactRound:
    if not isinstance(value, Mapping):
        raise ArtifactInputError(f"observed_elimination_outcomes[{index}] must be an object.")
    round_id = _text(value.get("round_id", f"round_{index + 1}"), f"round_id[{index}]")
    active_raw = value.get("active_candidates")
    if not isinstance(active_raw, Sequence) or isinstance(active_raw, (str, bytes)):
        raise ArtifactInputError(f"active_candidates[{index}] must be a list.")
    active = tuple(_text(item, f"active_candidates[{index}]") for item in active_raw)
    if len(active) < 2:
        raise ArtifactInputError(f"round {round_id} has fewer than two active candidates.")
    if len(set(active)) != len(active):
        raise ArtifactInputError(f"round {round_id} has duplicate active candidate labels.")

    outcome_type = _choice(value.get("outcome_type", "elimination"), OUTCOME_TYPES, f"outcome_type[{index}]")
    eliminated_raw = value.get("eliminated_candidates", [])
    if not isinstance(eliminated_raw, Sequence) or isinstance(eliminated_raw, (str, bytes)):
        raise ArtifactInputError(f"eliminated_candidates[{index}] must be a list.")
    eliminated = tuple(_text(item, f"eliminated_candidates[{index}]") for item in eliminated_raw)
    if len(set(eliminated)) != len(eliminated):
        raise ArtifactInputError(f"round {round_id} has duplicate eliminated labels.")
    if not set(eliminated).issubset(active):
        raise ArtifactInputError(f"round {round_id} names an eliminated candidate outside its active set.")
    if len(eliminated) >= len(active):
        raise ArtifactInputError(f"round {round_id} eliminates every active candidate, leaving no comparison set.")
    if outcome_type in {"no_elimination", "withdrawal"} and eliminated:
        raise ArtifactInputError(f"round {round_id} is {outcome_type} but lists eliminated candidates.")
    if outcome_type == "elimination" and not eliminated:
        raise ArtifactInputError(f"round {round_id} is an elimination round but lists no eliminated candidate.")

    score_raw = value.get("expert_scores", {})
    if score_raw is None:
        score_raw = {}
    if not isinstance(score_raw, Mapping):
        raise ArtifactInputError(f"expert_scores[{index}] must be an object keyed by active candidate.")
    scores = {str(name): _number(score, f"expert_scores[{index}][{name}]") for name, score in score_raw.items()}
    if scores and set(scores) != set(active):
        raise ArtifactInputError(f"round {round_id} expert_scores must cover exactly the active candidates.")

    finale_raw = value.get("finale_order", [])
    if not isinstance(finale_raw, Sequence) or isinstance(finale_raw, (str, bytes)):
        raise ArtifactInputError(f"finale_order[{index}] must be a list.")
    finale_order = tuple(_text(item, f"finale_order[{index}]") for item in finale_raw)
    if outcome_type == "finale":
        if set(finale_order) != set(active) or len(finale_order) != len(active):
            raise ArtifactInputError(f"finale round {round_id} needs a complete best-to-worst finale_order.")
    elif finale_order:
        raise ArtifactInputError(f"round {round_id} supplies finale_order outside a finale outcome.")

    return ArtifactRound(round_id, active, eliminated, scores, outcome_type, finale_order)


def config_from_mapping(payload: Mapping[str, Any]) -> ArtifactConfig:
    """Validate a JSON-like payload before any feasible-set computation."""
    if not isinstance(payload, Mapping):
        raise ArtifactInputError("Decision-artifact input must be an object.")
    outcomes = payload.get("observed_elimination_outcomes")
    if not isinstance(outcomes, Sequence) or isinstance(outcomes, (str, bytes)) or not outcomes:
        raise ArtifactInputError("observed_elimination_outcomes must be a nonempty list.")
    rule = _choice(payload.get("aggregation_rule_type"), RULE_TYPES, "aggregation_rule_type")
    judge_save = _choice(payload.get("judge_save_assumption"), JUDGE_SAVE_ASSUMPTIONS, "judge_save_assumption")
    if rule == "ranking_plus_judge_save" and judge_save not in {"direct", "weak_bottom_set"}:
        raise ArtifactInputError("ranking_plus_judge_save requires judge_save_assumption direct or weak_bottom_set.")
    if rule != "ranking_plus_judge_save" and judge_save == "weak_bottom_set":
        raise ArtifactInputError("weak_bottom_set is only meaningful for ranking_plus_judge_save.")
    cap = int(_number(payload.get("enumeration_cap", 8), "enumeration_cap"))
    draws = int(_number(payload.get("sampling_draws", 10_000), "sampling_draws"))
    seed = int(_number(payload.get("random_seed", 20260716), "random_seed"))
    if cap < 3:
        raise ArtifactInputError("enumeration_cap must be at least 3.")
    if draws < 100:
        raise ArtifactInputError("sampling_draws must be at least 100 when sampling is required.")
    rounds = tuple(_round_from_mapping(item, index) for index, item in enumerate(outcomes))
    if any(not item.expert_scores for item in rounds):
        raise ArtifactInputError("Every round must provide documented expert_scores for the selected aggregation rule.")
    return ArtifactConfig(
        artifact_label=_text(payload.get("artifact_label", "decision-artifact run"), "artifact_label"),
        observed_elimination_outcomes=rounds,
        aggregation_rule_type=rule,
        judge_save_assumption=judge_save,
        tie_handling_assumption=_choice(payload.get("tie_handling_assumption"), TIE_HANDLING_ASSUMPTIONS, "tie_handling_assumption"),
        disclosure_regime=_choice(payload.get("disclosure_regime"), DISCLOSURE_REGIMES, "disclosure_regime"),
        decision_objective=_choice(payload.get("decision_objective"), DECISION_OBJECTIVES, "decision_objective"),
        enumeration_cap=cap,
        sampling_draws=draws,
        random_seed=seed,
    )


def config_to_mapping(config: ArtifactConfig) -> dict[str, Any]:
    """Convert a validated configuration to a portable JSON mapping."""
    return {
        "artifact_label": config.artifact_label,
        "observed_elimination_outcomes": [
            {
                "round_id": item.round_id,
                "active_candidates": list(item.active_candidates),
                "eliminated_candidates": list(item.eliminated_candidates),
                "expert_scores": item.expert_scores,
                "outcome_type": item.outcome_type,
                "finale_order": list(item.finale_order),
            }
            for item in config.observed_elimination_outcomes
        ],
        "aggregation_rule_type": config.aggregation_rule_type,
        "judge_save_assumption": config.judge_save_assumption,
        "tie_handling_assumption": config.tie_handling_assumption,
        "disclosure_regime": config.disclosure_regime,
        "decision_objective": config.decision_objective,
        "enumeration_cap": config.enumeration_cap,
        "sampling_draws": config.sampling_draws,
        "random_seed": config.random_seed,
    }


def _normalized_scores(round_input: ArtifactRound) -> np.ndarray:
    scores = np.asarray([round_input.expert_scores[name] for name in round_input.active_candidates], dtype=float)
    shifted = scores - scores.min()
    if float(shifted.sum()) <= 1e-12:
        return np.full(len(scores), 1.0 / len(scores), dtype=float)
    return shifted / shifted.sum()


def _percentage_round(round_input: ArtifactRound) -> dict[str, Any]:
    n_active = len(round_input.active_candidates)
    judges = _normalized_scores(round_input)
    if round_input.outcome_type in {"no_elimination", "withdrawal"}:
        inequalities = np.empty((0, n_active), dtype=float)
        rhs = np.empty(0, dtype=float)
    elif round_input.outcome_type == "finale":
        rows: list[np.ndarray] = []
        rhs_values: list[float] = []
        index = {name: position for position, name in enumerate(round_input.active_candidates)}
        for best, next_best in zip(round_input.finale_order[:-1], round_input.finale_order[1:]):
            best_index, next_index = index[best], index[next_best]
            row = np.zeros(n_active, dtype=float)
            row[best_index], row[next_index] = -1.0, 1.0
            rows.append(row)
            rhs_values.append(float(judges[best_index] - judges[next_index]))
        inequalities = np.vstack(rows) if rows else np.empty((0, n_active), dtype=float)
        rhs = np.asarray(rhs_values, dtype=float)
    else:
        eliminated = {round_input.active_candidates.index(name) for name in round_input.eliminated_candidates}
        survivors = [index for index in range(n_active) if index not in eliminated]
        rows = []
        rhs_values = []
        for eliminated_index in sorted(eliminated):
            for survivor_index in survivors:
                row = np.zeros(n_active, dtype=float)
                row[eliminated_index], row[survivor_index] = 1.0, -1.0
                rows.append(row)
                rhs_values.append(float(judges[survivor_index] - judges[eliminated_index]))
        inequalities = np.vstack(rows)
        rhs = np.asarray(rhs_values, dtype=float)
    solution = solve_preference_bounds(
        inequalities,
        rhs,
        np.ones((1, n_active), dtype=float),
        np.asarray([1.0], dtype=float),
        tuple((0.0, 1.0) for _ in range(n_active)),
    )
    if not solution.feasible:
        return {
            "feasible": False,
            "feasible_set_width": np.nan,
            "n_feasible_states": np.nan,
            "method": "linear_programming",
            "constraint_count": len(inequalities),
            "note": "No compatible cardinal state under the documented inputs and rule.",
        }
    width = float(np.mean(solution.upper_bounds - solution.lower_bounds))
    return {
        "feasible": True,
        "feasible_set_width": width,
        "n_feasible_states": np.nan,
        "method": "linear_programming",
        "constraint_count": len(inequalities),
        "note": "Coordinate-wise share intervals are conditional on the documented percentage rule.",
    }


def _ordinal_mask(
    fan_ranks: np.ndarray,
    judge_ranks: np.ndarray,
    round_input: ArtifactRound,
    weak: bool,
) -> np.ndarray:
    if round_input.outcome_type in {"no_elimination", "withdrawal"}:
        return np.ones(len(fan_ranks), dtype=bool)
    combined = fan_ranks + judge_ranks[None, :]
    if round_input.outcome_type == "finale":
        positions = {name: index for index, name in enumerate(round_input.active_candidates)}
        order = [positions[name] for name in round_input.finale_order]
        return np.all(np.diff(combined[:, order], axis=1) >= -1e-12, axis=1)
    eliminated = [round_input.active_candidates.index(name) for name in round_input.eliminated_candidates]
    bottom_size = len(eliminated) + (1 if weak else 0)
    threshold_index = len(round_input.active_candidates) - bottom_size
    threshold = np.partition(combined, threshold_index, axis=1)[:, threshold_index]
    return np.all(combined[:, eliminated] >= threshold[:, None] - 1e-12, axis=1)


def _ordinal_round(round_input: ArtifactRound, config: ArtifactConfig, stream: int) -> dict[str, Any]:
    n_active = len(round_input.active_candidates)
    score_values = np.asarray([round_input.expert_scores[name] for name in round_input.active_candidates], dtype=float)
    tie_policy = "min_rank" if config.tie_handling_assumption == "strict" else "average_rank"
    judge_ranks = compute_judge_ranks(score_values, tie_policy)
    total = factorial(n_active)
    if n_active <= config.enumeration_cap:
        orders = np.asarray(list(permutations(range(n_active))), dtype=np.int16)
        enumeration_method = "exact"
    else:
        rng = np.random.default_rng(config.random_seed + stream)
        orders = np.argsort(rng.random((config.sampling_draws, n_active)), axis=1).astype(np.int16)
        enumeration_method = "fixed_seed_monte_carlo"
    fan_ranks = orders_to_fan_ranks(orders).astype(float)
    weak = config.aggregation_rule_type == "ranking_plus_judge_save" and config.judge_save_assumption == "weak_bottom_set"
    mask = _ordinal_mask(fan_ranks, judge_ranks, round_input, weak)
    accepted = fan_ranks[mask]
    if len(accepted) == 0:
        return {
            "feasible": False,
            "feasible_set_width": np.nan,
            "n_feasible_states": 0,
            "method": enumeration_method,
            "constraint_count": 1,
            "note": "No compatible strict public ranking under the documented inputs and rule.",
        }
    widths = []
    for candidate in range(n_active):
        support = accepted[:, candidate]
        widths.append(float(support.max() - support.min()))
    normalized_width = float(np.mean(widths) / (n_active - 1)) if n_active > 1 else 0.0
    return {
        "feasible": True,
        "feasible_set_width": normalized_width,
        "n_feasible_states": int(len(accepted)),
        "method": enumeration_method,
        "constraint_count": 1,
        "note": (
            "Normalized feasible public-rank support width; strict public ranks are enumerated or sampled."
            if enumeration_method == "exact"
            else "Normalized feasible public-rank support width estimated from fixed-seed uniform ranking draws."
        ),
        "n_total_states": int(total),
    }


def _uncertainty_class(width: float) -> str:
    if not np.isfinite(width):
        return "infeasible_or_unresolved"
    if width < 0.34:
        return "narrow_conditional_interval"
    if width < 0.67:
        return "moderate_conditional_interval"
    return "broad_conditional_interval"


def _disclosure_recommendation(config: ArtifactConfig, width: float) -> tuple[str, str]:
    if config.decision_objective == "protect_privacy":
        return (
            "Use coarsened vote-bin or pairwise-majority disclosure with a documented release rule.",
            "This preserves a privacy-oriented objective while making residual uncertainty auditable.",
        )
    if config.decision_objective == "preserve_discretion":
        return (
            "Retain the intervention option only with published eligibility and rationale records.",
            "The artifact treats discretion as a documented rule condition, not as evidence of public preference.",
        )
    if config.decision_objective == "improve_accountability":
        return (
            "Publish the applied rule, tie protocol, intervention rationale, and a coarsened public-preference signal.",
            "Accountability improves when later reviewers can reproduce the assumptions behind a conditional conclusion.",
        )
    if np.isfinite(width) and width >= 0.67:
        return (
            "Add the least intrusive disclosure channel that narrows the compatible-state set, starting with public rank or pairwise information.",
            "The current coarse outcome leaves a broad conditional feasible set.",
        )
    return (
        "Retain the documented disclosure regime and publish the rule, tie protocol, and uncertainty report alongside outcomes.",
        "The configured information produces a conditional interval that is not classified as broad.",
    )


def _design_warning(config: ArtifactConfig, round_results: pd.DataFrame, width: float) -> str:
    warnings: list[str] = []
    special = set(round_results["outcome_type"])
    if "withdrawal" in special:
        warnings.append("Withdrawal rounds are non-comparative and contribute no elimination constraint.")
    if "no_elimination" in special:
        warnings.append("No-elimination rounds contribute no outcome-ranking constraint.")
    if "finale" in special:
        warnings.append("Finale ordering is used only because a complete documented order was supplied.")
    if (round_results["eliminated_count"] > 1).any():
        warnings.append("Multiple eliminations are encoded against all non-eliminated active candidates.")
    if config.aggregation_rule_type == "ranking_plus_judge_save" and config.judge_save_assumption == "weak_bottom_set":
        warnings.append("A weak judge-save rule expands the compatible ranking set relative to a direct-elimination reading.")
    if np.isfinite(width) and width >= 0.67:
        warnings.append("Do not select or describe a single hidden public-preference point as recovered from these inputs.")
    return " ".join(warnings) if warnings else "Interpret each feasible set as conditional on the documented rule and disclosure assumptions."


def _accountability_implication(config: ArtifactConfig) -> str:
    fields = "outcome record, aggregation rule, judge-save assumption, tie protocol, disclosure regime, and decision objective"
    return (
        f"Retain a versioned record of the {fields}. The output is an auditable conditional recommendation, "
        "not a substitute for legal, privacy, or stakeholder review."
    )


def _robustness_label(config: ArtifactConfig, rule_robustness: pd.DataFrame | None) -> str:
    if rule_robustness is None or rule_robustness.empty:
        return "not_evaluated_in_this_artifact_run"
    if config.aggregation_rule_type == "percentage":
        row = rule_robustness.loc[rule_robustness["conclusion_id"].eq("C1")]
    elif config.aggregation_rule_type == "ranking_plus_judge_save":
        row = rule_robustness.loc[rule_robustness["conclusion_id"].eq("C2")]
    else:
        row = rule_robustness.loc[rule_robustness["conclusion_id"].eq("C3")]
    if row.empty:
        return "not_evaluated_in_available_rule_robustness_table"
    return str(row.iloc[0]["classification"])


def evaluate_artifact_config(
    config: ArtifactConfig,
    *,
    rule_robustness: pd.DataFrame | None = None,
) -> ArtifactResult:
    """Compute conditional round-level widths and a bounded design recommendation."""
    rows: list[dict[str, Any]] = []
    for stream, round_input in enumerate(config.observed_elimination_outcomes):
        solved = (
            _percentage_round(round_input)
            if config.aggregation_rule_type == "percentage"
            else _ordinal_round(round_input, config, stream)
        )
        rows.append(
            {
                "round_id": round_input.round_id,
                "outcome_type": round_input.outcome_type,
                "n_active": len(round_input.active_candidates),
                "eliminated_count": len(round_input.eliminated_candidates),
                "feasible": bool(solved["feasible"]),
                "feasible_set_width": solved["feasible_set_width"],
                "n_feasible_states": solved.get("n_feasible_states", np.nan),
                "n_total_states": solved.get("n_total_states", np.nan),
                "method": solved["method"],
                "constraint_count": solved["constraint_count"],
                "note": solved["note"],
            }
        )
    round_results = pd.DataFrame(rows)
    valid_widths = pd.to_numeric(round_results.loc[round_results["feasible"], "feasible_set_width"], errors="coerce").dropna()
    overall_width = float(valid_widths.mean()) if not valid_widths.empty else float("nan")
    recommendation, rationale = _disclosure_recommendation(config, overall_width)
    uncertainty_class = _uncertainty_class(overall_width)
    summary = {
        "artifact_label": config.artifact_label,
        "aggregation_rule_type": config.aggregation_rule_type,
        "judge_save_assumption": config.judge_save_assumption,
        "tie_handling_assumption": config.tie_handling_assumption,
        "disclosure_regime": config.disclosure_regime,
        "decision_objective": config.decision_objective,
        "n_documented_rounds": int(len(round_results)),
        "n_feasible_rounds": int(round_results["feasible"].sum()),
        "feasible_set_width": overall_width,
        "uncertainty_class": uncertainty_class,
        "rule_robustness_label": _robustness_label(config, rule_robustness),
        "disclosure_recommendation": recommendation,
        "design_warning": _design_warning(config, round_results, overall_width),
        "accountability_implication": _accountability_implication(config),
        "evidence_boundary": (
            "Artifact outputs are conditional on user-supplied rules and outcomes. They identify compatible states; "
            "they do not recover an empirical public vote, measure trust, or establish institutional impact."
        ),
    }
    recommendations = pd.DataFrame(
        [
            ("feasible_set_width", overall_width, "Mean over feasible documented rounds; units are rule-specific."),
            ("uncertainty_class", uncertainty_class, "Classifies the configured conditional width, not preference truth."),
            ("rule_robustness_label", summary["rule_robustness_label"], "Read from the available predeclared RRI table when applicable."),
            ("disclosure_recommendation", recommendation, rationale),
            ("design_warning", summary["design_warning"], "Warnings preserve special-case and rule-dependence boundaries."),
            ("accountability_implication", summary["accountability_implication"], "The system records assumptions needed for later audit."),
        ],
        columns=["decision_output", "value", "interpretation"],
    )
    return ArtifactResult(summary=summary, round_results=round_results, recommendation_table=recommendations)
