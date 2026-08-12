"""Verify the public Stage 26AF-1 repository without GitHub credentials."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import tempfile
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


REPOSITORY_URL = "https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation"
CLONE_URL = REPOSITORY_URL + ".git"
RAW_CSV_URL = (
    "https://raw.githubusercontent.com/denglizhen-113/"
    "coverage-width-tradeoffs-rule-constrained-aggregation/main/"
    "data/raw/2026_MCM_Problem_C_Data.csv"
)
RAW_CSV_SHA256 = "EA99CAEC6EA243BDB450A1971A95BA8A95701A93BE7FF29F0BA3C57D72DDFF52"


class VerificationError(RuntimeError):
    """Raised when a public endpoint or clean clone cannot be verified."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify public repository page, raw CSV, and clean clone access."
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/stage26AE/PUBLIC_RELEASE_ANONYMOUS_VERIFICATION.md"),
    )
    return parser.parse_args(argv)


def request(url: str) -> tuple[int, str, int]:
    request = urllib.request.Request(url, headers={"User-Agent": "C2-public-verification/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read()
        return response.status, response.geturl(), len(payload)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def clean_clone() -> tuple[str, str, str]:
    with tempfile.TemporaryDirectory(prefix="c2-public-anonymous-clone-") as directory:
        destination = Path(directory) / "repository"
        subprocess.run(
            [
                "git",
                "-c",
                "credential.helper=",
                "-c",
                "core.askPass=",
                "-c",
                "credential.interactive=never",
                "clone",
                "--quiet",
                CLONE_URL,
                str(destination),
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        head = subprocess.run(
            ["git", "-C", str(destination), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()
        origin = subprocess.run(
            ["git", "-C", str(destination), "remote", "get-url", "origin"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()
        data_hash = sha256(destination / "data/raw/2026_MCM_Problem_C_Data.csv")
    return head, origin, data_hash


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.project_root.resolve()
    output = (root / args.output).resolve()
    checked_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    page_status, page_final_url, _ = request(REPOSITORY_URL)
    raw_status, raw_final_url, raw_bytes = request(RAW_CSV_URL)
    head, origin, data_hash = clean_clone()
    if page_status != 200 or raw_status != 200:
        raise VerificationError(f"HTTP verification failed: page={page_status}, raw={raw_status}")
    if data_hash != RAW_CSV_SHA256:
        raise VerificationError(f"Clean-clone raw CSV hash mismatch: {data_hash}")
    report = f"""# Stage 26AF-1 Public Release Verification

Checked at (UTC): `{checked_at}`.

All requests below were performed without authenticated GitHub credentials.
The clone explicitly disables Git credential helpers, interactive prompting, and
askpass.

| Check | URL or command | Status | Evidence |
|---|---|---:|---|
| Repository page | `{REPOSITORY_URL}` | HTTP {page_status} | Final URL: `{page_final_url}`. |
| Raw COMAP CSV | `{RAW_CSV_URL}` | HTTP {raw_status} | Final URL: `{raw_final_url}`; {raw_bytes:,} bytes. |
| Clean clone | `git -c credential.helper= -c core.askPass= -c credential.interactive=never clone {CLONE_URL}` | exit 0 | Origin: `{origin}`; `HEAD`: `{head}`; cloned raw CSV SHA-256: `{data_hash}` (expected `{RAW_CSV_SHA256}`). |

Conclusion: `PUBLIC_RELEASE_ANONYMOUS_VERIFICATION_PASS`.

No privacy rollback was required.
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8", newline="\n")
    print(f"Wrote {output.relative_to(root).as_posix()}")
    print("PUBLIC_RELEASE_ANONYMOUS_VERIFICATION=PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError, VerificationError, urllib.error.URLError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
