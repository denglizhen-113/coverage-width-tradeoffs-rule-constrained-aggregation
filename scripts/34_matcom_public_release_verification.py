#!/usr/bin/env python3
"""Independently verify the public MATCOM Stage 32 v1.0.1 GitHub release.

This audit uses public GitHub endpoints. It ordinarily reads them anonymously;
an optional GitHub CLI fallback can read the same public endpoints if GitHub's
anonymous API rate limit is exhausted. It is intentionally limited to the
public versioned-release subgate: a GitHub release is not treated as a
persistent DOI archive and it cannot replace portal checks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path


REPOSITORY = "denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation"
TAG = "matcom-stage32-v1.0.1"
COMMIT = "4ca87c3381c304ae2f472437bfe21ca51dbc7938"
ASSET = "MATCOM_stage32_submission_package_v1.0.1.zip"
SHA256 = "5DD7BD387F3AB4CCE0628A703FACAA7193C31F885BAC72C3B148926E12462D1F"
OUTPUT = Path("outputs/stage34-matcom-public-release-verification")
API = "https://api.github.com"


class VerificationError(RuntimeError):
    """Raised when a public release invariant does not hold."""


def request_json(url: str, github_cli: Path | None) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "C2-MATCOM-release-verification/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code != 403 or github_cli is None:
            raise
        result = subprocess.run([str(github_cli), "api", url], check=True, capture_output=True, text=True, encoding="utf-8")
        return json.loads(result.stdout)


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"Accept": "application/octet-stream", "User-Agent": "C2-MATCOM-release-verification/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as handle:
        while block := response.read(1024 * 1024):
            handle.write(block)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def relative(root: Path, path: Path) -> Path:
    candidate = (root / path).resolve()
    if root != candidate and root not in candidate.parents:
        raise VerificationError(f"Output resolves outside project root: {path}")
    return candidate


def render(tag_object: str, tag_target: str, release_url: str, asset_url: str, size: int, digest: str, entries: int) -> str:
    return f"""# MATCOM Stage 32 Public Release Verification

## Decision

`F01A_PUBLIC_VERSIONED_RELEASE=PASS`.

The public, annotated GitHub release below is independently retrievable and
its release asset matches the declared SHA-256. This closes only the public
versioned-release component of P0 F01. It does **not** create a persistent DOI
archive or close the Editorial Manager gate; the submission decision remains
`DO_NOT_SUBMIT` until those external facts are recorded.

## Verified Public Evidence

| Field | Verified value |
| --- | --- |
| Repository | `https://github.com/{REPOSITORY}` |
| Release tag | `{TAG}` |
| Annotated tag object | `{tag_object}` |
| Tagged commit | `{tag_target}` |
| Expected corrected commit | `{COMMIT}` |
| Release page | {release_url} |
| Asset | `{ASSET}` |
| Asset URL | {asset_url} |
| Asset size | `{size}` bytes |
| GitHub asset digest | `{digest}` |
| Downloaded SHA-256 | `{SHA256}` |
| ZIP file entries | `{entries}` |

## Archive Layout Check

The downloaded ZIP contains repository-relative entries under all required
prefixes: `outputs/stage32-matcom-scientific-corrections/`, `scripts/`, and
`src/`. This is the correction to the v1.0.0 archive-layout defect. The
earlier v1.0.0 GitHub release is retained only as a prerelease audit record and
is explicitly marked superseded; it must not be cited or submitted.

## Remaining P0 Gates

| Gate | Status | Required verified fact |
| --- | --- | --- |
| F01A: public versioned release | PASS | This report verifies tag, commit, asset, hash, and archive layout. |
| F01B: persistent archive DOI | EXTERNAL_GATE | A published, version-specific DOI landing page from an authorized archive. |
| F01C: DOI-inserted package | PENDING | Regenerate the source package using real DOI metadata, audit it, and create a new release tag. |
| F02: Editorial Manager | EXTERNAL_GATE | Record portal article type, review model, upload mapping, author metadata, and the inspected generated PDF. |

No DOI value is inferred or inserted by this audit. A GitHub release URL is not
represented as a DOI.

## Reproduction

```powershell
& .\\.venv-stage26aa-tools\\Scripts\\python.exe scripts/34_matcom_public_release_verification.py --project-root .
```
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the public MATCOM Stage 32 v1.0.1 GitHub release.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root; defaults to current directory.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT, help="Project-relative generated-report directory.")
    parser.add_argument("--github-cli", type=Path, help="Optional GitHub CLI executable used only if anonymous API access is rate-limited.")
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    output = relative(root, args.output_dir)
    github_cli = args.github_cli.resolve() if args.github_cli else None
    if github_cli is not None and not github_cli.is_file():
        raise VerificationError(f"GitHub CLI executable does not exist: {github_cli}")

    ref = request_json(f"{API}/repos/{REPOSITORY}/git/ref/tags/{TAG}", github_cli)
    if ref["object"]["type"] != "tag":
        raise VerificationError("Release tag must be an annotated Git tag")
    tag = request_json(ref["object"]["url"], github_cli)
    if tag["object"]["type"] != "commit" or tag["object"]["sha"] != COMMIT:
        raise VerificationError(f"Annotated tag target mismatch: {tag['object']}")
    release = request_json(f"{API}/repos/{REPOSITORY}/releases/tags/{TAG}", github_cli)
    assets = [asset for asset in release["assets"] if asset["name"] == ASSET]
    if len(assets) != 1:
        raise VerificationError(f"Expected exactly one release asset named {ASSET}; found {len(assets)}")
    asset = assets[0]
    if asset.get("digest", "").lower() != f"sha256:{SHA256.lower()}":
        raise VerificationError(f"GitHub asset digest mismatch: {asset.get('digest')}")
    with tempfile.TemporaryDirectory(prefix="c2-matcom-v101-") as temp:
        local_asset = Path(temp) / ASSET
        download(asset["browser_download_url"], local_asset)
        local_sha = sha256(local_asset)
        if local_sha != SHA256:
            raise VerificationError(f"Downloaded asset SHA-256 mismatch: {local_sha}")
        with zipfile.ZipFile(local_asset) as archive:
            names = [entry.filename for entry in archive.infolist() if not entry.is_dir()]
    prefixes = ("outputs/stage32-matcom-scientific-corrections/", "scripts/", "src/")
    missing = [prefix for prefix in prefixes if not any(name.startswith(prefix) for name in names)]
    if missing:
        raise VerificationError(f"Release archive lacks repository-relative prefixes: {missing}")
    output.mkdir(parents=True, exist_ok=True)
    report = render(ref["object"]["sha"], tag["object"]["sha"], release["html_url"], asset["browser_download_url"], asset["size"], asset["digest"], len(names))
    (output / "PUBLIC_RELEASE_V101_VERIFICATION.md").write_text(report, encoding="utf-8", newline="\n")
    print("MATCOM_PUBLIC_RELEASE_V101_VERIFICATION=PASS")
    print("F01A_PUBLIC_VERSIONED_RELEASE=PASS")
    print("F01B_PERSISTENT_DOI=EXTERNAL_GATE")
    print("SUBMISSION_DECISION=DO_NOT_SUBMIT_UNTIL_EXTERNAL_GATES_CLOSE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, VerificationError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
