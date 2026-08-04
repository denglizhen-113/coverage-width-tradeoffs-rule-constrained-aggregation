# Stage 26X-1 Preregistered Design

## Lock record

- Design version: `26X-1-v1`.
- Preregistered timestamp: `2026-07-29T12:16:58.6473797+08:00` (Asia/Shanghai).
- Baseline manuscript: `outputs/stage26W/DSS_submission_draft_STAGE26W_source.md`.
- Baseline manuscript SHA256 before experiment: `6f1fc33fcd93e099b0ecf85f3f129e94b4aa00be80a42e8dd162bc3d2db45b76`.
- Lock rule: this file is hashed and set read-only before any Stage 26X-1 simulation is run. Seeds, grids, repetitions, metrics, and ruling rules below will not be changed after observing results.
- Exclusion rule: no seed, replication, method, or parameter condition will be removed because of its result. Execution failures, if any, remain logged and are rerun only with the same preregistered inputs.
- Removed alias: `prediction_only_judge_proxy` is excluded from every Stage 26X-1 raw file, summary, and figure. It is not an independently executed method.

## Seeds

The 20 seeds are generated before execution by the fixed rule

`seed_i = 20260716 + 1000 * i`, for `i = 0, 1, ..., 19`.

The locked list is:

`20260716, 20261716, 20262716, 20263716, 20264716, 20265716, 20266716, 20267716, 20268716, 20269716, 20270716, 20271716, 20272716, 20273716, 20274716, 20275716, 20276716, 20277716, 20278716, 20279716`.

The same list is used for the internal percentage synthesizer and the external ordinal synthesizer. Seed `20260716` is the original manuscript seed.

## Internal percentage synthesizer

Implementation inputs remain the existing project functions in `src/dss_common.py` and `src/synthetic_benchmark.py`. Stage 26X-1 adds a separate command-line runner that preserves replication-level records without modifying those source modules.

| Parameter | Locked values | Role |
|---|---|---|
| `n_active` | `4, 5, 6` | Candidate-count sensitivity; original value is 5. |
| `outcome_noise_probability` | `0.00, 0.05, 0.10, 0.20` | Correct-rule condition and three misspecification stress levels; original stress value is 0.10. |
| `n_replications` | `250` per seed and parameter cell | Same as the original Table 4 experiment. |
| `public_concentration` | `1.2` | Held at the existing generator default. |
| `judge_public_correlation` | `0.35` | Held at the existing generator default. |

Full factorial cells: `3 candidate counts x 4 noise levels = 12` per seed, `240` seed-parameter raw files, and `60,000` simulated cases. Each case records four supported methods: `rule_aware_partial_identification`, `rule_agnostic_partial_identification`, `naive_point_estimation`, and `full_disclosure_oracle_synthetic_only`.

For compatibility with the original generator, the random stream for one internal cell uses `seed + round(noise_probability * 1000)`.

## External ordinal synthesizer

The new runner calls the existing `_case()` and `_round_metrics()` logic in `src/external_testbed.py` and exposes only parameter combinations allowed by `_case()` (`n_candidates >= n_rounds + 3`).

| Cell | `n_candidates` | `n_rounds` | Intervention rounds implied by existing generator | Repetitions per seed |
|---|---:|---:|---|---:|
| E1 | 6 | 3 | round 2 only (`1 of 3`) | 120 |
| E2 | 7 | 3 | round 2 only (`1 of 3`) | 120 |
| E3 | 7 | 4 | rounds 2 and 4 (`2 of 4`); original Table 5 setting | 120 |

Other existing settings remain fixed: public Dirichlet concentration `1.4`, independent-expert Dirichlet concentration `1.1`, expert/public mixture `0.58/0.42`, primary tie policy `dense_rank`, and sensitivity policies `average_rank`, `min_rank`, `dense_rank`, `competition_rank`.

There are `3` parameter cells per seed, `60` seed-parameter raw files, and `7,200` external simulated cases. Each case records `rule_aware_discretion`, `direct_rule_misspecification`, and `rule_agnostic_ordinal`.

## Raw outputs

One CSV is written per synthesizer, seed, and parameter cell:

- Internal: `outputs/stage26X-1/raw/internal_seed-<seed>_n-<n_active>_noise-<noise>.csv`.
- External: `outputs/stage26X-1/raw/external_seed-<seed>_candidates-<n_candidates>_rounds-<n_rounds>.csv`.

Every row includes synthesizer, seed, all parameter values, replication number, method, coverage, width, and every metric reported by the original experiment. Internal files additionally retain `observed_outcome_noise`, `false_certainty`, `baseline_error`, `outcome_consistent`, and `feasible`. External files additionally retain `false_certainty`, `rule_robustness_index`, `disclosure_uncertainty_reduction`, and `recommendation_stability`.

## Summary tables and statistics

The runner first aggregates each method/parameter cell within seed. `Table4_multiseed.csv` and `Table5_multiseed.csv` then summarize the 20 seed-level estimates. Seeds, not individual replications, are the units for dispersion and quantiles.

For every reported metric the locked statistics are:

- arithmetic mean;
- median;
- sample standard deviation (`ddof=1`);
- empirical 2.5% quantile using pandas linear interpolation;
- empirical 97.5% quantile using pandas linear interpolation.

The tables also report `n_seeds=20`, repetitions per seed, total replication count, synthesizer parameters, and method.

## Stability definitions

All comparisons are paired within the same seed and parameter cell.

1. Width ordering stability: proportion of paired seed-parameter cells in which rule-aware mean width is strictly below the corresponding rule-agnostic/simplex-only mean width. Ties are not counted as lower.
2. Coverage tradeoff stability: proportion of paired seed-parameter cells in which rule-aware coverage is strictly below the corresponding rule-agnostic/simplex-only coverage. Clean and positive-noise cells are reported separately.
3. Coverage decline: `simplex-only coverage - rule-aware coverage` within each internal seed-parameter cell. Its mean, sample standard deviation, median, and 2.5%/97.5% empirical quantiles are reported.
4. Original-seed position: for each original parameter cell, the seed-20260716 value is ranked within all 20 seed-level values. Percentile rank uses average rank divided by 20. Values at or below 0.10 or at or above 0.90 are classified as tail; other values are classified as non-tail. Exact ties are reported.
5. Reversal region: a parameter cell is a reversal if the mean rule-aware width is greater than the comparator width, or if the preregistered ordering holds in fewer than half of its 20 seeds. Every such cell is listed.

## Robustness ruling rule

- `CONCLUSIONS_ROBUST_ACROSS_SEEDS`: width ordering holds in at least 95% of all paired internal and external seed-parameter cells; no parameter cell has majority reversal; clean internal coverage is not below simplex-only in any seed; all positive-noise coverage declines are reported without requiring them to be zero.
- `CONCLUSIONS_PARTIALLY_ROBUST`: width ordering holds in at least 50% but less than 95% of paired cells, or at least one parameter cell has a majority reversal, or clean coverage is below simplex-only in any seed while some preregistered parameter regions retain the ordering.
- `CONCLUSIONS_NOT_ROBUST`: width ordering holds in fewer than 50% of paired cells, or the claimed direction fails across the majority of preregistered parameter regions.

The ruling concerns the stated simulators and grids only. It does not establish user effects, organizational impact, or empirical recovery of hidden preferences.

## Figures

Figure 6 and Figure 7 use the seed-level distributions and show both coverage and width with 2.5%–97.5% empirical interval bars. Figure 6 facets the three internal candidate counts and displays the four noise conditions. Figure 7 displays the three external parameter cells. Existing metric colors are retained: green for coverage, blue for width, and the existing orange/red only where false certainty or related diagnostics are shown. PNG and vector PDF are produced from the same Matplotlib canvas; Times New Roman is embedded in PDF.
