#!/usr/bin/env python3
"""Rebuild the Stage 26W Figure 6 from the tracked Stage 21 summary table."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild only the Stage 26W synthetic coverage-width figure after "
            "removal of the unsupported prediction-only display alias."
        )
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Destination directory; defaults to outputs/stage26W under the project root.",
    )
    return parser.parse_args()


def load_figure_runtime(root: Path) -> ModuleType:
    helper = root / "scripts" / "25he_repair_submission_assets.py"
    if not helper.is_file():
        raise FileNotFoundError(f"Required plotting helper is missing: {helper}")
    spec = importlib.util.spec_from_file_location("stage25he_figure_runtime", helper)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load plotting helper: {helper}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate(root: Path, output_dir: Path) -> tuple[Path, Path]:
    source = root / "outputs" / "tables" / "synthetic_coverage_results.csv"
    if not source.is_file():
        raise FileNotFoundError(
            "Stage 26W Figure 6 requires outputs/tables/synthetic_coverage_results.csv. "
            "Run Stage 21 first."
        )

    runtime = load_figure_runtime(root)
    runtime.load_plot_runtime()
    frame = runtime.read_frame(source)
    output_dir.mkdir(parents=True, exist_ok=True)
    png = output_dir / "Figure_06_synthetic_benchmark_coverage.png"
    pdf = output_dir / "Figure_06_synthetic_benchmark_coverage.pdf"
    runtime.plot_synthetic_coverage(frame, png, vector_path=pdf)
    return png, pdf


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir is not None
        else root / "outputs" / "stage26W"
    )
    png, pdf = generate(root, output_dir)
    print(f"PNG = {png}")
    print(f"PDF = {pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
