# Stage 26AC Optimization Changelog

## Frozen boundary

- Source manuscript read only: `outputs/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md`.
- Source SHA-256 before and after: `758755B50CD1C059D939FA550AC151C7B55263348E7BB8B55B40E20FFF1C2D82`.
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
- Abstract word count: 211 ->
  178.

## Verification

- Current tests: 133 total, 0 failures,
  0 errors, 0 skipped.
- Direct staged-package tests before output generation: 100 total,
  2 expected artifact-order failures,
  0 errors, 0 skipped.
- Claim reconciliation fails closed on any mismatch.
