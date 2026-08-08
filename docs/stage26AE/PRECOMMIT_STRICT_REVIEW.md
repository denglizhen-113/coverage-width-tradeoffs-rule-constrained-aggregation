# Stage 26AE Precommit Strict Review

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
| Headline claim traceability | PASS, 24/24 |
| Literature metadata and citation integrity | PASS, 30/30; 29 DOI + COMAP source |
| Locked-environment tests | PASS, 133/133 |
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
   complete and local `origin` exactly equals `https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation.git`. A private
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

- Root tests: 133 tests, 0 failures,
  0 errors, 0 skipped.
- Staged pre-generation tests: 100 tests,
  2 expected failures, 0 errors. The failures
  are the two documented missing-generated-output tests.
- Claims: 24/24 PASS.
- Reference integrity: `INTEGRITY_PASS`; 30/30 body/list correspondence.
- Frozen X3: `758755B50CD1C059D939FA550AC151C7B55263348E7BB8B55B40E20FFF1C2D82` in root and staged reference.
- COMAP CSV: `EA99CAEC6EA243BDB450A1971A95BA8A95701A93BE7FF29F0BA3C57D72DDFF52`.
- Proposed publication tree: 318 files; 318
  currently tracked, 2 currently untracked, and 2
  tracked files modified. The CSV inventory records sizes and hashes for every
  payload file and deliberately excludes its own recursive self-entry.
- Reachable history: 2 commits;
  current HEAD `63e84f371bb2bf025f0500aa3ea15c27bdc0c6f4`.

## Figure delivery audit

| File | Pixel dimensions | Recorded resolution |
|---|---:|---:|
| `reference/figures/decision_support_workflow.png` | 2181 x 666 | 250 dpi |
| `reference/figures/disclosure_uncertainty_curve.png` | 2329 x 1339 | 250 dpi |
| `reference/figures/discretion_identifiability_frontier.png` | 1844 x 1230 | 250 dpi |
| `reference/figures/dss_conceptual_framework.png` | 2375 x 1551 | 250 dpi |
| `reference/figures/dss_evaluation_radar.png` | 2075 x 1984 | 300 dpi |
| `reference/figures/rule_robustness_heatmap.png` | 2049 x 879 | 250 dpi |
| `reference/stage26X-1/Figure_06_multiseed_internal_sensitivity.png` | 3491 x 2053 | 300 dpi |
| `reference/stage26X-1/Figure_07_multiseed_external_sensitivity.png` | 3129 x 1524 | 300 dpi |

## Root/staged active-generator synchronization

| Script | SHA-256 | Result |
|---|---|---|
| `25ha_apply_author_provided_information.py` | `2881420383298098EB42CFD109D6BE32CB411013941F05CA086DA0B25F177FD0` | MATCH |
| `25hb_apply_final_author_confirmations.py` | `62274C79C817C02040AE88A4947AE34C49FC849A9DCD48708F2F7A9333517787` | MATCH |
| `25hc_apply_repository_address_and_approval_closure.py` | `0A6E94C4A04E5E326EAEDEED741198A0CBDBA63A0399FB8BA3234C0D6FE5D509` | MATCH |
| `25hd_reconstruct_dss_submission_docx.py` | `1876D67235AFF93795CC1ABF5E83BBDD8111C3EF07FA7B8D0144D0ABAD5BBC62` | MATCH |
| `25he_finalize_dss_submission_package.py` | `B25105BD2355E6F851195B771DF4E883CB801402289E48926D6F9BE521A375CC` | MATCH |
| `25hf_resolve_dss_upload_gate.py` | `C9533F0F7817610519C9083E2439C2831AAF98CDF9F2415F6AD9AE0A7C7C3F86` | MATCH |
| `26y_ejor_submission_migration.py` | `64A600B47E15B582C013829233692D8C0C11441DDB3ADC15E45FA71F574EA8BE` | MATCH |
| `26ac_research_audit_optimization.py` | `B2CE5CA24FE8345FF9A8954459F29FF7DF5DF5E0FB92BAEABF22D9FFF6D9997E` | MATCH |
| `26ac1_repository_publication_readiness.py` | `5253EBDE5E8B82F62ACAF2EFAF58C7CE69C512674E7DA4C83FB718282DD47ECB` | MATCH |
| `26ad_literature_verification.py` | `B58C0EE88FDD32D187D9C0CC5B0CF8556E25E81C53B57575056FA29E8039E9C8` | MATCH |
| `26ae_precommit_strict_review.py` | `0DCD4381B72052C755969A42584C242A0FCCBE6E701AB3AA4AF947FEA0759EF6` | MATCH |

## Exact tracked modifications

- `pytest.ini`
- `scripts/26ae_precommit_strict_review.py`

## Exact untracked files proposed for review

- `docs/stage26AE/PRECOMMIT_STRICT_REVIEW.md`
- `docs/stage26AE/PUBLICATION_FILE_INVENTORY.csv`

## Decision

The current local changes are suitable for author review and a normal private
commit. They are not suitable for a claim of public availability or a SIMPAT
submission. After author approval: commit normally, recheck the renamed remote,
push while private, verify the pushed inventory, make public under the prior
conditional authorization, run anonymous page/raw/clone checks, verify licensed
journal metrics, and then execute Stage 26AB with the recorded revisions and a
post-edit 24-claim audit.
