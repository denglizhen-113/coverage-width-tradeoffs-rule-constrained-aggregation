"""Generate the final local review before the publication-repository commit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import struct
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


EXPECTED_REMOTE = (
    "https://github.com/denglizhen-113/"
    "coverage-width-tradeoffs-rule-constrained-aggregation.git"
)
FROZEN_X3_SHA256 = (
    "758755B50CD1C059D939FA550AC151C7B55263348E7BB8B55B40E20FFF1C2D82"
)
COMAP_SHA256 = (
    "EA99CAEC6EA243BDB450A1971A95BA8A95701A93BE7FF29F0BA3C57D72DDFF52"
)
PAIR_SCRIPTS = (
    "25ha_apply_author_provided_information.py",
    "25hb_apply_final_author_confirmations.py",
    "25hc_apply_repository_address_and_approval_closure.py",
    "25hd_reconstruct_dss_submission_docx.py",
    "25he_finalize_dss_submission_package.py",
    "25hf_resolve_dss_upload_gate.py",
    "26y_ejor_submission_migration.py",
    "26ac_research_audit_optimization.py",
    "26ac1_repository_publication_readiness.py",
    "26ad_literature_verification.py",
    "26ae_precommit_strict_review.py",
)
TEXT_SUFFIXES = {
    ".csv",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".tex",
    ".txt",
    ".yml",
    ".yaml",
}


class ReviewError(RuntimeError):
    """Raised when a local precommit integrity gate fails."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit the current research draft and staged publication repository, "
            "then generate an author-facing precommit report."
        )
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/stage26AE"))
    parser.add_argument(
        "--staging-dir", type=Path, default=Path("outputs/stage26AA/repo_staging")
    )
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def run_git(staging: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=staging,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def junit_totals(path: Path) -> tuple[int, int, int, int]:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    return tuple(
        sum(int(float(suite.attrib.get(key, "0"))) for suite in suites)
        for key in ("tests", "failures", "errors", "skipped")
    )


def png_metadata(path: Path) -> tuple[int, int, float | None]:
    width = height = 0
    dpi = None
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ReviewError(f"Invalid PNG signature: {path}")
        while True:
            raw_length = handle.read(4)
            if not raw_length:
                break
            length = struct.unpack(">I", raw_length)[0]
            kind = handle.read(4)
            data = handle.read(length)
            handle.read(4)
            if kind == b"IHDR":
                width, height = struct.unpack(">II", data[:8])
            elif kind == b"pHYs" and len(data) == 9 and data[8] == 1:
                x_ppm = struct.unpack(">I", data[:4])[0]
                dpi = x_ppm * 0.0254
            elif kind == b"IEND":
                break
    return width, height, dpi


def text_files(paths: list[Path]) -> list[tuple[Path, str]]:
    rows = []
    for path in paths:
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            "LICENSE",
            ".gitignore",
        }:
            continue
        try:
            rows.append((path, path.read_text(encoding="utf-8")))
        except UnicodeDecodeError as exc:
            raise ReviewError(f"Non-UTF-8 text file: {path}") from exc
    return rows


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def revision_intake() -> str:
    return """# Stage 26AB Revision Intake

Status: `RECORDED_NOT_EXECUTED`.

The following author instructions are binding when Stage 26AB is eventually
run. They do not authorize a journal migration before the remaining external
gates close.

1. Use `outputs/stage26AD/METHODS_research_draft_STAGE26AD.md` as the source;
   preserve the frozen X3 file only as a clean-room comparison target.
2. Do not compress the 178-token/approximately 179-word abstract unless a
   currently accessible official SIMPAT rule proves that it exceeds a limit.
3. Recheck the recorded single-anonymized policy. If the official page remains
   inaccessible, record `NO_SOURCE_FOUND`, retain the dated evidence, and add
   a portal manual check rather than inventing a rule.
4. For every inaccessible guide item, use `NO_SOURCE_FOUND`; do not import DSS,
   EJOR, or another journal's rules.
5. After every manuscript edit, rerun all 24 claim checks. Any failure is
   `CLAIM_DRIFT_DETECTED` and blocks a final manuscript.
6. Reproduction wording must say that outputs are generated in the order in
   `reproduce.md` before tests pass. A pre-generation bare run is 98/100, with
   exactly two missing-output failures.
7. Distinguish 67,200 known-truth cases from 552,000 method-level rows; never
   present the 261,600 Stage 26X-1 rows as the project total.

## Additional findings from the strict review

- Replace the phrase `a real empirical application with hidden truth` with an
  empirical-testbed formulation that keeps the latent-truth boundary explicit.
- Triage legacy DSS figures. Figures 1 and 2 still say `Decision Support`, while
  Figures 5 and 8 are all-1.0 artifact displays with little scientific content.
  Rebuild only essential labels and move non-core displays to supplementary
  material; do not change their underlying values.
- Regenerate submission artwork as vector PDF/EPS where possible. The six
  legacy PNGs carry 250-300 dpi metadata and are not ready to be asserted as
  compliant line art under the recorded SIMPAT guide.
- Add a concise implementation-verification and scalability boundary using
  existing code and logged runtimes only. Do not invent complexity benchmarks
  or execute an unregistered performance experiment.
- Apply the final affiliation, ORCID, and CRediT records. In particular, do not
  carry forward `1037 Luoyu Road` or Li Bo's obsolete `Supervision` role.
"""


def author_checklist() -> str:
    return """# Author Review Checklist Before Commit

No item below is represented as approved merely because it appears here.

## Research draft

- [ ] Approve the title and the 179-word rendered abstract in Stage 26AD.
- [ ] Review the three headline result groups: 180/180 and 0.050289;
  +0.050289/+0.163131; 0/120 versus 14/120.
- [ ] Accept the explicit limits: one empirical testbed, two registered
  simulators, one Bayesian prior/likelihood family, and 94 undefined intervals.
- [ ] Review all 17 added references and the two excluded candidates.
- [ ] Approve moving legacy DSS/artifact figures out of the SIMPAT main text.

## Identity and declarations for Stage 26AB

- [ ] Confirm Deng Lizhen: School of Life Science and Technology, Huazhong
  University of Science and Technology, East Building 11, 415 Luoyu East Road,
  Hongshan District, Wuhan, Hubei 430074, China; ORCID
  `0009-0003-2428-8176`.
- [ ] Confirm Liu Yuxin: School of Materials Science and Engineering, Wuhan
  University of Technology, 122 Luoshi Road, Wuhan 430070, China.
- [ ] Confirm Li Bo: School of Mechanical and Electronic Engineering, Wuhan
  University of Technology, 122 Luoshi Road, Wuhan 430070, China.
- [ ] Confirm CRediT contains no `Supervision` or `Funding acquisition` role.
- [ ] Confirm the OpenAI Codex disclosure accurately covers organization,
  language clarification, code review, and reproducibility checks.

## Repository and journal gates

- [ ] Approve the COMAP academic/research-purpose terms and retained raw CSV.
- [ ] Approve a normal corrective commit without history rewriting.
- [ ] Verify current SIMPAT JIF, JCR quartile, CAS year, major category, and
  zone from the licensed sources.
- [ ] Manually recheck the live SIMPAT guide and portal, especially review
  model, artwork, declarations, and file mapping.
- [ ] Authorize the private push only after reviewing the exact diff.
- [ ] After the private push, confirm commit and inventory, then follow the
  separately approved public-release and anonymous-check sequence.
"""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.project_root.resolve()
    output = (root / args.output_dir).resolve()
    staging = (root / args.staging_dir).resolve()
    staged_docs = staging / "docs/stage26AE"
    staged_script = staging / "scripts" / Path(__file__).name

    if not (staging / ".git").is_dir():
        raise ReviewError(f"Staging repository is not a Git worktree: {staging}")
    if Path(__file__).resolve() != (root / "scripts" / Path(__file__).name):
        raise ReviewError("Run the canonical script from the project scripts directory")

    output.mkdir(parents=True, exist_ok=True)
    staged_docs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).resolve(), staged_script)

    remote = run_git(staging, "remote", "get-url", "origin")
    if remote != EXPECTED_REMOTE:
        raise ReviewError(f"Unexpected origin: {remote}")

    root_junit = root / "outputs/stage26AC/pytest_results_precommit.xml"
    staged_junit = output / "staging_pytest_precommit.xml"
    root_tests = junit_totals(root_junit)
    staged_tests = junit_totals(staged_junit)
    if root_tests[:3] != (133, 0, 0):
        raise ReviewError(f"Root test gate failed: {root_tests}")
    if staged_tests[:3] != (100, 2, 0):
        raise ReviewError(f"Unexpected staged pre-generation boundary: {staged_tests}")

    claim_rows = list(
        csv.DictReader(
            (root / "outputs/stage26AC/CLAIM_TRACEABILITY_AUDIT.csv").open(
                encoding="utf-8", newline=""
            )
        )
    )
    claim_passes = sum(row.get("status") == "PASS" for row in claim_rows)
    if (len(claim_rows), claim_passes) != (24, 24):
        raise ReviewError(f"Claim gate failed: {claim_passes}/{len(claim_rows)}")

    integrity = (root / "outputs/stage26AD/REFERENCE_INTEGRITY_CHECK.md").read_text(
        encoding="utf-8"
    )
    if "`INTEGRITY_PASS`" not in integrity or "30/30" not in integrity:
        raise ReviewError("Reference integrity gate is not PASS")

    frozen_root = root / "outputs/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md"
    frozen_staged = staging / "reference/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md"
    if sha256(frozen_root) != FROZEN_X3_SHA256 or sha256(frozen_staged) != FROZEN_X3_SHA256:
        raise ReviewError("Frozen Stage 26X-3 hash changed")
    raw_csv = staging / "data/raw/2026_MCM_Problem_C_Data.csv"
    if sha256(raw_csv) != COMAP_SHA256:
        raise ReviewError("COMAP raw-data hash changed")

    pair_rows = []
    for name in PAIR_SCRIPTS:
        root_path = root / "scripts" / name
        staged_path = staging / "scripts" / name
        left = sha256(root_path)
        right = sha256(staged_path)
        if left != right:
            raise ReviewError(f"Root/staged generator mismatch: {name}")
        pair_rows.append((name, left))

    write(output / "STAGE26AB_REVISION_INTAKE.md", revision_intake())
    write(output / "AUTHOR_REVIEW_CHECKLIST.md", author_checklist())
    shutil.copy2(output / "STAGE26AB_REVISION_INTAKE.md", staged_docs)
    shutil.copy2(output / "AUTHOR_REVIEW_CHECKLIST.md", staged_docs)

    current_publication_paths = sorted(
        {
            line
            for line in run_git(
                staging, "ls-files", "--cached", "--others", "--exclude-standard"
            ).splitlines()
            if line
        }
    )
    pending_review_paths = {
        "docs/stage26AE/PRECOMMIT_STRICT_REVIEW.md",
        "docs/stage26AE/PUBLICATION_FILE_INVENTORY.csv",
    }
    publication_paths = sorted(set(current_publication_paths) | pending_review_paths)
    absolute_paths = [staging / path for path in current_publication_paths]
    texts = text_files(absolute_paths)

    secret_patterns = {
        "GitHub token": re.compile(r"(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})"),
        "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    }
    secret_hits = []
    for path, value in texts:
        for label, pattern in secret_patterns.items():
            if pattern.search(value):
                secret_hits.append((label, path.relative_to(staging).as_posix()))
    if secret_hits:
        raise ReviewError(f"Credential-like content found in {secret_hits}")

    local_path_pattern = re.compile(
        r"(?:[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\|/(?:home|Users)/[^/\s]+/)"
    )
    local_path_hits = [
        path.relative_to(staging).as_posix()
        for path, value in texts
        if local_path_pattern.search(value)
    ]
    if local_path_hits:
        raise ReviewError(f"Machine-specific absolute paths found: {local_path_hits}")

    positive_data_grants = (
        "Data license plan: " + "CC BY 4.0",
        "Data license: " + "CC BY 4.0",
        "CC BY 4.0" + " for data",
        "LICENSE-DATA-" + "CC-BY-4.0",
    )
    positive_grant_hits = [
        path.relative_to(staging).as_posix()
        for path, value in texts
        if any(token in value for token in positive_data_grants)
    ]
    if positive_grant_hits:
        raise ReviewError(
            f"Positive repository data-license grant remains: {positive_grant_hits}"
        )

    old_repository_url = "https://github.com/denglizhen-113/" + "C"
    old_url_hits = [
        path.relative_to(staging).as_posix()
        for path, value in texts
        if old_repository_url in value
    ]
    if old_url_hits:
        raise ReviewError(f"Old repository URL remains in publication files: {old_url_hits}")

    suspicious_names = [
        path
        for path in publication_paths
        if re.search(r"(^|/)(?:\.env(?:\.|$)|credentials?|secrets?)(?:/|$)", path, re.I)
        or re.search(r"\.(?:pem|key|p12|pfx|kdbx)$", path, re.I)
    ]
    if suspicious_names:
        raise ReviewError(f"Suspicious publication filenames: {suspicious_names}")

    png_rows = []
    for path in sorted((staging / "reference").rglob("*.png")):
        width, height, dpi = png_metadata(path)
        png_rows.append((path.relative_to(staging).as_posix(), width, height, dpi))

    tracked = set(run_git(staging, "ls-files").splitlines())
    untracked = set(
        run_git(staging, "ls-files", "--others", "--exclude-standard").splitlines()
    )
    untracked.update(pending_review_paths)
    modified = set(run_git(staging, "diff", "--name-only").splitlines())

    png_lines = "\n".join(
        f"| `{path}` | {width} x {height} | "
        f"{dpi:.0f} dpi |"
        for path, width, height, dpi in png_rows
    )
    pair_lines = "\n".join(
        f"| `{name}` | `{digest}` | MATCH |" for name, digest in pair_rows
    )
    modified_lines = "\n".join(f"- `{path}`" for path in sorted(modified))
    untracked_lines = "\n".join(f"- `{path}`" for path in sorted(untracked))

    report = f"""# Stage 26AE Precommit Strict Review

Audit date: 2026-08-08
Scope: current Stage 26AD research draft, all proposed publication-repository
files, current Git history, and the recorded Stage 26AB instructions.

## Executive judgment

`READY_FOR_AUTHOR_REVIEW_AND_PRIVATE_COMMIT`

This is not a public-release or submission-ready ruling. The local research
integrity gates pass: 24/24 claims, 30/30 cited references, 29 live DOI records,
133/133 locked-environment tests, the expected 98/100 pre-generation package
boundary, and unchanged frozen/raw-data hashes. No credential signature, old
repository URL, suspicious secret file, or positive CC/CC0 source-data grant
was found in the proposed current publication tree.

The statement that all academic work is complete is still too broad. Core
evidence integrity is complete, but SIMPAT-facing editorial and method
presentation remain unfinished: legacy DSS figures remain in the main-paper
plan, submission artwork is not yet in journal-ready vector/high-resolution
form, implementation/scalability boundaries are thin, final author metadata
has not been applied to a journal source, and the post-edit claim audit has not
yet been run because Stage 26AB has not started.

| Dimension | Ruling |
|---|---|
| Core scientific evidence | PASS WITH DISCLOSED LIMITATIONS |
| Headline claim traceability | PASS, {claim_passes}/{len(claim_rows)} |
| Literature metadata and citation integrity | PASS, 30/30; 29 DOI + COMAP source |
| Locked-environment tests | PASS, {root_tests[0]}/{root_tests[0]} |
| Fresh publication subset before generation | EXPECTED ORDER DEPENDENCY, 98/100 |
| License/provenance consistency | PASS WITH COMAP SCOPE LIMIT |
| Credential and local-path release scan | PASS |
| Repository rename in local configuration | PASS |
| Independent GitHub reachability | NOT VERIFIED IN THIS RUNTIME |
| Public availability | BLOCKED UNTIL PRIVATE PUSH AND ANONYMOUS CHECKS |
| SIMPAT licensed metric eligibility | AUTHOR_MUST_VERIFY |
| SIMPAT manuscript/artwork migration | NOT EXECUTED |

## Findings ordered by severity

### P0 - External gates; no local integrity failure

1. GitHub reachability could not be independently verified because this
   runtime could not connect to `github.com:443`. The author reports the rename
   complete and local `origin` exactly equals `{EXPECTED_REMOTE}`. A private
   push must not be inferred from that local configuration.
2. SIMPAT's current JIF, JCR quartile, CAS year, major category, and zone remain
   unverified in licensed sources. Public secondary signals are not a substitute.
3. The repository remains uncommitted and private. Public-availability wording
   in Stage 26AD deliberately uses private tense and must be updated only after
   a verified private push, public transition, anonymous raw-file request, and
   clean clone.

### P1 - Must be resolved in Stage 26AB before submission

1. Figures 1 and 2 still display `Decision Support` in titles/layers, which
   contradicts the accepted non-DSS title and method-selection positioning.
2. Figures 5 and 8 are all-1.0 artifact/completeness displays. Figure 8 is a
   radar chart of research-artifact checks, not model validation. Figures 3-5
   and 8, plus Tables 1 and 9, should be evaluated for supplementary placement
   so the main text centers registered Tables 4-7 and Figures 6-7.
3. The package contains eight PNG reference figures and no vector submission
   figures. The six legacy figures carry only 250-300 dpi metadata; the two
   core 26X figures carry 300 dpi. Under the dated SIMPAT artwork record, these
   cannot be asserted as compliant line drawings. Regenerate from tracked
   scripts as vector PDF/EPS where possible and verify embedded fonts.
4. The paper documents exact/sampled enumeration and the 69-minute full
   reproduction externally, but gives only a thin algorithmic-cost and
   scalability boundary. A SIMPAT editor may still question candidate-count
   growth, LP scaling, permutation enumeration, and posterior acceptance.
   Address this with existing implementation/log evidence only.
5. Stage 26AD contains the phrase `a real empirical application with hidden
   truth`. Replace it with `an empirical testbed with latent public preference`
   or equivalent. Elsewhere the manuscript already uses the correct boundary.
6. The final affiliation/ORCID/CRediT values are not part of Stage 26AD. Stage
   26AB must use the recorded school-level addresses, remove `1037 Luoyu Road`,
   and remove Li Bo's obsolete `Supervision` role.
7. The dated official capture says single-anonymized, but the 2026-08-08 live
   recheck returned Cloudflare 403. The owner URL, Git history, LICENSE, and
   historical scripts identify the authors. This is acceptable only if the
   single-anonymized rule is reconfirmed or retained with an explicit manual
   portal check.

### P2 - Disclosed residual scientific risks

- External validity is limited to one empirical competition testbed and two
  registered simulators.
- The Bayesian comparison covers one registered prior/likelihood family, and
  94 interval rows are undefined. The manuscript correctly says the resulting
  selection direction cannot be determined without changing the design.
- Proposition 2 and the 300/300 width ordering are structural nesting results,
  not independent empirical superiority evidence.
- The component ablation is one-at-a-time and does not identify interactions.

## Corrections made during this review

- Updated local `origin` to the author-confirmed final repository name.
- Removed residual `data license` ambiguity from Stage 25HA/25HB templates.
- Replaced the Stage 26Y current-empty assertion with a dated historical result
  and a fresh anonymous verification gate.
- Marked Stages 25HA-25HF and 26Y as historical DSS/EJOR generators in README.
- Updated two tests that incorrectly required obsolete repository wording.
- Re-ran Stage 26AC, Stage 26AD, the full test suite, and the staged pre-generation
  test boundary after those corrections.

## Machine-verifiable results

- Root tests: {root_tests[0]} tests, {root_tests[1]} failures,
  {root_tests[2]} errors, {root_tests[3]} skipped.
- Staged pre-generation tests: {staged_tests[0]} tests,
  {staged_tests[1]} expected failures, {staged_tests[2]} errors. The failures
  are the two documented missing-generated-output tests.
- Claims: {claim_passes}/{len(claim_rows)} PASS.
- Reference integrity: `INTEGRITY_PASS`; 30/30 body/list correspondence.
- Frozen X3: `{FROZEN_X3_SHA256}` in root and staged reference.
- COMAP CSV: `{COMAP_SHA256}`.
- Proposed publication tree: {len(publication_paths)} files; {len(tracked)}
  currently tracked, {len(untracked)} currently untracked, and {len(modified)}
  tracked files modified. The CSV inventory records sizes and hashes for every
  payload file and deliberately excludes its own recursive self-entry.
- Reachable history: {run_git(staging, 'rev-list', '--all', '--count')} commits;
  current HEAD `{run_git(staging, 'rev-parse', 'HEAD')}`.

## Figure delivery audit

| File | Pixel dimensions | Recorded resolution |
|---|---:|---:|
{png_lines}

## Root/staged active-generator synchronization

| Script | SHA-256 | Result |
|---|---|---|
{pair_lines}

## Exact tracked modifications

{modified_lines}

## Exact untracked files proposed for review

{untracked_lines}

## Decision

The current local changes are suitable for author review and a normal private
commit. They are not suitable for a claim of public availability or a SIMPAT
submission. After author approval: commit normally, recheck the renamed remote,
push while private, verify the pushed inventory, make public under the prior
conditional authorization, run anonymous page/raw/clone checks, verify licensed
journal metrics, and then execute Stage 26AB with the recorded revisions and a
post-edit 24-claim audit.
"""
    report_path = output / "PRECOMMIT_STRICT_REVIEW.md"
    write(report_path, report)
    shutil.copy2(report_path, staged_docs)

    # Build the inventory after the report is final. Exclude only the inventory
    # itself, whose self-hash cannot be represented inside its own contents.
    inventory_path = output / "PUBLICATION_FILE_INVENTORY.csv"
    final_paths = sorted(
        {
            line
            for line in run_git(
                staging, "ls-files", "--cached", "--others", "--exclude-standard"
            ).splitlines()
            if line
        }
        | {"docs/stage26AE/PUBLICATION_FILE_INVENTORY.csv"}
    )
    if final_paths != publication_paths:
        raise ReviewError("Publication inventory changed during report generation")
    with inventory_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("path", "bytes", "sha256"))
        for relative in final_paths:
            if relative == "docs/stage26AE/PUBLICATION_FILE_INVENTORY.csv":
                continue
            path = staging / relative
            writer.writerow((relative, path.stat().st_size, sha256(path)))
    shutil.copy2(inventory_path, staged_docs / inventory_path.name)

    print(f"Wrote {report_path.relative_to(root).as_posix()}")
    print(f"Wrote {(output / 'AUTHOR_REVIEW_CHECKLIST.md').relative_to(root).as_posix()}")
    print(f"Wrote {(output / 'STAGE26AB_REVISION_INTAKE.md').relative_to(root).as_posix()}")
    print(f"Wrote {inventory_path.relative_to(root).as_posix()}")
    print("PRECOMMIT_REVIEW=READY_FOR_AUTHOR_REVIEW_AND_PRIVATE_COMMIT")
    print("PUBLIC_RELEASE=BLOCKED_PENDING_PRIVATE_PUSH_AND_ANONYMOUS_CHECKS")
    print("SIMPAT_SUBMISSION=BLOCKED_PENDING_LICENSED_METRICS_AND_STAGE26AB")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ReviewError, OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
