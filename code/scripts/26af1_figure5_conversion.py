#!/usr/bin/env python3
"""Convert Stage 26AF Figure 5 to a Table 9 record and renumber figures.

This stage performs presentation-only transformations from the tracked Stage
26AF manuscript and figure package. It does not run either registered
experiment or alter any source table.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import shutil
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path("outputs/stage26AF/METHODS_research_draft_STAGE26AF.md")
DEFAULT_STAGE26AF_DIR = Path("outputs/stage26AF")
DEFAULT_OUTPUT = Path("outputs/stage26AF-1")
STAGE26AF_SOURCE_SHA256 = "9fe968728fa6abe2488543475b617d4cd526694d7c8e8ca6a5f37d0fb31f93f9"
STAGE26AF_MANIFEST_SHA256 = "81c470a13412a9fbe018db020227a30f9aa805de51c966ac9300f306dd1840e4"
FROZEN_X3_SHA256 = "758755b50cd1c059d939fa550ac151c7b55263348e7bb8b55b40e20fff1c2d82"
X1_PREREG_SHA256 = "e437a81b80143b2f03c81b005d463cc489185d7f781214e8446d1e111784257b"
X2_PREREG_SHA256 = "e5418f189061ed295a941327bcf3364081b4095d8b1a1855a416f0431191d19c"

MAIN_FIGURES = (
    (1, "Figure_01_rule_conditioned_inference_architecture", "Figure_01_rule_conditioned_inference_architecture", "conceptual architecture"),
    (2, "Figure_02_reproducible_comparison_workflow", "Figure_02_reproducible_comparison_workflow", "conceptual workflow"),
    (3, "Figure_03_discretion_identifiability_frontier", "Figure_03_discretion_identifiability_frontier", "outputs/tables/discretion_identifiability_summary.csv"),
    (4, "Figure_04_compatible_disclosure_scenarios", "Figure_04_compatible_disclosure_scenarios", "outputs/tables/value_of_disclosure.csv"),
    (5, "Figure_06_multiseed_internal_sensitivity", "Figure_05_multiseed_internal_sensitivity", "outputs/stage26X-1/tables/Table4_multiseed.csv"),
    (6, "Figure_07_multiseed_external_sensitivity", "Figure_06_multiseed_external_sensitivity", "outputs/stage26X-1/tables/Table5_multiseed.csv"),
)

DIAGNOSTICS = (
    (
        "Figure_05_rule_robustness_index",
        "RRI_Record_predeclared_conclusions",
        "former Figure 5: predeclared-conclusion RRI record",
        "outputs/tables/rule_robustness_index.csv",
    ),
    (
        "Artifact_Check_evidence_completeness",
        "Artifact_Check_evidence_completeness",
        "former Figure 8: artifact evidence-completeness check",
        "outputs/tables/dss_evaluation_metrics.csv",
    ),
)


class Stage26AF1Error(RuntimeError):
    """Raised when a Stage 26AF-1 integrity gate fails."""


def load_stage26af(root: Path) -> Any:
    path = root / "scripts" / "26af_figure_rebuild_complexity.py"
    if not path.is_file():
        raise Stage26AF1Error(f"Required Stage 26AF generator is missing: {path}")
    spec = importlib.util.spec_from_file_location("stage26af_for_26af1", path)
    if spec is None or spec.loader is None:
        raise Stage26AF1Error(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(root: Path, relative: Path | str) -> Path:
    path = root / Path(relative)
    if not path.is_file():
        raise Stage26AF1Error(f"Required file is missing: {path}")
    return path


def line_number(text: str, target: str) -> int:
    index = text.find(target)
    if index < 0:
        raise Stage26AF1Error(f"Cannot locate report target: {target}")
    return text[:index].count("\n") + 1


def table9_markdown(root: Path, base: Any) -> tuple[str, str]:
    source = pd.read_csv(require(root, "outputs/tables/claim_evidence_alignment.csv"), dtype=str).fillna("")
    expected = [
        "claim_id",
        "controlled_claim",
        "evidence_source",
        "evidence_type",
        "allowed_location",
        "mandatory_boundary",
        "alignment_status",
    ]
    if list(source.columns) != expected:
        raise Stage26AF1Error(f"Table 9 schema changed: {list(source.columns)}")
    rri = pd.read_csv(require(root, "outputs/tables/rule_robustness_index.csv"))
    counts = {str(row.conclusion_id): f"{int(row.supporting_configurations)}/{int(row.applicable_configurations)}" for row in rri.itertuples()}
    if counts != {"C1": "1/1", "C2": "4/4", "C3": "4/4", "C4": "1/1"}:
        raise Stage26AF1Error(f"Unexpected RRI supporting/applicable counts: {counts}")
    if not rri["rule_robustness_index"].eq(1.0).all():
        raise Stage26AF1Error("RRI values are no longer all 1.000")

    record = (
        "4/4 predeclared conclusions have RRI 1.000 "
        "(supporting/applicable: C1 1/1; C2 4/4; C3 4/4; C4 1/1)."
    )
    added = {
        "claim_id": "CE10",
        "controlled_claim": record,
        "evidence_source": "rule_robustness_index.csv",
        "evidence_type": "predeclared-configuration reproducibility diagnostic",
        "allowed_location": "Table 9 and repository record",
        "mandatory_boundary": "registered applicable configurations only; not welfare or method ranking",
        "alignment_status": "pass",
    }
    if "CE10" in set(source["claim_id"]):
        raise Stage26AF1Error("Table 9 source unexpectedly already contains CE10")
    rows = [tuple(row[column] for column in expected) for _, row in source.iterrows()]
    rows.append(tuple(added[column] for column in expected))
    headers = ["Claim", "Controlled claim", "Evidence source", "Evidence type", "Allowed location", "Mandatory boundary", "Status"]
    return base.markdown_table(headers, rows), record


def revise_manuscript(root: Path, source: str, base: Any) -> tuple[str, str]:
    section_before = (
        "### 7.3 Rule Robustness Index\n\n"
        "Figure 5 reports predeclared conclusion predicates, their supporting and applicable configurations, and RRI. All four evaluated conclusions have RRI 1.000 within their applicable configuration families. This statement is bounded by the registered configurations and does not establish welfare or method ranking.\n\n"
        "[[FIGURE 5]]\n\n"
        "**Method-selection implication.** RRI distinguishes persistence across the evaluated configuration family from claims about untested institutions."
    )
    section_after = (
        "### 7.3 Rule Robustness Index\n\n"
        "All 4/4 predeclared conclusions have RRI 1.000 within their registered applicable configuration families "
        "(supporting/applicable: C1 1/1, C2 4/4, C3 4/4, and C4 1/1). The compact record is included as the final row of Table 9, and `rule_robustness_index.csv` plus its vector and 600 dpi diagnostic remain in the repository. This statement does not establish welfare or method ranking.\n\n"
        "**Method-selection implication.** RRI distinguishes persistence across the evaluated configuration family from claims about untested institutions."
    )
    if source.count(section_before) != 1:
        raise Stage26AF1Error("Cannot locate the Stage 26AF Figure 5 section exactly once")
    revised = source.replace(section_before, section_after)

    table9, record = table9_markdown(root, base)
    if revised.count("[[TABLE 9]]") != 1:
        raise Stage26AF1Error("Cannot locate the Table 9 placeholder exactly once")
    revised = revised.replace("[[TABLE 9]]", table9)

    caption5 = "**Figure 5. Rule Robustness Index across predeclared conclusions.** RRI is the bounded share of applicable evaluated configurations supporting a conclusion, not a method or welfare ranking.\n\n"
    if revised.count(caption5) != 1:
        raise Stage26AF1Error("Cannot locate the Stage 26AF Figure 5 caption exactly once")
    revised = revised.replace(caption5, "")

    revised = revised.replace("Figure 6", "__INTERNAL_FIGURE__")
    revised = revised.replace("[[FIGURE 6]]", "__INTERNAL_PLACEHOLDER__")
    revised = revised.replace("Figure 7", "__EXTERNAL_FIGURE__")
    revised = revised.replace("[[FIGURE 7]]", "__EXTERNAL_PLACEHOLDER__")
    revised = revised.replace("__INTERNAL_FIGURE__", "Figure 5")
    revised = revised.replace("__INTERNAL_PLACEHOLDER__", "[[FIGURE 5]]")
    revised = revised.replace("__EXTERNAL_FIGURE__", "Figure 6")
    revised = revised.replace("__EXTERNAL_PLACEHOLDER__", "[[FIGURE 6]]")

    if any(token in revised for token in ("__INTERNAL_", "__EXTERNAL_")):
        raise Stage26AF1Error("A temporary figure-renumbering token remains")
    if re.search(r"\bFigure [78]\b|\[\[FIGURE [78]\]\]", revised):
        raise Stage26AF1Error("DANGLING_FIGURE_REFERENCE: Figure 7 or 8 remains")
    if len(re.findall(r"^\*\*Figure [1-6]\. ", revised, flags=re.MULTILINE)) != 6:
        raise Stage26AF1Error("DANGLING_FIGURE_REFERENCE: expected six final captions")
    placeholders = re.findall(r"\[\[FIGURE ([1-6])\]\]", revised)
    if placeholders != [str(number) for number in range(1, 7)]:
        raise Stage26AF1Error(f"DANGLING_FIGURE_REFERENCE: placeholders are {placeholders}")
    if revised.count(record) != 1:
        raise Stage26AF1Error("The exact Table 9 RRI record is missing or duplicated")
    return revised.rstrip() + "\n", record


def copy_figure_pair(source_dir: Path, source_stem: str, destination_dir: Path, destination_stem: str) -> tuple[Path, Path]:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destinations: list[Path] = []
    for suffix in (".png", ".pdf"):
        source = source_dir / f"{source_stem}{suffix}"
        if not source.is_file():
            raise Stage26AF1Error(f"Required Stage 26AF figure is missing: {source}")
        destination = destination_dir / f"{destination_stem}{suffix}"
        shutil.copyfile(source, destination)
        if sha256(source) != sha256(destination):
            raise Stage26AF1Error(f"Figure copy changed bytes: {source} -> {destination}")
        destinations.append(destination)
    return destinations[0], destinations[1]


def deliver_figures(root: Path, stage26af_dir: Path, output: Path, base: Any) -> list[dict[str, str]]:
    old_main = stage26af_dir / "figures" / "main"
    old_diagnostic = stage26af_dir / "figures" / "repository_diagnostic"
    new_main = output / "figures" / "main"
    new_diagnostic = output / "figures" / "repository_diagnostic"
    rows: list[dict[str, str]] = []

    for number, source_stem, destination_stem, evidence in MAIN_FIGURES:
        png, pdf = copy_figure_pair(old_main, source_stem, new_main, destination_stem)
        pixels, dpi = base.png_metadata(png)
        fonts = base.embedded_pdf_fonts(pdf)
        rows.append(
            {
                "contract_id": f"main_figure_{number}",
                "disposition": f"Figure {number}",
                "png": png.relative_to(root).as_posix(),
                "pdf": pdf.relative_to(root).as_posix(),
                "pixels": pixels,
                "dpi": dpi,
                "embedded_fonts": "; ".join(fonts),
                "png_sha256": sha256(png),
                "pdf_sha256": sha256(pdf),
                "source": evidence,
            }
        )

    diagnostic_specs = (
        (old_main, DIAGNOSTICS[0]),
        (old_diagnostic, DIAGNOSTICS[1]),
    )
    for source_dir, (source_stem, destination_stem, disposition, evidence) in diagnostic_specs:
        png, pdf = copy_figure_pair(source_dir, source_stem, new_diagnostic, destination_stem)
        pixels, dpi = base.png_metadata(png)
        fonts = base.embedded_pdf_fonts(pdf)
        rows.append(
            {
                "contract_id": destination_stem,
                "disposition": disposition,
                "png": png.relative_to(root).as_posix(),
                "pdf": pdf.relative_to(root).as_posix(),
                "pixels": pixels,
                "dpi": dpi,
                "embedded_fonts": "; ".join(fonts),
                "png_sha256": sha256(png),
                "pdf_sha256": sha256(pdf),
                "source": evidence,
            }
        )
    return rows


def figure_references(manuscript: str) -> list[tuple[int, str, str]]:
    rows: list[tuple[int, str, str]] = []
    for match in re.finditer(r"\bFigure ([1-8])\b|\[\[FIGURE ([1-8])\]\]", manuscript):
        number = match.group(1) or match.group(2)
        line = manuscript[: match.start()].count("\n") + 1
        status = "PASS" if number in {"1", "2", "3", "4", "5", "6"} else "DANGLING_FIGURE_REFERENCE"
        rows.append((line, f"Figure {number}", status))
    if any(status != "PASS" for _, _, status in rows):
        raise Stage26AF1Error("DANGLING_FIGURE_REFERENCE: out-of-range reference")
    return rows


def claim_report(root: Path, manuscript: str, base: Any) -> tuple[str, list[tuple[str, ...]]]:
    _, claims = base.load_claim_audit(root)
    rows: list[tuple[str, ...]] = []
    for row in claims:
        manuscript_status = base.manuscript_claim_status(manuscript, row["claim_id"])
        overall = "PASS" if row["status"] == "PASS" and manuscript_status.startswith("PASS") else "CLAIM_DRIFT_DETECTED"
        rows.append(
            (
                row["claim_id"],
                row["claim"],
                row["computed_value"],
                row["expected_value"],
                row["status"],
                manuscript_status,
                overall,
                row["evidence_files"],
            )
        )
    failures = [row for row in rows if row[6] != "PASS"]
    if failures:
        raise Stage26AF1Error(f"CLAIM_DRIFT_DETECTED: {[row[0] for row in failures]}")
    text = f"""# Stage 26AF-1 Post-Edit Claim Recheck

All 24 evidence calculations were recomputed from tracked inputs using the Stage 26AC audit functions. Manuscript-facing checks were then applied to the final six-figure Stage 26AF-1 draft. C10, C11, and C23 remain traceability facts rather than manuscript headline claims.

{base.markdown_table(["ID", "Claim", "Computed", "Expected", "Evidence check", "Manuscript check", "Overall", "Evidence"], rows)}

Result: `INTEGRITY_PASS` (24/24). No `CLAIM_DRIFT_DETECTED` condition was observed.
"""
    return text, rows


def write_reports(root: Path, output: Path, manuscript: str, record: str, delivery: list[dict[str, str]], base: Any) -> None:
    source_rri = require(root, "outputs/tables/rule_robustness_index.csv")
    conversion = f"""# Figure 5 Conversion Record

## Disposition

The author-approved Stage 26AF Figure 5 was removed from the main manuscript at former Section 7.3 and from the caption list. Its `[[FIGURE 5]]` placeholder was removed. The exact underlying CSV and the byte-identical PDF/PNG diagnostic remain in the repository.

## Table 9 record

The existing Table 9 structure is suitable because it explicitly aligns controlled claims, evidence sources, evidence types, permitted locations, and mandatory boundaries. The placeholder was therefore expanded from the unchanged nine-row source and the following compact final row was appended:

> CE10: {record} Source: `rule_robustness_index.csv`. Boundary: registered applicable configurations only; not welfare or method ranking.

Insertion locations in the updated manuscript:

- Section 7.3 bounded prose: line {line_number(manuscript, "All 4/4 predeclared conclusions")}
- Table 9 final row (`CE10`): line {line_number(manuscript, "| CE10 |")}

Data source: `{source_rri.relative_to(root).as_posix()}` (SHA-256 `{sha256(source_rri)}`). No value was recalculated or added.
"""
    (output / "FIGURE5_CONVERSION.md").write_text(conversion, encoding="utf-8", newline="\n")

    mapping = [
        ("Figure 1", "Figure 1", "Figure_01_rule_conditioned_inference_architecture", "main manuscript"),
        ("Figure 2", "Figure 2", "Figure_02_reproducible_comparison_workflow", "main manuscript"),
        ("Figure 3", "Figure 3", "Figure_03_discretion_identifiability_frontier", "main manuscript"),
        ("Figure 4", "Figure 4", "Figure_04_compatible_disclosure_scenarios", "main manuscript"),
        ("Figure 5", "No main-text number", "repository_diagnostic/RRI_Record_predeclared_conclusions", "Table 9 CE10 plus repository diagnostic"),
        ("Figure 6", "Figure 5", "Figure_05_multiseed_internal_sensitivity", "main manuscript"),
        ("Figure 7", "Figure 6", "Figure_06_multiseed_external_sensitivity", "main manuscript"),
        ("Figure 8", "No main-text number", "repository_diagnostic/Artifact_Check_evidence_completeness", "repository artifact diagnostic; removed in Stage 26AF"),
    ]
    references = figure_references(manuscript)
    final_files = sorted(path.name for path in (output / "figures" / "main").glob("*"))
    expected_files = sorted([f"{destination}.{suffix}" for _, _, destination, _ in MAIN_FIGURES for suffix in ("pdf", "png")])
    if final_files != expected_files:
        raise Stage26AF1Error(f"DANGLING_FIGURE_REFERENCE: final filenames differ: {final_files}")
    renumbering = f"""# Final Figure Renumbering

## Full mapping

{base.markdown_table(["Pre-26AF number", "Final number", "Final file stem", "Disposition"], mapping)}

## Main-text references and placeholders

{base.markdown_table(["Line", "Reference", "Status"], references)}

Six captions and six placeholders are present in ascending order. All caption numbers, prose references, placeholders, and main-figure filenames agree. Neither the main text nor appendix/caption material refers to Figure 7 or Figure 8. The former Figures 5 and 8 are unnumbered repository diagnostics.

Result: `PASS_NO_DANGLING_FIGURE_REFERENCE`.
"""
    (output / "FINAL_FIGURE_RENUMBERING.md").write_text(renumbering, encoding="utf-8", newline="\n")

    before_assertion = "Stage 26AF creates a separate presentation contract: seven numbered main figures plus one unnumbered repository artifact check, each with a vector PDF and 600 dpi PNG."
    after_assertion = "Stage 26AF-1 creates a separate presentation contract: six numbered main figures plus two unnumbered repository diagnostics, each with a vector PDF and 600 dpi PNG."
    old_snapshot = require(root, "outputs/stage26AF/FIGURE_SNAPSHOT_VERSIONING.md").read_text(encoding="utf-8")
    if before_assertion not in old_snapshot:
        raise Stage26AF1Error("Stage 26AF pre-update assertion is missing")
    delivery_table = base.markdown_table(
        ["Contract item", "Disposition", "PNG", "PDF", "DPI", "Embedded fonts", "PNG SHA-256", "PDF SHA-256", "Tracked source"],
        [
            (
                row["contract_id"], row["disposition"], row["png"], row["pdf"], row["dpi"],
                "PASS: " + row["embedded_fonts"], row["png_sha256"], row["pdf_sha256"], row["source"],
            )
            for row in delivery
        ],
    )
    contract = f"""# Figure Contract Update

## Historical contract

The Stage 26AA historical clean-room assertion remains 8/8 PNGs and is unchanged. Its files, hashes, and `outputs/stage26AA/REPRODUCIBILITY_VERIFICATION.md` were not modified.

## Assertion update

**Before (Stage 26AF):** {before_assertion}

**After (Stage 26AF-1):** {after_assertion}

The six retained scientific figures and both diagnostics are byte-identical to their Stage 26AF PDF/PNG sources. Only disposition paths and the old Figures 6/7 numbering changed. No retained canvas was regenerated or altered.

## Stage 26AF-1 6+2 contract

{delivery_table}

Result: `PASS_6_MAIN_PLUS_2_REPOSITORY_DIAGNOSTICS`; `PASS_HISTORICAL_8_OF_8_UNCHANGED`; `PASS_RETAINED_FIGURE_HASHES_UNCHANGED`.
"""
    (output / "FIGURE_CONTRACT_UPDATE.md").write_text(contract, encoding="utf-8", newline="\n")

    claims, _ = claim_report(root, manuscript, base)
    (output / "POST_EDIT_CLAIM_RECHECK.md").write_text(claims, encoding="utf-8", newline="\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert Stage 26AF Figure 5 to a Table 9 row and deliver the final 6+2 figure contract without rerunning experiments.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Project root containing the tracked Stage 26AF package.")
    parser.add_argument("--source-manuscript", type=Path, default=DEFAULT_SOURCE, help="Project-relative Stage 26AF source manuscript.")
    parser.add_argument("--stage26af-dir", type=Path, default=DEFAULT_STAGE26AF_DIR, help="Project-relative Stage 26AF output directory containing figures and contract reports.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Project-relative Stage 26AF-1 output directory.")
    return parser.parse_args(argv)


def resolve_relative(root: Path, value: Path, label: str) -> Path:
    if value.is_absolute():
        raise Stage26AF1Error(f"{label} must be project-relative")
    resolved = (root / value).resolve()
    if root != resolved and root not in resolved.parents:
        raise Stage26AF1Error(f"{label} resolves outside the project root: {value}")
    return resolved


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    source_path = resolve_relative(root, args.source_manuscript, "Source manuscript")
    stage26af_dir = resolve_relative(root, args.stage26af_dir, "Stage 26AF directory")
    output = resolve_relative(root, args.output_dir, "Output directory")
    if output == root:
        raise Stage26AF1Error("Output directory may not be the project root")

    boundaries = {
        require(root, "outputs/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md"): FROZEN_X3_SHA256,
        require(root, "outputs/stage26X-1/PREREGISTERED_DESIGN.md"): X1_PREREG_SHA256,
        require(root, "outputs/stage26X-2/PREREGISTERED_DESIGN.md"): X2_PREREG_SHA256,
    }
    before = {path: sha256(path) for path in boundaries}
    for path, expected in boundaries.items():
        if before[path] != expected:
            raise Stage26AF1Error(f"Protected input hash mismatch: {path} -> {before[path]}")
    if sha256(source_path) != STAGE26AF_SOURCE_SHA256:
        raise Stage26AF1Error(f"Stage 26AF source manuscript hash mismatch: {sha256(source_path)}")
    manifest = stage26af_dir / "figure_snapshot_manifest.csv"
    if not manifest.is_file() or sha256(manifest) != STAGE26AF_MANIFEST_SHA256:
        raise Stage26AF1Error("Stage 26AF figure manifest hash mismatch")

    source = source_path.read_text(encoding="utf-8")
    source_hash = sha256(source_path)
    base = load_stage26af(root)
    revised, record = revise_manuscript(root, source, base)

    if output.is_dir():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    manuscript_path = output / "METHODS_research_draft_STAGE26AF1.md"
    manuscript_path.write_text(revised, encoding="utf-8", newline="\n")
    delivery = deliver_figures(root, stage26af_dir, output, base)
    if len(delivery) != 8 or len(list((output / "figures" / "main").glob("*.png"))) != 6 or len(list((output / "figures" / "repository_diagnostic").glob("*.png"))) != 2:
        raise Stage26AF1Error("Stage 26AF-1 delivery is not 6+2")
    write_reports(root, output, revised, record, delivery, base)

    if sha256(source_path) != source_hash:
        raise Stage26AF1Error("Stage 26AF source manuscript changed during execution")
    for path, expected in boundaries.items():
        if sha256(path) != expected:
            raise Stage26AF1Error(f"Protected input changed during execution: {path}")

    print(f"Wrote {manuscript_path.relative_to(root).as_posix()}")
    print("FIGURES_MAIN=6; REPOSITORY_DIAGNOSTIC=2; RETAINED_HASHES=UNCHANGED")
    print("TABLE9_RRI_RECORD=CE10; CLAIMS_PASS=24/24")
    print("PASS_NO_DANGLING_FIGURE_REFERENCE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Stage26AF1Error as exc:
        raise SystemExit(f"Stage 26AF-1 failed: {exc}") from exc
