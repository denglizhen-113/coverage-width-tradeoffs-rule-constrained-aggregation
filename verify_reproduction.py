#!/usr/bin/env python3
"""Verify staged main tables, figures, raw counts, and integrated manuscript."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from PIL import Image
from pandas.api.types import is_numeric_dtype


ROOT = Path(__file__).resolve().parent
ATOL = 1e-12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_csv(actual: Path, expected: Path) -> dict[str, Any]:
    if not actual.is_file() or not expected.is_file():
        return {
            "status": "fail",
            "actual": actual.as_posix(),
            "expected": expected.as_posix(),
            "reason": "missing file",
        }
    left = pd.read_csv(actual)
    right = pd.read_csv(expected)
    if left.shape != right.shape or list(left.columns) != list(right.columns):
        return {
            "status": "fail",
            "actual": actual.as_posix(),
            "expected": expected.as_posix(),
            "reason": f"shape/schema mismatch: {left.shape} vs {right.shape}",
        }

    max_abs_difference = 0.0
    for column in left.columns:
        if is_numeric_dtype(left[column]) and is_numeric_dtype(right[column]):
            a = left[column].to_numpy(dtype=float)
            b = right[column].to_numpy(dtype=float)
            finite = np.isfinite(a) & np.isfinite(b)
            if finite.any():
                max_abs_difference = max(
                    max_abs_difference, float(np.max(np.abs(a[finite] - b[finite])))
                )
            if not np.allclose(a, b, rtol=0.0, atol=ATOL, equal_nan=True):
                return {
                    "status": "fail",
                    "actual": actual.as_posix(),
                    "expected": expected.as_posix(),
                    "reason": f"numeric mismatch in {column}",
                    "max_abs_difference": max_abs_difference,
                }
        else:
            a = left[column].fillna("<NA>").astype(str).tolist()
            b = right[column].fillna("<NA>").astype(str).tolist()
            if a != b:
                return {
                    "status": "fail",
                    "actual": actual.as_posix(),
                    "expected": expected.as_posix(),
                    "reason": f"text mismatch in {column}",
                }
    return {
        "status": "pass",
        "actual": actual.as_posix(),
        "expected": expected.as_posix(),
        "rows": len(left),
        "columns": len(left.columns),
        "max_abs_difference": max_abs_difference,
        "tolerance": ATOL,
    }


def compare_image(actual: Path, expected: Path) -> dict[str, Any]:
    if not actual.is_file() or not expected.is_file():
        return {
            "status": "fail",
            "actual": actual.as_posix(),
            "expected": expected.as_posix(),
            "reason": "missing file",
        }
    with Image.open(actual) as left_image, Image.open(expected) as right_image:
        left = np.asarray(left_image.convert("RGBA"), dtype=np.int16)
        right = np.asarray(right_image.convert("RGBA"), dtype=np.int16)
    if left.shape != right.shape:
        return {
            "status": "fail",
            "actual": actual.as_posix(),
            "expected": expected.as_posix(),
            "reason": f"pixel shape mismatch: {left.shape} vs {right.shape}",
        }
    difference = np.abs(left - right)
    exact = bool(np.array_equal(left, right))
    return {
        "status": "pass" if exact else "fail",
        "actual": actual.as_posix(),
        "expected": expected.as_posix(),
        "shape": list(left.shape),
        "mean_abs_pixel_difference": float(difference.mean()),
        "max_abs_pixel_difference": int(difference.max()),
        "reason": "" if exact else "pixels are not byte-identical after RGBA conversion",
    }


def csv_data_rows(paths: list[Path]) -> int:
    total = 0
    for path in paths:
        with path.open("r", encoding="utf-8", newline="") as handle:
            total += max(sum(1 for _ in handle) - 1, 0)
    return total


def count_check(label: str, directory: Path, files: int, rows: int) -> dict[str, Any]:
    paths = sorted(directory.glob("*.csv")) if directory.is_dir() else []
    actual_rows = csv_data_rows(paths)
    passed = len(paths) == files and actual_rows == rows
    return {
        "label": label,
        "status": "pass" if passed else "fail",
        "directory": directory.as_posix(),
        "expected_files": files,
        "actual_files": len(paths),
        "expected_rows": rows,
        "actual_rows": actual_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify regenerated paper tables, figures, raw archive counts, "
            "and the integrated manuscript against the staged references."
        )
    )
    parser.parse_args()

    table_pairs = [
        (ROOT / "outputs/tables/decision_alternatives_criteria.csv", ROOT / "reference/tables/decision_alternatives_criteria.csv"),
        (ROOT / "outputs/tables/assumption_inventory.csv", ROOT / "reference/tables/assumption_inventory.csv"),
        (ROOT / "outputs/tables/baseline_definition_table.csv", ROOT / "reference/tables/baseline_definition_table.csv"),
        (ROOT / "outputs/tables/design_recommendation_matrix.csv", ROOT / "reference/tables/design_recommendation_matrix.csv"),
        (ROOT / "outputs/tables/claim_evidence_alignment.csv", ROOT / "reference/tables/claim_evidence_alignment.csv"),
        (ROOT / "outputs/stage26X-1/tables/Table4_multiseed.csv", ROOT / "reference/stage26X-1/Table4_multiseed.csv"),
        (ROOT / "outputs/stage26X-1/tables/Table5_multiseed.csv", ROOT / "reference/stage26X-1/Table5_multiseed.csv"),
    ]
    for expected in sorted((ROOT / "reference/stage26X-2/tables").glob("*.csv")):
        table_pairs.append((ROOT / "outputs/stage26X-2/tables" / expected.name, expected))

    figure_pairs = [
        (ROOT / "outputs/figures/dss_conceptual_framework.png", ROOT / "reference/figures/dss_conceptual_framework.png"),
        (ROOT / "outputs/figures/decision_support_workflow.png", ROOT / "reference/figures/decision_support_workflow.png"),
        (ROOT / "outputs/figures/discretion_identifiability_frontier.png", ROOT / "reference/figures/discretion_identifiability_frontier.png"),
        (ROOT / "outputs/figures/disclosure_uncertainty_curve.png", ROOT / "reference/figures/disclosure_uncertainty_curve.png"),
        (ROOT / "outputs/figures/rule_robustness_heatmap.png", ROOT / "reference/figures/rule_robustness_heatmap.png"),
        (ROOT / "outputs/stage26X-1/Figure_06_multiseed_internal_sensitivity.png", ROOT / "reference/stage26X-1/Figure_06_multiseed_internal_sensitivity.png"),
        (ROOT / "outputs/stage26X-1/Figure_07_multiseed_external_sensitivity.png", ROOT / "reference/stage26X-1/Figure_07_multiseed_external_sensitivity.png"),
        (ROOT / "outputs/figures/dss_evaluation_radar.png", ROOT / "reference/figures/dss_evaluation_radar.png"),
    ]

    counts = [
        count_check("Stage 26X-1", ROOT / "outputs/stage26X-1/raw", 300, 261600),
        count_check("Stage 26X-2 maximum entropy", ROOT / "outputs/stage26X-2/raw/max_entropy", 300, 67200),
        count_check("Stage 26X-2 Bayesian", ROOT / "outputs/stage26X-2/raw/bayesian", 300, 67200),
        count_check("Stage 26X-2 ablation", ROOT / "outputs/stage26X-2/raw/ablation", 300, 156000),
    ]
    table_checks = [compare_csv(actual, expected) for actual, expected in table_pairs]
    figure_checks = [compare_image(actual, expected) for actual, expected in figure_pairs]

    actual_manuscript = ROOT / "outputs/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md"
    expected_manuscript = ROOT / "reference/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md"
    manuscript_check = {
        "status": "pass"
        if actual_manuscript.is_file()
        and expected_manuscript.is_file()
        and sha256(actual_manuscript) == sha256(expected_manuscript)
        else "fail",
        "actual": actual_manuscript.as_posix(),
        "expected": expected_manuscript.as_posix(),
        "actual_sha256": sha256(actual_manuscript) if actual_manuscript.is_file() else "missing",
        "expected_sha256": sha256(expected_manuscript) if expected_manuscript.is_file() else "missing",
    }

    all_checks = [*table_checks, *figure_checks, *counts, manuscript_check]
    passed = all(check["status"] == "pass" for check in all_checks)
    report = {
        "status": "pass" if passed else "fail",
        "numeric_tolerance": ATOL,
        "table_checks": table_checks,
        "figure_checks": figure_checks,
        "raw_count_checks": counts,
        "manuscript_check": manuscript_check,
    }
    output_dir = ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "reproduction_verification.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    lines = [
        "# Repository Reproduction Verification",
        "",
        f"Overall status: `{'PASS' if passed else 'FAIL'}`",
        "",
        f"Numeric absolute tolerance: `{ATOL}`; relative tolerance: `0`.",
        "",
        "## Tables",
        "",
        "| Actual | Status | Rows | Max absolute difference |",
        "|---|---|---:|---:|",
    ]
    for check in table_checks:
        lines.append(
            f"| `{Path(check['actual']).relative_to(ROOT).as_posix()}` | {check['status']} | "
            f"{check.get('rows', '')} | {check.get('max_abs_difference', '')} |"
        )
    lines.extend(["", "## Figures", "", "| Actual | Status | Mean pixel difference |", "|---|---|---:|"])
    for check in figure_checks:
        lines.append(
            f"| `{Path(check['actual']).relative_to(ROOT).as_posix()}` | {check['status']} | "
            f"{check.get('mean_abs_pixel_difference', '')} |"
        )
    lines.extend(["", "## Raw Archives", "", "| Class | Status | Files | Rows |", "|---|---|---:|---:|"])
    for check in counts:
        lines.append(
            f"| {check['label']} | {check['status']} | {check['actual_files']} | {check['actual_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Integrated Manuscript",
            "",
            f"- Status: `{manuscript_check['status']}`.",
            f"- Actual SHA-256: `{manuscript_check['actual_sha256']}`.",
            f"- Expected SHA-256: `{manuscript_check['expected_sha256']}`.",
            "",
        ]
    )
    (output_dir / "reproduction_verification.md").write_text(
        "\n".join(lines), encoding="utf-8", newline="\n"
    )
    print(f"REPRODUCTION_STATUS={'PASS' if passed else 'FAIL'}")
    print(f"REPORT={output_dir / 'reproduction_verification.md'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
