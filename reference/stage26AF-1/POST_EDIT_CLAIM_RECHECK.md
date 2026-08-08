# Stage 26AF-1 Post-Edit Claim Recheck

All 24 evidence calculations were recomputed from tracked inputs using the Stage 26AC audit functions. Manuscript-facing checks were then applied to the final six-figure Stage 26AF-1 draft. C10, C11, and C23 remain traceability facts rather than manuscript headline claims.

| ID | Claim | Computed | Expected | Evidence check | Manuscript check | Overall | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | Processed longitudinal panel rows | 4199 | 4199 | PASS | PASS | PASS | data/processed/panel_long.csv |
| C02 | Identification feature rows | 2777 | 2777 | PASS | PASS | PASS | data/processed/identification_features_long.csv |
| C03 | Typed public-appeal proxy rows | 2766 | 2766 | PASS | PASS | PASS | data/processed/identification_features_long.csv |
| C04 | Feasible P weeks | 247/248 | 247/248 | PASS | PASS | PASS | outputs/tables/constraint_summary.csv |
| C05 | R exact/sampled weeks and sampled draws | 13 exact; 1 sampled; [50000] | 13 exact; 1 sampled; [50000] | PASS | PASS | PASS | outputs/tables/ranking_identification_summary_r.csv |
| C06 | R-plus exact/sampled weeks and sampled draws | 36 exact; 37 sampled; [10000] | 36 exact; 37 sampled; [10000] | PASS | PASS | PASS | outputs/tables/ranking_identification_summary_rplus.csv |
| C07 | Preregistered seeds | 20 | 20 | PASS | PASS | PASS | outputs/stage26X-1/raw/*.csv |
| C08 | Registered parameter regions | 15 | 15 | PASS | PASS | PASS | outputs/stage26X-1/raw/*.csv |
| C09 | Stage 26X-1 synthetic cases | 67200 | 67200 | PASS | PASS | PASS | outputs/stage26X-1/raw/*.csv |
| C10 | Stage 26X-1 retained rows | 261600 | 261600 | PASS | PASS_NOT_ASSERTED_AS_HEADLINE | PASS | outputs/stage26X-1/raw/*.csv |
| C11 | Stage 26X-2 retained rows | 290400 | 290400 | PASS | PASS_NOT_ASSERTED_AS_HEADLINE | PASS | outputs/stage26X-2/raw/**/*.csv |
| C12 | Combined retained rows | 552000 | 552000 | PASS | PASS | PASS | outputs/stage26X-1/raw/*.csv; outputs/stage26X-2/raw/**/*.csv |
| C13 | Rule-aware width below rule-agnostic width | 300/300 | 300/300 | PASS | PASS | PASS | outputs/stage26X-1/raw/*.csv |
| C14 | Positive-noise coverage loss cells | 180/180 | 180/180 | PASS | PASS | PASS | outputs/stage26X-1/raw/internal_*.csv |
| C15 | Mean positive-noise coverage loss | 0.050289 | 0.050289 | PASS | PASS | PASS | outputs/stage26X-1/raw/internal_*.csv |
| C16 | Elimination-removal coverage effect | 0.050289 | 0.050289 | PASS | PASS | PASS | outputs/stage26X-2/tables/ablation_paired_effects.csv |
| C17 | Elimination-removal width effect | 0.163131 | 0.163131 | PASS | PASS | PASS | outputs/stage26X-2/tables/ablation_paired_effects.csv |
| C18 | Positive-noise ablation improves coverage | 180/180 | 180/180 | PASS | PASS | PASS | outputs/stage26X-2/tables/ablation_paired_effects.csv |
| C19 | Clean-cell elimination removal changes coverage | 0/60 | 0/60 | PASS | PASS | PASS | outputs/stage26X-2/tables/ablation_paired_effects.csv |
| C20 | Rule-aware Pareto dominance over Bayesian | 0/120 | 0/120 | PASS | PASS | PASS | outputs/stage26X-2/tables/attribution_pairwise_cells.csv |
| C21 | Bayesian Pareto dominance over rule-aware | 14/120 | 14/120 | PASS | PASS | PASS | outputs/stage26X-2/tables/attribution_pairwise_cells.csv |
| C22 | Insufficient posterior rows | 94 | 94 | PASS | PASS | PASS | outputs/stage26X-2/raw/bayesian/*.csv |
| C23 | Raw files across Stage 26X-1/2 | 1200 | 1200 | PASS | PASS_NOT_ASSERTED_AS_HEADLINE | PASS | outputs/stage26X-1/raw; outputs/stage26X-2/raw |
| C24 | Maximum Monte Carlo standard error | 0.005000 | 0.005000 | PASS | PASS | PASS | outputs/tables/ranking_identification_summary_r*.csv |

Result: `INTEGRITY_PASS` (24/24). No `CLAIM_DRIFT_DETECTED` condition was observed.
