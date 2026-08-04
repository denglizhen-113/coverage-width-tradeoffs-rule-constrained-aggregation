"""Baseline comparison views derived from the deterministic synthetic benchmark."""

from __future__ import annotations

import pandas as pd

from src.synthetic_benchmark import run_synthetic_benchmark


def build_baseline_comparison(
    *, n_replications: int = 250,
    n_active: int = 5,
    seed: int = 20260716,
) -> pd.DataFrame:
    benchmark = run_synthetic_benchmark(
        n_replications=n_replications,
        n_active=n_active,
        seed=seed,
        noise_levels=(0.0,),
    ).copy()
    labels = {
        "rule_aware_partial_identification": "Feasible set uses documented aggregation constraints.",
        "rule_agnostic_partial_identification": "Simplex-only set ignores the outcome rule.",
        "naive_point_estimation": "Point selected from judge shares; not an identified preference measure.",
        "prediction_only_judge_proxy": "Predictive proxy baseline; not a hidden-preference estimator.",
        "full_disclosure_oracle_synthetic_only": "Synthetic-only upper benchmark with latent preferences revealed.",
    }
    usefulness = {
        "rule_aware_partial_identification": "high: preserves rule-aware feasible uncertainty",
        "rule_agnostic_partial_identification": "moderate: valid but uninformative under coarse feedback",
        "naive_point_estimation": "low: false precision risk",
        "prediction_only_judge_proxy": "low: outcome prediction does not identify latent preference",
        "full_disclosure_oracle_synthetic_only": "upper benchmark only",
    }
    benchmark["interpretability"] = benchmark["method"].map(labels)
    benchmark["decision_usefulness"] = benchmark["method"].map(usefulness)
    benchmark["comparison_boundary"] = "Synthetic evidence only; no empirical hidden-preference recovery claim."
    return benchmark
