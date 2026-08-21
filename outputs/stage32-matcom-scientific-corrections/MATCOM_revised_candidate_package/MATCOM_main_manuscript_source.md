# Coverage-Width Tradeoffs in Rule-Constrained Expert-Crowd Aggregation

## Abstract

Institutional expert-crowd systems often reveal expert scores and coarse outcomes while public preferences remain latent. We formulate cardinal identified polytopes for percentage aggregation and ordinal feasible-ranking sets for rank aggregation with judge-save discretion. Two corrections sharpen the computational methodology. First, known-truth coverage of a polytope is evaluated by joint constraint membership rather than membership in the Cartesian product of its coordinate projections. Second, sharp ordinal rank endpoints are obtained by binary linear optimization instead of extrema of sampled permutations. The endpoint formulation uses 2,964 solver calls for 87 empirical weeks under the primary tie policy and agrees with complete enumeration in all small-field verification cases. Across 45,000 positive-noise paired internal replications, removing the elimination constraint increases joint-set coverage by 0.117600 (MCSE 0.001519) and mean coordinate width by 0.163131 (MCSE 0.000302). The former projection-box calculation understated the coverage change as 0.050289. Same-information Bayesian comparisons remain conditional on a 95% equal-tail posterior construction and a stated prior; Bayesian credible rectangles and identified sets are reported as different inferential objects. The contribution is an exact, auditable inverse-rule methodology and a bounded simulation study, not recovery of an observed audience vote or a claim of uniform method superiority.

**Keywords:** Expert-crowd aggregation; partial identification; exact rank support; mixed-integer optimization; latent public preference; simulation.

## 1. Introduction

Many decision systems combine an expert component with an unobserved public component and disclose only the aggregate consequence. The inverse problem is therefore set-valued: which latent public states are compatible with the expert record, the stated aggregation rule, and the observed outcome? We study this problem for percentage aggregation and rank aggregation with judge-save discretion. The competition record is an empirical testbed for a general class of expert-crowd systems; it is not treated as a source of observed audience votes.

The paper makes three contributions. First, it gives an exact binary-optimization formulation for sharp attainable public-rank endpoints under tie-inclusive bottom-set rules. This replaces the earlier practice of reading support extrema from a finite permutation sample. Second, it distinguishes joint identified-set coverage from coverage of marginal projection intervals and recomputes the misspecification experiment with metric-matched Monte Carlo uncertainty. Third, it states the boundary between identified sets and Bayesian credible rectangles, reports every undefined posterior region, and treats the uncertain season-28 rule assignment as a sensitivity assumption.

These contributions are narrower than the general possible-winner problem. We do not claim a new dichotomy for arbitrary voting rules. The special structure here consists of one hidden aggregate public ranking, one observed expert ranking, and an observed bottom-set implication. That structure admits a compact assignment MILP for support endpoints even though exact feasible-set counting may remain combinatorial.

## 2. Related work and novelty boundary

Partial identification separates data-consistent parameter sets from point recovery [1-4]. Bayesian credible sets in partially identified models have different semantics from estimated identified sets; Moon and Schorfheide recommend reporting the identified set and conditional-prior information alongside Bayesian summaries [5]. We follow that distinction explicitly.

The closest ordinal literature is computational social choice under incomplete preferences. Xia and Conitzer characterize possible and necessary winners under common rules [6]; Betzler and Dorn establish a broad complexity dichotomy for possible winners under scoring rules [7]; Bachrach, Betzler, and Faliszewski study probabilistic possible-winner counting and randomized computation [8]; Dey and Misra sharpen hardness results as missing pairwise information varies [9]; and Lu and Boutilier develop robust winner determination under partial rankings [10]. Their objects complete multiple partial voter orders and ask about winners. Our object is different: the public input is one latent aggregate permutation, expert ranks are observed, and a coarse institutional outcome constrains combined expert-public scores. The present novelty is the inverse-rule formulation and its exact support-endpoint MILP, not the general idea that incomplete rankings induce a completion set.

Simulation design follows ADEMP and transparent reporting guidance [11-13]. Fixed seeds and parameter cells were recorded in a hash-locked local design before the reported evaluation. Because no external immutable registration identifier predates result inspection, we use **predeclared** and **hash-locked**, not **preregistered**.

## 3. Data, rules, and provenance

The empirical testbed is the official COMAP 2026 Problem C data file [14]. The processed panel has 248 percentage-regime weeks, 14 early rank-regime weeks, and 73 weeks encoded under the rank-plus-judge-save interpretation. COMAP documents percentage aggregation for seasons 3-27 and describes a bottom-two judge-save mechanism from season 28, but states that the exact season in which rank aggregation returned is uncertain and treats season 28 as a reasonable assumption. We therefore label seasons 28-34 as the **primary season-28 rank-return assumption** and separately report results excluding season 28.

One percentage week, season 18 week 2, is skipped. The cause is not a missing public-appeal proxy. The constraint log records an eliminated contestant, Diana Nyad, without an active judge total after the source-status mapping. Because the elimination inequality cannot be constructed from the stated P-regime equation, that week has no identified set. The 11 unavailable typed proxies are downstream consequences of this skipped identification result and are neither inputs to nor causes of P-regime constraint construction. No value is imputed.

Withdrawals are excluded from outcome eligibility but remain in the active public-rank permutation when the source record marks them active for that week. Multiple eliminations use the observed eliminated set. Weekly latent rankings are not constrained to remain constant across rounds; multi-round synthetic case coverage is the conjunction of separately encoded round-level compatibility statements. A model with a stable or dynamically coupled latent ranking would be a different estimand and is not implemented here.

## 4. Cardinal identified polytope and coverage

Let $A$ be the active candidates, $q_i$ the normalized expert share, and $p_i$ the latent public share. Under percentage aggregation,

$P(O)=\{p\in\mathbb R^n: p_i\ge0,\ \sum_i p_i=1,\ q_e+p_e\le q_s+p_s\ \text{for every eliminated }e\text{ and eligible survivor }s}\}.$

Coordinate bounds $l_i=\min_{p\in P(O)}p_i$ and $u_i=\max_{p\in P(O)}p_i$ are sharp marginal projections. Their Cartesian product $\prod_i[l_i,u_i]$ is generally a strict outer approximation to $P(O)$. We therefore report two distinct diagnostics for a known synthetic truth $p^\star$:

$C_{set}=1\{p^\star\in P(O)\},\qquad C_{box}=1\{l_i\le p_i^\star\le u_i\ \forall i}.$

Only $C_{set}$ is called identified-set coverage. $C_{box}$ is retained as a legacy projection-envelope diagnostic. In the noisy generator the recorded eliminated candidate is the strictly second-worst combined-score candidate (ties occur with probability zero under the continuous generator), so every realized noise event violates at least one joint elimination inequality even when the truth remains inside all marginal intervals.

## 5. Ordinal feasible sets

Let $r_i^J$ be the observed expert rank and $r_i^F$ a latent strict public rank, a permutation of $1,\ldots,n$. Define combined rank score $c_i=r_i^J+r_i^F$, where a larger score is worse. For eligible set $G$ and $1\le k\le|G|$, let $\theta_k(c;G)$ be the $k$th largest value in $\{c_i:i\in G\}$ and define the tie-inclusive bottom set

$B_k(c;G)=\{i\in G:c_i\ge\theta_k(c;G)\}.$

This definition permits $|B_k|>k$ under ties. It also gives $B_k(c;G)\subseteq B_{k+1}(c;G)$ directly because $\theta_{k+1}\le\theta_k$. For $k$ observed eliminations, the direct rule requires $E\subseteq B_k$; the weak judge-save interpretation requires $E\subseteq B_{\min(k+1,|G|)}$. Expert ties are converted to ranks under the named policy (average, minimum/competition, or dense), and every sensitivity row preserves that policy label.

### 5.1 Exact support-endpoint MILP

Introduce binary assignment variables $x_{ir}$, equal to one when candidate $i$ receives public rank $r$. The permutation constraints are

$\sum_r x_{ir}=1\ \forall i,\qquad \sum_i x_{ir}=1\ \forall r.$

Then $s_i=r_i^J+\sum_r r x_{ir}$. For each eliminated $e$ and eligible $i\ne e$, introduce binary $y_{ie}$ and a valid upper bound $M$ on score differences:

$s_i-s_e\le M y_{ie},\qquad \sum_{i\in G\setminus\{e\}}y_{ie}\le m-1,$

where $m=k$ for direct elimination and $m=\min(k+1,|G|)$ for the weak save rule. If $s_i>s_e$, integrality forces $y_{ie}=1$; when $s_i\le s_e$, a feasible solution can take $y_{ie}=0$. Thus the second inequality is equivalent to $e\in B_m$. Finale order constraints are linear inequalities between adjacent combined scores in the observed placement order.

**Theorem 1 (sharp endpoint correctness).** For every encoded week, tie policy, mechanism, candidate $a$, and public rank $r$, the assignment MILP has a feasible integer solution with $x_{ar}=1$ if and only if there exists a strict public permutation satisfying the same finale or tie-inclusive bottom-set predicate used by the enumerative rule checker. Consequently, minimizing and maximizing $\sum_r r x_{ar}$ give the sharp attainable endpoints for candidate $a$.

**Proof.** A feasible integer assignment matrix has exactly one one in each row and column, hence represents one strict permutation; conversely every strict permutation defines such a matrix. For an elimination constraint, $s_i>s_e$ forces $y_{ie}=1$. If at most $m-1$ eligible scores are strictly greater than $s_e$, choose $y_{ie}=1$ exactly for those scores and zero otherwise, satisfying both inequalities. Therefore the auxiliary constraints hold exactly when $e$ is in the tie-inclusive bottom-$m$ set. Applying this to every eliminated candidate, or applying the adjacent finale inequalities, proves equivalence. Linear optimization over the equivalent feasible integer assignments attains the sharp minimum and maximum. $\square$

The algorithm solves two MILPs per candidate. A non-finale week has $n^2+|E|(|G|-1)$ binary variables, $2n+|E|(|G|-1)+|E|$ principal constraints, and $2n$ optimization calls. This is a workload bound, not a polynomial-time claim: general binary linear optimization is NP-hard, and exact compatible-permutation counting is not supplied by endpoint optimization. In this data, the primary tie-policy analysis required 2,964 solver calls; all four tie policies plus the direct counterfactual used 7,644 calls in 45.03 seconds on the recorded environment.

### 5.2 Set nesting and interpretation

Adding valid constraints intersects a feasible set and cannot enlarge it. Likewise, the direct ordinal set is contained in the weak save set because $B_k\subseteq B_{k+1}$. These are reported as lemmas and implementation invariants, not empirical wins. Cardinal share widths and normalized ordinal rank-support widths have no canonical common uncertainty scale; numerical cross-regime comparisons are descriptive unless a substantive common loss functional is supplied.

## 6. Bayesian comparator and simulation uncertainty

The internal Bayesian comparator draws from a symmetric $Dirichlet(1)$ prior and applies a zero-one likelihood for the observed linear constraints. With fixed $N=8192$ prior draws and at least 100 accepted states, the reported coordinate interval is the 95% equal-tail rectangle

$I_i^B=[Q_{0.025}(p_i\mid O),Q_{0.975}(p_i\mid O)].$

The external comparator is exact under a uniform distribution over compatible strict rankings and uses the analogous 0.025 and 0.975 marginal rank quantiles. These are marginal posterior credible rectangles, not identified sets and not frequentist confidence sets. “Same information” means the methods receive the same observed record; it does not make their inferential semantics identical. The fixed rejection bank is retained as a transparent baseline, not recommended as an efficient polytope sampler. Hit-and-run or sequential Monte Carlo is future work; no unrun sensitivity result is claimed.

For each performance estimator we report a Monte Carlo standard error over independent simulated replications: $s/\sqrt{N}$ for a mean and the equivalent Bernoulli standard error for binary coverage. Paired removal effects are computed replication by replication before their SE is calculated. The 20-seed standard deviation remains a random-stream stability diagnostic; empirical 2.5%-97.5% seed quantiles are not labeled confidence intervals.

## 7. Evaluation design

Twenty fixed seeds in the hash-locked evaluation configuration cover 12 internal regions (three active-set sizes by four outcome-noise levels) with 250 replications per seed-region and three external ordinal structures with 120 replications per seed-region. This gives 60,000 internal and 7,200 external known-truth cases. Clean simulations are implementation checks under correct specification. Positive outcome noise is a deliberately specified misspecification stress test, not an empirical institutional error rate.

Rule-aware and simplex-only identified sets are evaluated by joint truth membership. The legacy marginal-box diagnostic is shown only to document the metric correction. Bayesian rectangles use their explicitly defined credible-interval coverage. Maximum-entropy points are evaluated by point error and are excluded from coverage-width Pareto tests. The Pareto screen is an operational partial order—coverage no lower, width no higher, at least one strict—not an optimality theorem under an elicited loss function.

## 8. Results

### 8.1 Corrected internal coverage and MCSE

**Table 1. Joint-set coverage, legacy projection-envelope coverage, and width.** Each row pools the three active-set sizes and 20 fixed seeds at the stated noise level. MCSEs use all simulated replications in the row.

| outcome noise probability | method | joint set coverage | joint coverage mcse | projection box coverage | mean width | width mcse |
| --- | --- | --- | --- | --- | --- | --- |
| 0.00 | simplex-only | 1.000000 | 0.000000 | 1.000000 | 1.000000 | 0.000000 |
| 0.00 | rule-aware polytope | 1.000000 | 0.000000 | 1.000000 | 0.845077 | 0.000403 |
| 0.05 | simplex-only | 1.000000 | 0.000000 | 1.000000 | 1.000000 | 0.000000 |
| 0.05 | rule-aware polytope | 0.948800 | 0.001800 | 0.977933 | 0.841868 | 0.000452 |
| 0.10 | simplex-only | 1.000000 | 0.000000 | 1.000000 | 1.000000 | 0.000000 |
| 0.10 | rule-aware polytope | 0.898533 | 0.002465 | 0.957667 | 0.837820 | 0.000518 |
| 0.20 | simplex-only | 1.000000 | 0.000000 | 1.000000 | 1.000000 | 0.000000 |
| 0.20 | rule-aware polytope | 0.799867 | 0.003267 | 0.913533 | 0.830918 | 0.000584 |

[Insert Figure 3 near here]

Under clean generation, joint-set and projection-envelope coverage are both one. Under outcome noise, the projection box can still contain an infeasible truth, so it overstates coverage. Across positive-noise paired replications, removing elimination increases joint-set coverage by 0.117600, compared with the old projection-envelope change 0.050289. Width results are unchanged because the correction changes the coverage predicate, not the LP bounds.

**Table 2. Paired effect of removing the elimination constraint.** Changes are without-elimination minus full rule-aware, calculated within the same generated case.

| condition | paired replications | joint coverage change mean | joint coverage change mcse | legacy projection change mean | width change mean | width change mcse |
| --- | --- | --- | --- | --- | --- | --- |
| clean | 15000 | 0.000000 | 0.000000 | 0.000000 | 0.154923 | 0.000403 |
| positive_noise | 45000 | 0.117600 | 0.001519 | 0.050289 | 0.163131 | 0.000302 |

The direction of clean coverage and nested width is structural. The informative quantity is the magnitude under this generator, with its MCSE and stated misspecification boundary.

### 8.2 Exact ordinal endpoints

**Table 3. Legacy sampled/enumerated width versus exact MILP endpoint width.** “Monte Carlo” describes the legacy feasible-fraction computation; all revised endpoints are exact.

| regime | enumeration method | weeks | legacy mean width | exact mean width | maximum correction |
| --- | --- | --- | --- | --- | --- |
| R | exact | 13 | 0.885165 | 0.885165 | 0.000000 |
| R | monte_carlo | 1 | 0.966667 | 0.966667 | -0.000000 |
| R_plus | exact | 36 | 0.865234 | 0.865234 | 0.000000 |
| R_plus | monte_carlo | 37 | 0.981046 | 0.988184 | 0.025641 |

Among 470 contestant-week rows whose legacy endpoints came from sampled permutations, 23 have at least one corrected endpoint. The maximum normalized width correction is 0.266667, and the mean correction is 0.007318. The revised primary-policy mean exact width is 0.890986 in R and 0.927551 in R-plus. Feasible fractions and the weak/direct feasible-count ratio remain Monte Carlo estimates in large fields; their binomial MCSE applies to those proportions only and is not used to justify endpoint accuracy.

### 8.3 Rule-provenance sensitivity

**Table 4. Sensitivity to the uncertain season-28 rank-return assignment.** The primary scenario follows the COMAP reasonable assumption; the sensitivity excludes season 28 rather than asserting an undocumented alternative rule for it.

| rule provenance scenario | weeks | mean exact normalized rank width | mean direct R like exact normalized rank width | mean weak minus direct exact width |
| --- | --- | --- | --- | --- |
| primary_seasons_28_34 | 73 | 0.927551 | 0.870842 | 0.056710 |
| exclude_ambiguous_season_28 | 62 | 0.926487 | 0.874510 | 0.051978 |
| season_28_only | 11 | 0.933547 | 0.850167 | 0.083379 |

The weak-minus-direct comparison is within the same week and exact for rank-support width. Cross-season averages are descriptive because candidate fields, expert scores, event types, and histories differ.

### 8.4 Bayesian definition and undefined regions

**Table 5. Internal Bayesian rows below the fixed 100-accepted-draw threshold.** Denominators are complete; interval summaries are undefined in these rows.

| n active | outcome noise probability | denominator | undefined rows | undefined rate | accepted draws median | accepted draws min |
| --- | --- | --- | --- | --- | --- | --- |
| 4.0 | 0.00 | 5000 | 3 | 0.000600 | 3999.0 | 56 |
| 4.0 | 0.05 | 5000 | 4 | 0.000800 | 3967.5 | 8 |
| 4.0 | 0.10 | 5000 | 9 | 0.001800 | 3856.0 | 0 |
| 4.0 | 0.20 | 5000 | 15 | 0.003000 | 3718.0 | 8 |
| 5.0 | 0.00 | 5000 | 3 | 0.000600 | 3676.0 | 12 |
| 5.0 | 0.05 | 5000 | 6 | 0.001200 | 3619.0 | 6 |
| 5.0 | 0.10 | 5000 | 12 | 0.002400 | 3568.5 | 0 |
| 5.0 | 0.20 | 5000 | 17 | 0.003400 | 3451.0 | 1 |
| 6.0 | 0.00 | 5000 | 4 | 0.000800 | 3452.0 | 20 |
| 6.0 | 0.05 | 5000 | 3 | 0.000600 | 3400.0 | 17 |
| 6.0 | 0.10 | 5000 | 5 | 0.001000 | 3362.0 | 6 |
| 6.0 | 0.20 | 5000 | 13 | 0.002600 | 3216.5 | 0 |

There are 94 undefined internal rows, including 10 clean rows; the exact external ordinal posterior has 0 undefined rows. In the clean same-information seed-cell comparison retained from the verified experiment, Bayesian intervals strictly Pareto-dominate rule-aware intervals in 14/120 cells, all in the external seven-candidate, three-round region; reverse dominance is 0/120. Those 14 external results do not arise from internal rejection failures. They remain conditional on the uniform compatible-ranking posterior and on the operational Pareto criterion.

### 8.5 External simulation

The external known-truth simulation retains the previously verified result: the rule-aware and rule-agnostic ordinal sets contain the complete generated ranking across all three small-field structures, while direct-rule misspecification can exclude it. [Insert Figure 4 near here.] These cases are exact finite-state computations within the simulator and do not validate a historical institution.

## 9. Discussion

The exact endpoint formulation removes the main numerical mismatch in the ordinal analysis. Sampling remains useful for estimating compatible-state proportions and posterior masses, but a proportion MCSE cannot certify discovery of rare support endpoints. Separating these targets avoids transferring an error measure from one statistic to another.

The joint-coverage correction is equally consequential. Coordinate-wise sharp bounds summarize projections; they do not convert a polytope into a box. Reporting $C_{box}$ as set coverage masked some rule violations. The corrected result makes the simulated mechanism transparent: if the recorded outcome contradicts the generating rule, the hard rule-aware polytope excludes the generating truth, whereas the simplex-only set retains it at a width cost.

The paper does not derive a universal method-selection rule. Identified sets expose the consequences of institutional assumptions without adding a probability distribution within the set. Bayesian rectangles summarize probability under the fixed prior and zero-one likelihood. A user with a substantively defensible prior may prefer the latter; a user seeking assumption-transparent compatibility may prefer the former. Without an elicited loss function, coverage-width Pareto dominance is a descriptive screen rather than a complete decision theory.

## 10. Limitations

The empirical application identifies compatibility of latent public preferences; it does not produce an observed audience-vote estimate. The season-28 rule assignment is uncertain; excluding season 28 is reported, but undocumented historical tie-breaking and production decisions remain unidentified. Weekly rankings are not dynamically coupled. Exact endpoint MILPs do not give exact feasible-set cardinalities. The internal Bayesian rejection sampler has region-dependent failures and has not been replaced by a robust polytope sampler. Simulation results are conditional on the two generators, fixed grid, and specified noise process. No user, welfare, privacy, trust, cost, legal, or organizational outcome is measured; the earlier unmeasured “flexibility” and “accountability” figure panels and governance matrices are therefore removed from the main article.

## 11. Conclusion

Rule-constrained expert-crowd aggregation is naturally an inverse feasibility problem. Joint constraint membership is the correct coverage event for a polyhedral identified set, and exact optimization is the correct tool for sharp ordinal support endpoints when permutation enumeration is impractical. In this testbed, the corrections increase the measured coverage cost of outcome misspecification and reveal where sampled ordinal extrema were too narrow. The results support an auditable, rule-conditional methodology while leaving public preference partially identified.

## Data and code availability

    The empirical source is the official COMAP 2026 Problem C data file [14]. The local reproducibility bundle contains project-relative command-line scripts, fixed seeds, processed inputs, generated tables, tests, and hash manifests. The corrected Stage 32 code and evidence are publicly available in the versioned release `https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation/releases/tag/matcom-stage32-v1.0.1`. This statement identifies the public release directly and does not claim a persistent DOI archive.

## CRediT author contributions

Lizhen Deng: Conceptualization; Methodology; Software; Formal analysis; Investigation; Visualization; Writing - original draft; Writing - review and editing; Project administration. Yuxin Liu: Resources; Data curation; Validation. Bo Li: Resources; Data curation; Writing - review and editing.

## Funding

This research received no specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

## Competing interests

The authors declare no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Ethics statement

The study uses an official public competition dataset and synthetic simulations. It involves no intervention with human participants, collection of private participant data, or recovery of individual audience votes.

## Declaration of generative AI and AI-assisted technologies

During manuscript preparation, the authors used OpenAI ChatGPT/Codex for language editing, code review, test development, and reproducibility auditing. The authors reviewed and edited all outputs and take responsibility for the content.

## References

[1] C.F. Manski, Identification problems and decisions under ambiguity, Journal of Econometrics 95 (2) (2000) 415-442. https://doi.org/10.1016/S0304-4076(99)00045-7.

[2] E. Tamer, Partial Identification in Econometrics, Annual Review of Economics 2 (2010) 167-195. https://doi.org/10.1146/annurev.economics.050708.143401.

[3] G.W. Imbens, C.F. Manski, Confidence intervals for partially identified parameters, Econometrica 72 (6) (2004) 1845-1857. https://doi.org/10.1111/j.1468-0262.2004.00555.x.

[4] H. Kaido, F. Molinari, J. Stoye, Confidence Intervals for Projections of Partially Identified Parameters, Econometrica 87 (4) (2019) 1397-1432. https://doi.org/10.3982/ECTA14075.

[5] H.R. Moon, F. Schorfheide, Bayesian and Frequentist Inference in Partially Identified Models, Econometrica 80 (2) (2012) 755-782. https://doi.org/10.3982/ECTA8360.

[6] L. Xia, V. Conitzer, Determining Possible and Necessary Winners Given Partial Orders, Journal of Artificial Intelligence Research 41 (2011) 25-67. https://doi.org/10.1613/jair.3186.

[7] N. Betzler, B. Dorn, Towards a dichotomy for the Possible Winner problem in elections based on scoring rules, Journal of Computer and System Sciences 76 (8) (2010) 812-836. https://doi.org/10.1016/j.jcss.2010.04.002.

[8] Y. Bachrach, N. Betzler, P. Faliszewski, Probabilistic Possible Winner Determination, Proceedings of the AAAI Conference on Artificial Intelligence 24 (1) (2010) 697-702. https://doi.org/10.1609/aaai.v24i1.7609.

[9] P. Dey, N. Misra, On the exact amount of missing information that makes finding possible winners hard, Journal of Computer and System Sciences 135 (2023) 32-54. https://doi.org/10.1016/j.jcss.2023.02.003.

[10] T. Lu, C. Boutilier, Preference elicitation and robust winner determination for single- and multi-winner social choice, Artificial Intelligence 279 (2020) 103203. https://doi.org/10.1016/j.artint.2019.103203.

[11] T.P. Morris, I.R. White, M.J. Crowther, Using simulation studies to evaluate statistical methods, Statistics in Medicine 38 (11) (2019) 2074-2102. https://doi.org/10.1002/sim.8086.

[12] A. Burton, D.G. Altman, P. Royston, R.L. Holder, The design of simulation studies in medical statistics, Statistics in Medicine 25 (24) (2006) 4279-4292. https://doi.org/10.1002/sim.2673.

[13] T. Monks, C.S.M. Currie, B.S. Onggo, S. Robinson, M. Kunc, S.J.E. Taylor, Strengthening the reporting of empirical simulation studies: Introducing the STRESS guidelines, Journal of Simulation 13 (1) (2019) 55-67. https://doi.org/10.1080/17477778.2018.1442155.

[14] COMAP, 2026 MCM Problem C: Data With The Stars, The Consortium for Mathematics and Its Applications, 2026. https://contest.comap.com/undergraduate/contests/mcm/contests/2026/problems/index.html (accessed 2026-08-21).

## Figure captions

**Figure 1. Rule-conditioned inverse-inference architecture.** Observed expert inputs, the stated aggregation rule, and coarse outcomes map to a cardinal polytope or ordinal feasible-ranking set. Latent public preference remains partially identified.

**Figure 2. Reproducible comparison workflow.** The workflow separates configuration, information alignment, inference, simulation evaluation, and evidence auditing. Known-truth coverage is evaluated only in simulation.

**Figure 3. Corrected internal coverage-width evaluation.** Panel (a) distinguishes joint polytope membership from the legacy Cartesian product of marginal bounds; panel (b) reports mean coordinate width. Error bars are 95% Monte Carlo error intervals, estimate plus or minus 1.96 MCSE, over simulated replications. Outcome noise is a specified misspecification stress test.

**Figure 4. External ordinal simulation.** Known-truth coverage and normalized rank-support width across the three predeclared small-field structures. Results are conditional on the simulator and named tie policy.
