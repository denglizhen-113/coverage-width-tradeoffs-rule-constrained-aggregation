# Stage 26X-2 Same-Information Baseline Implementation

## Protected inputs

- `outputs/stage26X-2/PREREGISTERED_DESIGN.md`: SHA256 `e5418f189061ed295a941327bcf3364081b4095d8b1a1855a416f0431191d19c`.
- `outputs/stage26W/DSS_submission_draft_STAGE26W_source.md`: SHA256 `6f1fc33fcd93e099b0ecf85f3f129e94b4aa00be80a42e8dd162bc3d2db45b76`.
- `outputs/stage26X-1/PREREGISTERED_DESIGN.md`: SHA256 `e437a81b80143b2f03c81b005d463cc489185d7f781214e8446d1e111784257b`.
- `outputs/stage26X-1/ROBUSTNESS_ASSESSMENT.md`: SHA256 `34a18f4090f5bd0628cdca67f31b48690dda350d2fece74ba246a2fd369aa375`.
- `outputs/stage26X-1/tables/Table4_multiseed.csv`: SHA256 `ff70ea1496853db01267f4edd9942b405b24168e28be9de59b9ec9557078100f`.
- `outputs/stage26X-1/tables/Table5_multiseed.csv`: SHA256 `485563b5486a8f127ab3b6cec2baaa2556565821069f41ebd340b7e365c84899`.

## Independent implementations and evidence paths

| Baseline | Implementation file | Functions | Raw outputs | Execution log |
|---|---|---|---|---|
| Maximum-entropy / uniform compatible-state center | `src/max_entropy_center_baseline.py` | `solve_max_entropy_point`; `maximum_entropy_rank_center` | `outputs/stage26X-2/raw/max_entropy/` | `outputs/stage26X-2/logs/max_entropy_run_log.csv` |
| Bayesian latent preference | `src/bayesian_latent_preference_baseline.py` | `truncated_dirichlet_interval`; `exact_rank_posterior_interval` | `outputs/stage26X-2/raw/bayesian/` | `outputs/stage26X-2/logs/bayesian_run_log.csv` |

Maximum-entropy raw cells: `300`; log rows with status `completed` or `reused`: `300`; raw replication rows: `67200`.
Bayesian raw cells: `300`; log rows with status `completed` or `reused`: `300`; raw replication rows: `67200`.

## Information-set alignment

| Information item | Rule-aware comparator | Maximum-entropy center | Bayesian baseline | Alignment |
|---|---|---|---|---|
| Candidate identities and active set | Supplied | Supplied | Supplied | Same |
| Expert shares (internal) or expert scores (external) | Supplied | Supplied | Supplied | Same |
| Observed elimination outcome | Supplied | Supplied | Supplied | Same |
| Percentage-elimination inequalities (internal) | Applied | Applied unchanged | Applied unchanged as zero-one likelihood | Same |
| Dense-rank tie policy and weak-save intervention rule (external) | Applied | Applied unchanged | Applied unchanged as zero-one likelihood | Same |
| Synthetic latent truth | Evaluation only | Evaluation only | Evaluation only | Same; unavailable to fitted methods |
| Outcome-noise flag | Evaluation only | Not supplied | Not supplied | Same substantive information |
| Prior random draws | Not applicable | Not applicable | Computational approximation only | Not institutional information |

The maximum-entropy and Bayesian methods reconstruct each generated case independently from the registered observed inputs. Their raw files and logs are separate, and neither method reads another baseline's output.

## Solver and prior settings

- Internal maximum entropy: SciPy SLSQP over the exact rule-aware polytope; `maxiter=500`, `ftol=1e-10`, log floor `1e-12`, feasibility tolerance `1e-8`; initialization comes from `scipy.optimize.linprog`.
- External maximum entropy: exact enumeration of compatible strict rankings and their uniform-state expected rank.
- Internal Bayesian: symmetric `Dirichlet(1)` prior; `8192` fixed draws per seed-parameter cell; prior stream `seed + round(noise*1000) + 2620000`; no adaptive resampling; minimum accepted draws `100`; equal-tail probabilities `0.025` and `0.975`.
- External Bayesian: exact uniform posterior over compatible strict rankings; equal-tail probabilities `0.025` and `0.975`.

## Point-baseline results

`point_exact_recovery`, normalized mean absolute error, and top-choice accuracy evaluate a point estimate. `point_width=0` is a definition of a point output and is not interval coverage or a feasible-set width advantage.

| synthesizer         |   n_active |   outcome_noise_probability |   n_candidates |   n_rounds | method                      |   seed_count |   point_exact_recovery_mean |   normalized_mean_absolute_error_mean |   top_choice_accuracy_mean |   feasible_mean |
|:--------------------|-----------:|----------------------------:|---------------:|-----------:|:----------------------------|-------------:|----------------------------:|--------------------------------------:|---------------------------:|----------------:|
| internal_percentage |   4.000000 |                    0.000000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.144030 |                   0.222400 |        1.000000 |
| internal_percentage |   4.000000 |                    0.050000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.144908 |                   0.213800 |        1.000000 |
| internal_percentage |   4.000000 |                    0.100000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.144958 |                   0.219200 |        1.000000 |
| internal_percentage |   4.000000 |                    0.200000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.144536 |                   0.210800 |        1.000000 |
| internal_percentage |   5.000000 |                    0.000000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.120930 |                   0.147400 |        1.000000 |
| internal_percentage |   5.000000 |                    0.050000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.120880 |                   0.147400 |        1.000000 |
| internal_percentage |   5.000000 |                    0.100000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.120687 |                   0.140800 |        1.000000 |
| internal_percentage |   5.000000 |                    0.200000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.121183 |                   0.133000 |        1.000000 |
| internal_percentage |   6.000000 |                    0.000000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.103000 |                   0.123600 |        1.000000 |
| internal_percentage |   6.000000 |                    0.050000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.102936 |                   0.121000 |        1.000000 |
| internal_percentage |   6.000000 |                    0.100000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.102980 |                   0.112000 |        1.000000 |
| internal_percentage |   6.000000 |                    0.200000 |     nan        | nan        | maximum_entropy_center      |           20 |                    0.000000 |                              0.103498 |                   0.104800 |        1.000000 |
| external_ordinal    | nan        |                  nan        |       6.000000 |   3.000000 | maximum_entropy_rank_center |           20 |                    0.000000 |                              0.275881 |                   0.147639 |        1.000000 |
| external_ordinal    | nan        |                  nan        |       7.000000 |   3.000000 | maximum_entropy_rank_center |           20 |                    0.000000 |                              0.267285 |                   0.064028 |        1.000000 |
| external_ordinal    | nan        |                  nan        |       7.000000 |   4.000000 | maximum_entropy_rank_center |           20 |                    0.000000 |                              0.274977 |                   0.164688 |        1.000000 |

## Bayesian interval results

Intervals below are the empirical 2.5%-97.5% range of the 20 seed-level metric means. Replications are first averaged within seed and parameter cell.

| synthesizer         |   n_active |   outcome_noise_probability |   n_candidates |   n_rounds | method                          |   seed_count | coverage_seed_interval        | width_seed_interval           |   posterior_center_error_mean |   top_choice_accuracy_mean |   feasible_mean |
|:--------------------|-----------:|----------------------------:|---------------:|-----------:|:--------------------------------|-------------:|:------------------------------|:------------------------------|------------------------------:|---------------------------:|----------------:|
| internal_percentage |   4.000000 |                    0.000000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.885337 [0.845300, 0.910100] | 0.598361 [0.591720, 0.604448] |                      0.127570 |                   0.179915 |        0.999400 |
| internal_percentage |   4.000000 |                    0.050000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.849471 [0.803012, 0.885879] | 0.595175 [0.589822, 0.602808] |                      0.131019 |                   0.173130 |        0.999200 |
| internal_percentage |   4.000000 |                    0.100000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.817457 [0.775052, 0.857530] | 0.589942 [0.581294, 0.597285] |                      0.133028 |                   0.170084 |        0.998200 |
| internal_percentage |   4.000000 |                    0.200000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.756272 [0.716981, 0.787596] | 0.584140 [0.577137, 0.590740] |                      0.136657 |                   0.161473 |        0.997000 |
| internal_percentage |   5.000000 |                    0.000000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.850508 [0.817364, 0.882500] | 0.528934 [0.522116, 0.533438] |                      0.110354 |                   0.081045 |        0.999400 |
| internal_percentage |   5.000000 |                    0.050000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.813572 [0.776000, 0.858100] | 0.526019 [0.520392, 0.531165] |                      0.111472 |                   0.070070 |        0.998800 |
| internal_percentage |   5.000000 |                    0.100000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.791311 [0.744650, 0.838100] | 0.523860 [0.518039, 0.529667] |                      0.112627 |                   0.071973 |        0.997600 |
| internal_percentage |   5.000000 |                    0.200000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.736325 [0.669849, 0.787115] | 0.519478 [0.512760, 0.524954] |                      0.115070 |                   0.067430 |        0.996600 |
| internal_percentage |   6.000000 |                    0.000000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.828263 [0.782919, 0.896600] | 0.469315 [0.465631, 0.472580] |                      0.095605 |                   0.030221 |        0.999200 |
| internal_percentage |   6.000000 |                    0.050000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.799096 [0.752000, 0.839695] | 0.467836 [0.463036, 0.470977] |                      0.096286 |                   0.029614 |        0.999400 |
| internal_percentage |   6.000000 |                    0.100000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.760564 [0.705100, 0.809734] | 0.466052 [0.459560, 0.471803] |                      0.097203 |                   0.031442 |        0.999000 |
| internal_percentage |   6.000000 |                    0.200000 |     nan        | nan        | bayesian_truncated_dirichlet    |           20 | 0.701415 [0.653700, 0.762027] | 0.461983 [0.457284, 0.469700] |                      0.098946 |                   0.026464 |        0.997400 |
| external_ordinal    | nan        |                  nan        |       6.000000 |   3.000000 | bayesian_uniform_rank_posterior |           20 | 0.969167 [0.950000, 0.983333] | 0.921482 [0.915491, 0.928607] |                      0.275881 |                   0.147639 |        1.000000 |
| external_ordinal    | nan        |                  nan        |       7.000000 |   3.000000 | bayesian_uniform_rank_posterior |           20 | 0.997083 [0.987292, 1.000000] | 0.926452 [0.922847, 0.930968] |                      0.267285 |                   0.064028 |        1.000000 |
| external_ordinal    | nan        |                  nan        |       7.000000 |   4.000000 | bayesian_uniform_rank_posterior |           20 | 0.927917 [0.887292, 0.958750] | 0.924903 [0.921430, 0.929231] |                      0.274977 |                   0.164688 |        1.000000 |

### Posterior-status rows

| status                       |   rows |
|:-----------------------------|-------:|
| ok                           |  67106 |
| insufficient_posterior_draws |     94 |

Coverage, width, posterior-center error, and top-choice means are computed only where the fixed draw bank produced a defined posterior. Rows below the registered minimum remain in the raw outputs as `insufficient_posterior_draws`; `feasible_mean` retains the complete replication denominator and reports the defined-posterior rate. No draw bank was enlarged and no raw row was deleted.

The results are generated from the registered synthetic generators. They do not constitute user validation or recovery of true preferences in an observed population.
