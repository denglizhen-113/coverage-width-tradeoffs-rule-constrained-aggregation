# Stage 26AC Research Audit and Optimization Report

## Executive verdict

The research evidence is internally reproducible and materially stronger than the
current frozen manuscript presentation. All 24/24 audited
headline claims reconcile to tracked CSVs or logged calculations. The existing clean-room
record remains PASS: 16/16 tables and 8/8 figures matched exactly, 1,200 raw files contained
552,000 rows, and the Stage 26X-3 source hash remained `758755B50CD1C059D939FA550AC151C7B55263348E7BB8B55B40E20FFF1C2D82`. The current
Stage 26AC test run reports 133 tests, 0
failures, 0 errors, and 0 skipped.

Scientific submission is not yet unconditionally ready. The primary remaining limitations
are external validity, sensitivity to a single registered Bayesian prior/likelihood family,
94 fixed-draw posterior failures, and the lack of an observed public-vote truth label. Public
release and SIMPAT submission also remain gated by author-controlled repository naming/public
authorization and licensed JIF/JCR/CAS verification.

This stage creates a corrected non-frozen research draft. It does not alter the Stage 26X-3
source, Stage 21-24 artifacts, either preregistration, or any raw experimental output.

## Skill and audit strategy

The official curated `security-best-practices` skill was selected and installed because the
immediate operational risk is publication of a repository containing source-data terms,
author identities, history, and availability claims. No official academic-peer-review skill
was available in the curated catalog, and no untrusted third-party skill was installed.
Scientific review therefore relies on the repository's locked designs, raw outputs, tests,
generated tables, and clean-room verifier rather than a generic checklist.

## Research design review

### What is strong

- The inferential object is correctly bounded as latent public preference, feasible support
  intervals, and partially identified public appeal. The empirical data are not treated as
  observed true audience votes.
- Stage 26X-1 uses 20 preregistered seeds across 15 regions and
  67,200 known-truth synthetic cases. Stage 26X-2 aligns information sets for
  maximum-entropy and Bayesian comparators and adds registered component ablations.
- Evidence is unusually transparent about adverse findings: rule-aware Pareto dominance is
  0/120, whereas Bayesian dominance is
  14/120.
- The elimination effect is localized with paired ablation rather than inferred from an
  uncontrolled between-method difference: coverage changes by
  +0.050289 and width by
  +0.163131 across
  180 positive-noise cells.
- The 300/300 width ordering is correctly treated as a consequence of nesting, not marketed
  as an empirical performance discovery.
- The fixed Bayesian draw-bank failures are retained and disclosed instead of adaptively
  resampled or deleted.

### What the evidence supports

The defensible contribution is a conditional method-selection criterion. When the recorded
elimination rule is treated as reliable, its constraint narrows the feasible set without a
clean-cell coverage loss in this simulator. Under the registered positive-noise process, the
same constraint excludes generated truth in 180/180 cells; removing it restores mean coverage
0.050289 at mean width cost
0.163131. Bayesian intervals are preferable on both registered
metrics in 14/120 clean cells in one external region, while the reverse Pareto direction never
occurs. These are bounded simulator findings, not a universal ranking.

### What the evidence does not support

- No claim that inferred preferences equal true public votes in the empirical application.
- No claim that rule-aware inference uniformly outperforms Bayesian inference.
- No claim of user effectiveness, adoption, trust, welfare, or organizational benefit.
- No cross-regime cardinal comparison between percentage support width and ordinal rank width.
- No general robustness claim over priors, likelihoods, or misspecification processes not in
  the preregistered designs.

## Data and computation audit

| Item | Reconciled result | Assessment |
|---|---:|---|
| Empirical panel | 4,199 rows | PASS |
| Identification features | 2,777; 2,766 typed proxies | PASS; proxy is not observed truth |
| P constraints | 247/248 feasible | PASS; one logged skip |
| R enumeration | 13 exact; 1 sampled at 50,000 draws | PASS; frozen wording was wrong |
| R-plus enumeration | 36 exact; 37 sampled at 10,000 draws | PASS |
| Stage 26X-1 archive | 300 files; 261,600 rows | PASS |
| Stage 26X-2 archive | 900 files; 290,400 rows | PASS |
| Combined archive | 1200 files; 552,000 rows | PASS |
| Insufficient Bayesian posteriors | 94 rows | PASS disclosure; residual sensitivity risk |
| Maximum ranking MCSE | 0.005000 | PASS; numerical only |

The complete line-by-line reconciliation is in `CLAIM_TRACEABILITY_AUDIT.csv`.

## Manuscript audit and corrections

### High-severity defects corrected in the Stage 26AC draft

1. **Positioning/title mismatch.** The frozen source retained the old decision-support title.
   The new draft uses `Coverage-Width Tradeoffs in Rule-Constrained Expert-Crowd Aggregation` and removes the two uncited DSS references.
2. **Incorrect Monte Carlo statement.** The frozen source said all larger fields use 10,000
   permutations. The new draft states 50,000 for the one sampled R week and 10,000 for each of
   37 sampled R-plus weeks, directly matching the ranking summary tables.
3. **Incorrect availability tense.** The frozen source says data and code are available in a
   public repository, although the remote is private. The new draft says the package is prepared
   privately and forbids insertion of a public URL until anonymous access is verified.
4. **Missing source attribution.** The new draft names and cites COMAP in the empirical-data
   section and availability statement, records the official source and hash, and does not
   relicense the data.
5. **Wrong experiment-scale shorthand.** The new abstract distinguishes 67,200
   synthetic cases from 552,000 retained method-level rows; it no longer treats
   261,600 Stage 26X-1 rows as the project total.
6. **Reference hygiene.** Two uncited DSS references and one uncited Netflix reference were
   removed. Remaining references were renumbered and the COMAP source was added. The reference
   count changes from 15 to
   13, with every retained item cited.
7. **Related-work repetition.** A duplicate partial-identification explanation in Section 3.3
   was removed without weakening the discretion/transparency boundary.

The abstract changes from 211 to
178 machine-counted tokens. No target-journal abstract
limit is asserted because a current accessible official SIMPAT numeric limit was not found.

### Residual manuscript risks that require judgment or new work

| Risk | Severity | Why it remains | Safe disposition |
|---|---|---|---|
| External validity | High | One empirical competition testbed and two synthetic generators cannot establish behavior across institutions. | Keep claims conditional; a new external dataset would be a future study. |
| Bayesian specification sensitivity | High | Only the registered Dirichlet/uniform-ranking prior and zero-one likelihood are evaluated. | Do not claim robustness across Bayesian models; preregister any expansion. |
| 94 undefined Bayesian intervals | Medium-high | Defined-interval summaries condition on successful posterior draws. The direction of selection impact is unknown. | Preserve all rows and explicit denominator disclosure; do not post-hoc enlarge the bank. |
| Structural width result | Medium | 300/300 follows set nesting and is not independent validation. | Retain Proposition 2 framing and avoid performance language. |
| Empirical truth unavailable | High | No observed public-vote labels exist. | Use empirical data only as a feasible-set testbed; reserve coverage for known-truth simulation. |
| Literature breadth | Medium | The corrected draft has a focused but small reference base and no systematic recent-literature refresh. | Conduct a separate documented primary-source search before submission; do not insert remembered citations. |
| Journal eligibility | Blocking administrative | SIMPAT JIF/JCR/CAS status is not verified in licensed sources. | Author must verify current year and CAS major-category assignment. |

## Reproducibility and software quality

- The prior clean-room reconstruction took 69.01 minutes and reproduced 16/16 tables and 8/8
  figures exactly; its report remains the authoritative end-to-end verification record.
- The Stage 26AC run independently recounts all 1,200 raw files and 552,000 rows and recomputes
  each headline comparison from raw or paired-cell CSVs.
- Root-level pytest discovery previously entered staged and clean-room copies and failed during
  collection. `pytest.ini` now fixes `tests/` as the only collection root and excludes outputs,
  temporary clean rooms, and local environments.
- The current focused run passes 133 tests with no failures/errors.
- A direct bare `pytest` run inside the current staged publication subset collects
  100 tests: 98 pass and
  2 fail. The failures are `tests.test_robust_aggregation::test_requested_stage_outputs_exist`, `tests.test_specific_journal_submission::test_reference_plan_only_inserts_verified_complete_doi_rows`. Both assert
  the presence of generated tables/data that the staged repository intentionally omits before
  `reproduce.md` is run. This is an execution-order dependency, not a contradictory numerical
  result. The public verification command must therefore follow `reproduce.md`; a fresh clone
  is not honestly described as bare-`pytest` green before generation.
- The development tree contains 24 test files and the staged subset
  contains 18. Files not packaged are: `test_dss_stage23.py`, `test_stage25he_finalization.py`, `test_stage26ac_research_audit.py`, `test_stage26ad_literature_verification.py`, `test_stage26x3_repositioning.py`, `test_stage26y_ejor_submission_migration.py`. This is
  acceptable only if the staged repository is described as the publication subset rather than
  the complete development-history test suite.
- A pandas future-warning path in the active Stage 25H-E audit was replaced with an explicit
  boolean equality count; its numerical output is covered by existing traceability tests.
- All changed scripts retain command-line `--help` behavior. No stochastic operation or seed
  was added or changed.

## Repository, license, and release review

The COMAP file remains anonymously downloadable without login and matches
`EA99CAEC6EA243BDB450A1971A95BA8A95701A93BE7FF29F0BA3C57D72DDFF52`. The source-data copy may remain under the author's stated decision
rule, with COMAP attribution and `DATA_TERMS.md`; it is not open data and is not covered by the
MIT code license.

This stage corrects all six active Stage 25 generators that previously emitted or recommended
an additional data license. Historical generated records remain dated evidence and are not
silently rewritten. The staged repository is intentionally left dirty and private so the author
can review the exact changes before any commit or push.

Public release remains blocked until all of the following are true:

1. The author selects the final repository name.
2. Active URLs and generators are updated to the selected name.
3. The author decides whether a normal corrective commit is sufficient or private history must
   also be rewritten to remove obsolete license statements.
4. The corrected staged package is committed and pushed while private.
5. The author explicitly authorizes public release.
6. The final URL, raw CSV, clone path, and availability statements pass a new anonymous test.

## Submission readiness

| Dimension | Current ruling |
|---|---|
| Core evidence integrity | PASS |
| Headline-number traceability | PASS (24/24) |
| Existing clean-room reproduction | PASS |
| Root test suite | PASS (133/133) |
| Staged bare test run before generation | ORDER-DEPENDENT (98/100 pass) |
| Non-frozen research manuscript | IMPROVED; requires author review |
| Data permission/access gate | PASS WITH ATTRIBUTION AND SCOPE LIMIT |
| Repository public availability | BLOCKED |
| SIMPAT bibliometric eligibility | AUTHOR_MUST_VERIFY |
| SIMPAT live format compliance | NOT YET EXECUTED |
| Overall submission | NOT READY UNTIL AUTHOR GATES CLOSE |

## Recommended next sequence

1. Review `METHODS_research_draft_STAGE26AC.md`, especially the corrected abstract, Monte Carlo
   paragraph, COMAP citation, and truthful availability statement.
2. Select the repository name; the recommended candidate remains
   `coverage-width-tradeoffs-rule-constrained-aggregation`.
3. Decide normal corrective commit versus private-history rewrite for obsolete data-license
   statements. CSV removal is not required under the verified access ruling.
4. Verify SIMPAT's current JIF, JCR Q1, CAS major-category zone, and category assignment in the
   licensed sources.
5. After author approval, synchronize final URLs and package documentation, commit/push while
   private, then authorize public release and repeat anonymous validation.
6. Only after those gates close, execute journal-specific formatting and PDF inspection.

## Files produced by Stage 26AC

- `METHODS_research_draft_STAGE26AC.md`: corrected non-frozen research draft.
- `CLAIM_TRACEABILITY_AUDIT.csv`: computed claim-to-evidence reconciliation.
- `OPTIMIZATION_CHANGELOG.md`: exact scope and frozen-boundary record.
- `RESEARCH_AUDIT_AND_OPTIMIZATION_REPORT.md`: this report.
- `pytest_results.xml`: machine-readable current test run.
- `staging_pytest_results.xml`: machine-readable direct staged-package test boundary.

## Author decisions still required

- Approve or revise the Stage 26AC non-frozen manuscript changes.
- Select the final repository name.
- Choose normal corrective commit or private-history rewrite for obsolete license statements.
- Verify SIMPAT JIF/JCR/CAS eligibility and major-category assignment.
- After private-package review, explicitly authorize rename, push, and later public release.
