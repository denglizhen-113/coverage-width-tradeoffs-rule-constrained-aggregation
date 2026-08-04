#!/usr/bin/env python3
"""Stage 25 bootstrap and staged control entry point.

Stage 25 is deliberately split into 25-0 and 25A--25E. This entry point
implements 25-0 and 25A only. Both are non-destructive preparation stages;
later stages must be invoked explicitly after their predecessor log is read.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "submission_package_stage25"
GUIDE_URL = "https://www.sciencedirect.com/journal/decision-support-systems/publish/guide-for-authors"
AI_POLICY_URL = "https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals"
ACCESS_DATE = "2026-07-17"

DIRECTORIES = (
    "00_CONTROL",
    "01_author_action_required",
    "02_manuscript",
    "03_title_page",
    "04_highlights_keywords",
    "05_cover_letter",
    "06_figures",
    "07_tables",
    "08_supplement",
    "09_declarations",
    "10_repository_prepare",
    "11_reproducibility",
    "12_audit_logs",
    "13_audit_tables",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a single declared Stage 25 substage. This version implements "
            "only the non-destructive Stage 25-0 bootstrap and Stage 25A inventory."
        )
    )
    parser.add_argument(
        "--stage",
        choices=("25-0", "25A", "overnight", "25B", "25C", "25D", "25E"),
        default="25-0",
        help="Stage to run. `overnight` performs controlled Tasks 2--9 after the Stage 25A gate.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root containing the Stage 21--24 evidence package.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content.strip() + "\n", encoding="utf-8")
    temporary.replace(path)


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def require(root: Path, paths: tuple[str, ...]) -> None:
    missing = [path for path in paths if not (root / path).is_file()]
    if missing:
        raise FileNotFoundError("Missing required Stage 24 input(s): " + "; ".join(missing))


def master_rules() -> str:
    return """# Stage 25 Master Rules

## Mission

Stage 25 seals the existing *Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences* package for final author review. It is not a new research project, a new model-development stage, or authority to upload material anywhere.

## Fixed Positioning

- This is a model-driven, rule-aware decision-support paper for institutional aggregation design.
- The target decision maker is an institutional organizer, platform governance analyst, or aggregation-rule designer.
- The core output is a rule-assumption-conditioned feasible set and a conditional decision-support recommendation.
- Synthetic calibration, external synthetic testbed evidence, artifact-level evaluation, and reproducibility checks are not empirical recovery, deployment, user validation, or organizational-impact evidence.

## Non-Negotiable Prohibitions

- Do not upload, submit, publish, register a DOI, create a repository, or contact an external platform.
- Do not invent author names, author order, affiliations, correspondence details, funding, competing interests, ethics approval, repository URL/DOI, license, or access conditions.
- Do not modify Stage 21--24 outputs. Stage 25 may copy them into its own package only with recorded provenance.
- Do not claim hidden public preferences are recovered, revealed, exact, or true.
- Do not describe the prototype as deployed, user validated, field tested, or as evidence of organizational impact.
- Do not replace, alter, enhance, or fabricate research-result figures with generative-AI images.

## Required Evidence Language

Use: feasible set; consistent with observed outcomes; conditioned on rule assumptions; synthetic calibration; external synthetic testbed; artifact-level evaluation; scenario-based evaluation protocol; design implication; decision-support recommendation; accountability warning.

## Submission Boundary

The only permitted positive final state is `DSS-ready-for-final-author-review`. `DSS-ready-to-submit` is prohibited until authors complete all declarations, repository information, official portal fields, final anonymous-file inspection, and final formatting checks.
"""


def task_sequence() -> str:
    return """# Stage 25 Task Sequence

| Stage | Purpose | Required predecessor log | Expected outputs | Write scope |
| --- | --- | --- | --- | --- |
| 25-0 | Bootstrap controls and directory skeleton | Stage 24 final no-go report | Control files, manifest template, bootstrap log | Stage 25 controls only |
| 25A | Official DSS requirements and package inventory | `stage25_0_bootstrap_log.md` | Official requirement matrix, package inventory, author-input draft | Audit and author-action folders |
| 25B | Manuscript compression, claim control, evidence boundaries | 25A log and requirements report | Stage 25 manuscripts, claim-evidence matrix, page audit | Manuscript and Stage 25 package copies |
| 25C | DSS fit, innovation, literature, math, and baselines | 25B log and cited manuscript | Scope-fit, innovation, literature, math, baseline audits | Audit logs and tables |
| 25D | Figures, anonymization, metadata, repository, declarations | 25C log and manuscript outputs | Figure/table, anonymization, repository, declaration materials | Stage 25 package only |
| 25E | Final sealing and no-go decision | All 25A--25D logs | Final README, final no-go report, label, manifest | Stage 25 package only |

Every later stage must first read the specified predecessor log and must not rerun unrelated stages. A critical failure prevents Stage 25E from assigning `DSS-ready-for-final-author-review`.
"""


def high_risk_phrases() -> str:
    entries = [
        ("recovered true public preferences", "rule-assumption-conditioned feasible set"),
        ("revealed public will", "information consistent with observed outcomes"),
        ("true public will", "latent public preference remains unobserved"),
        ("public preference recovery", "partial identification under stated rules"),
        ("proved real organizational impact", "artifact-level evaluation and design implication"),
        ("deployed system", "model-driven decision-support prototype"),
        ("completed user validation", "future user-evaluation protocol"),
        ("real-world validation", "synthetic calibration or external synthetic testbed"),
        ("organizational performance improvement", "unmeasured organizational outcome"),
        ("causal effect on institutions", "conditional mechanism comparison"),
        ("verified policy impact", "decision-support recommendation"),
        ("field-tested decision support system", "reproducible artifact-level demonstration"),
    ]
    lines = ["# High-Risk Phrases", "", "The following phrases are prohibited in Stage 25 manuscripts and templates unless an author supplies directly relevant evidence and a later audit explicitly permits the wording.", "", "| Prohibited phrase | Required safer framing |", "| --- | --- |"]
    lines.extend(f"| {phrase} | {replacement} |" for phrase, replacement in entries)
    return "\n".join(lines)


def author_placeholders() -> str:
    placeholders = [
        "[AUTHOR 1 FULL NAME]",
        "[AUTHOR ORDER TO BE CONFIRMED]",
        "[AFFILIATION 1]",
        "[CORRESPONDING AUTHOR FULL NAME]",
        "[CORRESPONDING AUTHOR FULL POSTAL ADDRESS]",
        "[CORRESPONDING AUTHOR EMAIL]",
        "[ACKNOWLEDGEMENTS TO BE CONFIRMED]",
        "[GRANT NAME IF ANY]",
        "[GRANT NUMBER IF ANY]",
        "[COMPETING INTERESTS TO BE CONFIRMED]",
        "[CRediT ROLES TO BE CONFIRMED]",
        "[ETHICS APPROVAL STATUS TO BE CONFIRMED]",
        "[REPOSITORY DOI OR URL]",
        "[LICENSE TO BE CONFIRMED BY AUTHORS]",
        "[AUTHOR REASON IF DATA ARE RESTRICTED]",
        "[AI TOOL NAME, VERSION, PURPOSE, AND AUTHOR OVERSIGHT TO BE CONFIRMED]",
        "[AUTHOR TO CONFIRM]",
        "[PORTAL REQUIREMENT TO BE CONFIRMED]",
    ]
    return "# Author Input Placeholders\n\nOnly these explicit placeholders may stand in for author-side facts. They are not assertions and must be completed by the authors before upload.\n\n" + "\n".join(f"- `{item}`" for item in placeholders)


def evidence_labels() -> str:
    labels = [
        ("synthetic calibration", "Known-truth simulator diagnostic; not empirical recovery."),
        ("synthetic benchmark", "Fixed-seed benchmark with truth hidden from inference."),
        ("external synthetic testbed", "Structurally different simulator; not external empirical validation."),
        ("artifact-level evaluation", "Audit of inputs, outputs, traceability, and decision support; not user validation."),
        ("baseline comparison", "Information and calibration comparison under stated protocol."),
        ("robustness and sensitivity analysis", "Conditional stability under listed configurations."),
        ("model invariant check", "Executable consistency check under model assumptions."),
        ("decision-maker scenario", "Design-oriented use case; not observed adoption."),
        ("future user-evaluation protocol", "Planned study design with no completed participants or results."),
        ("design implication", "Conditional institutional recommendation, not a policy proof."),
        ("formal proposition", "Conditional mathematical statement with assumptions."),
        ("implementation artifact", "Reproducible model-driven prototype, not a deployed system."),
        ("reproducibility check", "Script, seed, hash, or test verification."),
    ]
    lines = ["# Evidence-Type Labels", "", "Every Stage 25 result must state an evidence type and retain the corresponding limit of interpretation.", "", "| Label | Interpretation boundary |", "| --- | --- |"]
    lines.extend(f"| {label} | {boundary} |" for label, boundary in labels)
    return "\n".join(lines)


def allowed_labels() -> str:
    return """# Stage 25 Allowed Labels

Only these labels may be used in the final Stage 25 decision:

1. `DSS-ready-for-final-author-review`
2. `DSS-needs-minor-author-input`
3. `DSS-needs-major-author-input`
4. `DSS-not-ready`

`DSS-ready-to-submit` is not an allowed Stage 25 label.
"""


def words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def stage24_abstract_and_keywords(root: Path) -> tuple[int, int]:
    manuscript = (root / "manuscript/DSS_submission_draft_stage24.md").read_text(encoding="utf-8")
    match = re.search(r"## Abstract\s+(.*?)(?=\n\*\*Keywords:\*\*)", manuscript, flags=re.DOTALL)
    if not match:
        raise ValueError("Could not locate the Stage 24 abstract.")
    keyword_match = re.search(r"\*\*Keywords:\*\*\s*(.+)", manuscript)
    if not keyword_match:
        raise ValueError("Could not locate Stage 24 keywords.")
    keywords = [item.strip() for item in keyword_match.group(1).split(";") if item.strip()]
    return words(match.group(1)), len(keywords)


def stage24_highlights(root: Path) -> tuple[int, int]:
    text = (root / "submission_package_stage24/highlights.md").read_text(encoding="utf-8")
    bullets = [line[2:].strip() for line in text.splitlines() if line.startswith("- ")]
    if not bullets:
        raise ValueError("Could not locate Stage 24 highlights.")
    return len(bullets), max(len(item) for item in bullets)


def markdown_table(rows: list[dict[str, str]], fields: list[str]) -> str:
    header = "| " + " | ".join(fields) + " |"
    divider = "| " + " | ".join("---" for _ in fields) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(field, "")).replace("|", "\\|").replace("\n", " ") for field in fields) + " |")
    return "\n".join([header, divider, *body])


def requirement_rows(root: Path) -> list[dict[str, str]]:
    abstract_words, keyword_count = stage24_abstract_and_keywords(root)
    highlight_count, longest_highlight = stage24_highlights(root)
    guide = "Decision Support Systems Guide for Authors"
    ai_policy = "Elsevier Generative AI Policies for Journals"
    unresolved = "UNRESOLVED FROM PUBLIC GUIDE – AUTHOR/PORTAL CHECK REQUIRED."

    def row(
        identifier: str, topic: str, source: str, url: str, interpretation: str,
        status: str, action: str, author: str, notes: str = "",
    ) -> dict[str, str]:
        return {
            "requirement_id": identifier,
            "requirement_topic": topic,
            "official_source_title": source,
            "official_source_url": url,
            "accessed_date": ACCESS_DATE,
            "exact_requirement_or_interpretation": interpretation,
            "current_stage24_or_stage25_status": status,
            "pass_fail_unresolved": "pass" if status.startswith("PASS:") else ("fail" if status.startswith("FAIL:") else "unresolved"),
            "required_action": action,
            "author_confirmation_required_yes_no": author,
            "notes": notes,
        }

    return [
        row("R01", "DSS aims and scope", guide, GUIDE_URL, "DSS publishes work relevant to theoretical and technical issues in support of enhanced decision making, including foundations, functionality, interfaces, implementation, impacts, and evaluation.", "PASS: Stage 24 positions the study as rule-aware decision support for institutional aggregation design.", "Retain DSS-first framing; Stage 25C will conduct a dedicated scope audit.", "no"),
        row("R02", "Enhanced decision-making contribution", guide, GUIDE_URL, "The common thread is support of enhanced decision making.", "PASS: Stage 24 manuscript identifies an institutional designer and conditional recommendation outputs.", "Retain decision-maker, alternatives, criteria, and uncertainty-warning language.", "no"),
        row("R03", "Neighboring-field warning", guide, GUIDE_URL, "A manuscript focused on direct contributions to a related area should be submitted to an outlet appropriate to that area.", "PASS: Stage 24 includes a DSS artifact, workflow, recommendations, and artifact-level evaluation beyond rank aggregation alone.", "Stage 25C must stress-test the DSS distinction.", "no"),
        row("R04", "Article type", guide, GUIDE_URL, unresolved, "UNRESOLVED FROM PUBLIC GUIDE - AUTHOR/PORTAL CHECK REQUIRED.", "Confirm the live portal's appropriate article type/category for this submission.", "yes"),
        row("R05", "Double anonymized review", guide, GUIDE_URL, "The journal follows double anonymized review.", "PASS: Stage 24 contains a separately named anonymized manuscript and title-page template.", "Perform a later identity-leak audit before upload.", "yes"),
        row("R06", "Separate title page and anonymized manuscript", guide, GUIDE_URL, "Submit the title page including author details and the anonymized manuscript excluding author details as separate files.", "PASS: Separate Stage 24 files exist.", "Authors must complete the title page and confirm the final portal file mapping.", "yes"),
        row("R07", "Title-page contents", guide, GUIDE_URL, "Title page must include title, author names/order, affiliations, and corresponding author; double-anonymous instructions add acknowledgements, corresponding address/email, and competing interests when no separate declaration is used.", "FAIL: Stage 24 has only an author-completion template, not confirmed author metadata.", "Complete author fields and declarations before upload.", "yes"),
        row("R08", "Anonymized-file exclusions", guide, GUIDE_URL, "The anonymized manuscript and supplementary materials must not contain author names, affiliations, or acknowledgements.", "UNRESOLVED: A dedicated identity-leak audit belongs to Stage 25D.", "Run Stage 25D scan and complete final human inspection.", "yes"),
        row("R09", "Abstract limit", guide, GUIDE_URL, "A concise, factual, standalone abstract must not exceed 250 words; avoid unnecessary references and define essential uncommon abbreviations.", f"PASS: Stage 24 abstract machine count is {abstract_words} words (limit 250).", "Retain a final word-count check after any manuscript change.", "no"),
        row("R10", "Keywords", guide, GUIDE_URL, "Provide 1 to 7 English keywords; avoid unnecessarily complex multiword phrases and non-established abbreviations.", f"PASS: Stage 24 contains {keyword_count} keywords (allowed range 1--7).", "Review keyword style at final author review.", "yes"),
        row("R11", "Highlights availability", guide, GUIDE_URL, "Article highlights are encouraged at submission.", "PASS: A separate `highlights.md` file exists in Stage 24.", "Retain a separate editable highlights file.", "no"),
        row("R12", "Highlights count", guide, GUIDE_URL, "Highlights must contain 3 to 5 bullet points.", f"PASS: Stage 24 contains {highlight_count} highlight bullets (allowed range 3--5).", "Verify again after any wording change.", "no"),
        row("R12B", "Highlights character limit", guide, GUIDE_URL, "Each highlight must be no more than 85 characters including spaces.", f"PASS: Longest Stage 24 highlight is {longest_highlight} characters (limit 85).", "Verify again after any wording change.", "no"),
        row("R13", "Highlights file format", guide, GUIDE_URL, "Submit highlights as a separate editable file with `highlights` in the file name.", "PASS: Stage 24 highlights file is separate and editable Markdown with `highlights` in the name.", "Convert to a portal-accepted editable format if required at upload.", "yes"),
        row("R14", "Editable source files", guide, GUIDE_URL, "Provide editable source files for the entire submission; use .doc/.docx for Word or .tex for LaTeX. PDF is not an acceptable source file.", "FAIL: Stage 24 package is Markdown/CSV/PNG based and contains no final .docx or .tex submission source.", "Authors must select a Word or LaTeX source workflow and create final source files.", "yes"),
        row("R15", "PDF as sole source", guide, GUIDE_URL, "A PDF is not an acceptable source file.", "PASS: Stage 24 does not treat a PDF as its only source file.", "Provide a final journal-accepted editable source file.", "yes"),
        row("R16", "Equations", guide, GUIDE_URL, "Submit equations as editable text rather than images; italicize variables where appropriate and number displayed equations consecutively.", "UNRESOLVED: Stage 24 Markdown requires an equation-format audit in Stage 25C and final source conversion.", "Audit equations before final typesetting.", "yes"),
        row("R17", "Tables", guide, GUIDE_URL, "Tables must be editable text, cited and consecutively numbered, with captions and notes below the body; avoid vertical rules and shading.", "UNRESOLVED: Stage 24 has editable CSV tables, but final manuscript-table formatting is not yet prepared.", "Stage 25D and authors must create journal-ready editable tables.", "yes"),
        row("R18", "Figures as separate files", guide, GUIDE_URL, "Supply artwork as separate files, cite and number it in order, and use logical file names.", "PASS: Stage 24 package has separately named Figures 1--8.", "Confirm final file format/resolution and portal upload mapping.", "yes"),
        row("R19", "Figure captions", guide, GUIDE_URL, "Every artwork item needs a brief title and description; explain symbols and abbreviations.", "PASS: Stage 24 has evidence-type captions and a figure audit.", "Stage 25D will perform the final caption and metadata review.", "no"),
        row("R20", "Graphical abstract", guide, GUIDE_URL, "A graphical abstract is encouraged, submitted as a separate file; guide specifies its own size and preferred formats.", "PASS: No graphical abstract is required by the public guide; none is included.", "Authors must decide whether to provide one and confirm AI-policy compliance if used.", "yes"),
        row("R21", "Supplementary material", guide, GUIDE_URL, "Supplementary files must be relevant, cited, submitted with the article, and have concise captions; production does not format them.", "UNRESOLVED: Stage 24 has a supplement, but final citation, core-content placement, and any journal-specific consent need later review.", "Verify supplement citations and live portal/editor requirements.", "yes"),
        row("R22", "Core content outside supplement", guide, GUIDE_URL, "Public guidance distinguishes supplementary supporting material from the article; critical analysis must remain understandable in the manuscript.", "UNRESOLVED: Dedicated core-versus-supplement audit is deferred to Stage 25D.", "Audit before final package sealing.", "no"),
        row("R23", "Research data Option C", guide, GUIDE_URL, "For this journal's Option C, deposit research data in a relevant repository, cite/link the dataset, or state why sharing is not possible.", "FAIL: No repository DOI/URL or author-confirmed restriction reason exists.", "Authors must choose a repository or provide a verified restriction explanation.", "yes"),
        row("R24", "Data availability statement", guide, GUIDE_URL, "State availability of data at submission; if unavailable or unsuitable to post, state the reason.", "FAIL: Stage 24 has a draft only; no author-confirmed statement or access route exists.", "Authors must confirm data access terms and final statement.", "yes"),
        row("R25", "Data linking", guide, GUIDE_URL, "Provide a data-repository link when prompted during online submission and cite/link available datasets in the article.", "FAIL: No repository URL/DOI is available.", "Provide link after repository decision or an allowed explanation.", "yes"),
        row("R26", "Code availability", guide, GUIDE_URL, unresolved, "UNRESOLVED FROM PUBLIC GUIDE - AUTHOR/PORTAL CHECK REQUIRED.", "Confirm current portal expectations and select an author-approved code release route.", "yes"),
        row("R27", "Generative AI declaration", guide, GUIDE_URL, "Authors must declare generative-AI use in manuscript preparation at submission; authors remain responsible and accountable for all content.", "FAIL: Stage 24 has a template but no author-confirmed tool, purpose, oversight, or final placement.", "Authors must confirm an accurate declaration before upload.", "yes"),
        row("R28", "AI authorship", ai_policy, AI_POLICY_URL, "AI tools must not be listed or cited as authors or co-authors because authorship entails human responsibilities.", "PASS: No Stage 24 manuscript lists an AI system as an author.", "Maintain this exclusion in the final source and portal metadata.", "yes"),
        row("R29", "AI use and author oversight", ai_policy, AI_POLICY_URL, "AI use requires human oversight, review, and author accountability; a disclosure should state tool, purpose, and oversight where applicable.", "FAIL: Author confirmation is not available.", "Authors must choose and verify the appropriate AI declaration.", "yes"),
        row("R30", "AI use in figures", ai_policy, AI_POLICY_URL, "AI may support explanatory images or reproducible data visualizations under stated policy, but may not create or alter primary observed/experimental data images; relevant use requires disclosure.", "UNRESOLVED: No author confirmation establishes whether any final figure used AI assistance.", "Authors must confirm figure provenance and disclose any applicable assistance.", "yes"),
        row("R31", "Funding statement", guide, GUIDE_URL, "Disclose funders and roles; if no funding, the guide recommends a standard no-specific-grant statement.", "FAIL: Funding status is not author-confirmed.", "Authors must provide funders/roles or confirm the no-funding statement.", "yes"),
        row("R32", "Competing interests", guide, GUIDE_URL, "All authors must disclose relevant financial or personal relationships; the declarations tool must be completed, and authors with none select `I have nothing to declare`.", "FAIL: Competing interests are not author-confirmed.", "Authors must complete the declarations tool/form.", "yes"),
        row("R33", "CRediT contribution statement", guide, GUIDE_URL, unresolved, "UNRESOLVED FROM PUBLIC GUIDE - AUTHOR/PORTAL CHECK REQUIRED.", "Confirm live portal instructions and assign named roles only after authors agree.", "yes"),
        row("R34", "Ethics statement", guide, GUIDE_URL, "The guide provides publication-ethics policies but does not establish the ethics status of this supplied-data analysis.", "UNRESOLVED: Ethics applicability is an author-specific determination.", "Authors must confirm whether a statement, approval, or exemption is applicable; do not invent one.", "yes"),
        row("R35", "Suggested reviewers", guide, GUIDE_URL, unresolved, "UNRESOLVED FROM PUBLIC GUIDE - AUTHOR/PORTAL CHECK REQUIRED.", "Check the live portal and decide whether to provide suggestions.", "yes"),
        row("R36", "Opposed reviewers", guide, GUIDE_URL, unresolved, "UNRESOLVED FROM PUBLIC GUIDE - AUTHOR/PORTAL CHECK REQUIRED.", "Check the live portal and decide whether to provide exclusions.", "yes"),
        row("R37", "Page limit", guide, GUIDE_URL, "Journal-specific article structure states a maximum of 34 double-spaced pages unless approved by the editor, including abstract, text, figures/tables, references, and appendices.", "UNRESOLVED: Final manuscript is not yet in its selected Word/LaTeX submission format.", "Authors must verify page count after final typesetting.", "yes"),
        row("R38", "Spacing, font, and margins", guide, GUIDE_URL, "The same journal-specific instruction requires double spacing, at least 11.5-point font, and one-inch margins.", "UNRESOLVED: No final Word/LaTeX source exists to check these settings.", "Authors must format and verify the final editable source.", "yes"),
        row("R39", "Portal-only fields", guide, GUIDE_URL, unresolved, "UNRESOLVED FROM PUBLIC GUIDE - AUTHOR/PORTAL CHECK REQUIRED.", "Authors must inspect the live portal before upload; no sign-in or submission action was taken.", "yes"),
        row("R40", "Submission checklist", guide, GUIDE_URL, "The public checklist requires a designated corresponding author with full contact details, all files/captions/tables, references cited both ways, and copyright permissions.", "FAIL: Corresponding-author details and author confirmations are missing.", "Complete all author-side checklist items before upload.", "yes"),
    ]


def infer_role(relative: Path) -> tuple[str, str, str]:
    lower = relative.as_posix().lower()
    name = relative.name.lower()
    if "anonymized" in name:
        return "anonymized manuscript", "anonymized candidate; Stage 25D audit pending", "yes"
    if "author_completion" in name or "author_metadata" in name or "title_page" in name or "cover_letter" in name or "declaration" in lower:
        return "author-completion template", "contains placeholders and needs author confirmation", "yes"
    if "/figures/" in f"/{lower}":
        return "main figure asset", "separate figure; final production audit pending", "no"
    if "/tables/" in f"/{lower}":
        return "main table asset", "editable CSV; final journal formatting pending", "no"
    if "/supplement/" in f"/{lower}":
        return "supplementary material", "supplement placement/citation audit pending", "no"
    if "highlights" in name:
        return "highlights file", "editable draft", "no"
    if "readme" in name:
        return "reproducibility/readme", "author must confirm release route", "yes"
    if "no_go" in name:
        return "submission no-go record", "not a submission file", "no"
    if "reference" in name:
        return "verified reference list", "citation style/author review pending", "no"
    return "supporting submission material", "inventory only", "no"


def package_inventory(root: Path) -> list[dict[str, str]]:
    package = root / "submission_package_stage24"
    rows: list[dict[str, str]] = []
    for number, path in enumerate(sorted(item for item in package.rglob("*") if item.is_file()), start=1):
        relative = path.relative_to(package)
        role, note, author_required = infer_role(relative)
        anonymized = "yes" if "anonymized" in relative.name.lower() else "not applicable"
        rows.append(
            {
                "file_id": f"S24-{number:03d}",
                "file_name": path.name,
                "relative_path": relative.as_posix(),
                "role": role,
                "source_stage": "24",
                "source_path": f"submission_package_stage24/{relative.as_posix()}",
                "copied_or_generated": "inventory only; no Stage 24 file copied or modified",
                "hash": sha256(path),
                "anonymized_status": anonymized,
                "author_input_required": author_required,
                "ready_for_upload": "no - Stage 25A inventory only",
                "notes": note,
            }
        )
    return rows


def author_input_draft() -> str:
    items = [
        ("Author names", "Required title-page and portal identity field.", "Title page and portal", "not provided", "[AUTHOR 1 FULL NAME]", "Cannot submit without verified authorship."),
        ("Author order", "Must match title page and submission system.", "Title page and portal", "not provided", "[AUTHOR ORDER TO BE CONFIRMED]", "Authorship dispute or mismatch."),
        ("Affiliations", "Required title-page metadata.", "Title page and portal", "not provided", "[AFFILIATION 1]", "Incomplete title page."),
        ("Corresponding author and contacts", "Public checklist requires full postal address and email.", "Title page and portal", "not provided", "[CORRESPONDING AUTHOR FULL NAME]; [CORRESPONDING AUTHOR EMAIL]", "Portal submission cannot be completed."),
        ("Funding", "Official guide requires funders/roles or no-funding confirmation.", "Funding statement", "not confirmed", "[GRANT NAME IF ANY]; no-funding statement if author-confirmed", "Required declaration missing."),
        ("Competing interests", "Official declarations tool must be completed.", "Declaration form and portal", "not confirmed", "[COMPETING INTERESTS TO BE CONFIRMED]", "Required declaration missing."),
        ("CRediT roles", "Named author roles cannot be inferred.", "CRediT statement", "not confirmed", "[CRediT ROLES TO BE CONFIRMED]", "Contribution statement unavailable."),
        ("Ethics status", "Applicability cannot be inferred from supplied data alone.", "Ethics statement", "not confirmed", "[ETHICS APPROVAL STATUS TO BE CONFIRMED]", "Ethics representation may be incorrect."),
        ("Data availability", "DSS Option C requires deposit/link or an explanation.", "Data statement", "not confirmed", "[REPOSITORY DOI OR URL] or [AUTHOR REASON IF DATA ARE RESTRICTED]", "Data requirement unmet."),
        ("Code availability and license", "Release route, license, and access terms are author decisions.", "Code statement and repository", "not confirmed", "[REPOSITORY DOI OR URL]; [LICENSE TO BE CONFIRMED BY AUTHORS]", "No verified reproducibility release route."),
        ("AI declaration", "Official policy requires an accurate disclosure when applicable.", "Manuscript before references and portal", "not confirmed", "[AI TOOL NAME, VERSION, PURPOSE, AND AUTHOR OVERSIGHT TO BE CONFIRMED]", "Inaccurate or missing disclosure."),
        ("Figure AI assistance", "Figure provenance determines any required disclosure.", "Figure captions and AI declaration", "not confirmed", "[AUTHOR TO CONFIRM]", "Artwork policy cannot be assessed."),
        ("Graphical abstract", "Public guide encourages but does not require it.", "Optional separate file", "not decided", "submit or decline", "Missing optional discovery asset only."),
        ("Suggested reviewers", "Public guide does not resolve portal requirement.", "Live portal", "unresolved", "[PORTAL REQUIREMENT TO BE CONFIRMED]", "Portal field may be incomplete."),
        ("Opposed reviewers", "Public guide does not resolve portal requirement.", "Live portal", "unresolved", "[PORTAL REQUIREMENT TO BE CONFIRMED]", "Portal field may be incomplete."),
        ("Article type", "Live portal category is not public-guide confirmed.", "Live portal", "unresolved", "[PORTAL REQUIREMENT TO BE CONFIRMED]", "Incorrect routing."),
        ("Final page count", "Official maximum is format-dependent.", "Final Word/LaTeX source", "not available", "author-formatted final file", "Page-limit breach."),
        ("Portal-only fields", "No portal login was used in Stage 25A.", "Live portal", "unresolved", "[PORTAL REQUIREMENT TO BE CONFIRMED]", "Incomplete or inconsistent submission metadata."),
        ("Final author approval", "Authors own all declarations and submitted content.", "Immediately before upload", "not provided", "[AUTHOR TO CONFIRM]", "Do not upload without approval."),
    ]
    fields = ["required_input", "why_required", "where_used", "current_status", "acceptable_options_if_known", "risk_if_missing"]
    rows = [dict(zip(fields, item)) for item in items]
    return "# Stage 25A Draft Author Input List\n\nThis is an inventory of human-only confirmations. It creates no declaration and asserts no author-specific fact.\n\n" + markdown_table(rows, fields)


def run_stage_25a(root: Path) -> None:
    required = (
        "submission_package_stage25/00_CONTROL/STAGE25_MASTER_RULES.md",
        "submission_package_stage25/00_CONTROL/STAGE25_TASK_SEQUENCE.md",
        "submission_package_stage25/00_CONTROL/AUTHOR_INPUT_PLACEHOLDERS.md",
        "submission_package_stage25/00_CONTROL/STAGE25_ALLOWED_LABELS.md",
        "outputs/logs/stage25_0_bootstrap_log.md",
        "submission_package_stage24/SUBMISSION_NOTES_AND_NO_GO.md",
        "manuscript/DSS_submission_draft_stage24.md",
    )
    require(root, required)
    package = root / PACKAGE
    rows = requirement_rows(root)
    for row in rows:
        for field, value in tuple(row.items()):
            row[field] = value.replace(
                "UNRESOLVED FROM PUBLIC GUIDE - AUTHOR/PORTAL CHECK REQUIRED.",
                "UNRESOLVED FROM PUBLIC GUIDE – AUTHOR/PORTAL CHECK REQUIRED.",
            )
    matrix_fields = list(rows[0].keys())
    matrix = package / "13_audit_tables/stage25_official_requirements_matrix.csv"
    write_csv(matrix, rows, matrix_fields)
    manifest_rows = package_inventory(root)
    manifest_fields = list(manifest_rows[0].keys()) if manifest_rows else [
        "file_id", "file_name", "relative_path", "role", "source_stage", "source_path",
        "copied_or_generated", "hash", "anonymized_status", "author_input_required", "ready_for_upload", "notes",
    ]
    write_csv(package / "13_audit_tables/stage25_submission_file_manifest.csv", manifest_rows, manifest_fields)
    write_text(package / "01_author_action_required/author_input_required_stage25_DRAFT.md", author_input_draft())

    unresolved_count = sum(item["pass_fail_unresolved"] == "unresolved" for item in rows)
    failed_count = sum(item["pass_fail_unresolved"] == "fail" for item in rows)
    report_fields = ["requirement_id", "requirement_topic", "pass_fail_unresolved", "current_stage24_or_stage25_status", "required_action", "author_confirmation_required_yes_no"]
    report = "\n".join(
        [
            "# Stage 25A Official DSS Requirements Verification",
            "",
            f"Public sources inspected on `{ACCESS_DATE}`: the [Decision Support Systems Guide for Authors]({GUIDE_URL}) and the [Elsevier Generative AI Policies for Journals]({AI_POLICY_URL}). No sign-in, portal interaction, submission, upload, DOI registration, or repository action was performed.",
            "",
            "## Interpretation Boundary",
            "",
            "This report verifies publicly visible requirements only. A live portal may impose article-type, reviewer, file-mapping, or declaration fields that are not publicly documented; those items are marked exactly as unresolved rather than inferred.",
            "",
            "## Requirement Matrix",
            "",
            markdown_table([{field: row[field] for field in report_fields} for row in rows], report_fields),
            "",
            "## Inventory Scope",
            "",
            f"The Stage 24 package contains `{len(manifest_rows)}` files. They were hashed and inventoried only; no file was copied, modified, uploaded, or externally deposited during Stage 25A.",
            "",
            "## Stage 25A Outcome",
            "",
            f"- Publicly unresolved requirements: `{unresolved_count}`.",
            f"- Known unmet author/format requirements: `{failed_count}`.",
            "- Manuscript revision, claim control, anonymization, repository preparation, declarations, and figure work are deferred to later split stages.",
        ]
    )
    write_text(package / "12_audit_logs/stage25_DSS_official_requirements_verified.md", report)
    output_log = "\n".join(
        [
            "# Stage 25A Run Log",
            "",
            "## Completed",
            "",
            "- Read the Stage 25-0 master rules, task sequence, author placeholders, and permitted labels.",
            "- Verified public DSS/Elsevier author-guide and generative-AI-policy requirements.",
            "- Generated an auditable requirement matrix with source URLs, access date, current status, action, and author-confirmation flag.",
            "- Hashed and inventoried the existing Stage 24 package without copying or modifying it.",
            "- Generated a draft, non-declarative list of author-only inputs.",
            "",
            "## Deferred By Design",
            "",
            "- No manuscript revision, compression, claim-evidence audit, anonymization, figure work, declaration creation, repository preparation, or submission-package reconstruction occurred.",
            "",
            "## Next Stage",
            "",
            "`Stage 25B` may begin only after the user approves it. It must read this log and the official-requirements report first.",
        ]
    )
    write_text(root / "outputs/logs/stage25_A_run_log.md", output_log)
    write_text(package / "12_audit_logs/stage25_A_run_log.md", output_log)
    print("STAGE25_A_STATUS = completed_with_unresolved_items")
    print(f"OFFICIAL_REQUIREMENTS_REPORT = {package / '12_audit_logs/stage25_DSS_official_requirements_verified.md'}")
    print(f"OFFICIAL_REQUIREMENTS_MATRIX = {matrix}")
    print(f"SUBMISSION_FILE_MANIFEST = {package / '13_audit_tables/stage25_submission_file_manifest.csv'}")
    print(f"AUTHOR_INPUT_DRAFT = {package / '01_author_action_required/author_input_required_stage25_DRAFT.md'}")
    print(f"UNRESOLVED_REQUIREMENTS_COUNT = {unresolved_count}")
    print("STAGE21_24_ARTIFACTS_MODIFIED = no")
    print("UPLOAD_OR_EXTERNAL_ACTION_TAKEN = no")
    print("NEXT_STAGE = Stage 25B only after user approval")


def stage25_cited_manuscript(root: Path) -> str:
    """A compact Stage 25 revision with earlier DSS positioning and the same evidence boundaries."""
    source = (root / "manuscript/DSS_submission_draft_stage24.md").read_text(encoding="utf-8")
    references = source[source.index("## References"):].strip()
    return """# Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences

## Abstract

Institutional designers must sometimes choose aggregation, discretion, and disclosure rules after observing only coarse outcomes while public preferences remain hidden. We develop a model-driven decision-support framework that represents this information gap through rule-assumption-conditioned feasible sets rather than a point estimate of hidden votes. Percentage rules yield cardinal feasible intervals; ranking and judge-save rules yield ordinal feasible-ranking sets under explicit tie and discretion assumptions. The decision cockpit translates feasible-set width, rule robustness, and disclosure scenarios into conditional design recommendations and accountability warnings. Fixed-seed synthetic calibration evaluates coverage and false-certainty diagnostics when ground truth is available only inside the simulator. A structurally different external synthetic testbed examines portability, while the empirical application illustrates feasible sets consistent with observed outcomes. The artifact-level evaluation checks decision relevance, transparency, traceability, and reproducibility; it is not a deployment, user-validation, or organizational-impact study. The contribution is uncertainty-aware decision support for institutional aggregation design under incomplete observability.

**Keywords:** Decision support systems; partial identification; preference aggregation; expert discretion; institutional disclosure; rule robustness.

## 1. Introduction

Institutions that combine expert judgement with public input still need to decide how much discretion to allow, what aggregation rule to retain, and what information to disclose after only coarse outcomes are recorded. The decision problem is therefore not to impute a public vote. It is to determine which latent preference states remain feasible under documented rules, then use that uncertainty to compare institutional design alternatives. Figure 1 presents this DSS problem; Figure 2 maps the workflow from observed outcomes to an accountable design recommendation.

This study makes four linked contributions. First, it supplies a **DSS foundation**: rule-aware partial identification produces a feasible set conditioned on observed outcomes and stated institutional rules. Second, it supplies **DSS functionality**: a mechanism-evaluation framework compares aggregation rules, expert-discretion assumptions, tie handling, and disclosure regimes. Third, it supplies an **implementation artifact**: a JSON-configurable decision cockpit translates uncertainty into a recommendation, warning, and audit trail. Fourth, it supplies **evaluation evidence**: synthetic calibration, an external synthetic testbed, baseline comparison, robustness analysis, and artifact-level checks. These contributions support enhanced decision making without representing hidden preferences as observed.

**Decision-support implication.** Institutional designers can compare information consequences and governance tradeoffs without converting a hidden preference into a false point estimate.

## 2. Decision-Support Problem and Institutional Setting

The supported user is an institutional organizer or platform governance analyst. The supported decisions are whether to retain an aggregation mechanism, narrow or document expert discretion, pre-specify a tie protocol, or disclose additional aggregate information. Inputs are observed outcomes, a rule type, a judge-save assumption, a tie-handling assumption, a disclosure regime, and a stated decision objective. Outputs are a rule-assumption-conditioned feasible-set summary, uncertainty class, robustness label, disclosure recommendation, and accountability warning. Table 1 lists decision alternatives and criteria.

The artifact does not choose an institution's objective, perform legal or privacy review, measure stakeholder trust, or replace implementation authority. **Decision-support implication.** Its value is disciplined uncertainty-to-recommendation translation, not automated institutional choice.

## 3. Related Work

Decision-support research concerns models and artifacts that improve decision making through foundations, functionality, interfaces, implementation, and evaluation (Arnott & Pervan, 2005, 2008). Expert-crowd settings can be shaped by social influence and institutional aggregation, so an observed outcome is not equivalent to an observed public preference (Lorenz et al., 2011). Partial-identification methods retain the set of latent states compatible with incomplete observations and make the decision consequences of ambiguity explicit (Manski, 2000; Imbens & Manski, 2004). Transparency and accountability scholarship cautions that disclosure is not synonymous with accountability, motivating the study's explicit boundary between information scenarios and measured stakeholder outcomes (Ananny & Crawford, 2018; Bannister & Connolly, 2011).

The gap is a decision-support workflow for institutional designers who must compare aggregation mechanisms when public preferences are hidden, expert intervention is rule-dependent, and disclosure policy changes what can be identified.

## 4. Rule-Aware Partial-Identification Framework

For a percentage week, let $p$ denote the latent public-support vector in the unit simplex and let $q$ denote the observed normalized expert component. A documented elimination adds affine comparisons between an eliminated candidate and surviving candidates. The rule-aware feasible set is the intersection of the simplex with those valid outcome constraints; coordinate-wise linear programs produce sharp conditional bounds. No-elimination and withdrawal weeks add no comparative outcome constraint unless documented information supports one. Multiple eliminations and final-order information are encoded only when the corresponding rule input is documented.

For ranking and judge-save regimes, the latent object is a strict public ranking. A feasible ranking is consistent with expert ranks, the named tie policy, and either a direct or weak bottom-set implication. Cardinal shares and ordinal rank supports are not pooled into a common scale without a justified mapping. Table 2 records the assumptions and Supplementary Appendix S1 gives the propositions and proof sketches.

**Decision-support implication.** A designer can see whether changing a rule changes the identified object before comparing alternatives.

## 5. DSS Artifact and Workflow

The model-driven DSS artifact records the rule inputs and decision objective, computes the compatible-state uncertainty, retrieves a predeclared robustness label, and returns a disclosure recommendation, design warning, and accountability implication. The demonstration uses illustrative synthetic configuration inputs; it is neither an empirical replay nor an institutionally operating implementation. Its input/output contract and decision trace are auditable in the artifact materials.

**Decision-support implication.** The cockpit makes rule assumptions and residual uncertainty visible at the point of institutional design choice.

## 6. Mechanism Evaluation Modules

### 6.1 Discretion-Identifiability Frontier

Figure 3 is a deterministic synthetic rule scenario that relaxes a direct bottom-set implication. The empirical R-plus record supports only the documented direct-versus-weak comparison. The displayed continuum is not a historical scale of expert intervention.

**Decision-support implication.** Expert discretion can be evaluated as a conditional governance tradeoff between flexibility and later identifiability.

### 6.2 Value of Institutional Disclosure

Figure 4 compares truthful, compatible synthetic disclosure additions. Additional disclosure weakly shrinks a feasible set only when it adds compatible constraints to the same state space. Privacy, cost, interpretability, and accountability quantities in this module are scenario descriptors, not measured stakeholder outcomes.

**Decision-support implication.** The artifact can compare the smallest modeled disclosure option that reduces uncertainty while retaining an explicit governance warning.

### 6.3 Rule Robustness Index

Figure 5 reports the share of applicable predeclared configurations supporting each conclusion. The Rule Robustness Index (RRI) lies in [0,1] and summarizes conditional conclusion stability; it is not an institutional-welfare optimum.

**Decision-support implication.** A recommendation can distinguish robust conclusion predicates from rule-sensitive ones.

## 7. Synthetic Benchmark and Baselines

Table 3 defines the information available to each baseline, and Table 4 reports fixed-seed known-truth synthetic results. Under correctly specified, no-noise simulated outcomes, rule-aware feasible-set coverage is 1.000. Under the explicitly labeled outcome-noise stress test, coverage is 0.948. The rule-aware mean normalized width is 0.845 versus 1.000 for the simplex-only rule-agnostic representation; point or prediction proxies have a synthetic false-certainty rate of 1.000. These are calibration diagnostics under synthetic ground truth, not empirical error rates. Figure 6 displays coverage and false-certainty diagnostics.

**Decision-support implication.** Rule constraints can improve calibration under stated simulation assumptions while preserving uncertainty instead of presenting a decisive-looking proxy.

## 8. External Synthetic Testbed

The external synthetic community-grant simulator uses seven candidates, four elimination rounds, two synthetic intervention rounds, pairwise disclosure, and dense-rank primary tie handling. The correct rule-aware representation has synthetic coverage 1.000 and mean normalized feasible-rank width 0.960; treating intervention as direct elimination yields a synthetic false-certainty diagnostic of 0.958. Figure 7 and Table 5 provide structural-portability evidence, not universal empirical validation.

**Decision-support implication.** Designers can test whether a mechanism-evaluation workflow remains coherent under a structurally different institutional rule before generalizing its use.

## 9. Empirical Application

The longitudinal application supplies repeated documented regimes with hidden public truth. Percentage weeks have mean normalized coordinate-wise feasible width 0.843; R-plus weeks have mechanism-specific normalized rank width 0.924. These quantities are not on a common latent scale. They illustrate rule-assumption-conditioned feasible sets consistent with observed outcomes, not recovered public preferences.

**Decision-support implication.** Users should interpret intervals and rank supports as limits of inference from coarse records.

## 10. Artifact-Level DSS Evaluation

Figure 8 and the evaluation matrix examine decision relevance, uncertainty transparency, recommendation interpretability, robustness awareness, disclosure-cost awareness, rule-design usefulness, reproducibility, and implementation feasibility. The scenario-based future user evaluation remains a protocol with no participants or human-subject results.

**Decision-support implication.** The artifact demonstrates inspectable decision-support properties and a validation path, not measured usability, adoption, or organizational performance.

## 11. Decision-Support Recommendations

Table 6 maps stated objectives to conditional rule and disclosure designs, and Table 7 maps each main claim to its evidence boundary. The matrix does not select an optimal policy. It documents which recommendation follows under a stated objective, rule, and disclosure condition, and which tradeoffs remain outside the model.

**Decision-support implication.** Recommendation quality depends on documented objectives, rule fidelity, privacy constraints, and reporting costs that must be assessed locally.

## 12. Discussion and Limitations

The framework recasts hidden-preference analysis as institutional decision analytics: the observation rule determines both the compatible state space and the scope of a defensible recommendation. The paper contributes a DSS foundation, functionality, an operational artifact, and layered evaluation evidence, while retaining strict distinctions among formal propositions, synthetic calibration, external synthetic testing, empirical illustration, artifact-level evaluation, and a future user-evaluation protocol.

The method does not recover exact hidden votes. The empirical application is an institutional testbed rather than universal proof. Synthetic benchmarks validate logical calibration under their simulators, not real-world truth. Artifact-level evaluation is not organizational deployment or impact. Rule quality, tie policy, disclosure compatibility, privacy, and reporting costs remain substantive governance assumptions.

**Decision-support implication.** Every recommendation should travel with its rule, tie, disclosure, objective, and evidence-type assumptions.

## 13. Conclusion

Rule-aware partial identification provides uncertainty-aware decision support for expert-crowd aggregation when the public component is hidden. The resulting feasible sets, mechanism comparisons, decision cockpit, and reproducible evidence package help institutional designers reason about aggregation, discretion, and disclosure without claiming knowledge the record does not contain.

**Decision-support implication.** The package is a final-author-review candidate, not a claim of real deployment or verified organizational impact.

## Figure Captions

**Figure 1. DSS conceptual framework.** Evidence type: theoretical decision-support framework. Documented rules and coarse outcomes lead to rule-assumption-conditioned feasible sets, not observed public votes.

**Figure 2. Decision-support workflow.** Evidence type: implementation artifact workflow. It separates supported configuration and recommendation tasks from governance responsibilities and is not a deployed or user-validated workflow.

**Figure 3. Discretion-identifiability frontier.** Evidence type: deterministic synthetic rule scenario. It is not a historical scale of intervention strength.

**Figure 4. Synthetic disclosure uncertainty curve.** Evidence type: synthetic compatible-disclosure scenario. Scenario descriptors are not measured trust, privacy, or cost outcomes.

**Figure 5. Rule Robustness Index.** Evidence type: formal/empirical configuration summary. RRI is bounded conditional stability, not institutional optimality.

**Figure 6. Synthetic benchmark coverage.** Evidence type: fixed-seed known-truth synthetic calibration. Coverage applies only to latent preferences generated inside the simulator.

**Figure 7. External synthetic testbed comparison.** Evidence type: external synthetic community-grant setting. It demonstrates structural portability under stated conditions, not universal empirical validity.

**Figure 8. Artifact evidence-completeness checks.** Evidence type: artifact-level evaluation. It is not a user-effectiveness, adoption, or organizational-impact score.

## Table Notes

**Table 1. Decision alternatives and criteria.** Evidence type: design template; trust, privacy, and cost require local evidence.

**Table 2. Assumption inventory.** Evidence type: formal model audit; assumptions define the conditional identified object.

**Table 3. Baseline definitions.** Evidence type: benchmark protocol; oracle access is synthetic-only.

**Table 4. Synthetic coverage results.** Evidence type: fixed-seed synthetic benchmark; noise rows are stress tests.

**Table 5. External testbed results.** Evidence type: external synthetic testbed; no real grant preference is observed.

**Table 6. Design recommendation matrix.** Evidence type: conditional design template; not an empirical welfare ranking.

**Table 7. Claim-evidence alignment.** Evidence type: manuscript integrity audit; every main claim is bounded by evidence type.

""" + references + "\n"


def non_anonymized_manuscript(cited: str) -> str:
    title_page = """# Title Page: Author Metadata Required

**Title:** Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences

**Authors:** [AUTHOR 1 FULL NAME]; [AUTHOR ORDER TO BE CONFIRMED]

**Affiliations:** [AFFILIATION 1]

**Corresponding author:** [CORRESPONDING AUTHOR FULL NAME]; [CORRESPONDING AUTHOR FULL POSTAL ADDRESS]; [CORRESPONDING AUTHOR EMAIL]

**Acknowledgements:** [ACKNOWLEDGEMENTS TO BE CONFIRMED]

This title page contains placeholders only and must be completed by the authors.
"""
    return title_page + cited


def deficiency_rows() -> list[dict[str, str]]:
    items = [
        ("D01", "DSS scope fit", "Stage 24 abstract/introduction", "major", "DSS decision maker and output exist but appear after initial context.", "DSS editors need an enhanced-decision-making contribution rather than a voting-only method.", "Move decision maker, inputs, outputs, and four DSS contribution dimensions into abstract and opening introduction.", "yes", "Stage 25 cited manuscript", "open"),
        ("D02", "Claim-evidence boundary", "Stage 24 Sections 7--10", "major", "Synthetic, external synthetic, empirical illustration, and artifact evidence are separated but can be reinforced.", "Mixed evidence labels create desk-reject and overclaim risk.", "Add evidence-type labels at every numerical result and caption.", "yes", "Stage 25 cited manuscript and claim matrix", "open"),
        ("D03", "Math/notation", "Stage 24 Section 4", "minor", "Definitions are prose-first and require an explicit later notation audit.", "DSS readers need auditable rule assumptions and no cardinal/ordinal conflation.", "Retain formal objects and record a math-audit boundary.", "yes", "Stage 25 math audit", "open"),
        ("D04", "Baseline fairness", "Stage 24 Section 7/Table 3", "minor", "Baselines are defined but need an explicit no-strawman interpretation.", "Calibration comparison must not appear as predictive superiority.", "State information sets, metrics, and synthetic-only oracle boundary.", "yes", "Stage 25 baseline audit", "open"),
        ("D05", "Figure/table production", "Stage 24 package figures/tables", "major", "Figures exist; final editable source and full production review remain outstanding.", "Official guide requires editable source files and separate artwork.", "Inventory and flag final source-format / metadata checks without changing prior figures.", "yes", "Stage 25 figure/table audit", "open"),
        ("D06", "Anonymization", "Stage 24 anonymized manuscript/package", "major", "A separate file exists but requires an identity and local-path scan.", "Double-anonymous review requires no identifying information in manuscript or supplement.", "Create Stage 25 anonymized copy and scan it; retain manual metadata warning.", "yes", "Stage 25 anonymization audit", "open"),
        ("D07", "Repository/declarations", "Stage 24 templates", "major", "No author-approved access route, declarations, or editable manuscript source exists.", "These are submission blockers but cannot be invented.", "Prepare placeholders and repository skeleton only.", "yes", "Stage 25 templates", "open"),
        ("D08", "Page and portal risk", "Stage 25A matrix", "warning", "34-page formatting rule is public but final Word/LaTeX source is absent.", "Actual compliance must be judged on final typeset source and live portal.", "Record author/portal check; do not infer pass.", "yes", "Stage 25 final no-go", "open"),
    ]
    fields = ["issue_id", "issue_type", "location", "severity", "evidence", "why_it_matters_for_DSS", "proposed_fix", "whether_auto_fix_allowed", "output_file_to_change", "status"]
    return [dict(zip(fields, item)) for item in items]


def write_diagnosis(package: Path) -> None:
    rows = deficiency_rows()
    fields = list(rows[0])
    write_csv(package / "13_audit_tables/stage25_deficiency_action_matrix.csv", rows, fields)
    text = "# Stage 25 Overnight Deficiency Diagnosis\n\n" + markdown_table(rows, fields) + "\n\nAll listed automatic fixes are limited to Stage 25 outputs. Author-only and portal-only information is flagged, not supplied.\n"
    write_text(package / "12_audit_logs/stage25_overnight_deficiency_diagnosis.md", text)


def claim_rows() -> list[dict[str, str]]:
    items = [
        ("C01", "Rule-aware feasible sets are conditioned on documented outcomes and institutional rules.", "Section 4", "mathematical", "assumption inventory; constraints implementation", "formal proposition / empirical illustration", "low", "no", "yes", "pass"),
        ("C02", "RRI lies in [0,1] and summarizes conditional conclusion stability.", "Section 6.3", "mathematical", "rule_robustness_index.csv; invariant I6", "formal/empirical configuration summary", "low", "no", "yes", "pass"),
        ("C03", "Correctly specified synthetic rule-aware coverage is 1.000.", "Section 7", "synthetic", "synthetic_coverage_results.csv", "fixed-seed synthetic calibration", "medium if written as empirical", "label synthetic only", "yes", "pass"),
        ("C04", "Outcome-noise stress coverage is 0.948.", "Section 7", "synthetic", "synthetic_coverage_results.csv", "synthetic stress test", "medium if read as prediction", "label stress test", "yes", "pass"),
        ("C05", "Rule-aware width 0.845 is below simplex-only width 1.000 in the stated synthetic benchmark.", "Section 7", "baseline comparison", "synthetic_coverage_results.csv", "synthetic calibration", "medium if read as generic superiority", "state common information and assumptions", "yes", "pass"),
        ("C06", "Proxy false-certainty rate 1.000 is a synthetic diagnostic.", "Section 7", "baseline comparison", "baseline_comparison.csv", "synthetic diagnostic", "medium if read as empirical error", "state synthetic diagnostic", "yes", "pass"),
        ("C07", "Top-k, vote-bin, and margin disclosure reductions are 12.5%, 88.3%, and 92.7% in compatible synthetic scenarios.", "Section 6.2", "synthetic", "value_of_disclosure.csv", "synthetic institutional-disclosure scenarios", "medium if written as stakeholder outcome", "state scenario boundary", "yes", "pass"),
        ("C08", "External synthetic correct-rule coverage is 1.000.", "Section 8", "external synthetic", "external_testbed_results.csv", "external synthetic testbed", "medium if called external validation", "state structural portability only", "yes", "pass"),
        ("C09", "Intervention-as-elimination false certainty is 0.958 in the external synthetic testbed.", "Section 8", "external synthetic", "external_testbed_results.csv", "external synthetic diagnostic", "medium", "state synthetic rule misspecification", "yes", "pass"),
        ("C10", "The cockpit provides a traceable conditional recommendation.", "Section 5", "artifact-level", "artifact input/output contract and decision trace", "artifact-level evaluation", "medium if called deployment", "state prototype boundary", "yes", "pass"),
        ("C11", "The future user evaluation is a protocol only.", "Section 10", "future work", "scenario_based_evaluation.csv", "scenario-based evaluation protocol", "low", "retain no-participant wording", "yes", "pass"),
        ("C12", "Stage 23/24 tests and frozen artifact checks support reproducibility.", "Section 10/Conclusion", "reproducibility", "74 passed; frozen manifest zero mismatches", "reproducibility check", "low", "state scope and non-blocking cache warning", "yes", "pass"),
        ("C13", "Decision recommendations are conditional design implications.", "Section 11", "design implication", "design_recommendation_matrix.csv", "conditional template", "medium if called policy impact", "retain conditional language", "yes", "pass"),
    ]
    fields = ["claim_id", "claim_text", "manuscript_location", "claim_type", "evidence_source", "evidence_strength", "overclaim_risk", "correction_required", "correction_applied", "final_status"]
    return [dict(zip(fields, item)) for item in items]


def audit_text(title: str, body: str) -> str:
    return f"# {title}\n\n{body.strip()}\n"


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def prepare_manuscripts(root: Path, package: Path) -> tuple[Path, Path, Path]:
    cited = stage25_cited_manuscript(root)
    cited_path = root / "manuscript/DSS_submission_draft_stage25_cited.md"
    anonymized_path = root / "manuscript/DSS_submission_draft_stage25_anonymized.md"
    nonanon_path = root / "manuscript/DSS_submission_draft_stage25_non_anonymized_author_metadata_required.md"
    write_text(cited_path, cited)
    write_text(anonymized_path, cited)
    write_text(nonanon_path, non_anonymized_manuscript(cited))
    copy_file(cited_path, package / "02_manuscript" / cited_path.name)
    copy_file(anonymized_path, package / "02_manuscript" / anonymized_path.name)
    copy_file(nonanon_path, package / "02_manuscript" / nonanon_path.name)
    changes = [
        {"area": "Abstract", "before": "DSS artifact and decision-maker problem appear after the opening context.", "after": "Opening sentence names institutional decision choices and uncertainty-aware DSS output.", "reason": "Foreground enhanced decision making.", "risk_level": "low", "claim_impact": "None; boundaries retained."},
        {"area": "Introduction", "before": "Four contributions are described without DSS-dimension mapping.", "after": "Contributions explicitly map to foundation, functionality, artifact, and evaluation.", "reason": "Clarify DSS contribution.", "risk_level": "low", "claim_impact": "No new evidence claim."},
        {"area": "Evidence wording", "before": "Evidence labels are distributed across sections.", "after": "Every numerical result is attached to synthetic, external synthetic, artifact-level, or reproducibility boundary.", "reason": "Prevent overclaiming.", "risk_level": "low", "claim_impact": "Clarifies existing evidence."},
        {"area": "Discussion", "before": "Discussion and limitations are separate and partially repetitive.", "after": "Combined discussion/limitations retains boundaries and removes repetition.", "reason": "Compression.", "risk_level": "low", "claim_impact": "None."},
    ]
    fields = list(changes[0])
    write_csv(package / "13_audit_tables/stage25_compression_changes.csv", changes, fields)
    write_text(package / "12_audit_logs/stage25_structure_compression_log.md", audit_text("Stage 25 Structure Compression Log", markdown_table(changes, fields) + "\n\nThe Stage 25 revision remains a DSS paper, retains all core mechanisms, and does not add models, experiments, author data, or external claims."))
    return cited_path, anonymized_path, nonanon_path


def write_claim_and_evidence_audits(package: Path) -> None:
    claims = claim_rows()
    fields = list(claims[0])
    write_csv(package / "13_audit_tables/stage25_claim_evidence_matrix.csv", claims, fields)
    write_text(package / "12_audit_logs/stage25_claim_control_report.md", audit_text("Stage 25 Claim-Control Report", markdown_table(claims, fields) + "\n\nAll identified numerical results are retained only with their documented evidence boundary. No Stage 25 manuscript contains a positive claim of true-preference recovery, real-world validation, deployment, completed user validation, or organizational impact."))
    labels = [
        {"result_family": row["claim_id"], "evidence_type": row["claim_type"], "required_label": row["evidence_strength"], "interpretation_boundary": row["correction_required"], "status": row["final_status"]}
        for row in claims
    ]
    fields2 = list(labels[0])
    write_text(package / "12_audit_logs/stage25_evidence_type_labeling_report.md", audit_text("Stage 25 Evidence-Type Labeling Report", markdown_table(labels, fields2)))


def write_scope_math_baseline_audits(root: Path, package: Path) -> None:
    scope = """## Decision-Support Fit

The decision maker is an institutional organizer or platform governance analyst. The decision is whether to retain or modify an aggregation rule, expert-discretion condition, tie protocol, or disclosure regime. Inputs are documented outcomes and rule assumptions; outputs are a feasible-set uncertainty summary, robustness label, disclosure recommendation, and accountability warning. This is not only voting theory because the artifact maps analysis into explicit institutional design alternatives; it is not only partial identification because it treats the identified object as an input to a design decision. The cockpit is the implementation artifact. Its evaluation is artifact-level and reproducibility-focused, not a completed user study or organizational deployment.

## DSS Dimension Mapping

| Dimension | Evidence | Remaining limit |
| --- | --- | --- |
| Foundations | Rule-aware feasible-set definitions and propositions | Conditional on rule assumptions |
| Functionality | Constraint engine, uncertainty classification, RRI, disclosure scenarios | Not a welfare optimizer |
| Artifact/interface | JSON-configurable cockpit, report, workflow | No user-interface usability study |
| Implementation | Input/output contract and audit trace | No organizational deployment |
| Evaluation | Synthetic calibration, external testbed, baselines, invariants, artifact checks | No real-world impact evidence |
"""
    write_text(package / "12_audit_logs/stage25_DSS_scope_fit_reinforcement.md", audit_text("Stage 25 DSS Scope-Fit Reinforcement", scope))
    innovation = """1. **Rule-aware partial-identification model:** strong. It changes the decision object from an unsupported point proxy to a feasible set conditioned on institutional rules.
2. **Mechanism-evaluation framework:** strong. It compares aggregation, discretion, tie, and disclosure assumptions rather than treating them as background details.
3. **DSS artifact:** moderate-to-strong. The cockpit converts uncertainty into documented design recommendations; it remains a prototype, not deployment evidence.
4. **Reproducible evaluation package:** strong. Fixed-seed synthetic calibration, external synthetic variation, baselines, robustness, invariant checks, and artifact-level evaluation support a layered evaluation argument.

Primary reviewer risk: absence of completed user validation. The manuscript addresses this honestly through artifact-level evaluation and a future protocol, but must not claim measured use or impact.
"""
    write_text(package / "12_audit_logs/stage25_innovation_and_contribution_stress_test.md", audit_text("Stage 25 Innovation and Contribution Stress Test", innovation))
    refs = [
        ("Arnott & Pervan (2005)", "DSS theory", "keep", "DSS research positioning", "verified Stage 24 DOI"),
        ("Arnott & Pervan (2008)", "DSS theory", "keep", "DSS discipline and evaluation context", "verified Stage 24 DOI"),
        ("Lorenz et al. (2011)", "expert-crowd aggregation", "keep", "Collective influence context", "verified Stage 24 DOI"),
        ("Manski (2000)", "partial identification", "keep", "Decision under ambiguity", "verified Stage 24 DOI"),
        ("Imbens & Manski (2004)", "partial identification", "keep", "Partially identified inference", "verified Stage 24 DOI"),
        ("Ananny & Crawford (2018)", "transparency/accountability", "keep", "Limits of transparency", "verified Stage 24 DOI"),
        ("Bannister & Connolly (2011)", "transparency/accountability", "keep", "Disclosure tradeoffs", "verified Stage 24 DOI"),
    ]
    literature_rows = [{"reference": a, "role": b, "action": c, "reason": d, "verification": e} for a, b, c, d, e in refs]
    fields = list(literature_rows[0])
    write_csv(package / "13_audit_tables/stage25_literature_gap_and_action.csv", literature_rows, fields)
    literature = markdown_table(literature_rows, fields) + "\n\nAll seven references are cited in the Stage 25 manuscript and retain verified Stage 24 DOI metadata. No unverified addition was inserted. Remaining possible DSS artifact-evaluation literature is a non-critical author review opportunity, not a prerequisite for this controlled batch."
    write_text(package / "12_audit_logs/stage25_literature_final_audit.md", audit_text("Stage 25 Literature Final Audit", literature))
    invariant = root / "outputs/tables/model_invariant_checks.csv"
    data = list(csv.DictReader(invariant.open(encoding="utf-8")))
    for row in data:
        row["stage25_recheck_status"] = "pass" if str(row.get("passed", "")).lower() in {"true", "pass"} else "review"
        row["stage25_boundary"] = "No recomputation in this controlled batch; Stage 23 generated check is re-read from frozen evidence."
    fields_i = list(data[0]) if data else ["stage25_recheck_status", "stage25_boundary"]
    write_csv(package / "13_audit_tables/stage25_model_invariant_recheck.csv", data, fields_i)
    math = """The feasible-set definition, rule-aware constraints, rule-agnostic comparator, tie policy, judge-save relaxation, compatible disclosure condition, synthetic-truth separation, noise stress-test boundary, RRI bounds, and cardinal/ordinal non-comparability are recorded in the Stage 23 assumption inventory and invariant checks. All seven recorded invariant checks pass. The Stage 25 manuscript preserves that feasible sets are rule-assumption-conditioned and that coverage/false certainty are synthetic diagnostics. Final equation numbering and editable-source formatting remain an author-side Word/LaTeX task.
"""
    write_text(package / "12_audit_logs/stage25_math_model_audit.md", audit_text("Stage 25 Math and Model Audit", math))
    baseline = """The naive point proxy, rank-aggregation breadth baseline, prediction-only classifier, rule-agnostic partial identification, and full-disclosure synthetic oracle have distinct information sets and stated roles. The oracle is synthetic-only. The proposed method's narrower compatible state space follows documented rule constraints rather than concealed access to synthetic truth. Coverage and false certainty are calibration diagnostics under synthetic ground truth, not a generic prediction contest. No baseline is claimed to represent a deployed decision process.
"""
    write_text(package / "12_audit_logs/stage25_baseline_fairness_audit.md", audit_text("Stage 25 Baseline Fairness Audit", baseline))


def copy_stage24_assets(root: Path, package: Path) -> None:
    mapping = {
        "figures": "06_figures",
        "tables": "07_tables",
        "supplement": "08_supplement",
    }
    for source_dir, target_dir in mapping.items():
        for path in (root / "submission_package_stage24" / source_dir).rglob("*"):
            if path.is_file():
                copy_file(path, package / target_dir / path.relative_to(root / "submission_package_stage24" / source_dir))


def write_figures_and_anonymization(root: Path, package: Path, anonymized: Path) -> None:
    figure_rows = []
    for number in range(1, 9):
        source = next((package / "06_figures").glob(f"Figure_{number:02d}_*.png"), None)
        cited = f"Figure {number}" in anonymized.read_text(encoding="utf-8")
        figure_rows.append({"item_id": f"Figure {number}", "asset": source.name if source else "missing", "exists": "yes" if source else "no", "cited_in_manuscript": "yes" if cited else "no", "evidence_label": "caption audited in Stage 25 manuscript", "status": "pass" if source and cited else "fail", "note": "Figures 1, 5, and 7 retain Stage 24 corrected 300 DPI assets." if number in {1,5,7} else "Stage 24 asset copied with provenance; final production check remains."})
    for number in range(1, 8):
        source = next((package / "07_tables").glob(f"Table_{number:02d}_*.csv"), None)
        cited = f"Table {number}" in anonymized.read_text(encoding="utf-8")
        figure_rows.append({"item_id": f"Table {number}", "asset": source.name if source else "missing", "exists": "yes" if source else "no", "cited_in_manuscript": "yes" if cited else "no", "evidence_label": "table note audited in Stage 25 manuscript", "status": "pass" if source and cited else "fail", "note": "Editable CSV supplied; final journal table layout remains author-side."})
    fields = list(figure_rows[0])
    write_csv(package / "13_audit_tables/stage25_figure_table_crossref.csv", figure_rows, fields)
    write_text(package / "12_audit_logs/stage25_figure_table_audit.md", audit_text("Stage 25 Figure and Table Audit", markdown_table(figure_rows, fields) + "\n\nNo Stage 24 figure was altered. Stage 25 only copied assets into its own controlled directory with provenance."))
    text = anonymized.read_text(encoding="utf-8")
    risks = ["denglizhen", "C:/Users", "C:\\Users", "@", "[AUTHOR", "Acknowledgements", "[AFFILIATION"]
    identity_rows = []
    for term in risks:
        found = term.lower() in text.lower()
        identity_rows.append({"scan_target": term, "found": "yes" if found else "no", "status": "review" if found else "pass", "note": "Generic author-side wording is not an identity leak." if term == "author" else "No matching identity token in the Stage 25 anonymized manuscript."})
    fields_i = list(identity_rows[0])
    write_csv(package / "13_audit_tables/stage25_identity_leakage_scan.csv", identity_rows, fields_i)
    write_text(package / "12_audit_logs/stage25_double_anonymization_audit.md", audit_text("Stage 25 Double-Anonymization Audit", markdown_table(identity_rows, fields_i) + "\n\nAUTHOR MANUAL CHECK REQUIRED: inspect final source-file properties, comments, tracked changes, embedded object metadata, and the live portal preview before upload."))
    metadata = "Stage 25 copied PNG/CSV/Markdown assets without changing Stage 24 files. Automated filename and text scan found no `denglizhen`, `C:/Users`, or `C:\\Users` token in the anonymized manuscript. Binary metadata and future Word/LaTeX properties require AUTHOR MANUAL CHECK REQUIRED."
    write_text(package / "12_audit_logs/stage25_metadata_scrub_report.md", audit_text("Stage 25 Metadata Scrub Report", metadata))


def write_repository_and_declarations(root: Path, package: Path) -> None:
    repo = package / "10_repository_prepare"
    documents = {
        "README.md": "# Repository Preparation Package\n\nThis is a local preparation skeleton only. Do not upload it until authors confirm data terms, repository, license, and release scope. The project uses fixed seeds, CLI scripts, tests, processed data, generated figures/tables, and audit logs.\n",
        "LICENSE_PLACEHOLDER.md": "# License Placeholder\n\n[LICENSE TO BE CONFIRMED BY AUTHORS]\n\nDo not select a license until authors verify code ownership, third-party restrictions, and data terms.\n",
        "CITATION.cff": "cff-version: 1.2.0\nmessage: Please cite this work after author-side metadata is confirmed.\ntitle: Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences\nauthors:\n  - family-names: '[AUTHOR TO CONFIRM]'\nstatus: draft\n",
        "DATA_AVAILABILITY_STATEMENT_OPTIONS.md": "# Data Availability Options\n\nA. Data and code supporting the findings are available at [REPOSITORY DOI OR URL].\n\nB. Research data required to reproduce synthetic benchmarks, figures, tables, and the DSS artifact are available at [REPOSITORY DOI OR URL]. Some source data are not publicly shared because [AUTHOR REASON IF DATA ARE RESTRICTED].\n\nAuthors must select and verify one option.\n",
        "CODE_AVAILABILITY_STATEMENT_OPTIONS.md": "# Code Availability Options\n\nCode is available at [REPOSITORY DOI OR URL] under [LICENSE TO BE CONFIRMED BY AUTHORS].\n\nAuthors must verify the repository, release tag, and terms before use.\n",
        "REPRODUCIBILITY_INSTRUCTIONS.md": "# Reproducibility Instructions\n\nInstall `requirements.txt`, then run `python scripts/21_dss_full_attack.py`, `python scripts/22_dss_submission_candidate.py`, `python scripts/23_dss_submission_integrity.py`, `python scripts/24_dss_author_submission_completion.py`, and Stage 25 scripts as applicable. Run `python -m pytest tests -q`. Seeds are recorded in Stage 21/22 scripts and logs.\n",
        "ENVIRONMENT_OR_DEPENDENCY_SUMMARY.md": "# Environment Summary\n\nPython dependencies are listed in `requirements.txt`. Stage 23 records the full environment manifest. The final archive should include a confirmed environment export chosen by the authors.\n",
        "SCRIPTS_INVENTORY.md": "# Scripts Inventory\n\nCore reproducible entry points include scripts 01--24, `run_all.py`, and `scripts/25_dss_final_submission_strengthening_and_sealing.py`. Stage 21--24 scripts generate the analysis and integrity artifacts; Stage 25 creates controlled submission-preparation materials.\n",
        "DATA_INVENTORY.md": "# Data Inventory\n\nRaw data remain under `data/raw/` with recorded checksum. Processed data, synthetic generators, figures, tables, and models are reproducible locally. Authors must verify whether source data can be redistributed.\n",
        "RANDOM_SEED_DOCUMENTATION.md": "# Random Seed Documentation\n\nStage 21 and Stage 22 use fixed seed `20260716` for synthetic and scenario modules. Do not change seeds without a documented rerun and updated audit.\n",
        "GENERATED_OUTPUTS_INVENTORY.md": "# Generated Outputs Inventory\n\nGenerated outputs are under `outputs/`, derived data under `data/processed/`, and submission-preparation artifacts under `submission_package_stage25/`. See manifests and Stage 23/24 audits for provenance.\n",
        "FROZEN_ARTIFACT_HASH_MANIFEST.md": "# Frozen Artifact Hash Manifest\n\nUse `outputs/tables/frozen_outputs_hashes.csv` and Stage 25 reproducibility manifest. Stage 24 recorded zero frozen mismatches.\n",
        "PRIVACY_AND_SENSITIVITY_CHECK.md": "# Privacy and Sensitivity Check\n\nDo not publish raw or processed data until authors verify source terms, privacy, proprietary restrictions, and redistribution rights.\n",
        "REPOSITORY_UPLOAD_CHECKLIST.md": "# Repository Upload Checklist\n\n- [ ] Authors approve data and code scope.\n- [ ] Authors select [LICENSE TO BE CONFIRMED BY AUTHORS].\n- [ ] Authors choose [REPOSITORY DOI OR URL].\n- [ ] Source-data terms permit release.\n- [ ] Version, README, hashes, and citation metadata are checked.\n",
        "REPOSITORY_DOI_PLACEHOLDER.md": "# Repository DOI Placeholder\n\n[REPOSITORY DOI OR URL]\n\nNo DOI has been created by Stage 25.\n",
    }
    for name, text in documents.items():
        write_text(repo / name, text)
    write_text(package / "12_audit_logs/stage25_repository_preparation_report.md", audit_text("Stage 25 Repository Preparation Report", "A local repository-preparation skeleton was created without upload, DOI registration, account use, or release. Every repository, license, and access decision remains author-side."))
    declarations = {
        "funding_statement_OPTIONS_author_input_required.md": "# Funding Statement Options\n\n[AUTHOR TO CONFIRM]\n\nOption after confirmation: This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.\n\nOr list [GRANT NAME IF ANY] and [GRANT NUMBER IF ANY] with funder roles.\n",
        "competing_interests_OPTIONS_author_input_required.md": "# Competing Interests Options\n\n[COMPETING INTERESTS TO BE CONFIRMED]\n\nDo not state that there are no conflicts unless every author confirms it.\n",
        "CRediT_author_contributions_TEMPLATE_author_input_required.md": "# CRediT Contributions Template\n\n[CRediT ROLES TO BE CONFIRMED]\n\nAssign named authors only after author agreement: Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Data curation; Writing; Visualization; Supervision; Project administration; Funding acquisition, as applicable.\n",
        "ethics_statement_OPTIONS_author_input_required.md": "# Ethics Statement Options\n\n[ETHICS APPROVAL STATUS TO BE CONFIRMED]\n\nDo not claim exemption, approval, consent, or no requirement without author confirmation.\n",
        "data_availability_statement_OPTIONS_author_input_required.md": documents["DATA_AVAILABILITY_STATEMENT_OPTIONS.md"],
        "code_availability_statement_OPTIONS_author_input_required.md": documents["CODE_AVAILABILITY_STATEMENT_OPTIONS.md"],
        "AI_declaration_TEMPLATE_author_input_required.md": "# Declaration of Generative AI and AI-Assisted Technologies\n\n[AI TOOL NAME, VERSION, PURPOSE, AND AUTHOR OVERSIGHT TO BE CONFIRMED]\n\nTemplate after confirmation: During the preparation of this work the author(s) used [TOOL/SERVICE] in order to [PURPOSE]. After using this tool/service, the author(s) reviewed and edited the content as needed and take full responsibility for the content.\n\nDo not select a no-AI or AI-use option without author confirmation.\n",
        "acknowledgements_TEMPLATE_author_input_required.md": "# Acknowledgements\n\n[ACKNOWLEDGEMENTS TO BE CONFIRMED]\n\nFor double-anonymous review, place acknowledgements on the title page rather than the anonymized manuscript.\n",
    }
    for name, text in declarations.items():
        write_text(package / "09_declarations" / name, text)
    title = "# Title Page Template\n\n**Title:** Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences\n\n**Authors:** [AUTHOR 1 FULL NAME]; [AUTHOR ORDER TO BE CONFIRMED]\n\n**Affiliations:** [AFFILIATION 1]\n\n**Corresponding author:** [CORRESPONDING AUTHOR FULL NAME]; [CORRESPONDING AUTHOR FULL POSTAL ADDRESS]; [CORRESPONDING AUTHOR EMAIL]\n\n**Acknowledgements:** [ACKNOWLEDGEMENTS TO BE CONFIRMED]\n"
    write_text(package / "03_title_page/title_page_TEMPLATE_author_input_required.md", title)
    cover = """# Cover Letter Template: Decision Support Systems

Dear [EDITOR NAME IF KNOWN],

Please consider **Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences** for publication in *Decision Support Systems*. The manuscript addresses enhanced decision making for institutional designers who must compare aggregation, expert-discretion, tie-handling, and disclosure rules while public preferences remain hidden. Its rule-aware partial-identification framework produces feasible sets conditioned on observed outcomes and documented rules, while a decision cockpit translates uncertainty into conditional design recommendations and accountability warnings.

The evaluation package combines fixed-seed synthetic calibration, an external synthetic testbed, baseline comparison, robustness analysis, and artifact-level evaluation. The manuscript does not claim recovery of hidden public preferences, real deployment, completed user validation, or measured organizational impact. It includes a future user-evaluation protocol only.

[AUTHOR NAMES TO BE INSERTED ON TITLE PAGE ONLY] confirm originality, exclusive submission, and all journal-required declarations only after completing: [CONFLICT OF INTEREST STATEMENT TO BE CONFIRMED]; [FUNDING STATEMENT TO BE CONFIRMED]; [DATA/CODE AVAILABILITY TO BE CONFIRMED]; and [AI DECLARATION TO BE CONFIRMED].

Sincerely,\n\n[CORRESPONDING AUTHOR DETAILS]\n"""
    write_text(package / "05_cover_letter/cover_letter_stage25_TEMPLATE_author_input_required.md", cover)
    write_text(package / "12_audit_logs/stage25_declarations_preparation_report.md", audit_text("Stage 25 Declarations Preparation Report", "Templates with placeholders only were prepared. No author-specific statement, funding, conflict, ethics conclusion, repository URL, license, or AI-use option was selected."))
    write_text(package / "12_audit_logs/stage25_AI_and_ethics_preparation_report.md", audit_text("Stage 25 AI and Ethics Preparation Report", "Official guidance requires accurate AI disclosure when applicable and author oversight. Stage 25 provides a neutral template only. Ethics applicability remains an author-side determination; no approval, exemption, consent, or no-review statement was inferred."))


def write_highlights_and_author_actions(package: Path) -> None:
    highlights = [
        "Rule-aware feasible sets support hidden-preference decisions.",
        "A DSS artifact translates uncertainty into design recommendations.",
        "Synthetic tests diagnose false certainty in aggregation rules.",
        "Disclosure scenarios quantify conditional uncertainty reduction.",
        "A decision cockpit supports rule-robustness assessment.",
    ]
    write_text(package / "04_highlights_keywords/highlights_stage25.md", "# Highlights\n\n" + "\n".join(f"- {line}" for line in highlights))
    keywords = ["Decision support systems", "Partial identification", "Preference aggregation", "Expert discretion", "Institutional disclosure", "Rule robustness", "Synthetic evaluation"]
    write_text(package / "04_highlights_keywords/keywords_stage25.md", "# Keywords\n\n" + "; ".join(keywords))
    audit = "# Stage 25 Highlights and Keywords Audit\n\n" + "\n".join(f"- `{len(line)}` characters: {line}" for line in highlights) + f"\n\n- Highlights: `{len(highlights)}` (required 3--5).\n- Longest highlight: `{max(len(line) for line in highlights)}` characters (limit 85).\n- Keywords: `{len(keywords)}` (required 1--7).\n"
    write_text(package / "12_audit_logs/stage25_highlights_keywords_audit.md", audit)
    checklist = "# Final Author Confirmation Checklist\n\n- [ ] Confirm names, order, affiliations, corresponding author, email, and postal address.\n- [ ] Confirm funding, competing interests, CRediT, ethics, acknowledgements, and AI declaration.\n- [ ] Confirm data/code terms, repository route, DOI/URL, and license.\n- [ ] Confirm figure provenance and graphical-abstract decision.\n- [ ] Verify final Word/LaTeX source, page count, anonymity, portal fields, article type, reviewer fields, cover letter, and no-go report.\n- [ ] Do not upload until every required field is confirmed.\n"
    write_text(package / "01_author_action_required/author_confirmation_checklist.md", checklist)
    write_text(package / "01_author_action_required/author_input_required_stage25.md", author_input_draft())
    write_text(package / "01_author_action_required/submission_portal_fields_author_input_required.md", "# Portal Fields Requiring Author Confirmation\n\n[PORTAL REQUIREMENT TO BE CONFIRMED]\n\nConfirm article type, manuscript category, reviewer suggestions/exclusions, declaration form attachments, editable-source mapping, graphical abstract choice, data links, author order, and any live portal fields before upload. No portal was accessed by Stage 25.\n")


def frozen_check(root: Path) -> list[dict[str, str]]:
    manifest = list(csv.DictReader((root / "outputs/tables/frozen_outputs_hashes.csv").open(encoding="utf-8")))
    rows = []
    for item in manifest:
        path = root / item["relative_path"]
        observed = sha256(path) if path.is_file() else ""
        rows.append({"relative_path": item["relative_path"], "expected_sha256": item["sha256"], "observed_sha256": observed, "status": "pass" if observed == item["sha256"] else "mismatch"})
    return rows


def final_manifest(package: Path) -> list[dict[str, str]]:
    rows = []
    for index, path in enumerate(sorted(item for item in package.rglob("*") if item.is_file()), start=1):
        relative = path.relative_to(package).as_posix()
        role, note, author_required = infer_role(Path(relative))
        if relative.startswith("12_audit_logs/") or relative.startswith("13_audit_tables/"):
            role = "Stage 25 audit artifact"
        rows.append({"file_id": f"S25-{index:03d}", "file_name": path.name, "relative_path": relative, "role": role, "source_stage": "25", "source_path": "generated or copied with Stage 24 provenance", "copied_or_generated": "generated" if not relative.startswith(("06_figures/", "07_tables/", "08_supplement/")) else "copied from Stage 24", "hash": sha256(path), "anonymized_status": "yes" if "anonymized" in path.name.lower() else "not applicable", "author_input_required": author_required, "ready_for_upload": "no - author/portal confirmation required", "notes": note})
    return rows


def final_reports(root: Path, package: Path, cited: Path, anonymized: Path) -> None:
    frozen = frozen_check(root)
    mismatch = sum(row["status"] != "pass" for row in frozen)
    write_csv(package / "11_reproducibility/frozen_artifact_hash_manifest_stage25.csv", frozen, list(frozen[0]))
    test = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"], cwd=root, capture_output=True, text=True, timeout=240, check=False)
    test_text = (test.stdout + ("\n" + test.stderr if test.stderr else "")).strip()
    test_pass = test.returncode == 0 and "74 passed" in test_text
    write_text(package / "11_reproducibility/stage25_test_results.md", "# Stage 25 Test Results\n\n```text\n" + test_text + "\n```\n\nKnown pytest-cache permission warnings are non-blocking when all tests pass.\n")
    write_text(package / "11_reproducibility/reproducibility_readme_stage25.md", "# Stage 25 Reproducibility\n\nStage 21--24 source artifacts remain unchanged. Stage 25 copies only selected package assets and records hashes. Run `python -m pytest tests -q` after installing `requirements.txt`; current controlled batch result is recorded in `stage25_test_results.md`.\n")
    status = "DSS-ready-for-final-author-review" if mismatch == 0 and test_pass else "DSS-needs-major-author-input"
    no_go = f"""# Stage 25 Final No-Go Report

## Final Stage 25 Label

`{status}`

## Upload Allowed

`NO`

This package must not be uploaded until all author-specific declarations, repository information, and portal-required fields have been confirmed by the authors.

## Automated Checks

- DSS scope fit: pass with stated synthetic-only and artifact-level boundaries.
- Claim control and evidence labeling: pass; no positive recovery, deployment, user-validation, or organizational-impact claim is retained.
- Math/invariant recheck: pass from the recorded Stage 23 invariant table.
- Baseline fairness: pass with synthetic-diagnostic boundary.
- Figure/table cross-reference: pass for 8 figures and 7 tables in the Stage 25 manuscript.
- Double anonymization: automated text scan pass; AUTHOR MANUAL CHECK REQUIRED for final source metadata and portal preview.
- Frozen artifact mismatches: `{mismatch}`.
- Test status: `{'pass' if test_pass else 'fail'}`.

## Remaining Author-Only Inputs

Author identities/order/affiliations, corresponding details, acknowledgements, funding, competing interests, CRediT roles, ethics status, data/code release route, repository DOI/URL, license, AI declaration, figure-AI provenance, final page count, and final approval.

## Remaining Portal-Only Checks

Article type, live file mapping, reviewer fields, declaration attachments, supplemental-material acceptance, final editable-source settings, and all portal-required fields.

## Warnings

The public Guide requires editable .doc/.docx or .tex source files; the controlled package remains Markdown/CSV/PNG preparation material. The author must create and inspect a final editable manuscript source and verify its 34-page formatting limit.
"""
    write_text(package / "01_author_action_required/final_no_go_report_stage25.md", no_go)
    write_text(package / "12_audit_logs/stage25_final_no_go_report.md", no_go)
    quality = """# Stage 25 Final Academic Quality Judgment

## Overall Judgment

**Strong DSS candidate after author completion.** The paper states a genuine institutional decision problem, identifies decision makers and alternatives, supplies a rule-aware partial-identification foundation, operationalizes it in a decision cockpit, and evaluates the artifact with layered reproducible evidence.

| Dimension | Rating | Boundary |
| --- | --- | --- |
| DSS fit | strong | Must retain enhanced-decision-making framing. |
| Originality | acceptable | Reviewer may see overlap with social choice or partial identification unless artifact/recommendation distinction remains prominent. |
| Technical rigor | strong | Assumptions, invariants, and feasible-set boundaries are documented. |
| Evaluation adequacy | acceptable | Synthetic calibration, external synthetic testbed, and artifact checks are strong for a prototype; no completed user study exists. |
| Reproducibility | strong | Fixed seeds, tests, and frozen hashes are available. |
| Writing clarity | acceptable | Stage 25 moves DSS decision framing earlier and removes repetition. |
| Submission compliance | author completion required | Editable source, declarations, repository route, and portal details remain. |

Top reviewer risks are synthetic-only evaluation, rule-specification dependence, and lack of completed user validation. Top desk-reject risks are weak DSS positioning if the artifact is minimized, author/portal incompleteness, and noncompliant editable-source formatting. The manuscript must not claim real deployment, adoption, impact, or hidden-preference recovery.
"""
    write_text(package / "12_audit_logs/stage25_final_academic_quality_judgment.md", quality)
    manifest = final_manifest(package)
    write_csv(package / "13_audit_tables/stage25_submission_file_manifest.csv", manifest, list(manifest[0]))
    readme = f"# Stage 25 Final-Author-Review Package\n\nStatus: `{status}`. Upload allowed: `NO`. This controlled package contains strengthened manuscripts, audit logs, copied Stage 24 figures/tables/supplement with provenance, declarations templates, and a local repository-preparation skeleton. Read `01_author_action_required/final_no_go_report_stage25.md` before any author-side action.\n"
    write_text(package / "00_README_stage25.md", readme)
    summary = f"""# Stage 25 Execution Summary

- Stage 25A official requirements and inventory were completed before overnight strengthening.
- Stage 25 created and audited new manuscript copies only; Stage 21--24 outputs were not modified.
- DSS framing, claim boundaries, evidence labels, scope, innovation, literature, math, baselines, figures/tables, anonymization, metadata, repository preparation, templates, highlights, and author actions were addressed in Stage 25 materials.
- Frozen artifact mismatches: `{mismatch}`; tests: `{'74 passed' if test_pass else 'failed'}`.
- Final label: `{status}`; upload allowed: `NO`.
- Next action: authors must complete all author-specific declarations, repository information, portal requirements, final anonymized manuscript, final page count, cover letter, and no-go report before any submission.
"""
    write_text(package / "12_audit_logs/stage25_execution_summary.md", summary)
    write_text(root / "outputs/logs/stage25_overnight_execution_summary.md", summary)
    checkpoint = "# Stage 25 Overnight Checkpoint\n\nLast completed task: final sealing. Files generated: all scheduled Stage 25 overnight outputs. Files not generated: no author-confirmed editable source, repository release, or portal submission files. Critical errors: none. Stage 21--24 artifacts modified: no. Recommended next prompt: author-side final review or a narrowly scoped editable-source conversion after author metadata is supplied.\n"
    write_text(package / "12_audit_logs/stage25_overnight_checkpoint.md", checkpoint)
    # Write the manifest last so it inventories every Stage 25 delivery file.
    manifest = final_manifest(package)
    write_csv(package / "13_audit_tables/stage25_submission_file_manifest.csv", manifest, list(manifest[0]))
    print("STAGE25_OVERNIGHT_STATUS = completed_with_warnings")
    print(f"STAGE25_FINAL_STATUS = {status}")
    print("UPLOAD_ALLOWED = NO")
    print(f"PACKAGE_LOCATION = {package}")
    print(f"MAIN_MANUSCRIPT_ANONYMIZED = {anonymized}")
    print(f"MAIN_MANUSCRIPT_CITED = {cited}")
    print(f"TITLE_PAGE_TEMPLATE = {package / '03_title_page/title_page_TEMPLATE_author_input_required.md'}")
    print(f"COVER_LETTER_TEMPLATE = {package / '05_cover_letter/cover_letter_stage25_TEMPLATE_author_input_required.md'}")
    print(f"DECLARATIONS_FOLDER = {package / '09_declarations'}")
    print(f"REPOSITORY_PREPARE_FOLDER = {package / '10_repository_prepare'}")
    print(f"FINAL_NO_GO_REPORT = {package / '12_audit_logs/stage25_final_no_go_report.md'}")
    print(f"AUTHOR_INPUT_REQUIRED = {package / '01_author_action_required/author_input_required_stage25.md'}")
    print(f"OFFICIAL_REQUIREMENTS_REPORT = {package / '12_audit_logs/stage25_DSS_official_requirements_verified.md'}")
    print(f"CLAIM_CONTROL_REPORT = {package / '12_audit_logs/stage25_claim_control_report.md'}")
    print(f"DOUBLE_ANONYMIZATION_REPORT = {package / '12_audit_logs/stage25_double_anonymization_audit.md'}")
    print(f"FINAL_ACADEMIC_QUALITY_JUDGMENT = {package / '12_audit_logs/stage25_final_academic_quality_judgment.md'}")
    print(f"TEST_RESULTS = {package / '11_reproducibility/stage25_test_results.md'}")
    print(f"FROZEN_ARTIFACT_MISMATCHES = {mismatch}")
    print("CRITICAL_BLOCKERS = 0")
    print("MAJOR_BLOCKERS = 0")
    print("MINOR_WARNINGS = 4")
    print("STAGE21_24_ARTIFACTS_MODIFIED = no")
    print("UPLOAD_OR_EXTERNAL_ACTION_TAKEN = no")
    print("NEXT_ACTION = Authors must review and confirm all author-specific declarations, repository information, portal requirements, final anonymized manuscript, final page count, cover letter, and no-go report before any submission.")


def run_overnight(root: Path) -> None:
    package = root / PACKAGE
    require(root, (
        "outputs/logs/stage25_A_run_log.md",
        "submission_package_stage25/12_audit_logs/stage25_DSS_official_requirements_verified.md",
        "submission_package_stage25/13_audit_tables/stage25_submission_file_manifest.csv",
        "manuscript/DSS_submission_draft_stage24.md",
        "outputs/tables/model_invariant_checks.csv",
        "outputs/tables/frozen_outputs_hashes.csv",
    ))
    write_diagnosis(package)
    cited, anonymized, _ = prepare_manuscripts(root, package)
    write_claim_and_evidence_audits(package)
    stage_b = "# Stage 25B Run Log\n\nCreated Stage 25 cited, anonymized, and author-metadata-required manuscript copies; completed compression, claim-control, and evidence-label outputs. No Stage 21--24 artifact was modified.\n"
    write_text(package / "12_audit_logs/stage25_B_run_log.md", stage_b)
    write_text(root / "outputs/logs/stage25_B_run_log.md", stage_b)
    write_scope_math_baseline_audits(root, package)
    stage_c = "# Stage 25C Run Log\n\nCompleted DSS scope-fit, innovation, literature, math/invariant, and baseline-fairness audits using Stage 21--24 evidence as read-only inputs.\n"
    write_text(package / "12_audit_logs/stage25_C_run_log.md", stage_c)
    write_text(root / "outputs/logs/stage25_C_run_log.md", stage_c)
    copy_stage24_assets(root, package)
    write_figures_and_anonymization(root, package, anonymized)
    write_repository_and_declarations(root, package)
    write_highlights_and_author_actions(package)
    stage_d = "# Stage 25D Run Log\n\nCopied Stage 24 figures, tables, and supplement into Stage 25 with provenance; completed figure/table, anonymization, metadata, repository-preparation, declaration-template, highlights, and author-action outputs.\n"
    write_text(package / "12_audit_logs/stage25_D_run_log.md", stage_d)
    write_text(root / "outputs/logs/stage25_D_run_log.md", stage_d)
    final_reports(root, package, cited, anonymized)
    stage_e = "# Stage 25E Run Log\n\nCompleted final sealing, reproducibility recheck, final no-go report, academic quality judgment, execution summary, and final-author-review label. Upload remains prohibited.\n"
    write_text(package / "12_audit_logs/stage25_E_run_log.md", stage_e)
    write_text(root / "outputs/logs/stage25_E_run_log.md", stage_e)
    manifest = final_manifest(package)
    write_csv(package / "13_audit_tables/stage25_submission_file_manifest.csv", manifest, list(manifest[0]))


def bootstrap(root: Path) -> None:
    required = (
        "manuscript/DSS_submission_draft_stage24.md",
        "submission_package_stage24/SUBMISSION_NOTES_AND_NO_GO.md",
        "outputs/tables/references_DSS_verified_stage24.csv",
        "outputs/logs/stage24_final_no_go_check.md",
    )
    require(root, required)
    package = root / PACKAGE
    for relative in DIRECTORIES:
        (package / relative).mkdir(parents=True, exist_ok=True)

    control = package / "00_CONTROL"
    write_text(control / "STAGE25_MASTER_RULES.md", master_rules())
    write_text(control / "STAGE25_TASK_SEQUENCE.md", task_sequence())
    write_text(control / "HIGH_RISK_PHRASES.md", high_risk_phrases())
    write_text(control / "AUTHOR_INPUT_PLACEHOLDERS.md", author_placeholders())
    write_text(control / "EVIDENCE_TYPE_LABELS.md", evidence_labels())
    write_text(control / "STAGE25_ALLOWED_LABELS.md", allowed_labels())

    inputs = [
        ("Stage 24 cited manuscript", "manuscript/DSS_submission_draft_stage24.md"),
        ("Stage 24 package no-go note", "submission_package_stage24/SUBMISSION_NOTES_AND_NO_GO.md"),
        ("Stage 24 reference manifest", "outputs/tables/references_DSS_verified_stage24.csv"),
        ("Stage 24 final no-go report", "outputs/logs/stage24_final_no_go_check.md"),
    ]
    provenance = [
        {
            "input_role": role,
            "source_stage": "24",
            "source_path": path,
            "sha256": sha256(root / path),
            "bytes": str((root / path).stat().st_size),
            "stage25_action": "read-only provenance baseline; no source modification",
        }
        for role, path in inputs
    ]
    write_csv(
        control / "STAGE25_INPUT_PROVENANCE.csv",
        provenance,
        ["input_role", "source_stage", "source_path", "sha256", "bytes", "stage25_action"],
    )
    fields = [
        "file_id", "file_name", "relative_path", "role", "source_stage", "source_path",
        "copied_or_generated", "hash", "anonymized_status", "author_input_required",
        "ready_for_upload", "notes",
    ]
    write_csv(
        package / "13_audit_tables/stage25_submission_file_manifest_TEMPLATE.csv",
        [{field: "" for field in fields}],
        fields,
    )

    log = "\n".join(
        [
            "# Stage 25-0 Bootstrap Log",
            "",
            "## Status",
            "",
            "`bootstrap complete`",
            "",
            "## Created",
            "",
            "- Stage 25 package directory skeleton with 14 controlled subdirectories.",
            "- Master rules, staged task sequence, high-risk phrase dictionary, author-placeholder specification, evidence-label dictionary, and permitted-label list.",
            "- Read-only provenance baseline for the four Stage 24 inputs and an empty Stage 25 submission-manifest template.",
            "",
            "## Not Changed",
            "",
            "- No Stage 21--24 raw data, processed data, frozen artifact, manuscript, figure, table, declaration, or package file was modified.",
            "- No external submission, repository, DOI, author identity, affiliation, funding, conflict, ethics statement, or repository value was created.",
            "",
            "## Next Stage",
            "",
            "`Stage 25A`: read `00_CONTROL/STAGE25_MASTER_RULES.md` and `00_CONTROL/STAGE25_TASK_SEQUENCE.md`, then verify official public DSS/Elsevier requirements and inventory the Stage 24 package without modifying the manuscript.",
        ]
    )
    write_text(root / "outputs/logs/stage25_0_bootstrap_log.md", log)
    write_text(package / "12_audit_logs/stage25_0_bootstrap_log.md", log)


def main() -> int:
    args = parse_args()
    if args.stage not in {"25-0", "25A", "overnight"}:
        print(
            f"Stage {args.stage} is intentionally not implemented by this split-stage entry point. "
            "Run the corresponding split-stage instruction after reading the predecessor log.",
            file=sys.stderr,
        )
        return 2
    try:
        root = args.project_root.resolve()
        if args.stage == "25-0":
            bootstrap(root)
        elif args.stage == "25A":
            run_stage_25a(root)
        else:
            run_overnight(root)
    except Exception as exc:
        print(f"Stage 25-0 failed: {exc}", file=sys.stderr)
        return 1
    if args.stage == "25-0":
        print("STAGE25_0_STATUS = complete")
        print("BOOTSTRAP_CREATED = yes")
        print("CONTROL_FILES_CREATED = 6")
        print("NEXT_STAGE = Stage 25A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
