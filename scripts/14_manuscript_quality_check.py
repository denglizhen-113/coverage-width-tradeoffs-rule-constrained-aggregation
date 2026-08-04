#!/usr/bin/env python3
"""Check submission-manuscript completeness, evidence links, and claim boundaries."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PHRASES = (
    "true fan votes",
    "recovered votes",
    "exact public vote",
    "causal effect of fan preference",
    "proves audience support",
)
REQUIRED_MANUSCRIPT = [
    "00_title_abstract_keywords.md", "01_introduction.md", "02_related_work.md",
    "03_data_and_institutional_rules.md", "04_methods.md", "05_results.md",
    "06_prediction_and_counterfactuals.md", "07_discussion.md", "08_limitations.md",
    "09_conclusion.md", "claim_evidence_map.md", "figure_table_plan.md",
    "data_code_availability.md", "ai_assisted_writing_statement.md", "reproducibility_statement.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check manuscript claims, evidence paths, word limits, and submission boundaries."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    return parser.parse_args()


def row(check: str, status: str, detail: str) -> dict[str, str]:
    return {"check": check, "status": status, "detail": detail}


def abstract_words(text: str) -> int:
    abstract = text.split("## Abstract", 1)[1].split("## Keywords", 1)[0]
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", abstract))


def keyword_count(text: str) -> int:
    keywords = text.split("## Keywords", 1)[1].strip().splitlines()[0]
    return len([item for item in keywords.split(";") if item.strip()])


def quality_rows(root: Path) -> list[dict[str, str]]:
    manuscript = root / "manuscript"
    documents = {name: (manuscript / name) for name in REQUIRED_MANUSCRIPT}
    rows: list[dict[str, str]] = []
    missing = [name for name, path in documents.items() if not path.is_file()]
    rows.append(row("Required submission manuscript files exist", "pass" if not missing else "fail", "All files present." if not missing else ", ".join(missing)))
    if missing:
        return rows
    texts = {name: path.read_text(encoding="utf-8") for name, path in documents.items()}
    phrase_hits = []
    for name, text in texts.items():
        lower = text.casefold()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lower:
                phrase_hits.append(f"{name}: {phrase}")
    rows.append(row("Prohibited phrases are absent", "pass" if not phrase_hits else "fail", "No hits." if not phrase_hits else "; ".join(phrase_hits)))
    count = abstract_words(texts["00_title_abstract_keywords.md"])
    rows.append(row("Abstract length is 180-220 words", "pass" if 180 <= count <= 220 else "fail", f"Abstract words: {count}."))
    keywords = keyword_count(texts["00_title_abstract_keywords.md"])
    rows.append(row("Keyword count is 5-7", "pass" if 5 <= keywords <= 7 else "fail", f"Keywords: {keywords}."))

    claims = pd.read_csv(root / "outputs/tables/claim_evidence_map.csv")
    core = claims.loc[claims["strength_level"].eq("core")]
    linked = all((root / item.strip()).is_file() for output in core["supporting_output"] for item in str(output).split(";"))
    finding_text = texts["05_results.md"]
    findings = all(f"Finding {number}" in finding_text for number in range(1, 6))
    rows.append(row("All five core findings have generated supporting outputs", "pass" if len(core) == 5 and linked and findings else "fail", f"core={len(core)}, outputs_exist={linked}, findings_present={findings}."))
    exploratory = claims.loc[claims["strength_level"].eq("exploratory")]
    exploratory_ok = bool((~exploratory["can_be_main_claim"].astype(bool)).all()) and all("Appendix" in str(value) or "Section 7" in str(value) for value in exploratory["suggested_paper_location"])
    rows.append(row("Exploratory results are segregated from core claims", "pass" if exploratory_ok else "fail", f"Exploratory rows: {len(exploratory)}; all not-main and appendix/discussion located: {exploratory_ok}."))

    method_text = texts["04_methods.md"] + texts["05_results.md"]
    regimes_ok = "not directly comparable" in method_text and "ordinal" in method_text and "cardinal" in method_text
    rows.append(row("P/R/R_plus quantities are not equated", "pass" if regimes_ok else "fail", "Methods and results explicitly distinguish cardinal intervals from ordinal rank sets." if regimes_ok else "Missing explicit metric distinction."))
    validation_text = texts["06_prediction_and_counterfactuals.md"].casefold()
    prediction_text = validation_text.split("## scenario analyses", 1)[0]
    prediction_ok = (
        "validation" in prediction_text
        and "not establish unobserved public votes" in prediction_text
        and "causal" not in prediction_text
    )
    rows.append(row("Prediction is described as validation rather than causal vote recovery", "pass" if prediction_ok else "fail", "Required validation boundary found." if prediction_ok else "Prediction boundary wording is incomplete."))
    counterfactual_ok = "scenario analyses" in validation_text and "not causal effects" in validation_text
    rows.append(row("Counterfactuals are described as scenarios rather than historical replacements", "pass" if counterfactual_ok else "fail", "Scenario-analysis boundary found." if counterfactual_ok else "Counterfactual boundary wording is incomplete."))
    discussion_ok = "limitations" in texts["07_discussion.md"].casefold() and "missing public input" in texts["08_limitations.md"].casefold()
    rows.append(row("Discussion includes and links limitations", "pass" if discussion_ok else "fail", "Discussion and dedicated limitations section are present." if discussion_ok else "Limitations linkage missing."))

    path_pattern = re.compile(r"`((?:data|outputs|scripts|src|tests)/[^`\s]+|requirements\.txt|run_all\.py)`")
    missing_paths = []
    for name, text in texts.items():
        for relative in path_pattern.findall(text):
            if not (root / relative).is_file():
                missing_paths.append(f"{name}: {relative}")
    rows.append(row("Manuscript references resolve to existing project paths", "pass" if not missing_paths else "fail", "All checked paths exist." if not missing_paths else "; ".join(missing_paths)))

    plan = pd.read_csv(root / "outputs/tables/main_text_figure_table_plan.csv")
    main = plan.loc[plan["main_text"].astype(bool)]
    figures = main.loc[main["item_type"].eq("figure")]
    tables = main.loc[main["item_type"].eq("table")]
    figure_count_ok = len(figures) == 5 and len(tables) == 4
    image_issues = []
    for relative in figures["file_or_source"]:
        image_path = root / relative
        try:
            dpi = Image.open(image_path).info.get("dpi", (0, 0))[0]
            if float(dpi) < 250:
                image_issues.append(f"{relative}: dpi={dpi}")
        except OSError:
            image_issues.append(f"{relative}: unreadable")
    rows.append(row("Main-text plan contains five figures and four tables with sufficient figure dpi", "pass" if figure_count_ok and not image_issues else "fail", f"figures={len(figures)}, tables={len(tables)}; " + ("all figures >=250 dpi." if not image_issues else "; ".join(image_issues))))
    return rows


def report(rows: pd.DataFrame) -> str:
    lines = [
        "# Manuscript Quality Check",
        "",
        f"- Checks: {len(rows)}",
        f"- Passed: {int(rows['status'].eq('pass').sum())}",
        f"- Failed: {int(rows['status'].eq('fail').sum())}",
        "",
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for item in rows.itertuples(index=False):
        lines.append(f"| {item.check} | {item.status} | {item.detail} |")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    try:
        rows = pd.DataFrame(quality_rows(root))
        output = root / "outputs/logs/manuscript_quality_check.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report(rows) + "\n", encoding="utf-8", newline="\n")
    except (OSError, ValueError, KeyError, IndexError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    failures = int(rows["status"].eq("fail").sum())
    print(f"Manuscript quality check: {len(rows) - failures}/{len(rows)} checks passed")
    print(f"Report: {output}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
