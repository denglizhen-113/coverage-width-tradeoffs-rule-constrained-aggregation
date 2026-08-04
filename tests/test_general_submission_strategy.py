"""Focused checks for the deterministic general submission strategy stage."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "17_general_submission_strategy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("general_submission", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_general_abstract_is_within_limit_and_uses_safe_language() -> None:
    module = load_module()
    content = module.title_abstract_general()
    abstract = content.split("## Abstract", 1)[1].split("## Keywords", 1)[0]
    assert 180 <= module.word_count(abstract) <= 220
    lowered = content.casefold()
    assert all(phrase not in lowered for phrase in module.FORBIDDEN)


def test_general_target_matrix_redirects_away_from_public_planning() -> None:
    module = load_module()
    matrix = module.journal_type_matrix().set_index("journal_type")
    assert matrix.loc["Decision analysis / decision sciences", "fit"] == "strong"
    assert matrix.loc["Public sector / socio-economic planning", "fit"] == "weak"
    assert matrix.loc["Public sector / socio-economic planning", "extra_public_service_application_required"] == "yes"


def test_literature_map_has_verified_sources_for_core_general_directions() -> None:
    module = load_module()
    literature = module.literature_rows()
    verified = literature.loc[literature["verified"].eq("yes")]
    expected = {
        "Partial identification and bounds",
        "Social choice theory",
        "Rank aggregation",
        "Preference inference",
        "Expert-crowd / collective decision-making",
        "Decision-making under uncertainty",
        "Prediction as validation",
        "Mechanism design / institutional discretion",
        "Empirical competition/platform testbeds",
    }
    assert expected.issubset(set(verified["direction"]))
    assert verified["doi_or_stable_url"].str.startswith("https://doi.org/").all()
