from __future__ import annotations

import csv
import hashlib
import importlib.util
import re
from pathlib import Path

import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "26af_figure_rebuild_complexity.py"
GENERATED_OUTPUT = ROOT / "outputs" / "stage26AF"
REFERENCE_OUTPUT = ROOT / "reference" / "stage26AF"
OUTPUT = GENERATED_OUTPUT if GENERATED_OUTPUT.is_dir() else REFERENCE_OUTPUT
FROZEN_X3_SHA256 = "758755b50cd1c059d939fa550ac151c7b55263348e7bb8b55b40e20fff1c2d82"
X1_PREREG_SHA256 = "e437a81b80143b2f03c81b005d463cc489185d7f781214e8446d1e111784257b"
X2_PREREG_SHA256 = "e5418f189061ed295a941327bcf3364081b4095d8b1a1855a416f0431191d19c"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_stage26af():
    spec = importlib.util.spec_from_file_location("stage26af_contract", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def existing_path(generated: str, reference: str) -> Path:
    candidate = ROOT / generated
    return candidate if candidate.is_file() else ROOT / reference


def snapshot_path(row: dict[str, str]) -> Path:
    candidate = ROOT / row["path"]
    if candidate.is_file():
        return candidate
    if row["contract"] == "stage26AF_vector_600dpi":
        relative = Path(row["path"]).relative_to("outputs/stage26AF")
        return REFERENCE_OUTPUT / relative
    name = Path(row["path"]).name
    if row["figure_id"] in {"historical_figure_6", "historical_figure_7"}:
        return ROOT / "reference" / "stage26X-1" / name
    return ROOT / "reference" / "figures" / name


def test_frozen_and_preregistered_boundaries_are_unchanged():
    frozen = existing_path(
        "outputs/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md",
        "reference/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md",
    )
    assert digest(frozen) == FROZEN_X3_SHA256
    assert digest(ROOT / "outputs/stage26X-1/PREREGISTERED_DESIGN.md") == X1_PREREG_SHA256
    assert digest(ROOT / "outputs/stage26X-2/PREREGISTERED_DESIGN.md") == X2_PREREG_SHA256


def test_historical_and_stage26af_snapshot_contracts_coexist():
    with (OUTPUT / "figure_snapshot_manifest.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    historical = [row for row in rows if row["contract"] == "historical_cleanroom_8_png"]
    current = [row for row in rows if row["contract"] == "stage26AF_vector_600dpi"]
    assert len(historical) == 8
    assert len(current) == 8
    assert all("immutable historical evidence" in row["scope"] for row in historical)
    assert all("Stage 26AF presentation contract" in row["scope"] for row in current)
    for row in rows:
        path = snapshot_path(row)
        assert path.is_file()
        assert digest(path) == row["sha256"]

    if GENERATED_OUTPUT.is_dir() and REFERENCE_OUTPUT.is_dir():
        with (REFERENCE_OUTPUT / "figure_snapshot_manifest.csv").open(encoding="utf-8", newline="") as handle:
            reference_rows = list(csv.DictReader(handle))
        generated_hashes = {
            row["figure_id"]: row["sha256"]
            for row in rows
            if row["contract"] == "stage26AF_vector_600dpi"
        }
        reference_hashes = {
            row["figure_id"]: row["sha256"]
            for row in reference_rows
            if row["contract"] == "stage26AF_vector_600dpi"
        }
        assert generated_hashes == reference_hashes


def test_stage26af_delivers_seven_main_figures_and_one_repository_check():
    module = load_stage26af()
    main = OUTPUT / "figures" / "main"
    repository = OUTPUT / "figures" / "repository_diagnostic"
    pngs = sorted(main.glob("Figure_*.png"))
    pdfs = sorted(main.glob("Figure_*.pdf"))
    assert len(pngs) == 7
    assert len(pdfs) == 7
    assert [path.name[:9] for path in pngs] == [f"Figure_{number:02d}" for number in range(1, 8)]
    assert len(list(repository.glob("*.png"))) == 1
    assert len(list(repository.glob("*.pdf"))) == 1

    for png in [*pngs, *repository.glob("*.png")]:
        with Image.open(png) as image:
            dpi = image.info["dpi"]
            assert abs(float(dpi[0]) - 600.0) <= 1.0
            assert abs(float(dpi[1]) - 600.0) <= 1.0
    for pdf in [*pdfs, *repository.glob("*.pdf")]:
        assert module.embedded_pdf_fonts(pdf)


def test_stage26af_manuscript_removes_figure8_and_legacy_positioning():
    manuscript = (OUTPUT / "METHODS_research_draft_STAGE26AF.md").read_text(encoding="utf-8")
    assert "[[FIGURE 8]]" not in manuscript
    assert re.search(r"\bFigure 8\b", manuscript) is None
    assert "Decision Support" not in manuscript
    assert "decision-support" not in manuscript.casefold()
    assert "a real empirical application with hidden truth" not in manuscript
    assert "a longitudinal empirical testbed with latent public preference" in manuscript
    assert len(re.findall(r"^\*\*Figure [1-7]\.", manuscript, flags=re.MULTILINE)) == 7
    assert "### 6.1 Computational complexity and observed execution boundary" in manuscript


def test_figure5_is_a_constant_tracked_result_and_remains_author_gated():
    table_path = existing_path(
        "outputs/tables/rule_robustness_index.csv",
        "reference/stage26AF/source_tables/rule_robustness_index.csv",
    )
    table = pd.read_csv(table_path)
    assert table["supporting_configurations"].equals(table["applicable_configurations"])
    assert table["rule_robustness_index"].eq(1.0).all()
    audit = (OUTPUT / "FIGURE_AUDIT.md").read_text(encoding="utf-8")
    assert "NO_INFORMATION_BEYOND_TABLE" in audit
    assert "AUTHOR_DECISION_REQUIRED" in audit
    assert "Stage 26AF does not remove Figure 5" in audit


def test_post_edit_claim_and_reference_gates_pass():
    claim_report = (OUTPUT / "POST_EDIT_CLAIM_RECHECK.md").read_text(encoding="utf-8")
    numbering = (OUTPUT / "FIGURE_RENUMBERING_CHECK.md").read_text(encoding="utf-8")
    assert "INTEGRITY_PASS` (24/24)" in claim_report
    assert "No `CLAIM_DRIFT_DETECTED` condition was observed" in claim_report
    assert "PASS_NO_DANGLING_FIGURE_REFERENCE" in numbering
    assert "DANGLING_FIGURE_REFERENCE:" not in numbering
