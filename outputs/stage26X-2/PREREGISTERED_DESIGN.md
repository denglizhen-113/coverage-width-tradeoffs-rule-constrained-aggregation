# Stage 26X-2 Preregistered Design

## Lock record

- Design version: `26X-2-v1`.
- Preregistered timestamp: `2026-07-29T20:43:13.0621616+08:00` (Asia/Shanghai).
- Stage 26X-1 design SHA256: `e437a81b80143b2f03c81b005d463cc489185d7f781214e8446d1e111784257b`.
- Stage 26X-1 assessment SHA256: `34a18f4090f5bd0628cdca67f31b48690dda350d2fece74ba246a2fd369aa375`.
- Stage 26X-1 Table 4 SHA256: `ff70ea1496853db01267f4edd9942b405b24168e28be9de59b9ec9557078100f`.
- Stage 26X-1 Table 5 SHA256: `485563b5486a8f127ab3b6cec2baaa2556565821069f41ebd340b7e365c84899`.
- Stage 26W manuscript SHA256: `6f1fc33fcd93e099b0ecf85f3f129e94b4aa00be80a42e8dd162bc3d2db45b76`.
- Lock rule: this design is hashed and set read-only before any Stage 26X-2 simulation is run. No baseline definition, seed, parameter cell, repetition count, posterior setting, component toggle, or ruling threshold may be changed after observing results.
- Exclusion rule: no seed, replication, method, component configuration, or parameter cell will be omitted because of its result. A failed cell is reported and rerun only with its original locked inputs.
- Naming prohibition: no implementation, raw file, table, or report may reuse a `prediction_only` name.

## Reused seed and parameter design

The Stage 26X-1 design is reused without alteration.

- Seeds: `seed_i = 20260716 + 1000*i`, `i=0,...,19`.
- Internal grid: `n_active in {4,5,6}` crossed with `outcome_noise_probability in {0.00,0.05,0.10,0.20}`.
- Internal replications: `250` per seed-parameter cell.
- External grid: `(n_candidates,n_rounds) in {(6,3),(7,3),(7,4)}`.
- External replications: `120` per seed-parameter cell.
- Internal generator stream: `seed + round(outcome_noise_probability*1000)`.
- External generator stream: `seed`.

All methods within a seed-parameter-replication cell receive the same generated case. Synthetic latent truth and the generator's noise flag are evaluation-only fields and are never supplied to a fitted baseline or component solver.

## Same-information-set baselines

Two baselines are implemented in separate source files and executed to separate raw directories and logs.

### Baseline A: maximum-entropy center

Internal percentage model:

- Input: active-candidate count, observed expert shares, observed eliminated candidate, and the same documented percentage-elimination inequalities used by `rule_aware_partial_identification`.
- Output: the unique point that maximizes Shannon entropy over the same feasible polytope.
- Solver: SciPy SLSQP minimizes `sum_i p_i log(p_i)` subject to the exact equality, inequality, and bound constraints.
- Numerical settings: `maxiter=500`, `ftol=1e-10`, positivity floor inside the logarithm `1e-12`, feasibility tolerance `1e-8`.
- Initialization: a feasible point returned by `scipy.optimize.linprog`; no synthetic truth is used.

External ordinal model:

- Input: active candidates, observed expert scores, observed elimination, intervention indicator, documented weak-save interpretation, and primary dense-rank tie handling, exactly as for `rule_aware_discretion`.
- The maximum-entropy distribution on the finite compatible ranking set is uniform.
- Output point: the candidate-wise expected rank under that uniform compatible-state distribution.
- Enumeration is exact because the registered cells have at most seven candidates.

Evaluation-only metrics are exact-vector/ranking recovery, normalized mean absolute error, top-choice accuracy, feasibility, and zero point width. Point exact recovery is not treated as interval coverage in the attribution ruling.

### Baseline B: Bayesian latent preference

Internal percentage model:

- Prior: symmetric `Dirichlet(1,...,1)`, uniform on the simplex.
- Likelihood: one for a latent preference vector satisfying the same observed elimination inequalities used by the rule-aware set, zero otherwise.
- Posterior approximation: rejection filtering of `8192` fixed prior draws per seed-parameter cell. The same prior draw bank is reused across replications within that cell, but every case applies its own observed constraints.
- Prior-draw stream: `seed + round(outcome_noise_probability*1000) + 2620000`.
- No adaptive resampling is permitted. If fewer than `100` draws are accepted for a case, that case is marked `insufficient_posterior_draws`; it is not silently enlarged or removed.
- Interval: candidate-wise equal-tail posterior interval at probabilities `0.025` and `0.975`, using NumPy linear quantiles.

External ordinal model:

- Prior: uniform over all strict public-rank permutations.
- Likelihood: one for permutations compatible with the same observed outcome, weak-save interpretation, expert scores, and dense-rank tie handling used by `rule_aware_discretion`, zero otherwise.
- Posterior: exact uniform distribution over compatible permutations.
- Interval: candidate-wise equal-tail posterior rank interval at `0.025` and `0.975`, normalized by `n_candidates-1` for width.

Evaluation-only metrics are simultaneous truth coverage across all candidate intervals, average normalized interval width, posterior-center error, top-choice accuracy, accepted posterior state/draw count, and feasibility.

## Information-set alignment

For both synthesizers, the compared rule-aware method, maximum-entropy center, and Bayesian baseline receive identical substantive inputs: candidate identities, expert shares/scores, observed institutional outcome, and documented rule interpretation. The external methods also receive the same primary tie policy and intervention indicator. None receives synthetic truth, the noise flag, oracle values, or future outcomes. Random draws are computational inputs, not additional institutional information.

## Component ablation

The design is leave-one-out rather than a post-result-selected factorial subset.

Internal percentage synthesizer:

| Configuration | elimination | tie | save | disclosure |
|---|---:|---|---|---|
| `internal_full_rule` | 1 | not applicable | not applicable | not applicable |
| `internal_without_elimination` | 0 | not applicable | not applicable | not applicable |

The internal model has no tie, save, or disclosure component. Those cells are recorded as `not_applicable`; no artificial internal toggle is created.

External ordinal synthesizer:

| Configuration | elimination | tie | save | disclosure |
|---|---:|---:|---:|---:|
| `external_full` | 1 | 1 | 1 | 1 |
| `external_without_elimination` | 0 | 1 | 1 | 1 |
| `external_without_tie_handling` | 1 | 0 | 1 | 1 |
| `external_without_save` | 1 | 1 | 0 | 1 |
| `external_without_disclosure` | 1 | 1 | 1 | 0 |

Definitions:

- `elimination=0`: the observed elimination mask is not applied.
- `tie=0`: exact score ties are deterministically broken by stable candidate order (`ordinal` ranks); this removes the documented tie-equivalence treatment without changing scores or candidate labels.
- `save=0`: intervention rounds are encoded as direct elimination (`weak=False`).
- `disclosure=0`: the existing synthetic top-versus-runner-up pairwise disclosure mask is not applied.
- `external_full`: applies the observed elimination, dense-rank tie policy, weak-save handling on intervention rounds, and the existing synthetic pairwise disclosure.

All ablation configurations are evaluated on the same generated case. Coverage is simultaneous case coverage across rounds; width is the mean normalized compatible-rank width across rounds. Internal outputs also retain the observed outcome-noise indicator.

## Raw outputs and independent logs

- Maximum entropy raw: `outputs/stage26X-2/raw/max_entropy/<synthesizer>_<seed>_<params>.csv`.
- Bayesian raw: `outputs/stage26X-2/raw/bayesian/<synthesizer>_<seed>_<params>.csv`.
- Ablation raw: `outputs/stage26X-2/raw/ablation/<synthesizer>_<seed>_<params>.csv`.
- Independent execution logs: `outputs/stage26X-2/logs/max_entropy_run_log.csv`, `bayesian_run_log.csv`, and `ablation_run_log.csv`.

Each raw row retains seed, all parameter values, replication identifier, method/configuration, coverage or exact-recovery field as applicable, width, error metrics, feasibility, and baseline- or ablation-specific diagnostics. Logs record cell inputs, row count, status, elapsed seconds, output path, and SHA256.

## Summaries and intervals

Raw replication records are first aggregated within seed and parameter cell. Across-seed summaries use the 20 seed-level estimates as statistical units and report mean, median, sample standard deviation (`ddof=1`), and empirical 2.5%/97.5% quantiles with linear interpolation.

A component removal improves coverage when its paired seed-cell coverage is strictly greater than the full configuration. It worsens coverage when strictly lower. Width changes are `removed-component width - full width`.

## Attribution ruling

The ruling is selected by these locked rules:

- `RULE_AWARE_ADVANTAGE_SUBSTANTIATED`: against the Bayesian same-information interval baseline, the rule-aware method has coverage greater than or equal to the baseline and width less than or equal to the baseline in at least 95% of clean internal and external paired seed-parameter cells, with at least one strict inequality in those cells, and no registered parameter region has majority reversal.
- `RULE_AWARE_ADVANTAGE_STRUCTURAL_ONLY`: the Stage 26X-1 rule-aware-versus-rule-agnostic width ordering remains in at least 95% of paired cells, but the preceding same-information Pareto-dominance condition is not met.
- `RULE_AWARE_ADVANTAGE_NOT_SUPPORTED`: the Stage 26X-1 structural width ordering fails in a majority of registered parameter regions, or the Bayesian same-information baseline Pareto-dominates the rule-aware method in at least 50% of clean internal and external paired seed-parameter cells.

Maximum-entropy point outputs are assessed through point error and top-choice accuracy and are not mislabeled as interval coverage. Component attribution is reported separately from this overall ruling, including every removal that improves coverage and its paired width change.

The ruling concerns only the registered synthetic generators, priors, constraints, and grids. It does not establish empirical hidden-preference recovery, user effects, organizational impact, or universal superiority.
