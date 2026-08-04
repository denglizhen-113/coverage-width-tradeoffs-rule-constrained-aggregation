"""Focused contracts for Stage 26X-2 real baselines and component ablation."""

from __future__ import annotations

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/26x2_baselines_ablation.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage26x2_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_max_entropy_center_is_uniform_on_unconstrained_simplex() -> None:
    from src.max_entropy_center_baseline import solve_max_entropy_point

    result = solve_max_entropy_point(
        A_ub=np.empty((0, 3)),
        b_ub=np.empty(0),
        A_eq=np.ones((1, 3)),
        b_eq=np.array([1.0]),
        bounds=((0.0, 1.0),) * 3,
    )

    assert result.feasible
    assert result.solver_success
    assert np.allclose(result.point, np.full(3, 1.0 / 3.0), atol=1e-7)


def test_max_entropy_center_obeys_same_linear_constraint_set() -> None:
    from src.max_entropy_center_baseline import solve_max_entropy_point

    result = solve_max_entropy_point(
        A_ub=np.array([[1.0, 0.0, 0.0]]),
        b_ub=np.array([0.1]),
        A_eq=np.ones((1, 3)),
        b_eq=np.array([1.0]),
        bounds=((0.0, 1.0),) * 3,
    )

    assert result.feasible
    assert result.point[0] <= 0.1 + 1e-8
    assert np.allclose(result.point, np.array([0.1, 0.45, 0.45]), atol=1e-6)


def test_max_entropy_external_center_is_uniform_state_expectation() -> None:
    from src.max_entropy_center_baseline import maximum_entropy_rank_center

    accepted = np.array([[1.0, 2.0, 3.0], [2.0, 1.0, 3.0]])

    center = maximum_entropy_rank_center(accepted)

    assert np.allclose(center, np.array([1.5, 1.5, 3.0]))


def test_truncated_dirichlet_interval_filters_only_by_observed_constraints() -> None:
    from src.bayesian_latent_preference_baseline import truncated_dirichlet_interval

    draws = np.array(
        [
            [0.1, 0.3, 0.6],
            [0.2, 0.3, 0.5],
            [0.5, 0.2, 0.3],
            [0.6, 0.2, 0.2],
        ]
    )
    result = truncated_dirichlet_interval(
        draws,
        A_ub=np.array([[1.0, -1.0, 0.0]]),
        b_ub=np.array([0.0]),
        min_accepted=2,
    )

    assert result.feasible
    assert result.accepted_count == 2
    assert np.allclose(result.center, np.array([0.15, 0.3, 0.55]))
    assert np.all(result.lower <= result.upper)


def test_external_bayesian_interval_uses_exact_compatible_rank_states() -> None:
    from src.bayesian_latent_preference_baseline import exact_rank_posterior_interval

    accepted = np.array(
        [
            [1.0, 2.0, 3.0],
            [1.0, 3.0, 2.0],
            [2.0, 1.0, 3.0],
            [2.0, 3.0, 1.0],
        ]
    )
    result = exact_rank_posterior_interval(accepted)

    assert result.feasible
    assert result.accepted_count == 4
    assert np.allclose(result.center, accepted.mean(axis=0))
    assert np.all(result.lower <= result.center)
    assert np.all(result.center <= result.upper)


def test_tie_off_uses_stable_candidate_order_without_changing_scores() -> None:
    from src.rule_component_ablation import stable_ordinal_ranks

    ranks = stable_ordinal_ranks(np.array([10.0, 10.0, 8.0, 8.0]))

    assert np.array_equal(ranks, np.array([1.0, 2.0, 3.0, 4.0]))


def test_registered_ablation_configs_are_leave_one_component_out() -> None:
    from src.rule_component_ablation import EXTERNAL_ABLATION_CONFIGS

    configs = {item.name: item for item in EXTERNAL_ABLATION_CONFIGS}
    full = configs["external_full"]
    assert full.elimination and full.tie and full.save and full.disclosure
    for component in ("elimination", "tie", "save", "disclosure"):
        item = configs[f"external_without_{'tie_handling' if component == 'tie' else component}"]
        assert not getattr(item, component)
        assert sum(
            getattr(item, other) != getattr(full, other)
            for other in ("elimination", "tie", "save", "disclosure")
        ) == 1


def test_stage26x2_preregistration_is_locked_and_forbidden_alias_is_absent() -> None:
    design = ROOT / "outputs/stage26X-2/PREREGISTERED_DESIGN.md"
    assert design.is_file()
    assert design.stat().st_file_attributes & 1
    for path in (
        ROOT / "src/max_entropy_center_baseline.py",
        ROOT / "src/bayesian_latent_preference_baseline.py",
        ROOT / "src/rule_component_ablation.py",
    ):
        if path.exists():
            assert "prediction_only" not in path.read_text(encoding="utf-8")


def test_stage26x2_runner_is_hash_gated_and_reuses_locked_grid() -> None:
    module = _load_runner()
    assert module.SEEDS == tuple(20260716 + 1000 * index for index in range(20))
    assert module.INTERNAL_GRID == tuple(
        (n_active, noise)
        for n_active in (4, 5, 6)
        for noise in (0.00, 0.05, 0.10, 0.20)
    )
    assert module.EXTERNAL_GRID == ((6, 3), (7, 3), (7, 4))
    assert module.verify_preregistered_design(ROOT) == module.PREREGISTERED_DESIGN_SHA256


def test_internal_max_entropy_raw_is_a_real_point_baseline() -> None:
    module = _load_runner()
    frame = module.run_internal_max_entropy_cell(
        seed=20260716,
        n_active=4,
        noise_probability=0.0,
        n_replications=2,
    )
    assert len(frame) == 2
    assert set(frame["method"]) == {"maximum_entropy_center"}
    assert "point_exact_recovery" in frame.columns
    assert "coverage" not in frame.columns
    assert frame["point_width"].eq(0.0).all()
    assert frame["solver_success"].all()


def test_internal_bayesian_raw_retains_posterior_diagnostics() -> None:
    module = _load_runner()
    frame = module.run_internal_bayesian_cell(
        seed=20260716,
        n_active=4,
        noise_probability=0.0,
        n_replications=2,
    )
    assert len(frame) == 2
    assert set(frame["method"]) == {"bayesian_truncated_dirichlet"}
    assert {"coverage", "width", "accepted_posterior_draws", "posterior_status"}.issubset(
        frame.columns
    )
    assert frame["accepted_posterior_draws"].ge(100).all()


def test_external_baselines_and_ablation_keep_independent_rows() -> None:
    module = _load_runner()
    maximum_entropy = module.run_external_max_entropy_cell(
        seed=20260716,
        n_candidates=6,
        n_rounds=3,
        n_replications=1,
    )
    bayesian = module.run_external_bayesian_cell(
        seed=20260716,
        n_candidates=6,
        n_rounds=3,
        n_replications=1,
    )
    ablation = module.run_external_ablation_cell(
        seed=20260716,
        n_candidates=6,
        n_rounds=3,
        n_replications=1,
    )
    assert len(maximum_entropy) == 1
    assert len(bayesian) == 1
    assert len(ablation) == 5
    assert maximum_entropy.iloc[0]["method"] == "maximum_entropy_rank_center"
    assert bayesian.iloc[0]["method"] == "bayesian_uniform_rank_posterior"
    assert set(ablation["configuration"]) == {
        "external_full",
        "external_without_elimination",
        "external_without_tie_handling",
        "external_without_save",
        "external_without_disclosure",
    }


def test_raw_filenames_are_deterministic_and_baseline_specific() -> None:
    module = _load_runner()
    assert module.internal_raw_filename("max_entropy", 20260716, 5, 0.10) == (
        "internal_seed-20260716_n-5_noise-0.10.csv"
    )
    assert module.external_raw_filename("bayesian", 20260716, 7, 4) == (
        "external_seed-20260716_candidates-7_rounds-4.csv"
    )
    assert module.raw_subdirectory("max_entropy").as_posix().endswith(
        "stage26X-2/raw/max_entropy"
    )
    assert module.raw_subdirectory("bayesian").as_posix().endswith(
        "stage26X-2/raw/bayesian"
    )


def test_internal_ablation_is_derived_from_verified_x1_replication_rows() -> None:
    module = _load_runner()
    source = pd.DataFrame(
        {
            "synthesizer": ["internal_percentage"] * 4,
            "seed": [20260716] * 4,
            "n_active": [4] * 4,
            "outcome_noise_probability": [0.1] * 4,
            "replication": [0, 0, 1, 1],
            "observed_outcome_noise": [False, False, True, True],
            "method": [
                "rule_aware_partial_identification",
                "rule_agnostic_partial_identification",
                "rule_aware_partial_identification",
                "rule_agnostic_partial_identification",
            ],
            "coverage": [1.0, 1.0, 0.0, 1.0],
            "width": [0.8, 1.0, 0.7, 1.0],
            "feasible": [True] * 4,
        }
    )
    result = module.derive_internal_ablation(source)
    assert len(result) == 4
    assert set(result["configuration"]) == {
        "internal_full_rule",
        "internal_without_elimination",
    }
    assert set(result["source_method"]) == set(source["method"])
    assert result["tie"].eq("not_applicable").all()


def test_validate_raw_cell_rejects_missing_replication_rows() -> None:
    module = _load_runner()
    frame = module.run_internal_max_entropy_cell(
        seed=20260716,
        n_active=4,
        noise_probability=0.0,
        n_replications=2,
    ).iloc[:1]
    with pytest.raises(ValueError, match="row count"):
        module.validate_raw_cell(
            frame,
            kind="max_entropy",
            synthesizer="internal",
            seed=20260716,
            n_active=4,
            noise_probability=0.0,
            n_replications=2,
        )


def test_safe_resume_reuses_only_a_valid_raw_cell(tmp_path: Path) -> None:
    module = _load_runner()
    frame = module.run_internal_max_entropy_cell(
        seed=20260716,
        n_active=4,
        noise_probability=0.0,
        n_replications=2,
    )
    output = tmp_path / "cell.csv"
    module.atomic_write_csv(frame, output)

    def must_not_run() -> pd.DataFrame:
        raise AssertionError("valid raw cell was recomputed")

    resumed, status = module.load_or_run_cell(
        output,
        must_not_run,
        kind="max_entropy",
        synthesizer="internal",
        seed=20260716,
        n_active=4,
        noise_probability=0.0,
        n_replications=2,
    )
    assert status == "reused"
    assert len(resumed) == 2


def test_seed_level_summary_preserves_seed_as_statistical_unit() -> None:
    module = _load_runner()
    frame = pd.DataFrame(
        {
            "synthesizer": ["internal_percentage"] * 4,
            "seed": [1, 1, 2, 2],
            "n_active": [4] * 4,
            "outcome_noise_probability": [0.0] * 4,
            "method": ["bayesian_truncated_dirichlet"] * 4,
            "coverage": [1.0, 0.0, 1.0, 1.0],
            "width": [0.2, 0.4, 0.1, 0.3],
        }
    )
    seed_level = module.summarize_seed_level(
        frame,
        group_columns=[
            "synthesizer",
            "seed",
            "n_active",
            "outcome_noise_probability",
            "method",
        ],
        metrics=["coverage", "width"],
    )
    assert len(seed_level) == 2
    assert seed_level.loc[seed_level["seed"].eq(1), "coverage"].iloc[0] == 0.5
    across = module.summarize_across_seeds(
        seed_level,
        group_columns=[
            "synthesizer",
            "n_active",
            "outcome_noise_probability",
            "method",
        ],
        metrics=["coverage", "width"],
    )
    assert across["seed_count"].iloc[0] == 2
    assert across["coverage_mean"].iloc[0] == 0.75


def test_locked_attribution_rules_do_not_treat_point_width_as_interval_evidence() -> None:
    module = _load_runner()
    ruling = module.select_attribution_ruling(
        structural_width_ordering_proportion=1.0,
        structural_majority_reversal_regions=0,
        structural_region_count=15,
        bayesian_clean_pareto_proportion=0.90,
        bayesian_majority_reversal_regions=0,
        bayesian_dominates_proportion=0.0,
    )
    assert ruling == "RULE_AWARE_ADVANTAGE_STRUCTURAL_ONLY"


def test_registered_cell_plans_use_every_locked_seed_and_grid_cell() -> None:
    module = _load_runner()
    for kind in ("max_entropy", "bayesian", "ablation"):
        cells = module.registered_cells(kind)
        assert len(cells) == 300
        assert sum(cell["synthesizer"] == "internal" for cell in cells) == 240
        assert sum(cell["synthesizer"] == "external" for cell in cells) == 60
        assert {cell["seed"] for cell in cells} == set(module.SEEDS)


def test_paired_ablation_effects_identify_coverage_improvement_and_width_cost() -> None:
    module = _load_runner()
    seed_level = pd.DataFrame(
        {
            "synthesizer": ["external_ordinal"] * 4,
            "seed": [1, 1, 2, 2],
            "n_candidates": [6] * 4,
            "n_rounds": [3] * 4,
            "configuration": [
                "external_full",
                "external_without_save",
                "external_full",
                "external_without_save",
            ],
            "coverage": [0.8, 1.0, 1.0, 1.0],
            "width": [0.4, 0.6, 0.5, 0.7],
        }
    )
    effects = module.compute_ablation_effects(seed_level)
    assert effects["coverage_improved"].tolist() == [True, False]
    assert np.allclose(effects["coverage_change"], [0.2, 0.0])
    assert np.allclose(effects["width_change"], [0.2, 0.2])


def test_ablation_summary_merges_effect_counts_one_to_one() -> None:
    module = _load_runner()
    records = []
    for seed in (1, 2):
        for configuration, elimination in (
            ("internal_full_rule", 1),
            ("internal_without_elimination", 0),
        ):
            records.append(
                {
                    "synthesizer": "internal_percentage",
                    "seed": seed,
                    "n_active": 4,
                    "outcome_noise_probability": 0.0,
                    "replication": 0,
                    "configuration": configuration,
                    "elimination": elimination,
                    "tie": "not_applicable",
                    "save": "not_applicable",
                    "disclosure": "not_applicable",
                    "coverage": 1.0,
                    "width": 0.8 if elimination else 1.0,
                    "feasible": True,
                }
            )
        for configuration in (
            "external_full",
            "external_without_elimination",
            "external_without_tie_handling",
            "external_without_save",
            "external_without_disclosure",
        ):
            records.append(
                {
                    "synthesizer": "external_ordinal",
                    "seed": seed,
                    "n_candidates": 6,
                    "n_rounds": 3,
                    "replication": 0,
                    "configuration": configuration,
                    "elimination": configuration != "external_without_elimination",
                    "tie": configuration != "external_without_tie_handling",
                    "save": configuration != "external_without_save",
                    "disclosure": configuration != "external_without_disclosure",
                    "coverage": 1.0,
                    "width": 0.5 if configuration == "external_full" else 0.6,
                    "feasible": True,
                    "false_certainty": 0.0,
                    "mean_compatible_states": 10.0,
                }
            )
    _, _, _, effect_summary = module._ablation_summaries(pd.DataFrame(records))
    assert len(effect_summary) == 5
    assert effect_summary["paired_cells"].eq(2).all()


def test_component_overall_summary_uses_all_registered_paired_cells() -> None:
    module = _load_runner()
    effect_summary = pd.DataFrame(
        {
            "synthesizer": ["external_ordinal"] * 3,
            "configuration": [
                "external_without_save",
                "external_without_save",
                "external_without_disclosure",
            ],
            "paired_cells": [20, 20, 20],
            "coverage_improved_count": [0, 0, 0],
            "coverage_worsened_count": [20, 20, 0],
            "coverage_change_mean": [-0.8, -0.6, 0.0],
            "width_change_mean": [-0.1, -0.05, 0.2],
        }
    )
    overall = module.component_overall_summary(effect_summary)
    save = overall.loc[
        overall["configuration"].eq("external_without_save")
    ].iloc[0]
    assert save["paired_cells"] == 40
    assert save["coverage_change_mean"] == pytest.approx(-0.7)
    assert save["width_change_mean"] == pytest.approx(-0.075)
