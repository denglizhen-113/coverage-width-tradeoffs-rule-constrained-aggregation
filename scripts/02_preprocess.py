#!/usr/bin/env python3
"""Create analysis-ready long, week-level, and contestant-level datasets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover - runtime setup failure
    raise SystemExit(
        "pandas is required. Install pandas>=2.0 and rerun this command."
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocessing import build_preprocessed_tables, load_source_csv  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Transform the audited wide source into long, week-level, and "
            "contestant-level research datasets."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root (default: parent of the scripts directory).",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/2026_MCM_Problem_C_Data.csv"),
        help="Source CSV, relative to the project root by default.",
    )
    parser.add_argument(
        "--audit-summary",
        type=Path,
        default=Path("outputs/tables/data_audit_summary.csv"),
        help="Audit summary produced by scripts/01_data_audit.py.",
    )
    parser.add_argument(
        "--special-cases",
        type=Path,
        default=Path("outputs/tables/special_cases.csv"),
        help="Audited special cases produced by scripts/01_data_audit.py.",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path("data/processed"),
        help="Processed data directory, relative to the project root by default.",
    )
    parser.add_argument(
        "--logs-dir",
        type=Path,
        default=Path("outputs/logs"),
        help="Log directory, relative to the project root by default.",
    )
    return parser.parse_args()


def resolve_from_root(path: Path, project_root: Path) -> Path:
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    source = resolve_from_root(args.input, project_root).resolve()
    audit_summary_path = resolve_from_root(args.audit_summary, project_root).resolve()
    special_cases_path = resolve_from_root(args.special_cases, project_root).resolve()
    processed_dir = resolve_from_root(args.processed_dir, project_root).resolve()
    logs_dir = resolve_from_root(args.logs_dir, project_root).resolve()

    required = [source, audit_summary_path, special_cases_path]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print(
            "ERROR: Missing required input(s): " + ", ".join(missing),
            file=sys.stderr,
        )
        print(
            "Run scripts/01_data_audit.py before preprocessing.", file=sys.stderr
        )
        return 2

    try:
        parsed, raw, csv_settings = load_source_csv(source)
        audit_summary = pd.read_csv(
            audit_summary_path, dtype=str, keep_default_na=False
        )
        special_cases = pd.read_csv(
            special_cases_path, dtype=str, keep_default_na=False
        )
        panel, week_level, contestant_level, report = build_preprocessed_tables(
            source,
            parsed,
            raw,
            audit_summary,
            special_cases,
            csv_settings,
        )
    except (OSError, UnicodeError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    processed_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    panel_path = processed_dir / "panel_long.csv"
    week_path = processed_dir / "week_level.csv"
    contestant_path = processed_dir / "contestant_level.csv"
    report_path = logs_dir / "preprocess_report.md"

    csv_options = {
        "index": False,
        "encoding": "utf-8",
        "na_rep": "",
        "lineterminator": "\n",
        "float_format": "%.12g",
    }
    panel.to_csv(panel_path, **csv_options)
    week_level.to_csv(week_path, **csv_options)
    contestant_level.to_csv(contestant_path, **csv_options)
    report_path.write_text(report, encoding="utf-8", newline="\n")

    print(f"Source: {source}")
    print(f"panel_long.csv: {len(panel)} rows x {len(panel.columns)} columns")
    print(f"week_level.csv: {len(week_level)} rows x {len(week_level.columns)} columns")
    print(
        "contestant_level.csv: "
        f"{len(contestant_level)} rows x {len(contestant_level.columns)} columns"
    )
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

