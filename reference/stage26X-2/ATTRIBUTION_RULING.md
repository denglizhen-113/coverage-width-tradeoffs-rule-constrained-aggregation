# Stage 26X-2 Attribution Ruling

## Registered evidence tests

- Stage 26X-1 structural width ordering: `300/300` paired seed-parameter cells (`1.000000`); majority-reversal regions: `0/15`.
- Clean same-information Bayesian comparison: rule-aware Pareto dominance in `0/120` cells (`0.000000`).
- Bayesian Pareto dominance over rule-aware in `14/120` clean cells (`0.116667`); majority-reversal regions: `1`.
- Maximum-entropy point outputs are excluded from the coverage-width Pareto test. Their zero point width is not treated as interval evidence.
- Fixed-draw internal Bayesian rows without a defined posterior: `94` overall, including `10` under zero outcome noise. They remain in the raw evidence; interval metrics use defined-posterior rows and the baseline report separately gives the complete-denominator feasible rate.

## Region evidence

| parameter_region                | synthesizer         |   paired_cells_structural |   width_lower_count |   width_lower_proportion | majority_reversal_structural   |   paired_cells_bayesian |   aware_pareto_count |   aware_pareto_proportion |   bayesian_pareto_count |   bayesian_pareto_proportion |   majority_reversal_bayesian |
|:--------------------------------|:--------------------|--------------------------:|--------------------:|-------------------------:|:-------------------------------|------------------------:|---------------------:|--------------------------:|------------------------:|-----------------------------:|-----------------------------:|
| external candidates=6, rounds=3 | external_ordinal    |                        20 |                  20 |                 1.000000 | False                          |               20.000000 |             0.000000 |                  0.000000 |                0.000000 |                     0.000000 |                     0.000000 |
| external candidates=7, rounds=3 | external_ordinal    |                        20 |                  20 |                 1.000000 | False                          |               20.000000 |             0.000000 |                  0.000000 |               14.000000 |                     0.700000 |                     1.000000 |
| external candidates=7, rounds=4 | external_ordinal    |                        20 |                  20 |                 1.000000 | False                          |               20.000000 |             0.000000 |                  0.000000 |                0.000000 |                     0.000000 |                     0.000000 |
| internal n=4, noise=0.00        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |               20.000000 |             0.000000 |                  0.000000 |                0.000000 |                     0.000000 |                     0.000000 |
| internal n=4, noise=0.05        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |              nan        |           nan        |                nan        |              nan        |                   nan        |                   nan        |
| internal n=4, noise=0.10        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |              nan        |           nan        |                nan        |              nan        |                   nan        |                   nan        |
| internal n=4, noise=0.20        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |              nan        |           nan        |                nan        |              nan        |                   nan        |                   nan        |
| internal n=5, noise=0.00        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |               20.000000 |             0.000000 |                  0.000000 |                0.000000 |                     0.000000 |                     0.000000 |
| internal n=5, noise=0.05        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |              nan        |           nan        |                nan        |              nan        |                   nan        |                   nan        |
| internal n=5, noise=0.10        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |              nan        |           nan        |                nan        |              nan        |                   nan        |                   nan        |
| internal n=5, noise=0.20        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |              nan        |           nan        |                nan        |              nan        |                   nan        |                   nan        |
| internal n=6, noise=0.00        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |               20.000000 |             0.000000 |                  0.000000 |                0.000000 |                     0.000000 |                     0.000000 |
| internal n=6, noise=0.05        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |              nan        |           nan        |                nan        |              nan        |                   nan        |                   nan        |
| internal n=6, noise=0.10        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |              nan        |           nan        |                nan        |              nan        |                   nan        |                   nan        |
| internal n=6, noise=0.20        | internal_percentage |                        20 |                  20 |                 1.000000 | False                          |              nan        |           nan        |                nan        |              nan        |                   nan        |                   nan        |

## Component attribution

The leave-one-out results identify paired changes associated with removing one registered rule component. They do not identify component interactions or effects outside the registered synthetic mechanisms.

| synthesizer         |   n_active |   outcome_noise_probability |   n_candidates |   n_rounds | configuration                |   coverage_improved_count |   paired_cells |   coverage_change_mean |   width_change_mean |
|:--------------------|-----------:|----------------------------:|---------------:|-----------:|:-----------------------------|--------------------------:|---------------:|-----------------------:|--------------------:|
| internal_percentage |   4.000000 |                    0.050000 |            nan |        nan | internal_without_elimination |                        20 |             20 |               0.021400 |            0.179224 |
| internal_percentage |   4.000000 |                    0.100000 |            nan |        nan | internal_without_elimination |                        20 |             20 |               0.045600 |            0.185395 |
| internal_percentage |   4.000000 |                    0.200000 |            nan |        nan | internal_without_elimination |                        20 |             20 |               0.092800 |            0.193859 |
| internal_percentage |   5.000000 |                    0.050000 |            nan |        nan | internal_without_elimination |                        20 |             20 |               0.020800 |            0.156802 |
| internal_percentage |   5.000000 |                    0.100000 |            nan |        nan | internal_without_elimination |                        20 |             20 |               0.040800 |            0.160852 |
| internal_percentage |   5.000000 |                    0.200000 |            nan |        nan | internal_without_elimination |                        20 |             20 |               0.083000 |            0.167003 |
| internal_percentage |   6.000000 |                    0.050000 |            nan |        nan | internal_without_elimination |                        20 |             20 |               0.024000 |            0.138370 |
| internal_percentage |   6.000000 |                    0.100000 |            nan |        nan | internal_without_elimination |                        20 |             20 |               0.040600 |            0.140292 |
| internal_percentage |   6.000000 |                    0.200000 |            nan |        nan | internal_without_elimination |                        20 |             20 |               0.083600 |            0.146386 |

## Unresolved explanations

- The synthetic generators do not establish recovery of latent public preference in an observed population.
- The Bayesian interval depends on the preregistered `Dirichlet(1)` or uniform-ranking prior and the zero-one constraint likelihood; other priors were not tested.
- The leave-one-out design cannot separate component interactions.
- The external pairwise disclosure is synthetic and generated from the simulated latent ordering; no empirical disclosure process was observed.

## Ruling

RULE_AWARE_ADVANTAGE_STRUCTURAL_ONLY

The width ordering remains the structural feasible-set result guaranteed by the added constraints, while the preregistered same-information Pareto threshold is not met. The manuscript contribution must therefore be positioned as a formal partial-identification framework, feasible-set characterization, and quantified coverage-width tradeoff rather than a generally superior inference method.
