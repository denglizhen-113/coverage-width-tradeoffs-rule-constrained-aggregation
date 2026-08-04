"""Focused checks for the high-tier venue and research-upgrade planning stage."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "20_high_tier_upgrade_strategy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("high_tier_upgrade", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_venue_matrix_has_requested_venues_and_does_not_infer_unverified_metrics() -> None:
    module = load_module()
    venues = module.venue_matrix()
    assert len(venues) == 8
    names = set(venues["official_name"])
    assert any("PACMHCI" in name for name in names)
    assert "Scientific Reports" in names
    scientific = venues.loc[venues["official_name"].eq("Scientific Reports")].iloc[0]
    assert scientific["latest_impact_factor"] == "4.9 (2025)"
    assert scientific["JCR_quartile"] == "manual verification needed"
    tcss = venues.loc[venues["official_name"].eq("IEEE Transactions on Computational Social Systems")].iloc[0]
    assert tcss["latest_impact_factor"] == "manual verification needed"


def test_upgrade_plan_has_at_least_five_bounded_modules_and_five_formal_claims() -> None:
    module = load_module()
    modules = module.innovation_modules()
    propositions = module.formal_claims()
    assert len(modules) >= 5
    assert {"M1", "M2", "M3", "M4", "M5"}.issubset(set(modules["module_id"]))
    assert modules["can_be_done_without_new_proprietary_data"].iloc[:5].eq("yes").all()
    assert len(propositions) == 5
    assert propositions["statement"].str.len().gt(40).all()


def test_three_route_reframing_abstracts_are_near_two_hundred_words() -> None:
    module = load_module()
    briefs = module.version_briefs()
    assert len(briefs) == 3
    for brief in briefs:
        assert 170 <= module.word_count(str(brief["abstract"])) <= 230
        assert len(str(brief["keywords"]).split(";")) == 5
