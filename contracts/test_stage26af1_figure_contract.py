from __future__ import annotations

import hashlib
import importlib.util
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "26af1_figure5_conversion.py"
GENERATED = ROOT / "outputs" / "stage26AF-1"
REFERENCE = ROOT / "reference" / "stage26AF-1"
OUTPUT = GENERATED if GENERATED.is_dir() else REFERENCE
GENERATED_AF = ROOT / "outputs" / "stage26AF"
REFERENCE_AF = ROOT / "reference" / "stage26AF"
STAGE26AF = GENERATED_AF if GENERATED_AF.is_dir() else REFERENCE_AF
FROZEN_X3_SHA256 = "758755b50cd1c059d939fa550ac151c7b55263348e7bb8b55b40e20fff1c2d82"
X1_PREREG_SHA256 = "e437a81b80143b2f03c81b005d463cc489185d7f781214e8446d1e111784257b"
X2_PREREG_SHA256 = "e5418f189061ed295a941327bcf3364081b4095d8b1a1855a416f0431191d19c"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def existing_path(generated: str, reference: str) -> Path:
    candidate = ROOT / generated
    return candidate if candidate.is_file() else ROOT / reference


def load_stage26af1():
    spec = importlib.util.spec_from_file_location("stage26af1_contract", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stage26af1_help_and_protected_boundaries():
    module = load_stage26af1()
    assert SCRIPT.is_file()
    assert callable(module.parse_args)
    frozen = existing_path(
        "outputs/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md",
        "reference/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md",
    )
    assert digest(frozen) == FROZEN_X3_SHA256
    assert digest(ROOT / "outputs/stage26X-1/PREREGISTERED_DESIGN.md") == X1_PREREG_SHA256
    assert digest(ROOT / "outputs/stage26X-2/PREREGISTERED_DESIGN.md") == X2_PREREG_SHA256


def test_stage26af1_delivers_six_main_and_two_repository_figures():
    module = load_stage26af1()
    base = module.load_stage26af(ROOT)
    main = OUTPUT / "figures" / "main"
    repository = OUTPUT / "figures" / "repository_diagnostic"
    pngs = sorted(main.glob("Figure_*.png"))
    pdfs = sorted(main.glob("Figure_*.pdf"))
    assert len(pngs) == len(pdfs) == 6
    assert [path.name[:9] for path in pngs] == [f"Figure_{number:02d}" for number in range(1, 7)]
    assert {path.stem for path in repository.glob("*.png")} == {
        "Artifact_Check_evidence_completeness",
        "RRI_Record_predeclared_conclusions",
    }
    assert len(list(repository.glob("*.pdf"))) == 2
    for png in [*pngs, *repository.glob("*.png")]:
        with Image.open(png) as image:
            dpi = image.info["dpi"]
            assert abs(float(dpi[0]) - 600.0) <= 1.0
            assert abs(float(dpi[1]) - 600.0) <= 1.0
    for pdf in [*pdfs, *repository.glob("*.pdf")]:
        assert base.embedded_pdf_fonts(pdf)


def test_stage26af1_manuscript_has_table9_record_and_consistent_numbering():
    manuscript = (OUTPUT / "METHODS_research_draft_STAGE26AF1.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^\*\*Figure [1-6]\. ", manuscript, flags=re.MULTILINE)) == 6
    assert re.findall(r"\[\[FIGURE ([1-6])\]\]", manuscript) == [str(number) for number in range(1, 7)]
    assert re.search(r"\bFigure [78]\b|\[\[FIGURE [78]\]\]", manuscript) is None
    assert "Figure 5. Rule Robustness Index" not in manuscript
    assert manuscript.count("| CE10 |") == 1
    assert "4/4 predeclared conclusions have RRI 1.000" in manuscript
    assert "C1 1/1; C2 4/4; C3 4/4; C4 1/1" in manuscript
    assert "rule_robustness_index.csv" in manuscript


def test_stage26af1_reports_and_retained_hashes_pass():
    contract = (OUTPUT / "FIGURE_CONTRACT_UPDATE.md").read_text(encoding="utf-8")
    numbering = (OUTPUT / "FINAL_FIGURE_RENUMBERING.md").read_text(encoding="utf-8")
    claims = (OUTPUT / "POST_EDIT_CLAIM_RECHECK.md").read_text(encoding="utf-8")
    conversion = (OUTPUT / "FIGURE5_CONVERSION.md").read_text(encoding="utf-8")
    assert "PASS_6_MAIN_PLUS_2_REPOSITORY_DIAGNOSTICS" in contract
    assert "PASS_HISTORICAL_8_OF_8_UNCHANGED" in contract
    assert "PASS_RETAINED_FIGURE_HASHES_UNCHANGED" in contract
    assert "PASS_NO_DANGLING_FIGURE_REFERENCE" in numbering
    assert "INTEGRITY_PASS` (24/24)" in claims
    assert "No `CLAIM_DRIFT_DETECTED` condition was observed" in claims
    assert "No value was recalculated or added" in conversion

    pairs = {
        STAGE26AF / "figures/main/Figure_01_rule_conditioned_inference_architecture.png": OUTPUT / "figures/main/Figure_01_rule_conditioned_inference_architecture.png",
        STAGE26AF / "figures/main/Figure_02_reproducible_comparison_workflow.png": OUTPUT / "figures/main/Figure_02_reproducible_comparison_workflow.png",
        STAGE26AF / "figures/main/Figure_03_discretion_identifiability_frontier.png": OUTPUT / "figures/main/Figure_03_discretion_identifiability_frontier.png",
        STAGE26AF / "figures/main/Figure_04_compatible_disclosure_scenarios.png": OUTPUT / "figures/main/Figure_04_compatible_disclosure_scenarios.png",
        STAGE26AF / "figures/main/Figure_05_rule_robustness_index.png": OUTPUT / "figures/repository_diagnostic/RRI_Record_predeclared_conclusions.png",
        STAGE26AF / "figures/main/Figure_06_multiseed_internal_sensitivity.png": OUTPUT / "figures/main/Figure_05_multiseed_internal_sensitivity.png",
        STAGE26AF / "figures/main/Figure_07_multiseed_external_sensitivity.png": OUTPUT / "figures/main/Figure_06_multiseed_external_sensitivity.png",
        STAGE26AF / "figures/repository_diagnostic/Artifact_Check_evidence_completeness.png": OUTPUT / "figures/repository_diagnostic/Artifact_Check_evidence_completeness.png",
    }
    assert all(digest(source) == digest(destination) for source, destination in pairs.items())
