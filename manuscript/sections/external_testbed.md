# Structurally Different External Testbed

To examine structural portability without claiming a second empirical validation, we construct a fixed-seed synthetic community-grant prioritization panel. The setting begins with seven proposals, runs four elimination rounds, uses a synthetic expert intervention in two rounds, adopts dense-rank tie handling, and releases one synthetic pairwise public-priority relation. These ingredients differ from the single-week percentage simulator and from the longitudinal empirical testbed.

| method | coverage_rate | average_feasible_set_width | false_certainty_rate | rule_robustness_index | disclosure_uncertainty_reduction | recommendation_stability |
| --- | --- | --- | --- | --- | --- | --- |
| direct_rule_misspecification | 0.042 | 0.883 | 0.958 | 0.046 | 0.138 | 1.000 |
| rule_agnostic_ordinal | 1.000 | 1.000 | 0.000 | 1.000 | 0.095 | 1.000 |
| rule_aware_discretion | 1.000 | 0.960 | 0.000 | 0.942 | 0.125 | 1.000 |

The rule-aware discretion representation retains the known synthetic ranking whenever the simulation follows its stated direct or weak intervention rule. Treating every intervention as direct is deliberately a misspecification comparator, not a plausible empirical estimate. The testbed demonstrates structural portability of the conditional DSS logic under this institutional mechanism; it neither proves universal applicability nor supplies evidence about real grant decisions, users, or organizations.
