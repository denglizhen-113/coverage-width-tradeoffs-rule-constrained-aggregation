# Prediction and Counterfactuals

## Prediction as validation

The historical combined lag model improves over uniform risk in forward validation (log loss 1.838463 versus 2.077488). The uncertainty-aware lag model has log loss 1.849835. These are descriptive validation results for the feature construction. They do not establish unobserved public votes, and the same-week judge benchmark is reported separately because it uses information unavailable to a prior-week forecast.

## Scenario analyses of mechanisms

Counterfactual calculations retain multiple identified-set scenarios. In P, percentage aggregation has an outcome-change rate of 0.005608 and a winner-change rate of 0.000000 across its coordinate scenarios. Applying direct ranking to R_plus scenarios has an outcome-change rate of 0.477300. These values describe the behavior of specified rules under feasible scenarios; they are not causal effects of replacing an historical rule.

The judge-save weak mechanism intentionally reports set admissibility rather than a unique winner or finalist outcome, because an unobserved save decision remains unresolved. The lambda/gamma grid, Pareto frontier, controversial cases, and dynamic examples are retained as appendix material. In particular, no positive uncertainty penalty is presented as empirically dominant.

Traceable sources: `outputs/tables/prediction_results.csv`, `outputs/tables/counterfactual_results_by_regime.csv`, `outputs/tables/pareto_frontier_points.csv`, and `outputs/tables/controversial_cases_counterfactual.csv`.
