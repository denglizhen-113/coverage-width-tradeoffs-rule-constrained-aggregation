# Stage 33 MATCOM Reviewer Preflight Report

## Decision

`DO_NOT_SUBMIT`.

The submitted-for-review target is the Stage 32 corrected package, not the
superseded Stage 31.5 package. Stage 32 corrects a substantive coverage metric
and sampled ordinal endpoints; using Stage 31.5 would report a stale coverage
effect and non-sharp ordinal supports. The local package passes its scientific
and technical contracts. The corrected Stage 32 release is publicly versioned;
submission remains blocked only until the Editorial Manager portal facts and
generated PDF are checked.

## Scope and Evidence

- Package: `outputs/stage32-matcom-scientific-corrections/MATCOM_revised_candidate_package`
- Manifested files: `18`; hash reconciliation: `PASS`.
- Corrected positive-noise joint-coverage change: `0.117600` (MCSE `0.001519`); legacy projection-envelope value: `0.050289`.
- Exact ordinal analysis: `87` empirical weeks and `2,964` primary-policy MILP calls.
- Main DOCX: `5` editable tables, `67` Office Math objects, `0` table/body drawing objects, literal TeX commands absent: `PASS`.
- Figure assets: `4` PDF plus `4` TIFF, each numbered 1-4.

## Findings

| ID | Severity | Status | Area | Evidence | Required action |
| --- | --- | --- | --- | --- | --- |
| F01 | P1 | PASS | Corrected public release | Stage 34 independently verified tag matcom-stage32-v1.0.1, commit 4ca87c3381c304ae2f472437bfe21ca51dbc7938, and release SHA-256. | Use the versioned v1.0.1 release; no DOI is asserted. |
| F02 | P0 | EXTERNAL_GATE | Editorial Manager | Article type, review model, upload slots, metadata confirmation, and portal PDF are unavailable locally. | Record the five portal gates and inspect the generated PDF before submission. |
| F03 | P1 | PASS | Scientific correction | Joint coverage and exact ordinal endpoint corrections are generated from Stage 32 raw evidence. | Use Stage 32 only; do not submit the superseded Stage 31.5 package. |
| F04 | P1 | PASS | Mathematics rendering | Office Math=67; literal TeX=False; Unicode math symbols=True. | Retain generated Stage 32 DOCX and visually check the portal PDF. |
| F05 | P1 | PASS | Author metadata | Title page, CRediT, manuscript, and cover letter use the same three named authors and plural approval language. | All authors must still reconfirm this metadata in the portal. |
| F06 | P1 | PASS | Package integrity | Manifest has 18 entries for 18 packaged files. | Do not alter package files after this audit; rerun generator if edits are required. |
| F07 | P2 | PASS | References | In-text citation set=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]; reference set=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]. | Keep citation and reference lists synchronized on further revisions. |
| F08 | P2 | PASS | Figure mapping | PDF figures=4; TIFF figures=4; all files exceed 1 KB. | Confirm the authenticated portal's separate-figure and caption upload instructions. |
| F09 | P2 | PASS | Highlights | Five Highlights detected; lengths=[66, 61, 70, 66, 65]. | Upload only if the live portal exposes or encourages a Highlights slot. |

## Scientific Review

The revised contribution is suitable in principle for a simulation and
computational-methodology venue: it frames the competition record as an
empirical testbed, uses joint membership for polytope coverage, solves ordinal
support endpoints exactly, and states the distinct semantics of identified sets
and Bayesian credible rectangles. The reported uncertainty is bounded by the
specified generators, fixed grid, prior, and uncertain season-28 rule mapping.
The revised manuscript appropriately does not claim observed audience-vote
recovery, a universally superior method, an empirical institutional effect, or
a general polynomial-time result.

The prior Stage 31.5 scientific lock is invalidated for submission purposes:
the corrected effect is `0.117600`, not `0.050289`, and 23 of 470 legacy
sampled ordinal contestant-week rows have at least one endpoint correction.
The Stage 32 source and generated tables are therefore the only defensible
submission basis.

## Technical Review

The current package is structurally stronger than Stage 31.5. It contains a
separate title page, main manuscript, cover letter, Highlights, captions, and
four matching PDF/TIFF figure pairs. The main DOCX carries Word-native tables
and Office Math rather than raw TeX strings. Three-author title-page metadata,
CRediT roles, competing-interest language, generative-AI declaration, and
cover-letter approval language are now mutually consistent. Every listed
reference is cited in the text, and all packaged file hashes reconcile with the
generated manifest.

This preflight cannot assess the PDF that Editorial Manager generates after
upload. It also does not authenticate any external repository, archive, DOI,
author approval, article type, review model, or portal upload mapping.

## Required Human Close-Out

1. In Editorial Manager, record the exact article type, review/anonymization
   model, and file slots. Map only the Stage 32 package files to those slots.
2. Reconfirm the three authors' order, affiliations, ORCIDs, emails, CRediT,
   declarations, and approval of the final portal PDF.
3. Inspect the portal-generated PDF: five tables, 67 mathematical objects,
   figure/caption ordering, references, and special symbols must render without
   truncation or duplication.

## Reproduction

```powershell
& .\.venv-stage26aa-tools\Scripts\python.exe scripts/32_matcom_scientific_corrections.py --project-root .
$env:PYTHONPATH='.'
& .\.venv-stage26aa-tools\Scripts\python.exe -m pytest -q tests/test_stage32_scientific_corrections.py tests/test_stage33_matcom_reviewer_preflight.py
& .\.venv-stage26aa-tools\Scripts\python.exe scripts/33_matcom_reviewer_preflight.py --project-root .
```
