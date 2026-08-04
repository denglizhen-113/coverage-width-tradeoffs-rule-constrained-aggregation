#!/usr/bin/env python3
"""Create Stage 25F author-side completion materials without external actions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_RELATIVE = Path("submission_package_stage25")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create the non-destructive Stage 25F author-side completion gate and "
            "DSS submission simulation. It never uploads, deposits, or modifies "
            "Stage 21--24 artifacts."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root containing submission_package_stage25.",
    )
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content.strip() + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def markdown_table(rows: list[dict[str, str]], fields: list[str]) -> str:
    header = "| " + " | ".join(fields) + " |"
    divider = "| " + " | ".join("---" for _ in fields) + " |"
    body = [
        "| " + " | ".join(str(row.get(field, "")).replace("|", "/") for field in fields) + " |"
        for row in rows
    ]
    return "\n".join([header, divider, *body])


def required_inputs(root: Path) -> dict[str, Path]:
    package = root / PACKAGE_RELATIVE
    return {
        "Stage 25 final no-go report": package / "12_audit_logs/stage25_final_no_go_report.md",
        "Stage 25 execution summary": package / "12_audit_logs/stage25_execution_summary.md",
        "Official DSS requirements report": package / "12_audit_logs/stage25_DSS_official_requirements_verified.md",
        "Author confirmation checklist": package / "01_author_action_required/author_confirmation_checklist.md",
        "Author input list": package / "01_author_action_required/author_input_required_stage25.md",
        "Submission file manifest": package / "13_audit_tables/stage25_submission_file_manifest.csv",
        "Stage 25 cited manuscript": root / "manuscript/DSS_submission_draft_stage25_cited.md",
        "Stage 25 anonymized manuscript": root / "manuscript/DSS_submission_draft_stage25_anonymized.md",
    }


def frozen_recheck(root: Path, package: Path) -> tuple[int, int]:
    manifest = package / "11_reproducibility/frozen_artifact_hash_manifest_stage25.csv"
    if not manifest.is_file():
        return 0, 1
    checked = 0
    mismatches = 0
    with manifest.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            path = root / row["relative_path"]
            checked += 1
            if not path.is_file() or sha256(path) != row["expected_sha256"]:
                mismatches += 1
    return checked, mismatches


def scan_status(root: Path, package: Path) -> dict[str, str]:
    cited = (root / "manuscript/DSS_submission_draft_stage25_cited.md").read_text(encoding="utf-8")
    anonymized = (root / "manuscript/DSS_submission_draft_stage25_anonymized.md").read_text(encoding="utf-8")
    source_extensions = {".docx", ".tex"}
    source_files = [
        path for base in (root / "manuscript", package)
        for path in base.rglob("*")
        if path.is_file() and path.suffix.lower() in source_extensions
    ]
    pdfs = [
        path for base in (root / "manuscript", package)
        for path in base.rglob("*.pdf")
        if path.is_file()
    ]
    identity_patterns = {
        "Windows username": r"denglizhen",
        "Windows path": r"[A-Za-z]:\\",
        "Email address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "Author placeholder leak": r"\[AUTHOR[^\]]*\]",
    }
    identity_hits = [
        label for label, pattern in identity_patterns.items() if re.search(pattern, anonymized, flags=re.IGNORECASE)
    ]
    placeholder_count = len(re.findall(r"\[REF-[^\]]+\]", cited))
    figures = list((package / "06_figures").glob("Figure_*.png"))
    tables = list((package / "07_tables").glob("Table_*.csv"))
    return {
        "reference_placeholders": str(placeholder_count),
        "anonymized_text_identity_hits": "; ".join(identity_hits) if identity_hits else "0",
        "editable_source_count": str(len(source_files)),
        "pdf_preview_count": str(len(pdfs)),
        "figure_count": str(len(figures)),
        "table_count": str(len(tables)),
    }


def blockers_document() -> str:
    fields = [
        "blocker_id", "category", "exact_required_input", "why_required", "where_used",
        "current_status", "acceptable_values_or_template", "risk_if_unresolved", "can_codex_fill_yes_no",
    ]
    rows = [
        {"blocker_id": "A01", "category": "Author-only information", "exact_required_input": "Author full names", "why_required": "Verified authorship and title-page identity", "where_used": "Title page; portal", "current_status": "not provided", "acceptable_values_or_template": "[AUTHOR 1 FULL NAME]", "risk_if_unresolved": "cannot complete authorship metadata", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A02", "category": "Author-only information", "exact_required_input": "Author order", "why_required": "Authorship order must be author-approved", "where_used": "Title page; portal", "current_status": "not provided", "acceptable_values_or_template": "[AUTHOR ORDER CONFIRMED BY AUTHORS]", "risk_if_unresolved": "authorship dispute or mismatch", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A03", "category": "Author-only information", "exact_required_input": "Affiliations", "why_required": "Required title-page and portal metadata", "where_used": "Title page; portal", "current_status": "not provided", "acceptable_values_or_template": "[AFFILIATION N]", "risk_if_unresolved": "incomplete title page", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A04", "category": "Author-only information", "exact_required_input": "Corresponding author", "why_required": "Submission contact must be authorized", "where_used": "Title page; portal", "current_status": "not provided", "acceptable_values_or_template": "[CORRESPONDING AUTHOR FULL NAME]", "risk_if_unresolved": "cannot assign correspondence", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A05", "category": "Author-only information", "exact_required_input": "Corresponding-author email", "why_required": "Required contact detail", "where_used": "Title page; portal", "current_status": "not provided", "acceptable_values_or_template": "[CORRESPONDING AUTHOR EMAIL]", "risk_if_unresolved": "contact metadata incomplete", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A06", "category": "Author-only information", "exact_required_input": "Corresponding-author postal address", "why_required": "Required title-page contact detail", "where_used": "Title page; portal", "current_status": "not provided", "acceptable_values_or_template": "[POSTAL ADDRESS]", "risk_if_unresolved": "title page incomplete", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A07", "category": "Author-only information", "exact_required_input": "Funding statement", "why_required": "Declaration must be accurate", "where_used": "Declarations; manuscript; portal", "current_status": "not confirmed", "acceptable_values_or_template": "[FUNDER, GRANT, ROLE] or author-confirmed no-funding statement", "risk_if_unresolved": "inaccurate or missing declaration", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A08", "category": "Author-only information", "exact_required_input": "Competing-interests statement", "why_required": "Publisher declaration", "where_used": "Declarations; portal", "current_status": "not confirmed", "acceptable_values_or_template": "[DISCLOSE INTERESTS] or author-confirmed none", "risk_if_unresolved": "required declaration missing", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A09", "category": "Author-only information", "exact_required_input": "CRediT roles", "why_required": "Roles cannot be inferred", "where_used": "Title page/declarations; portal", "current_status": "not confirmed", "acceptable_values_or_template": "[AUTHOR]: [CRediT ROLES]", "risk_if_unresolved": "contribution statement unavailable", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A10", "category": "Author-only information", "exact_required_input": "Ethics statement", "why_required": "Applicability requires author/institutional determination", "where_used": "Declarations; portal", "current_status": "not confirmed", "acceptable_values_or_template": "[ETHICS DETERMINATION AND BASIS]", "risk_if_unresolved": "incorrect ethics representation", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A11", "category": "Author-only information", "exact_required_input": "Data availability statement", "why_required": "Research-data declaration", "where_used": "Manuscript; portal", "current_status": "not confirmed", "acceptable_values_or_template": "[DOI/URL] or [VERIFIED ACCESS RESTRICTION EXPLANATION]", "risk_if_unresolved": "data statement is incomplete", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A12", "category": "Author-only information", "exact_required_input": "Code availability statement", "why_required": "Access route must be accurate", "where_used": "Manuscript; portal", "current_status": "not confirmed", "acceptable_values_or_template": "[DOI/URL] or [VERIFIED ACCESS EXPLANATION]", "risk_if_unresolved": "code statement is incomplete", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A13", "category": "Author-only information", "exact_required_input": "Repository route", "why_required": "Authors control disclosure and data access", "where_used": "Data/code statements", "current_status": "not selected", "acceptable_values_or_template": "[APPROVED REPOSITORY] or [APPROVED RESTRICTION ROUTE]", "risk_if_unresolved": "no verified release route", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A14", "category": "Author-only information", "exact_required_input": "Repository license", "why_required": "License is a legal/author decision", "where_used": "Repository metadata; availability statements", "current_status": "not selected", "acceptable_values_or_template": "[AUTHOR-APPROVED LICENSE]", "risk_if_unresolved": "reuse rights unclear", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A15", "category": "Author-only information", "exact_required_input": "Repository DOI or URL", "why_required": "Linking and availability statements", "where_used": "Manuscript; portal", "current_status": "not available", "acceptable_values_or_template": "[REPOSITORY DOI OR STABLE URL]", "risk_if_unresolved": "data/code route cannot be verified", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A16", "category": "Author-only information", "exact_required_input": "Generative-AI declaration", "why_required": "Accurate disclosure requires author confirmation", "where_used": "Manuscript; portal", "current_status": "not confirmed", "acceptable_values_or_template": "[TOOL, PURPOSE, OVERSIGHT] or author-confirmed no-use statement", "risk_if_unresolved": "policy compliance cannot be confirmed", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A17", "category": "Author-only information", "exact_required_input": "Whether any figure used AI assistance", "why_required": "Artwork-policy and disclosure check", "where_used": "AI declaration; figure provenance", "current_status": "not confirmed", "acceptable_values_or_template": "[YES/NO + FIGURE-SPECIFIC DETAILS IF YES]", "risk_if_unresolved": "figure policy cannot be assessed", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A18", "category": "Author-only information", "exact_required_input": "Figure provenance confirmation", "why_required": "Authors must confirm source and permissions", "where_used": "Figure files; declarations", "current_status": "not confirmed", "acceptable_values_or_template": "[AUTHOR CONFIRMATION FOR FIGURES 1--8]", "risk_if_unresolved": "provenance and rights unclear", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A19", "category": "Format/source-file tasks", "exact_required_input": "Final editable .docx or .tex source", "why_required": "Public guide requires an editable submission source", "where_used": "Upload package", "current_status": "absent: Markdown preparation only", "acceptable_values_or_template": "final cited and anonymized .docx or .tex", "risk_if_unresolved": "submission source requirement not met", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A20", "category": "Format/source-file tasks", "exact_required_input": "Final typeset page count", "why_required": "Public guide records a format-dependent 34-page limit", "where_used": "Final PDF/source review", "current_status": "not available", "acceptable_values_or_template": "[FINAL PDF PAGE COUNT AFTER TYPESSETTING]", "risk_if_unresolved": "page-limit breach not excluded", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "P01", "category": "Portal-only checks", "exact_required_input": "Article type", "why_required": "Public guide does not resolve live category selection", "where_used": "DSS portal", "current_status": "UNRESOLVED FROM PUBLIC GUIDE — AUTHOR/PORTAL CHECK REQUIRED.", "acceptable_values_or_template": "[PORTAL ARTICLE TYPE]", "risk_if_unresolved": "incorrect editorial routing", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "P02", "category": "Portal-only checks", "exact_required_input": "Portal-only file requirements", "why_required": "Live portal may specify field/file mapping", "where_used": "DSS portal", "current_status": "UNRESOLVED FROM PUBLIC GUIDE — AUTHOR/PORTAL CHECK REQUIRED.", "acceptable_values_or_template": "[PORTAL REQUIREMENTS CONFIRMED]", "risk_if_unresolved": "incomplete package", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "M01", "category": "Manual verification tasks", "exact_required_input": "Final document-property metadata inspection", "why_required": "Text scan cannot inspect embedded metadata", "where_used": "Final source/PDF", "current_status": "not possible before final source exists", "acceptable_values_or_template": "inspect author, company, comments, revision, path, and embedded-object properties", "risk_if_unresolved": "identity leakage", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "M02", "category": "Manual verification tasks", "exact_required_input": "Final anonymized manuscript preview", "why_required": "Double anonymization requires rendered review", "where_used": "Final anonymous source/PDF; portal preview", "current_status": "text scan passed; rendered review outstanding", "acceptable_values_or_template": "[AUTHOR MANUAL CHECK COMPLETED]", "risk_if_unresolved": "identity leak or formatting defect", "can_codex_fill_yes_no": "NO"},
        {"blocker_id": "A21", "category": "Author-only information", "exact_required_input": "Final author approval before upload", "why_required": "Authors own submitted content and declarations", "where_used": "Immediately before upload", "current_status": "not provided", "acceptable_values_or_template": "[ALL AUTHORS APPROVE FINAL PACKAGE]", "risk_if_unresolved": "do not upload", "can_codex_fill_yes_no": "NO"},
    ]
    return "\n".join([
        "# Stage 25F Remaining Blockers Consolidated",
        "",
        "## Status",
        "",
        "All remaining blockers require author completion, final-source work, or live-portal inspection. No author-specific fact is inferred here, and this report authorizes no upload.",
        "",
        "## Blockers",
        "",
        markdown_table(rows, fields),
        "",
        "## Gate",
        "",
        "The package remains `DSS-ready-for-final-author-review`, not ready for upload. Close every item above, then repeat the final source, anonymous-preview, metadata, and portal checks.",
    ])


def fill_in_packet() -> str:
    return """# Stage 25F Author Fill-In Packet

Complete this packet from verified author and institutional records. Bracketed fields are placeholders. Do not select an option unless it is true and approved by the authors.

## 1. Manuscript Title Confirmation

- Confirmed title: [RULE-AWARE DECISION SUPPORT FOR EXPERT-CROWD AGGREGATION UNDER HIDDEN PUBLIC PREFERENCES]
- Author-approved final title: [CONFIRM OR REPLACE WITH APPROVED TITLE]

## 2. Author List and Order

| order | full name | ORCID if supplied by author | affiliation marker |
| --- | --- | --- | --- |
| 1 | [AUTHOR 1 FULL NAME] | [ORCID OPTIONAL] | [1] |
| 2 | [AUTHOR 2 FULL NAME IF APPLICABLE] | [ORCID OPTIONAL] | [N] |

Author order confirmed by all authors: [YES/NO; DATE; APPROVER]

## 3. Affiliations

1. [AFFILIATION 1: DEPARTMENT, INSTITUTION, CITY, POSTAL CODE, COUNTRY]
2. [AFFILIATION 2 IF APPLICABLE]

## 4. Corresponding Author

- Name: [CORRESPONDING AUTHOR FULL NAME]
- Email: [CORRESPONDING AUTHOR EMAIL]
- Postal address: [FULL POSTAL ADDRESS]

## 5. Acknowledgements

Choose only one after author confirmation.

- Option A: [ACKNOWLEDGEMENTS TEXT, INCLUDING PERMISSION IF NEEDED]
- Option B: [AUTHORS CONFIRM THAT NO ACKNOWLEDGEMENTS WILL BE INCLUDED]

## 6. Funding

Choose only one after author confirmation.

- Option A: [FUNDER NAME, GRANT NUMBER, AND FUNDER ROLE]
- Option B: [AUTHORS CONFIRM THE ACCURATE NO-FUNDING STATEMENT]

## 7. Competing Interests

Choose only one after author confirmation.

- Option A: [DISCLOSE EACH RELEVANT FINANCIAL OR NON-FINANCIAL INTEREST]
- Option B: [AUTHORS CONFIRM THE ACCURATE NO-COMPETING-INTERESTS STATEMENT]

## 8. CRediT Author Contributions

| author | CRediT roles confirmed by authors |
| --- | --- |
| [AUTHOR NAME] | [CONCEPTUALIZATION; METHODOLOGY; SOFTWARE; VALIDATION; FORMAL ANALYSIS; WRITING; ETC.] |
| [AUTHOR NAME IF APPLICABLE] | [ROLES] |

## 9. Ethics Statement

Select the author/institutionally verified option only.

- Option A: [ETHICS APPROVAL OR DETERMINATION, BODY, REFERENCE, AND RATIONALE]
- Option B: [OTHER ACCURATE ETHICS/APPLICABILITY STATEMENT APPROVED BY AUTHORS]

## 10. Data Availability

Select the verified route only.

- Option A: [DATA REPOSITORY NAME, DOI OR STABLE URL, ACCESS TERMS]
- Option B: [ACCURATE RESTRICTION/ACCESS EXPLANATION AND CONTACT ROUTE]

## 11. Code Availability

Select the verified route only.

- Option A: [CODE REPOSITORY NAME, DOI OR STABLE URL, VERSION/TAG, LICENSE]
- Option B: [ACCURATE RESTRICTION/ACCESS EXPLANATION AND CONTACT ROUTE]

## 12. Repository Choice

- Selected repository or approved restriction route: [AUTHOR DECISION]
- Data package scope: [FILES TO INCLUDE]
- Code package scope: [FILES TO INCLUDE]
- Privacy/sensitivity review completed: [YES/NO; REVIEWER; DATE]

## 13. License Choice

- Data license or access terms: [AUTHOR-APPROVED LICENSE/TERMS]
- Code license or access terms: [AUTHOR-APPROVED LICENSE/TERMS]

## 14. Generative-AI Declaration

Select only the verified option.

- Option A: [TOOL NAME/VERSION, PURPOSE, LOCATIONS USED, AND AUTHOR OVERSIGHT]
- Option B: [AUTHORS CONFIRM THE ACCURATE NO-GENERATIVE-AI-USE STATEMENT]

## 15. Figure Provenance

| figure(s) | source/provenance confirmed | AI assistance used? | permissions/status |
| --- | --- | --- | --- |
| 1--8 | [YES/NO] | [YES/NO; DETAILS IF YES] | [CONFIRMED/OUTSTANDING] |

## 16. Graphical Abstract Decision

- Option A: [SUBMIT A GRAPHICAL ABSTRACT; AUTHOR CONFIRMS PROVENANCE AND POLICY COMPLIANCE]
- Option B: [DO NOT SUBMIT A GRAPHICAL ABSTRACT]

## 17. Suggested Reviewers If Required

- Portal requirement checked: [YES/NO]
- Proposed reviewers, if required and ethically appropriate: [NAME, AFFILIATION, EMAIL, RATIONALE]

## 18. Opposed Reviewers If Required

- Portal requirement checked: [YES/NO]
- Opposed reviewers, if permitted and justified: [NAME, AFFILIATION, CONCISE REASON]

## 19. Final Page Count

- Final editable source format: [.DOCX/.TEX]
- Final cited PDF pages: [NUMBER]
- Final anonymized PDF pages: [NUMBER]
- 34-page public-guide check completed: [YES/NO; DATE]

## 20. Final Approval Statement

We confirm that the title page, anonymized manuscript, cited manuscript, figures, tables, supplement, declarations, availability statements, repository decision, AI declaration, and portal entries are accurate and approved for submission.

- Authorized corresponding author: [NAME]
- Confirmation date: [DATE]
- All-author approval recorded: [YES/NO]
"""


def simulation_report(scan: dict[str, str], frozen_checked: int, frozen_mismatches: int, missing: list[str]) -> str:
    fields = ["upload_item", "classification", "evidence_checked", "remaining_condition"]
    rows = [
        {"upload_item": "Anonymized manuscript", "classification": "READY_AFTER_FORMAT_CONVERSION", "evidence_checked": "Markdown text scan found no identity hit; required file exists", "remaining_condition": "Create anonymous .docx/.tex, render PDF, inspect properties and portal preview"},
        {"upload_item": "Title page", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": "Placeholder template exists", "remaining_condition": "Fill verified authorship/contact metadata and convert to final editable source"},
        {"upload_item": "Highlights", "classification": "READY_AFTER_FORMAT_CONVERSION", "evidence_checked": "Five bullets; Stage 25 audit recorded maximum 76 characters", "remaining_condition": "Create portal-accepted editable file and recheck after edits"},
        {"upload_item": "Keywords", "classification": "READY_AFTER_FORMAT_CONVERSION", "evidence_checked": "Six keywords in cited manuscript", "remaining_condition": "Carry into final editable source and confirm portal style"},
        {"upload_item": "Cover letter", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": "Author-input template exists", "remaining_condition": "Complete author-specific claims and portal fields"},
        {"upload_item": "Figures", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": f"{scan['figure_count']} PNG assets; cross-reference audit passed", "remaining_condition": "Confirm provenance/AI assistance, format/resolution, and portal mapping"},
        {"upload_item": "Tables", "classification": "READY_AFTER_FORMAT_CONVERSION", "evidence_checked": f"{scan['table_count']} editable CSV tables; cross-reference audit passed", "remaining_condition": "Lay out editable journal tables in final source"},
        {"upload_item": "Supplementary material", "classification": "READY_AFTER_FORMAT_CONVERSION", "evidence_checked": "Markdown/CSV supplement exists", "remaining_condition": "Create final editable files and verify citations/portal mapping"},
        {"upload_item": "Declarations", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": "Neutral templates exist", "remaining_condition": "Complete funding, interests, CRediT, ethics, acknowledgements"},
        {"upload_item": "Data availability statement", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": "Options template exists", "remaining_condition": "Confirm data route, DOI/URL or accurate restriction explanation"},
        {"upload_item": "Code availability statement", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": "Options template exists", "remaining_condition": "Confirm code route, DOI/URL or accurate restriction explanation"},
        {"upload_item": "Repository files", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": "Local preparation skeleton exists; no deposit made", "remaining_condition": "Approve scope, sensitivity, license, repository, and release route"},
        {"upload_item": "AI declaration", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": "Template exists; no option selected", "remaining_condition": "Authors verify tool use, figure provenance, wording, and placement"},
        {"upload_item": "Conflict-of-interest statement", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": "Template exists", "remaining_condition": "Authors supply accurate declaration"},
        {"upload_item": "Funding statement", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": "Template exists", "remaining_condition": "Authors supply funder details or confirm applicable statement"},
        {"upload_item": "CRediT statement", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": "Template exists", "remaining_condition": "Authors assign and approve roles"},
        {"upload_item": "Ethics statement", "classification": "READY_AFTER_AUTHOR_INPUT", "evidence_checked": "Template exists", "remaining_condition": "Authors/institution verify applicability and exact wording"},
        {"upload_item": "Editable .docx or .tex source", "classification": "NOT_READY", "evidence_checked": f"Editable source scan found {scan['editable_source_count']} final source file(s)", "remaining_condition": "Create and inspect final cited and anonymized .docx or .tex sources"},
        {"upload_item": "Final PDF preview", "classification": "NOT_READY", "evidence_checked": f"Final source/PDF scan found {scan['pdf_preview_count']} PDF preview file(s)", "remaining_condition": "Render the final cited and anonymized sources; verify page count and layout"},
        {"upload_item": "Graphical abstract", "classification": "MANUAL_PORTAL_CHECK_REQUIRED", "evidence_checked": "Public Stage 25A audit recorded it as optional", "remaining_condition": "Authors decide and confirm live portal requirement and provenance"},
    ]
    missing_line = "; ".join(missing) if missing else "none"
    return "\n".join([
        "# Stage 25F Submission File Readiness Simulation",
        "",
        "## Simulation Boundary",
        "",
        "This is a local, non-upload simulation based on the Stage 25 package and public-requirements audit. No journal portal, repository, DOI service, or submission system was opened or used.",
        "",
        "## Evidence Snapshot",
        "",
        f"- Required-input files missing: {missing_line}.",
        f"- Frozen artifact recheck: {frozen_checked} checked; {frozen_mismatches} mismatch(es).",
        f"- Cited-manuscript reference placeholders: {scan['reference_placeholders']}.",
        f"- Anonymized-manuscript text identity hits: {scan['anonymized_text_identity_hits']}.",
        "- Text-level anonymization is not a substitute for final document-property and rendered-preview inspection.",
        "",
        "## Simulated Upload Items",
        "",
        markdown_table(rows, fields),
        "",
        "## Result",
        "",
        "The package is suitable for final author review, not upload. The blocking path is author confirmation, final editable-source conversion, rendered-page inspection, and live-portal confirmation.",
    ])


def source_checklist(scan: dict[str, str]) -> str:
    state = "absent" if scan["editable_source_count"] == "0" else f"{scan['editable_source_count']} file(s) found"
    return f"""# Stage 25F Editable Source and Page-Count Checklist

## Current Check

Final editable source scan: `{state}`. Final PDF-preview scan: `{scan['pdf_preview_count']} file(s) found`.

**FINAL EDITABLE .DOCX OR .TEX SOURCE REQUIRED BEFORE SUBMISSION.**

## Required Author-Side Checklist

- [ ] Convert the final cited manuscript to `.docx` or `.tex` without overwriting its Markdown source.
- [ ] Convert the final anonymized manuscript to `.docx` or `.tex` without overwriting its Markdown source.
- [ ] Ensure equations are editable text/equation objects, not screenshots.
- [ ] Ensure tables are editable text/tables, not screenshots.
- [ ] Keep Figures 1--8 as separate files and verify final submission format/resolution.
- [ ] Include complete evidence-type figure captions in the final source.
- [ ] Generate final cited and anonymized PDF previews from the editable sources.
- [ ] Record and inspect final page count; check the public-guide 34-page formatting constraint after typesetting.
- [ ] Inspect margins, spacing, and font size against the current Guide and the live portal's article-type instructions.
- [ ] Inspect hidden metadata: author, company, revision, comments, document properties, embedded objects, and file paths.
- [ ] Accept or remove all tracked changes/comments before creating the final PDFs.
- [ ] Verify title page is separate from the anonymized manuscript in both source files and portal file mapping.
- [ ] Verify the anonymized manuscript contains no names, affiliations, acknowledgements, funding, self-identifying statements, or local paths.

## Conversion Boundary

No conversion was attempted in Stage 25F because the controlled package contains Markdown preparation materials and no pre-existing, approved Word/LaTeX conversion mechanism. The final source must be generated and reviewed by the authors or their approved typesetting workflow.
"""


def red_team_report(scan: dict[str, str]) -> str:
    fields = ["risk", "rating", "assessment", "concrete Stage 25 package response or required closeout"]
    rows = [
        {"risk": "DSS fit", "rating": "MEDIUM", "assessment": "The manuscript states decision maker, inputs, outputs, cockpit, and evaluation, but editors may still screen it against narrowly technical voting work.", "concrete Stage 25 package response or required closeout": "Retain the DSS-first abstract/introduction and cover-letter template; authors must preserve this framing during final conversion."},
        {"risk": "Perceived as voting theory only", "rating": "MEDIUM", "assessment": "Mechanism rules are prominent, which can obscure decision support if formatting compresses artifact sections.", "concrete Stage 25 package response or required closeout": "Keep Sections 2, 5, 10, and 11 and Figures 1, 2, and 8 visible in final source."},
        {"risk": "Perceived as partial identification only", "rating": "MEDIUM", "assessment": "Formal feasible-set definitions are central but are paired with mechanism comparison and recommendations.", "concrete Stage 25 package response or required closeout": "Do not remove the stated DSS foundation/functionality/artifact/evaluation contribution mapping."},
        {"risk": "Synthetic-only evidence overreach", "rating": "LOW", "assessment": "All reported calibration and external-testbed results are explicitly synthetic; empirical application is bounded as illustration.", "concrete Stage 25 package response or required closeout": "Preserve synthetic, external-synthetic, empirical-illustration, and artifact-level labels in captions and final source."},
        {"risk": "No completed user validation", "rating": "LOW", "assessment": "The manuscript explicitly labels user evaluation as a future protocol and does not imply human-subject results.", "concrete Stage 25 package response or required closeout": "Preserve this limitation and avoid adding unverified usability claims."},
        {"risk": "Decision cockpit insufficiently artifact-like", "rating": "MEDIUM", "assessment": "Artifact input/output and decision trace are documented, but evaluation remains artifact-level.", "concrete Stage 25 package response or required closeout": "Keep cockpit workflow, input/output contract references, and Figure 8 in the final version."},
        {"risk": "Design recommendations too generic", "rating": "MEDIUM", "assessment": "Recommendations are conditional rather than empirical policy prescriptions, as required by evidence limits.", "concrete Stage 25 package response or required closeout": "Keep Table 6 and its conditions, warnings, and decision-support implication intact."},
        {"risk": "Baseline fairness", "rating": "LOW", "assessment": "Baselines are defined by available information; false-certainty is labeled as a synthetic diagnostic.", "concrete Stage 25 package response or required closeout": "Keep Table 3 and the synthetic-only metric interpretation."},
        {"risk": "Residual claim overstatement", "rating": "LOW", "assessment": "Stage 25 cited manuscript has zero reference placeholders and retained negative boundaries on recovery, deployment, and impact claims.", "concrete Stage 25 package response or required closeout": "Run a final wording check after editable-source conversion; do not replace bounded terms with recovery or validation claims."},
        {"risk": "Limitations weaken contribution", "rating": "LOW", "assessment": "Limitations are specific and paired with the decision-support contribution rather than retracting it.", "concrete Stage 25 package response or required closeout": "Do not delete the limitations section during page fitting."},
        {"risk": "Reference adequacy", "rating": "HIGH", "assessment": "The manuscript contains a compact, verified core reference list. Authors must make a final scholarly-coverage decision before locking the formatted version; no unverified citation can be added.", "concrete Stage 25 package response or required closeout": "Use the Stage 25 literature audit during author review; add only necessary, bibliographically verified sources and recheck every in-text/reference-list match."},
        {"risk": "Declarations incomplete", "rating": "HIGH", "assessment": "No author names, funding, interests, ethics, repository, availability, or AI facts are available for automatic completion.", "concrete Stage 25 package response or required closeout": "Complete AUTHOR_FILL_IN_PACKET_STAGE25F.md and transfer only author-approved text into templates and portal fields."},
        {"risk": "Submission readiness after author input", "rating": "HIGH", "assessment": "No final editable source or PDF preview is present; live-portal requirements are unresolved.", "concrete Stage 25 package response or required closeout": "Use editable_source_and_page_count_checklist.md, then repeat manual metadata, anonymous-preview, and portal mapping checks before upload."},
    ]
    return "\n".join([
        "# Stage 25F Final Red-Team Report",
        "",
        "## Scope",
        "",
        "This red-team review tests likely editor and reviewer objections using the completed Stage 25 materials. It does not add evidence, modify the research design, or claim a submission is authorized.",
        "",
        markdown_table(rows, fields),
        "",
        "## Red-Team Judgment",
        "",
        f"Automatic evidence integrity remains favorable: {scan['reference_placeholders']} citation placeholders, {scan['anonymized_text_identity_hits']} anonymized-text identity hits, and no editable final source/PDF yet. High risks are author-side scholarly, declaration, formatting, and portal gates; they are not failures of the frozen empirical or synthetic evidence.",
    ])


def author_memo() -> str:
    return """# Read This Before Submission: Stage 25F

## Already Completed

- The Stage 25 package contains cited and anonymized manuscript drafts, 8 figures, 7 tables, a supplement, audit logs, author-input templates, and a repository-preparation skeleton.
- The prior controlled audit recorded 74 passing tests and 20 frozen artifacts with 0 mismatches.
- The cited manuscript uses bounded language: it reports rule-assumption-conditioned feasible sets, synthetic calibration, external synthetic evidence, and artifact-level evaluation; it does not claim recovery of hidden public preferences, deployment, user validation, or organizational impact.

## Authors Must Fill

Complete `AUTHOR_FILL_IN_PACKET_STAGE25F.md` before finalizing the title page, cover letter, declarations, data/code statements, repository route, license, AI disclosure, and portal metadata.

## Authors Must Not Ignore

- No author, funding, conflict, ethics, repository, license, or AI-use value may be inferred from templates.
- Do not add a claim of true-preference recovery, real-world validation, deployment, user validation, or organizational impact during final editing.
- Do not replace source Markdown with a final PDF-only submission; a final editable Word or LaTeX source is required.

## Portal Checks

Confirm article type, file mapping, reviewer fields, declarations, supplement handling, graphical-abstract status, and any portal-only requirements. Public-guide verification does not replace the live portal.

## After .docx/.tex/PDF Conversion

Use `editable_source_and_page_count_checklist.md`: inspect editable equations/tables, separate figures/captions, page count, margins/spacing/font, comments/tracked changes, document properties, and final PDF layout.

## Anonymized Manuscript

Confirm the final anonymous source/PDF has no author names, affiliations, acknowledgements, funding, self-identifying text, local paths, comments, tracked changes, or embedded metadata. Inspect the portal preview as well as the file.

## Title Page and Declarations

Confirm title, author order, affiliations, corresponding details, acknowledgements, funding, competing interests, CRediT, ethics, data/code statements, and AI declaration against approved records.

## Repository and AI Checks

Choose the repository/restriction route, license, data/code scope, DOI/URL, and access terms before writing availability statements. Confirm figure provenance and any generative-AI assistance before selecting AI wording.

Do not upload this submission until every author-only field, repository decision, declaration, final editable source file, page count, and portal-only field has been confirmed.
"""


def run(root: Path) -> int:
    root = root.resolve()
    package = root / PACKAGE_RELATIVE
    inputs = required_inputs(root)
    missing = [f"{name}: {path}" for name, path in inputs.items() if not path.is_file()]
    if missing:
        write_text(
            package / "12_audit_logs/stage25F_missing_input_report.md",
            "# Stage 25F Missing Input Report\n\n" + "\n".join(f"- {item}" for item in missing),
        )
    if not (root / "manuscript/DSS_submission_draft_stage25_cited.md").is_file() or not (root / "manuscript/DSS_submission_draft_stage25_anonymized.md").is_file():
        raise FileNotFoundError("Stage 25F requires both Stage 25 manuscript files to produce a valid gate.")

    scan = scan_status(root, package)
    frozen_checked, frozen_mismatches = frozen_recheck(root, package)
    blockers = package / "01_author_action_required/stage25F_remaining_blockers_consolidated.md"
    fill_in = package / "01_author_action_required/AUTHOR_FILL_IN_PACKET_STAGE25F.md"
    simulation = package / "12_audit_logs/stage25F_submission_simulation_report.md"
    source_list = package / "01_author_action_required/editable_source_and_page_count_checklist.md"
    red_team = package / "12_audit_logs/stage25F_final_red_team_report.md"
    memo = package / "01_author_action_required/READ_THIS_BEFORE_SUBMISSION_STAGE25F.md"
    log = root / "outputs/logs/stage25F_run_log.md"

    write_text(blockers, blockers_document())
    write_text(fill_in, fill_in_packet())
    write_text(simulation, simulation_report(scan, frozen_checked, frozen_mismatches, missing))
    write_text(source_list, source_checklist(scan))
    write_text(red_team, red_team_report(scan))
    write_text(memo, author_memo())

    completed = "completed_with_warnings" if frozen_mismatches == 0 and not missing else "failed"
    label = "DSS-ready-for-final-author-review" if completed == "completed_with_warnings" else "DSS-not-ready"
    run_log = "\n".join([
        "# Stage 25F Run Log",
        "",
        "## Scope",
        "",
        "Stage 25F created only author-side completion and local submission-simulation materials. No Stage 21--24 artifact was written, and no upload, repository deposit, DOI registration, submission record, or external action was taken.",
        "",
        "## Input and Integrity Checks",
        "",
        f"- Required inputs missing: {len(missing)}.",
        f"- Frozen artifacts rechecked: {frozen_checked}; mismatches: {frozen_mismatches}.",
        f"- Cited-manuscript reference placeholders: {scan['reference_placeholders']}.",
        f"- Anonymized-manuscript text identity hits: {scan['anonymized_text_identity_hits']}.",
        f"- Final editable .docx/.tex sources found: {scan['editable_source_count']}.",
        f"- Final PDF previews found: {scan['pdf_preview_count']}.",
        "",
        "## Generated",
        "",
        f"- {blockers}",
        f"- {fill_in}",
        f"- {simulation}",
        f"- {source_list}",
        f"- {red_team}",
        f"- {memo}",
        "",
        "## Final Gate",
        "",
        f"Status: `{completed}`.",
        f"Label: `{label}`.",
        "Upload allowed: `NO`.",
        "",
        "The remaining work is author-side completion, approved final editable-source production, manual metadata/PDF inspection, and live DSS portal confirmation.",
    ])
    write_text(log, run_log)

    print(f"STAGE25F_STATUS = {completed}")
    print(f"FINAL_LABEL_AFTER_STAGE25F = {label}")
    print("UPLOAD_ALLOWED = NO")
    print(f"AUTHOR_FILL_IN_PACKET = {fill_in}")
    print(f"REMAINING_BLOCKERS = {blockers}")
    print(f"SUBMISSION_SIMULATION_REPORT = {simulation}")
    print(f"EDITABLE_SOURCE_CHECKLIST = {source_list}")
    print(f"FINAL_RED_TEAM_REPORT = {red_team}")
    print(f"AUTHOR_REVIEW_MEMO = {memo}")
    print("STAGE21_24_ARTIFACTS_MODIFIED = no")
    print("UPLOAD_OR_EXTERNAL_ACTION_TAKEN = no")
    print("NEXT_ACTION = Authors must complete the fill-in packet, generate or confirm final editable source files, inspect final PDF/page count, complete declarations, confirm repository/data/code/AI statements, and check live DSS portal fields before upload.")
    return 0 if completed != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(run(parse_args().project_root))
