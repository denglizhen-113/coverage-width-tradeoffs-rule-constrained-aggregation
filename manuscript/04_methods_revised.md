# Methods

## 4.1 Setup and notation

For week t with active set A_t, let j_it be contestant i's normalized expert share, with sum_i j_it = 1. The hidden public object depends on the rule. We observe the active set, the expert component, the institutional rule, and the eliminated set E_t. We identify all hidden states consistent with those observables; no public ballot is observed.

## 4.2 Percentage aggregation

Under P, p_t = (p_it : i in A_t) belongs to the simplex Delta_t = {p_it >= 0, sum_i p_it = 1}. Higher combined score is better, so an eliminated contestant e and a non-withdrawn survivor s imply j_et + p_et <= j_st + p_st. Equivalently, p_et - p_st <= j_st - j_et. These inequalities, the simplex equality, and [0,1] coordinate bounds define a convex polytope F_t. For each contestant i, linear programs compute L_it = min_{p in F_t} p_it and U_it = max_{p in F_t} p_it. The reported P width is U_it - L_it (normalized because p lies on a unit simplex). Bounds are sharp coordinate-wise; the vector of coordinate midpoints need not belong to F_t.

No-elimination weeks add no unjustified outcome inequality. Withdrawal weeks are treated as non-comparative. Multiple eliminations require each eliminated contestant to be weakly below every non-withdrawn survivor but do not order the eliminated contestants. If a final round supplies unique active placements, all recorded pairwise order inequalities are added.

## 4.3 Ranking aggregation

Under R and R_plus, r^J_it is the judge rank and r^F_it is a strict candidate public rank, both with 1 denoting best. The combined rank is c_it = r^J_it + r^F_it, so larger c_it is worse. A candidate public permutation is direct-feasible when every observed eliminated contestant lies in the tie-inclusive bottom-k set B_k(c_t), where k is the recorded number of eliminations. The feasible set is the collection of all such public permutations.

For each contestant, the ordinal support is the set of feasible r^F_it values. Its width is max(r^F_it) - min(r^F_it), normalized by |A_t|-1. Entropy is H_it = -sum_r q_itr log(q_itr), where q_itr is the feasible-ranking frequency of rank r; weekly normalized entropy averages H_it/log(|A_t|). These are ordinal uncertainty summaries, not cardinal support shares.

Exact enumeration evaluates every |A_t|! public permutation in small fields. In the empirical runs, R has 13 exact and 1 sampled week, while R_plus has 36 exact and 37 sampled weeks. Larger fields use 10,000 fixed-seed uniform draws; the reported maximum Monte Carlo standard error for feasible fractions is approximately 0.005. This error is numerical and is not uncertainty about public behavior. Retained feasible-ranking files use a fixed-seed reservoir cap for storage, while rank distributions and widths use all evaluated draws.

## 4.4 Judge-save weak identification

For R_plus, the recorded elimination is compatible with a candidate ranking when the eliminated set belongs to B_{k+1}(c_t), a tie-inclusive bottom set enlarged by one save-eligible position. Hence every direct-feasible permutation is weak-feasible: F_direct,t is a subset of F_weak,t. The within-week weak/direct ratio |F_weak,t|/|F_direct,t| summarizes the loss of identification. This is a comparison of the same rule environment under direct and weak outcome implications, not a cross-regime average.

## 4.5 Typed dynamic proxies

For descriptive longitudinal organization, P uses (L_it+U_it)/2 and R/R_plus use 1-(mean(r^F_it)-1)/(|A_t|-1). The former is a cardinal interval midpoint and the latter an ordinal rank score. Their uncertainty values are, respectively, interval width and normalized rank width. Exponential smoothing uses alpha=0.5; uncertainty-weighted smoothing uses alpha/(1+u_it). These proxies are not public ballots and are not directly comparable across rule types.

## 4.6 Validation and scenarios

Historical validation lags public, dynamic, uncertainty, and expert features by one contestant observation. Same-week judge models are explanatory benchmarks, not deployable forecasts. Scenario analyses use P lower/midpoint/upper coordinate bounds or retained ordinal feasible rankings and condition on observed active trajectories. They do not reconstruct a causal alternative season.
