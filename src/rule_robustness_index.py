"""Conclusion-level Rule Robustness Index (RRI) utilities.

RRI is the share of predeclared, applicable configurations supporting a
conclusion predicate. It does not average cardinal and ordinal widths into one
latent-preference metric.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _as_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.casefold().isin({"true", "1", "yes"})


def classify_rri(value: float) -> str:
    if value >= 0.95:
        return "robust"
    if value >= 0.60:
        return "assumption-sensitive"
    return "non-identifiable"


def build_rule_robustness_index(
    identification: pd.DataFrame,
    ranking_ties: pd.DataFrame,
) -> pd.DataFrame:
    """Compute predeclared conclusion stability from existing output files."""
    p = identification.loc[identification["regime"].eq("P")].iloc[0]
    tie = ranking_ties.copy()
    rplus = tie.loc[tie["regime"].eq("R_plus")].copy()
    if rplus.empty:
        raise ValueError("R_plus tie-policy sensitivity rows are required for RRI.")
    rows: list[dict[str, object]] = []

    aware_width = float(p["mean_normalized_uncertainty"])
    agnostic_width = 1.0
    predicate = aware_width <= agnostic_width + 1e-12
    rows.append(
        {
            "conclusion_id": "C1",
            "conclusion": "Correct rule-aware P constraints are no less informative than the simplex-only rule-agnostic representation.",
            "configuration_family": "rule-aware versus rule-agnostic cardinal P",
            "applicable_configurations": 1,
            "supporting_configurations": int(predicate),
            "rule_robustness_index": float(predicate),
            "classification": classify_rri(float(predicate)),
            "evidence_type": "empirical P summary plus analytical simplex baseline",
            "boundary": "This compares nested P constraints only; it does not compare P width to ordinal width.",
        }
    )

    tie_group = rplus.groupby("tie_policy", as_index=False).agg(
        mean_ordinal_width=("normalized_rank_width", "mean"),
        weak_count=("n_feasible_permutations", "sum"),
        direct_count=("n_feasible_direct_R_like", "sum"),
    )
    supports = tie_group["weak_count"] >= tie_group["direct_count"]
    rri = float(supports.mean())
    rows.append(
        {
            "conclusion_id": "C2",
            "conclusion": "The weak judge-save feasible ranking set contains the direct-feasible ranking set within evaluated R_plus weeks.",
            "configuration_family": "strict/relaxed tie handling and judge-save interpretations",
            "applicable_configurations": int(len(tie_group)),
            "supporting_configurations": int(supports.sum()),
            "rule_robustness_index": rri,
            "classification": classify_rri(rri),
            "evidence_type": "empirical R_plus tie-policy sensitivity",
            "boundary": "Containment is a within-week ordinal relation, not a cross-regime comparison.",
        }
    )

    wide = tie_group["mean_ordinal_width"] >= 0.70
    rri = float(wide.mean())
    rows.append(
        {
            "conclusion_id": "C3",
            "conclusion": "Ordinal feasible-ranking uncertainty remains broad across documented tie policies.",
            "configuration_family": "strict/relaxed tie handling",
            "applicable_configurations": int(len(tie_group)),
            "supporting_configurations": int(wide.sum()),
            "rule_robustness_index": rri,
            "classification": classify_rri(rri),
            "evidence_type": "empirical R_plus tie-policy sensitivity",
            "boundary": "The 0.70 threshold is a predeclared descriptive predicate, not a welfare cutoff.",
        }
    )

    rows.append(
        {
            "conclusion_id": "C4",
            "conclusion": "Cardinal and ordinal uncertainty summaries require a common functional before direct numerical comparison.",
            "configuration_family": "cardinal versus ordinal representation",
            "applicable_configurations": 1,
            "supporting_configurations": 1,
            "rule_robustness_index": 1.0,
            "classification": "robust",
            "evidence_type": "formal representation boundary",
            "boundary": "This is a comparability condition, not a numerical finding about which regime is more uncertain.",
        }
    )
    return pd.DataFrame(rows)
