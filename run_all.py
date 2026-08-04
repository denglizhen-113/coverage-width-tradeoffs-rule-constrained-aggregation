#!/usr/bin/env python3
"""Run the reproducible pipeline through robust aggregation evaluation."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

STAGE_CHOICES = (
    "18", "19", "20", "21", "22", "23", "24",
    "25-0", "25A", "25-overnight", "25B", "25C", "25D", "25E",
    "25F", "25G", "25H", "25HA", "25HB", "25HC-closure", "25HC-title",
    "25HD-reconstruct", "25HE-finalize", "25HE-repair", "25HF",
    "26W-figure", "26X-1", "26X-2", "26X-3", "26Y",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run identification, dynamic inference, prediction, counterfactual, "
            "robust aggregation, and manuscript result stages."
        )
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--skip-preprocess",
        action="store_true",
        help="Reuse existing audited/processed inputs and run stages 03-12.",
    )
    parser.add_argument(
        "--manuscript",
        action="store_true",
        help="Also run leakage/claim audit and submission-manuscript quality checks.",
    )
    parser.add_argument(
        "--submission-audit",
        action="store_true",
        help="Also run the strict target-journal, reviewer, and submission-package audit.",
    )
    parser.add_argument(
        "--overnight-submission",
        action="store_true",
        help=(
            "Run stages 13-16 using existing generated results, producing strict "
            "overnight submission audits and SEPS-oriented manuscript copies without "
            "rewriting the baseline manuscript."
        ),
    )
    parser.add_argument(
        "--general-submission",
        action="store_true",
        help=(
            "Run stage 17 using existing results, freezing the current evidence and "
            "generating a general decision-analysis submission line without changing "
            "models, baseline manuscript files, or SEPS-oriented copies."
        ),
    )
    parser.add_argument(
        "--stage",
        action="append",
        choices=STAGE_CHOICES,
        help=(
            "Run one explicit post-Stage-17 entry point. Repeat to run multiple "
            "stages in the supplied order; frozen stages are never selected implicitly."
        ),
    )
    parser.add_argument(
        "--documents-skill-root",
        type=Path,
        help="Required only for --stage 25G; directory containing render_docx.py.",
    )
    args = parser.parse_args()
    if args.overnight_submission and args.general_submission:
        parser.error("--overnight-submission and --general-submission cannot be combined.")
    legacy_modes = (
        args.skip_preprocess,
        args.manuscript,
        args.submission_audit,
        args.overnight_submission,
        args.general_submission,
    )
    if args.stage and any(legacy_modes):
        parser.error("--stage cannot be combined with the Stage 1-17 mode flags.")
    if args.stage and "25G" in args.stage and args.documents_skill_root is None:
        parser.error("--stage 25G requires --documents-skill-root.")
    return args


def explicit_stage_steps(
    root: Path, stages: list[str], documents_skill_root: Path | None
) -> list[tuple[str, Path, list[str]]]:
    project_args = ["--project-root", str(root)]
    specs: dict[str, tuple[str, str, list[str]]] = {
        "18": ("18 specific-journal submission", "18_specific_journal_submission.py", project_args),
        "19": ("19 decision-analysis submission", "19_decision_analysis_submission.py", project_args),
        "20": ("20 high-tier upgrade strategy", "20_high_tier_upgrade_strategy.py", project_args),
        "21": ("21 DSS full attack", "21_dss_full_attack.py", project_args),
        "22": ("22 DSS submission candidate", "22_dss_submission_candidate.py", project_args),
        "23": ("23 DSS submission integrity", "23_dss_submission_integrity.py", project_args),
        "24": ("24 DSS author completion", "24_dss_author_submission_completion.py", project_args),
        "25F": ("25F author-side gate", "25f_final_author_side_completion_gate.py", project_args),
        "25H": ("25H author-input gate", "25h_author_filled_final_consistency_gate.py", project_args),
        "25HA": ("25H-A author information", "25ha_apply_author_provided_information.py", project_args),
        "25HB": ("25H-B confirmations", "25hb_apply_final_author_confirmations.py", project_args),
        "25HC-closure": ("25H-C repository closure", "25hc_apply_repository_address_and_approval_closure.py", project_args),
        "25HC-title": ("25H-C title-page DOCX", "25hc_generate_non_anonymized_author_review_docx.py", project_args),
        "25HD-reconstruct": ("25H-D DOCX reconstruction", "25hd_reconstruct_dss_submission_docx.py", project_args),
        "25HE-finalize": ("25H-E package finalization", "25he_finalize_dss_submission_package.py", project_args),
        "25HE-repair": ("25H-E asset repair", "25he_repair_submission_assets.py", project_args),
        "25HF": ("25H-F upload gate", "25hf_resolve_dss_upload_gate.py", project_args),
        "26W-figure": ("26W Figure 6 rebuild", "26w_rebuild_figure06.py", project_args),
        "26X-1": ("26X-1 multiseed sensitivity", "26x1_multiseed_sensitivity.py", ["--mode", "run", "--root", str(root)]),
        "26X-2": ("26X-2 baselines and ablation", "26x2_baselines_ablation.py", ["--mode", "run", "--root", str(root)]),
        "26X-3": ("26X-3 manuscript repositioning", "26x3_reposition_manuscript.py", project_args),
        "26Y": ("26Y EJOR migration", "26y_ejor_submission_migration.py", project_args),
    }
    for substage in ("25-0", "25A", "25B", "25C", "25D", "25E"):
        specs[substage] = (
            f"{substage} submission strengthening",
            "25_dss_final_submission_strengthening_and_sealing.py",
            ["--stage", substage, *project_args],
        )
    specs["25-overnight"] = (
        "25 overnight submission strengthening",
        "25_dss_final_submission_strengthening_and_sealing.py",
        ["--stage", "overnight", *project_args],
    )
    if documents_skill_root is not None:
        specs["25G"] = (
            "25G editable source generation",
            "25g_final_editable_source_generation.py",
            [*project_args, "--documents-skill-root", str(documents_skill_root.resolve())],
        )

    return [
        (label, root / "scripts" / script, list(extra_args))
        for stage in stages
        for label, script, extra_args in (specs[stage],)
    ]


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    report_path = root / "outputs" / "logs" / "pipeline_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    if args.stage:
        steps = explicit_stage_steps(root, args.stage, args.documents_skill_root)
    elif args.general_submission:
        required = [
            root / "data/processed/panel_long.csv",
            root / "outputs/tables/identification_comparison_by_regime.csv",
            root / "outputs/tables/ranking_identification_summary_rplus.csv",
            root / "outputs/tables/prediction_results.csv",
            root / "outputs/tables/pareto_frontier_points.csv",
        ]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            print(
                "ERROR: --general-submission requires existing processed and result files: "
                + ", ".join(missing),
                file=sys.stderr,
            )
            return 2
        steps = [
            ("17 general submission strategy", root / "scripts/17_general_submission_strategy.py"),
        ]
    elif args.overnight_submission:
        required = [
            root / "data/processed/panel_long.csv",
            root / "outputs/tables/identification_comparison_by_regime.csv",
            root / "outputs/tables/ranking_identification_summary_rplus.csv",
            root / "outputs/tables/prediction_results.csv",
        ]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            print(
                "ERROR: --overnight-submission requires existing processed and result files: "
                + ", ".join(missing),
                file=sys.stderr,
            )
            return 2
        steps = [
            ("13 leakage and claim audit", root / "scripts/13_leakage_and_claim_audit.py"),
            ("14 manuscript quality check", root / "scripts/14_manuscript_quality_check.py"),
            ("15 submission readiness audit", root / "scripts/15_submission_audit.py"),
            ("16 overnight submission strengthening", root / "scripts/16_overnight_submission.py"),
        ]
    elif args.skip_preprocess:
        required = [
            root / "data/processed/panel_long.csv",
            root / "data/processed/week_level.csv",
            root / "data/processed/contestant_level.csv",
        ]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            print(
                "ERROR: --skip-preprocess requires existing processed files: "
                + ", ".join(missing),
                file=sys.stderr,
            )
            return 2
        steps = [
            ("03 constraints", root / "scripts/03_build_constraints.py"),
            ("04 partial identification", root / "scripts/04_partial_identification.py"),
            ("05 ranking identification", root / "scripts/05_ranking_identification.py"),
            ("06 identification features", root / "scripts/06_build_identification_features.py"),
            ("07 expert-crowd divergence", root / "scripts/07_expert_crowd_divergence.py"),
            ("08 dynamic preference", root / "scripts/08_dynamic_preference_model.py"),
            ("09 prediction experiments", root / "scripts/09_prediction_experiments.py"),
            ("10 counterfactual mechanisms", root / "scripts/10_counterfactual_mechanisms.py"),
            ("11 robust aggregation", root / "scripts/11_robust_aggregation_evaluation.py"),
            ("12 manuscript results", root / "scripts/12_update_manuscript_results.py"),
        ]
    else:
        steps = [
            ("01 data audit", root / "scripts/01_data_audit.py"),
            ("02 preprocessing", root / "scripts/02_preprocess.py"),
            ("03 constraints", root / "scripts/03_build_constraints.py"),
            ("04 partial identification", root / "scripts/04_partial_identification.py"),
            ("05 ranking identification", root / "scripts/05_ranking_identification.py"),
            ("06 identification features", root / "scripts/06_build_identification_features.py"),
            ("07 expert-crowd divergence", root / "scripts/07_expert_crowd_divergence.py"),
            ("08 dynamic preference", root / "scripts/08_dynamic_preference_model.py"),
            ("09 prediction experiments", root / "scripts/09_prediction_experiments.py"),
            ("10 counterfactual mechanisms", root / "scripts/10_counterfactual_mechanisms.py"),
            ("11 robust aggregation", root / "scripts/11_robust_aggregation_evaluation.py"),
            ("12 manuscript results", root / "scripts/12_update_manuscript_results.py"),
        ]

    if not (args.overnight_submission or args.general_submission) and (args.manuscript or args.submission_audit):
        steps.extend(
            [
                ("13 leakage and claim audit", root / "scripts/13_leakage_and_claim_audit.py"),
                ("14 manuscript quality check", root / "scripts/14_manuscript_quality_check.py"),
            ]
        )

    if not (args.overnight_submission or args.general_submission) and args.submission_audit:
        steps.append(("15 submission readiness audit", root / "scripts/15_submission_audit.py"))

    records: list[dict[str, str | int]] = []
    exit_code = 0
    for step in steps:
        name, script = step[0], step[1]
        extra_args = step[2] if len(step) == 3 else ["--project-root", str(root)]
        if not script.is_file():
            records.append(
                {
                    "name": name,
                    "script": str(script),
                    "return_code": 2,
                    "status": "missing_script",
                    "stdout": "",
                    "stderr": f"Script not found: {script}",
                }
            )
            exit_code = 2
            break
        command = [sys.executable, str(script), *extra_args]
        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        records.append(
            {
                "name": name,
                "script": str(script),
                "command": subprocess.list2cmdline(command),
                "return_code": result.returncode,
                "status": "completed" if result.returncode == 0 else "failed",
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        )
        print(f"[{records[-1]['status']}] {name}")
        if result.returncode != 0:
            exit_code = result.returncode
            break

    lines = [
        "# Pipeline Report",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        f"- Python: `{sys.executable}`",
        f"- Project root: `{root}`",
        f"- Skip preprocessing: `{args.skip_preprocess}`",
        f"- Manuscript checks: `{args.manuscript}`",
        f"- Submission audit: `{args.submission_audit}`",
        f"- Overnight submission: `{args.overnight_submission}`",
        f"- General submission: `{args.general_submission}`",
        f"- Explicit stages: `{', '.join(args.stage or []) or 'none'}`",
        "",
    ]
    for record in records:
        lines.extend(
            [
                f"## {record['name']}",
                "",
                f"- Status: `{record['status']}`",
                f"- Return code: `{record['return_code']}`",
                f"- Script: `{record['script']}`",
                f"- Command: `{record.get('command', '')}`",
                "",
                "```text",
                str(record["stdout"]),
                "```",
                "",
            ]
        )
        if record["stderr"]:
            lines.extend(
                ["Standard error:", "", "```text", str(record["stderr"]), "```", ""]
            )
    report_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"Pipeline report: {report_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
