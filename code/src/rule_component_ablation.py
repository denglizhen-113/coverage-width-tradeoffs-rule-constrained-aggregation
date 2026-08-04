"""Registered internal and external rule-component ablations."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import numpy as np

from src.dss_artifact import ArtifactRound, _ordinal_mask
from src.dss_common import (
    SyntheticPreferenceCase,
    base_percentage_constraints,
    covers_truth,
    mean_normalized_width,
    solve_case_bounds,
)
from src.external_testbed import ExternalCase, _all_fan_ranks, _disclosure_mask, _width
from src.ranking_identification import compute_judge_ranks


@dataclass(frozen=True)
class ExternalAblationConfig:
    name: str
    elimination: bool
    tie: bool
    save: bool
    disclosure: bool


EXTERNAL_ABLATION_CONFIGS = (
    ExternalAblationConfig("external_full", True, True, True, True),
    ExternalAblationConfig("external_without_elimination", False, True, True, True),
    ExternalAblationConfig("external_without_tie_handling", True, False, True, True),
    ExternalAblationConfig("external_without_save", True, True, False, True),
    ExternalAblationConfig("external_without_disclosure", True, True, True, False),
)


def stable_ordinal_ranks(scores: np.ndarray) -> np.ndarray:
    """Break exact score ties by stable candidate order for the tie-off ablation."""
    values = np.asarray(scores, dtype=float)
    order = np.argsort(-values, kind="stable")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.arange(1, len(values) + 1, dtype=float)
    return ranks


@lru_cache(maxsize=None)
def _cached_fan_ranks(n_active: int) -> np.ndarray:
    return _all_fan_ranks(n_active)


def internal_case_ablation(case: SyntheticPreferenceCase) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, include_elimination in (
        ("internal_full_rule", True),
        ("internal_without_elimination", False),
    ):
        lower, upper, feasible = solve_case_bounds(
            *base_percentage_constraints(
                case,
                include_elimination_constraint=include_elimination,
            )
        )
        rows.append(
            {
                "configuration": name,
                "elimination": include_elimination,
                "tie": "not_applicable",
                "save": "not_applicable",
                "disclosure": "not_applicable",
                "coverage": float(
                    feasible and covers_truth(lower, upper, case.public_preference)
                ),
                "width": mean_normalized_width(lower, upper) if feasible else np.nan,
                "feasible": bool(feasible),
            }
        )
    return rows


def _external_round_ablation(
    round_input: ArtifactRound,
    true_ranks: np.ndarray,
    intervention: bool,
    config: ExternalAblationConfig,
) -> dict[str, Any]:
    scores = np.asarray(
        [round_input.expert_scores[name] for name in round_input.active_candidates],
        dtype=float,
    )
    judge_ranks = (
        compute_judge_ranks(scores, "dense_rank")
        if config.tie
        else stable_ordinal_ranks(scores)
    )
    fan_ranks = _cached_fan_ranks(len(round_input.active_candidates))
    if config.elimination:
        mask = _ordinal_mask(
            fan_ranks,
            judge_ranks,
            round_input,
            weak=bool(config.save and intervention),
        )
    else:
        mask = np.ones(len(fan_ranks), dtype=bool)
    if config.disclosure:
        mask &= _disclosure_mask(fan_ranks, true_ranks)
    accepted = fan_ranks[mask]
    if config.elimination:
        truth_compatible = bool(
            _ordinal_mask(
                true_ranks.reshape(1, -1),
                judge_ranks,
                round_input,
                weak=bool(config.save and intervention),
            )[0]
        )
    else:
        truth_compatible = True
    if config.disclosure:
        truth_compatible = bool(
            truth_compatible
            and _disclosure_mask(true_ranks.reshape(1, -1), true_ranks)[0]
        )
    return {
        "truth_covered": truth_compatible,
        "width": _width(accepted),
        "feasible": bool(len(accepted)),
        "n_compatible_states": int(len(accepted)),
    }


def external_case_ablation(case: ExternalCase) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for config in EXTERNAL_ABLATION_CONFIGS:
        round_results = [
            _external_round_ablation(round_input, truth, intervention, config)
            for round_input, truth, intervention in zip(
                case.rounds,
                case.public_ranks,
                case.intervention_rounds,
            )
        ]
        covered = float(all(bool(item["truth_covered"]) for item in round_results))
        feasible = bool(all(bool(item["feasible"]) for item in round_results))
        rows.append(
            {
                "configuration": config.name,
                "elimination": config.elimination,
                "tie": config.tie,
                "save": config.save,
                "disclosure": config.disclosure,
                "coverage": covered,
                "width": float(np.nanmean([item["width"] for item in round_results])),
                "false_certainty": float(feasible and not covered),
                "feasible": feasible,
                "mean_compatible_states": float(
                    np.mean([item["n_compatible_states"] for item in round_results])
                ),
            }
        )
    return rows
