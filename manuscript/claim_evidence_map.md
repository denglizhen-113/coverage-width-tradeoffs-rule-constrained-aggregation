# Claim-Evidence Map

This map separates identification claims from descriptive validation and exploratory scenario analysis.

## Core Claims

### A1: Elimination-only feedback induces partial rather than point identification.

- Evidence: `outputs/tables/constraint_summary.csv; outputs/tables/uncertainty_by_week_regime_p.csv`
- Caveat: The result is conditional on the encoded institutional rule and observed active field.
- Proposed location: Abstract; Sections 1, 4, 5 (Finding 1)

### A2: Percentage aggregation creates wide feasible cardinal preference intervals.

- Evidence: `outputs/tables/identification_comparison_by_regime.csv; outputs/figures/uncertainty_over_weeks_regime_p.png`
- Caveat: Coordinate-wise bounds are not a jointly feasible public-share vector.
- Proposed location: Sections 4.2 and 5 (Finding 1)

### A3: Ranking mechanisms identify ordinal rankings, not cardinal public support shares.

- Evidence: `outputs/tables/ranking_identification_summary_r.csv; outputs/tables/ranking_identification_summary_rplus.csv`
- Caveat: Exact enumeration is unavailable for some large fields and fixed-seed sampling is used.
- Proposed location: Sections 4.3 and 5 (Finding 2)

### A4: The R_plus judge-save rule weakens identifiability relative to direct R-like elimination.

- Evidence: `outputs/tables/ranking_identification_summary_rplus.csv; outputs/figures/judge_save_identifiability_loss.png`
- Caveat: The comparison is within week and depends on the tie-inclusive bottom-set interpretation.
- Proposed location: Sections 4.4 and 5 (Finding 3)

### A5: Within-week R_plus feasible sets never violate direct-set containment.

- Evidence: `outputs/tables/ranking_identification_summary_rplus.csv; outputs/logs/ranking_identification_report_rplus.md`
- Caveat: Containment is evaluated under the recorded rule and tie policy.
- Proposed location: Sections 4.4 and 5 (Finding 3)

## Secondary Findings

### B1: The ordering P < R < R_plus in normalized uncertainty is descriptive.

- Evidence: `outputs/tables/identification_comparison_by_regime.csv; outputs/figures/identification_width_by_regime.png`
- Caveat: Cardinal interval width and ordinal rank width are mechanism-specific quantities.
- Proposed location: Section 5 (Finding 4)

### B2: Expert and inferred public-preference channels exhibit descriptive divergence.

- Evidence: `outputs/tables/expert_crowd_divergence.csv; outputs/logs/expert_crowd_divergence_report.md`
- Caveat: One mixed-effects fit is unstable; coefficients depend on proxy construction and fixed effects.
- Proposed location: Section 6; Appendix regression table

### B3: Historical public-proxy features contain limited but nonzero predictive signal in the specified validation design.

- Evidence: `outputs/tables/prediction_results.csv; outputs/tables/prediction_results_by_regime.csv`
- Caveat: Prediction is not evidence of point recovery; same-week judge baselines are not prior-week forecasts.
- Proposed location: Section 6; Table 4

## Exploratory Findings

### C1: Controversial-case rank ranges illustrate scenario sensitivity.

- Evidence: `outputs/tables/controversial_cases_counterfactual.csv; outputs/figures/controversial_cases_counterfactual.png`
- Caveat: Not a causal estimate of an alternative historical placement.
- Proposed location: Appendix

### C2: Counterfactual outcome and winner changes are scenario-dependent.

- Evidence: `outputs/tables/counterfactual_results_by_regime.csv; outputs/figures/mechanism_outcome_changes.png`
- Caveat: The simulation conditions on observed active trajectories and uses identified-set scenarios.
- Proposed location: Appendix; Section 6 caveat

### C3: The empirical Pareto frontier summarizes a specification-specific trade-off.

- Evidence: `outputs/tables/pareto_frontier_points.csv; outputs/figures/pareto_frontier.png`
- Caveat: The scalar objectives and normalization are not a welfare criterion.
- Proposed location: Appendix

### C4: No lambda/gamma setting is a generally preferred mechanism.

- Evidence: `outputs/tables/robust_aggregation_results.csv; outputs/figures/lambda_gamma_sensitivity.png`
- Caveat: Positive gamma points are not on the current all-objective frontier.
- Proposed location: Appendix; Section 7 caveat

### C5: Uncertainty-aware aggregation is a design template, not an empirically selected rule.

- Evidence: `outputs/tables/robust_aggregation_results.csv; outputs/logs/robust_aggregation_report.md`
- Caveat: The design depends on normative objectives and an uncertainty penalty chosen outside the data.
- Proposed location: Section 7; Appendix
