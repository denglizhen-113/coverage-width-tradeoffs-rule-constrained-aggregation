#!/usr/bin/env python3
"""Build unified cardinal/ordinal identification features."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.identification_features import (  # noqa: E402
    build_identification_features,
    feature_coverage,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Unify P intervals and R/R_plus ordinal sets into typed appeal proxies."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--panel", type=Path, default=Path("data/processed/panel_long.csv"))
    parser.add_argument(
        "--p-bounds", type=Path, default=Path("data/processed/preference_bounds_regime_p.csv")
    )
    parser.add_argument(
        "--ranking-contestant",
        type=Path,
        default=Path("outputs/tables/ranking_contestant_identification.csv"),
    )
    parser.add_argument(
        "--ranking-r",
        type=Path,
        default=Path("outputs/tables/ranking_identification_summary_r.csv"),
    )
    parser.add_argument(
        "--ranking-rplus",
        type=Path,
        default=Path("outputs/tables/ranking_identification_summary_rplus.csv"),
    )
    parser.add_argument(
        "--comparison",
        type=Path,
        default=Path("outputs/tables/identification_comparison_by_regime.csv"),
    )
    parser.add_argument(
        "--feasible-r",
        type=Path,
        default=Path("data/processed/feasible_rankings_regime_r.csv"),
    )
    parser.add_argument(
        "--feasible-rplus",
        type=Path,
        default=Path("data/processed/feasible_rankings_regime_rplus.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/identification_features_long.csv"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("outputs/logs/identification_features_report.md"),
    )
    return parser.parse_args()


def resolve(path: Path, root: Path) -> Path:
    return path if path.is_absolute() else root / path


def markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    def clean(value: Any) -> str:
        if pd.isna(value):
            return ""
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(clean(v) for v in row) + " |" for row in rows)
    return "\n".join(lines)


def build_report(
    features: pd.DataFrame,
    coverage: pd.DataFrame,
    comparison: pd.DataFrame,
    detail_counts: dict[str, int],
) -> str:
    missing = (
        features.loc[features["public_appeal_proxy"].isna(), "proxy_missing_reason"]
        .value_counts(dropna=False)
        .rename_axis("reason")
        .reset_index(name="rows")
    )
    return "\n".join(
        [
            "# Identification Feature Construction Report",
            "",
            f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
            "",
            "## Coverage",
            "",
            markdown_table(
                ["Regime", "Active rows", "Proxy available", "Proxy missing", "Contestant-seasons", "Mean proxy", "Mean uncertainty"],
                (
                    (
                        row.regime,
                        int(row.active_rows),
                        int(row.proxy_available_rows),
                        int(row.proxy_missing_rows),
                        int(row.contestant_seasons),
                        f"{row.mean_proxy:.6f}",
                        f"{row.mean_uncertainty:.6f}",
                    )
                    for row in coverage.itertuples(index=False)
                ),
            ),
            "",
            f"The output contains {len(features):,} unique active season-week-contestant rows and {len(features.columns)} columns.",
            "",
            "## Proxy definitions",
            "",
            "- P: `public_appeal_proxy` is the midpoint of the coordinate-wise feasible support interval; uncertainty is its interval width.",
            "- R/R_plus: `public_appeal_proxy = 1 - (mean_fan_rank - 1)/(n_active - 1)`; uncertainty is normalized fan-rank support width.",
            "- `public_appeal_type` keeps the cardinal interval midpoint and ordinal rank score distinct. They are standardized latent public-appeal proxies, not a common cardinal vote-share measure.",
            "",
            "## Missing proxy rows",
            "",
            markdown_table(
                ["Reason", "Rows"],
                missing[["reason", "rows"]].itertuples(index=False, name=None),
            ) if not missing.empty else "No proxy rows are missing.",
            "",
            "The P-regime missing rows arise from the previously logged Season 18 Week 2 constraint skip. No midpoint is imputed at this stage.",
            "",
            "## Ordinal provenance",
            "",
            f"The retained feasible-ranking audit files contain {detail_counts['R']:,} R rows and {detail_counts['R_plus']:,} R_plus rows. Contestant mean ranks and widths are taken from `ranking_contestant_identification.csv`, which was computed from all evaluated rankings rather than the capped audit detail.",
            "",
            "## Cross-regime interpretation",
            "",
            markdown_table(
                ["Regime", "Weeks", "Mean normalized uncertainty", "Notes"],
                (
                    (
                        row.regime,
                        int(row.n_weeks),
                        f"{row.mean_normalized_uncertainty:.6f}",
                        row.notes,
                    )
                    for row in comparison.itertuples(index=False)
                ),
            ),
            "",
            "Subsequent models include regime indicators and report mechanism-specific sensitivity because P and ordinal proxies do not identify the same primitive quantity.",
            "",
            "## Interpretation boundary",
            "",
            "This table does not recover true public votes. It converts previously identified sets into typed, uncertainty-tagged features for descriptive dynamic models, predictive validation, and sensitivity-based mechanism simulations.",
            "",
        ]
    )


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    paths = {
        name: resolve(getattr(args, name), root)
        for name in (
            "panel",
            "p_bounds",
            "ranking_contestant",
            "ranking_r",
            "ranking_rplus",
            "comparison",
            "feasible_r",
            "feasible_rplus",
        )
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        print(f"ERROR: Missing required input(s): {', '.join(missing)}", file=sys.stderr)
        print("Run stages 02, 04, and 05 first.", file=sys.stderr)
        return 2
    output_path = resolve(args.output, root)
    report_path = resolve(args.report, root)
    try:
        panel = pd.read_csv(paths["panel"])
        p_bounds = pd.read_csv(paths["p_bounds"])
        ranking_contestant = pd.read_csv(paths["ranking_contestant"])
        ranking_summary = pd.concat(
            [pd.read_csv(paths["ranking_r"]), pd.read_csv(paths["ranking_rplus"])],
            ignore_index=True,
        )
        comparison = pd.read_csv(paths["comparison"])
        features = build_identification_features(
            panel, p_bounds, ranking_contestant, ranking_summary
        )
        coverage = feature_coverage(features)
        detail_counts = {
            "R": len(pd.read_csv(paths["feasible_r"], usecols=["season"])),
            "R_plus": len(pd.read_csv(paths["feasible_rplus"], usecols=["season"])),
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        features.to_csv(
            output_path,
            index=False,
            encoding="utf-8",
            na_rep="",
            lineterminator="\n",
            float_format="%.12g",
        )
        report_path.write_text(
            build_report(features, coverage, comparison, detail_counts),
            encoding="utf-8",
            newline="\n",
        )
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"identification_features_long.csv: {features.shape[0]} rows x {features.shape[1]} columns")
    print(f"Proxy available: {int(features['public_appeal_proxy'].notna().sum())}")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
