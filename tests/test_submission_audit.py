"""Focused checks for the deterministic pre-submission audit artifacts."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "15_submission_audit.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("submission_audit", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_revised_abstracts_meet_journal_word_limit() -> None:
    module = load_audit_module()
    version_a, version_b = module.revised_abstracts()
    assert 180 <= module.word_count(version_a) <= 220
    assert 180 <= module.word_count(version_b) <= 220


def test_highlights_are_short_and_safe() -> None:
    module = load_audit_module()
    highlights = module.highlights()
    points = [line.removeprefix("- ") for line in highlights.splitlines() if line.startswith("- ")]
    assert 3 <= len(points) <= 5
    assert all(len(point) <= 85 for point in points)
    lower = highlights.casefold()
    assert "true votes" not in lower
    assert "recovered votes" not in lower
