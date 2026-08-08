"""Audit the current research evidence and build a non-frozen corrected draft."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd


FINAL_TITLE = "Coverage-Width Tradeoffs in Rule-Constrained Expert-Crowd Aggregation"
SOURCE_MANUSCRIPT = Path(
    "outputs/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md"
)
SOURCE_MANUSCRIPT_SHA256 = (
    "758755b50cd1c059d939fa550ac151c7b55263348e7bb8b55b40e20fff1c2d82"
)
DEFAULT_OUTPUT_DIR = Path("outputs/stage26AC")
COMAP_PAGE = (
    "https://contest.comap.com/undergraduate/contests/mcm/contests/2026/"
    "problems/index.html"
)
COMAP_CSV = (
    "https://contest.comap.com/undergraduate/contests/mcm/contests/2026/"
    "problems/2026_MCM_Problem_C_Data.csv"
)
COMAP_SHA256 = (
    "ea99caec6ea243bdb450a1971a95ba8a95701a93be7ff29f0ba3c57d72ddff52"
)
REPOSITORY_URL = (
    "https://github.com/denglizhen-113/"
    "coverage-width-tradeoffs-rule-constrained-aggregation"
)


class AuditError(RuntimeError):
    """Raised when required audit evidence is missing or inconsistent."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reconcile manuscript claims against tracked evidence and generate a "
            "corrected, non-frozen Stage 26AC research draft and detailed audit."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Project root (default: current directory).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Project-relative output directory (default: outputs/stage26AC).",
    )
    parser.add_argument(
        "--pytest-junit",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "pytest_results.xml",
        help="Project-relative pytest JUnit XML used as current test evidence.",
    )
    parser.add_argument(
        "--staging-pytest-junit",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "staging_pytest_results.xml",
        help=(
            "Project-relative pytest JUnit XML from a direct staged-package test "
            "run (default: outputs/stage26AC/staging_pytest_results.xml)."
        ),
    )
    return parser.parse_args(argv)


def require_file(root: Path, relative: Path | str) -> Path:
    path = root / Path(relative)
    if not path.is_file():
        raise AuditError(f"Required file is missing: {path}")
    return path


def require_dir(root: Path, relative: Path | str) -> Path:
    path = root / Path(relative)
    if not path.is_dir():
        raise AuditError(f"Required directory is missing: {path}")
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_data_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            next(reader)
        except StopIteration as exc:
            raise AuditError(f"CSV is empty: {path}") from exc
        return sum(1 for _ in reader)


def as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series.dtype):
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().eq("true")


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def collect_raw_evidence(root: Path) -> dict[str, object]:
    x1_dir = require_dir(root, "outputs/stage26X-1/raw")
    x1_files = sorted(x1_dir.glob("*.csv"))
    if len(x1_files) != 300:
        raise AuditError(f"Expected 300 Stage 26X-1 raw CSVs, found {len(x1_files)}")

    x1_rows = 0
    x1_cases = 0
    seeds: set[int] = set()
    regions: set[tuple[object, ...]] = set()
    width_below = 0
    positive_noise_cells = 0
    positive_noise_coverage_losses = 0
    coverage_loss_values: list[float] = []

    for path in x1_files:
        frame = pd.read_csv(path)
        x1_rows += len(frame)
        x1_cases += int(frame["replication"].nunique())
        seeds.add(int(frame["seed"].iloc[0]))
        synthesizer = str(frame["synthesizer"].iloc[0])
        method_means = frame.groupby("method", sort=False)[["coverage", "width"]].mean()

        if synthesizer == "internal_percentage":
            n_active = int(frame["n_active"].iloc[0])
            noise = float(frame["outcome_noise_probability"].iloc[0])
            regions.add((synthesizer, n_active, noise))
            aware = "rule_aware_partial_identification"
            comparator = "rule_agnostic_partial_identification"
            if method_means.loc[aware, "width"] < method_means.loc[comparator, "width"]:
                width_below += 1
            if noise > 0:
                positive_noise_cells += 1
                loss = float(
                    method_means.loc[comparator, "coverage"]
                    - method_means.loc[aware, "coverage"]
                )
                coverage_loss_values.append(loss)
                if loss > 0:
                    positive_noise_coverage_losses += 1
        elif synthesizer == "external_ordinal":
            n_candidates = int(frame["n_candidates"].iloc[0])
            n_rounds = int(frame["n_rounds"].iloc[0])
            regions.add((synthesizer, n_candidates, n_rounds))
            aware = "rule_aware_discretion"
            comparator = "rule_agnostic_ordinal"
            if method_means.loc[aware, "width"] < method_means.loc[comparator, "width"]:
                width_below += 1
        else:
            raise AuditError(f"Unexpected Stage 26X-1 synthesizer in {path}: {synthesizer}")

    x2_counts: dict[str, dict[str, int]] = {}
    for class_name in ("max_entropy", "bayesian", "ablation"):
        class_dir = require_dir(root, f"outputs/stage26X-2/raw/{class_name}")
        files = sorted(class_dir.glob("*.csv"))
        x2_counts[class_name] = {
            "files": len(files),
            "rows": sum(csv_data_rows(path) for path in files),
        }

    insufficient = 0
    for path in sorted((root / "outputs/stage26X-2/raw/bayesian").glob("*.csv")):
        status = pd.read_csv(path, usecols=["posterior_status"])["posterior_status"]
        insufficient += int(status.ne("ok").sum())

    return {
        "x1_files": len(x1_files),
        "x1_rows": x1_rows,
        "x1_cases": x1_cases,
        "seeds": len(seeds),
        "regions": len(regions),
        "width_below": width_below,
        "positive_noise_cells": positive_noise_cells,
        "positive_noise_coverage_losses": positive_noise_coverage_losses,
        "positive_noise_mean_loss": sum(coverage_loss_values)
        / len(coverage_loss_values),
        "x2_counts": x2_counts,
        "x2_rows": sum(item["rows"] for item in x2_counts.values()),
        "x2_files": sum(item["files"] for item in x2_counts.values()),
        "combined_rows": x1_rows
        + sum(item["rows"] for item in x2_counts.values()),
        "combined_files": len(x1_files)
        + sum(item["files"] for item in x2_counts.values()),
        "insufficient_posterior": insufficient,
    }


def collect_summary_evidence(root: Path) -> dict[str, object]:
    pairwise = pd.read_csv(
        require_file(root, "outputs/stage26X-2/tables/attribution_pairwise_cells.csv")
    )
    clean = pairwise.loc[as_bool(pairwise["clean_cell"])].copy()

    ablation = pd.read_csv(
        require_file(root, "outputs/stage26X-2/tables/ablation_paired_effects.csv")
    )
    internal = ablation.loc[
        ablation["synthesizer"].eq("internal_percentage")
        & ablation["configuration"].eq("internal_without_elimination")
    ].copy()
    positive = internal.loc[internal["outcome_noise_probability"].gt(0)]
    clean_ablation = internal.loc[internal["outcome_noise_probability"].eq(0)]

    panel = pd.read_csv(require_file(root, "data/processed/panel_long.csv"))
    features = pd.read_csv(
        require_file(root, "data/processed/identification_features_long.csv")
    )
    constraints = pd.read_csv(
        require_file(root, "outputs/tables/constraint_summary.csv")
    )
    p_constraints = constraints.loc[constraints["regime"].eq("P")]

    ranking_r = pd.read_csv(
        require_file(root, "outputs/tables/ranking_identification_summary_r.csv")
    )
    ranking_rplus = pd.read_csv(
        require_file(root, "outputs/tables/ranking_identification_summary_rplus.csv")
    )
    r_sampled = ranking_r.loc[ranking_r["enumeration_method"].eq("monte_carlo")]
    rplus_sampled = ranking_rplus.loc[
        ranking_rplus["enumeration_method"].eq("monte_carlo")
    ]

    return {
        "clean_pairwise": len(clean),
        "aware_pareto": int(as_bool(clean["aware_pareto_dominates"]).sum()),
        "bayesian_pareto": int(as_bool(clean["bayesian_pareto_dominates"]).sum()),
        "positive_ablation_cells": len(positive),
        "positive_ablation_coverage_improved": int(
            as_bool(positive["coverage_improved"]).sum()
        ),
        "ablation_coverage_change": float(positive["coverage_change"].mean()),
        "ablation_width_change": float(positive["width_change"].mean()),
        "clean_ablation_cells": len(clean_ablation),
        "clean_ablation_changed": int(
            clean_ablation["coverage_change"].abs().gt(1e-12).sum()
        ),
        "panel_rows": len(panel),
        "feature_rows": len(features),
        "typed_proxy_rows": int(features["public_appeal_proxy"].notna().sum()),
        "p_weeks": len(p_constraints),
        "p_feasible": int(p_constraints["feasible"].eq(True).sum()),
        "r_exact": int(ranking_r["enumeration_method"].eq("exact").sum()),
        "r_sampled": len(r_sampled),
        "r_sample_draws": sorted(
            int(value) for value in r_sampled["n_evaluated_permutations"].unique()
        ),
        "rplus_exact": int(ranking_rplus["enumeration_method"].eq("exact").sum()),
        "rplus_sampled": len(rplus_sampled),
        "rplus_sample_draws": sorted(
            int(value)
            for value in rplus_sampled["n_evaluated_permutations"].unique()
        ),
        "max_mcse": float(
            max(ranking_r["mc_standard_error"].max(), ranking_rplus["mc_standard_error"].max())
        ),
    }


def parse_pytest_junit(root: Path, path: Path) -> dict[str, object]:
    junit = require_file(root, path)
    xml_root = ET.parse(junit).getroot()
    suites = [xml_root] if xml_root.tag == "testsuite" else list(xml_root.findall("testsuite"))
    result: dict[str, object] = {
        key: sum(int(suite.attrib.get(key, "0")) for suite in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    result["failed_testcases"] = [
        f"{case.attrib.get('classname', '<unknown>')}::{case.attrib.get('name', '<unknown>')}"
        for suite in suites
        for case in suite.iter("testcase")
        if case.find("failure") is not None or case.find("error") is not None
    ]
    return result


def collect_test_scope(root: Path) -> dict[str, object]:
    root_tests = {
        path.name for path in require_dir(root, "tests").glob("test_*.py")
    }
    staging_tests = {
        path.name
        for path in require_dir(
            root, "outputs/stage26AA/repo_staging/tests"
        ).glob("test_*.py")
    }
    return {
        "root_count": len(root_tests),
        "staging_count": len(staging_tests),
        "staging_omissions": sorted(root_tests - staging_tests),
        "staging_only": sorted(staging_tests - root_tests),
    }


def exact_replacements(text: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise AuditError(
                f"Expected exactly one manuscript occurrence, found {count}: {old[:80]!r}"
            )
        text = text.replace(old, new)
    return text


def renumber_body_citations(body: str) -> str:
    mapping = {old: old - 2 for old in range(3, 15)}

    def replace(match: re.Match[str]) -> str:
        old_numbers = [int(value) for value in match.group(1).split(",")]
        if any(value not in mapping for value in old_numbers):
            raise AuditError(f"Unexpected cited reference in manuscript body: {match.group(0)}")
        return "[" + ",".join(str(mapping[value]) for value in old_numbers) + "]"

    return re.sub(r"\[([0-9]+(?:,[0-9]+)*)\]", replace, body)


def build_revised_manuscript(source: str) -> tuple[str, dict[str, int]]:
    if "## References\n" not in source:
        raise AuditError("Source manuscript has no References heading")
    body, reference_tail = source.split("## References\n", maxsplit=1)
    if "\n## Figure Captions\n" not in reference_tail:
        raise AuditError("Source manuscript has no Figure Captions heading")
    references_text, tail = reference_tail.split("\n## Figure Captions\n", maxsplit=1)

    old_abstract = body.split("## Abstract\n\n", 1)[1].split("\n\n**Keywords:**", 1)[0]
    new_abstract = (
        "Institutional aggregation often reveals expert scores, ranks, eliminations, "
        "or final outcomes while leaving public preferences latent. We formulate "
        "rule-conditioned feasible sets: percentage rules produce cardinal support "
        "intervals, whereas ranking and judge-save rules produce ordinal feasible-ranking "
        "sets under explicit tie and discretion assumptions. Twenty preregistered seeds "
        "cover 12 internal parameter regions and three external rule structures, yielding "
        "67,200 synthetic cases and 552,000 retained method-level rows across sensitivity, "
        "same-information baseline, and component-ablation runs. Rule-aware width is below "
        "the rule-agnostic comparator in 300/300 cells, as implied by the set nesting in "
        "Proposition 2 rather than an independent performance gain. Positive outcome noise "
        "lowers rule-aware coverage in 180/180 internal cells by a mean 0.050289. Removing "
        "the elimination constraint restores 0.050289 coverage while increasing width by "
        "0.163131; clean-cell coverage is unchanged. In clean same-information comparisons, "
        "rule-aware intervals Pareto-dominate Bayesian intervals in 0/120 cells, whereas "
        "Bayesian intervals dominate in 14/120, all in the external seven-candidate, "
        "three-round region. The contribution is a bounded method-selection criterion, not "
        "a claim of uniform method superiority or observed user effects."
    )

    body = exact_replacements(
        body,
        [
            (
                "# Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences",
                f"# {FINAL_TITLE}",
            ),
            (old_abstract, new_abstract),
            (
                "Small fields are enumerated exactly. Larger fields use 10,000 fixed-seed uniform permutations. In the empirical runs, R has 13 exact and 1 sampled week; R-plus has 36 exact and 37 sampled weeks. The maximum reported Monte Carlo standard error for feasible fractions is approximately 0.005. This is numerical approximation error, not uncertainty about public behaviour.",
                "Small fields are enumerated exactly. In the empirical runs, the one sampled R week uses 50,000 fixed-seed uniform permutations, while each of the 37 sampled R-plus weeks uses 10,000; R has 13 exact weeks and R-plus has 36. The maximum reported Monte Carlo standard error for feasible fractions is approximately 0.005. This is numerical approximation error, not uncertainty about public behaviour.",
            ),
            (
                "Partial identification retains all latent states compatible with incomplete observations rather than selecting one unsupported state [8,9]. Decision criteria such as minimax regret illustrate why unresolved states may remain decision-relevant [10]. Institutional discretion changes what an outcome reveals, so it must enter the observation rule rather than be treated as an after-the-fact correction [14]. Transparency research also cautions that disclosure is not synonymous with accountability or measured organizational benefit [12,13]. Accordingly, this paper evaluates disclosure as compatible constraint addition and reports privacy, cost, and accountability terms only as design considerations unless empirical evidence exists.",
                "Institutional discretion changes what an outcome reveals, so it must enter the observation rule rather than be treated as an after-the-fact correction [14]. Transparency research also cautions that disclosure is not synonymous with accountability or measured organizational benefit [12,13]. Accordingly, this paper evaluates disclosure as compatible constraint addition and reports privacy, cost, and accountability terms only as design considerations unless empirical evidence exists.",
            ),
            (
                "The processed longitudinal panel contains 4,199 contestant-week records before identification-specific availability restrictions.",
                "The empirical testbed uses the official COMAP 2026 MCM Problem C data file, Data With The Stars [[COMAP_SOURCE]]. The processed longitudinal panel contains 4,199 contestant-week records before identification-specific availability restrictions.",
            ),
            (
                "## Data and Code Availability for Anonymized Review\n\nThe data and code supporting the findings of this study are available in a public repository. Repository details are supplied in the title page/submission metadata and will be fully disclosed after peer review according to journal requirements.",
                f"## Data and Code Availability\n\nThe empirical source is the official COMAP 2026 MCM Problem C data file [[COMAP_SOURCE]], anonymously downloadable from the official problem page and byte-matched to SHA-256 `EA99CAEC6EA243BDB450A1971A95BA8A95701A93BE7FF29F0BA3C57D72DDFF52`. COMAP states that its material may be reproduced for academic/research purposes; the source is attributed and is not relicensed by this study. The code, fixed seed list, configurations, source-data copy, and audit artifacts are prepared at {REPOSITORY_URL}. At this audit stage the repository remains private; public availability may be claimed only after the author-controlled release and an anonymous URL, raw-file, and clone verification.",
            ),
        ],
    )

    body = renumber_body_citations(body)
    if body.count("[[COMAP_SOURCE]]") != 2:
        raise AuditError("Expected two COMAP citation placeholders in revised body")
    body = body.replace("[[COMAP_SOURCE]]", "[13]")

    references: dict[int, str] = {}
    for match in re.finditer(r"^\[([0-9]+)\] (.+)$", references_text, flags=re.MULTILINE):
        references[int(match.group(1))] = match.group(2).strip()
    if sorted(references) != list(range(1, 16)):
        raise AuditError("Source reference list is not the expected 1-15 sequence")

    revised_references = [
        f"[{old - 2}] {references[old]}" for old in range(3, 15)
    ]
    revised_references.append(
        "[13] COMAP, 2026 MCM Problem C: Data With The Stars, The Consortium "
        f"for Mathematics and Its Applications, 2026. {COMAP_PAGE} "
        "(accessed 2026-08-08)."
    )

    revised = (
        body.rstrip()
        + "\n\n## References\n\n"
        + "\n\n".join(revised_references)
        + "\n\n## Figure Captions\n"
        + tail.lstrip()
    )

    cited = {
        int(value)
        for match in re.finditer(r"\[([0-9]+(?:,[0-9]+)*)\]", body)
        for value in match.group(1).split(",")
    }
    listed = set(range(1, 14))
    if cited != listed:
        raise AuditError(
            f"Revised citation/reference mismatch: cited={sorted(cited)}, listed={sorted(listed)}"
        )
    if "available in a public repository" in revised:
        raise AuditError("Revised manuscript still contains an unsupported public claim")
    if "Decision Support" in revised or "Netflix Prize" in revised:
        raise AuditError("Revised manuscript still contains removed legacy framing")

    def words(text: str) -> int:
        return len(re.findall(r"\b[\w-]+\b", text))

    return revised, {
        "old_abstract_words": words(old_abstract),
        "new_abstract_words": words(new_abstract),
        "references_before": 15,
        "references_after": 13,
    }


def claim_row(
    claim_id: str,
    claim: str,
    computed: object,
    expected: object,
    evidence: str,
    note: str,
    tolerance: float | None = None,
) -> dict[str, str]:
    if tolerance is None:
        passed = computed == expected
    else:
        passed = abs(float(computed) - float(expected)) <= tolerance
    return {
        "claim_id": claim_id,
        "claim": claim,
        "computed_value": str(computed),
        "expected_value": str(expected),
        "status": "PASS" if passed else "FAIL",
        "evidence_files": evidence,
        "note": note,
    }


def build_claim_rows(raw: dict[str, object], summary: dict[str, object]) -> list[dict[str, str]]:
    x2 = raw["x2_counts"]
    assert isinstance(x2, dict)
    rows = [
        claim_row("C01", "Processed longitudinal panel rows", summary["panel_rows"], 4199, "data/processed/panel_long.csv", "Direct row count."),
        claim_row("C02", "Identification feature rows", summary["feature_rows"], 2777, "data/processed/identification_features_long.csv", "Direct row count."),
        claim_row("C03", "Typed public-appeal proxy rows", summary["typed_proxy_rows"], 2766, "data/processed/identification_features_long.csv", "Nonmissing proxy count; not a true public-vote label."),
        claim_row("C04", "Feasible P weeks", f"{summary['p_feasible']}/{summary['p_weeks']}", "247/248", "outputs/tables/constraint_summary.csv", "Season 18 Week 2 accounts for the logged skip."),
        claim_row("C05", "R exact/sampled weeks and sampled draws", f"{summary['r_exact']} exact; {summary['r_sampled']} sampled; {summary['r_sample_draws']}", "13 exact; 1 sampled; [50000]", "outputs/tables/ranking_identification_summary_r.csv", "Corrects the frozen manuscript's blanket 10,000-draw sentence."),
        claim_row("C06", "R-plus exact/sampled weeks and sampled draws", f"{summary['rplus_exact']} exact; {summary['rplus_sampled']} sampled; {summary['rplus_sample_draws']}", "36 exact; 37 sampled; [10000]", "outputs/tables/ranking_identification_summary_rplus.csv", "Direct enumeration-method and evaluated-draw counts."),
        claim_row("C07", "Preregistered seeds", raw["seeds"], 20, "outputs/stage26X-1/raw/*.csv", "Distinct raw seed values."),
        claim_row("C08", "Registered parameter regions", raw["regions"], 15, "outputs/stage26X-1/raw/*.csv", "12 internal plus 3 external regions."),
        claim_row("C09", "Stage 26X-1 synthetic cases", raw["x1_cases"], 67200, "outputs/stage26X-1/raw/*.csv", "Sum of distinct replication IDs within each seed-region file."),
        claim_row("C10", "Stage 26X-1 retained rows", raw["x1_rows"], 261600, "outputs/stage26X-1/raw/*.csv", "Direct CSV row count."),
        claim_row("C11", "Stage 26X-2 retained rows", raw["x2_rows"], 290400, "outputs/stage26X-2/raw/**/*.csv", "67,200 maximum-entropy + 67,200 Bayesian + 156,000 ablation rows."),
        claim_row("C12", "Combined retained rows", raw["combined_rows"], 552000, "outputs/stage26X-1/raw/*.csv; outputs/stage26X-2/raw/**/*.csv", "Correct total for abstract and cover letter."),
        claim_row("C13", "Rule-aware width below rule-agnostic width", f"{raw['width_below']}/{raw['x1_files']}", "300/300", "outputs/stage26X-1/raw/*.csv", "Cell-level mean comparison; direction follows set nesting."),
        claim_row("C14", "Positive-noise coverage loss cells", f"{raw['positive_noise_coverage_losses']}/{raw['positive_noise_cells']}", "180/180", "outputs/stage26X-1/raw/internal_*.csv", "Rule-agnostic minus rule-aware cell means."),
        claim_row("C15", "Mean positive-noise coverage loss", f"{raw['positive_noise_mean_loss']:.6f}", "0.050289", "outputs/stage26X-1/raw/internal_*.csv", "Rounded to six decimals.", tolerance=5e-7),
        claim_row("C16", "Elimination-removal coverage effect", f"{summary['ablation_coverage_change']:.6f}", "0.050289", "outputs/stage26X-2/tables/ablation_paired_effects.csv", "Positive-noise paired mean.", tolerance=5e-7),
        claim_row("C17", "Elimination-removal width effect", f"{summary['ablation_width_change']:.6f}", "0.163131", "outputs/stage26X-2/tables/ablation_paired_effects.csv", "Positive-noise paired mean.", tolerance=5e-7),
        claim_row("C18", "Positive-noise ablation improves coverage", f"{summary['positive_ablation_coverage_improved']}/{summary['positive_ablation_cells']}", "180/180", "outputs/stage26X-2/tables/ablation_paired_effects.csv", "Paired cell count."),
        claim_row("C19", "Clean-cell elimination removal changes coverage", f"{summary['clean_ablation_changed']}/{summary['clean_ablation_cells']}", "0/60", "outputs/stage26X-2/tables/ablation_paired_effects.csv", "Absolute tolerance 1e-12."),
        claim_row("C20", "Rule-aware Pareto dominance over Bayesian", f"{summary['aware_pareto']}/{summary['clean_pairwise']}", "0/120", "outputs/stage26X-2/tables/attribution_pairwise_cells.csv", "Clean same-information paired cells."),
        claim_row("C21", "Bayesian Pareto dominance over rule-aware", f"{summary['bayesian_pareto']}/{summary['clean_pairwise']}", "14/120", "outputs/stage26X-2/tables/attribution_pairwise_cells.csv", "All 14 are in the external 7-candidate, 3-round region."),
        claim_row("C22", "Insufficient posterior rows", raw["insufficient_posterior"], 94, "outputs/stage26X-2/raw/bayesian/*.csv", "Retained; no adaptive resampling or deletion."),
        claim_row("C23", "Raw files across Stage 26X-1/2", raw["combined_files"], 1200, "outputs/stage26X-1/raw; outputs/stage26X-2/raw", "300 + 900 files."),
        claim_row("C24", "Maximum Monte Carlo standard error", f"{summary['max_mcse']:.6f}", "0.005000", "outputs/tables/ranking_identification_summary_r*.csv", "Maximum is 0.0049999936 before six-decimal rounding; numerical approximation error, not behavioral uncertainty.", tolerance=5e-7),
    ]
    if any(row["status"] != "PASS" for row in rows):
        failures = [row["claim_id"] for row in rows if row["status"] != "PASS"]
        raise AuditError(f"Claim reconciliation failed: {failures}")
    return rows


def write_claim_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def render_report(
    source_hash: str,
    raw: dict[str, object],
    summary: dict[str, object],
    pytest_result: dict[str, object],
    staging_pytest_result: dict[str, object],
    test_scope: dict[str, object],
    manuscript_stats: dict[str, int],
    claim_rows: list[dict[str, str]],
) -> str:
    passed_claims = sum(row["status"] == "PASS" for row in claim_rows)
    staging_passed = (
        int(staging_pytest_result["tests"])
        - int(staging_pytest_result["failures"])
        - int(staging_pytest_result["errors"])
        - int(staging_pytest_result["skipped"])
    )
    staging_failures = ", ".join(
        f"`{name}`" for name in staging_pytest_result["failed_testcases"]
    )
    staging_omissions = ", ".join(
        f"`{name}`" for name in test_scope["staging_omissions"]
    )
    return f"""# Stage 26AC Research Audit and Optimization Report

## Executive verdict

The research evidence is internally reproducible and materially stronger than the
current frozen manuscript presentation. All {passed_claims}/{len(claim_rows)} audited
headline claims reconcile to tracked CSVs or logged calculations. The existing clean-room
record remains PASS: 16/16 tables and 8/8 figures matched exactly, 1,200 raw files contained
552,000 rows, and the Stage 26X-3 source hash remained `{source_hash.upper()}`. The current
Stage 26AC test run reports {pytest_result['tests']} tests, {pytest_result['failures']}
failures, {pytest_result['errors']} errors, and {pytest_result['skipped']} skipped.

Scientific submission is not yet unconditionally ready. The primary remaining limitations
are external validity, sensitivity to a single registered Bayesian prior/likelihood family,
94 fixed-draw posterior failures, and the lack of an observed public-vote truth label. Public
release and SIMPAT submission also remain gated by author-controlled repository naming/public
authorization and licensed JIF/JCR/CAS verification.

This stage creates a corrected non-frozen research draft. It does not alter the Stage 26X-3
source, Stage 21-24 artifacts, either preregistration, or any raw experimental output.

## Skill and audit strategy

The official curated `security-best-practices` skill was selected and installed because the
immediate operational risk is publication of a repository containing source-data terms,
author identities, history, and availability claims. No official academic-peer-review skill
was available in the curated catalog, and no untrusted third-party skill was installed.
Scientific review therefore relies on the repository's locked designs, raw outputs, tests,
generated tables, and clean-room verifier rather than a generic checklist.

## Research design review

### What is strong

- The inferential object is correctly bounded as latent public preference, feasible support
  intervals, and partially identified public appeal. The empirical data are not treated as
  observed true audience votes.
- Stage 26X-1 uses {raw['seeds']} preregistered seeds across {raw['regions']} regions and
  {raw['x1_cases']:,} known-truth synthetic cases. Stage 26X-2 aligns information sets for
  maximum-entropy and Bayesian comparators and adds registered component ablations.
- Evidence is unusually transparent about adverse findings: rule-aware Pareto dominance is
  {summary['aware_pareto']}/{summary['clean_pairwise']}, whereas Bayesian dominance is
  {summary['bayesian_pareto']}/{summary['clean_pairwise']}.
- The elimination effect is localized with paired ablation rather than inferred from an
  uncontrolled between-method difference: coverage changes by
  {summary['ablation_coverage_change']:+.6f} and width by
  {summary['ablation_width_change']:+.6f} across
  {summary['positive_ablation_cells']} positive-noise cells.
- The 300/300 width ordering is correctly treated as a consequence of nesting, not marketed
  as an empirical performance discovery.
- The fixed Bayesian draw-bank failures are retained and disclosed instead of adaptively
  resampled or deleted.

### What the evidence supports

The defensible contribution is a conditional method-selection criterion. When the recorded
elimination rule is treated as reliable, its constraint narrows the feasible set without a
clean-cell coverage loss in this simulator. Under the registered positive-noise process, the
same constraint excludes generated truth in 180/180 cells; removing it restores mean coverage
{summary['ablation_coverage_change']:.6f} at mean width cost
{summary['ablation_width_change']:.6f}. Bayesian intervals are preferable on both registered
metrics in 14/120 clean cells in one external region, while the reverse Pareto direction never
occurs. These are bounded simulator findings, not a universal ranking.

### What the evidence does not support

- No claim that inferred preferences equal true public votes in the empirical application.
- No claim that rule-aware inference uniformly outperforms Bayesian inference.
- No claim of user effectiveness, adoption, trust, welfare, or organizational benefit.
- No cross-regime cardinal comparison between percentage support width and ordinal rank width.
- No general robustness claim over priors, likelihoods, or misspecification processes not in
  the preregistered designs.

## Data and computation audit

| Item | Reconciled result | Assessment |
|---|---:|---|
| Empirical panel | {summary['panel_rows']:,} rows | PASS |
| Identification features | {summary['feature_rows']:,}; {summary['typed_proxy_rows']:,} typed proxies | PASS; proxy is not observed truth |
| P constraints | {summary['p_feasible']}/{summary['p_weeks']} feasible | PASS; one logged skip |
| R enumeration | {summary['r_exact']} exact; {summary['r_sampled']} sampled at {summary['r_sample_draws'][0]:,} draws | PASS; frozen wording was wrong |
| R-plus enumeration | {summary['rplus_exact']} exact; {summary['rplus_sampled']} sampled at {summary['rplus_sample_draws'][0]:,} draws | PASS |
| Stage 26X-1 archive | {raw['x1_files']} files; {raw['x1_rows']:,} rows | PASS |
| Stage 26X-2 archive | {raw['x2_files']} files; {raw['x2_rows']:,} rows | PASS |
| Combined archive | {raw['combined_files']} files; {raw['combined_rows']:,} rows | PASS |
| Insufficient Bayesian posteriors | {raw['insufficient_posterior']} rows | PASS disclosure; residual sensitivity risk |
| Maximum ranking MCSE | {summary['max_mcse']:.6f} | PASS; numerical only |

The complete line-by-line reconciliation is in `CLAIM_TRACEABILITY_AUDIT.csv`.

## Manuscript audit and corrections

### High-severity defects corrected in the Stage 26AC draft

1. **Positioning/title mismatch.** The frozen source retained the old decision-support title.
   The new draft uses `{FINAL_TITLE}` and removes the two uncited DSS references.
2. **Incorrect Monte Carlo statement.** The frozen source said all larger fields use 10,000
   permutations. The new draft states 50,000 for the one sampled R week and 10,000 for each of
   37 sampled R-plus weeks, directly matching the ranking summary tables.
3. **Incorrect availability tense.** The frozen source says data and code are available in a
   public repository, although the remote is private. The new draft says the package is prepared
   privately and forbids insertion of a public URL until anonymous access is verified.
4. **Missing source attribution.** The new draft names and cites COMAP in the empirical-data
   section and availability statement, records the official source and hash, and does not
   relicense the data.
5. **Wrong experiment-scale shorthand.** The new abstract distinguishes {raw['x1_cases']:,}
   synthetic cases from {raw['combined_rows']:,} retained method-level rows; it no longer treats
   261,600 Stage 26X-1 rows as the project total.
6. **Reference hygiene.** Two uncited DSS references and one uncited Netflix reference were
   removed. Remaining references were renumbered and the COMAP source was added. The reference
   count changes from {manuscript_stats['references_before']} to
   {manuscript_stats['references_after']}, with every retained item cited.
7. **Related-work repetition.** A duplicate partial-identification explanation in Section 3.3
   was removed without weakening the discretion/transparency boundary.

The abstract changes from {manuscript_stats['old_abstract_words']} to
{manuscript_stats['new_abstract_words']} machine-counted tokens. No target-journal abstract
limit is asserted because a current accessible official SIMPAT numeric limit was not found.

### Residual manuscript risks that require judgment or new work

| Risk | Severity | Why it remains | Safe disposition |
|---|---|---|---|
| External validity | High | One empirical competition testbed and two synthetic generators cannot establish behavior across institutions. | Keep claims conditional; a new external dataset would be a future study. |
| Bayesian specification sensitivity | High | Only the registered Dirichlet/uniform-ranking prior and zero-one likelihood are evaluated. | Do not claim robustness across Bayesian models; preregister any expansion. |
| 94 undefined Bayesian intervals | Medium-high | Defined-interval summaries condition on successful posterior draws. The direction of selection impact is unknown. | Preserve all rows and explicit denominator disclosure; do not post-hoc enlarge the bank. |
| Structural width result | Medium | 300/300 follows set nesting and is not independent validation. | Retain Proposition 2 framing and avoid performance language. |
| Empirical truth unavailable | High | No observed public-vote labels exist. | Use empirical data only as a feasible-set testbed; reserve coverage for known-truth simulation. |
| Literature breadth | Medium | The corrected draft has a focused but small reference base and no systematic recent-literature refresh. | Conduct a separate documented primary-source search before submission; do not insert remembered citations. |
| Journal eligibility | Blocking administrative | SIMPAT JIF/JCR/CAS status is not verified in licensed sources. | Author must verify current year and CAS major-category assignment. |

## Reproducibility and software quality

- The prior clean-room reconstruction took 69.01 minutes and reproduced 16/16 tables and 8/8
  figures exactly; its report remains the authoritative end-to-end verification record.
- The Stage 26AC run independently recounts all 1,200 raw files and 552,000 rows and recomputes
  each headline comparison from raw or paired-cell CSVs.
- Root-level pytest discovery previously entered staged and clean-room copies and failed during
  collection. `pytest.ini` now fixes `tests/` as the only collection root and excludes outputs,
  temporary clean rooms, and local environments.
- The current focused run passes {pytest_result['tests']} tests with no failures/errors.
- A direct bare `pytest` run inside the current staged publication subset collects
  {staging_pytest_result['tests']} tests: {staging_passed} pass and
  {staging_pytest_result['failures']} fail. The failures are {staging_failures}. Both assert
  the presence of generated tables/data that the staged repository intentionally omits before
  `reproduce.md` is run. This is an execution-order dependency, not a contradictory numerical
  result. The public verification command must therefore follow `reproduce.md`; a fresh clone
  is not honestly described as bare-`pytest` green before generation.
- The development tree contains {test_scope['root_count']} test files and the staged subset
  contains {test_scope['staging_count']}. Files not packaged are: {staging_omissions}. This is
  acceptable only if the staged repository is described as the publication subset rather than
  the complete development-history test suite.
- A pandas future-warning path in the active Stage 25H-E audit was replaced with an explicit
  boolean equality count; its numerical output is covered by existing traceability tests.
- All changed scripts retain command-line `--help` behavior. No stochastic operation or seed
  was added or changed.

## Repository, license, and release review

The COMAP file remains anonymously downloadable without login and matches
`{COMAP_SHA256.upper()}`. The source-data copy may remain under the author's stated decision
rule, with COMAP attribution and `DATA_TERMS.md`; it is not open data and is not covered by the
MIT code license.

This stage corrects all six active Stage 25 generators that previously emitted or recommended
an additional data license. Historical generated records remain dated evidence and are not
silently rewritten. The staged repository is intentionally left dirty and private so the author
can review the exact changes before any commit or push.

Public release remains blocked until all of the following are true:

1. The author selects the final repository name.
2. Active URLs and generators are updated to the selected name.
3. The author decides whether a normal corrective commit is sufficient or private history must
   also be rewritten to remove obsolete license statements.
4. The corrected staged package is committed and pushed while private.
5. The author explicitly authorizes public release.
6. The final URL, raw CSV, clone path, and availability statements pass a new anonymous test.

## Submission readiness

| Dimension | Current ruling |
|---|---|
| Core evidence integrity | PASS |
| Headline-number traceability | PASS ({passed_claims}/{len(claim_rows)}) |
| Existing clean-room reproduction | PASS |
| Root test suite | PASS ({pytest_result['tests']}/{pytest_result['tests']}) |
| Staged bare test run before generation | ORDER-DEPENDENT ({staging_passed}/{staging_pytest_result['tests']} pass) |
| Non-frozen research manuscript | IMPROVED; requires author review |
| Data permission/access gate | PASS WITH ATTRIBUTION AND SCOPE LIMIT |
| Repository public availability | BLOCKED |
| SIMPAT bibliometric eligibility | AUTHOR_MUST_VERIFY |
| SIMPAT live format compliance | NOT YET EXECUTED |
| Overall submission | NOT READY UNTIL AUTHOR GATES CLOSE |

## Recommended next sequence

1. Review `METHODS_research_draft_STAGE26AC.md`, especially the corrected abstract, Monte Carlo
   paragraph, COMAP citation, and truthful availability statement.
2. Select the repository name; the recommended candidate remains
   `coverage-width-tradeoffs-rule-constrained-aggregation`.
3. Decide normal corrective commit versus private-history rewrite for obsolete data-license
   statements. CSV removal is not required under the verified access ruling.
4. Verify SIMPAT's current JIF, JCR Q1, CAS major-category zone, and category assignment in the
   licensed sources.
5. After author approval, synchronize final URLs and package documentation, commit/push while
   private, then authorize public release and repeat anonymous validation.
6. Only after those gates close, execute journal-specific formatting and PDF inspection.

## Files produced by Stage 26AC

- `METHODS_research_draft_STAGE26AC.md`: corrected non-frozen research draft.
- `CLAIM_TRACEABILITY_AUDIT.csv`: computed claim-to-evidence reconciliation.
- `OPTIMIZATION_CHANGELOG.md`: exact scope and frozen-boundary record.
- `RESEARCH_AUDIT_AND_OPTIMIZATION_REPORT.md`: this report.
- `pytest_results.xml`: machine-readable current test run.
- `staging_pytest_results.xml`: machine-readable direct staged-package test boundary.

## Author decisions still required

- Approve or revise the Stage 26AC non-frozen manuscript changes.
- Select the final repository name.
- Choose normal corrective commit or private-history rewrite for obsolete license statements.
- Verify SIMPAT JIF/JCR/CAS eligibility and major-category assignment.
- After private-package review, explicitly authorize rename, push, and later public release.
"""


def render_changelog(
    source_hash: str,
    manuscript_stats: dict[str, int],
    pytest_result: dict[str, object],
    staging_pytest_result: dict[str, object],
) -> str:
    return f"""# Stage 26AC Optimization Changelog

## Frozen boundary

- Source manuscript read only: `{SOURCE_MANUSCRIPT.as_posix()}`.
- Source SHA-256 before and after: `{source_hash.upper()}`.
- Stage 21-24 artifacts, Stage 26X-1/26X-2 preregistrations, raw outputs, and
  Stage 26X-3 source were not modified.

## Active-source changes

- Added `pytest.ini` to the root and staged repository to restrict collection to `tests/`.
- Corrected six root and six staged Stage 25 generators so source data inherit the
  documented COMAP terms and are not assigned an additional repository data license.
- Replaced one warning-prone pandas boolean count with explicit `eq(True)` semantics.
- Added this deterministic Stage 26AC audit generator and focused tests.

## Generated manuscript changes

- Final title inserted.
- Abstract scale corrected to 67,200 cases and 552,000 retained rows.
- R/R-plus Monte Carlo draw counts corrected.
- COMAP attribution, source URL, access date, and data hash added.
- Public-repository claim changed to the truthful current private status.
- Three uncited legacy references removed; COMAP source added; citations renumbered.
- Abstract word count: {manuscript_stats['old_abstract_words']} ->
  {manuscript_stats['new_abstract_words']}.

## Verification

- Current tests: {pytest_result['tests']} total, {pytest_result['failures']} failures,
  {pytest_result['errors']} errors, {pytest_result['skipped']} skipped.
- Direct staged-package tests before output generation: {staging_pytest_result['tests']} total,
  {staging_pytest_result['failures']} expected artifact-order failures,
  {staging_pytest_result['errors']} errors, {staging_pytest_result['skipped']} skipped.
- Claim reconciliation fails closed on any mismatch.
"""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.project_root.resolve()
    output_dir = args.output_dir
    if output_dir.is_absolute():
        raise AuditError("--output-dir must be project-relative")
    output = root / output_dir
    output.mkdir(parents=True, exist_ok=True)

    source_path = require_file(root, SOURCE_MANUSCRIPT)
    source_hash = sha256(source_path)
    if source_hash != SOURCE_MANUSCRIPT_SHA256:
        raise AuditError(
            "Frozen Stage 26X-3 manuscript hash mismatch: "
            f"expected {SOURCE_MANUSCRIPT_SHA256}, observed {source_hash}"
        )

    raw = collect_raw_evidence(root)
    summary = collect_summary_evidence(root)
    pytest_result = parse_pytest_junit(root, args.pytest_junit)
    if pytest_result["failures"] or pytest_result["errors"]:
        raise AuditError(f"Current pytest evidence is not passing: {pytest_result}")
    staging_pytest_result = parse_pytest_junit(root, args.staging_pytest_junit)
    test_scope = collect_test_scope(root)

    source = source_path.read_text(encoding="utf-8")
    revised, manuscript_stats = build_revised_manuscript(source)
    claim_rows = build_claim_rows(raw, summary)

    revised_path = output / "METHODS_research_draft_STAGE26AC.md"
    claim_path = output / "CLAIM_TRACEABILITY_AUDIT.csv"
    changelog_path = output / "OPTIMIZATION_CHANGELOG.md"
    report_path = output / "RESEARCH_AUDIT_AND_OPTIMIZATION_REPORT.md"

    revised_path.write_text(revised, encoding="utf-8", newline="\n")
    write_claim_csv(claim_path, claim_rows)
    changelog_path.write_text(
        render_changelog(
            source_hash, manuscript_stats, pytest_result, staging_pytest_result
        ),
        encoding="utf-8",
        newline="\n",
    )
    report_path.write_text(
        render_report(
            source_hash,
            raw,
            summary,
            pytest_result,
            staging_pytest_result,
            test_scope,
            manuscript_stats,
            claim_rows,
        ),
        encoding="utf-8",
        newline="\n",
    )

    if sha256(source_path) != source_hash:
        raise AuditError("Frozen source changed during Stage 26AC")

    print(f"Wrote {relative(revised_path, root)}")
    print(f"Wrote {relative(claim_path, root)}")
    print(f"Wrote {relative(changelog_path, root)}")
    print(f"Wrote {relative(report_path, root)}")
    print(f"CLAIMS_PASS={len(claim_rows)}/{len(claim_rows)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
