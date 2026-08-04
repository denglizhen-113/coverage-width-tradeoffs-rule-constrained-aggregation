# Supplementary Appendix: Rule-Aware DSS under Hidden Preferences

## S1. Formal Propositions and Proof Sketches

# Formal Propositions

## Proposition 1

**Statement.** Additional disclosure weakly shrinks the feasible preference set.

**Assumptions.** The latent state space and base rule are fixed; the extra disclosure is truthful, correctly encoded, and adds conjunctive constraints.

**Intuition.** Every state compatible with richer disclosure is also compatible with the coarser record.

**Proof sketch.** The richer feasible set is the base feasible set intersected with extra constraints, so it is a subset or equal set.

**Empirical implication.** Synthetic disclosure scenarios should show nonnegative shrinkage; historical disclosure is not asserted.

**Manuscript insertion point.** Methods disclosure module and appendix.

## Proposition 2

**Statement.** Correct rule-aware constraints produce feasible sets no larger than rule-agnostic constraints.

**Assumptions.** Both models share a latent state space and every rule-aware constraint is valid; the rule-agnostic constraints are nested.

**Intuition.** Known rule detail removes states that a simplex-only representation cannot exclude.

**Proof sketch.** Intersect the common state space with the larger rule-agnostic constraint set and its rule-aware superset.

**Empirical implication.** Synthetic baseline comparison should show width no larger for the rule-aware set under correct specification.

**Manuscript insertion point.** Methods and synthetic benchmark appendix.

## Proposition 3

**Statement.** Undisclosed expert-discretion relaxations can increase identifiability uncertainty relative to direct aggregation.

**Assumptions.** Same active set and score rule; direct feasibility logically implies weak feasibility; tie policy is fixed.

**Intuition.** A relaxed bottom-set condition admits every direct state and may admit weak-only states.

**Proof sketch.** Direct feasibility implies weak feasibility. Strict expansion follows whenever at least one weak-only state exists.

**Empirical implication.** Observed R_plus containment is a binary rule comparison; multi-level frontiers are synthetic scenarios.

**Manuscript insertion point.** Discretion module, results, and appendix.

## Proposition 4

**Statement.** Ordinal and cardinal regimes cannot be compared directly without a common uncertainty functional.

**Assumptions.** No justified mapping from ordinal ranks to cardinal shares is imposed and samples/state spaces differ.

**Intuition.** Rank-support width and share-interval width have different units and semantics.

**Proof sketch.** A rescaling or rank relabeling counterexample changes raw width without preserving a common information interpretation.

**Empirical implication.** Report regime-specific summaries or define and validate a common functional before comparison.

**Manuscript insertion point.** Methods comparability note and RRI section.

## Proposition 5

**Statement.** Prediction accuracy on observed outcomes is not evidence of hidden preference recovery.

**Assumptions.** Feedback is coarse, hidden preference is unobserved, and no injective latent-to-observable mapping is justified.

**Intuition.** Different latent states can generate the same elimination outcome.

**Proof sketch.** Any feasible set with more than one state gives a counterexample: an outcome predictor need not distinguish those states.

**Empirical implication.** Prediction may be used as outcome-consistency evidence only.

**Manuscript insertion point.** Validation section and limitations.


## S2. Model Invariant Checks

| check_id | invariant | passed | observed_value | evidence_source |
| --- | --- | --- | --- | --- |
| I1 | Feasible-set width lies in [0,1] for normalized synthetic summaries. | True | all normalized synthetic widths in [0,1] | synthetic_coverage_results.csv |
| I2 | Rule-aware width does not exceed rule-agnostic width under nested correct P constraints. | True | aware=0.845; agnostic=1.000 | synthetic_coverage_results.csv |
| I3 | Compatible synthetic disclosure additions do not exceed elimination-only mean width. | True | base=0.844; compared=5 nested scenario releases | value_of_disclosure.csv |
| I4 | Correctly specified no-noise rule-aware set covers known synthetic truth. | True | coverage=1.000 | synthetic_coverage_results.csv |
| I5 | Noise condition is labeled as stress test and may reduce coverage. | True | clean=1.000; noise=0.948 | synthetic_coverage_results.csv |
| I6 | RRI values are bounded in [0,1]. | True | min=1.000; max=1.000 | rule_robustness_index.csv |
| I7 | External testbed is structurally distinct and correct-rule coverage is one under its simulator. | True | 7 candidates; 4 rounds; two intervention rounds; dense-rank protocol | external_testbed_results.csv |

## S3. Complete Baseline Definitions

| baseline | represents | information_used | information_not_used | may_see_synthetic_truth | evaluation_metric | permitted_conclusion |
| --- | --- | --- | --- | --- | --- | --- |
| naive_point_estimation | Normalized judge-share point used as a transparent proxy baseline. | Observed synthetic judge share only. | Does not use synthetic truth or rule constraints. | no | Absolute synthetic point error and false-certainty diagnostic. | A point proxy can be inaccurate even when it appears decisive. |
| rank_aggregation_without_rule_constraints | All strict public rankings remain feasible before observed outcome rules are imposed. | Candidate set only. | Does not use observed elimination, judge ranks, or synthetic truth. | no | Known-truth coverage and normalized feasible-rank width. | Rule-agnostic ordinal uncertainty is a breadth baseline, not a realistic institutional mechanism. |
| prediction_only_classifier | Historical predictive model treated as a secondary validation comparator. | Pre-outcome historical covariates under the declared split. | Does not observe synthetic truth and does not encode feasible-set constraints. | no | Held-out classification metrics. | Predictive fit is not hidden-preference recovery or identification. |
| rule_agnostic_partial_identification | Simplex-only cardinal feasible set without observed-elimination inequalities. | Simplex and active candidate count. | Does not use rule-aware outcome constraints or synthetic truth. | no | Known-truth coverage and feasible-share width. | It provides a nested information baseline for the rule-aware polytope. |
| full_disclosure_oracle_synthetic_only | Synthetic upper-information reference that fixes the simulated public preference. | Synthetic truth by construction. | Unavailable in empirical analysis and not a deployable baseline. | yes, synthetic only | Synthetic width and calibration reference. | It marks an information bound, not an attainable empirical result. |

## S4. Synthetic Generation Details

The main benchmark uses fixed seed 20260716, five active candidates, Dirichlet public and expert components, a documented percentage elimination rule, and a deliberately noisy-outcome stress condition. Synthetic truth is passed only to post-inference calibration checks. The disclosure simulator holds the state space and rule fixed before adding truthful compatible synthetic constraints.

## S5. External Testbed Generation Details

The external simulator uses seven proposals, four rounds, two synthetic intervention rounds, pairwise-majority disclosure, dense-rank primary tie handling, and four tie-policy sensitivity configurations. It compares correct weak-rule encoding, direct-rule misspecification, and rule-agnostic ordinal support.

## S6. Extended Robustness Material

Retain `outputs/tables/robustness_sensitivity.csv`, ranking tie-policy sensitivity, sampling diagnostics, prediction diagnostics, and exploratory counterfactual materials as supplement-only resources. None should be used to claim point recovery, causality, or a preferred universal aggregation parameter.
