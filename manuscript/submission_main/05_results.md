# Results

## Finding 1: Elimination-only observations are partially identifying

P has nonempty feasible regions in 247 of 248 eligible weeks. Mean normalized coordinate-wise width is 0.842991. Thus the recorded rule and elimination restrict public-support states without selecting a unique support vector. Figure 2 and Table 2 report these P-regime bounds.

## Finding 2: The rule determines the identified object

P identifies cardinal support intervals. R and R_plus identify feasible ordinal rankings, with mean normalized rank widths of 0.890986 and 0.923933. These summaries are not directly comparable to P interval width because they describe different mathematical objects. Table 2 retains this distinction in its notes.

## Finding 3: Judge-save weakens within-week identification

For 73 R_plus weeks, the weak/direct feasible-set ratio averages 2.665961 and has median 1.571821. The weak set is strictly larger in 56 weeks, equal in 17, and never smaller. The result follows the specified tie-inclusive bottom-(k+1) condition and should be read as a within-week mechanism comparison. Figure 3 and Table 3 provide the audit trail.

## Finding 4: Cross-regime uncertainty is descriptive context

The sample averages order P (0.842991), R (0.890986), and R_plus (0.923933). This ordering is descriptive only: the regimes differ in hidden object, season composition, and active-field size. It is not evidence that changing an institutional rule causally moves one common uncertainty metric.

## Finding 5: Proxy validation is limited and secondary

Across 211 forward-chaining events, the strictly historical combined lag model has accuracy 0.317536 and log loss 1.838463, compared with 0.118483 and 2.077488 for uniform risk. The lowest log loss, 1.705755, belongs to a same-week judge benchmark and is not a prior-week forecast. These results show limited validation signal under the stated design; they do not establish an observed public ballot.

Traceable sources: `outputs/tables/identification_comparison_by_regime.csv`, `outputs/tables/ranking_identification_summary_rplus.csv`, `outputs/tables/prediction_results.csv`, `outputs/figures/uncertainty_over_weeks_regime_p.png`, and `outputs/figures/judge_save_identifiability_loss.png`.
