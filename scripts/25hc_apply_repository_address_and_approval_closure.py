#!/usr/bin/env python3
"""Apply Stage 25H-C confirmations without creating a repository or uploading anything."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path("submission_package_stage25")
GITHUB_PROFILE_URL = "https://github.com/denglizhen-113"
RECOMMENDED_REPOSITORY_NAME = "rule-aware-dss-expert-crowd"
CORRESPONDING_ADDRESS = (
    "Huazhong University of Science and Technology, 1037 Luoyu Road, "
    "Hongshan District, Wuhan, Hubei 430074, China"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply Stage 25H-C confirmations and record remaining rerun blockers."
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


def verify_frozen_artifacts(root: Path) -> int:
    """Fail before writes if a Stage 21--24 artifact differs from its manifest hash."""
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
            mismatches.append(f"{relative_path or '<missing path>'}: malformed or missing")
            continue
        observed = sha256(target)
        if observed != expected:
            mismatches.append(f"{relative_path}: expected {expected}, observed {observed}")

    if mismatches:
        raise RuntimeError(
            "Frozen Stage 21--24 artifact verification failed; no Stage 25H-C file was written. "
            + "; ".join(mismatches)
        )
    return len(rows)


def replace_required(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    if old not in content:
        raise ValueError(f"Expected Stage 25H-C replacement anchor not found in {path}: {old}")
    write_text(path, content.replace(old, new, 1))


def data_availability_statement() -> str:
    return """# Data Availability Statement

Data availability: The data supporting the findings of this study will be made available in a public GitHub repository before final submission. The repository URL will be added before upload.

GITHUB REPOSITORY URL STILL REQUIRED BEFORE FINAL UPLOAD.

Data license plan: CC BY 4.0.
"""


def code_availability_statement() -> str:
    return """# Code Availability Statement

Code availability: The code used in this study will be made available in the same public GitHub repository before final submission. The repository URL will be added before upload.

GITHUB REPOSITORY URL STILL REQUIRED BEFORE FINAL UPLOAD.

Code license plan: MIT License.
"""


def repository_readiness_checklist() -> str:
    return f"""# GitHub Repository Readiness Checklist: Stage 25H-C

No repository has been created or accessed by this stage. This checklist distinguishes the confirmed account homepage from the still-required concrete publication repository URL.

## Identity and URL

- [x] GitHub account homepage recorded: {GITHUB_PROFILE_URL}
- [ ] Concrete public repository URL: AUTHOR INPUT STILL REQUIRED
- [ ] Public accessibility verified without a signed-in session.
- Recommended repository name: `{RECOMMENDED_REPOSITORY_NAME}`. This is a proposed name only, not evidence that a repository exists.

## Required Repository Contents

- [ ] `README.md` explaining the project, data provenance, and rerun entry points.
- [ ] `LICENSE-CODE-MIT` or `LICENSE` containing the formal MIT code license.
- [ ] `LICENSE-DATA-CC-BY-4.0` or an explicit CC BY 4.0 data-license section in `README.md`.
- [ ] `code/` containing the releasable scripts and modules.
- [ ] `data/` containing only releasable data and required provenance notices.
- [ ] `figures/` or `outputs/` containing the cited reproducible figures/tables.
- [ ] `requirements.txt` or `environment.yml` specifying the runnable environment.
- [ ] `reproduce.md` with end-to-end reproduction instructions.

## Availability and Release Checks

- [x] Code license plan: MIT License.
- [x] Data license plan: CC BY 4.0.
- [ ] Authors confirm that source-data terms permit the planned public release.
- [ ] Data availability statement contains the final concrete repository URL.
- [ ] Code availability statement contains the final concrete repository URL.
- [ ] Reproduction instructions have been executed from a clean environment or the limitations are documented.

The account homepage must not be substituted for the concrete repository URL in the manuscript, declarations, cover letter, or submission portal.
"""


def source_page_count_validation() -> str:
    return """# Stage 25H-C Final Source and Page-Count Validation

## Source-File Decision

- Primary source file: DOCX.
- Backup source file: TEX.
- PDF role: preview/checking only; it is not a submission source file.
- The final DOCX must remain single-column for the selected workflow.

## Page-Count Boundary

The final page count must be obtained from a PDF exported from the final DOCX source and checked against the latest applicable journal and portal requirements. The Stage 25G fallback preview count of 15 pages was generated from a fallback workflow and is not a final editor-validated count.

FINAL_EDITOR_VALIDATED_PAGE_COUNT STILL REQUIRED.

Before the full Stage 25H rerun, authors must export the final DOCX to PDF, inspect pagination and formatting, record the page count, and recheck the final PDF, DOCX, and portal preview for author-identifying metadata.
"""


def final_author_approval_checklist() -> str:
    return """# Final Author Approval Checklist: Stage 25H-C

No explicit all-author approval was provided to Stage 25H-C. Leave every item below unchecked until the named author(s) provide confirmation.

- [ ] Deng Lizhen approved the final title, author order, declarations, and submission package.
- [ ] Liu Yuxin approved the final title, author order, CRediT role, declarations, and submission package.
- [ ] Li Bo approved the final title, author order, CRediT role, declarations, and submission package.
- [ ] All authors approved the corresponding-author designation.
- [ ] All authors approved public GitHub release of data and code.
- [ ] All authors approved the MIT License for code and CC BY 4.0 for data.

CREDIT AUTHOR CONFIRMATION STILL REQUIRED.

FINAL AUTHOR APPROVAL STILL REQUIRED.
"""


def rerun_decision() -> str:
    return """# Stage 25H-C Rerun Decision

## Label

FULL_STAGE25H_RERUN_NOT_ALLOWED_MULTIPLE_BLOCKERS

## Resolved in Stage 25H-C

- Corresponding-author postal address is recorded in the author packet and title-page template.
- GitHub account homepage is recorded but is explicitly not treated as a repository URL.
- MIT code-license and CC BY 4.0 data-license plans remain recorded.
- DOCX remains the primary source, TEX the backup, and PDF preview/checking only.

## Remaining Conditions for a Full Stage 25H Rerun

1. Concrete public GitHub repository URL: AUTHOR INPUT STILL REQUIRED.
2. Final DOCX-exported PDF page count: FINAL_EDITOR_VALIDATED_PAGE_COUNT STILL REQUIRED.
3. CRediT roles confirmed by all authors: AUTHOR INPUT STILL REQUIRED.
4. Final submission package approved by all authors: FINAL AUTHOR APPROVAL STILL REQUIRED.

The author previously reported manual metadata inspection complete, but the final DOCX-exported PDF and the live portal preview still require manual inspection when they exist. No upload is authorized.
"""


def run_log(frozen_count: int) -> str:
    return f"""# Stage 25H-C Run Log

Stage 25H-C applied only the newly confirmed corresponding-author address and re-recorded the confirmed GitHub account homepage, licensing, source-format, AI, and figure-provenance boundaries.

- Corresponding-author full address applied: {CORRESPONDING_ADDRESS}
- GitHub account homepage recorded: {GITHUB_PROFILE_URL}
- Concrete GitHub repository URL: still required; no repository was created or accessed.
- License plan: MIT for code and CC BY 4.0 for data.
- Primary source: DOCX; backup source: TEX; PDF preview/checking only.
- Final editor-validated page count: still required.
- CRediT author confirmation: still required.
- Final author approval: still required.
- Frozen Stage 21-24 artifact verification: {frozen_count}/{frozen_count} SHA-256 entries matched.
- Stage 21-24 artifacts modified: no.
- Upload or external action taken: no.
"""


def run(root: Path) -> int:
    root = root.resolve()
    package = root / PACKAGE
    author_packet = package / "01_author_action_required/AUTHOR_FILL_IN_PACKET_STAGE25F.md"
    title_page = package / "03_title_page/title_page_TEMPLATE_author_input_required.md"
    required = [
        author_packet,
        title_page,
        package / "12_audit_logs/stage25H_B_remaining_blockers_after_final_author_update.md",
        package / "12_audit_logs/stage25_DSS_official_requirements_verified.md",
        package / "11_reproducibility/frozen_artifact_hash_manifest_stage25.csv",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing required Stage 25H-C inputs: " + "; ".join(missing))

    frozen_count = verify_frozen_artifacts(root)

    replace_required(
        author_packet,
        "This packet records the confirmations explicitly provided through Stage 25H-A and Stage 25H-B.",
        "This packet records the confirmations explicitly provided through Stage 25H-A, Stage 25H-B, and Stage 25H-C.",
    )
    replace_required(
        author_packet,
        "- Postal address: AUTHOR INPUT STILL REQUIRED IF THE DSS PORTAL REQUIRES A POSTAL ADDRESS.",
        f"- Postal address: {CORRESPONDING_ADDRESS}\n- Postal address status: author-confirmed for the title page and portal if required.",
    )
    replace_required(
        title_page,
        "**Corresponding author postal address:** AUTHOR INPUT STILL REQUIRED IF THE DSS PORTAL REQUIRES A POSTAL ADDRESS.",
        f"**Corresponding author postal address:** {CORRESPONDING_ADDRESS}",
    )

    declaration_dir = package / "09_declarations"
    repository_dir = package / "10_repository_prepare"
    write_text(declaration_dir / "data_availability_statement_OPTIONS_author_input_required.md", data_availability_statement())
    write_text(declaration_dir / "code_availability_statement_OPTIONS_author_input_required.md", code_availability_statement())
    write_text(repository_dir / "DATA_AVAILABILITY_STATEMENT_OPTIONS.md", data_availability_statement())
    write_text(repository_dir / "CODE_AVAILABILITY_STATEMENT_OPTIONS.md", code_availability_statement())

    author_actions = package / "01_author_action_required"
    audit_logs = package / "12_audit_logs"
    write_text(author_actions / "GITHUB_REPOSITORY_READINESS_CHECKLIST_STAGE25H_C.md", repository_readiness_checklist())
    write_text(author_actions / "FINAL_AUTHOR_APPROVAL_CHECKLIST_STAGE25H_C.md", final_author_approval_checklist())
    write_text(author_actions / "STAGE25H_C_RERUN_DECISION.md", rerun_decision())
    write_text(audit_logs / "stage25H_C_final_source_and_page_count_validation.md", source_page_count_validation())
    write_text(root / "outputs/logs/stage25H_C_run_log.md", run_log(frozen_count))

    print("STAGE25H_C_STATUS = completed_with_warnings")
    print("CORRESPONDING_AUTHOR_FULL_ADDRESS_APPLIED = yes")
    print("GITHUB_ACCOUNT_HOMEPAGE_RECORDED = yes")
    print("CONCRETE_GITHUB_REPOSITORY_URL_STATUS = still_required")
    print("LICENSE_PLAN_STATUS = confirmed")
    print("PRIMARY_SOURCE_FORMAT = DOCX")
    print("BACKUP_SOURCE_FORMAT = TEX")
    print("PDF_ROLE = preview_only")
    print("FINAL_EDITOR_VALIDATED_PAGE_COUNT = STILL_REQUIRED")
    print("CREDIT_AUTHOR_CONFIRMATION = still_required")
    print("FINAL_AUTHOR_APPROVAL = still_required")
    print("RERUN_DECISION = FULL_STAGE25H_RERUN_NOT_ALLOWED_MULTIPLE_BLOCKERS")
    print("UPLOAD_ALLOWED = NO")
    print("STAGE21_24_ARTIFACTS_MODIFIED = no")
    print("UPLOAD_OR_EXTERNAL_ACTION_TAKEN = no")
    print("NEXT_ACTION = Resolve any remaining repository URL, final page count, and author approval blockers, then rerun full Stage 25H.")
    return 0


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(run(args.project_root))
