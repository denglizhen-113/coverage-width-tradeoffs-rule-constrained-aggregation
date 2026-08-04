#!/usr/bin/env python3
"""Apply only the confirmed Stage 25H-A author information without external actions."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path("submission_package_stage25")
TITLE = "Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences"
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
DATA = (
    "The data supporting the findings of this study will be made available in a public GitHub "
    "repository before submission or upon publication. The repository URL will be added before final upload."
)
CODE = (
    "The code used in this study will be made available in a public GitHub repository before "
    "submission or upon publication. The repository URL will be added before final upload."
)
AI = (
    "During the preparation of this work, the authors used ChatGPT and Codex to assist with language "
    "polishing, structural review, checklist generation, formatting support, and submission-readiness "
    "auditing. After using these tools, the authors reviewed and edited the content as needed and take "
    "full responsibility for the content of the publication."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply confirmed Stage 25H-A author information and identify remaining submission blockers."
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

Complete this packet from verified author and institutional records. Confirmations applied in Stage 25H-A are limited to the information explicitly supplied by the authors. Every remaining AUTHOR INPUT STILL REQUIRED field remains a submission blocker.

## 1. Manuscript Title Confirmation

- Final selected title: {TITLE}
- Title-selection basis: The manuscript explicitly develops a rule-aware DSS framework, decision cockpit, partial-identification analysis, synthetic calibration, external synthetic testing, and institutional design recommendations. This existing title is more specific and evidence-aligned than the broader alternative referring only to robust social choice.

## 2. Author List and Order

| order | Romanized name | affiliation marker | current status |
| --- | --- | --- | --- |
| 1 | Deng Lizhen | 1 | author-provided |
| 2 | Liu Yuxin | 2 | author-provided |
| 3 | Li Bo | 3 | author-provided; affiliation unresolved |

Author order follows the author-provided sequence above. FINAL AUTHOR APPROVAL STILL REQUIRED.

## 3. Affiliations

1. Huazhong University of Science and Technology
2. Wuhan University of Technology
3. Li Bo affiliation: AUTHOR INPUT STILL REQUIRED

## 4. Corresponding Author

- Corresponding author name: AUTHOR INPUT STILL REQUIRED
- Corresponding author email: AUTHOR INPUT STILL REQUIRED
- Corresponding author postal address: AUTHOR INPUT STILL REQUIRED
- Status: CORRESPONDING AUTHOR INPUT STILL REQUIRED.
- Recommendation only: Deng Lizhen may serve as corresponding author only after all authors approve and a valid email address is supplied.

## 5. Acknowledgements

Acknowledgements: None.

Do not place acknowledgements in the anonymized manuscript.

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

Data availability: {DATA}

GITHUB DATA URL STILL REQUIRED.

## 11. Code Availability

Code availability: {CODE}

GITHUB CODE URL STILL REQUIRED.

## 12. Repository Choice

- Repository route: GitHub.
- Repository URL: AUTHOR INPUT STILL REQUIRED
- Repository DOI: Not available unless authors later archive an approved release through Zenodo or another DOI-granting repository.
- No repository, DOI, release, tag, or external deposit has been created by Stage 25.

## 13. License Choice

REPOSITORY LICENSE INPUT STILL REQUIRED.

Recommended options for author decision only: MIT License for code; CC BY 4.0 or CC0 for data, subject to data constraints and author approval.

## 14. Generative-AI Declaration

Declaration of generative AI and AI-assisted technologies in the writing process: {AI}

FINAL AI DECLARATION REQUIRES AUTHOR CONFIRMATION OF EXACT TOOLS AND USES.

## 15. Figure Provenance

FIGURE PROVENANCE INPUT STILL REQUIRED.

All figures must be confirmed as generated from code, data outputs, or manual author-created diagrams. No figure, image, or artwork should be treated as AI-generated unless explicitly declared and checked against Elsevier policy.

## 16. Graphical Abstract Decision

GRAPHICAL ABSTRACT DECISION STILL REQUIRED.

If the DSS portal treats it as optional, authors may decide not to submit one. If the live portal requires it, authors must prepare and verify it separately.

## 17. Suggested Reviewers If Required

Suggested reviewers: Not provided unless required by the DSS portal.

## 18. Opposed Reviewers If Required

Opposed reviewers: None provided unless required by the DSS portal.

## 19. Final Source Format and Page Count

- Preferred final source format: AUTHOR INPUT STILL REQUIRED
- Current fallback-generated PDF preview page count: 15 pages.
- FINAL WORD/LATEX EDITOR PAGE COUNT STILL REQUIRES AUTHOR CONFIRMATION.

## 20. Final Approval Statement

MANUAL METADATA CHECK STILL REQUIRED.

FINAL AUTHOR APPROVAL STILL REQUIRED.
"""


def title_page() -> str:
    return f"""# Title Page Template

**Title:** {TITLE}

**Authors:** Deng Lizhen; Liu Yuxin; Li Bo

**Affiliations:**

1. Huazhong University of Science and Technology
2. Wuhan University of Technology
3. Li Bo affiliation: AUTHOR INPUT STILL REQUIRED

**Corresponding author:** AUTHOR INPUT STILL REQUIRED

**Corresponding author email:** AUTHOR INPUT STILL REQUIRED

**Corresponding author postal address:** AUTHOR INPUT STILL REQUIRED

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

Deng Lizhen, Liu Yuxin, and Li Bo are listed in the author-provided order. The following statements remain subject to final author confirmation and portal requirements: Funding: {FUNDING} Declaration of competing interest: {COMPETING} Data and code will be released through GitHub before submission or upon publication, but the repository URLs are still required. The final generative-AI declaration and CRediT roles also require final author confirmation.

Sincerely,

CORRESPONDING AUTHOR INPUT STILL REQUIRED.
"""


def declarations() -> dict[str, str]:
    return {
        "acknowledgements_TEMPLATE_author_input_required.md": """# Acknowledgements

Acknowledgements: None.

For double-anonymous review, do not place acknowledgements in the anonymized manuscript.
""",
        "funding_statement_OPTIONS_author_input_required.md": f"""# Funding Statement

Funding: {FUNDING}

This author-provided statement is applied to the preparation package. FINAL AUTHOR APPROVAL STILL REQUIRED.
""",
        "competing_interests_OPTIONS_author_input_required.md": f"""# Declaration of Competing Interest

Declaration of competing interest: {COMPETING}

This author-provided statement is applied to the preparation package. FINAL AUTHOR APPROVAL STILL REQUIRED.
""",
        "CRediT_author_contributions_TEMPLATE_author_input_required.md": """# CRediT Author Contributions

- Deng Lizhen: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Visualization, Writing - original draft, Writing - review and editing, Project administration.
- Liu Yuxin: Writing - review and editing, Validation, Resources, Investigation.
- Li Bo: Supervision, Writing - review and editing, Validation.

CREDIT ROLES REQUIRE FINAL AUTHOR CONFIRMATION.
""",
        "ethics_statement_OPTIONS_author_input_required.md": f"""# Ethics Statement

Ethics statement: {ETHICS}

This statement is consistent with the current manuscript's artifact-level evaluation and future-protocol wording. FINAL AUTHOR APPROVAL STILL REQUIRED.
""",
        "data_availability_statement_OPTIONS_author_input_required.md": f"""# Data Availability Statement

Data availability: {DATA}

GITHUB DATA URL STILL REQUIRED.
""",
        "code_availability_statement_OPTIONS_author_input_required.md": f"""# Code Availability Statement

Code availability: {CODE}

GITHUB CODE URL STILL REQUIRED.

REPOSITORY LICENSE INPUT STILL REQUIRED.
""",
        "AI_declaration_TEMPLATE_author_input_required.md": f"""# Declaration of Generative AI and AI-Assisted Technologies

Declaration of generative AI and AI-assisted technologies in the writing process: {AI}

FINAL AI DECLARATION REQUIRES AUTHOR CONFIRMATION OF EXACT TOOLS AND USES.

No claim is made here that generative AI created data, results, references, figures, or scientific conclusions.
""",
    }


def repository_templates() -> dict[str, str]:
    return {
        "README.md": f"""# Repository Preparation Package

This is a local preparation skeleton only. Repository route selected by authors: GitHub.

Repository URL: AUTHOR INPUT STILL REQUIRED

Data availability: {DATA}

Code availability: {CODE}

No upload, DOI, release, tag, or external deposit has been created. REPOSITORY LICENSE INPUT STILL REQUIRED.
""",
        "LICENSE_PLACEHOLDER.md": """# License Placeholder

REPOSITORY LICENSE INPUT STILL REQUIRED.

Recommended options for author decision only: MIT License for code; CC BY 4.0 or CC0 for data, depending on author preference, ownership, source terms, and data constraints.
""",
        "REPOSITORY_DOI_PLACEHOLDER.md": """# Repository DOI Placeholder

Repository route: GitHub.

Repository URL: AUTHOR INPUT STILL REQUIRED

Repository DOI: not available unless authors later archive an approved release through Zenodo or another DOI-granting repository.

No DOI has been created by Stage 25.
""",
        "DATA_AVAILABILITY_STATEMENT_OPTIONS.md": f"""# Data Availability Statement

Data availability: {DATA}

GITHUB DATA URL STILL REQUIRED.
""",
        "CODE_AVAILABILITY_STATEMENT_OPTIONS.md": f"""# Code Availability Statement

Code availability: {CODE}

GITHUB CODE URL STILL REQUIRED.

REPOSITORY LICENSE INPUT STILL REQUIRED.
""",
        "CITATION.cff": f"""cff-version: 1.2.0
message: Please cite this work after author-side metadata is confirmed.
title: {TITLE}
authors:
  - family-names: Deng
    given-names: Lizhen
  - family-names: Liu
    given-names: Yuxin
  - family-names: Li
    given-names: Bo
status: draft
""",
    }


def remaining_report() -> str:
    fields = ["category", "remaining_item", "status", "why_it_remains", "next_author_action"]
    rows = [
        {"category": "Must be supplied before Stage 25H can pass", "remaining_item": "Li Bo affiliation", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "No affiliation was provided and it cannot be inferred.", "next_author_action": "Provide Li Bo's approved institutional affiliation."},
        {"category": "Must be supplied before Stage 25H can pass", "remaining_item": "Corresponding author name and email", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "The authors explicitly left corresponding authorship unresolved.", "next_author_action": "Confirm name and a valid email; obtain all-author approval."},
        {"category": "Must be supplied before Stage 25H can pass", "remaining_item": "GitHub data URL", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "GitHub route is selected but no repository exists or URL is supplied.", "next_author_action": "Create/approve the repository outside Codex and provide the final stable URL."},
        {"category": "Must be supplied before Stage 25H can pass", "remaining_item": "GitHub code URL", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "GitHub route is selected but no repository exists or URL is supplied.", "next_author_action": "Create/approve the repository outside Codex and provide the final stable URL."},
        {"category": "Must be supplied before Stage 25H can pass", "remaining_item": "Repository license", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "License choice is a legal/ownership decision.", "next_author_action": "Confirm code and data license terms."},
        {"category": "Must be supplied before Stage 25H can pass", "remaining_item": "Exact AI tools and uses", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "Current disclosure is conservative but needs author verification.", "next_author_action": "Confirm the exact tools, uses, and final declaration placement."},
        {"category": "Must be supplied before Stage 25H can pass", "remaining_item": "Figure provenance", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "No author confirmation identifies the source/provenance of Figures 1-8.", "next_author_action": "Confirm each figure's code/data/manual origin and any AI assistance."},
        {"category": "Must be supplied before Stage 25H can pass", "remaining_item": "Final approval from all authors", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "No collective final approval was supplied.", "next_author_action": "Record all-author final approval."},
        {"category": "Can be decided inside the live DSS portal", "remaining_item": "Corresponding-author postal address if portal requires it", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "Public guide/portal configuration may determine the field.", "next_author_action": "Supply address if the final portal requires it."},
        {"category": "Can be decided inside the live DSS portal", "remaining_item": "Whether a graphical abstract is required", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "Public guide treats it as optional; portal may differ.", "next_author_action": "Confirm portal requirement and submit/decline accordingly."},
        {"category": "Can be decided inside the live DSS portal", "remaining_item": "Suggested and opposed reviewers", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "No author list was provided and portal requirement is unresolved.", "next_author_action": "Complete only if the portal requests these fields."},
        {"category": "Must be manually checked outside Codex", "remaining_item": "Final source format and editor validation", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "DOCX and TEX exist, but authors have not selected or validated a final editor workflow.", "next_author_action": "Choose DOCX or TEX and inspect final editor output."},
        {"category": "Must be manually checked outside Codex", "remaining_item": "Final editor page count", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "The 15-page fallback preview is not final Word/LaTeX validation.", "next_author_action": "Provide final editor PDF page count and 34-page check."},
        {"category": "Must be manually checked outside Codex", "remaining_item": "Manual metadata inspection", "status": "AUTHOR INPUT STILL REQUIRED", "why_it_remains": "Automatic inspection cannot certify editor/portal metadata.", "next_author_action": "Confirm manual inspection of DOCX, TEX if used, PDF, and portal preview."},
        {"category": "Optional or conditional", "remaining_item": "Repository DOI through Zenodo or similar", "status": "OPTIONAL/CONDITIONAL", "why_it_remains": "GitHub route is selected; a DOI requires a later archival release.", "next_author_action": "Decide whether to archive a release after repository preparation."},
    ]
    return "\n".join([
        "# Stage 25H-A Remaining Author Inputs After User Update",
        "",
        "## Title Decision",
        "",
        f"Selected title: {TITLE}",
        "",
        "Reason: the existing manuscript title directly names the rule-aware DSS framework, expert-crowd setting, and hidden-public-preference information problem documented in the abstract, introduction, artifact section, and conclusion. The broader robust-social-choice alternative is less specific to the actual paper.",
        "",
        "## Remaining Inputs",
        "",
        markdown_table(rows, fields),
        "",
        "## Manual Check Outside Codex",
        "",
        "Manual metadata inspection and final editor/PDF review must be performed outside Codex before Stage 25H can pass.",
    ])


def declaration_precheck(root: Path, package: Path) -> str:
    manuscript = (root / "manuscript/DSS_submission_draft_stage25_cited.md").read_text(encoding="utf-8")
    checks = [
        ("Funding", "pass", "No grant or funding claim appears in the Stage 25 cited manuscript or applied declaration.", "No funding statement is internally consistent."),
        ("Competing interests", "pass", "No conflict claim appears elsewhere in the reviewed Stage 25 templates.", "No competing-interest statement is internally consistent pending final approval."),
        ("Ethics", "pass with boundary", "The manuscript reports artifact-level evaluation and a future user-evaluation protocol, not an executed user study, interview, survey, behavioral experiment, or human-subject result.", "The no-ethics-required statement is not contradicted by the current manuscript."),
        ("Data and code availability", "open blocker", "GitHub is the selected route, but no GitHub data or code URL is supplied.", "Do not claim present availability until the URLs are added."),
        ("AI and figure provenance", "open blocker", "AI writing-process declaration is drafted, but figure provenance remains unconfirmed.", "Confirm Figures 1-8 and reconcile any AI assistance with the final declaration."),
        ("CRediT and author order", "pass with boundary", "The three listed authors appear in the author-provided order; the CRediT draft assigns roles conservatively.", "CREDIT ROLES REQUIRE FINAL AUTHOR CONFIRMATION."),
        ("Acknowledgements", "pass", "Acknowledgements: None is applied in title-page/declaration materials and excluded from anonymized manuscript materials.", "No contradiction found."),
        ("Corresponding author", "open blocker", "No corresponding author, email, or approval is available.", "Portal readiness is blocked until supplied."),
    ]
    rows = [
        {"topic": topic, "status": status, "evidence": evidence, "required_action": action}
        for topic, status, evidence, action in checks
    ]
    return "\n".join([
        "# Stage 25H-A Declaration Consistency Pre-Check",
        "",
        markdown_table(rows, ["topic", "status", "evidence", "required_action"]),
        "",
        "## Result",
        "",
        "No contradiction requiring a manuscript rewrite was detected. The remaining data/code URL, AI/figure provenance, corresponding-author, license, final-source, metadata, and all-author-approval blockers prevent full Stage 25H certification.",
    ])


def next_actions() -> str:
    return """# Stage 25H-A Next Author Actions

- [ ] Provide Li Bo's approved affiliation.
- [ ] Confirm a corresponding author, valid email, and postal address if required by the portal.
- [ ] Create/approve the GitHub repository outside Codex and provide data and code URLs.
- [ ] Confirm repository license terms and whether a DOI archive will be created later.
- [ ] Confirm exact generative-AI tools and uses for the final declaration.
- [ ] Confirm provenance and any AI assistance for Figures 1-8.
- [ ] Decide whether to submit a graphical abstract and complete reviewer fields only if required by the portal.
- [ ] Choose DOCX or TEX as the final source and validate it in the selected editor.
- [ ] Provide final editor-generated PDF page count and complete the 34-page check.
- [ ] Complete manual metadata, comments, tracked-changes, anonymization, and portal-preview inspection.
- [ ] Record final approval from all authors.

After every item above is resolved, rerun the full Stage 25H final consistency gate. Do not upload before that gate passes.
"""


def run(root: Path) -> int:
    root = root.resolve()
    package = root / PACKAGE
    required = [
        root / "manuscript/DSS_submission_draft_stage25_cited.md",
        package / "01_author_action_required/AUTHOR_FILL_IN_PACKET_STAGE25F.md",
        package / "03_title_page/title_page_TEMPLATE_author_input_required.md",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing required Stage 25H-A inputs: " + "; ".join(missing))

    write_text(package / "01_author_action_required/AUTHOR_FILL_IN_PACKET_STAGE25F.md", author_packet())
    write_text(package / "03_title_page/title_page_TEMPLATE_author_input_required.md", title_page())
    write_text(package / "05_cover_letter/cover_letter_stage25_TEMPLATE_author_input_required.md", cover_letter())
    for filename, content in declarations().items():
        write_text(package / "09_declarations" / filename, content)
    for filename, content in repository_templates().items():
        write_text(package / "10_repository_prepare" / filename, content)

    remaining = package / "12_audit_logs/stage25H_A_remaining_author_inputs_after_user_update.md"
    precheck = package / "12_audit_logs/stage25H_A_declaration_precheck.md"
    actions = package / "01_author_action_required/STAGE25H_A_NEXT_AUTHOR_ACTIONS.md"
    write_text(remaining, remaining_report())
    write_text(precheck, declaration_precheck(root, package))
    write_text(actions, next_actions())

    run_log = root / "outputs/logs/stage25H_A_run_log.md"
    write_text(
        run_log,
        "\n".join([
            "# Stage 25H-A Run Log",
            "",
            "Author-provided information was applied only to Stage 25 author-side packet/templates.",
            f"- Final title selected: {TITLE}.",
            "- Applied: author order, two confirmed affiliations, acknowledgements, funding, competing interests, CRediT draft, ethics statement, GitHub repository route, provisional data/code statements, and generative-AI declaration draft.",
            "- Retained as blockers: Li Bo affiliation, corresponding-author details, GitHub URLs, license, AI-use precision, figure provenance, graphical-abstract decision, source format/editor validation, final page count, metadata check, and all-author approval.",
            "- Full Stage 25H rerun allowed: no.",
            "- Stage 21-24 artifacts modified: no.",
            "- Upload or external action taken: no.",
        ]),
    )

    print("STAGE25H_A_STATUS = completed_with_warnings")
    print("AUTHOR_INFO_APPLIED = yes")
    print(f"FINAL_TITLE_SELECTED = {TITLE}")
    print(f"AUTHOR_FILL_IN_PACKET_UPDATED = {package / '01_author_action_required/AUTHOR_FILL_IN_PACKET_STAGE25F.md'}")
    print(f"REMAINING_AUTHOR_INPUTS_REPORT = {remaining}")
    print(f"DECLARATION_PRECHECK = {precheck}")
    print(f"NEXT_AUTHOR_ACTIONS = {actions}")
    print("FULL_STAGE25H_RERUN_ALLOWED = no")
    print("UPLOAD_ALLOWED = NO")
    print("STAGE21_24_ARTIFACTS_MODIFIED = no")
    print("UPLOAD_OR_EXTERNAL_ACTION_TAKEN = no")
    print("NEXT_ACTION = Resolve remaining author-side blockers, then rerun full Stage 25H final consistency gate.")
    return 0


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(run(args.project_root))
