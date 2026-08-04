# Method and Theory Upgrade Notes

These propositions formalize the boundary conditions of the existing framework and the proposed disclosure/robustness extensions. They should be written with exact notation only after the relevant module defines its state space, tie policy, and constraint map. None should be stated as an empirical universal without its listed assumptions.

## P1. Additional disclosure weakly shrinks feasible preference sets

**Statement.** If added disclosure is truthful and imposes additional constraints on the same latent state space, the feasible set under the richer disclosure is a subset of, or equal to, the feasible set under coarse disclosure.

**Intuition.** Every state consistent with the richer record must also be consistent with the coarser record; additional information can rule states out but cannot create compatibility.

**Assumptions.** Same rule, latent state space, and outcome; added disclosure is correctly encoded and logically conjunctive; no measurement error or contradictory record.

**Proof sketch.** Write the coarse feasible set as states satisfying base constraints and the rich set as base constraints plus disclosure constraints. Set intersection yields containment.

**Insertion point.** Methods disclosure extension and Appendix proof.

**Empirical verification.** No for proof; yes for numerical shrinkage illustrations.

## P2. Rule-aware constraints are tighter than rule-agnostic constraints

**Statement.** When the rule-aware constraint set contains every valid rule-agnostic constraint and adds only correct rule-specific constraints, its feasible set is a subset of, or equal to, the rule-agnostic feasible set.

**Intuition.** Encoding known institutional detail removes states that a generic outcome-only representation cannot exclude.

**Assumptions.** Rule-specific constraints are correctly derived; the rule-agnostic model is nested rather than differently misspecified; both use the same latent space.

**Proof sketch.** Compare intersections of the same base state space with a subset and its superset of constraints.

**Insertion point.** Methods and synthetic benchmark appendix.

**Empirical verification.** No for proof; yes for benchmark magnitude and misspecification checks.

## P3. Expert-discretion relaxation can expand identifiability uncertainty

**Statement.** If a discretionary rule weakens a direct elimination condition to a logically weaker tie-inclusive bottom-set condition, every direct-feasible state is discretion-feasible; strict expansion occurs whenever an additional state satisfies only the weaker condition.

**Intuition.** A relaxation preserves prior compatibility and may admit further hidden rankings.

**Assumptions.** Same active set and scoring rule; weak condition is a logical relaxation; tie policy is fixed and documented.

**Proof sketch.** Show that direct feasibility implies weak feasibility, then give the strict-expansion condition as existence of a weak-only state.

**Insertion point.** Methods, results, and Appendix proof; M1 frontier section.

**Empirical verification.** No for containment proof; yes for empirical frequency and frontier estimation.

## P4. Ordinal and cardinal uncertainty require a common functional for comparison

**Statement.** Raw cardinal interval width and ordinal rank-support width do not define an ordered common uncertainty scale unless an explicit common uncertainty functional and its interpretation are specified.

**Intuition.** The objects live on different state spaces and units; a larger number in one representation need not mean more information loss than a smaller number in another.

**Assumptions.** No fixed, justified mapping from rank configurations to cardinal support vectors has been imposed; regime samples and active-set sizes may differ.

**Proof sketch.** Construct representations with equal reported widths under arbitrary rescaling or rank relabeling but different information content; comparison is undefined without a declared map.

**Insertion point.** Methods comparability note and Figure 4 caption; M2 design.

**Empirical verification.** No for the conceptual statement; yes if proposing a new common functional.

## P5. Prediction cannot identify hidden preferences from coarse outcomes alone

**Statement.** Predictive performance for observed institutional outcomes cannot identify hidden preferences unless additional assumptions make the mapping from hidden preferences to the observable distribution injective.

**Intuition.** Distinct hidden states can produce the same elimination outcome or the same predictive distribution after aggregation and coarse observation.

**Assumptions.** Coarse feedback; no observation of the hidden collective input; no independently justified injectivity condition.

**Proof sketch.** Exhibit multiple latent states in a feasible set that imply the same observed outcome; a predictor can be accurate over that outcome without distinguishing them.

**Insertion point.** Validation section and Appendix proof sketch.

**Empirical verification.** No for non-identification proof; yes for consistency checks against observed outcomes.
