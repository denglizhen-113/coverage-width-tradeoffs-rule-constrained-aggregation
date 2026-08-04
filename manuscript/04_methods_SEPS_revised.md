# Methods: SEPS-Oriented Revision

## Setup

For week t, let A_t be the active contestant set and E_t the recorded eliminated set. The observed record contains the expert component, institutional rule, active set, and coarse outcome. No public ballot is observed. The target is the set of hidden public states compatible with these observables.

## Percentage regime P

Let j_it be the expert share and p_it the hidden public share. The candidate vector p_t lies in the simplex Delta_t = {p_it >= 0, sum_(i in A_t) p_it = 1}. For an eliminated contestant e and non-withdrawn survivor s, higher combined score is better and the recorded outcome implies j_et + p_et <= j_st + p_st, or p_et - p_st <= j_st - j_et. These inequalities, the simplex equality, and coordinate bounds define F_t. For every i, we solve L_it = min_(p in F_t) p_it and U_it = max_(p in F_t) p_it by linear programming. U_it - L_it is a sharp coordinate-wise width. Coordinate midpoints are descriptive and need not constitute a jointly feasible vector.

No-elimination and withdrawal-only weeks add no fabricated outcome inequality. Multiple eliminations compare each eliminated contestant to every non-withdrawn survivor without ordering eliminated contestants. A finale contributes complete pairwise ordering only when unique active placements are observed.

## Ranking regimes R and R_plus

Let r^J_it and r^F_it denote judge and candidate public ranks, respectively, with 1 = best for both. Candidate public ranks are strict permutations. The combined rank c_it = r^J_it + r^F_it is worse when larger. With k recorded eliminations, a direct feasible ranking places every eliminated contestant in the tie-inclusive bottom-k set B_k(c_t). The R feasible set is the collection of candidate permutations satisfying this condition.

For R_plus, the implemented weak judge-save condition replaces B_k(c_t) with B_(k+1)(c_t). Therefore F_direct,t is a subset of F_weak,t. The weak/direct ratio is a within-week identifiability-loss summary, not a cross-regime causal contrast. In the generated results, it averages 2.665961 and is never below one.

For contestant i, ordinal support width is max(r^F_it) - min(r^F_it), normalized by |A_t|-1. If q_itr is the feasible-ranking frequency of rank r, H_it = -sum_r q_itr log(q_itr) and weekly normalized entropy averages H_it/log(|A_t|). These are ordinal summaries; they are not support shares and must not be equated with P widths.

## Computation and typed proxies

Exact enumeration evaluates all |A_t|! permutations in small fields. Larger fields use 10,000 fixed-seed uniform draws. R_plus has 36 exact and 37 sampled weeks; its largest recorded Monte Carlo standard error for a feasible fraction is 0.005000. This numerical error is separate from mechanism-induced uncertainty. Retained rankings use a fixed-seed reservoir only for storage; full evaluated draws determine distributions and widths.

P proxy values use (L_it + U_it)/2, while R/R_plus proxy values use 1 - (mean(r^F_it)-1)/(|A_t|-1). They are typed cardinal and ordinal summaries, respectively. Exponential smoothing organizes these summaries over time; it does not produce an observed ballot.

## Validation and scenario boundary

Strictly historical validation uses previous contestant observations. Same-week judge models are explanatory baselines rather than deployable forecasts. Counterfactual calculations propagate feasible-set scenarios conditional on the observed active trajectory; they are scenario analyses and do not supply causal replacement histories.
