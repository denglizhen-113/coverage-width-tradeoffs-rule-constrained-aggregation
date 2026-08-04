"""Run registered same-information baselines and component ablations for Stage 26X-2."""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src.bayesian_latent_preference_baseline import (
    exact_rank_posterior_interval,
    truncated_dirichlet_interval,
)
from src.dss_common import (
    base_percentage_constraints,
    generate_percentage_case,
    point_is_outcome_consistent,
)
from src.external_testbed import (
    _all_fan_ranks,
    _case as generate_external_case,
    _method_mask,
)
from src.max_entropy_center_baseline import (
    maximum_entropy_rank_center,
    solve_max_entropy_point,
)
from src.ranking_identification import compute_judge_ranks
from src.rule_component_ablation import external_case_ablation


SEEDS = tuple(20260716 + 1000 * index for index in range(20))
INTERNAL_GRID = tuple(
    (n_active, noise_probability)
    for n_active in (4, 5, 6)
    for noise_probability in (0.00, 0.05, 0.10, 0.20)
)
EXTERNAL_GRID = ((6, 3), (7, 3), (7, 4))
INTERNAL_REPLICATIONS = 250
EXTERNAL_REPLICATIONS = 120
BAYESIAN_PRIOR_DRAWS = 8192
BAYESIAN_MIN_ACCEPTED = 100
PREREGISTERED_DESIGN = Path("outputs/stage26X-2/PREREGISTERED_DESIGN.md")
PREREGISTERED_DESIGN_SHA256 = "e5418f189061ed295a941327bcf3364081b4095d8b1a1855a416f0431191d19c"
RAW_KINDS = ("max_entropy", "bayesian", "ablation")
PROTECTED_INPUT_HASHES = {
    Path("outputs/stage26W/DSS_submission_draft_STAGE26W_source.md"): (
        "6f1fc33fcd93e099b0ecf85f3f129e94b4aa00be80a42e8dd162bc3d2db45b76"
    ),
    Path("outputs/stage26X-1/PREREGISTERED_DESIGN.md"): (
        "e437a81b80143b2f03c81b005d463cc489185d7f781214e8446d1e111784257b"
    ),
    Path("outputs/stage26X-1/ROBUSTNESS_ASSESSMENT.md"): (
        "34a18f4090f5bd0628cdca67f31b48690dda350d2fece74ba246a2fd369aa375"
    ),
    Path("outputs/stage26X-1/tables/Table4_multiseed.csv"): (
        "ff70ea1496853db01267f4edd9942b405b24168e28be9de59b9ec9557078100f"
    ),
    Path("outputs/stage26X-1/tables/Table5_multiseed.csv"): (
        "485563b5486a8f127ab3b6cec2baaa2556565821069f41ebd340b7e365c84899"
    ),
}


def raw_subdirectory(kind: str, root: Path = ROOT) -> Path:
    if kind not in RAW_KINDS:
        raise ValueError(f"Unknown Stage 26X-2 raw-output kind: {kind}")
    return root / "outputs/stage26X-2/raw" / kind


def internal_raw_filename(
    kind: str,
    seed: int,
    n_active: int,
    noise_probability: float,
) -> str:
    if kind not in RAW_KINDS:
        raise ValueError(f"Unknown Stage 26X-2 raw-output kind: {kind}")
    return (
        f"internal_seed-{seed}_n-{n_active}_noise-{noise_probability:.2f}.csv"
    )


def external_raw_filename(
    kind: str,
    seed: int,
    n_candidates: int,
    n_rounds: int,
) -> str:
    if kind not in RAW_KINDS:
        raise ValueError(f"Unknown Stage 26X-2 raw-output kind: {kind}")
    return (
        f"external_seed-{seed}_candidates-{n_candidates}_rounds-{n_rounds}.csv"
    )


def derive_internal_ablation(source_frame: pd.DataFrame) -> pd.DataFrame:
    method_to_configuration = {
        "rule_aware_partial_identification": "internal_full_rule",
        "rule_agnostic_partial_identification": "internal_without_elimination",
    }
    selected = source_frame.loc[
        source_frame["method"].isin(method_to_configuration)
    ].copy()
    selected["source_method"] = selected["method"]
    selected["configuration"] = selected["source_method"].map(
        method_to_configuration
    )
    selected["elimination"] = selected["configuration"].eq(
        "internal_full_rule"
    ).astype(int)
    selected["tie"] = "not_applicable"
    selected["save"] = "not_applicable"
    selected["disclosure"] = "not_applicable"
    selected = selected.drop(columns="method")
    return selected


def atomic_write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    os.close(handle)
    temporary_path = Path(temporary_name)
    try:
        frame.to_csv(temporary_path, index=False)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def validate_raw_cell(
    frame: pd.DataFrame,
    *,
    kind: str,
    synthesizer: str,
    seed: int,
    n_replications: int,
    n_active: int | None = None,
    noise_probability: float | None = None,
    n_candidates: int | None = None,
    n_rounds: int | None = None,
) -> None:
    if kind not in RAW_KINDS:
        raise ValueError(f"Unknown Stage 26X-2 raw-output kind: {kind}")
    if synthesizer not in {"internal", "external"}:
        raise ValueError(f"Unknown synthesizer: {synthesizer}")
    expected_multiplier = 1
    identity_column = "method"
    expected_identities: set[str]
    if kind == "max_entropy":
        expected_identities = {
            "maximum_entropy_center"
            if synthesizer == "internal"
            else "maximum_entropy_rank_center"
        }
    elif kind == "bayesian":
        expected_identities = {
            "bayesian_truncated_dirichlet"
            if synthesizer == "internal"
            else "bayesian_uniform_rank_posterior"
        }
    else:
        identity_column = "configuration"
        if synthesizer == "internal":
            expected_identities = {
                "internal_full_rule",
                "internal_without_elimination",
            }
        else:
            expected_identities = {
                "external_full",
                "external_without_elimination",
                "external_without_tie_handling",
                "external_without_save",
                "external_without_disclosure",
            }
        expected_multiplier = len(expected_identities)
    expected_rows = n_replications * expected_multiplier
    if len(frame) != expected_rows:
        raise ValueError(
            f"Raw cell row count is {len(frame)}; expected {expected_rows}."
        )
    required = {
        "synthesizer",
        "seed",
        "replication",
        identity_column,
        "feasible",
        "width" if kind != "max_entropy" else "point_width",
    }
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Raw cell missing required columns: {missing}")
    expected_synthesizer = (
        "internal_percentage" if synthesizer == "internal" else "external_ordinal"
    )
    if set(frame["synthesizer"].astype(str)) != {expected_synthesizer}:
        raise ValueError("Raw cell synthesizer value does not match its cell.")
    if set(pd.to_numeric(frame["seed"]).astype(int)) != {seed}:
        raise ValueError("Raw cell seed value does not match its cell.")
    if set(frame[identity_column].astype(str)) != expected_identities:
        raise ValueError("Raw cell method/configuration set is incomplete or unexpected.")
    replication = pd.to_numeric(frame["replication"]).astype(int)
    expected_replications = set(range(n_replications))
    if set(replication) != expected_replications:
        raise ValueError("Raw cell replication identifiers are incomplete or unexpected.")
    if frame.duplicated(["replication", identity_column]).any():
        raise ValueError("Raw cell has duplicate replication-method/configuration keys.")
    parameter_checks = (
        (("n_active", n_active), ("outcome_noise_probability", noise_probability))
        if synthesizer == "internal"
        else (("n_candidates", n_candidates), ("n_rounds", n_rounds))
    )
    for column, expected in parameter_checks:
        if expected is None or column not in frame:
            raise ValueError(f"Raw cell lacks registered parameter {column}.")
        values = pd.to_numeric(frame[column]).to_numpy(dtype=float)
        if not np.allclose(values, float(expected), atol=1e-12, rtol=0.0):
            raise ValueError(f"Raw cell parameter {column} does not match its cell.")


def load_or_run_cell(
    path: Path,
    factory: Callable[[], pd.DataFrame],
    **validation: Any,
) -> tuple[pd.DataFrame, str]:
    if path.exists():
        frame = pd.read_csv(path)
        validate_raw_cell(frame, **validation)
        return frame, "reused"
    frame = factory()
    validate_raw_cell(frame, **validation)
    atomic_write_csv(frame, path)
    persisted = pd.read_csv(path)
    validate_raw_cell(persisted, **validation)
    return persisted, "completed"


def summarize_seed_level(
    frame: pd.DataFrame,
    *,
    group_columns: list[str],
    metrics: list[str],
) -> pd.DataFrame:
    return (
        frame.groupby(group_columns, as_index=False, dropna=False)[metrics]
        .mean()
        .sort_values(group_columns)
        .reset_index(drop=True)
    )


def summarize_across_seeds(
    seed_level: pd.DataFrame,
    *,
    group_columns: list[str],
    metrics: list[str],
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    grouped = seed_level.groupby(group_columns, dropna=False, sort=True)
    for key, group in grouped:
        key_values = key if isinstance(key, tuple) else (key,)
        record = dict(zip(group_columns, key_values))
        record["seed_count"] = int(group["seed"].nunique())
        for metric in metrics:
            values = pd.to_numeric(group[metric], errors="coerce").dropna()
            record[f"{metric}_mean"] = float(values.mean())
            record[f"{metric}_median"] = float(values.median())
            record[f"{metric}_std"] = float(values.std(ddof=1))
            record[f"{metric}_q025"] = float(
                values.quantile(0.025, interpolation="linear")
            )
            record[f"{metric}_q975"] = float(
                values.quantile(0.975, interpolation="linear")
            )
        records.append(record)
    return pd.DataFrame.from_records(records)


def select_attribution_ruling(
    *,
    structural_width_ordering_proportion: float,
    structural_majority_reversal_regions: int,
    structural_region_count: int,
    bayesian_clean_pareto_proportion: float,
    bayesian_majority_reversal_regions: int,
    bayesian_dominates_proportion: float,
) -> str:
    if (
        structural_width_ordering_proportion >= 0.95
        and structural_majority_reversal_regions == 0
        and bayesian_clean_pareto_proportion >= 0.95
        and bayesian_majority_reversal_regions == 0
    ):
        return "RULE_AWARE_ADVANTAGE_SUBSTANTIATED"
    if (
        structural_majority_reversal_regions > structural_region_count / 2
        or bayesian_dominates_proportion >= 0.5
    ):
        return "RULE_AWARE_ADVANTAGE_NOT_SUPPORTED"
    return "RULE_AWARE_ADVANTAGE_STRUCTURAL_ONLY"


def registered_cells(kind: str) -> list[dict[str, Any]]:
    if kind not in RAW_KINDS:
        raise ValueError(f"Unknown Stage 26X-2 raw-output kind: {kind}")
    cells: list[dict[str, Any]] = []
    for seed in SEEDS:
        for n_active, noise_probability in INTERNAL_GRID:
            cells.append(
                {
                    "kind": kind,
                    "synthesizer": "internal",
                    "seed": seed,
                    "n_active": n_active,
                    "noise_probability": noise_probability,
                    "n_replications": INTERNAL_REPLICATIONS,
                }
            )
        for n_candidates, n_rounds in EXTERNAL_GRID:
            cells.append(
                {
                    "kind": kind,
                    "synthesizer": "external",
                    "seed": seed,
                    "n_candidates": n_candidates,
                    "n_rounds": n_rounds,
                    "n_replications": EXTERNAL_REPLICATIONS,
                }
            )
    return cells


def _cell_output_path(root: Path, cell: dict[str, Any]) -> Path:
    kind = str(cell["kind"])
    if cell["synthesizer"] == "internal":
        filename = internal_raw_filename(
            kind,
            int(cell["seed"]),
            int(cell["n_active"]),
            float(cell["noise_probability"]),
        )
    else:
        filename = external_raw_filename(
            kind,
            int(cell["seed"]),
            int(cell["n_candidates"]),
            int(cell["n_rounds"]),
        )
    return raw_subdirectory(kind, root) / filename


def _cell_id(cell: dict[str, Any]) -> str:
    if cell["synthesizer"] == "internal":
        return (
            f"internal|seed={cell['seed']}|n={cell['n_active']}|"
            f"noise={float(cell['noise_probability']):.2f}"
        )
    return (
        f"external|seed={cell['seed']}|candidates={cell['n_candidates']}|"
        f"rounds={cell['n_rounds']}"
    )


def _x1_internal_source_path(root: Path, cell: dict[str, Any]) -> Path:
    return root / "outputs/stage26X-1/raw" / internal_raw_filename(
        "ablation",
        int(cell["seed"]),
        int(cell["n_active"]),
        float(cell["noise_probability"]),
    )


def _validate_x1_internal_source(
    frame: pd.DataFrame,
    *,
    seed: int,
    n_active: int,
    noise_probability: float,
) -> None:
    required = {
        "synthesizer",
        "seed",
        "n_active",
        "outcome_noise_probability",
        "replication",
        "method",
        "coverage",
        "width",
        "feasible",
    }
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Stage 26X-1 source is missing columns: {missing}")
    selected = frame.loc[
        frame["method"].isin(
            {
                "rule_aware_partial_identification",
                "rule_agnostic_partial_identification",
            }
        )
    ]
    if len(selected) != 2 * INTERNAL_REPLICATIONS:
        raise ValueError("Stage 26X-1 source lacks complete internal ablation rows.")
    if selected.duplicated(["replication", "method"]).any():
        raise ValueError("Stage 26X-1 source has duplicate replication-method keys.")
    if set(pd.to_numeric(selected["replication"]).astype(int)) != set(
        range(INTERNAL_REPLICATIONS)
    ):
        raise ValueError("Stage 26X-1 source replication identifiers are incomplete.")
    checks = (
        ("seed", seed),
        ("n_active", n_active),
        ("outcome_noise_probability", noise_probability),
    )
    for column, expected in checks:
        values = pd.to_numeric(selected[column]).to_numpy(dtype=float)
        if not np.allclose(values, float(expected), atol=1e-12, rtol=0.0):
            raise ValueError(f"Stage 26X-1 source {column} does not match its cell.")


def _cell_factory(
    root: Path,
    cell: dict[str, Any],
) -> tuple[Callable[[], pd.DataFrame], str, str]:
    kind = str(cell["kind"])
    synthesizer = str(cell["synthesizer"])
    seed = int(cell["seed"])
    n_replications = int(cell["n_replications"])
    if synthesizer == "internal":
        n_active = int(cell["n_active"])
        noise_probability = float(cell["noise_probability"])
        if kind == "max_entropy":
            return (
                lambda: run_internal_max_entropy_cell(
                    seed=seed,
                    n_active=n_active,
                    noise_probability=noise_probability,
                    n_replications=n_replications,
                ),
                "",
                "",
            )
        if kind == "bayesian":
            return (
                lambda: run_internal_bayesian_cell(
                    seed=seed,
                    n_active=n_active,
                    noise_probability=noise_probability,
                    n_replications=n_replications,
                ),
                "",
                "",
            )
        source_path = _x1_internal_source_path(root, cell)
        if not source_path.is_file():
            raise RuntimeError(f"Stage 26X-1 source file is missing: {source_path}")
        source_hash = file_sha256(source_path)

        def derive() -> pd.DataFrame:
            source = pd.read_csv(source_path)
            _validate_x1_internal_source(
                source,
                seed=seed,
                n_active=n_active,
                noise_probability=noise_probability,
            )
            return derive_internal_ablation(source)

        return derive, source_path.relative_to(root).as_posix(), source_hash
    n_candidates = int(cell["n_candidates"])
    n_rounds = int(cell["n_rounds"])
    if kind == "max_entropy":
        factory = lambda: run_external_max_entropy_cell(
            seed=seed,
            n_candidates=n_candidates,
            n_rounds=n_rounds,
            n_replications=n_replications,
        )
    elif kind == "bayesian":
        factory = lambda: run_external_bayesian_cell(
            seed=seed,
            n_candidates=n_candidates,
            n_rounds=n_rounds,
            n_replications=n_replications,
        )
    else:
        factory = lambda: run_external_ablation_cell(
            seed=seed,
            n_candidates=n_candidates,
            n_rounds=n_rounds,
            n_replications=n_replications,
        )
    return factory, "", ""


def _validation_arguments(cell: dict[str, Any]) -> dict[str, Any]:
    arguments = {
        "kind": cell["kind"],
        "synthesizer": cell["synthesizer"],
        "seed": int(cell["seed"]),
        "n_replications": int(cell["n_replications"]),
    }
    if cell["synthesizer"] == "internal":
        arguments.update(
            n_active=int(cell["n_active"]),
            noise_probability=float(cell["noise_probability"]),
        )
    else:
        arguments.update(
            n_candidates=int(cell["n_candidates"]),
            n_rounds=int(cell["n_rounds"]),
        )
    return arguments


def _write_execution_log(
    root: Path,
    kind: str,
    records: list[dict[str, Any]],
) -> None:
    log_path = root / f"outputs/stage26X-2/logs/{kind}_run_log.csv"
    atomic_write_csv(pd.DataFrame.from_records(records), log_path)


def execute_registered_kind(root: Path, kind: str) -> tuple[int, int]:
    verify_protected_inputs(root)
    completed = 0
    reused = 0
    records: list[dict[str, Any]] = []
    cells = registered_cells(kind)
    for index, cell in enumerate(cells, start=1):
        output_path = _cell_output_path(root, cell)
        factory, source_path, source_hash = _cell_factory(root, cell)
        started_at = datetime.now(timezone.utc).isoformat()
        started = time.perf_counter()
        record = {
            "cell_id": _cell_id(cell),
            "kind": kind,
            "synthesizer": cell["synthesizer"],
            "seed": cell["seed"],
            "n_active": cell.get("n_active", ""),
            "outcome_noise_probability": cell.get("noise_probability", ""),
            "n_candidates": cell.get("n_candidates", ""),
            "n_rounds": cell.get("n_rounds", ""),
            "replications": cell["n_replications"],
            "started_at_utc": started_at,
            "source_path": source_path,
            "source_sha256": source_hash,
            "output_path": output_path.relative_to(root).as_posix(),
        }
        try:
            frame, status = load_or_run_cell(
                output_path,
                factory,
                **_validation_arguments(cell),
            )
            elapsed = time.perf_counter() - started
            record.update(
                status=status,
                rows=len(frame),
                elapsed_seconds=elapsed,
                output_sha256=file_sha256(output_path),
                error="",
            )
            if status == "completed":
                completed += 1
            else:
                reused += 1
        except Exception as exc:
            record.update(
                status="failed",
                rows=0,
                elapsed_seconds=time.perf_counter() - started,
                output_sha256="",
                error=f"{type(exc).__name__}: {exc}",
            )
            records.append(record)
            _write_execution_log(root, kind, records)
            raise
        records.append(record)
        _write_execution_log(root, kind, records)
        if index % 10 == 0 or index == len(cells):
            print(
                f"{kind}: {index}/{len(cells)} cells; "
                f"completed={completed}, reused={reused}",
                flush=True,
            )
    return completed, reused


def load_registered_kind(root: Path, kind: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for cell in registered_cells(kind):
        path = _cell_output_path(root, cell)
        if not path.is_file():
            raise RuntimeError(f"Registered raw output is missing: {path}")
        frame = pd.read_csv(path)
        validate_raw_cell(frame, **_validation_arguments(cell))
        frame.insert(0, "raw_file", path.relative_to(root).as_posix())
        frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False)


def compute_ablation_effects(seed_level: pd.DataFrame) -> pd.DataFrame:
    effect_frames: list[pd.DataFrame] = []
    specifications = (
        (
            "internal_percentage",
            "internal_full_rule",
            ["seed", "n_active", "outcome_noise_probability"],
        ),
        (
            "external_ordinal",
            "external_full",
            ["seed", "n_candidates", "n_rounds"],
        ),
    )
    for synthesizer, full_name, keys in specifications:
        selected = seed_level.loc[seed_level["synthesizer"].eq(synthesizer)].copy()
        if selected.empty:
            continue
        full = selected.loc[selected["configuration"].eq(full_name), keys + ["coverage", "width"]]
        full = full.rename(
            columns={"coverage": "full_coverage", "width": "full_width"}
        )
        removed = selected.loc[~selected["configuration"].eq(full_name)]
        paired = removed.merge(full, on=keys, how="left", validate="many_to_one")
        if paired[["full_coverage", "full_width"]].isna().any().any():
            raise ValueError(f"Missing full ablation comparator for {synthesizer}.")
        paired["coverage_change"] = paired["coverage"] - paired["full_coverage"]
        paired["width_change"] = paired["width"] - paired["full_width"]
        paired["coverage_improved"] = paired["coverage_change"] > 1e-12
        paired["coverage_worsened"] = paired["coverage_change"] < -1e-12
        effect_frames.append(paired)
    if not effect_frames:
        return pd.DataFrame()
    result = pd.concat(effect_frames, ignore_index=True, sort=False)
    sort_columns = [
        column
        for column in (
            "synthesizer",
            "configuration",
            "n_active",
            "outcome_noise_probability",
            "n_candidates",
            "n_rounds",
            "seed",
        )
        if column in result
    ]
    return result.sort_values(sort_columns, kind="stable").reset_index(drop=True)


def component_overall_summary(effect_summary: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for (synthesizer, configuration), group in effect_summary.groupby(
        ["synthesizer", "configuration"],
        sort=True,
    ):
        weights = pd.to_numeric(group["paired_cells"]).to_numpy(dtype=float)
        records.append(
            {
                "synthesizer": synthesizer,
                "configuration": configuration,
                "registered_regions": len(group),
                "paired_cells": int(weights.sum()),
                "coverage_improved_count": int(group["coverage_improved_count"].sum()),
                "coverage_worsened_count": int(group["coverage_worsened_count"].sum()),
                "coverage_change_mean": float(
                    np.average(group["coverage_change_mean"], weights=weights)
                ),
                "width_change_mean": float(
                    np.average(group["width_change_mean"], weights=weights)
                ),
            }
        )
    return pd.DataFrame.from_records(records)


def atomic_write_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    os.close(handle)
    temporary_path = Path(temporary_name)
    try:
        temporary_path.write_text(text, encoding="utf-8")
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _baseline_summaries(
    maximum_entropy: pd.DataFrame,
    bayesian: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    seed_frames: list[pd.DataFrame] = []
    across_frames: list[pd.DataFrame] = []
    specifications = (
        (
            maximum_entropy,
            "internal_percentage",
            ["synthesizer", "seed", "n_active", "outcome_noise_probability", "method"],
            ["synthesizer", "n_active", "outcome_noise_probability", "method"],
            [
                "point_exact_recovery",
                "normalized_mean_absolute_error",
                "top_choice_accuracy",
                "point_width",
                "outcome_consistent",
                "feasible",
                "solver_success",
            ],
        ),
        (
            maximum_entropy,
            "external_ordinal",
            ["synthesizer", "seed", "n_candidates", "n_rounds", "method"],
            ["synthesizer", "n_candidates", "n_rounds", "method"],
            [
                "point_exact_recovery",
                "normalized_mean_absolute_error",
                "top_choice_accuracy",
                "point_width",
                "feasible",
                "mean_compatible_states",
            ],
        ),
        (
            bayesian,
            "internal_percentage",
            ["synthesizer", "seed", "n_active", "outcome_noise_probability", "method"],
            ["synthesizer", "n_active", "outcome_noise_probability", "method"],
            [
                "coverage",
                "width",
                "posterior_center_error",
                "top_choice_accuracy",
                "accepted_posterior_draws",
                "feasible",
            ],
        ),
        (
            bayesian,
            "external_ordinal",
            ["synthesizer", "seed", "n_candidates", "n_rounds", "method"],
            ["synthesizer", "n_candidates", "n_rounds", "method"],
            [
                "coverage",
                "width",
                "posterior_center_error",
                "top_choice_accuracy",
                "accepted_posterior_states",
                "feasible",
            ],
        ),
    )
    for frame, synthesizer, seed_groups, across_groups, metrics in specifications:
        selected = frame.loc[frame["synthesizer"].eq(synthesizer)].copy()
        seed_level = summarize_seed_level(
            selected,
            group_columns=seed_groups,
            metrics=metrics,
        )
        seed_frames.append(seed_level)
        across_frames.append(
            summarize_across_seeds(
                seed_level,
                group_columns=across_groups,
                metrics=metrics,
            )
        )
    return (
        pd.concat(seed_frames, ignore_index=True, sort=False),
        pd.concat(across_frames, ignore_index=True, sort=False),
    )


def _ablation_summaries(
    ablation: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    seed_frames: list[pd.DataFrame] = []
    across_frames: list[pd.DataFrame] = []
    specifications = (
        (
            "internal_percentage",
            [
                "synthesizer",
                "seed",
                "n_active",
                "outcome_noise_probability",
                "configuration",
            ],
            ["synthesizer", "n_active", "outcome_noise_probability", "configuration"],
            ["coverage", "width", "feasible"],
        ),
        (
            "external_ordinal",
            ["synthesizer", "seed", "n_candidates", "n_rounds", "configuration"],
            ["synthesizer", "n_candidates", "n_rounds", "configuration"],
            ["coverage", "width", "feasible", "false_certainty", "mean_compatible_states"],
        ),
    )
    for synthesizer, seed_groups, across_groups, metrics in specifications:
        selected = ablation.loc[ablation["synthesizer"].eq(synthesizer)].copy()
        seed_level = summarize_seed_level(
            selected,
            group_columns=seed_groups,
            metrics=metrics,
        )
        seed_frames.append(seed_level)
        across_frames.append(
            summarize_across_seeds(
                seed_level,
                group_columns=across_groups,
                metrics=metrics,
            )
        )
    seed_level = pd.concat(seed_frames, ignore_index=True, sort=False)
    across = pd.concat(across_frames, ignore_index=True, sort=False)
    effects = compute_ablation_effects(seed_level)
    effect_summary_frames: list[pd.DataFrame] = []
    for synthesizer, groups in (
        (
            "internal_percentage",
            ["synthesizer", "n_active", "outcome_noise_probability", "configuration"],
        ),
        (
            "external_ordinal",
            ["synthesizer", "n_candidates", "n_rounds", "configuration"],
        ),
    ):
        selected = effects.loc[effects["synthesizer"].eq(synthesizer)].copy()
        summary = summarize_across_seeds(
            selected,
            group_columns=groups,
            metrics=["coverage_change", "width_change"],
        )
        counts = (
            selected.groupby(groups, as_index=False, dropna=False)
            .agg(
                paired_cells=("seed", "size"),
                coverage_improved_count=("coverage_improved", "sum"),
                coverage_worsened_count=("coverage_worsened", "sum"),
            )
        )
        counts["coverage_improved_proportion"] = (
            counts["coverage_improved_count"] / counts["paired_cells"]
        )
        counts["coverage_worsened_proportion"] = (
            counts["coverage_worsened_count"] / counts["paired_cells"]
        )
        effect_summary_frames.append(
            summary.merge(
                counts,
                on=groups,
                how="left",
                validate="one_to_one",
            )
        )
    effect_summary = pd.concat(effect_summary_frames, ignore_index=True, sort=False)
    return seed_level, across, effects, effect_summary


def load_x1_comparator_seed_level(root: Path) -> pd.DataFrame:
    records: list[pd.DataFrame] = []
    for seed in SEEDS:
        for n_active, noise_probability in INTERNAL_GRID:
            path = root / "outputs/stage26X-1/raw" / internal_raw_filename(
                "ablation", seed, n_active, noise_probability
            )
            frame = pd.read_csv(path)
            _validate_x1_internal_source(
                frame,
                seed=seed,
                n_active=n_active,
                noise_probability=noise_probability,
            )
            selected = frame.loc[
                frame["method"].isin(
                    {
                        "rule_aware_partial_identification",
                        "rule_agnostic_partial_identification",
                    }
                )
            ]
            records.append(
                selected.groupby(
                    [
                        "synthesizer",
                        "seed",
                        "n_active",
                        "outcome_noise_probability",
                        "method",
                    ],
                    as_index=False,
                )[["coverage", "width"]].mean()
            )
        for n_candidates, n_rounds in EXTERNAL_GRID:
            path = root / "outputs/stage26X-1/raw" / external_raw_filename(
                "ablation", seed, n_candidates, n_rounds
            )
            frame = pd.read_csv(path)
            selected = frame.loc[
                frame["method"].isin(
                    {"rule_aware_discretion", "rule_agnostic_ordinal"}
                )
            ].copy()
            if len(selected) != 2 * EXTERNAL_REPLICATIONS:
                raise ValueError("Stage 26X-1 source lacks complete external comparator rows.")
            if selected.duplicated(["replication", "method"]).any():
                raise ValueError("Stage 26X-1 external source has duplicate comparator rows.")
            records.append(
                selected.groupby(
                    [
                        "synthesizer",
                        "seed",
                        "n_candidates",
                        "n_rounds",
                        "method",
                    ],
                    as_index=False,
                )[["coverage", "width"]].mean()
            )
    return pd.concat(records, ignore_index=True, sort=False)


def _attribution_analysis(
    x1_seed_level: pd.DataFrame,
    baseline_seed_level: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    structural_frames: list[pd.DataFrame] = []
    bayesian_frames: list[pd.DataFrame] = []
    specifications = (
        (
            "internal_percentage",
            ["seed", "n_active", "outcome_noise_probability"],
            "rule_aware_partial_identification",
            "rule_agnostic_partial_identification",
            "bayesian_truncated_dirichlet",
        ),
        (
            "external_ordinal",
            ["seed", "n_candidates", "n_rounds"],
            "rule_aware_discretion",
            "rule_agnostic_ordinal",
            "bayesian_uniform_rank_posterior",
        ),
    )
    for synthesizer, keys, aware_name, agnostic_name, bayesian_name in specifications:
        x1 = x1_seed_level.loc[x1_seed_level["synthesizer"].eq(synthesizer)]
        aware = x1.loc[x1["method"].eq(aware_name), keys + ["coverage", "width"]]
        agnostic = x1.loc[x1["method"].eq(agnostic_name), keys + ["coverage", "width"]]
        structural = aware.merge(
            agnostic,
            on=keys,
            suffixes=("_aware", "_agnostic"),
            validate="one_to_one",
        )
        structural.insert(0, "synthesizer", synthesizer)
        structural["structural_width_lower"] = (
            structural["width_aware"] < structural["width_agnostic"] - 1e-12
        )
        if synthesizer == "internal_percentage":
            structural["parameter_region"] = structural.apply(
                lambda row: (
                    f"internal n={int(row['n_active'])}, "
                    f"noise={float(row['outcome_noise_probability']):.2f}"
                ),
                axis=1,
            )
        else:
            structural["parameter_region"] = structural.apply(
                lambda row: (
                    f"external candidates={int(row['n_candidates'])}, "
                    f"rounds={int(row['n_rounds'])}"
                ),
                axis=1,
            )
        structural_frames.append(structural)

        bayesian = baseline_seed_level.loc[
            baseline_seed_level["synthesizer"].eq(synthesizer)
            & baseline_seed_level["method"].eq(bayesian_name),
            keys + ["coverage", "width", "feasible"],
        ]
        paired = aware.merge(
            bayesian,
            on=keys,
            suffixes=("_aware", "_bayesian"),
            validate="one_to_one",
        )
        paired.insert(0, "synthesizer", synthesizer)
        paired["clean_cell"] = (
            paired["outcome_noise_probability"].eq(0.0)
            if synthesizer == "internal_percentage"
            else True
        )
        aware_weak = (
            (paired["coverage_aware"] >= paired["coverage_bayesian"] - 1e-12)
            & (paired["width_aware"] <= paired["width_bayesian"] + 1e-12)
        )
        aware_strict = (
            (paired["coverage_aware"] > paired["coverage_bayesian"] + 1e-12)
            | (paired["width_aware"] < paired["width_bayesian"] - 1e-12)
        )
        bayesian_weak = (
            (paired["coverage_bayesian"] >= paired["coverage_aware"] - 1e-12)
            & (paired["width_bayesian"] <= paired["width_aware"] + 1e-12)
        )
        bayesian_strict = (
            (paired["coverage_bayesian"] > paired["coverage_aware"] + 1e-12)
            | (paired["width_bayesian"] < paired["width_aware"] - 1e-12)
        )
        paired["aware_pareto_dominates"] = aware_weak & aware_strict
        paired["bayesian_pareto_dominates"] = bayesian_weak & bayesian_strict
        paired["parameter_region"] = structural["parameter_region"].to_numpy()
        bayesian_frames.append(paired)

    structural = pd.concat(structural_frames, ignore_index=True, sort=False)
    bayesian_pairs = pd.concat(bayesian_frames, ignore_index=True, sort=False)
    structural_regions = (
        structural.groupby("parameter_region", as_index=False)
        .agg(
            synthesizer=("synthesizer", "first"),
            paired_cells=("seed", "size"),
            width_lower_count=("structural_width_lower", "sum"),
            width_lower_proportion=("structural_width_lower", "mean"),
        )
    )
    structural_regions["majority_reversal"] = (
        structural_regions["width_lower_proportion"] < 0.5
    )
    clean = bayesian_pairs.loc[bayesian_pairs["clean_cell"]].copy()
    bayesian_regions = (
        clean.groupby("parameter_region", as_index=False)
        .agg(
            synthesizer=("synthesizer", "first"),
            paired_cells=("seed", "size"),
            aware_pareto_count=("aware_pareto_dominates", "sum"),
            aware_pareto_proportion=("aware_pareto_dominates", "mean"),
            bayesian_pareto_count=("bayesian_pareto_dominates", "sum"),
            bayesian_pareto_proportion=("bayesian_pareto_dominates", "mean"),
        )
    )
    bayesian_regions["majority_reversal"] = (
        bayesian_regions["bayesian_pareto_proportion"] > 0.5
    )
    structural_ordering = float(structural["structural_width_lower"].mean())
    structural_reversals = int(structural_regions["majority_reversal"].sum())
    aware_pareto = float(clean["aware_pareto_dominates"].mean())
    bayesian_reversals = int(bayesian_regions["majority_reversal"].sum())
    bayesian_dominates = float(clean["bayesian_pareto_dominates"].mean())
    ruling = select_attribution_ruling(
        structural_width_ordering_proportion=structural_ordering,
        structural_majority_reversal_regions=structural_reversals,
        structural_region_count=len(structural_regions),
        bayesian_clean_pareto_proportion=aware_pareto,
        bayesian_majority_reversal_regions=bayesian_reversals,
        bayesian_dominates_proportion=bayesian_dominates,
    )
    statistics = {
        "structural_cell_count": len(structural),
        "structural_width_lower_count": int(structural["structural_width_lower"].sum()),
        "structural_width_ordering_proportion": structural_ordering,
        "structural_region_count": len(structural_regions),
        "structural_majority_reversal_regions": structural_reversals,
        "clean_bayesian_cell_count": len(clean),
        "aware_pareto_count": int(clean["aware_pareto_dominates"].sum()),
        "aware_pareto_proportion": aware_pareto,
        "bayesian_pareto_count": int(clean["bayesian_pareto_dominates"].sum()),
        "bayesian_dominates_proportion": bayesian_dominates,
        "bayesian_majority_reversal_regions": bayesian_reversals,
        "ruling": ruling,
    }
    region_evidence = structural_regions.merge(
        bayesian_regions,
        on=["parameter_region", "synthesizer"],
        how="outer",
        suffixes=("_structural", "_bayesian"),
    )
    return statistics, bayesian_pairs, region_evidence


def _format_interval(mean: Any, lower: Any, upper: Any) -> str:
    if pd.isna(mean):
        return "MISSING"
    return f"{float(mean):.6f} [{float(lower):.6f}, {float(upper):.6f}]"


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def create_baseline_report(
    root: Path,
    maximum_entropy: pd.DataFrame,
    bayesian: pd.DataFrame,
    baseline_across: pd.DataFrame,
    protected_hashes: dict[str, str],
) -> str:
    point = baseline_across.loc[
        baseline_across["method"].isin(
            {"maximum_entropy_center", "maximum_entropy_rank_center"}
        )
    ].copy()
    point_table = point[
        [
            column
            for column in (
                "synthesizer",
                "n_active",
                "outcome_noise_probability",
                "n_candidates",
                "n_rounds",
                "method",
                "seed_count",
                "point_exact_recovery_mean",
                "normalized_mean_absolute_error_mean",
                "top_choice_accuracy_mean",
                "feasible_mean",
            )
            if column in point
        ]
    ]
    interval = baseline_across.loc[
        baseline_across["method"].isin(
            {"bayesian_truncated_dirichlet", "bayesian_uniform_rank_posterior"}
        )
    ].copy()
    interval["coverage_seed_interval"] = interval.apply(
        lambda row: _format_interval(
            row["coverage_mean"], row["coverage_q025"], row["coverage_q975"]
        ),
        axis=1,
    )
    interval["width_seed_interval"] = interval.apply(
        lambda row: _format_interval(
            row["width_mean"], row["width_q025"], row["width_q975"]
        ),
        axis=1,
    )
    interval_table = interval[
        [
            column
            for column in (
                "synthesizer",
                "n_active",
                "outcome_noise_probability",
                "n_candidates",
                "n_rounds",
                "method",
                "seed_count",
                "coverage_seed_interval",
                "width_seed_interval",
                "posterior_center_error_mean",
                "top_choice_accuracy_mean",
                "feasible_mean",
            )
            if column in interval
        ]
    ]
    max_log = pd.read_csv(root / "outputs/stage26X-2/logs/max_entropy_run_log.csv")
    bayes_log = pd.read_csv(root / "outputs/stage26X-2/logs/bayesian_run_log.csv")
    posterior_status = (
        bayesian["posterior_status"].fillna("MISSING").value_counts().rename_axis("status").reset_index(name="rows")
    )
    lines = [
        "# Stage 26X-2 Same-Information Baseline Implementation",
        "",
        "## Protected inputs",
        "",
    ]
    lines.extend(f"- `{path}`: SHA256 `{digest}`." for path, digest in protected_hashes.items())
    lines.extend(
        [
            "",
            "## Independent implementations and evidence paths",
            "",
            "| Baseline | Implementation file | Functions | Raw outputs | Execution log |",
            "|---|---|---|---|---|",
            "| Maximum-entropy / uniform compatible-state center | `src/max_entropy_center_baseline.py` | `solve_max_entropy_point`; `maximum_entropy_rank_center` | `outputs/stage26X-2/raw/max_entropy/` | `outputs/stage26X-2/logs/max_entropy_run_log.csv` |",
            "| Bayesian latent preference | `src/bayesian_latent_preference_baseline.py` | `truncated_dirichlet_interval`; `exact_rank_posterior_interval` | `outputs/stage26X-2/raw/bayesian/` | `outputs/stage26X-2/logs/bayesian_run_log.csv` |",
            "",
            f"Maximum-entropy raw cells: `{max_log['cell_id'].nunique()}`; log rows with status `completed` or `reused`: `{int(max_log['status'].isin(['completed', 'reused']).sum())}`; raw replication rows: `{len(maximum_entropy)}`.",
            f"Bayesian raw cells: `{bayes_log['cell_id'].nunique()}`; log rows with status `completed` or `reused`: `{int(bayes_log['status'].isin(['completed', 'reused']).sum())}`; raw replication rows: `{len(bayesian)}`.",
            "",
            "## Information-set alignment",
            "",
            "| Information item | Rule-aware comparator | Maximum-entropy center | Bayesian baseline | Alignment |",
            "|---|---|---|---|---|",
            "| Candidate identities and active set | Supplied | Supplied | Supplied | Same |",
            "| Expert shares (internal) or expert scores (external) | Supplied | Supplied | Supplied | Same |",
            "| Observed elimination outcome | Supplied | Supplied | Supplied | Same |",
            "| Percentage-elimination inequalities (internal) | Applied | Applied unchanged | Applied unchanged as zero-one likelihood | Same |",
            "| Dense-rank tie policy and weak-save intervention rule (external) | Applied | Applied unchanged | Applied unchanged as zero-one likelihood | Same |",
            "| Synthetic latent truth | Evaluation only | Evaluation only | Evaluation only | Same; unavailable to fitted methods |",
            "| Outcome-noise flag | Evaluation only | Not supplied | Not supplied | Same substantive information |",
            "| Prior random draws | Not applicable | Not applicable | Computational approximation only | Not institutional information |",
            "",
            "The maximum-entropy and Bayesian methods reconstruct each generated case independently from the registered observed inputs. Their raw files and logs are separate, and neither method reads another baseline's output.",
            "",
            "## Solver and prior settings",
            "",
            "- Internal maximum entropy: SciPy SLSQP over the exact rule-aware polytope; `maxiter=500`, `ftol=1e-10`, log floor `1e-12`, feasibility tolerance `1e-8`; initialization comes from `scipy.optimize.linprog`.",
            "- External maximum entropy: exact enumeration of compatible strict rankings and their uniform-state expected rank.",
            "- Internal Bayesian: symmetric `Dirichlet(1)` prior; `8192` fixed draws per seed-parameter cell; prior stream `seed + round(noise*1000) + 2620000`; no adaptive resampling; minimum accepted draws `100`; equal-tail probabilities `0.025` and `0.975`.",
            "- External Bayesian: exact uniform posterior over compatible strict rankings; equal-tail probabilities `0.025` and `0.975`.",
            "",
            "## Point-baseline results",
            "",
            "`point_exact_recovery`, normalized mean absolute error, and top-choice accuracy evaluate a point estimate. `point_width=0` is a definition of a point output and is not interval coverage or a feasible-set width advantage.",
            "",
            point_table.to_markdown(index=False, floatfmt=".6f"),
            "",
            "## Bayesian interval results",
            "",
            "Intervals below are the empirical 2.5%-97.5% range of the 20 seed-level metric means. Replications are first averaged within seed and parameter cell.",
            "",
            interval_table.to_markdown(index=False, floatfmt=".6f"),
            "",
            "### Posterior-status rows",
            "",
            posterior_status.to_markdown(index=False),
            "",
            "Coverage, width, posterior-center error, and top-choice means are computed only where the fixed draw bank produced a defined posterior. Rows below the registered minimum remain in the raw outputs as `insufficient_posterior_draws`; `feasible_mean` retains the complete replication denominator and reports the defined-posterior rate. No draw bank was enlarged and no raw row was deleted.",
            "",
            "The results are generated from the registered synthetic generators. They do not constitute user validation or recovery of true preferences in an observed population.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def create_ablation_report(
    ablation: pd.DataFrame,
    ablation_across: pd.DataFrame,
    effect_summary: pd.DataFrame,
) -> str:
    result_table = ablation_across.copy()
    result_table["coverage"] = result_table.apply(
        lambda row: _format_interval(
            row["coverage_mean"], row["coverage_q025"], row["coverage_q975"]
        ),
        axis=1,
    )
    result_table["width"] = result_table.apply(
        lambda row: _format_interval(
            row["width_mean"], row["width_q025"], row["width_q975"]
        ),
        axis=1,
    )
    toggles = (
        ablation[["configuration", "elimination", "tie", "save", "disclosure"]]
        .drop_duplicates()
        .copy()
    )
    result_table = result_table.merge(toggles, on="configuration", how="left")
    display_results = result_table[
        [
            column
            for column in (
                "synthesizer",
                "n_active",
                "outcome_noise_probability",
                "n_candidates",
                "n_rounds",
                "configuration",
                "elimination",
                "tie",
                "save",
                "disclosure",
                "coverage",
                "width",
                "seed_count",
            )
            if column in result_table
        ]
    ]
    effect_display = effect_summary[
        [
            column
            for column in (
                "synthesizer",
                "n_active",
                "outcome_noise_probability",
                "n_candidates",
                "n_rounds",
                "configuration",
                "paired_cells",
                "coverage_change_mean",
                "coverage_change_q025",
                "coverage_change_q975",
                "coverage_improved_count",
                "coverage_improved_proportion",
                "coverage_worsened_count",
                "width_change_mean",
                "width_change_q025",
                "width_change_q975",
            )
            if column in effect_summary
        ]
    ]
    improvements = effect_summary.loc[
        effect_summary["coverage_improved_count"].gt(0)
    ].copy()
    overall = component_overall_summary(effect_summary)
    largest = overall.loc[
        overall.groupby("synthesizer")["width_change_mean"].idxmax()
    ][
        [
            "synthesizer",
            "configuration",
            "registered_regions",
            "paired_cells",
            "width_change_mean",
            "coverage_change_mean",
        ]
    ]
    ablation_log_status = (
        ablation["raw_file"].nunique()
        if "raw_file" in ablation
        else 0
    )
    lines = [
        "# Stage 26X-2 Rule-Component Ablation Results",
        "",
        "## Execution scope",
        "",
        f"- Registered raw cells: `{ablation_log_status}`; raw rows: `{len(ablation)}`.",
        "- Internal percentage model: full rule and elimination-off. Tie, save, and disclosure are not applicable to this synthesizer.",
        "- External ordinal model: full configuration plus one-at-a-time removal of elimination, tie handling, save handling, and disclosure.",
        "- All configurations use the same 20 seeds, registered parameter grid, and generated case within each replication.",
        "- External disclosure is the testbed's existing synthetic pairwise relation between its top two latent priorities; it is generated as part of the synthetic case.",
        "",
        "## Configuration results",
        "",
        "Coverage and width entries show the mean and empirical 2.5%-97.5% interval across 20 seed-level means.",
        "",
        display_results.to_markdown(index=False),
        "",
        "## Paired leave-one-out effects",
        "",
        "Changes are `component removed - full configuration` within the same seed and parameter cell. A positive coverage change is an improvement; a positive width change is a wider identified set.",
        "",
        effect_display.to_markdown(index=False, floatfmt=".6f"),
        "",
        "## Component removals with a coverage improvement",
        "",
    ]
    if improvements.empty:
        lines.append("No registered component removal has a strictly positive seed-cell coverage change.")
    else:
        lines.extend(
            [
                improvements[
                    [
                        column
                        for column in (
                            "synthesizer",
                            "n_active",
                            "outcome_noise_probability",
                            "n_candidates",
                            "n_rounds",
                            "configuration",
                            "coverage_improved_count",
                            "paired_cells",
                            "coverage_change_mean",
                            "width_change_mean",
                        )
                        if column in improvements
                    ]
                ].to_markdown(index=False, floatfmt=".6f")
            ]
        )
    lines.extend(
        [
            "",
            "## Component effects across all registered regions",
            "",
            "Means in this table pool the paired seed-parameter cells for each component; every registered region has 20 seeds.",
            "",
            overall.to_markdown(index=False, floatfmt=".6f"),
            "",
            "## Largest width-contraction contribution",
            "",
            "Within each synthesizer, this is the component removal with the largest mean positive width change across all of its registered seed-parameter cells. It describes the greatest one-at-a-time contribution among the registered components, not a causal interaction effect.",
            "",
            largest.to_markdown(index=False, floatfmt=".6f"),
            "",
            "## Interaction effects",
            "",
            "Cannot be estimated from this leave-one-out design. No joint two-component or higher-order removal was preregistered, so interaction terms are not identified by these outputs.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def create_attribution_report(
    statistics: dict[str, Any],
    region_evidence: pd.DataFrame,
    effect_summary: pd.DataFrame,
) -> str:
    ruling = str(statistics["ruling"])
    coverage_improvements = effect_summary.loc[
        effect_summary["coverage_improved_count"].gt(0)
    ]
    lines = [
        "# Stage 26X-2 Attribution Ruling",
        "",
        "## Registered evidence tests",
        "",
        f"- Stage 26X-1 structural width ordering: `{statistics['structural_width_lower_count']}/{statistics['structural_cell_count']}` paired seed-parameter cells (`{statistics['structural_width_ordering_proportion']:.6f}`); majority-reversal regions: `{statistics['structural_majority_reversal_regions']}/{statistics['structural_region_count']}`.",
        f"- Clean same-information Bayesian comparison: rule-aware Pareto dominance in `{statistics['aware_pareto_count']}/{statistics['clean_bayesian_cell_count']}` cells (`{statistics['aware_pareto_proportion']:.6f}`).",
        f"- Bayesian Pareto dominance over rule-aware in `{statistics['bayesian_pareto_count']}/{statistics['clean_bayesian_cell_count']}` clean cells (`{statistics['bayesian_dominates_proportion']:.6f}`); majority-reversal regions: `{statistics['bayesian_majority_reversal_regions']}`.",
        "- Maximum-entropy point outputs are excluded from the coverage-width Pareto test. Their zero point width is not treated as interval evidence.",
        f"- Fixed-draw internal Bayesian rows without a defined posterior: `{statistics['posterior_insufficient_total']}` overall, including `{statistics['posterior_insufficient_clean']}` under zero outcome noise. They remain in the raw evidence; interval metrics use defined-posterior rows and the baseline report separately gives the complete-denominator feasible rate.",
        "",
        "## Region evidence",
        "",
        region_evidence.to_markdown(index=False, floatfmt=".6f"),
        "",
        "## Component attribution",
        "",
        "The leave-one-out results identify paired changes associated with removing one registered rule component. They do not identify component interactions or effects outside the registered synthetic mechanisms.",
        "",
    ]
    if coverage_improvements.empty:
        lines.append("No component removal improves coverage in any registered seed-parameter cell.")
    else:
        lines.extend(
            [
                coverage_improvements[
                    [
                        column
                        for column in (
                            "synthesizer",
                            "n_active",
                            "outcome_noise_probability",
                            "n_candidates",
                            "n_rounds",
                            "configuration",
                            "coverage_improved_count",
                            "paired_cells",
                            "coverage_change_mean",
                            "width_change_mean",
                        )
                        if column in coverage_improvements
                    ]
                ].to_markdown(index=False, floatfmt=".6f")
            ]
        )
    lines.extend(["", "## Unresolved explanations", ""])
    lines.extend(
        [
            "- The synthetic generators do not establish recovery of latent public preference in an observed population.",
            "- The Bayesian interval depends on the preregistered `Dirichlet(1)` or uniform-ranking prior and the zero-one constraint likelihood; other priors were not tested.",
            "- The leave-one-out design cannot separate component interactions.",
            "- The external pairwise disclosure is synthetic and generated from the simulated latent ordering; no empirical disclosure process was observed.",
            "",
            "## Ruling",
            "",
            ruling,
            "",
        ]
    )
    if ruling == "RULE_AWARE_ADVANTAGE_SUBSTANTIATED":
        lines.append(
            "Under the registered synthetic grids, the clean-cell same-information Bayesian comparison meets the preregistered Pareto threshold. This does not establish user effects, organizational impact, or universal superiority."
        )
    elif ruling == "RULE_AWARE_ADVANTAGE_STRUCTURAL_ONLY":
        lines.append(
            "The width ordering remains the structural feasible-set result guaranteed by the added constraints, while the preregistered same-information Pareto threshold is not met. The manuscript contribution must therefore be positioned as a formal partial-identification framework, feasible-set characterization, and quantified coverage-width tradeoff rather than a generally superior inference method."
        )
    else:
        lines.append(
            "The registered evidence does not support a rule-aware advantage under the locked criteria. Claims of method-level superiority must be removed; only formal definitions and directly established mathematical results remain attributable."
        )
    return "\n".join(lines).rstrip() + "\n"


def generate_reports(root: Path) -> dict[str, Any]:
    protected_hashes = verify_protected_inputs(root)
    maximum_entropy = load_registered_kind(root, "max_entropy")
    bayesian = load_registered_kind(root, "bayesian")
    ablation = load_registered_kind(root, "ablation")
    baseline_seed, baseline_across = _baseline_summaries(maximum_entropy, bayesian)
    ablation_seed, ablation_across, effects, effect_summary = _ablation_summaries(ablation)
    x1_seed = load_x1_comparator_seed_level(root)
    statistics, bayesian_pairs, region_evidence = _attribution_analysis(
        x1_seed,
        baseline_seed,
    )
    insufficient = bayesian["posterior_status"].ne("ok")
    clean_internal = (
        bayesian["synthesizer"].eq("internal_percentage")
        & bayesian["outcome_noise_probability"].eq(0.0)
    )
    statistics["posterior_insufficient_total"] = int(insufficient.sum())
    statistics["posterior_insufficient_clean"] = int(
        (insufficient & clean_internal).sum()
    )
    tables = root / "outputs/stage26X-2/tables"
    table_outputs = {
        "baseline_seed_level.csv": baseline_seed,
        "baseline_across_seed.csv": baseline_across,
        "ablation_seed_level.csv": ablation_seed,
        "ablation_across_seed.csv": ablation_across,
        "ablation_paired_effects.csv": effects,
        "ablation_effect_summary.csv": effect_summary,
        "x1_comparator_seed_level.csv": x1_seed,
        "attribution_pairwise_cells.csv": bayesian_pairs,
        "attribution_regions.csv": region_evidence,
    }
    for filename, frame in table_outputs.items():
        atomic_write_csv(frame, tables / filename)
    atomic_write_text(
        create_baseline_report(
            root,
            maximum_entropy,
            bayesian,
            baseline_across,
            protected_hashes,
        ),
        root / "outputs/stage26X-2/BASELINE_IMPLEMENTATION.md",
    )
    atomic_write_text(
        create_ablation_report(ablation, ablation_across, effect_summary),
        root / "outputs/stage26X-2/ABLATION_RESULTS.md",
    )
    atomic_write_text(
        create_attribution_report(statistics, region_evidence, effect_summary),
        root / "outputs/stage26X-2/ATTRIBUTION_RULING.md",
    )
    return statistics


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_preregistered_design(root: Path) -> str:
    observed = file_sha256(root / PREREGISTERED_DESIGN)
    if observed != PREREGISTERED_DESIGN_SHA256:
        raise RuntimeError(
            "Stage 26X-2 preregistration hash mismatch: "
            f"expected {PREREGISTERED_DESIGN_SHA256}, observed {observed}."
        )
    return observed


def verify_protected_inputs(root: Path) -> dict[str, str]:
    observed = {PREREGISTERED_DESIGN.as_posix(): verify_preregistered_design(root)}
    for relative_path, expected in PROTECTED_INPUT_HASHES.items():
        path = root / relative_path
        if not path.is_file():
            raise RuntimeError(f"Required protected input is missing: {relative_path}")
        actual = file_sha256(path)
        if actual != expected:
            raise RuntimeError(
                f"Protected input hash mismatch for {relative_path}: "
                f"expected {expected}, observed {actual}."
            )
        observed[relative_path.as_posix()] = actual
    return observed


def _point_metrics(point: np.ndarray, truth: np.ndarray) -> dict[str, float]:
    point = np.asarray(point, dtype=float)
    truth = np.asarray(truth, dtype=float)
    return {
        "point_exact_recovery": float(np.allclose(point, truth, atol=1e-8, rtol=0.0)),
        "normalized_mean_absolute_error": float(np.abs(point - truth).mean()),
        "top_choice_accuracy": float(int(np.argmax(point)) == int(np.argmax(truth))),
        "point_width": 0.0,
    }


def run_internal_max_entropy_cell(
    *,
    seed: int,
    n_active: int,
    noise_probability: float,
    n_replications: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + int(round(noise_probability * 1_000)))
    records: list[dict[str, Any]] = []
    for replication in range(n_replications):
        case = generate_percentage_case(
            rng,
            n_active=n_active,
            outcome_noise_probability=noise_probability,
        )
        constraints = base_percentage_constraints(case, include_elimination_constraint=True)
        result = solve_max_entropy_point(
            A_ub=constraints[0],
            b_ub=constraints[1],
            A_eq=constraints[2],
            b_eq=constraints[3],
            bounds=constraints[4],
        )
        metrics = (
            _point_metrics(result.point, case.public_preference)
            if result.solver_success
            else {
                "point_exact_recovery": np.nan,
                "normalized_mean_absolute_error": np.nan,
                "top_choice_accuracy": np.nan,
                "point_width": 0.0,
            }
        )
        records.append(
            {
                "synthesizer": "internal_percentage",
                "seed": seed,
                "n_active": n_active,
                "outcome_noise_probability": noise_probability,
                "replication": replication,
                "method": "maximum_entropy_center",
                **metrics,
                "outcome_consistent": float(
                    result.solver_success and point_is_outcome_consistent(result.point, case)
                ),
                "feasible": result.feasible,
                "solver_success": result.solver_success,
                "solver_iterations": result.iterations,
                "solver_objective": result.objective,
                "observed_outcome_noise": case.observed_outcome_noise,
            }
        )
    return pd.DataFrame.from_records(records)


def run_internal_bayesian_cell(
    *,
    seed: int,
    n_active: int,
    noise_probability: float,
    n_replications: int,
) -> pd.DataFrame:
    case_rng = np.random.default_rng(seed + int(round(noise_probability * 1_000)))
    prior_rng = np.random.default_rng(
        seed + int(round(noise_probability * 1_000)) + 2_620_000
    )
    prior_draws = prior_rng.dirichlet(np.ones(n_active), size=BAYESIAN_PRIOR_DRAWS)
    records: list[dict[str, Any]] = []
    for replication in range(n_replications):
        case = generate_percentage_case(
            case_rng,
            n_active=n_active,
            outcome_noise_probability=noise_probability,
        )
        A_ub, b_ub, _, _, _ = base_percentage_constraints(
            case,
            include_elimination_constraint=True,
        )
        result = truncated_dirichlet_interval(
            prior_draws,
            A_ub=A_ub,
            b_ub=b_ub,
            min_accepted=BAYESIAN_MIN_ACCEPTED,
        )
        if result.feasible:
            coverage = float(
                np.all(case.public_preference >= result.lower - 1e-8)
                and np.all(case.public_preference <= result.upper + 1e-8)
            )
            width = float(np.mean(result.upper - result.lower))
            center_error = float(np.abs(result.center - case.public_preference).mean())
            top_choice = float(
                int(np.argmax(result.center)) == int(np.argmax(case.public_preference))
            )
        else:
            coverage = width = center_error = top_choice = np.nan
        records.append(
            {
                "synthesizer": "internal_percentage",
                "seed": seed,
                "n_active": n_active,
                "outcome_noise_probability": noise_probability,
                "replication": replication,
                "method": "bayesian_truncated_dirichlet",
                "coverage": coverage,
                "width": width,
                "posterior_center_error": center_error,
                "top_choice_accuracy": top_choice,
                "accepted_posterior_draws": result.accepted_count,
                "posterior_status": result.status,
                "feasible": result.feasible,
                "observed_outcome_noise": case.observed_outcome_noise,
            }
        )
    return pd.DataFrame.from_records(records)


@lru_cache(maxsize=None)
def _cached_fan_ranks(n_active: int) -> np.ndarray:
    return _all_fan_ranks(n_active)


def _compatible_external_states(
    round_input: Any,
    intervention: bool,
) -> np.ndarray:
    scores = np.asarray(
        [round_input.expert_scores[name] for name in round_input.active_candidates],
        dtype=float,
    )
    judge_ranks = compute_judge_ranks(scores, "dense_rank")
    states = _cached_fan_ranks(len(round_input.active_candidates))
    mask = _method_mask(
        "rule_aware_discretion",
        states,
        judge_ranks,
        round_input,
        intervention,
    )
    return states[mask]


def run_external_max_entropy_cell(
    *,
    seed: int,
    n_candidates: int,
    n_rounds: int,
    n_replications: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records: list[dict[str, Any]] = []
    for replication in range(n_replications):
        case = generate_external_case(rng, n_candidates=n_candidates, n_rounds=n_rounds)
        exact: list[float] = []
        errors: list[float] = []
        top_choices: list[float] = []
        state_counts: list[int] = []
        for round_input, truth, intervention in zip(
            case.rounds,
            case.public_ranks,
            case.intervention_rounds,
        ):
            states = _compatible_external_states(round_input, intervention)
            center = maximum_entropy_rank_center(states)
            exact.append(float(np.allclose(center, truth, atol=1e-8, rtol=0.0)))
            errors.append(float(np.abs(center - truth).mean() / (len(truth) - 1)))
            top_choices.append(float(int(np.argmin(center)) == int(np.argmin(truth))))
            state_counts.append(int(len(states)))
        records.append(
            {
                "synthesizer": "external_ordinal",
                "seed": seed,
                "n_candidates": n_candidates,
                "n_rounds": n_rounds,
                "replication": replication,
                "method": "maximum_entropy_rank_center",
                "point_exact_recovery": float(all(value == 1.0 for value in exact)),
                "normalized_mean_absolute_error": float(np.mean(errors)),
                "top_choice_accuracy": float(np.mean(top_choices)),
                "point_width": 0.0,
                "feasible": bool(all(count > 0 for count in state_counts)),
                "mean_compatible_states": float(np.mean(state_counts)),
            }
        )
    return pd.DataFrame.from_records(records)


def run_external_bayesian_cell(
    *,
    seed: int,
    n_candidates: int,
    n_rounds: int,
    n_replications: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records: list[dict[str, Any]] = []
    for replication in range(n_replications):
        case = generate_external_case(rng, n_candidates=n_candidates, n_rounds=n_rounds)
        covered: list[float] = []
        widths: list[float] = []
        errors: list[float] = []
        top_choices: list[float] = []
        state_counts: list[int] = []
        for round_input, truth, intervention in zip(
            case.rounds,
            case.public_ranks,
            case.intervention_rounds,
        ):
            states = _compatible_external_states(round_input, intervention)
            result = exact_rank_posterior_interval(states)
            covered.append(
                float(
                    result.feasible
                    and np.all(truth >= result.lower - 1e-8)
                    and np.all(truth <= result.upper + 1e-8)
                )
            )
            widths.append(float(np.mean(result.upper - result.lower) / (len(truth) - 1)))
            errors.append(float(np.abs(result.center - truth).mean() / (len(truth) - 1)))
            top_choices.append(
                float(int(np.argmin(result.center)) == int(np.argmin(truth)))
            )
            state_counts.append(result.accepted_count)
        records.append(
            {
                "synthesizer": "external_ordinal",
                "seed": seed,
                "n_candidates": n_candidates,
                "n_rounds": n_rounds,
                "replication": replication,
                "method": "bayesian_uniform_rank_posterior",
                "coverage": float(all(value == 1.0 for value in covered)),
                "width": float(np.mean(widths)),
                "posterior_center_error": float(np.mean(errors)),
                "top_choice_accuracy": float(np.mean(top_choices)),
                "accepted_posterior_states": float(np.mean(state_counts)),
                "posterior_status": "ok",
                "feasible": bool(all(count > 0 for count in state_counts)),
            }
        )
    return pd.DataFrame.from_records(records)


def run_external_ablation_cell(
    *,
    seed: int,
    n_candidates: int,
    n_rounds: int,
    n_replications: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records: list[dict[str, Any]] = []
    for replication in range(n_replications):
        case = generate_external_case(rng, n_candidates=n_candidates, n_rounds=n_rounds)
        for row in external_case_ablation(case):
            records.append(
                {
                    "synthesizer": "external_ordinal",
                    "seed": seed,
                    "n_candidates": n_candidates,
                    "n_rounds": n_rounds,
                    "replication": replication,
                    **row,
                }
            )
    return pd.DataFrame.from_records(records)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the hash-gated Stage 26X-2 real baselines and component ablations."
    )
    parser.add_argument(
        "--mode",
        choices=("run", "max-entropy", "bayesian", "ablation", "summarize", "smoke"),
        default="run",
        help=(
            "run executes/resumes both baselines and ablation, then summarizes; "
            "the three named modes execute one independent output family; "
            "summarize requires all registered raw files; smoke writes nothing."
        ),
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    verify_protected_inputs(root)
    started = time.perf_counter()
    if args.mode == "smoke":
        run_internal_max_entropy_cell(
            seed=SEEDS[0], n_active=4, noise_probability=0.0, n_replications=1
        )
        run_internal_bayesian_cell(
            seed=SEEDS[0], n_active=4, noise_probability=0.0, n_replications=1
        )
        run_external_max_entropy_cell(
            seed=SEEDS[0], n_candidates=6, n_rounds=3, n_replications=1
        )
        run_external_bayesian_cell(
            seed=SEEDS[0], n_candidates=6, n_rounds=3, n_replications=1
        )
        run_external_ablation_cell(
            seed=SEEDS[0], n_candidates=6, n_rounds=3, n_replications=1
        )
        print(
            f"Stage 26X-2 smoke test completed in "
            f"{time.perf_counter() - started:.3f} seconds."
        )
        return 0
    mode_to_kind = {
        "max-entropy": "max_entropy",
        "bayesian": "bayesian",
        "ablation": "ablation",
    }
    if args.mode in mode_to_kind:
        kind = mode_to_kind[args.mode]
        completed, reused = execute_registered_kind(root, kind)
        print(
            f"Stage 26X-2 {kind} completed={completed}, reused={reused} "
            f"in {time.perf_counter() - started:.3f} seconds."
        )
        return 0
    if args.mode == "run":
        for kind in RAW_KINDS:
            completed, reused = execute_registered_kind(root, kind)
            print(f"{kind}: completed={completed}, reused={reused}", flush=True)
    statistics = generate_reports(root)
    print(
        f"Stage 26X-2 {args.mode} finished in "
        f"{time.perf_counter() - started:.3f} seconds; "
        f"ruling={statistics['ruling']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
