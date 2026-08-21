# MATCOM Stage 32 Public Release Verification

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
| Repository | `https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation` |
| Release tag | `matcom-stage32-v1.0.1` |
| Annotated tag object | `dde60244ab928f301f25a6ba8565fb570b36f5d6` |
| Tagged commit | `4ca87c3381c304ae2f472437bfe21ca51dbc7938` |
| Expected corrected commit | `4ca87c3381c304ae2f472437bfe21ca51dbc7938` |
| Release page | https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation/releases/tag/matcom-stage32-v1.0.1 |
| Asset | `MATCOM_stage32_submission_package_v1.0.1.zip` |
| Asset URL | https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation/releases/download/matcom-stage32-v1.0.1/MATCOM_stage32_submission_package_v1.0.1.zip |
| Asset size | `2852873` bytes |
| GitHub asset digest | `sha256:5dd7bd387f3ab4cce0628a703facaa7193c31f885bac72c3b148926e12462d1f` |
| Downloaded SHA-256 | `5DD7BD387F3AB4CCE0628A703FACAA7193C31F885BAC72C3B148926E12462D1F` |
| ZIP file entries | `51` |

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
& .\.venv-stage26aa-tools\Scripts\python.exe scripts/34_matcom_public_release_verification.py --project-root .
```
