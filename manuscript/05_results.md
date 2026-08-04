# Results

## Finding 1: Elimination-only feedback yields wide feasible preference sets

P yields a nonempty linear feasible region in 247 of 248 eligible weeks. Its mean normalized coordinate-wise identification width is 0.842991. This is direct evidence for partial, rather than point, identification: the observed elimination restricts public support without selecting one support vector. Figure 2 and Table 2 report the distribution and timing of these widths.

## Finding 2: Aggregation rules determine whether the hidden object is cardinal or ordinal

P constrains cardinal support coordinates on a simplex. R and R_plus instead constrain feasible public rank permutations. Their normalized rank widths are 0.890986 and 0.923933, respectively. These values are useful regime summaries, but P interval width and ordinal rank width are not directly comparable measurements. Table 2 records their definitions.

## Finding 3: Judge-save weakens identifiability by expanding the feasible ranking set

Across the 73 R_plus weeks, the weak/direct feasible-set ratio has mean 2.665961 and median 1.571821. The weak set is strictly larger in 56 weeks, equal in 17 weeks, and never smaller. This within-week containment result is the central mechanism comparison: a bottom-set judge-save condition preserves institutional discretion while reducing what the elimination record identifies. Figure 3 and Table 3 provide the corresponding audit.

## Finding 4: Cross-regime uncertainty differences are descriptive and mechanism-dependent

The sample ordering P < R < R_plus in average normalized uncertainty is 0.842991, 0.890986, and 0.923933. It should not be interpreted as a causal rule comparison because the hidden objects, season composition, and field sizes differ. Figure 4 is retained to show descriptive context with this limitation visible in the caption and text.

## Finding 5: Dynamic proxies and prediction experiments provide validation signals but do not establish unobserved public votes

Typed proxies permit lagged validation without treating their midpoint or rank-score construction as observed public input. Over 211 forward-chaining events, the strictly historical combined model has accuracy 0.317536 and log loss 1.838463, compared with 0.118483 and 2.077488 for uniform risk. The lowest log loss, 1.705755, belongs to the explicitly marked same-week judge baseline and is not a prior-week forecast. Figure 5 and Table 4 therefore present prediction as limited validation evidence, not as an identification result.

Traceable sources: `outputs/tables/identification_comparison_by_regime.csv`, `outputs/tables/ranking_identification_summary_rplus.csv`, `outputs/tables/prediction_results.csv`, `outputs/figures/uncertainty_over_weeks_regime_p.png`, `outputs/figures/judge_save_identifiability_loss.png`, `outputs/figures/identification_width_by_regime.png`, and `outputs/figures/prediction_comparison.png`.
