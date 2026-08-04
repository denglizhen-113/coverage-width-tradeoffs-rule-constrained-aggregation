"""Synthetic value-of-institutional-disclosure scenarios for percentage rules."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.dss_common import (
    SyntheticPreferenceCase,
    append_inequalities,
    base_percentage_constraints,
    covers_truth,
    generate_percentage_case,
    mean_normalized_width,
    solve_case_bounds,
)


DISCLOSURE_METADATA = {
    "elimination_only": (0.10, 0.10, 0.15, "Outcome plus documented rule only."),
    "elimination_plus_judge_ranking": (0.20, 0.12, 0.28, "Judge ranking is a coarsening of already supplied synthetic judge shares; it adds no preference constraint here."),
    "elimination_plus_top_k_public_rank": (0.42, 0.30, 0.52, "Synthetic disclosure of the top two public positions."),
    "elimination_plus_vote_bin_intervals": (0.58, 0.46, 0.68, "Synthetic release of public-support bins with fixed bin width."),
    "elimination_plus_pairwise_majority": (0.63, 0.55, 0.72, "Synthetic disclosure of pairwise public ordering only."),
    "elimination_plus_margin_intervals": (0.76, 0.70, 0.82, "Synthetic disclosure of bounded public-support margins."),
    "full_public_vote_theoretical_upper_benchmark": (1.00, 1.00, 1.00, "Synthetic theoretical upper benchmark; not a proposed empirical release."),
}


def _order_constraints(case: SyntheticPreferenceCase, *, top_k: int | None = None) -> tuple[list[np.ndarray], list[float]]:
    order = np.argsort(-case.public_preference, kind="stable")
    selected = order if top_k is None else order[:top_k]
    rows: list[np.ndarray] = []
    rhs: list[float] = []
    for left, right in zip(selected[:-1], selected[1:]):
        row = np.zeros(case.n_active, dtype=float)
        row[right] = 1.0
        row[left] = -1.0
        rows.append(row)
        rhs.append(0.0)
    return rows, rhs


def _margin_constraints(case: SyntheticPreferenceCase, *, half_width: float = 0.025) -> tuple[list[np.ndarray], list[float]]:
    reference = int(np.argmax(case.public_preference))
    rows: list[np.ndarray] = []
    rhs: list[float] = []
    for contestant in range(case.n_active):
        if contestant == reference:
            continue
        target = float(case.public_preference[contestant] - case.public_preference[reference])
        upper = np.zeros(case.n_active, dtype=float)
        upper[contestant] = 1.0
        upper[reference] = -1.0
        lower = -upper
        rows.extend([upper, lower])
        rhs.extend([target + half_width, -target + half_width])
    return rows, rhs


def _vote_bin_bounds(case: SyntheticPreferenceCase, *, bin_width: float = 0.10) -> tuple[tuple[float, float], ...]:
    bounds = []
    for value in case.public_preference:
        lower = max(0.0, np.floor(value / bin_width) * bin_width)
        upper = min(1.0, lower + bin_width)
        bounds.append((float(lower), float(upper)))
    return tuple(bounds)


def evaluate_disclosure_case(case: SyntheticPreferenceCase) -> pd.DataFrame:
    """Evaluate nested synthetic disclosure policies on one known-truth case."""
    base = base_percentage_constraints(case, include_elimination_constraint=True)
    base_lower, base_upper, base_feasible = solve_case_bounds(*base)
    base_width = mean_normalized_width(base_lower, base_upper) if base_feasible else np.nan
    rows = []
    for name, (cost, privacy, accountability, note) in DISCLOSURE_METADATA.items():
        A_ub, b_ub, A_eq, b_eq, bounds = base
        if name == "elimination_plus_top_k_public_rank":
            A_ub, b_ub = append_inequalities(A_ub, b_ub, *_order_constraints(case, top_k=2))
        elif name == "elimination_plus_pairwise_majority":
            A_ub, b_ub = append_inequalities(A_ub, b_ub, *_order_constraints(case, top_k=None))
        elif name == "elimination_plus_margin_intervals":
            A_ub, b_ub = append_inequalities(A_ub, b_ub, *_margin_constraints(case))
        elif name == "elimination_plus_vote_bin_intervals":
            bounds = _vote_bin_bounds(case)
        elif name == "full_public_vote_theoretical_upper_benchmark":
            bounds = tuple((float(value), float(value)) for value in case.public_preference)
        lower, upper, feasible = solve_case_bounds(A_ub, b_ub, A_eq, b_eq, bounds)
        width = mean_normalized_width(lower, upper) if feasible else np.nan
        rows.append(
            {
                "disclosure_regime": name,
                "evidence_type": "synthetic institutional-disclosure scenario",
                "mean_feasible_set_width": width,
                "uncertainty_reduction": float(base_width - width) if feasible and np.isfinite(base_width) else np.nan,
                "relative_uncertainty_reduction": float((base_width - width) / base_width) if feasible and base_width > 0 else np.nan,
                "interpretability_gain_design_score": accountability,
                "disclosure_cost_design_score": cost,
                "privacy_risk_design_score": privacy,
                "accountability_gain_design_score": accountability,
                "synthetic_truth_covered": bool(feasible and covers_truth(lower, upper, case.public_preference)),
                "feasible": feasible,
                "scenario_note": note,
            }
        )
    return pd.DataFrame(rows)


def run_value_of_disclosure(*, seed: int = 20260716, n_cases: int = 100, n_active: int = 5) -> pd.DataFrame:
    """Average deterministic disclosure scenarios across synthetic cases."""
    if n_cases < 1:
        raise ValueError("n_cases must be positive.")
    rng = np.random.default_rng(seed)
    frames = []
    for case_id in range(n_cases):
        case = generate_percentage_case(rng, n_active=n_active)
        frame = evaluate_disclosure_case(case)
        frame["synthetic_case_id"] = case_id
        frames.append(frame)
    detailed = pd.concat(frames, ignore_index=True)
    summary = detailed.groupby("disclosure_regime", as_index=False).agg(
        n_synthetic_cases=("synthetic_case_id", "nunique"),
        mean_feasible_set_width=("mean_feasible_set_width", "mean"),
        uncertainty_reduction=("uncertainty_reduction", "mean"),
        relative_uncertainty_reduction=("relative_uncertainty_reduction", "mean"),
        interpretability_gain_design_score=("interpretability_gain_design_score", "first"),
        disclosure_cost_design_score=("disclosure_cost_design_score", "first"),
        privacy_risk_design_score=("privacy_risk_design_score", "first"),
        accountability_gain_design_score=("accountability_gain_design_score", "first"),
        synthetic_truth_coverage_rate=("synthetic_truth_covered", "mean"),
        feasible_rate=("feasible", "mean"),
        scenario_note=("scenario_note", "first"),
    )
    summary["evidence_type"] = "synthetic institutional-disclosure scenario"
    summary["interpretation_boundary"] = (
        "Scores are predeclared design-scenario descriptors, not observed trust, cost, privacy, or accountability measurements."
    )
    order = list(DISCLOSURE_METADATA)
    summary["display_order"] = summary["disclosure_regime"].map({name: index + 1 for index, name in enumerate(order)})
    return summary.sort_values("display_order", kind="stable").reset_index(drop=True)
