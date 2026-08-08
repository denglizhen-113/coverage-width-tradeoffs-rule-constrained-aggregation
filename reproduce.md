# Reproduction Commands and Paper Mapping

Run every command from the repository root in the listed order. These are the
commands used by the Stage 26AA clean-room verification; none assumes a
pre-existing processed table, result figure, replication archive, or cache.

Repository URL:
https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation

The order below is part of the reproducibility contract. A direct `pytest`
run before generating the omitted processed data and tables passes 98 of 100
collected staged-package tests; the two failures assert outputs that do not
exist until the preceding generation commands complete. The verified claim is
that tests pass after following this document in order, not that a fresh clone
is bare-`pytest` green before generation.

## Source Data Input

The raw input `data/raw/2026_MCM_Problem_C_Data.csv` is included in this
package. It is the official COMAP 2026 MCM Problem C data file (421
contestant-season rows, 53 columns, 90,002 bytes), byte-identical to the
official download:

- Official problem page:
  https://contest.comap.com/undergraduate/contests/mcm/contests/2026/problems/index.html
- Official data file:
  https://contest.comap.com/undergraduate/contests/mcm/contests/2026/problems/2026_MCM_Problem_C_Data.csv
- SHA-256:
  `EA99CAEC6EA243BDB450A1971A95BA8A95701A93BE7FF29F0BA3C57D72DDFF52`

Use of the file is governed by `DATA_TERMS.md`: COMAP permits reproduction
for academic/research purposes only, and this repository does not relicense
the data. The Stage 26AA clean-room reproduction starts from this included
file; it does not download it. If you redistribute the package, preserve
`DATA_TERMS.md` and the COMAP attribution.

## 1. Environment

```powershell
$env:CONDA_PKGS_DIRS = Join-Path (Get-Location) '.conda-pkgs'
conda create --yes --prefix .conda-env --file conda-lock-win-64.txt
$env:PYTHONNOUSERSITE = '1'
$env:MPLCONFIGDIR = Join-Path (Get-Location) '.mplconfig'
$py = Resolve-Path '.conda-env\python.exe'
& $py -m pip install --no-cache-dir -r requirements.txt -r requirements-docs.txt
```

Expected: an isolated environment, package cache, and Matplotlib configuration
containing the exact win-64 Conda builds and the exact direct versions in both
requirement files. The binary lock is needed
because PyPI and Conda builds with the same NumPy/Pandas/Matplotlib version
produce numerically equivalent tables but not the historical byte hashes and
PNG dimensions used by the Stage 26X-2 protected-input gate. This step creates
no paper result.

## 2. Empirical Audit and Core Inference

```powershell
& $py run_all.py
```

This executes Stages 01-12 from the raw COMAP CSV. Among its outputs are the
audited 4,199-row panel, regime-specific identified sets, empirical summary
tables, and core manuscript inputs. Relevant later inputs include:

- `outputs/tables/identification_comparison_by_regime.csv`
- `outputs/tables/ranking_identification_summary_rplus.csv`
- `outputs/tables/ranking_tie_policy_sensitivity.csv`
- `outputs/tables/uncertainty_by_week_regime_p.csv`

Paper mapping: empirical application in Section 9.5 and the empirical evidence
underlying the model-assumption and claim-boundary discussion. The inferred
quantities are not observed public votes.

## 3. Freeze the Generated Core and Build Stage 21 Inputs

```powershell
& $py run_all.py --overnight-submission
& $py run_all.py --general-submission
& $py scripts/18_specific_journal_submission.py --project-root .
```

The first command builds the Stage 13-16 audit chain required by Stage 17,
including `outputs/logs/overnight_go_no_go_report.md`. Expected downstream
provenance outputs include:

- `outputs/tables/frozen_outputs_hashes.csv`
- `outputs/tables/reference_insertion_plan.csv`

These are provenance inputs for Stages 21-23, not new experimental claims.

## 4. Main Conceptual and Synthetic Figures

```powershell
& $py scripts/21_dss_full_attack.py --project-root .
$stage22Tests = @(
    'tests/test_constraints.py',
    'tests/test_counterfactuals.py',
    'tests/test_decision_analysis_submission.py',
    'tests/test_dss_submission_candidate.py',
    'tests/test_dss_upgrade.py',
    'tests/test_dynamic_preference.py',
    'tests/test_general_submission_strategy.py',
    'tests/test_high_tier_upgrade_strategy.py',
    'tests/test_identification_features.py',
    'tests/test_overnight_submission.py',
    'tests/test_prediction.py',
    'tests/test_preprocessing.py',
    'tests/test_ranking_identification.py',
    'tests/test_robust_aggregation.py',
    'tests/test_specific_journal_submission.py',
    'tests/test_submission_audit.py'
)
& $py -m pytest @stage22Tests -q -p no:cacheprovider
& $py scripts/22_dss_submission_candidate.py --project-root . --tests-passed 69
```

The declared subset is the complete 69-test contract set that existed when
the frozen Stage 22 evaluation figure was generated. The later 26X contracts
are run separately in Section 9. Stage 22 receives `69` only after this command
actually reports `69 passed`.

Command-to-paper mapping:

| Generated output | Paper item |
|---|---|
| `outputs/figures/dss_conceptual_framework.png` | Figure 1 |
| `outputs/figures/decision_support_workflow.png` | Figure 2 |
| `outputs/figures/discretion_identifiability_frontier.png` | Figure 3 |
| `outputs/figures/disclosure_uncertainty_curve.png` | Figure 4 |
| `outputs/figures/rule_robustness_heatmap.png` | Figure 5 |
| `outputs/figures/dss_evaluation_radar.png` | Repository-only artifact-completeness diagnostic (historical Figure 8) |
| `outputs/tables/decision_alternatives_criteria.csv` | Table 1 source |
| `outputs/tables/design_recommendation_matrix.csv` | Table 8 source |

Figures 3-5 are bounded synthetic/configuration diagnostics. The historical
Figure 8 is an artifact-completeness check, not model validation or user
validation. Stage 26AF removes it from the main manuscript but retains the
underlying table, generator, and repository diagnostic.

## 5. Remaining Main Table Sources

```powershell
& $py scripts/23_dss_submission_integrity.py --project-root . --tests-passed 69 --skip-snapshot-reproduction
```

Expected and mapped outputs:

| Generated output | Paper item |
|---|---|
| `outputs/tables/assumption_inventory.csv` | Table 2 source |
| `outputs/tables/baseline_definition_table.csv` | Table 3 source |
| `outputs/tables/claim_evidence_alignment.csv` | Table 9 source |

`--tests-passed 69` records the completed pre-Stage-23 contract run above;
`--skip-snapshot-reproduction` avoids Stage 23's redundant nested workspace.
It does not skip any main table listed here.

## 6. Stage 26X-1 Preregistered Multiseed Experiment

```powershell
& $py scripts/26x1_multiseed_sensitivity.py --mode run --root .
```

This command must generate all of the following from the locked
`outputs/stage26X-1/PREREGISTERED_DESIGN.md`:

- 20 preregistered seeds.
- 12 internal regions: 3 active-set sizes x 4 outcome-noise levels.
- 3 external candidate-round regions.
- 15 parameter regions, 300 seed-region cells/raw files.
- 67,200 simulated cases: 60,000 internal and 7,200 external.
- 261,600 method-level raw rows.

Paper mapping:

| Generated output | Paper item |
|---|---|
| `outputs/stage26X-1/tables/Table4_multiseed.csv` | Table 4 |
| `outputs/stage26X-1/tables/Table5_multiseed.csv` | Table 5 |
| `outputs/stage26X-1/Figure_06_multiseed_internal_sensitivity.png` and `.pdf` | Figure 6 |
| `outputs/stage26X-1/Figure_07_multiseed_external_sensitivity.png` and `.pdf` | Figure 7 |
| `outputs/stage26X-1/ROBUSTNESS_ASSESSMENT.md` | Section 9.1-9.2 claims and intervals |

## 7. Stage 26X-2 Baselines and Ablation

```powershell
& $py scripts/26x2_baselines_ablation.py --mode run --root .
```

The single registered command executes three separate experiment classes:

| Class | Raw directory | Expected files | Expected rows |
|---|---|---:|---:|
| Maximum-entropy baseline | `outputs/stage26X-2/raw/max_entropy/` | 300 | 67,200 |
| Bayesian baseline | `outputs/stage26X-2/raw/bayesian/` | 300 | 67,200 |
| Component ablation | `outputs/stage26X-2/raw/ablation/` | 300 | 156,000 |

Stage 26X-2 total: 900 raw files and 290,400 rows. Stage 26X-1 plus Stage
26X-2 total: 1,200 raw files and 552,000 rows.

Paper mapping:

| Generated output | Paper item |
|---|---|
| `outputs/stage26X-2/tables/attribution_pairwise_cells.csv` and `attribution_regions.csv` | Table 6 and Section 9.3 |
| `outputs/stage26X-2/tables/ablation_paired_effects.csv` and `ablation_effect_summary.csv` | Table 7 and Section 9.4 |
| `outputs/stage26X-2/BASELINE_IMPLEMENTATION.md` | Baseline definition and posterior-status disclosure |
| `outputs/stage26X-2/ABLATION_RESULTS.md` | Component-effect disclosure |
| `outputs/stage26X-2/ATTRIBUTION_RULING.md` | Method-selection boundary |

## 8. Rebuild the Manuscript-Facing Integration

```powershell
& $py scripts/26x3_reposition_manuscript.py --project-root .
```

Expected:
`outputs/stage26X-3/METHODS_submission_draft_STAGE26X3_source.md` plus its
disclosure and positioning reports. Tables 4-7 are rebuilt into this source
from Stage 26X-1/26X-2 outputs. The command does not alter Stage 26W or either
preregistration.

## 9. Focused Contracts and Final Verification

```powershell
& $py -m pytest tests/test_stage26x1_multiseed.py tests/test_stage26x2_baselines_ablation.py -q -p no:cacheprovider
& $py verify_reproduction.py
```

Expected:

- focused tests pass;
- `outputs/reproduction_verification.json` and
  `outputs/reproduction_verification.md` are created;
- every table comparison passes at absolute tolerance `1e-12` with exact
  nonnumeric cells;
- all eight PNGs match their reference pixels;
- raw file/row counts equal the registered totals;
- the rebuilt Stage 26X-3 manuscript is byte-identical to the reference.

This byte-identity check concerns the historical Stage 26X-3 reconstruction.
It does not overwrite or certify the later non-frozen
`manuscript/METHODS_research_draft_STAGE26AD.md`, whose factual corrections and
literature verification are documented under `docs/stage26AC/` and
`docs/stage26AD/`.

## 10. Stage 26AF Presentation Contract

After Stages 26X-1 through 26X-3 have generated their registered outputs, run:

```powershell
& $py scripts/26af_figure_rebuild_complexity.py --root . --source-manuscript manuscript/METHODS_research_draft_STAGE26AD.md --output-dir outputs/stage26AF
& $py -m pytest contracts/test_stage26af_figure_contract.py -q -p no:cacheprovider
```

This stage does not rerun an experiment. It reads existing tracked tables and
logs, creates seven main-manuscript figures as embedded-font vector PDFs and
600 dpi PNGs, retains the former Figure 8 as an unnumbered repository artifact
check, inserts the analytic complexity boundary into a new non-frozen
manuscript, and recomputes the 24-item claim audit.

The historical eight-PNG clean-room contract and the Stage 26AF contract are
separate. The former remains under `reference/figures/` and
`reference/stage26X-1/`; the latter is under `reference/stage26AF/`. The focused
test compares regenerated Stage 26AF PNG hashes with the Stage 26AF reference
manifest when both are present. It never overwrites or repurposes the historical
8/8 pixel record.

## 11. Stage 26AF-1 Final 6+2 Figure Contract

Run this stage only after Stage 26AF has completed. The generator intentionally
replaces its own `outputs/stage26AF-1/` directory on rerun, so do not run the
contract test concurrently with the generator.

```powershell
& $py scripts/26af1_figure5_conversion.py --root . --source-manuscript manuscript/METHODS_research_draft_STAGE26AF.md --stage26af-dir outputs/stage26AF --output-dir outputs/stage26AF-1
& $py -m pytest contracts/test_stage26af1_figure_contract.py -q -p no:cacheprovider
```

The command does not rerun an experiment or calculate a new result. It copies
the retained Stage 26AF PDF/PNG bytes into the final numbering, converts the
former Figure 5 into the final Table 9 `CE10` record, and retains both removed
figures as unnumbered repository diagnostics. The CSV remains at
`outputs/tables/rule_robustness_index.csv` and is also preserved in the Stage
26AF reference package.

Final mapping:

| Stage 26AF-1 output | Final disposition |
|---|---|
| `outputs/stage26AF-1/figures/main/Figure_01_rule_conditioned_inference_architecture.*` | Figure 1 |
| `outputs/stage26AF-1/figures/main/Figure_02_reproducible_comparison_workflow.*` | Figure 2 |
| `outputs/stage26AF-1/figures/main/Figure_03_discretion_identifiability_frontier.*` | Figure 3 |
| `outputs/stage26AF-1/figures/main/Figure_04_compatible_disclosure_scenarios.*` | Figure 4 |
| `outputs/stage26AF-1/figures/main/Figure_05_multiseed_internal_sensitivity.*` | Figure 5 |
| `outputs/stage26AF-1/figures/main/Figure_06_multiseed_external_sensitivity.*` | Figure 6 |
| `outputs/stage26AF-1/figures/repository_diagnostic/RRI_Record_predeclared_conclusions.*` | Unnumbered RRI reproducibility record; source for Table 9 CE10 |
| `outputs/stage26AF-1/figures/repository_diagnostic/Artifact_Check_evidence_completeness.*` | Unnumbered artifact-completeness diagnostic |

The historical 8/8 PNG assertion, the Stage 26AF 7+1 checkpoint, and the Stage
26AF-1 6+2 final contract are stage-scoped and coexist. The Stage 26AF-1 focused
test is under `contracts/`, so the documented pre-generation default result
remains 98/100 with only the two disclosed order-dependent failures.

## Runtime and Storage

The pre-Stage-26AA archive contained 66.41 MiB of 26X raw CSVs: 24.84 MiB for
Stage 26X-1 and 41.57 MiB for Stage 26X-2. No single file exceeded 0.10 MiB,
so GitHub's single-file limit was not the issue; the archive is omitted because
1,200 deterministic raw files are more efficiently regenerated.

Before clean verification, the observed Stage 26X-1 file-write span in the
retained run was about 76 minutes. Stage 26X-2 logged about 476 aggregate
cell-seconds plus summary time. Plan for roughly 1-2 CPU hours for Stage 26X-1
and 10-20 minutes for Stage 26X-2 on a modern four-core desktop, plus the core
pipeline. These are operational estimates, not benchmark claims. The measured
Stage 26AA clean-room times are recorded in the top-level
`outputs/stage26AA/REPRODUCIBILITY_VERIFICATION.md` after execution.
