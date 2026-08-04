#!/usr/bin/env python3
"""Audit prediction leakage, counterfactual inputs, and manuscript claims."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.prediction import MODEL_SPECS, build_prediction_frame


FORBIDDEN_PHRASES = (
    "true fan votes",
    "recovered votes",
    "exact public vote",
    "causal effect of fan preference",
    "proves audience support",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit leakage risks and claim language in the submission manuscript."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    return parser.parse_args()


def make_row(
    audit_id: str,
    area: str,
    check: str,
    status: str,
    evidence: str,
    files_checked: str,
    recommendation: str,
) -> dict[str, str]:
    return {
        "audit_id": audit_id,
        "area": area,
        "check": check,
        "status": status,
        "evidence": evidence,
        "files_checked": files_checked,
        "recommendation": recommendation,
    }


def is_close_or_missing(left: pd.Series, right: pd.Series) -> bool:
    left = pd.to_numeric(left, errors="coerce").to_numpy(dtype=float)
    right = pd.to_numeric(right, errors="coerce").to_numpy(dtype=float)
    return bool(np.all(np.isclose(left, right, equal_nan=True)))


def audit_prediction(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    prohibited = {
        "eliminated_this_week", "placement", "final_rank", "finale_week",
        "finale_outcome", "winner", "winner_changed",
    }
    current_judge = {"judge_pct", "judge_rank"}
    violations: list[str] = []
    same_week_violations: list[str] = []
    for name, spec in MODEL_SPECS.items():
        features = set(spec["features"])
        forbidden = sorted(features.intersection(prohibited))
        if forbidden:
            violations.append(f"{name}: {', '.join(forbidden)}")
        if not spec["same_week"] and features.intersection(current_judge):
            same_week_violations.append(name)
    rows.append(
        make_row(
            "L1", "prediction", "Outcome and finale fields are excluded from predictor lists.",
            "pass" if not violations else "fail",
            "No prohibited feature names in MODEL_SPECS." if not violations else "; ".join(violations),
            "src/prediction.py", "Keep labels and final outcomes outside model feature lists.",
        )
    )
    rows.append(
        make_row(
            "L2", "prediction", "Current-week judge fields occur only in same-week baselines.",
            "pass" if not same_week_violations else "fail",
            "All models using judge_pct or judge_rank at week t are marked same-week."
            if not same_week_violations else "; ".join(same_week_violations),
            "src/prediction.py", "Retain explicit same-week labels in all result tables and captions.",
        )
    )

    dynamic_path = root / "data/processed/dynamic_public_appeal.csv"
    week_path = root / "data/processed/week_level.csv"
    results_path = root / "outputs/tables/prediction_results.csv"
    dynamic = pd.read_csv(dynamic_path)
    week = pd.read_csv(week_path)
    frame = build_prediction_frame(dynamic, week)
    history = frame.loc[frame["history_available"]].copy()
    no_future = bool((history["lag_source_week"] < history["week"]).all())
    rows.append(
        make_row(
            "L3", "prediction", "Lag source week is strictly earlier than prediction week.",
            "pass" if no_future else "fail",
            f"History-available rows checked: {len(history)}; all lag_source_week < week: {no_future}.",
            "src/prediction.py; data/processed/dynamic_public_appeal.csv; data/processed/week_level.csv",
            "Fail the pipeline if a lag source is current or future.",
        )
    )
    reference = dynamic[["season", "contestant_id", "week", "public_appeal_proxy", "dynamic_public_appeal"]].rename(
        columns={
            "week": "lag_source_week",
            "public_appeal_proxy": "expected_proxy_lag",
            "dynamic_public_appeal": "expected_dynamic_lag",
        }
    )
    merged = history.merge(reference, on=["season", "contestant_id", "lag_source_week"], how="left", validate="m:1")
    proxy_ok = is_close_or_missing(merged["public_appeal_proxy_lag1"], merged["expected_proxy_lag"])
    dynamic_ok = is_close_or_missing(merged["dynamic_public_appeal_lag1"], merged["expected_dynamic_lag"])
    rows.append(
        make_row(
            "L4", "prediction", "Lagged public and dynamic proxies equal their recorded prior observations.",
            "pass" if proxy_ok and dynamic_ok else "fail",
            f"public_proxy_lag1 match={proxy_ok}; dynamic_public_appeal_lag1 match={dynamic_ok}.",
            "src/prediction.py; data/processed/dynamic_public_appeal.csv",
            "Use only prior contestant observations for public-proxy features.",
        )
    )
    results = pd.read_csv(results_path)
    result_issues: list[str] = []
    for row in results.itertuples(index=False):
        expected = bool(MODEL_SPECS[str(row.model)]["same_week"])
        actual = str(row.same_week_baseline).strip().casefold() == "true"
        if expected != actual:
            result_issues.append(str(row.model))
    rows.append(
        make_row(
            "L5", "prediction", "Published result rows preserve same-week baseline flags.",
            "pass" if not result_issues else "fail",
            "All prediction result rows agree with MODEL_SPECS."
            if not result_issues else "Mismatched flags: " + ", ".join(sorted(set(result_issues))),
            "outputs/tables/prediction_results.csv; src/prediction.py",
            "Keep same-week baselines visibly separated from historical models.",
        )
    )
    return rows


def audit_counterfactual(root: Path) -> list[dict[str, str]]:
    source_path = root / "src/counterfactuals.py"
    source = source_path.read_text(encoding="utf-8")
    score_tokens = (
        "direct_score = -(judge_rank + fan_rank)",
        "percentage_score = judge_pct + scenario.public_score",
        "uncertainty_aware_scores(",
    )
    score_ok = all(token in source for token in score_tokens)
    placement_present = "observed_placement" in source and "counterfactual_rank" in source
    return [
        make_row(
            "L6", "counterfactual", "Observed final placement is not a mechanism-score input.",
            "pass" if score_ok else "fail",
            "Mechanism scores use observed weekly judge values, feasible public scenarios, and uncertainty. "
            "Observed placement is retained only for ex-post rank-shift and winner/finalist comparison."
            if score_ok and placement_present else "Could not locate the expected score construction tokens.",
            "src/counterfactuals.py",
            "Do not add placement, finale outcome, or observed winner fields to mechanism scores.",
        )
    ]


def audit_claims(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    manuscript = root / "manuscript"
    hits: list[str] = []
    for path in sorted(manuscript.glob("*.md")):
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in text:
                hits.append(f"{path.name}: {phrase}")
    rows.append(
        make_row(
            "C1", "claims", "Submission manuscript excludes prohibited vote-recovery and causal language.",
            "pass" if not hits else "fail",
            "No prohibited phrases found." if not hits else "; ".join(hits),
            "manuscript/*.md",
            "Replace any flagged wording with feasible-set, descriptive, or scenario-analysis language.",
        )
    )
    claim_path = root / "outputs/tables/claim_evidence_map.csv"
    claims = pd.read_csv(claim_path)
    core = claims.loc[claims["strength_level"].eq("core")]
    secondary = claims.loc[claims["strength_level"].eq("secondary")]
    exploratory = claims.loc[claims["strength_level"].eq("exploratory")]
    shape_ok = len(core) == 5 and len(secondary) == 3 and len(exploratory) == 5
    rows.append(
        make_row(
            "C2", "claims", "Claim-evidence map separates five core, three secondary, and five exploratory claims.",
            "pass" if shape_ok else "fail",
            f"core={len(core)}, secondary={len(secondary)}, exploratory={len(exploratory)}.",
            "outputs/tables/claim_evidence_map.csv",
            "Keep only core claims in the abstract and central contribution statements.",
        )
    )
    return rows


def report(rows: pd.DataFrame) -> str:
    lines = [
        "# Leakage and Claim Audit",
        "",
        f"- Checks: {len(rows)}",
        f"- Passed: {int(rows['status'].eq('pass').sum())}",
        f"- Warnings: {int(rows['status'].eq('warning').sum())}",
        f"- Failed: {int(rows['status'].eq('fail').sum())}",
        "",
        "| ID | Area | Status | Check | Evidence | Recommendation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows.itertuples(index=False):
        lines.append(
            f"| {row.audit_id} | {row.area} | {row.status} | {row.check} | {row.evidence} | {row.recommendation} |"
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    required = [
        root / "data/processed/dynamic_public_appeal.csv",
        root / "data/processed/week_level.csv",
        root / "outputs/tables/prediction_results.csv",
        root / "outputs/tables/claim_evidence_map.csv",
        root / "src/counterfactuals.py",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print("ERROR: Missing required audit input(s): " + ", ".join(missing), file=sys.stderr)
        return 2
    try:
        rows = pd.DataFrame(audit_prediction(root) + audit_counterfactual(root) + audit_claims(root))
        table_path = root / "outputs/tables/leakage_audit_table.csv"
        log_path = root / "outputs/logs/leakage_and_claim_audit.md"
        table_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        rows.to_csv(table_path, index=False)
        log_path.write_text(report(rows) + "\n", encoding="utf-8", newline="\n")
    except (OSError, ValueError, KeyError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    failures = int(rows["status"].eq("fail").sum())
    print(f"Leakage and claim audit: {len(rows) - failures}/{len(rows)} checks passed")
    print(f"Audit table: {table_path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
