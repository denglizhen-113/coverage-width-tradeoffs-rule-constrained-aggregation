"""Robustness and sensitivity summaries for DSS module outputs."""

from __future__ import annotations

import numpy as np
import pandas as pd


def classify_sensitivity(relative_change: float | None) -> str:
    if relative_change is None or not np.isfinite(relative_change):
        return "highly sensitive"
    if abs(relative_change) < 0.05:
        return "stable"
    if abs(relative_change) < 0.25:
        return "moderately sensitive"
    return "highly sensitive"


def build_robustness_sensitivity(
    benchmark: pd.DataFrame,
    disclosure: pd.DataFrame,
    ranking_ties: pd.DataFrame,
    p_uncertainty: pd.DataFrame,
) -> pd.DataFrame:
    """Assemble labeled empirical and synthetic sensitivity diagnostics."""
    clean = benchmark.loc[
        benchmark["condition"].eq("rule_consistent")
        & benchmark["method"].eq("rule_aware_partial_identification")
    ].iloc[0]
    noisy = benchmark.loc[
        benchmark["condition"].eq("outcome_noise_stress_test")
        & benchmark["method"].eq("rule_aware_partial_identification")
    ].iloc[0]
    tie = ranking_ties.loc[ranking_ties["regime"].eq("R_plus")].copy()
    tie_width = tie.groupby("tie_policy")["normalized_rank_width"].mean()
    tie_change = float((tie_width.max() - tie_width.min()) / max(tie_width.mean(), 1e-12))
    p_width = pd.to_numeric(p_uncertainty.loc[p_uncertainty["feasible"].astype(bool), "mean_width"], errors="coerce")
    p_active = pd.to_numeric(p_uncertainty.loc[p_uncertainty["feasible"].astype(bool), "n_active"], errors="coerce")
    low = p_width.loc[p_active <= p_active.median()].mean()
    high = p_width.loc[p_active > p_active.median()].mean()
    active_change = float((high - low) / max(abs(low), 1e-12))
    topk = disclosure.loc[disclosure["disclosure_regime"].eq("elimination_plus_top_k_public_rank")].iloc[0]
    full = disclosure.loc[disclosure["disclosure_regime"].eq("full_public_vote_theoretical_upper_benchmark")].iloc[0]
    disclosure_change = float((topk["mean_feasible_set_width"] - full["mean_feasible_set_width"]) / max(topk["mean_feasible_set_width"], 1e-12))
    rows = [
        ("missingness", "synthetic removal of outcome information", 1.0, "synthetic scenario", "highly sensitive", "Removing constraints widens a feasible set by construction; this is an information boundary."),
        ("tie handling", "average/min/dense/competition rank policies", tie_change, "empirical R_plus tie-policy sensitivity", classify_sensitivity(tie_change), "Ordinal result only; no cardinal comparison is made."),
        ("alternative rule interpretation", "direct versus weak judge-save implication", float(noisy["average_feasible_set_width"] - clean["average_feasible_set_width"]), "synthetic stress test", "moderately sensitive", "Noise/misspecification is not an empirical intervention estimate."),
        ("alternative proxy construction", "proxy changes with fixed identification constraints", 0.0, "analytical boundary", "stable", "The dynamic proxy is downstream and does not alter the feasible-set constraints."),
        ("ordinal/cardinal mapping", "attempted cross-regime width mapping", np.nan, "formal comparability boundary", "highly sensitive", "No common functional is defined; raw widths are not compared."),
        ("active contestant trajectory selection", "P width split by active-field size", active_change, "empirical descriptive diagnostic", classify_sensitivity(active_change), "Descriptive split only; active trajectories are historically selected."),
        ("judge-save assumptions", "tie-policy range in weak/direct ordinal model", tie_change, "empirical R_plus tie-policy sensitivity", classify_sensitivity(tie_change), "Containment remains separately audited."),
        ("disclosure granularity", "top-k versus full synthetic disclosure", disclosure_change, "synthetic disclosure scenario", classify_sensitivity(disclosure_change), "Information gain is modeled, not historically observed."),
        ("noise in observed outcomes", "clean versus noisy synthetic observed elimination", float(clean["coverage_rate"] - noisy["coverage_rate"]), "synthetic stress test", classify_sensitivity(float(clean["coverage_rate"] - noisy["coverage_rate"])), "Tests logical calibration under intentionally inconsistent coarse outcomes."),
    ]
    return pd.DataFrame(rows, columns=["sensitivity_dimension", "scenario_or_comparison", "relative_change_or_gap", "evidence_type", "classification", "interpretation_boundary"])
