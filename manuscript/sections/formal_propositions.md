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
