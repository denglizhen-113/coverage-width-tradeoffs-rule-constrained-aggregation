from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "33_matcom_reviewer_preflight.py"
OUTPUT = ROOT / "outputs" / "stage33-matcom-reviewer-preflight"


def load_module():
    spec = importlib.util.spec_from_file_location("stage33_preflight", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stage33_report_preserves_submission_block_and_local_evidence() -> None:
    module = load_module()
    report = (OUTPUT / "MATCOM_REVIEWER_PREFLIGHT_REPORT.md").read_text(encoding="utf-8")
    findings = (OUTPUT / "MATCOM_REVIEWER_FINDINGS.csv").read_text(encoding="utf-8")
    assert "`DO_NOT_SUBMIT`" in report
    assert "Stage 32 corrected package" in report
    assert "0.117600" in report
    assert "Office Math" in report
    assert "P0" in report and "EXTERNAL_GATE" in report
    assert "F02,P0,EXTERNAL_GATE" in findings
    assert "F01,P1,PASS" in findings
    assert module.PACKAGE.as_posix() in report
