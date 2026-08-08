"""Generate the additive Stage 26Y EJOR migration and audit package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


SOURCE_RELATIVE = Path("outputs/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md")
SOURCE_SHA256 = "758755b50cd1c059d939fa550ac151c7b55263348e7bb8b55b40e20fff1c2d82"
CONTRIBUTION_RELATIVE = Path("outputs/stage26X-3/CONTRIBUTION_REPOSITIONING.md")
CONTRIBUTION_SHA256 = "f52f1c7dd51479db951bb531ac0102c9634648e5c9742ad0b660ec1bbaa3bfab"
TITLE = "Coverage-Width Tradeoffs in Rule-Constrained Expert-Crowd Aggregation"
OLD_TITLE = "Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences"
EJOR_GUIDE_URL = (
    "https://www.sciencedirect.com/journal/"
    "european-journal-of-operational-research/publish/guide-for-authors"
)
EJOR_HOME_URL = (
    "https://www.sciencedirect.com/journal/european-journal-of-operational-research"
)
REPOSITORY_URL = "https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation"
RETRIEVED = "2026-07-31"

OUTPUT_NAMES = {
    "AUTHOR_DECISIONS_AND_ELIGIBILITY.md",
    "COVER_LETTER_DRAFT.md",
    "EJOR_OFFICIAL_REQUIREMENTS.md",
    "EJOR_submission_draft_STAGE26Y_source.md",
    "HIGHLIGHTS.md",
    "MIGRATION_AUDIT.md",
    "OUTPUT_MANIFEST.csv",
    "STAGE24_PACKAGE_MANIFEST_DIAGNOSTIC.md",
    "TITLE_PAGE.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate an additive Stage 26Y EJOR migration package from the locked "
            "Stage 26X-3 manuscript. Frozen Stage 24/25 files are never modified."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root containing outputs/stage26X-3 and submission_package_stage24.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Destination directory; defaults to outputs/stage26Y under the project root.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def count_csv_rows(directory: Path) -> tuple[int, int]:
    files = sorted(directory.rglob("*.csv"))
    rows = 0
    for path in files:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            count = sum(1 for _ in handle)
        if count == 0:
            raise ValueError(f"Raw CSV is empty: {path}")
        rows += count - 1
    return len(files), rows


def abstract_text(manuscript: str) -> str:
    match = re.search(r"^## Abstract\n\n(.+?)\n\n\*\*Keywords:", manuscript, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError("Could not locate the manuscript abstract.")
    return " ".join(match.group(1).split())


APA_REFERENCES = """## References

Ananny, M., & Crawford, K. (2018). Seeing without knowing: Limitations of the transparency ideal and its application to algorithmic accountability. *New Media & Society, 20*(3), 973-989. https://doi.org/10.1177/1461444816676645

Arrow, K. J. (1950). A difficulty in the concept of social welfare. *Journal of Political Economy, 58*(4), 328-346. https://doi.org/10.1086/256963

Bannister, F., & Connolly, R. (2011). The trouble with transparency: A critical review of openness in e-government. *Policy & Internet, 3*(1), 1-30. https://doi.org/10.2202/1944-2866.1076

Dwork, C., Kumar, R., Naor, M., & Sivakumar, D. (2001). Rank aggregation methods for the Web. In *Proceedings of the 10th International Conference on World Wide Web* (pp. 613-622). https://doi.org/10.1145/371920.372165

Imbens, G. W., & Manski, C. F. (2004). Confidence intervals for partially identified parameters. *Econometrica, 72*(6), 1845-1857. https://doi.org/10.1111/j.1468-0262.2004.00555.x

Liang, A. (2019). Inference of preference heterogeneity from choice data. *Journal of Economic Theory, 179*, 275-311. https://doi.org/10.1016/j.jet.2018.09.010

Lorenz, J., Rauhut, H., Schweitzer, F., & Helbing, D. (2011). How social influence can undermine the wisdom of crowd effect. *Proceedings of the National Academy of Sciences, 108*(22), 9020-9025. https://doi.org/10.1073/pnas.1008636108

Manski, C. F. (2000). Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice. *Journal of Econometrics, 95*(2), 415-442. https://doi.org/10.1016/S0304-4076(99)00045-7

Manski, C. F. (2007). Minimax-regret treatment choice with missing outcome data. *Journal of Econometrics, 139*(1), 105-115. https://doi.org/10.1016/j.jeconom.2006.06.006

Shmueli, G. (2010). To explain or to predict? *Statistical Science, 25*(3), 289-310. https://doi.org/10.1214/10-STS330

Steunenberg, B. (1996). Agent discretion, regulatory policymaking, and different institutional arrangements. *Public Choice, 86*(3-4), 309-339. https://doi.org/10.1007/BF00136524

Young, H. P. (1988). Condorcet's theory of voting. *American Political Science Review, 82*(4), 1231-1244. https://doi.org/10.2307/1961757
"""


DECLARATIONS = """## Acknowledgements

None.

## Funding

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

## Declaration of Competing Interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## CRediT Author Contributions

Deng Lizhen: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Visualization, Writing - original draft, Writing - review and editing, Project administration. Liu Yuxin: Writing - review and editing, Validation, Resources, Investigation. Li Bo: Supervision, Writing - review and editing, Validation.

## Ethics Statement

This study did not involve human participants, animals, clinical data, or personally identifiable information; therefore, ethics approval was not required.

## Declaration of Generative AI and AI-Assisted Technologies in the Manuscript Preparation Process

During the preparation of this work, the authors used ChatGPT and Codex for language polishing, readability review, manuscript consistency checking, and submission-readiness review. After using these tools, the authors reviewed and edited the content as needed and take full responsibility for the content of the publication. These tools were not used to generate research data, experimental results, references, figures, scientific conclusions, or author-side facts.
"""


def migrate_manuscript(source: str) -> str:
    if not source.startswith(f"# {OLD_TITLE}\n"):
        raise ValueError("Unexpected Stage 26X-3 manuscript title.")
    manuscript = source.replace(f"# {OLD_TITLE}", f"# {TITLE}", 1)

    title_page_block = """

**Authors:** Deng Lizhen^a^; Liu Yuxin^b^; Li Bo^b^

**Affiliations:** ^a^ Huazhong University of Science and Technology, 1037 Luoyu Road, Hongshan District, Wuhan, Hubei 430074, China. ^b^ Wuhan University of Technology, No. 122 Luoshi Road, Hongshan District, Wuhan, Hubei 430070, China.

**Corresponding author:** Deng Lizhen, 3070116993@qq.com; Huazhong University of Science and Technology, 1037 Luoyu Road, Hongshan District, Wuhan, Hubei 430074, China.
"""
    manuscript = manuscript.replace(f"# {TITLE}\n", f"# {TITLE}{title_page_block}\n", 1)

    manuscript = re.sub(
        r"\*\*Keywords:\*\*.*",
        "**Keywords:** Decision analysis; partial identification; group decision making; coverage-width tradeoff; latent public preference.",
        manuscript,
        count=1,
    )

    citations = {
        "[8,9]": "(Manski, 2000; Imbens & Manski, 2004)",
        "[10]": "(Manski, 2007)",
        "[3,4]": "(Arrow, 1950; Young, 1988)",
        "[5]": "(Dwork et al., 2001)",
        "[6]": "(Liang, 2019)",
        "[7]": "(Lorenz et al., 2011)",
        "[14]": "(Steunenberg, 1996)",
        "[12,13]": "(Ananny & Crawford, 2018; Bannister & Connolly, 2011)",
        "[11]": "(Shmueli, 2010)",
    }
    for old, new in citations.items():
        manuscript = manuscript.replace(old, new)

    data_section = """## Data and Code Availability

The data, code, fixed seed list, configurations, and generated audit artifacts supporting this study are retained in the local reproducibility package. The designated repository is https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation. Public availability must not be claimed until the tracked package is uploaded, made public with author authorization, and verified anonymously.

""" + DECLARATIONS
    manuscript, count = re.subn(
        r"## Data and Code Availability for Anonymized Review\n\n.*?(?=\n## References)",
        data_section.rstrip(),
        manuscript,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise ValueError("Could not replace the anonymized data and code section.")

    start = manuscript.index("## References")
    end = manuscript.index("## Figure Captions")
    manuscript = manuscript[:start] + APA_REFERENCES.rstrip() + "\n\n" + manuscript[end:]
    return manuscript.rstrip() + "\n"


def title_page() -> str:
    return f"""# Title Page

**Title:** {TITLE}

**Authors:** Deng Lizhen^a^; Liu Yuxin^b^; Li Bo^b^

**Affiliations:**

- ^a^ Huazhong University of Science and Technology, 1037 Luoyu Road, Hongshan District, Wuhan, Hubei 430074, China
- ^b^ Wuhan University of Technology, No. 122 Luoshi Road, Hongshan District, Wuhan, Hubei 430070, China

**Corresponding author:** Deng Lizhen

**Email:** 3070116993@qq.com

**Postal address:** Huazhong University of Science and Technology, 1037 Luoyu Road, Hongshan District, Wuhan, Hubei 430074, China

**Article type:** Theory and Methodology Paper

**Proposed first EJOR keyword / portal section:** Decision analysis
"""


def highlights() -> str:
    return """# Highlights

- Rule constraints define feasible sets for latent public preference.
- Elimination noise lowers coverage in every registered noisy cell.
- Removing elimination restores coverage while widening feasible sets.
- Bayesian intervals dominate in 14 of 120 clean comparison cells.
"""


def cover_letter(x1_rows: int, x2_rows: int) -> str:
    return f"""# Cover Letter Draft

Dear Editors,

Please consider the manuscript, \"{TITLE},\" as a Theory and Methodology Paper for the *European Journal of Operational Research*.

The study makes three bounded contributions. First, it localizes a coverage-width mechanism in the registered synthetic design: positive outcome noise reduces rule-aware coverage in 180 of 180 cells by a mean of 0.050289, while removing the elimination constraint changes coverage by +0.050289 and width by +0.163131. Second, it identifies a method-selection boundary. Rule-aware intervals Pareto-dominate the same-information Bayesian baseline in 0 of 120 clean cells, whereas Bayesian intervals dominate in 14 of 120 cells, all in the external seven-candidate, three-round region. Third, it formalizes rule-conditioned cardinal and ordinal feasible sets for latent public preference and treats the 300 of 300 width ordering as the consequence of set nesting, not as independent evidence of method superiority.

These adverse comparisons are central to the manuscript. We do not claim that rule-aware inference is generally better than posterior interval inference. The contribution is a conditional selection criterion: retain elimination constraints when the recorded rule is treated as reliable; relax them when rule violation is admitted and a wider feasible set is acceptable; and use posterior intervals when their additional probability-model assumptions are suitable, including in the identified region where they have the strict Pareto direction.

The evaluation uses 20 preregistered seeds and 300 registered seed-parameter cells. The multi-seed sensitivity archive contains {x1_rows:,} raw replication rows. Independent baseline and ablation archives contain {x2_rows:,} additional rows, for {x1_rows + x2_rows:,} retained raw rows locally. The fixed Bayesian draw bank contains 94 insufficient-posterior rows, including 10 under zero outcome noise; all are disclosed, with no replacement draws or deletion.

AUTHOR ACTION REQUIRED BEFORE SUBMISSION: verify the tracked reproducibility package at the designated repository after the final private push and public-release transition. Replace this notice only after anonymous URL, raw-data, manifest, and clean-clone checks pass. Until then, this draft does not claim that the raw records are publicly accessible.

The empirical competition record is used as a testbed for a general expert-crowd aggregation problem. The manuscript does not claim to observe the true audience vote, establish organizational effects, or show uniform method superiority.

Correspondence: Deng Lizhen, 3070116993@qq.com, Huazhong University of Science and Technology, 1037 Luoyu Road, Hongshan District, Wuhan, Hubei 430074, China.
"""


def official_requirements() -> str:
    return f"""# Stage 26Y EJOR Official Requirements

Official Guide for Authors: {EJOR_GUIDE_URL}

Official journal page: {EJOR_HOME_URL}

Retrieved: {RETRIEVED}

## Review model and identity handling

The guide states \"single blind review process\". Reviewers therefore receive author identities. The new-submission guide also requires title-page information in the manuscript and a single PDF or Word manuscript file. Stage 26Y creates a full-identity source and title page; it does not create or require an anonymized EJOR manuscript.

## Length and layout

The guide says the article must \"not exceed 30 pages\" including abstract, figures, tables, references, and appendices. Initial format is A4 or letter, single column, 11-point font, 1.5 line spacing, with no author-supplied line numbers. Markdown word count cannot certify pagination; final DOCX or PDF pagination remains required.

## Highlights

The guide says Highlights are \"mandatory from the First Submission\". It requires 3-5 bullets, no more than 85 characters including spaces per bullet, no abbreviations, in a separate editable file. `HIGHLIGHTS.md` contains four compliant source bullets.

## Paper type

Theory and Methodology papers contribute to the \"methodology of OR\" or its foundations. Innovative Applications describe \"novel ways to solve real problems\". This manuscript belongs under Theory and Methodology because its contributions are a formal feasible-set framework, synthetic mechanism localization, and a method-selection boundary. It does not document implementation that solves an observed managerial problem, and it has no user or organizational-effect validation. Innovative Applications is therefore not supported by the evidence.

## References

The guide specifies \"American Psychological Association\" style, alphabetical ordering, and citation-list consistency. Stage 26Y converts the cited literature to author-year citations and APA-style entries and removes three uncited DSS/data-set references from the migrated source.

## Keywords

The guide requires up to five keywords, with the first selected from the EJOR list and entered as the portal section/category. Stage 26Y uses `Decision analysis` as the first official-list keyword and four manuscript-specific keywords.

## Cover letter

The official new-submission file inventory lists the cover letter as optional. The claim that it is mandatory or carries a documented special weight is `NO_SOURCE_FOUND`. A strategically focused draft is nevertheless supplied because it addresses the paper's adverse comparison directly.

## Current metric and timing warning

The official journal page displayed Impact Factor `6.0` on {RETRIEVED}; the historical `5.1` value is not current and also exceeds a strict upper bound of `5.0`. The guide reports immediate editorial actions usually in under one week, about three months to a first reviewed decision, and just under one year from submission to publication for accepted papers. The unverified claim of a 60-70% desk-reject rate is not used.
"""


def stage24_diagnostic(root: Path) -> str:
    manifest_path = root / "outputs/tables/stage24_submission_package_manifest.csv"
    package = root / "submission_package_stage24"
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))

    actual = []
    for path in sorted(item for item in package.rglob("*") if item.is_file()):
        actual.append(
            {
                "package_file": path.relative_to(package).as_posix(),
                "bytes": str(path.stat().st_size),
                "sha256": sha256(path),
            }
        )
    by_path = {row["package_file"]: row for row in actual}
    manifest_paths = [row["package_file"] for row in manifest]
    actual_paths = [row["package_file"] for row in actual]
    missing = sorted(set(manifest_paths) - set(actual_paths))
    extra = sorted(set(actual_paths) - set(manifest_paths))
    mismatches = []
    for expected in manifest:
        observed = by_path.get(expected["package_file"])
        if observed and (
            observed["bytes"] != expected["bytes"]
            or observed["sha256"] != expected["sha256"]
        ):
            mismatches.append((expected, observed))

    script = (root / "scripts/24_dss_author_submission_completion.py").read_text(
        encoding="utf-8"
    )
    manifest_position = script.index("manifest = package_manifest(root, package)")
    final_write_position = script.index(
        'write_text(package / "SUBMISSION_NOTES_AND_NO_GO.md", no_go)'
    )
    order_status = (
        "pass"
        if manifest_paths == sorted(manifest_paths, key=str.casefold)
        else "fail"
    )

    mismatch_rows = "\n".join(
        "| "
        + " | ".join(
            [
                expected["package_file"],
                expected["bytes"],
                observed["bytes"],
                expected["sha256"],
                observed["sha256"],
            ]
        )
        + " |"
        for expected, observed in mismatches
    ) or "| None | - | - | - | - |"

    return f"""# Stage 24 Package Manifest Diagnostic

## Scope

Read-only diagnosis of `submission_package_stage24/` against `outputs/tables/stage24_submission_package_manifest.csv`. No Stage 24 or Stage 25 file was edited.

## Results

- Manifest rows: `{len(manifest)}`.
- Actual package files: `{len(actual)}`.
- Missing files: `{len(missing)}`.
- Extra files: `{len(extra)}`.
- Manifest entry-order check: `{order_status}`.
- Size or SHA-256 mismatches: `{len(mismatches)}`.

| File | Manifest bytes | Actual bytes | Manifest SHA-256 | Actual SHA-256 |
|---|---:|---:|---|---|
{mismatch_rows}

The manifest is already sorted; this is not an entry-order-only issue. The current package note is byte-identical to `outputs/logs/stage24_final_no_go_check.md`, so the note itself is internally consistent with the final log.

## Cause

In `scripts/24_dss_author_submission_completion.py`, `package_manifest(...)` is evaluated before the final no-go report is written into `submission_package_stage24/SUBMISSION_NOTES_AND_NO_GO.md` (`{manifest_position} < {final_write_position}` in the script text). The manifest therefore records the pre-existing version of that file and the script overwrites it afterward. Its generic role `figure or table asset` is also inaccurate because the role map has no explicit entry for this note.

## Handling

`AUTHOR_DECISION_REQUIRED`

Do not repair the frozen Stage 24 package in place. In a later maintenance stage, version the generator and write the final no-go report before computing the package manifest; add an explicit manifest role for the submission note; generate a new versioned package; then require zero missing, extra, size, and hash differences. This report is the requested diagnosis and repair plan only.
"""


def eligibility() -> str:
    return f"""# Stage 26Y Author Decisions and Current Eligibility

## Author-fixed historical decisions

- Historical target: European Journal of Operational Research.
- Fixed title: *{TITLE}*.
- Stage 24 handling: diagnosis and record only; do not modify frozen files.

## Current gate

`DO_NOT_UPLOAD_EJOR_PACKAGE`

The official EJOR page displayed Impact Factor `6.0` on {RETRIEVED}. EJOR therefore fails the currently stated strict `3-5` impact-factor screen, regardless of its Chinese Academy of Sciences classification. The historical table's `5.1` value is both stale and greater than `5.0`. No authorized current Chinese Academy of Sciences major-category record is stored in this project, so that field remains `AUTHOR_MUST_VERIFY` rather than being asserted.

This Stage 26Y package completes the previously omitted migration and preserves the historical author decision for audit purposes. It is not a recommendation to submit to EJOR under the current hard screen.

## Repository release gate

The repository check recorded on {RETRIEVED} found the then-designated repository publicly reachable but empty. That result is historical and does not establish the current state of {REPOSITORY_URL}. A fresh anonymous URL, raw-data, manifest, and clean-clone verification is required before any manuscript or cover letter claims public availability.
"""


def migration_audit(
    source_path: Path,
    manuscript: str,
    x1_files: int,
    x1_rows: int,
    x2_files: int,
    x2_rows: int,
) -> str:
    abstract = abstract_text(manuscript)
    keywords_match = re.search(r"\*\*Keywords:\*\* (.+)", manuscript)
    keywords = [item.strip() for item in keywords_match.group(1).split(";")] if keywords_match else []
    numeric_citations = re.findall(r"\[[0-9]+(?:,[0-9]+)*\]", manuscript)
    required = ["180/180", "0.050289", "0.163131", "0/120", "14/120", "94", "300/300"]
    missing = [item for item in required if item not in manuscript]
    status = "pass" if not missing and not numeric_citations else "fail"
    return f"""# Stage 26Y Migration Audit

- Source: `{source_path.as_posix()}`.
- Source SHA-256: `{SOURCE_SHA256}`.
- Generated title: `{TITLE}`.
- Abstract word count: `{len(abstract.split())}`; EJOR range is 50-250.
- Keyword count: `{len(keywords)}`; EJOR maximum is 5.
- First keyword: `{keywords[0] if keywords else 'MISSING'}`.
- Required adverse-result tokens missing: `{', '.join(missing) if missing else 'none'}`.
- Residual numeric citation tokens: `{len(numeric_citations)}`.
- Stage 26X-1 raw archive: `{x1_files}` CSV files, `{x1_rows}` rows.
- Stage 26X-2 raw archive: `{x2_files}` CSV files, `{x2_rows}` rows.
- Total retained Stage 26X raw rows: `{x1_rows + x2_rows}`.
- Overall source migration check: `{status}`.

The `261,600` figure applies to Stage 26X-1 sensitivity replications, not to the complete Stage 26X raw archive. Stage 26X-2 contributes another `290,400` rows. Reporting `261,600` as the total available raw output would undercount the evidence package.
"""


def write_manifest(output_dir: Path) -> None:
    rows = []
    for path in sorted(item for item in output_dir.iterdir() if item.is_file()):
        if path.name == "OUTPUT_MANIFEST.csv":
            continue
        rows.append(
            {
                "file": path.name,
                "sha256": sha256(path),
                "bytes": str(path.stat().st_size),
            }
        )
    with (output_dir / "OUTPUT_MANIFEST.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=["file", "sha256", "bytes"])
        writer.writeheader()
        writer.writerows(rows)


def generate(root: Path, output_dir: Path) -> None:
    root = root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    source_path = root / SOURCE_RELATIVE
    contribution_path = root / CONTRIBUTION_RELATIVE
    if sha256(source_path) != SOURCE_SHA256:
        raise ValueError("Stage 26X-3 source hash differs from the locked migration input.")
    if sha256(contribution_path) != CONTRIBUTION_SHA256:
        raise ValueError("Stage 26X-3 contribution report hash differs from the locked input.")

    source = source_path.read_text(encoding="utf-8")
    for token in ("180/180", "0.050289", "0.163131", "0/120", "14/120", "94", "300/300"):
        if token not in source:
            raise ValueError(f"Required evidence token absent from locked source: {token}")

    x1_files, x1_rows = count_csv_rows(root / "outputs/stage26X-1/raw")
    x2_files, x2_rows = count_csv_rows(root / "outputs/stage26X-2/raw")
    if (x1_files, x1_rows, x2_files, x2_rows) != (300, 261600, 900, 290400):
        raise ValueError(
            "Raw archive counts differ from the audited Stage 26Y expectations: "
            f"{x1_files=}, {x1_rows=}, {x2_files=}, {x2_rows=}"
        )

    manuscript = migrate_manuscript(source)
    write_text(output_dir / "AUTHOR_DECISIONS_AND_ELIGIBILITY.md", eligibility())
    write_text(output_dir / "COVER_LETTER_DRAFT.md", cover_letter(x1_rows, x2_rows))
    write_text(output_dir / "EJOR_OFFICIAL_REQUIREMENTS.md", official_requirements())
    write_text(output_dir / "EJOR_submission_draft_STAGE26Y_source.md", manuscript)
    write_text(output_dir / "HIGHLIGHTS.md", highlights())
    write_text(
        output_dir / "MIGRATION_AUDIT.md",
        migration_audit(SOURCE_RELATIVE, manuscript, x1_files, x1_rows, x2_files, x2_rows),
    )
    write_text(
        output_dir / "STAGE24_PACKAGE_MANIFEST_DIAGNOSTIC.md",
        stage24_diagnostic(root),
    )
    write_text(output_dir / "TITLE_PAGE.md", title_page())
    write_manifest(output_dir)

    observed = {path.name for path in output_dir.iterdir() if path.is_file()}
    if observed != OUTPUT_NAMES:
        raise ValueError(f"Unexpected Stage 26Y outputs: {sorted(observed ^ OUTPUT_NAMES)}")


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    output_dir = args.output_dir or root / "outputs/stage26Y"
    generate(root, output_dir.resolve())
    print(f"Stage 26Y generated at {output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
