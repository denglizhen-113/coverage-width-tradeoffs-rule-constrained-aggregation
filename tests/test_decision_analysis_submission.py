"""Focused checks for the Decision Analysis submission-assembly stage."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "19_decision_analysis_submission.py"


def load_module():
    spec = importlib.util.spec_from_file_location("decision_analysis_submission", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_da_abstract_uses_required_structure_safe_language_and_stricter_cap() -> None:
    module = load_module()
    content = module.da_title_abstract()
    audit = module.validate_abstract(content)
    assert 230 <= audit["word_count"] <= 250
    assert not audit["missing_terms"]
    assert not audit["missing_labels"]
    assert not audit["forbidden_hits"]
    assert not audit["formula_markers"]


def test_guideline_checklist_records_stricter_official_abstract_cap() -> None:
    module = load_module()
    checklist = module.guideline_checklist()
    official = checklist.loc[checklist["requirement"].str.contains("Official ScholarOne")].iloc[0]
    discrepancy = checklist.loc[checklist["requirement"].str.contains("300-word versus 250-word")].iloc[0]
    assert official["status"] == "satisfied"
    assert discrepancy["status"] == "manual check still needed"


def test_da_figure_table_plan_has_exact_main_text_ceiling() -> None:
    module = load_module()
    plan = module.da_figure_table_plan()
    main = plan.loc[plan["placement"].eq("main")]
    assert main["item_type"].eq("figure").sum() == 4
    assert main["item_type"].eq("table").sum() == 3
    assert main["safe_language_check"].eq("pass").all()
