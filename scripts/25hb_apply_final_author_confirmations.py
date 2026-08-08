#!/usr/bin/env python3
"""Apply confirmed Stage 25H-B author information without uploading or depositing anything."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path("submission_package_stage25")
TITLE = "Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences"
CORRESPONDING_NAME = "Deng Lizhen"
CORRESPONDING_EMAIL = "3070116993@qq.com"
GITHUB_PROFILE_URL = "https://github.com/denglizhen-113"
FUNDING = (
    "This research received no specific grant from any funding agency in the public, "
    "commercial, or not-for-profit sectors."
)
COMPETING = (
    "The authors declare that they have no known competing financial interests or personal "
    "relationships that could have appeared to influence the work reported in this paper."
)
ETHICS = (
    "This study did not involve human participants, animals, clinical data, or personally "
    "identifiable information; therefore, ethics approval was not required."
)
AI = (
    "During the preparation of this work, the authors used ChatGPT and Codex for language polishing, "
    "readability review, manuscript consistency checking, and submission-readiness review. After using "
    "these tools, the authors reviewed and edited the content as needed and take full responsibility "
    "for the content of the publication."
)
FIGURE_PROVENANCE = (
    "The authors confirm that the figures were generated from code outputs, data outputs, or author-created "
    "diagrams, and were not created or altered using generative AI or AI-assisted image tools."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply Stage 25H-B confirmations and determine whether the full Stage 25H rerun is allowed."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
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


def verify_frozen_artifact_manifest(root: Path) -> int:
    """Fail before writing H-B outputs if a frozen Stage 21--24 artifact changed."""
    manifest = root / PACKAGE / "11_reproducibility/frozen_artifact_hash_manifest_stage25.csv"
    if not manifest.is_file():
        raise FileNotFoundError(f"Frozen-artifact manifest is missing: {manifest}")

    with manifest.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise ValueError(f"Frozen-artifact manifest has no entries: {manifest}")

    mismatches: list[str] = []
    for row in rows:
        relative_path = row.get("relative_path", "")
        expected = row.get("expected_sha256", "")
        target = root / relative_path
        if not relative_path or not expected or not target.is_file():
            mismatches.append(f"{relative_path or '<missing path>'}: missing or malformed manifest entry")
            continue
        observed = sha256(target)
        if observed != expected:
            mismatches.append(f"{relative_path}: expected {expected}, observed {observed}")

    if mismatches:
        raise RuntimeError(
            "Frozen Stage 21--24 artifact verification failed; no Stage 25H-B files were written. "
            + "; ".join(mismatches)
        )
    return len(rows)


def markdown_table(rows: list[dict[str, str]], fields: list[str]) -> str:
    header = "| " + " | ".join(fields) + " |"
    divider = "| " + " | ".join("---" for _ in fields) + " |"
    body = [
        "| " + " | ".join(str(row.get(field, "")).replace("|", "/") for field in fields) + " |"
        for row in rows
    ]
    return "\n".join([header, divider, *body])


def author_packet() -> str:
    return f"""# Stage 25F Author Fill-In Packet

This packet records the confirmations explicitly provided through Stage 25H-A and Stage 25H-B. Every field marked AUTHOR INPUT STILL REQUIRED remains a blocker; no repository, DOI, external deposit, or upload has been created.

## 1. Manuscript Title Confirmation

- Final selected title: {TITLE}
- Basis: the current manuscript explicitly centers a rule-aware DSS framework, decision cockpit, partial identification, synthetic evaluation, and institutional design recommendations.

## 2. Author List and Order

| order | Romanized name | affiliation marker | current status |
| --- | --- | --- | --- |
| 1 | Deng Lizhen | 1 | author-confirmed |
| 2 | Liu Yuxin | 2 | author-confirmed |
| 3 | Li Bo | 3 | author-confirmed |

Author order follows the author-provided sequence. FINAL AUTHOR APPROVAL STILL REQUIRED.

## 3. Affiliations

1. Huazhong University of Science and Technology
2. Wuhan University of Technology
3. Wuhan University of Technology

## 4. Corresponding Author

- Corresponding author: {CORRESPONDING_NAME}
- Email: {CORRESPONDING_EMAIL}
- Postal address: AUTHOR INPUT STILL REQUIRED IF THE DSS PORTAL REQUIRES A POSTAL ADDRESS.

## 5. Acknowledgements

Acknowledgements: None. Do not place acknowledgements in the anonymized manuscript.

## 6. Funding

Funding: {FUNDING}

## 7. Competing Interests

Declaration of competing interest: {COMPETING}

## 8. CRediT Author Contributions

- Deng Lizhen: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Visualization, Writing - original draft, Writing - review and editing, Project administration.
- Liu Yuxin: Writing - review and editing, Validation, Resources, Investigation.
- Li Bo: Supervision, Writing - review and editing, Validation.

CREDIT ROLES REQUIRE FINAL AUTHOR CONFIRMATION.

## 9. Ethics Statement

Ethics statement: {ETHICS}

## 10. Data Availability

Data availability: The data supporting the findings of this study will be made available in a public GitHub repository before submission or upon publication. The repository URL will be added before final upload.

GITHUB REPOSITORY URL STILL REQUIRED BEFORE FINAL UPLOAD.

## 11. Code Availability

Code availability: The code used in this study will be made available in the same public GitHub repository before submission or upon publication. The repository URL will be added before final upload.

GITHUB REPOSITORY URL STILL REQUIRED BEFORE FINAL UPLOAD.

## 12. Repository Choice

- Repository route: one public GitHub repository for data and code.
- Confirmed GitHub account profile: {GITHUB_PROFILE_URL}
- Preferred structure: code/, data/, docs/ or supplementary/, README.md, LICENSE or LICENSE-CODE, DATA_TERMS.md, CITATION.cff if available, and environment/requirements information.
- Publication repository URL: AUTHOR INPUT STILL REQUIRED. The confirmed account profile is not a repository URL.
- Repository DOI: Not available at initial submission. DOI may be generated later through Zenodo if the authors choose.

## 13. License Choice

- Code license plan: MIT License.
- Data terms: COMAP academic/research-purpose permission with attribution; see DATA_TERMS.md; no repository relicense.
- The MIT code-license file and DATA_TERMS.md must be present in the repository before final release.

## 14. Generative-AI Declaration

Declaration of generative AI and AI-assisted technologies in the writing process: {AI}

The declared scope excludes research data, experimental results, references, figures, scientific conclusions, and author-side facts.

## 15. Figure Provenance

AI-assisted figures/images/artwork: No.

Figure provenance statement: {FIGURE_PROVENANCE}

## 16. Graphical Abstract Decision

Graphical abstract: Not submitted unless required by the DSS portal.

GRAPHICAL ABSTRACT REQUIRED BY PORTAL - AUTHOR ACTION REQUIRED if the portal requires one.

## 17. Suggested Reviewers If Required

Suggested reviewers: Not provided unless required by the DSS portal.

## 18. Opposed Reviewers If Required

Opposed reviewers: None provided unless required by the DSS portal.

## 19. Final Source Format and Page Count

- Primary source format: DOCX.
- Secondary backup source format: TEX.
- PDF role: preview/checking file only; it is not a source file.
- Stage 25G fallback preview page count: 15 pages.
- Final DOCX-exported PDF page count: FINAL EDITOR VALIDATION REQUIRED.

## 20. Final Approval Statement

Manual metadata inspection: author reports that manual inspection has been performed and no problem is expected.

AUTHOR MANUAL METADATA CHECK REPORTED COMPLETE; AUTOMATED METADATA CHECK LIMITED.

FINAL AUTHOR APPROVAL STILL REQUIRED.
"""


def title_page() -> str:
    return f"""# Title Page Template

**Title:** {TITLE}

**Authors:** Deng Lizhen; Liu Yuxin; Li Bo

**Affiliations:**

1. Huazhong University of Science and Technology
2. Wuhan University of Technology
3. Wuhan University of Technology

**Corresponding author:** {CORRESPONDING_NAME}

**Corresponding author email:** {CORRESPONDING_EMAIL}

**Corresponding author postal address:** AUTHOR INPUT STILL REQUIRED IF THE DSS PORTAL REQUIRES A POSTAL ADDRESS.

**Acknowledgements:** None.

**Funding:** {FUNDING}

**Declaration of competing interest:** {COMPETING}

This title page is not part of the anonymized manuscript. CREDIT ROLES REQUIRE FINAL AUTHOR CONFIRMATION. FINAL AUTHOR APPROVAL STILL REQUIRED.
"""


def cover_letter() -> str:
    return f"""# Cover Letter Template: Decision Support Systems

Dear [EDITOR NAME IF KNOWN],

Please consider **{TITLE}** for publication in *Decision Support Systems*. The manuscript addresses enhanced decision making for institutional designers who must compare aggregation, expert-discretion, tie-handling, and disclosure rules while public preferences remain hidden. Its rule-aware partial-identification framework produces feasible sets conditioned on observed outcomes and documented rules, while a decision cockpit translates uncertainty into conditional design recommendations and accountability warnings.

The evaluation package combines fixed-seed synthetic calibration, an external synthetic testbed, baseline comparison, robustness analysis, and artifact-level evaluation. The manuscript does not claim recovery of hidden public preferences, real deployment, completed user validation, or measured organizational impact. It includes a future user-evaluation protocol only.

Deng Lizhen, Liu Yuxin, and Li Bo are listed in author-provided order. The corresponding author is currently {CORRESPONDING_NAME} ({CORRESPONDING_EMAIL}). Funding: {FUNDING} Declaration of competing interest: {COMPETING} Data and code will be released through one public GitHub repository, but the repository URL remains required before final upload. GITHUB REPOSITORY URL STILL REQUIRED BEFORE FINAL UPLOAD. The AI declaration and figure provenance are recorded in the attached declaration templates. CREDIT ROLES REQUIRE FINAL AUTHOR CONFIRMATION. FINAL AUTHOR APPROVAL STILL REQUIRED.

Sincerely,

{CORRESPONDING_NAME}
{CORRESPONDING_EMAIL}
"""


def declaration_templates() -> dict[str, str]:
    return {
        "AI_declaration_TEMPLATE_author_input_required.md": f"""# Declaration of Generative AI and AI-Assisted Technologies

Declaration of generative AI and AI-assisted technologies in the writing process: {AI}

The declared scope excludes research data, experimental results, references, figures, scientific conclusions, and author-side facts.
""",
        "data_availability_statement_OPTIONS_author_input_required.md": """# Data Availability Statement

Data availability: The data supporting the findings of this study will be made available in a public GitHub repository before submission or upon publication. The repository URL will be added before final upload.

GITHUB REPOSITORY URL STILL REQUIRED BEFORE FINAL UPLOAD.

Data terms: COMAP academic/research-purpose permission with attribution; see DATA_TERMS.md; no repository relicense.
""",
        "code_availability_statement_OPTIONS_author_input_required.md": """# Code Availability Statement

Code availability: The code used in this study will be made available in a public GitHub repository before submission or upon publication. The repository URL will be added before final upload.

GITHUB REPOSITORY URL STILL REQUIRED BEFORE FINAL UPLOAD.

Code license plan: MIT License.
""",
        "CRediT_author_contributions_TEMPLATE_author_input_required.md": """# CRediT Author Contributions

- Deng Lizhen: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Visualization, Writing - original draft, Writing - review and editing, Project administration.
- Liu Yuxin: Writing - review and editing, Validation, Resources, Investigation.
- Li Bo: Supervision, Writing - review and editing, Validation.

CREDIT ROLES REQUIRE FINAL AUTHOR CONFIRMATION.
""",
        "figure_provenance_statement_author_confirmed.md": f"""# Figure Provenance Statement

AI-assisted figures/images/artwork: No.

{FIGURE_PROVENANCE}

This statement applies to Figures 1-8 in the Stage 25 package. If a later source-file review contradicts it, stop and flag FIGURE PROVENANCE CONTRADICTION - AUTHOR REVIEW REQUIRED.
""",
    }


def repository_templates() -> dict[str, str]:
    return {
        "README.md": f"""# Repository Preparation Package

Repository route: one public GitHub repository for data and code.

Confirmed GitHub account profile: {GITHUB_PROFILE_URL}

Required repository structure: code/, data/, docs/ or supplementary/, README.md, LICENSE or LICENSE-CODE, DATA_TERMS.md, CITATION.cff if available, and environment/requirements information.

Publication repository URL: AUTHOR INPUT STILL REQUIRED. The confirmed account profile is not a repository URL.

No repository, DOI, release, tag, or external deposit has been created by Stage 25.

Code license plan: MIT License. Data terms: COMAP academic/research-purpose permission with attribution; no repository relicense.
""",
        "LICENSE_PLACEHOLDER.md": """# License Plan

Code license plan: MIT License.

Data terms: COMAP academic/research-purpose permission with attribution; see DATA_TERMS.md; no repository relicense.

The MIT code-license file, DATA_TERMS.md, and any required third-party/source-data notices must be present in the GitHub repository before release. This local preparation package does not create a license grant for third-party data.
""",
        "LICENSE_FILES_AUTHOR_ACTION_REQUIRED.md": """# Repository License Files: Author Action Required

- [ ] Add the official MIT License text as LICENSE or LICENSE-CODE for code.
- [ ] Add DATA_TERMS.md with the verified COMAP permission, attribution, official source URLs, and checksum.
- [ ] Confirm ownership, source-data terms, and third-party dependencies before release.
- [ ] Confirm that redistribution of source data remains within the COMAP academic/research-purpose terms recorded in DATA_TERMS.md.
""",
        "REPOSITORY_DOI_PLACEHOLDER.md": f"""# Repository URL and DOI Status

Repository route: GitHub.

Confirmed GitHub account profile: {GITHUB_PROFILE_URL}

Publication repository URL: AUTHOR INPUT STILL REQUIRED. The confirmed account profile is not a repository URL.

Repository DOI: Not available at initial submission. DOI may be generated later through Zenodo or another DOI-granting repository if authors archive an approved release.

No DOI has been created by Stage 25.
""",
        "DATA_AVAILABILITY_STATEMENT_OPTIONS.md": """# Data Availability Statement

Data availability: The data supporting the findings of this study will be made available in a public GitHub repository before submission or upon publication. The repository URL will be added before final upload.

GITHUB REPOSITORY URL STILL REQUIRED BEFORE FINAL UPLOAD.

Data terms: COMAP academic/research-purpose permission with attribution; see DATA_TERMS.md; no repository relicense.
""",
        "CODE_AVAILABILITY_STATEMENT_OPTIONS.md": """# Code Availability Statement

Code availability: The code used in this study will be made available in a public GitHub repository before submission or upon publication. The repository URL will be added before final upload.

GITHUB REPOSITORY URL STILL REQUIRED BEFORE FINAL UPLOAD.

Code license plan: MIT License.
""",
    }


def remaining_blockers_report() -> str:
    fields = ["classification", "item", "status", "evidence_or_condition", "next_action"]
    rows = [
        {"classification": "Resolved by this update", "item": "Corresponding author name", "status": "resolved", "evidence_or_condition": f"{CORRESPONDING_NAME} is confirmed as corresponding author.", "next_action": "Use on title page and cover letter."},
        {"classification": "Resolved by this update", "item": "Corresponding author email", "status": "resolved", "evidence_or_condition": CORRESPONDING_EMAIL, "next_action": "Use on title page and cover letter."},
        {"classification": "Resolved by this update", "item": "Li Bo affiliation", "status": "resolved", "evidence_or_condition": "Wuhan University of Technology.", "next_action": "Use on title page."},
        {"classification": "Resolved by this update", "item": "Repository terms", "status": "resolved plan", "evidence_or_condition": "MIT License for code; COMAP academic/research-purpose permission and attribution for source data; no data relicense.", "next_action": "Preserve LICENSE and DATA_TERMS.md in the repository."},
        {"classification": "Resolved by this update", "item": "AI declaration", "status": "resolved declaration scope", "evidence_or_condition": "ChatGPT/Codex for language, readability, consistency, and submission-readiness review only.", "next_action": "Keep final wording consistent."},
        {"classification": "Resolved by this update", "item": "Figure provenance", "status": "confirmed", "evidence_or_condition": "Author confirms code/data/author-created figures with no generative-AI image assistance.", "next_action": "Stop if a later source review contradicts this statement."},
        {"classification": "Resolved by this update", "item": "Primary source format", "status": "resolved", "evidence_or_condition": "DOCX primary; TEX backup; PDF preview only.", "next_action": "Use DOCX for final source preparation."},
        {"classification": "Still required before full Stage 25H can pass", "item": "GitHub repository URL and final availability", "status": "AUTHOR INPUT STILL REQUIRED", "evidence_or_condition": f"GitHub account profile {GITHUB_PROFILE_URL} is confirmed, but it is not a repository URL and no repository is created.", "next_action": "Provide final public repository URL after author-controlled creation."},
        {"classification": "Still required before full Stage 25H can pass", "item": "Final editor-validated PDF page count", "status": "FINAL EDITOR VALIDATION REQUIRED", "evidence_or_condition": "Fallback preview is 15 pages but not a DOCX-editor validation.", "next_action": "Create final DOCX-exported PDF and provide its page count."},
        {"classification": "Still required before full Stage 25H can pass", "item": "CRediT final confirmation", "status": "AUTHOR INPUT STILL REQUIRED", "evidence_or_condition": "The roles remain a conservative draft.", "next_action": "Obtain all-author confirmation of named roles."},
        {"classification": "Still required before full Stage 25H can pass", "item": "Final approval from all authors", "status": "AUTHOR INPUT STILL REQUIRED", "evidence_or_condition": "No explicit all-author final approval was provided.", "next_action": "Record final approval."},
        {"classification": "Portal-only or conditional", "item": "Corresponding-author postal address", "status": "AUTHOR INPUT STILL REQUIRED IF PORTAL REQUIRES", "evidence_or_condition": "No postal address supplied.", "next_action": "Provide only if the live portal requires it."},
        {"classification": "Portal-only or conditional", "item": "Graphical abstract", "status": "not submitted unless required", "evidence_or_condition": "No firm author decision; public guide previously recorded it as optional.", "next_action": "Act only if the portal requires one."},
        {"classification": "Portal-only or conditional", "item": "Final live DSS portal field check", "status": "required", "evidence_or_condition": "Article type, file mapping, reviewer fields, and portal configuration require live review.", "next_action": "Complete after full Stage 25H passes."},
        {"classification": "Manual author check already reported but should be logged", "item": "Metadata inspection", "status": "reported complete; automated check limited", "evidence_or_condition": "Author reports manual inspection performed and no problem expected.", "next_action": "Log again during full Stage 25H and inspect final portal preview."},
    ]
    return "\n".join([
        "# Stage 25H-B Remaining Blockers After Final Author Update",
        "",
        markdown_table(rows, fields),
        "",
        "## Result",
        "",
        "Multiple author-side requirements remain: final GitHub URL, final editor-validated page count, CRediT confirmation, and final all-author approval. Full Stage 25H rerun is not yet allowed.",
    ])


def source_format_memo() -> str:
    return """# Stage 25H-B Source Format and Page Count Decision

## Primary Source Format

Primary source format: DOCX.

The Stage 25 public-requirements audit records that an editable Word or LaTeX source is required and that PDF is not acceptable as the sole source. DOCX is selected as the primary working source because the Stage 25 package already contains an editable cited and anonymized DOCX workflow. No local public-guide evidence establishes TEX as preferable for this submission.

## Backup and PDF Roles

- Secondary backup source format: TEX.
- PDF: preview/checking file only, not a source file.

## Page Count

- Stage 25G fallback-generated PDF preview page count: 15 pages.
- Final editor-validated DOCX PDF page count: FINAL EDITOR VALIDATION REQUIRED.

The fallback preview is not a substitute for the page count of the final DOCX exported by the author-selected editor. Before full Stage 25H can pass, authors must export the final DOCX to PDF, inspect the result, record its page count, and complete the public-guide page-limit check.
"""


def declaration_check() -> str:
    fields = ["topic", "status", "consistency finding", "remaining action"]
    rows = [
        {"topic": "Title page and author packet", "status": "pass with approval boundary", "consistency finding": "Deng Lizhen, Liu Yuxin, and Li Bo appear in the same order; all affiliations are supplied.", "remaining action": "Final author approval still required."},
        {"topic": "Corresponding author", "status": "pass with portal boundary", "consistency finding": f"{CORRESPONDING_NAME} and {CORRESPONDING_EMAIL} align across title page, packet, and cover letter.", "remaining action": "Postal address only if portal requires it."},
        {"topic": "Funding and competing interests", "status": "pass", "consistency finding": "No-funding and no-competing-interest statements align across updated templates.", "remaining action": "Retain final author approval."},
        {"topic": "Ethics", "status": "pass with boundary", "consistency finding": "No-ethics-required statement remains consistent with artifact-level evaluation and a future protocol, not an executed human study.", "remaining action": "Do not add a user-study claim without revisiting ethics."},
        {"topic": "Data/code and repository", "status": "open blocker", "consistency finding": f"GitHub route, account profile {GITHUB_PROFILE_URL}, MIT code licensing, and COMAP source-data terms align, but the publication repository URL is absent.", "remaining action": "Provide final public repository URL before upload."},
        {"topic": "AI declaration and figures", "status": "pass with provenance check", "consistency finding": "Declared ChatGPT/Codex writing-process scope excludes figures; author confirms no generative-AI figure assistance.", "remaining action": "Stop if a later source review finds a contradiction."},
        {"topic": "CRediT", "status": "open blocker", "consistency finding": "Named role draft aligns with author order.", "remaining action": "CREDIT ROLES REQUIRE FINAL AUTHOR CONFIRMATION."},
        {"topic": "Manuscript declarations", "status": "pass with separation boundary", "consistency finding": "Author-specific declarations remain outside the anonymized manuscript.", "remaining action": "Keep title page and anonymous review file separated."},
    ]
    return "\n".join([
        "# Stage 25H-B Declaration Consistency Check",
        "",
        markdown_table(rows, fields),
        "",
        "No contradiction requiring a substantive manuscript rewrite was found. Remaining blockers are limited to final author/repository/editor confirmations.",
    ])


def rerun_decision() -> str:
    return f"""# Stage 25H-B Rerun Decision

## Label

FULL_STAGE25H_RERUN_NOT_ALLOWED_AUTHOR_INPUT_MISSING

## Reason

Although this update resolves correspondence, Li Bo affiliation, license planning, AI declaration scope, figure provenance, primary source format, and the GitHub account profile ({GITHUB_PROFILE_URL}), multiple required confirmations remain unavailable:

- final public GitHub repository URL (the confirmed account profile is not a repository URL);
- final DOCX-editor-validated PDF page count;
- final CRediT author-role confirmation; and
- final approval from all authors.

GITHUB REPOSITORY URL STILL REQUIRED BEFORE FINAL UPLOAD.

The author reports manual metadata inspection as complete, but automated metadata inspection remains limited and must be logged again when the final source/PDF is available. No upload is authorized.
"""


def run(root: Path) -> int:
    root = root.resolve()
    package = root / PACKAGE
    required = [
        root / "manuscript/DSS_submission_draft_stage25_cited.md",
        package / "01_author_action_required/AUTHOR_FILL_IN_PACKET_STAGE25F.md",
        package / "12_audit_logs/stage25_DSS_official_requirements_verified.md",
        package / "11_reproducibility/frozen_artifact_hash_manifest_stage25.csv",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing required Stage 25H-B inputs: " + "; ".join(missing))

    frozen_verified = verify_frozen_artifact_manifest(root)

    write_text(package / "01_author_action_required/AUTHOR_FILL_IN_PACKET_STAGE25F.md", author_packet())
    write_text(package / "03_title_page/title_page_TEMPLATE_author_input_required.md", title_page())
    write_text(package / "05_cover_letter/cover_letter_stage25_TEMPLATE_author_input_required.md", cover_letter())
    for filename, content in declaration_templates().items():
        write_text(package / "09_declarations" / filename, content)
    for filename, content in repository_templates().items():
        write_text(package / "10_repository_prepare" / filename, content)

    blockers = package / "12_audit_logs/stage25H_B_remaining_blockers_after_final_author_update.md"
    source_memo = package / "12_audit_logs/stage25H_B_source_format_and_page_count_decision.md"
    declaration = package / "12_audit_logs/stage25H_B_declaration_consistency_check.md"
    decision = package / "01_author_action_required/STAGE25H_B_RERUN_DECISION.md"
    write_text(blockers, remaining_blockers_report())
    write_text(source_memo, source_format_memo())
    write_text(declaration, declaration_check())
    write_text(decision, rerun_decision())

    run_log = root / "outputs/logs/stage25H_B_run_log.md"
    write_text(
        run_log,
        "\n".join([
            "# Stage 25H-B Run Log",
            "",
            "Stage 25H-B applied only confirmed author-side information to Stage 25 templates.",
            "- Corresponding author: Deng Lizhen; email: 3070116993@qq.com.",
            "- Li Bo affiliation: Wuhan University of Technology.",
            f"- Confirmed GitHub account profile: {GITHUB_PROFILE_URL}; publication repository URL remains required.",
            "- Repository terms: MIT for code; COMAP academic/research-purpose permission with attribution for source data; no data relicense.",
            "- AI declaration and figure provenance confirmation updated.",
            "- Primary source: DOCX; TEX backup; PDF preview only.",
            "- Fallback preview page count: 15; final editor validation still required.",
            "- Full Stage 25H rerun allowed: no.",
            f"- Frozen Stage 21-24 artifact verification: {frozen_verified}/{frozen_verified} SHA-256 entries matched.",
            "- Stage 21-24 artifacts modified: no.",
            "- Upload or external action taken: no.",
        ]),
    )

    print("STAGE25H_B_STATUS = completed_with_warnings")
    print("AUTHOR_INFO_APPLIED = yes")
    print("CORRESPONDING_AUTHOR_CONFIRMED = yes")
    print("LI_BO_AFFILIATION_CONFIRMED = yes")
    print("LICENSE_PLAN_CONFIRMED = yes")
    print("AI_DECLARATION_UPDATED = yes")
    print("FIGURE_PROVENANCE_STATUS = confirmed")
    print("PRIMARY_SOURCE_FORMAT = DOCX")
    print("PDF_ROLE = preview_only")
    print("FALLBACK_PREVIEW_PAGE_COUNT = 15")
    print("FINAL_EDITOR_VALIDATED_PAGE_COUNT = FINAL EDITOR VALIDATION REQUIRED")
    print("GITHUB_REPOSITORY_URL_STATUS = still_required")
    print("FINAL_AUTHOR_APPROVAL_STATUS = still_required")
    print("RERUN_DECISION = FULL_STAGE25H_RERUN_NOT_ALLOWED_AUTHOR_INPUT_MISSING")
    print("UPLOAD_ALLOWED = NO")
    print("STAGE21_24_ARTIFACTS_MODIFIED = no")
    print("UPLOAD_OR_EXTERNAL_ACTION_TAKEN = no")
    print("NEXT_ACTION = If GitHub URL, final editor-validated page count, final metadata check, and author approval are confirmed, rerun full Stage 25H; otherwise resolve the remaining listed blockers first.")
    return 0


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(run(args.project_root))
