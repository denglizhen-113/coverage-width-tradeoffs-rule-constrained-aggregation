"""Focused checks for the deterministic overnight pre-submission stage."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "16_overnight_submission.py"


def load_module():
    spec = importlib.util.spec_from_file_location("overnight_submission", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_overnight_abstract_is_safe_and_within_word_limit() -> None:
    module = load_module()
    content = module.title_abstract({})
    abstract = content.split("## Abstract", 1)[1].split("## Keywords", 1)[0]
    assert 180 <= module.word_count(abstract) <= 220
    lowered = content.casefold()
    assert all(phrase not in lowered for phrase in module.FORBIDDEN)


def test_overnight_fit_audit_is_not_cosmetic() -> None:
    module = load_module()
    fit = module.target_fit_rows().set_index("item")
    assert fit.loc["Public/service-sector decision problem", "status"] == "fail"
    assert fit.loc["Need to consider a different venue class", "status"] == "pass"


def test_literature_table_keeps_unverified_directions_out_of_citations() -> None:
    module = load_module()
    table = module.literature_rows()
    verified = table.loc[table["verification_status"].str.contains("Crossref", na=False)]
    unresolved = table.loc[table["verification_status"].str.contains("Manual", na=False)]
    assert len(verified) >= 7
    assert len(unresolved) >= 3
    assert verified["doi_or_stable_url"].str.startswith("https://doi.org/").all()
