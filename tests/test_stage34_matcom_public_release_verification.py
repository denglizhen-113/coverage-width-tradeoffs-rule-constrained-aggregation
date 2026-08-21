from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "34_matcom_public_release_verification.py"
REPORT = ROOT / "outputs" / "stage34-matcom-public-release-verification" / "PUBLIC_RELEASE_V101_VERIFICATION.md"


def load_module():
    spec = importlib.util.spec_from_file_location("stage34_release_verification", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stage34_report_records_versioned_release_without_claiming_a_doi() -> None:
    module = load_module()
    report = REPORT.read_text(encoding="utf-8")
    assert module.TAG in report
    assert module.COMMIT in report
    assert module.SHA256 in report
    assert "F01A_PUBLIC_VERSIONED_RELEASE=PASS" in report
    assert "F01B: persistent archive DOI | EXTERNAL_GATE" in report
    assert "DO_NOT_SUBMIT" in report
