"""Focused contracts for the preregistered Stage 26X-1 experiment."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/26x1_multiseed_sensitivity.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("stage26x1_multiseed", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stage26x1_runner_exists() -> None:
    assert SCRIPT.is_file()


def test_stage26x1_runner_exposes_command_line_help() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "preregistered" in result.stdout.lower()
    assert "--mode" in result.stdout


def test_preregistered_seed_rule_and_hash_are_locked() -> None:
    module = _load_module()
    assert module.SEEDS == tuple(20260716 + 1000 * index for index in range(20))
    assert module.verify_preregistered_design(ROOT) == module.PREREGISTERED_DESIGN_SHA256


def test_internal_raw_rows_are_replication_level_and_exclude_deleted_alias() -> None:
    module = _load_module()
    frame = module.run_internal_cell(seed=20260716, n_active=4, noise_probability=0.0, n_replications=2)
    assert len(frame) == 8
    assert frame["replication"].nunique() == 2
    assert set(frame["method"]) == {
        "rule_aware_partial_identification",
        "rule_agnostic_partial_identification",
        "naive_point_estimation",
        "full_disclosure_oracle_synthetic_only",
    }
    assert "prediction_only_judge_proxy" not in set(frame["method"])
    assert {
        "synthesizer",
        "seed",
        "n_active",
        "outcome_noise_probability",
        "replication",
        "coverage",
        "width",
        "false_certainty",
        "baseline_error",
        "outcome_consistent",
        "feasible",
        "observed_outcome_noise",
    }.issubset(frame.columns)


def test_external_raw_rows_keep_all_original_metrics() -> None:
    module = _load_module()
    frame = module.run_external_cell(seed=20260716, n_candidates=6, n_rounds=3, n_replications=1)
    assert len(frame) == 3
    assert set(frame["method"]) == {
        "rule_aware_discretion",
        "direct_rule_misspecification",
        "rule_agnostic_ordinal",
    }
    assert {
        "synthesizer",
        "seed",
        "n_candidates",
        "n_rounds",
        "replication",
        "coverage",
        "width",
        "false_certainty",
        "rule_robustness_index",
        "disclosure_uncertainty_reduction",
        "recommendation_stability",
    }.issubset(frame.columns)


def test_multiseed_summary_uses_seed_level_estimates() -> None:
    module = _load_module()
    seed_level = pd.DataFrame(
        {
            "condition": ["clean"] * 3,
            "method": ["aware"] * 3,
            "seed": [1, 2, 3],
            "coverage_rate": [0.0, 0.5, 1.0],
            "average_width": [0.2, 0.4, 0.6],
            "n_replications": [10, 10, 10],
        }
    )
    summary = module.summarize_across_seeds(
        seed_level,
        group_columns=["condition", "method"],
        metric_columns=["coverage_rate", "average_width"],
    )
    row = summary.iloc[0]
    assert row["n_seeds"] == 3
    assert row["replications_per_seed"] == 10
    assert row["total_replications"] == 30
    assert row["coverage_rate_mean"] == 0.5
    assert row["coverage_rate_median"] == 0.5
    assert row["coverage_rate_std"] == 0.5
    assert row["coverage_rate_q025"] == 0.025
    assert row["coverage_rate_q975"] == 0.975


def test_preregistered_grids_and_raw_filenames_are_locked() -> None:
    module = _load_module()
    assert module.INTERNAL_GRID == tuple(
        (n_active, noise)
        for n_active in (4, 5, 6)
        for noise in (0.00, 0.05, 0.10, 0.20)
    )
    assert module.EXTERNAL_GRID == ((6, 3), (7, 3), (7, 4))
    assert module.internal_raw_filename(20260716, 5, 0.10) == (
        "internal_seed-20260716_n-5_noise-0.10.csv"
    )
    assert module.external_raw_filename(20260716, 7, 4) == (
        "external_seed-20260716_candidates-7_rounds-4.csv"
    )


def test_seed_level_aggregators_preserve_original_metrics() -> None:
    module = _load_module()
    internal = module.aggregate_internal_seed(
        module.run_internal_cell(
            seed=20260716,
            n_active=4,
            noise_probability=0.0,
            n_replications=2,
        )
    )
    assert len(internal) == 4
    assert {
        "coverage_rate",
        "average_feasible_set_width",
        "false_certainty_rate",
        "baseline_error",
        "outcome_consistency_rate",
        "feasible_rate",
    }.issubset(internal.columns)
    external = module.aggregate_external_seed(
        module.run_external_cell(
            seed=20260716,
            n_candidates=6,
            n_rounds=3,
            n_replications=1,
        )
    )
    assert len(external) == 3
    assert {
        "coverage_rate",
        "average_feasible_set_width",
        "false_certainty_rate",
        "rule_robustness_index",
        "disclosure_uncertainty_reduction",
        "recommendation_stability",
    }.issubset(external.columns)


def test_original_seed_position_counts_only_exact_ties() -> None:
    module = _load_module()
    frame = pd.DataFrame(
        {
            "seed": [module.SEEDS[0], module.SEEDS[1]],
            "n_active": [5, 5],
            "method": ["aware", "aware"],
            "coverage_rate": [0.3, 0.1 + 0.2],
        }
    )
    rows = module._position_rows(
        frame,
        filters={"n_active": 5},
        methods=("aware",),
        metrics=("coverage_rate",),
        label="toy",
    )
    assert rows[0]["exact_ties"] == 1
