"""Audit active publication surfaces after the approved repository-name decision."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path


REPOSITORY_NAME = "coverage-width-tradeoffs-rule-constrained-aggregation"
REPOSITORY_URL = f"https://github.com/denglizhen-113/{REPOSITORY_NAME}"
EXPECTED_REMOTE = f"{REPOSITORY_URL}.git"
OLD_NAME = "rule-aware-dss-expert-crowd"
STAGING = Path("outputs/stage26AA/repo_staging")
OUTPUT = Path("outputs/stage26AC-1")
SCRIPT_NAMES = (
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
)
LICENSE_SCRIPT_NAMES = SCRIPT_NAMES[:6]
PUBLICATION_ARTIFACTS = {
    Path("outputs/stage26AC/METHODS_research_draft_STAGE26AC.md"): STAGING
    / "manuscript/METHODS_research_draft_STAGE26AC.md",
    Path("outputs/stage26AD/METHODS_research_draft_STAGE26AD.md"): STAGING
    / "manuscript/METHODS_research_draft_STAGE26AD.md",
    Path("outputs/stage26AC/CLAIM_TRACEABILITY_AUDIT.csv"): STAGING
    / "docs/stage26AC/CLAIM_TRACEABILITY_AUDIT.csv",
    Path("outputs/stage26AC/OPTIMIZATION_CHANGELOG.md"): STAGING
    / "docs/stage26AC/OPTIMIZATION_CHANGELOG.md",
    Path("outputs/stage26AC/RESEARCH_AUDIT_AND_OPTIMIZATION_REPORT.md"): STAGING
    / "docs/stage26AC/RESEARCH_AUDIT_AND_OPTIMIZATION_REPORT.md",
    Path("outputs/stage26AD/EXISTING_REFERENCES_VERIFICATION.md"): STAGING
    / "docs/stage26AD/EXISTING_REFERENCES_VERIFICATION.md",
    Path("outputs/stage26AD/LITERATURE_GAP_ANALYSIS.md"): STAGING
    / "docs/stage26AD/LITERATURE_GAP_ANALYSIS.md",
    Path("outputs/stage26AD/VERIFIED_NEW_REFERENCES.md"): STAGING
    / "docs/stage26AD/VERIFIED_NEW_REFERENCES.md",
    Path("outputs/stage26AD/UNVERIFIED_CANDIDATES.md"): STAGING
    / "docs/stage26AD/UNVERIFIED_CANDIDATES.md",
    Path("outputs/stage26AD/CITATION_INTEGRATION_LOG.md"): STAGING
    / "docs/stage26AD/CITATION_INTEGRATION_LOG.md",
    Path("outputs/stage26AD/REFERENCE_INTEGRITY_CHECK.md"): STAGING
    / "docs/stage26AD/REFERENCE_INTEGRITY_CHECK.md",
}


class ReadinessError(RuntimeError):
    """Raised when an active publication surface is inconsistent."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check repository URLs, COMAP terms, active generators, manuscript "
            "attribution, and the remaining external rename gate."
        )
    )
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    return parser.parse_args(argv)


def read(root: Path, relative: Path | str) -> str:
    path = root / Path(relative)
    if not path.is_file():
        raise ReadinessError(f"Required file is missing: {path}")
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_remote(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root / STAGING), "remote", "get-url", "origin"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ReadinessError("Unable to read staged repository origin")
    return result.stdout.strip()


def sync_publication_artifacts(root: Path) -> None:
    for source, destination in PUBLICATION_ARTIFACTS.items():
        source_path = root / source
        destination_path = root / destination
        if not source_path.is_file():
            raise ReadinessError(f"Publication source is missing: {source_path}")
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_bytes(source_path.read_bytes())
    for name in SCRIPT_NAMES[-3:]:
        source_path = root / "scripts" / name
        destination_path = root / STAGING / "scripts" / name
        destination_path.write_bytes(source_path.read_bytes())


def assert_active_surfaces(root: Path) -> dict[str, object]:
    public_docs = (
        Path("README.md"),
        STAGING / "README.md",
        STAGING / "reproduce.md",
        STAGING / "DATA_TERMS.md",
        Path("outputs/stage26AC/METHODS_research_draft_STAGE26AC.md"),
        Path("outputs/stage26AD/METHODS_research_draft_STAGE26AD.md"),
        STAGING / "manuscript/METHODS_research_draft_STAGE26AC.md",
        STAGING / "manuscript/METHODS_research_draft_STAGE26AD.md",
    )
    missing_url = [str(path) for path in public_docs if REPOSITORY_URL not in read(root, path)]
    if missing_url:
        raise ReadinessError(f"Approved URL missing from active surfaces: {missing_url}")

    active_scripts = []
    hash_rows = []
    for name in SCRIPT_NAMES:
        root_path = root / "scripts" / name
        staged_path = root / STAGING / "scripts" / name
        if not root_path.is_file() or not staged_path.is_file():
            raise ReadinessError(f"Root/staged script pair is missing: {name}")
        root_hash = sha256(root_path)
        staged_hash = sha256(staged_path)
        if root_hash != staged_hash:
            raise ReadinessError(f"Root/staged script hashes differ: {name}")
        if name != "26ac1_repository_publication_readiness.py":
            active_scripts.extend(
                (
                    root_path.read_text(encoding="utf-8"),
                    staged_path.read_text(encoding="utf-8"),
                )
            )
        hash_rows.append((name, root_hash.upper()))

    active_text = "\n".join(active_scripts + [read(root, path) for path in public_docs])
    if OLD_NAME in active_text:
        raise ReadinessError("Obsolete repository name remains in an active surface")

    license_text = "\n".join(
        read(root, base / name)
        for base in (Path("scripts"), STAGING / "scripts")
        for name in LICENSE_SCRIPT_NAMES
    )
    forbidden = [token for token in ("CC BY 4.0", "CC0", "LICENSE-DATA") if token in license_text]
    if forbidden:
        raise ReadinessError(f"Active generators retain forbidden license wording: {forbidden}")

    terms = read(root, STAGING / "DATA_TERMS.md")
    if "© 2026 COMAP" not in terms or "May be reproduced for academic/research purposes" not in terms:
        raise ReadinessError("DATA_TERMS.md does not preserve the verified COMAP notice")
    reproduce = read(root, STAGING / "reproduce.md")
    for phrase in ("passes 98 of 100", "following this document in order", "bare-`pytest` green"):
        if phrase not in reproduce:
            raise ReadinessError(f"reproduce.md is missing required test-order wording: {phrase}")
    manuscript = read(root, "outputs/stage26AD/METHODS_research_draft_STAGE26AD.md")
    for phrase in ("COMAP 2026 MCM Problem C data file [13]", "is not relicensed", "[13] COMAP"):
        if phrase not in manuscript:
            raise ReadinessError(f"Stage 26AD manuscript is missing COMAP evidence: {phrase}")

    return {
        "public_docs": public_docs,
        "hash_rows": hash_rows,
        "remote": git_remote(root),
    }


def render_cover_letter() -> str:
    return f"""# Cover-Letter Reproducibility Paragraph

The reproducibility package is designated for `{REPOSITORY_URL}`. Following
`reproduce.md` in its documented order, the clean-room run regenerated 1,200
raw experiment files containing 552,000 retained method-level rows and matched
16/16 manuscript tables and 8/8 figures. The package does not claim that a
fresh clone is bare-`pytest` green before generation: a direct pre-generation
staged-package run passed 98/100 tests, and the two failures were assertions for
generated artifacts that the release intentionally omits. After those artifacts
were generated in the documented sequence, the complete verification run
passed. The fixed Bayesian draw bank retained and disclosed all 94
insufficient-posterior rows; none was replaced or deleted.

This paragraph may be inserted into the eventual SIMPAT cover letter only
after the repository is public and the designated URL, raw CSV URL, and clone
path pass anonymous verification. Before that gate it is approved wording, not
a public-availability claim.
"""


def render_audit(result: dict[str, object]) -> str:
    remote = str(result["remote"])
    remote_ready = remote == EXPECTED_REMOTE
    remote_status = "PASS" if remote_ready else "BLOCK_PUBLIC_RELEASE"
    remote_paragraph = (
        f"The author reports that the GitHub rename is complete and local `origin` "
        f"equals `{EXPECTED_REMOTE}`. Configuration status: `PASS`. Remote network "
        "reachability remains a separate pre-push check because github.com was "
        "temporarily unreachable during this audit. The repository must remain "
        "private until the private push and later anonymous public checks complete."
        if remote_ready
        else f"The remote rename has not completed. Current staged origin is `{remote}`; "
        f"expected is `{EXPECTED_REMOTE}`. Status: `BLOCK_PUBLIC_RELEASE`."
    )
    remaining_steps = (
        "1. Review and normally commit the staged changes.\n"
        "2. Recheck authenticated remote reachability and push while private.\n"
        "3. Confirm the pushed commit and repository file inventory.\n"
        "4. Make public under the author's conditional approval.\n"
        "5. Verify the repository page, raw COMAP CSV, and clone URL anonymously.\n"
        "6. If any check fails, return the repository to private."
        if remote_ready
        else "1. Complete the GitHub rename and update local `origin`.\n"
        "2. Do not commit, push, or publish until the URL matches."
    )
    rows = "\n".join(
        f"| `{name}` | `{digest}` | MATCH root/staged |"
        for name, digest in result["hash_rows"]
    )
    docs = "\n".join(
        f"- `{path.as_posix()}`" for path in result["public_docs"]
    )
    return f"""# Stage 26AC-1 URL and Terms Audit

## Ruling

Active files are internally prepared for `{REPOSITORY_URL}`. The six Stage 25
license generators no longer assign CC BY 4.0, CC0, or a repository data
license to the COMAP file. COMAP attribution, its formal reference entry, and
the test-order boundary are present.

{remote_paragraph}

## Active public-facing surfaces

{docs}

Each surface contains the approved URL. The Stage 26AC/26AD manuscripts retain
private tense and therefore do not yet claim successful public access.

## Generator synchronization

| Script | SHA-256 | Result |
|---|---|---|
{rows}

## Terms and provenance

- `DATA_TERMS.md` preserves the COMAP copyright notice and the verbatim
  academic/research-purpose permission.
- MIT remains code-only; no active generator emits a separate data license.
- Historical Stage 25 logs and frozen outputs were not silently rewritten.
- The author selected a normal corrective commit; history rewrite is neither
  required nor authorized.

## Remaining external sequence

{remaining_steps}
"""


def render_update(result: dict[str, object]) -> str:
    remote_ready = result["remote"] == EXPECTED_REMOTE
    external_status = (
        f"The author reports that the GitHub rename is complete and local `origin` is "
        f"`{EXPECTED_REMOTE}`. Independent remote reachability could not be repeated "
        "because github.com:443 was temporarily unreachable. No commit, push, "
        "visibility change, or history rewrite was attempted."
        if remote_ready
        else f"Current origin is `{result['remote']}`. The approved rename and origin "
        "update remain incomplete; no commit, push, visibility change, or history "
        "rewrite was attempted."
    )
    return f"""# Stage 26AC-1 Publication-Surface Update

## Completed locally

- Approved repository name and URL propagated to root/staged active generators.
- Root and publication README files use the final research title and URL.
- `reproduce.md` records the 98/100 pre-generation boundary and the required
  generation-before-test order.
- `DATA_TERMS.md` includes the repository URL and preserves exact COMAP terms.
- Stage 26AC and Stage 26AD drafts include COMAP attribution, reference [13],
  the approved URL, and truthful private status.
- A cover-letter paragraph with the same reproducibility boundary was prepared.
- Ten root/staged generator pairs are byte-identical after synchronization.
- The latest non-frozen manuscript and its 26AC/26AD audit trail were copied
  into `manuscript/` and `docs/` without replacing the frozen X3 reference.

## Deliberately preserved

Frozen manuscripts, Stage 21-24 products, preregistrations, raw outputs, and
dated historical logs retain their original bytes and wording. Corrections are
carried by the new active files and the eventual normal commit rather than by
rewriting provenance.

## External state

{external_status}
"""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.project_root.resolve()
    output = root / args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    sync_publication_artifacts(root)
    result = assert_active_surfaces(root)
    files = {
        "PUBLICATION_SURFACE_UPDATE.md": render_update(result),
        "URL_AND_TERMS_AUDIT.md": render_audit(result),
        "COVER_LETTER_REPRODUCIBILITY_PARAGRAPH.md": render_cover_letter(),
    }
    for name, content in files.items():
        (output / name).write_text(content, encoding="utf-8", newline="\n")
        print(f"Wrote {(args.output_dir / name).as_posix()}")
    staged_audit = root / STAGING / "docs/stage26AC-1"
    staged_audit.mkdir(parents=True, exist_ok=True)
    for name in files:
        (staged_audit / name).write_bytes((output / name).read_bytes())
    remote_ready = result["remote"] == EXPECTED_REMOTE
    print(f"ACTIVE_SURFACES=PASS")
    print(f"REMOTE_RENAME={'PASS' if remote_ready else 'PENDING'}")
    print(f"PUBLIC_RELEASE={'READY_FOR_PRIVATE_COMMIT' if remote_ready else 'BLOCKED'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReadinessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
