"""Focused checks for specific-journal screening and package assembly."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "18_specific_journal_submission.py"


def load_module():
    spec = importlib.util.spec_from_file_location("specific_submission", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_journal_ranking_is_explicit_and_preserves_scope_limits() -> None:
    module = load_module()
    matrix = module.journal_matrix().set_index("official_journal_name")
    assert matrix.loc["Decision Analysis", "final_recommendation_rank"] == 1
    assert matrix.loc["Group Decision and Negotiation", "final_recommendation_rank"] == 2
    assert matrix.loc["Decision Support Systems", "estimated_fit"] == "weak"
    assert "manual verification needed" in matrix.loc["Decision Analysis", "article_type_requirements"]


def test_reference_plan_only_inserts_verified_complete_doi_rows() -> None:
    module = load_module()
    literature = pd.read_csv(ROOT / "outputs/tables/general_literature_required_sources.csv")
    plan = module.reference_plan(literature)
    inserted = plan.loc[plan["insertion_status"].str.startswith("inserted")]
    assert not inserted.empty
    assert inserted["metadata_check"].eq("pass").all()
    manual = plan.loc[plan["metadata_check"].eq("manual verification needed")]
    assert manual["insertion_status"].eq("not inserted").all()


def test_main_figure_and_table_plan_stays_within_requested_ceiling() -> None:
    module = load_module()
    plan = module.figure_plan()
    main = plan.loc[plan["placement"].eq("main")]
    assert (main["item_type"] == "figure").sum() == 4
    assert (main["item_type"] == "table").sum() == 3
    assert main["proxy_language_safe"].eq("yes").all()
