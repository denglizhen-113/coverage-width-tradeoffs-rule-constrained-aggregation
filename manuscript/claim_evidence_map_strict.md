# Strict Claim-Evidence Map

Only the five main claims may anchor the abstract, introduction contribution list, and conclusion.

## Main Claims

| claim_id | claim_text | evidence | allowed_manuscript_location | abstract_can_mention |
| --- | --- | --- | --- | --- |
| A1 | Elimination-only feedback induces partial rather than point identification. | outputs/tables/constraint_summary.csv; outputs/tables/uncertainty_by_week_regime_p.csv | Abstract, introduction end, results, conclusion | yes |
| A2 | Percentage aggregation creates wide feasible cardinal preference intervals. | outputs/tables/identification_comparison_by_regime.csv; outputs/figures/uncertainty_over_weeks_regime_p.png | Abstract, introduction end, results, conclusion | yes |
| A3 | Ranking mechanisms identify ordinal rankings, not cardinal public support shares. | outputs/tables/ranking_identification_summary_r.csv; outputs/tables/ranking_identification_summary_rplus.csv | Abstract, introduction end, results, conclusion | yes |
| A4 | The R_plus judge-save rule weakens identifiability relative to direct R-like elimination. | outputs/tables/ranking_identification_summary_rplus.csv; outputs/figures/judge_save_identifiability_loss.png | Abstract, introduction end, results, conclusion | yes |
| A5 | Within-week R_plus feasible sets never violate direct-set containment. | outputs/tables/ranking_identification_summary_rplus.csv; outputs/logs/ranking_identification_report_rplus.md | Abstract, introduction end, results, conclusion | yes |

## Supporting Claims

| claim_id | claim_text | evidence | allowed_manuscript_location | abstract_can_mention |
| --- | --- | --- | --- | --- |
| B1 | The ordering P < R < R_plus in normalized uncertainty is descriptive. | outputs/tables/identification_comparison_by_regime.csv; outputs/figures/identification_width_by_regime.png | Results or discussion, not abstract center | no |
| B2 | Expert and inferred public-preference channels exhibit descriptive divergence. | outputs/tables/expert_crowd_divergence.csv; outputs/logs/expert_crowd_divergence_report.md | Results or discussion, not abstract center | no |
| B3 | Historical public-proxy features contain limited but nonzero predictive signal in the specified validation design. | outputs/tables/prediction_results.csv; outputs/tables/prediction_results_by_regime.csv | Results or discussion, not abstract center | no |

## Exploratory Claims

| claim_id | claim_text | evidence | allowed_manuscript_location | abstract_can_mention |
| --- | --- | --- | --- | --- |
| C1 | Controversial-case rank ranges illustrate scenario sensitivity. | outputs/tables/controversial_cases_counterfactual.csv; outputs/figures/controversial_cases_counterfactual.png | Appendix or caveated discussion only | no |
| C2 | Counterfactual outcome and winner changes are scenario-dependent. | outputs/tables/counterfactual_results_by_regime.csv; outputs/figures/mechanism_outcome_changes.png | Appendix or caveated discussion only | no |
| C3 | The empirical Pareto frontier summarizes a specification-specific trade-off. | outputs/tables/pareto_frontier_points.csv; outputs/figures/pareto_frontier.png | Appendix or caveated discussion only | no |
| C4 | No lambda/gamma setting is a generally preferred mechanism. | outputs/tables/robust_aggregation_results.csv; outputs/figures/lambda_gamma_sensitivity.png | Appendix or caveated discussion only | no |
| C5 | Uncertainty-aware aggregation is a design template, not an empirically selected rule. | outputs/tables/robust_aggregation_results.csv; outputs/logs/robust_aggregation_report.md | Appendix or caveated discussion only | no |
