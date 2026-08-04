# Repository Working Rules

These rules apply to every file and subdirectory in this repository.

## Research integrity

- All code, tables, figures, and reported findings must be reproducible from
  tracked inputs and command-line scripts.
- Never fabricate observations, external validation signals, model results,
  confidence intervals, or citations.
- Do not claim that inferred public preference is the true audience vote.
  Use terms such as *latent public preference*, *feasible support interval*,
  and *partially identified public appeal*.
- Every substantive claim must be traceable to a generated table, figure, or
  logged calculation.

## Data protection and provenance

- Never manually edit, overwrite, move, or delete supplied raw data.
- Work from immutable copies under `data/raw/`; verify copies with a checksum.
- Preserve `0`, parsed missing values, empty strings, and explicit tokens such
  as `N/A` as distinct audit states until their meanings are documented.
- Record every cleaning, normalization, exclusion, imputation, and field
  mapping rule in a generated Markdown report.
- If the observed schema differs from an expected schema, log the difference
  and adapt explicitly; never force the data into an unsupported assumption.

## Code and execution

- Every pipeline script must run from the command line at the project root and
  expose useful `--help` text.
- Use project-relative paths by default; do not hard-code machine-specific
  absolute paths.
- Set and record a fixed random seed for every stochastic operation.
- Save all generated figures, tables, models, and logs under `outputs/` and all
  derived datasets under `data/processed/`.
- Scripts must create their own output directories and be safe to rerun.
- Prefer deterministic, runnable baselines before more complex models.
- Fail with an actionable message when required data or dependencies are
  absent. Optional stages may skip only when the skip is recorded in a report.

## Validation

- Add focused tests for shared parsing, constraint, inference, and aggregation
  logic as those modules are introduced.
- Validate schemas, row counts, key uniqueness, numerical ranges, and output
  existence at stage boundaries.
- Reconcile headline counts and statistics against source data before using
  them in the manuscript.
- Keep assumptions, limitations, and unresolved `TODO` items visible in logs.

## Manuscript and outputs

- Write the paper as a general study of expert-crowd decision systems; use the
  competition data as an empirical testbed rather than the paper's sole topic.
- Do not place manually edited results in `outputs/`. Generated outputs must be
  replaceable by rerunning the responsible script.
- Do not silently update manuscript numbers. Regenerate or verify their source
  table or figure first.

