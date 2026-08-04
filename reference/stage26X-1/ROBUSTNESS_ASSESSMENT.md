# Stage 26X-1 Robustness Assessment

## Execution and evidence scope

- Preregistered design SHA256: `e437a81b80143b2f03c81b005d463cc489185d7f781214e8446d1e111784257b`.
- Seeds: `20`; internal raw cells: `240`; external raw cells: `60`.
- Internal simulated cases: `60000`; external simulated cases: `7200`.
- Dispersion and quantiles use seed-level estimates; replications are not treated as independent statistical units.
- `prediction_only_judge_proxy` is absent from all Stage 26X-1 raw files, summaries, and figures.
- These are synthetic-simulator sensitivity results, not user validation or empirical recovery of true public preferences.

## Width ordering

Across internal and external paired seed-parameter cells, rule-aware width is strictly below the rule-agnostic comparator in `300/300` cells (`1.000000`).
Internal count: `240/240`. External count: `60/60`.

### Internal parameter regions

|   n_active |   outcome_noise_probability |   paired_seeds |   width_lower_count |   width_lower_proportion |   coverage_lower_count |   coverage_lower_proportion |   aware_width_mean |   comparator_width_mean |
|-----------:|----------------------------:|---------------:|--------------------:|-------------------------:|-----------------------:|----------------------------:|-------------------:|------------------------:|
|   4.000000 |                    0.000000 |      20.000000 |           20.000000 |                 1.000000 |               0.000000 |                    0.000000 |           0.824777 |                1.000000 |
|   4.000000 |                    0.050000 |      20.000000 |           20.000000 |                 1.000000 |              20.000000 |                    1.000000 |           0.820776 |                1.000000 |
|   4.000000 |                    0.100000 |      20.000000 |           20.000000 |                 1.000000 |              20.000000 |                    1.000000 |           0.814605 |                1.000000 |
|   4.000000 |                    0.200000 |      20.000000 |           20.000000 |                 1.000000 |              20.000000 |                    1.000000 |           0.806141 |                1.000000 |
|   5.000000 |                    0.000000 |      20.000000 |           20.000000 |                 1.000000 |               0.000000 |                    0.000000 |           0.846346 |                1.000000 |
|   5.000000 |                    0.050000 |      20.000000 |           20.000000 |                 1.000000 |              20.000000 |                    1.000000 |           0.843198 |                1.000000 |
|   5.000000 |                    0.100000 |      20.000000 |           20.000000 |                 1.000000 |              20.000000 |                    1.000000 |           0.839148 |                1.000000 |
|   5.000000 |                    0.200000 |      20.000000 |           20.000000 |                 1.000000 |              20.000000 |                    1.000000 |           0.832997 |                1.000000 |
|   6.000000 |                    0.000000 |      20.000000 |           20.000000 |                 1.000000 |               0.000000 |                    0.000000 |           0.864107 |                1.000000 |
|   6.000000 |                    0.050000 |      20.000000 |           20.000000 |                 1.000000 |              20.000000 |                    1.000000 |           0.861630 |                1.000000 |
|   6.000000 |                    0.100000 |      20.000000 |           20.000000 |                 1.000000 |              20.000000 |                    1.000000 |           0.859708 |                1.000000 |
|   6.000000 |                    0.200000 |      20.000000 |           20.000000 |                 1.000000 |              20.000000 |                    1.000000 |           0.853614 |                1.000000 |

### External parameter regions

|   n_candidates |   n_rounds |   paired_seeds |   width_lower_count |   width_lower_proportion |   coverage_lower_count |   coverage_lower_proportion |   aware_width_mean |   comparator_width_mean |
|---------------:|-----------:|---------------:|--------------------:|-------------------------:|-----------------------:|----------------------------:|-------------------:|------------------------:|
|       6.000000 |   3.000000 |      20.000000 |           20.000000 |                 1.000000 |               0.000000 |                    0.000000 |           0.954234 |                1.000000 |
|       7.000000 |   3.000000 |      20.000000 |           20.000000 |                 1.000000 |               0.000000 |                    0.000000 |           0.961905 |                1.000000 |
|       7.000000 |   4.000000 |      20.000000 |           20.000000 |                 1.000000 |               0.000000 |                    0.000000 |           0.959115 |                1.000000 |

## Coverage tradeoff

Clean internal cells with rule-aware coverage below simplex-only coverage: `0/60`.
Positive-noise internal cells with rule-aware coverage below simplex-only coverage: `180/180`.
Coverage decline (`simplex-only - rule-aware`) across positive-noise seed-parameter cells: mean `0.050289`, median `0.044000`, sample std `0.029666`, empirical 2.5%-97.5% interval `[0.012000, 0.108000]`.

## Original seed position

Percentile rank is average rank divided by 20; values at or below 0.10 or at or above 0.90 are classified as tail.

| cell                           | method                               | metric                     |   original_seed_value |   percentile_rank | classification   |   exact_ties |
|:-------------------------------|:-------------------------------------|:---------------------------|----------------------:|------------------:|:-----------------|-------------:|
| internal n=5 noise=0.00        | rule_aware_partial_identification    | coverage_rate              |              1.000000 |          0.525000 | non-tail         |           20 |
| internal n=5 noise=0.00        | rule_aware_partial_identification    | average_feasible_set_width |              0.845468 |          0.300000 | non-tail         |            1 |
| internal n=5 noise=0.00        | rule_agnostic_partial_identification | coverage_rate              |              1.000000 |          0.525000 | non-tail         |           20 |
| internal n=5 noise=0.00        | rule_agnostic_partial_identification | average_feasible_set_width |              1.000000 |          0.525000 | non-tail         |           20 |
| internal n=5 noise=0.10        | rule_aware_partial_identification    | coverage_rate              |              0.948000 |          0.150000 | non-tail         |            1 |
| internal n=5 noise=0.10        | rule_aware_partial_identification    | average_feasible_set_width |              0.836233 |          0.150000 | non-tail         |            1 |
| internal n=5 noise=0.10        | rule_agnostic_partial_identification | coverage_rate              |              1.000000 |          0.525000 | non-tail         |           20 |
| internal n=5 noise=0.10        | rule_agnostic_partial_identification | average_feasible_set_width |              1.000000 |          0.525000 | non-tail         |           20 |
| external candidates=7 rounds=4 | rule_aware_discretion                | coverage_rate              |              1.000000 |          0.525000 | non-tail         |           20 |
| external candidates=7 rounds=4 | rule_aware_discretion                | average_feasible_set_width |              0.960461 |          0.800000 | non-tail         |            1 |
| external candidates=7 rounds=4 | rule_agnostic_ordinal                | coverage_rate              |              1.000000 |          0.525000 | non-tail         |           20 |
| external candidates=7 rounds=4 | rule_agnostic_ordinal                | average_feasible_set_width |              1.000000 |          0.525000 | non-tail         |           20 |

## Reversal regions

No preregistered parameter region meets the reversal definition.

## Original-setting reproduction

All `66` metric comparisons for seed 20260716 at the original internal and external settings match the historical Table 4/Table 5 source CSV values within absolute tolerance `1e-12`: `true`.

| cell                           | method                                | metric                           |           current |        historical | matches   |
|:-------------------------------|:--------------------------------------|:---------------------------------|------------------:|------------------:|:----------|
| internal n=5 noise=0.00        | rule_aware_partial_identification     | coverage_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.00        | rule_aware_partial_identification     | average_feasible_set_width       |   0.845467843945  |   0.845467843945  | True      |
| internal n=5 noise=0.00        | rule_aware_partial_identification     | false_certainty_rate             |   0               |   0               | True      |
| internal n=5 noise=0.00        | rule_aware_partial_identification     | baseline_error                   | nan               | nan               | True      |
| internal n=5 noise=0.00        | rule_aware_partial_identification     | outcome_consistency_rate         |   1               |   1               | True      |
| internal n=5 noise=0.00        | rule_aware_partial_identification     | feasible_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.00        | rule_agnostic_partial_identification  | coverage_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.00        | rule_agnostic_partial_identification  | average_feasible_set_width       |   1               |   1               | True      |
| internal n=5 noise=0.00        | rule_agnostic_partial_identification  | false_certainty_rate             |   0               |   0               | True      |
| internal n=5 noise=0.00        | rule_agnostic_partial_identification  | baseline_error                   | nan               | nan               | True      |
| internal n=5 noise=0.00        | rule_agnostic_partial_identification  | outcome_consistency_rate         |   1               |   1               | True      |
| internal n=5 noise=0.00        | rule_agnostic_partial_identification  | feasible_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.00        | naive_point_estimation                | coverage_rate                    |   0               |   0               | True      |
| internal n=5 noise=0.00        | naive_point_estimation                | average_feasible_set_width       |   0               |   0               | True      |
| internal n=5 noise=0.00        | naive_point_estimation                | false_certainty_rate             |   1               |   1               | True      |
| internal n=5 noise=0.00        | naive_point_estimation                | baseline_error                   |   0.108614635543  |   0.108614635543  | True      |
| internal n=5 noise=0.00        | naive_point_estimation                | outcome_consistency_rate         |   0.712           |   0.712           | True      |
| internal n=5 noise=0.00        | naive_point_estimation                | feasible_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.00        | full_disclosure_oracle_synthetic_only | coverage_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.00        | full_disclosure_oracle_synthetic_only | average_feasible_set_width       |   0               |   0               | True      |
| internal n=5 noise=0.00        | full_disclosure_oracle_synthetic_only | false_certainty_rate             |   0               |   0               | True      |
| internal n=5 noise=0.00        | full_disclosure_oracle_synthetic_only | baseline_error                   |   0               |   0               | True      |
| internal n=5 noise=0.00        | full_disclosure_oracle_synthetic_only | outcome_consistency_rate         |   1               |   1               | True      |
| internal n=5 noise=0.00        | full_disclosure_oracle_synthetic_only | feasible_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.10        | rule_aware_partial_identification     | coverage_rate                    |   0.948           |   0.948           | True      |
| internal n=5 noise=0.10        | rule_aware_partial_identification     | average_feasible_set_width       |   0.836232636848  |   0.836232636848  | True      |
| internal n=5 noise=0.10        | rule_aware_partial_identification     | false_certainty_rate             |   0               |   0               | True      |
| internal n=5 noise=0.10        | rule_aware_partial_identification     | baseline_error                   | nan               | nan               | True      |
| internal n=5 noise=0.10        | rule_aware_partial_identification     | outcome_consistency_rate         |   1               |   1               | True      |
| internal n=5 noise=0.10        | rule_aware_partial_identification     | feasible_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.10        | rule_agnostic_partial_identification  | coverage_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.10        | rule_agnostic_partial_identification  | average_feasible_set_width       |   1               |   1               | True      |
| internal n=5 noise=0.10        | rule_agnostic_partial_identification  | false_certainty_rate             |   0               |   0               | True      |
| internal n=5 noise=0.10        | rule_agnostic_partial_identification  | baseline_error                   | nan               | nan               | True      |
| internal n=5 noise=0.10        | rule_agnostic_partial_identification  | outcome_consistency_rate         |   1               |   1               | True      |
| internal n=5 noise=0.10        | rule_agnostic_partial_identification  | feasible_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.10        | naive_point_estimation                | coverage_rate                    |   0               |   0               | True      |
| internal n=5 noise=0.10        | naive_point_estimation                | average_feasible_set_width       |   0               |   0               | True      |
| internal n=5 noise=0.10        | naive_point_estimation                | false_certainty_rate             |   1               |   1               | True      |
| internal n=5 noise=0.10        | naive_point_estimation                | baseline_error                   |   0.102565589351  |   0.102565589351  | True      |
| internal n=5 noise=0.10        | naive_point_estimation                | outcome_consistency_rate         |   0.66            |   0.66            | True      |
| internal n=5 noise=0.10        | naive_point_estimation                | feasible_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.10        | full_disclosure_oracle_synthetic_only | coverage_rate                    |   1               |   1               | True      |
| internal n=5 noise=0.10        | full_disclosure_oracle_synthetic_only | average_feasible_set_width       |   0               |   0               | True      |
| internal n=5 noise=0.10        | full_disclosure_oracle_synthetic_only | false_certainty_rate             |   0               |   0               | True      |
| internal n=5 noise=0.10        | full_disclosure_oracle_synthetic_only | baseline_error                   |   0               |   0               | True      |
| internal n=5 noise=0.10        | full_disclosure_oracle_synthetic_only | outcome_consistency_rate         |   0.884           |   0.884           | True      |
| internal n=5 noise=0.10        | full_disclosure_oracle_synthetic_only | feasible_rate                    |   1               |   1               | True      |
| external candidates=7 rounds=4 | rule_aware_discretion                 | coverage_rate                    |   1               |   1               | True      |
| external candidates=7 rounds=4 | rule_aware_discretion                 | average_feasible_set_width       |   0.960461309524  |   0.960461309524  | True      |
| external candidates=7 rounds=4 | rule_aware_discretion                 | false_certainty_rate             |   0               |   0               | True      |
| external candidates=7 rounds=4 | rule_aware_discretion                 | rule_robustness_index            |   0.941666666667  |   0.941666666667  | True      |
| external candidates=7 rounds=4 | rule_aware_discretion                 | disclosure_uncertainty_reduction |   0.125248015873  |   0.125248015873  | True      |
| external candidates=7 rounds=4 | rule_aware_discretion                 | recommendation_stability         |   1               |   1               | True      |
| external candidates=7 rounds=4 | direct_rule_misspecification          | coverage_rate                    |   0.0416666666667 |   0.0416666666667 | True      |
| external candidates=7 rounds=4 | direct_rule_misspecification          | average_feasible_set_width       |   0.882614087302  |   0.882614087302  | True      |
| external candidates=7 rounds=4 | direct_rule_misspecification          | false_certainty_rate             |   0.958333333333  |   0.958333333333  | True      |
| external candidates=7 rounds=4 | direct_rule_misspecification          | rule_robustness_index            |   0.0458333333333 |   0.0458333333333 | True      |
| external candidates=7 rounds=4 | direct_rule_misspecification          | disclosure_uncertainty_reduction |   0.138199404762  |   0.138199404762  | True      |
| external candidates=7 rounds=4 | direct_rule_misspecification          | recommendation_stability         |   1               |   1               | True      |
| external candidates=7 rounds=4 | rule_agnostic_ordinal                 | coverage_rate                    |   1               |   1               | True      |
| external candidates=7 rounds=4 | rule_agnostic_ordinal                 | average_feasible_set_width       |   1               |   1               | True      |
| external candidates=7 rounds=4 | rule_agnostic_ordinal                 | false_certainty_rate             |   0               |   0               | True      |
| external candidates=7 rounds=4 | rule_agnostic_ordinal                 | rule_robustness_index            |   1               |   1               | True      |
| external candidates=7 rounds=4 | rule_agnostic_ordinal                 | disclosure_uncertainty_reduction |   0.0952380952381 |   0.0952380952381 | True      |
| external candidates=7 rounds=4 | rule_agnostic_ordinal                 | recommendation_stability         |   1               |   1               | True      |

## Figure evidence

- Figure 6 PNG and PDF were generated from the same Matplotlib canvas; embedded PDF fonts: `/FHXFSG+TimesNewRomanPS-BoldMT; /FHXFSG+TimesNewRomanPSMT`.
- Figure 7 PNG and PDF were generated from the same Matplotlib canvas; embedded PDF fonts: `/FHXFSG+TimesNewRomanPS-BoldMT; /FHXFSG+TimesNewRomanPSMT`.
- Both figures report coverage and width with seed-level empirical 2.5%-97.5% intervals.

## Ruling

CONCLUSIONS_ROBUST_ACROSS_SEEDS

The width ordering holds in `1.000000` of `300` paired cells across `15` preregistered parameter regions; majority reversal regions: `0`; clean internal coverage-lower cells: `0`.
