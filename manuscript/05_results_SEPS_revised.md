# Results: SEPS-Oriented Revision

## Feasible sets remain wide under coarse feedback

For P, 247 eligible weeks yield nonempty feasible regions. Mean normalized coordinate-wise width is 0.842991. The result shows that the recorded rule and elimination restrict a set of compatible latent preference states without selecting one point-valued public input.

## The aggregation mechanism changes the identified object

P produces cardinal feasible-share intervals. R and R_plus produce feasible ordinal public rankings, with mean normalized rank-support widths of 0.890986 and 0.923933. These quantities are not directly comparable because their scales, state spaces, and sample compositions differ.

## Judge-save discretion weakens the observable implication

Across 73 R_plus weeks, the weak/direct feasible-set ratio averages 2.665961 and has median 1.571821. The weak set is strictly larger in 56 weeks, equal in 17 weeks, and never smaller. This is a within-week comparison of direct versus weak outcome implications, not an estimate of the causal effect of switching a real institution's rule.

## Secondary validation evidence

The strictly historical combined-lag model has forward-chaining accuracy 0.317536 and log loss 1.838463, compared with 0.118483 and 2.077488 for uniform risk. The lower log loss of the same-week judge benchmark (1.705755) is not a forecasting result because it uses current-week judge information. These checks provide limited validation signal and do not observe a public ballot.

Traceable sources: `outputs/tables/identification_comparison_by_regime.csv`, `outputs/tables/ranking_identification_summary_rplus.csv`, `outputs/tables/prediction_results.csv`, `outputs/figures/uncertainty_over_weeks_regime_p.png`, and `outputs/figures/judge_save_identifiability_loss.png`.
