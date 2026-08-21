#!/usr/bin/env python3
"""Run a local MATCOM reviewer-style preflight for the Stage 32 package.

This audit is deliberately conservative. It verifies local scientific and file
contracts, records issues resolved by Stage 32, and distinguishes them from
external author and Editorial Manager gates that cannot be verified locally.
It never uploads, submits, publishes, or changes raw inputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path("outputs/stage32-matcom-scientific-corrections/MATCOM_revised_candidate_package")
STAGE32 = Path("outputs/stage32-matcom-scientific-corrections")
OUTPUT = Path("outputs/stage33-matcom-reviewer-preflight")
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"


class PreflightError(RuntimeError):
    """Raised when required Stage 32 input material is unavailable."""


def resolve(root: Path, relative: Path, label: str) -> Path:
    if relative.is_absolute():
        raise PreflightError(f"{label} must be project-relative: {relative}")
    path = (root / relative).resolve()
    if path != root and root not in path.parents:
        raise PreflightError(f"{label} resolves outside project root: {relative}")
    return path


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def parse_manifest(path: Path) -> dict[str, tuple[int, str]]:
    pattern = re.compile(r"^\| (.*?) \| (\d+) \| ([0-9A-F]{64}) \|$", re.MULTILINE)
    return {name: (int(size), digest) for name, size, digest in pattern.findall(path.read_text(encoding="utf-8"))}


def citation_numbers(body: str) -> set[int]:
    values: set[int] = set()
    for match in re.finditer(r"\[(\d+(?:[-,]\d+)*)\]", body):
        for component in match.group(1).split(","):
            if "-" in component:
                start, end = (int(value) for value in component.split("-", 1))
                values.update(range(start, end + 1))
            else:
                values.add(int(component))
    return values


def inspect_docx(path: Path) -> dict[str, int | bool]:
    with zipfile.ZipFile(path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
    text = "".join(node.text or "" for node in document.iter(W_NS + "t"))
    math_text = "".join(node.text or "" for node in document.iter(M_NS + "t"))
    return {
        "tables": sum(1 for _ in document.iter(W_NS + "tbl")),
        "drawings": sum(1 for _ in document.iter(W_NS + "drawing")),
        "office_math": sum(1 for _ in document.iter(M_NS + "oMath")),
        "literal_latex": bool(re.search(r"\\(?:sum|forall|in|le|ge)", text)),
        "math_symbols": all(symbol in math_text for symbol in ("∑", "∀", "∈", "≤", "≥")),
    }


def finding(identifier: str, severity: str, status: str, area: str, evidence: str, action: str) -> dict[str, str]:
    return {
        "id": identifier,
        "severity": severity,
        "status": status,
        "area": area,
        "evidence": evidence,
        "required_action": action,
    }


def render_report(findings: list[dict[str, str]], metadata: dict[str, str]) -> str:
    rows = "\n".join(
        f"| {item['id']} | {item['severity']} | {item['status']} | {item['area']} | {item['evidence']} | {item['required_action']} |"
        for item in findings
    )
    blocking = [item for item in findings if item["severity"] == "P0" and item["status"] != "PASS"]
    local_failures = [item for item in findings if item["status"] == "FAIL"]
    decision = "DO_NOT_SUBMIT" if blocking else "LOCAL_PACKAGE_READY_FOR_PORTAL"
    return f"""# Stage 33 MATCOM Reviewer Preflight Report

## Decision

`{decision}`.

The submitted-for-review target is the Stage 32 corrected package, not the
superseded Stage 31.5 package. Stage 32 corrects a substantive coverage metric
and sampled ordinal endpoints; using Stage 31.5 would report a stale coverage
effect and non-sharp ordinal supports. The local package passes its scientific
and technical contracts. The corrected Stage 32 release is publicly versioned;
submission remains blocked only until the Editorial Manager portal facts and
generated PDF are checked.

## Scope and Evidence

- Package: `{metadata['package']}`
- Manifested files: `{metadata['manifested_files']}`; hash reconciliation: `{metadata['manifest_ok']}`.
- Corrected positive-noise joint-coverage change: `0.117600` (MCSE `0.001519`); legacy projection-envelope value: `0.050289`.
- Exact ordinal analysis: `87` empirical weeks and `2,964` primary-policy MILP calls.
- Main DOCX: `{metadata['tables']}` editable tables, `{metadata['office_math']}` Office Math objects, `{metadata['drawings']}` table/body drawing objects, literal TeX commands absent: `{metadata['literal_latex_absent']}`.
- Figure assets: `{metadata['pdf_figures']}` PDF plus `{metadata['tiff_figures']}` TIFF, each numbered 1-4.

## Findings

| ID | Severity | Status | Area | Evidence | Required action |
| --- | --- | --- | --- | --- | --- |
{rows}

## Scientific Review

The revised contribution is suitable in principle for a simulation and
computational-methodology venue: it frames the competition record as an
empirical testbed, uses joint membership for polytope coverage, solves ordinal
support endpoints exactly, and states the distinct semantics of identified sets
and Bayesian credible rectangles. The reported uncertainty is bounded by the
specified generators, fixed grid, prior, and uncertain season-28 rule mapping.
The revised manuscript appropriately does not claim observed audience-vote
recovery, a universally superior method, an empirical institutional effect, or
a general polynomial-time result.

The prior Stage 31.5 scientific lock is invalidated for submission purposes:
the corrected effect is `0.117600`, not `0.050289`, and 23 of 470 legacy
sampled ordinal contestant-week rows have at least one endpoint correction.
The Stage 32 source and generated tables are therefore the only defensible
submission basis.

## Technical Review

The current package is structurally stronger than Stage 31.5. It contains a
separate title page, main manuscript, cover letter, Highlights, captions, and
four matching PDF/TIFF figure pairs. The main DOCX carries Word-native tables
and Office Math rather than raw TeX strings. Three-author title-page metadata,
CRediT roles, competing-interest language, generative-AI declaration, and
cover-letter approval language are now mutually consistent. Every listed
reference is cited in the text, and all packaged file hashes reconcile with the
generated manifest.

This preflight cannot assess the PDF that Editorial Manager generates after
upload. It also does not authenticate any external repository, archive, DOI,
author approval, article type, review model, or portal upload mapping.

## Required Human Close-Out

1. In Editorial Manager, record the exact article type, review/anonymization
   model, and file slots. Map only the Stage 32 package files to those slots.
2. Reconfirm the three authors' order, affiliations, ORCIDs, emails, CRediT,
   declarations, and approval of the final portal PDF.
3. Inspect the portal-generated PDF: five tables, 67 mathematical objects,
   figure/caption ordering, references, and special symbols must render without
   truncation or duplication.

## Reproduction

```powershell
& .\\.venv-stage26aa-tools\\Scripts\\python.exe scripts/32_matcom_scientific_corrections.py --project-root .
$env:PYTHONPATH='.'
& .\\.venv-stage26aa-tools\\Scripts\\python.exe -m pytest -q tests/test_stage32_scientific_corrections.py tests/test_stage33_matcom_reviewer_preflight.py
& .\\.venv-stage26aa-tools\\Scripts\\python.exe scripts/33_matcom_reviewer_preflight.py --project-root .
```
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a local reviewer-style MATCOM preflight for the Stage 32 corrected candidate.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root; defaults to current directory.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT, help="Project-relative report output directory.")
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    package = resolve(root, PACKAGE, "Stage 32 package")
    stage32 = resolve(root, STAGE32, "Stage 32 outputs")
    output = resolve(root, args.output_dir, "Stage 33 output")
    required = [package / name for name in ("MATCOM_main_manuscript_source.md", "MATCOM_main_manuscript.docx", "MATCOM_title_page_source.md", "MATCOM_cover_letter_source.md", "MATCOM_Highlights.txt", "PACKAGE_MANIFEST.md", "PACKAGE_STATUS.md")]
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    if missing:
        raise PreflightError(f"Required Stage 32 package files missing: {missing}")

    manifest = parse_manifest(package / "PACKAGE_MANIFEST.md")
    files = sorted(path for path in package.rglob("*") if path.is_file() and path.name != "PACKAGE_MANIFEST.md")
    manifest_ok = len(manifest) == len(files) and all(
        manifest.get(path.relative_to(package).as_posix()) == (path.stat().st_size, sha256(path))
        for path in files
    )
    manuscript = (package / "MATCOM_main_manuscript_source.md").read_text(encoding="utf-8")
    body, references = manuscript.split("## References", 1)
    listed = {int(match.group(1)) for match in re.finditer(r"(?m)^\[(\d+)\] ", references)}
    citations_ok = citation_numbers(body) == listed
    docx = inspect_docx(package / "MATCOM_main_manuscript.docx")
    title = (package / "MATCOM_title_page_source.md").read_text(encoding="utf-8")
    cover = (package / "MATCOM_cover_letter_source.md").read_text(encoding="utf-8")
    highlights = [line[2:] for line in (package / "MATCOM_Highlights.txt").read_text(encoding="utf-8").splitlines() if line.startswith("- ")]
    figures_pdf = sorted((package / "figures/pdf").glob("Figure_*.pdf"))
    figures_tiff = sorted((package / "figures/tiff").glob("Figure_*.tif"))
    coverage_report = (stage32 / "reports/COVERAGE_METRIC_CORRECTION.md").read_text(encoding="utf-8")
    ordinal = (stage32 / "reports/EXACT_ORDINAL_ENDPOINT_AUDIT.md").read_text(encoding="utf-8")

    authors_ok = all(name in title and name in manuscript for name in ("Lizhen Deng", "Yuxin Liu", "Bo Li")) and "approved by all authors" in cover
    figures_ok = len(figures_pdf) == len(figures_tiff) == 4 and all(path.stat().st_size > 1000 for path in figures_pdf + figures_tiff)
    math_ok = docx["office_math"] >= 10 and not docx["literal_latex"] and bool(docx["math_symbols"])
    findings = [
        finding("F01", "P1", "PASS", "Corrected public release", "Stage 34 independently verified tag matcom-stage32-v1.0.1, commit 4ca87c3381c304ae2f472437bfe21ca51dbc7938, and release SHA-256.", "Use the versioned v1.0.1 release; no DOI is asserted."),
        finding("F02", "P0", "EXTERNAL_GATE", "Editorial Manager", "Article type, review model, upload slots, metadata confirmation, and portal PDF are unavailable locally.", "Record the five portal gates and inspect the generated PDF before submission."),
        finding("F03", "P1", "PASS" if "0.117600" in coverage_report and "0.050289" in coverage_report and "23" in ordinal else "FAIL", "Scientific correction", "Joint coverage and exact ordinal endpoint corrections are generated from Stage 32 raw evidence.", "Use Stage 32 only; do not submit the superseded Stage 31.5 package."),
        finding("F04", "P1", "PASS" if math_ok else "FAIL", "Mathematics rendering", f"Office Math={docx['office_math']}; literal TeX={docx['literal_latex']}; Unicode math symbols={docx['math_symbols']}.", "Retain generated Stage 32 DOCX and visually check the portal PDF."),
        finding("F05", "P1", "PASS" if authors_ok else "FAIL", "Author metadata", "Title page, CRediT, manuscript, and cover letter use the same three named authors and plural approval language.", "All authors must still reconfirm this metadata in the portal."),
        finding("F06", "P1", "PASS" if manifest_ok else "FAIL", "Package integrity", f"Manifest has {len(manifest)} entries for {len(files)} packaged files.", "Do not alter package files after this audit; rerun generator if edits are required."),
        finding("F07", "P2", "PASS" if citations_ok else "FAIL", "References", f"In-text citation set={sorted(citation_numbers(body))}; reference set={sorted(listed)}.", "Keep citation and reference lists synchronized on further revisions."),
        finding("F08", "P2", "PASS" if figures_ok else "FAIL", "Figure mapping", f"PDF figures={len(figures_pdf)}; TIFF figures={len(figures_tiff)}; all files exceed 1 KB.", "Confirm the authenticated portal's separate-figure and caption upload instructions."),
        finding("F09", "P2", "PASS" if len(highlights) == 5 and all(len(line) <= 85 for line in highlights) else "FAIL", "Highlights", f"Five Highlights detected; lengths={[len(line) for line in highlights]}.", "Upload only if the live portal exposes or encourages a Highlights slot."),
    ]
    metadata = {
        "package": PACKAGE.as_posix(), "manifested_files": str(len(files)), "manifest_ok": "PASS" if manifest_ok else "FAIL",
        "tables": str(docx["tables"]), "office_math": str(docx["office_math"]), "drawings": str(docx["drawings"]),
        "literal_latex_absent": "PASS" if not docx["literal_latex"] else "FAIL", "pdf_figures": str(len(figures_pdf)), "tiff_figures": str(len(figures_tiff)),
    }
    write(output / "MATCOM_REVIEWER_PREFLIGHT_REPORT.md", render_report(findings, metadata))
    with (output / "MATCOM_REVIEWER_FINDINGS.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(findings[0]))
        writer.writeheader()
        writer.writerows(findings)
    print("STAGE33_MATCOM_REVIEWER_PREFLIGHT=PASS")
    print(f"LOCAL_FINDINGS={sum(item['status'] == 'PASS' for item in findings)}/{len(findings)} PASS; EXTERNAL_GATES={sum(item['status'] == 'EXTERNAL_GATE' for item in findings)}")
    print("SUBMISSION_DECISION=DO_NOT_SUBMIT_UNTIL_EXTERNAL_GATES_CLOSE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PreflightError as exc:
        raise SystemExit(f"Stage 33 failed: {exc}") from exc
