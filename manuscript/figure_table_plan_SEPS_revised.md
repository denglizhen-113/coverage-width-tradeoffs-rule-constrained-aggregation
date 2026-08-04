# Figure and Table Plan: SEPS-Oriented Revision

## Main-text selection

The proposal keeps 4 figures and 3 tables, within the requested ceiling of five figures and four tables. The prediction figure and table move to the appendix because validation is secondary. No new figures or models are generated.

| item_type | item_id | main_text | file_or_source | purpose | decision | caption_and_label_check | comparability_or_proxy_note | pixel_size | dpi_check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| figure | Figure 1 | True | conceptual_framework_hidden_preferences.png | Conceptual feasible-set framework | Keep | Self-contained conceptual labels; no claim of observed ballot. | Provide vector source if guide requires. | 2526x1007 | 300 dpi |
| figure | Figure 2 | True | uncertainty_over_weeks_regime_p.png | P interval width over weeks | Keep | Caption must say coordinate-wise feasible width. | P only. | 2194x1384 | 300 dpi |
| figure | Figure 3 | True | judge_save_identifiability_loss.png | R_plus weak versus direct expansion | Keep | State tie-inclusive bottom-set rule. | Within-regime only. | 2434x1444 | 300 dpi |
| figure | Figure 4 | True | identification_width_by_regime.png | Cross-regime uncertainty context | Keep with caveat | State cardinal/ordinal non-comparability prominently. | Descriptive only. | 2194x1414 | 300 dpi |
| figure | Figure 5 | False | prediction_comparison.png | Prediction validation | Appendix | Same-week models must be marked explanatory. | Secondary validation. | 3634x1594 | 300 dpi |
| table | Table 1 | True | data/processed/identification_features_long.csv; outputs/tables/constraint_summary.csv | Dataset and regime summary | Keep | Add rule and event-type footnotes. | Separate cardinal and ordinal objects. | not applicable | not applicable |
| table | Table 2 | True | outputs/tables/identification_comparison_by_regime.csv | Partial-identification summary | Keep | Use a prominent non-comparability note. | Mechanism-specific measures. | not applicable | not applicable |
| table | Table 3 | True | outputs/tables/ranking_identification_summary_rplus.csv | Direct versus weak judge-save comparison | Keep | Report exact/sampled rows and tie policy. | Within-week comparison. | not applicable | not applicable |
| table | Table 4 | False | outputs/tables/prediction_results.csv | Prediction validation | Appendix | Separate same-week from historical models. | Secondary validation. | not applicable | not applicable |

## Appendix / supplement recommendations

- Controversial-case scenario panels.
- Lambda/gamma sensitivity and Pareto details.
- Dynamic proxy examples and full regression coefficients.
- Ranking sampling diagnostics and tie-policy sensitivity.
- Prediction calibration and full model tables.
- Pipeline reproducibility, data audit, and all audit checklists.

Each retained main-text caption must define the estimand, distinguish P intervals from ordinal ranking sets, avoid point-recovery wording, and state whether it reports an exact or sampled result.
