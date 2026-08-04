# Prediction and Counterfactuals

## Validation, not a deployment claim

The same-week judge-only model is an explanatory benchmark because it uses the current week's judge scores. It is not a deployable prediction model. Strict prediction validation is represented by the lagged models, which use prior contestant observations only. The combined historical model improves over uniform risk but does not outperform the same-week judge benchmark. This limited signal does not validate a point-valued public-preference measure.

## Scenario analysis, not causal history

Counterfactual calculations propagate feasible-set scenarios. In P, lower, midpoint, and upper coordinate vectors are sensitivity inputs and need not be jointly feasible. In R/R_plus, retained feasible joint rankings are used without converting them into support shares. Season rankings condition on observed active trajectories and do not generate unobserved future performances.

Outcome and winner changes are therefore scenario-sensitivity summaries, not causal effects of replacing an historical mechanism. The judge-save weak analysis reports admissibility only and leaves unique winner/finalist outcomes undefined. The Pareto frontier contains only gamma=0 points in the current grid; this is evidence against claiming that a positive uncertainty penalty improves outcomes. Uncertainty-aware aggregation remains a conceptual design input, not an empirically selected mechanism.

Detailed prediction tables, Pareto points, lambda/gamma sensitivity, and controversial cases belong in an appendix.
