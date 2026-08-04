#!/usr/bin/env python3
"""Stop Stage 25H safely when author-only input remains incomplete."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path("submission_package_stage25")

REQUIRED_ITEMS = [
    ("H01", "Author names", "Author list and order"),
    ("H02", "Author order", "Author list and order"),
    ("H03", "Affiliations", "Affiliations"),
    ("H04", "Corresponding author", "Corresponding author"),
    ("H05", "Corresponding author email", "Corresponding author"),
    ("H06", "Funding statement", "Funding"),
    ("H07", "Competing interests", "Competing interests"),
    ("H08", "CRediT roles", "CRediT author contributions"),
    ("H09", "Ethics statement", "Ethics statement"),
    ("H10", "Data availability statement", "Data availability"),
    ("H11", "Code availability statement", "Code availability"),
    ("H12", "Repository route", "Repository choice"),
    ("H13", "Repository license", "License choice"),
    ("H14", "Repository DOI or URL if available", "Repository/data/code availability"),
    ("H15", "AI declaration", "Generative-AI declaration"),
    ("H16", "Figure provenance confirmation", "Figure provenance"),
    ("H17", "Final page count", "Final page count"),
    ("H18", "Final author approval", "Final approval statement"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Stage 25H author-input gate without uploading or modifying frozen artifacts."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content.strip() + "\n", encoding="utf-8")
    temporary.replace(path)


def markdown_table(rows: list[dict[str, str]], fields: list[str]) -> str:
    header = "| " + " | ".join(fields) + " |"
    separator = "| " + " | ".join("---" for _ in fields) + " |"
    body = [
        "| " + " | ".join(str(row.get(field, "")).replace("|", "/") for field in fields) + " |"
        for row in rows
    ]
    return "\n".join([header, separator, *body])


def run(root: Path) -> int:
    root = root.resolve()
    package = root / PACKAGE
    packet = package / "01_author_action_required/AUTHOR_FILL_IN_PACKET_STAGE25F.md"
    if not packet.is_file():
        raise FileNotFoundError(f"Missing required Stage 25H author packet: {packet}")
    content = packet.read_text(encoding="utf-8")
    placeholders = sorted(set(re.findall(r"\[[^\]\n]+\]", content)))
    incomplete = bool(placeholders)
    if not incomplete:
        raise RuntimeError(
            "The author packet no longer contains placeholders. This controlled early-stop entry point "
            "must be replaced by the full author-confirmed Stage 25H consistency workflow."
        )

    fields = ["item_id", "required_item", "packet_section", "status", "evidence", "required_action"]
    rows = [
        {
            "item_id": item_id,
            "required_item": item,
            "packet_section": section,
            "status": "AUTHOR INPUT STILL REQUIRED.",
            "evidence": "The Stage 25F author fill-in packet retains unselected bracketed placeholder fields.",
            "required_action": "Authors must provide or explicitly approve the applicable statement; Codex must not infer it.",
        }
        for item_id, item, section in REQUIRED_ITEMS
    ]
    completion_report = package / "12_audit_logs/stage25H_author_fill_in_completion_check.md"
    incomplete_report = package / "12_audit_logs/stage25H_incomplete_author_input_report.md"
    completion_content = "\n".join([
        "# Stage 25H Author Fill-In Completion Check",
        "",
        "## Gate Result",
        "",
        "Author fill-in packet status: INCOMPLETE.",
        "",
        f"Detected unselected placeholder values: {len(placeholders)}.",
        "",
        markdown_table(rows, fields),
        "",
        "## Mandatory Stop",
        "",
        "AUTHOR INPUT STILL REQUIRED.",
        "",
        "Stage 25H stops at this gate. The final anonymization consistency check, title-page separation check, declaration consistency check, and final source/PDF validation are not rerun because author-side facts and confirmations are unavailable.",
    ])
    write_text(completion_report, completion_content)
    write_text(
        incomplete_report,
        "\n".join([
            "# Stage 25H Incomplete Author Input Report",
            "",
            "The author fill-in packet has not been completed. This is a required stopping condition.",
            "",
            "Missing or unconfirmed author-side categories:",
            "",
            *[f"- {item}: AUTHOR INPUT STILL REQUIRED." for _, item, _ in REQUIRED_ITEMS],
            "",
            "No author facts, declaration choices, repository route, license, DOI/URL, AI statement, final page-count confirmation, or approval has been inferred.",
            "",
            "No Stage 21-24 artifact was modified. No upload or external action was taken.",
        ]),
    )

    go_no_go = package / "01_author_action_required/STAGE25H_FINAL_GO_NO_GO.md"
    write_text(
        go_no_go,
        "\n".join([
            "# Stage 25H Final Go/No-Go Decision",
            "",
            "## Final Label",
            "",
            "NOT_READY_AUTHOR_INPUT_MISSING",
            "",
            "## Decision",
            "",
            "The author fill-in packet remains incomplete. Required author names, affiliations, correspondence details, declarations, repository route, AI/figure provenance confirmation, final page-count confirmation, and final author approval are not available. The Stage 25H gate therefore stops before any final consistency certification.",
            "",
            "## Upload",
            "",
            "UPLOAD_ALLOWED = NO_AUTOMATED_UPLOAD",
            "",
            "No automated or external upload is authorized. After all author-side entries are complete, rerun a full Stage 25H consistency check before any manual portal entry.",
        ]),
    )
    run_log = root / "outputs/logs/stage25H_run_log.md"
    write_text(
        run_log,
        "\n".join([
            "# Stage 25H Run Log",
            "",
            "Stage 25H stopped at the required author-input completion gate.",
            "",
            f"- Placeholder values detected in author fill-in packet: {len(placeholders)}.",
            f"- Required author-side categories still unconfirmed: {len(REQUIRED_ITEMS)}.",
            "- Later Stage 25H checks were not run, as required when the packet is incomplete.",
            "- Stage 21-24 artifacts modified: no.",
            "- Upload or external action taken: no.",
            "",
            "Final label: NOT_READY_AUTHOR_INPUT_MISSING.",
            "Upload allowed: NO_AUTOMATED_UPLOAD.",
        ]),
    )

    print("STAGE25H_STATUS = completed_with_warnings")
    print("FINAL_GO_NO_GO_LABEL = NOT_READY_AUTHOR_INPUT_MISSING")
    print("UPLOAD_ALLOWED = NO_AUTOMATED_UPLOAD")
    print("AUTHOR_FILL_IN_COMPLETE = no")
    print("DECLARATIONS_CONSISTENT = no")
    print("ANONYMIZED_MANUSCRIPT_CLEAR = no")
    print("MANUAL_METADATA_CHECK_CONFIRMED = no")
    print("FINAL_EDITABLE_SOURCE_CONFIRMED = no")
    print("FINAL_PDF_CONFIRMED = no")
    print("FINAL_PAGE_COUNT = NOT_CONFIRMED")
    print("REPOSITORY_ROUTE_CONFIRMED = no")
    print("DATA_CODE_AI_STATEMENTS_CONFIRMED = no")
    print("STAGE21_24_ARTIFACTS_MODIFIED = no")
    print("UPLOAD_OR_EXTERNAL_ACTION_TAKEN = no")
    print(f"FINAL_GO_NO_GO_REPORT = {go_no_go}")
    print("NEXT_ACTION = If and only if all fields are confirmed, authors may manually enter the DSS submission portal and perform a final live portal check before upload.")
    return 0


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(run(args.project_root))
