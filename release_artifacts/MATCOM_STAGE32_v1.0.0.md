# MATCOM Stage 32 Corrected Release v1.0.0

This immutable release records the corrected submission basis for *Mathematics
and Computers in Simulation*. It supersedes the local Stage 31.5 candidate.

- Release tag: matcom-stage32-v1.0.0
- Base commit before this release: $base
- Release archive: MATCOM_stage32_submission_package_v1.0.0.zip
- Archive SHA-256: $hash
- Archive contents: corrected Stage 32 generator; exact rank-support and
  joint-polytope implementations; focused Stage 32/33 tests; scientific
  correction tables and reports; Stage 33 reviewer preflight; and the complete
  editable MATCOM submission candidate package.

## Verification

`powershell
& .\.venv-stage26aa-tools\Scripts\python.exe scripts/32_matcom_scientific_corrections.py --project-root .
& .\.venv-stage26aa-tools\Scripts\python.exe scripts/33_matcom_reviewer_preflight.py --project-root .
='.'
& .\.venv-stage26aa-tools\Scripts\python.exe -m pytest -q tests/test_stage32_scientific_corrections.py tests/test_stage33_matcom_reviewer_preflight.py
`

This GitHub release is versioned and publicly downloadable. A persistent
archive DOI is still required before manuscript submission; do not substitute
an unpublished or concept DOI.