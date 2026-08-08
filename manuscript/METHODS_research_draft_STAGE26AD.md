# Coverage-Width Tradeoffs in Rule-Constrained Expert-Crowd Aggregation

## Abstract

Institutional aggregation often reveals expert scores, ranks, eliminations, or final outcomes while leaving public preferences latent. We formulate rule-conditioned feasible sets: percentage rules produce cardinal support intervals, whereas ranking and judge-save rules produce ordinal feasible-ranking sets under explicit tie and discretion assumptions. Twenty preregistered seeds cover 12 internal parameter regions and three external rule structures, yielding 67,200 synthetic cases and 552,000 retained method-level rows across sensitivity, same-information baseline, and component-ablation runs. Rule-aware width is below the rule-agnostic comparator in 300/300 cells, as implied by the set nesting in Proposition 2 rather than an independent performance gain. Positive outcome noise lowers rule-aware coverage in 180/180 internal cells by a mean 0.050289. Removing the elimination constraint restores 0.050289 coverage while increasing width by 0.163131; clean-cell coverage is unchanged. In clean same-information comparisons, rule-aware intervals Pareto-dominate Bayesian intervals in 0/120 cells, whereas Bayesian intervals dominate in 14/120, all in the external seven-candidate, three-round region. The contribution is a bounded method-selection criterion, not a claim of uniform method superiority or observed user effects.

**Keywords:** Expert-crowd aggregation; latent public preference; partial identification; feasible support interval; coverage-width tradeoff; method selection.

## 1. Introduction

Institutions and platforms often combine expert judgement with public input while disclosing only expert scores, rankings, eliminations, or final outcomes. When the public component is hidden, the same observed outcome can be compatible with multiple latent preference states, and a point estimate can conceal that ambiguity. The inferential problem is to characterize what the record and stated rule identify without treating latent public preference as an observed vote.

The central object is a feasible set of latent public preferences consistent with the observation process. Percentage aggregation induces a convex polytope of cardinal public-support vectors. Rank aggregation induces a set of feasible strict public rankings. A judge-save intervention weakens a direct elimination implication to tie-inclusive bottom-set membership. Because these mechanisms identify different mathematical objects, their uncertainty summaries are reported within regime and are not pooled into a common scale.

Figure 1 summarizes the inference architecture. Institutional evidence enters a rule-conditioned constraint layer; the output is a feasible set, sensitivity record, and explicit assumption boundary. The red boundary is substantive: hidden public preferences remain latent.

[[FIGURE 1]]

The study makes three contributions. First, it localizes a coverage-width tradeoff to the elimination constraint in the registered internal simulator: removing that constraint under positive outcome noise restores a mean 0.050289 coverage while increasing mean width by 0.163131, with no clean-cell coverage change. Second, it identifies a method-selection boundary: Bayesian intervals Pareto-dominate rule-aware intervals in 14/120 clean paired cells, all in the external seven-candidate, three-round region, while the reverse comparison occurs in 0/120 cells. Third, it supplies a formal partial-identification framework for rule-conditioned cardinal and ordinal feasible sets; the 300/300 width ordering is interpreted as the empirical realization of Proposition 2, not as an independently discovered performance gain.

The remainder of the paper positions the partial-identification problem, documents the empirical and synthetic evidence, defines the rule-conditioned feasible sets, reports the multi-seed baseline and ablation results, and states the conditions under which each method is informative.

## 2. Inferential Problem and Research Questions

The observed record supplies the active candidate set, expert scores or ranks, outcome type, eliminated or withdrawn units, aggregation regime, tie policy, judge-save interpretation, and disclosure state. The analysis returns the identified object, feasible-set width or rank support, robustness diagnostics, and the conditions under which the result changes. Table 1 records the institutional alternatives and claim boundaries retained from the original design framing.

[[TABLE 1]]

The analysis addresses four research questions. **RQ1:** What cardinal or ordinal latent public-preference states remain feasible under each documented aggregation regime? **RQ2:** How does a weak judge-save implication change identifiability relative to direct elimination within the same rule environment? **RQ3:** Which registered constraint removals change coverage and width under clean and noisy synthetic outcomes? **RQ4:** How do rule-aware, rule-agnostic, maximum-entropy, and Bayesian methods compare when their observed information is aligned?

The framework does not choose an institution's normative objective, measure stakeholder welfare, or infer a true public vote from the empirical application. Its scope is the identified set and the method-selection boundary supported by the registered synthetic designs.

**Method-selection implication.** A method choice is conditioned on the observation rule, rule reliability, and the coverage-width objective rather than on a claim that one method applies uniformly.

## 3. Related Work

### 3.1 Partial identification and method selection under uncertainty

Partial identification replaces an unsupported point claim with the set of values consistent with observations and assumptions [6,14,15]. The inferential literature develops confidence regions for partially identified parameters, projections, subvectors, and other functions of identified sets [7,16,17]. Related work also connects choice data to preference heterogeneity and decisions under incomplete information [4,8]. This paper uses that logic in an institutional inverse problem: observed expert scores and coarse outcomes restrict, but do not reveal, the latent public component. Its contribution is not a new generic confidence-region procedure; it is the explicit mapping from heterogeneous aggregation rules to different cardinal and ordinal feasible objects and to a conditional method-selection boundary.

### 3.2 Computational social choice and aggregation rules

Social-choice foundations show that collective orderings depend on the aggregation rule and the admissible preference domain [1,2]. Algorithmic rank aggregation and computational social choice make the rule itself an explicit mathematical and computational object [3,18], while judgment-aggregation results show that jointly attractive aggregation requirements can be incompatible [19]. These literatures primarily map individual inputs into collective outcomes. The present study addresses the inverse direction: given expert inputs, a documented rule, and a coarse institutional outcome, which latent public states remain feasible? It therefore does not claim to solve voting-rule design or to rank social-choice mechanisms by welfare.

### 3.3 Expert judgment, crowd aggregation, and social influence

Crowd accuracy is not guaranteed by group size alone. Prior work studies how social influence can degrade collective estimates [5], how expertise or selected subsets can be used in aggregation [20,21], and how resistance to influence or network structure changes collective estimation [22,23]. More recent studies directly examine expertise effects and information aggregation beyond a simple independent-crowd model [24,25]. This paper does not optimize crowd composition or estimate individual expertise. It treats the public component as latent and asks how much the observed expert-crowd outcome identifies under the stated rule.

### 3.4 Simulation methodology, discretion, and the research gap

Simulation evidence requires declared data-generating factors, performance measures, verification and validation, sensitivity analysis, and transparent reporting [26-30]. The present evaluation accordingly separates known-truth calibration from the empirical testbed, fixes seeds and parameter cells in preregistered designs, reports undefined posterior rows, and distinguishes structural nesting from empirical performance. These controls support reproducibility within the registered simulators; they do not validate untested institutions, priors, likelihoods, or misspecification processes.

Transparency and discretion also have limits: more disclosure need not reveal the underlying process, and institutional discretion changes the mapping from observations to admissible latent states [10-12]. The resulting gap is a rule-aware, auditable comparison that distinguishes explanation from prediction [9], localizes which institutional constraint creates a coverage-width tradeoff, and compares feasible-set and posterior summaries on aligned information. The contribution is therefore a bounded method-selection criterion rather than a universal superiority claim.

## 4. Data, Institutional Rules, and Evidence Scope

### 4.1 Longitudinal empirical testbed

The empirical testbed uses the official COMAP 2026 MCM Problem C data file, Data With The Stars [13]. The processed longitudinal panel contains 4,199 contestant-week records before identification-specific availability restrictions. The unified identification feature file contains 2,777 active contestant-week records, of which 2,766 have a typed public-appeal proxy. Its regime coverage is 248 P season-weeks (1,997 active contestant-weeks across 25 seasons), 14 R season-weeks (78 active contestant-weeks across 2 seasons), and 73 R-plus season-weeks (702 active contestant-weeks across 7 seasons). Of the 248 P weeks, 247 yield identification results. The remaining P week contains 11 records with missing typed proxies because its documented constraint construction was skipped; those records remain logged and are not imputed.

The data pipeline preserves zeros, parsed missing values, empty strings, and explicit missing tokens as distinct audit states until their meanings are documented. It also distinguishes withdrawals, no-elimination weeks, multiple eliminations, final rounds, scores above 10, and partner-name normalization. These cases are not silently coerced into ordinary elimination weeks. The empirical application is a repeated institutional testbed with documented regime changes; it is not a direct observation of public ballots and is not claimed to represent all expert-crowd systems.

### 4.2 Three regime-specific observation rules

In regime P, the combined decision uses a normalized expert component and a hidden cardinal public-support vector. In regime R, expert and public ranks are aggregated and the lowest combined standing is eliminated under a named tie policy. In regime R-plus, a judge-save intervention means that the observed eliminated contestant need only belong to an enlarged tie-inclusive bottom set before the save decision. Table 2 records the assumptions, violation consequences, and claim boundaries.

[[TABLE 2]]

No-elimination weeks add no comparative constraint. Withdrawals are non-comparative unless the record documents otherwise. Multiple eliminations constrain eliminated units relative to non-withdrawn survivors but do not impose an order among eliminated units. Final-order constraints are added only when documented placements support them. Hence P, R, and R-plus are three information environments with different identified objects, not interchangeable measures of one latent vote share.

### 4.3 Evidence hierarchy

The paper separates five evidence types: formal propositions; multi-seed known-truth synthetic calibration; a structurally different external synthetic testbed; a real empirical application with hidden truth; and artifact-level reproducibility checks. Formal claims establish conditional set relations. Synthetic evidence evaluates the registered methods under known simulators. The empirical application illustrates feasible sets consistent with observed outcomes. Artifact checks concern traceability and execution, not human usefulness, adoption, or organizational impact.

**Method-selection implication.** Every reported quantity is interpreted within its rule, simulator, and inferential object, preventing a synthetic or posterior quantity from being presented as an observed institutional outcome.

## 5. Rule-Aware Partial-Identification Framework

### 5.1 Setup

For week $t$, let $A_t$ be the active set with size $n_t$. Let $q_{it}$ be contestant $i$'s normalized expert component. The record supplies the rule, outcome type, eliminated set $E_t$, withdrawal set, and any final order. The latent public object depends on the rule. The method identifies all latent states consistent with the documented observation process; it does not observe a public ballot.

### 5.2 Percentage-regime polytope

Under P, the latent public-support vector $p_t$ belongs to the unit simplex. Higher combined score is better. If eliminated candidate $e$ is compared with non-withdrawn survivor $s$, the documented rule implies $q_{et}+p_{et} \le q_{st}+p_{st}$. The rule-aware feasible polytope is

[[EQUATION 1: F_t^P = {p in R^(n_t): p_i >= 0, sum_i p_i = 1, p_e - p_s <= q_s - q_e for all (e,s) in E_t x S_t}.]]

For each active candidate, coordinate-wise linear programs produce sharp conditional lower and upper bounds:

[[EQUATION 2: L_it = min_(p in F_t^P) p_i,    U_it = max_(p in F_t^P) p_i.]]

The normalized coordinate width is

[[EQUATION 3: w_it^P = U_it - L_it,    with 0 <= w_it^P <= 1.]]

Bounds are sharp coordinate-wise; the vector of coordinate midpoints need not be jointly feasible. A feasible set is therefore not replaced by a synthetic point unless a clearly labeled descriptive proxy is required.

### 5.3 Ranking and judge-save regimes

Under R and R-plus, $r_t^J$ is the expert ranking and $r_t^F$ is a strict latent public ranking, both with 1 denoting best. The combined rank is $c_{it}=r_{it}^J+r_{it}^F$, so larger values are worse. Let $B_k(c_t;\tau)$ be the tie-inclusive bottom-$k$ set under tie policy $\tau$. The direct ranking feasible set is

[[EQUATION 4: F_t^R = {r^F in Pi(A_t): E_t is a subset of B_k(r^J + r^F; tau)}.]]

For R-plus, a weak judge-save implication enlarges the admissible bottom set by one save-eligible position:

[[EQUATION 5: F_t^(R+) = {r^F in Pi(A_t): E_t is a subset of B_(k+1)(r^J + r^F; tau)}.]]

With a fixed active set and tie policy, direct feasibility implies weak feasibility. The within-week identifiability-loss ratio is

[[EQUATION 6: F_t^R is a subset of F_t^(R+),    rho_t = |F_t^(R+)| / |F_t^R| when |F_t^R| > 0.]]

For candidate $i$, ordinal width is the range of feasible ranks normalized by $n_t-1$:

[[EQUATION 7: w_it^R = (max_(r in F_t) r_i - min_(r in F_t) r_i) / (n_t - 1).]]

Small fields are enumerated exactly. In the empirical runs, the one sampled R week uses 50,000 fixed-seed uniform permutations, while each of the 37 sampled R-plus weeks uses 10,000; R has 13 exact weeks and R-plus has 36. The maximum reported Monte Carlo standard error for feasible fractions is approximately 0.005. This is numerical approximation error, not uncertainty about public behaviour.

### 5.4 Disclosure, robustness, coverage, and false certainty

If disclosure state $d_2$ truthfully adds compatible constraints $C(d_2)$ to the same baseline state space as $d_1$, then

[[EQUATION 8: F_t(d_2) = F_t(d_1) intersect C(d_2),    so F_t(d_2) is a subset of F_t(d_1).]]

For a normalized width functional $W$ defined within one mechanism, disclosure uncertainty reduction is $[W(d_1)-W(d_2)]/W(d_1)$ when the denominator is positive. RRI is the share of applicable, predeclared configurations supporting a conclusion predicate:

[[EQUATION 9: RRI(h) = number of applicable configurations supporting h / number of applicable configurations,    0 <= RRI(h) <= 1.]]

In known-truth simulation, coverage is the proportion of replications in which the latent synthetic truth lies inside the reported feasible set. For a point proxy, false certainty is the proportion of replications in which its zero-width claim does not equal the known synthetic truth. In the external ordinal testbed, false certainty instead records a nonempty constrained set that excludes the complete known synthetic ranking under misspecification. These diagnostics are not empirical prediction accuracy.

### 5.5 Conditional propositions and invariants

**Proposition 1 (compatible disclosure nesting).** Under a fixed latent state space and correctly encoded truthful disclosure, additional conjunctive disclosure weakly shrinks the feasible set. This follows directly from Equation (8).

**Proposition 2 (rule-aware nesting).** If rule-aware constraints are valid additions to a rule-agnostic state space, the rule-aware set cannot be larger than the rule-agnostic set. Strict shrinkage requires at least one state excluded by the added rule information.

**Proposition 3 (weak judge-save expansion).** Under the same active set, combined-rank rule, and tie policy, the direct feasible set is contained in the weak judge-save set. Strict expansion occurs if a weak-only public ranking exists.

**Proposition 4 (cardinal-ordinal non-comparability).** Without a justified mapping or common functional, cardinal support intervals and ordinal rank supports cannot be interpreted as the same latent uncertainty scale.

Invariant tests require normalized widths and RRI values to lie in [0, 1], correct no-noise synthetic truth to remain feasible, compatible disclosure uncertainty to be non-increasing, and rule-aware width not to exceed a nested rule-agnostic baseline. Outcome noise is explicitly a misspecification stress test and may reduce coverage.

**Method-selection implication.** The formal model identifies which assumptions remove states and which conclusions disappear when those assumptions are relaxed.

## 6. Reproducible Inference Artifact and Workflow

The implementation has a documented JSON input contract and structured output contract. Inputs record observed outcomes, active candidates, expert components, aggregation regime, tie policy, judge-save assumption, and disclosure state. The inference layer selects the mechanism-specific state space, encodes the registered constraints, checks feasibility, and computes bounds, feasible rankings, or comparator outputs.

Every run records the rule, tie treatment, disclosure state, evidence type, residual uncertainty, seed, and configuration. Figure 2 shows the auditable sequence from record encoding through feasible-state construction, baseline comparison, robustness analysis, and evidence export. The artifact is a reproducible research implementation; no user-effectiveness or organizational-outcome claim is attached to it.

[[FIGURE 2]]

**Method-selection implication.** The artifact makes the information set and assumption changes inspectable for each comparator.

## 7. Mechanism-Evaluation Modules

### 7.1 Discretion-identifiability frontier

Figure 3 is a deterministic synthetic nested-rule scenario. The horizontal positions represent direct, weak-save, and broader-save assumptions; they are not a historical estimate of intervention strength. Relaxing a bottom-set implication increases modeled flexibility and may increase feasible-rank width. The empirical R-plus record supports only the direct-versus-weak comparison defined by the documented mechanism.

[[FIGURE 3]]

**Method-selection implication.** Expert discretion changes the observation rule and therefore the identified set; the model does not assign welfare value to that change.

### 7.2 Compatible disclosure constraints

Figure 4 compares truthful, compatible synthetic disclosure additions to the same latent state space. Outcome-only and judge-rank records leave mean normalized width 0.844 in the scenario; top-$k$ disclosure reduces it to 0.739, while vote bins, pairwise relations, and margin intervals produce different reductions. The nesting claim applies only to compatible constraint addition.

[[FIGURE 4]]

The synthetic reductions relative to the outcome-only width are 12.5% for top-$k$ ranks, 88.3% for vote bins, and 92.7% for margin intervals. These are modeled information changes, not measured privacy, cost, trust, or organizational outcomes.

**Method-selection implication.** Disclosure constraints can be compared by the feasible states they remove, subject to compatibility with the baseline state space.

### 7.3 Rule Robustness Index

Figure 5 reports predeclared conclusion predicates, their supporting and applicable configurations, and RRI. All four evaluated conclusions have RRI 1.000 within their applicable configuration families. This statement is bounded by the registered configurations and does not establish welfare or method ranking.

[[FIGURE 5]]

**Method-selection implication.** RRI distinguishes persistence across the evaluated configuration family from claims about untested institutions.

## 8. Evaluation Design and Baselines

### 8.1 Declared information-set comparison

The comparison distinguishes set estimators from point estimators. Rule-aware and rule-agnostic sets share each generated case; rule constraints are added only to the rule-aware set. The maximum-entropy center is a zero-width point summary of the rule-aware polytope and is evaluated by point recovery and error, not interval coverage. The Bayesian baseline uses the same observed record with a registered prior and zero-one constraint likelihood. The synthetic oracle sees latent truth only for calibration.

| Method | Observed information | Output | Permitted comparison |
|---|---|---|---|
| Rule-aware partial identification | Expert component, coarse outcome, registered rule | Feasible set | Coverage and width within simulator |
| Rule-agnostic partial identification | Active state space without outcome-rule constraints | Feasible set | Structural nesting comparator |
| Maximum-entropy center | Same rule-aware feasible polytope | Point | Point error and top-choice accuracy only |
| Bayesian latent-preference baseline | Same observed record plus registered prior and zero-one likelihood | Posterior interval | Coverage-width comparison under the registered prior |
| Full-disclosure oracle | Synthetic latent truth | Point | Calibration boundary; synthetic only |

### 8.2 Multi-seed internal benchmark

The internal percentage benchmark uses 20 preregistered seeds, active-set sizes 4, 5, and 6, outcome-noise probabilities 0, 0.05, 0.10, and 0.20, and 250 replications per seed-parameter cell. Outcome noise intentionally violates the generating rule. Seed-level means are summarized by the mean, median, sample standard deviation, and empirical 2.5%-97.5% interval; replications are not treated as independent seed-level observations.

### 8.3 Multi-seed external benchmark

The external ordinal simulator uses the same 20 seeds and three registered structures: six candidates with three rounds, seven candidates with three rounds, and seven candidates with four rounds. Each seed-structure cell has 120 replications. It varies candidate count, repeated eliminations, intervention, disclosure, and tie handling. Its purpose is to identify behavior within these structures, not to establish validity outside the simulators.

## 9. Results

### 9.1 Internal coverage-width tradeoff

Table 4 and Figure 6 report the internal multi-seed distributions. Rule-aware width is below simplex-only width in 240/240 internal seed-parameter cells. This direction is the realized set nesting in Proposition 2; the table quantifies its magnitude and does not treat it as independent evidence of method ranking. In the 60 clean cells, rule-aware coverage is not below simplex-only coverage. In all 180 positive-noise cells, rule-aware coverage is lower; the mean decline is 0.050289, with median 0.044000 and empirical 2.5%-97.5% interval [0.012000, 0.108000].

**Table 4. Multi-seed internal coverage and width.** Values are seed-level mean, median, sample standard deviation, and empirical 2.5%-97.5% interval. Outcome-noise rows are synthetic misspecification stress tests.

| Active candidates | Outcome noise | Method | Coverage: mean; median; SD; empirical 2.5%-97.5% | Width: mean; median; SD; empirical 2.5%-97.5% | Seeds x replications |
|---|---|---|---|---|---|
| 4 | 0.00 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 4 | 0.00 | Rule-aware set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 0.8248; med 0.8251; SD 0.0037; [0.8178, 0.8315] | 20 x 250 |
| 4 | 0.05 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 4 | 0.05 | Rule-aware set | 0.9786; med 0.9800; SD 0.0106; [0.9539, 0.9920] | 0.8208; med 0.8215; SD 0.0035; [0.8154, 0.8268] | 20 x 250 |
| 4 | 0.10 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 4 | 0.10 | Rule-aware set | 0.9544; med 0.9540; SD 0.0127; [0.9318, 0.9764] | 0.8146; med 0.8153; SD 0.0049; [0.8060, 0.8236] | 20 x 250 |
| 4 | 0.20 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 4 | 0.20 | Rule-aware set | 0.9072; med 0.9060; SD 0.0152; [0.8880, 0.9341] | 0.8061; med 0.8078; SD 0.0054; [0.7957, 0.8124] | 20 x 250 |
| 5 | 0.00 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 5 | 0.00 | Rule-aware set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 0.8463; med 0.8468; SD 0.0031; [0.8406, 0.8504] | 20 x 250 |
| 5 | 0.05 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 5 | 0.05 | Rule-aware set | 0.9792; med 0.9800; SD 0.0063; [0.9657, 0.9880] | 0.8432; med 0.8427; SD 0.0033; [0.8381, 0.8495] | 20 x 250 |
| 5 | 0.10 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 5 | 0.10 | Rule-aware set | 0.9592; med 0.9580; SD 0.0107; [0.9419, 0.9760] | 0.8391; med 0.8391; SD 0.0029; [0.8338, 0.8437] | 20 x 250 |
| 5 | 0.20 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 5 | 0.20 | Rule-aware set | 0.9170; med 0.9120; SD 0.0168; [0.8937, 0.9442] | 0.8330; med 0.8320; SD 0.0045; [0.8264, 0.8418] | 20 x 250 |
| 6 | 0.00 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 6 | 0.00 | Rule-aware set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 0.8641; med 0.8641; SD 0.0023; [0.8601, 0.8675] | 20 x 250 |
| 6 | 0.05 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 6 | 0.05 | Rule-aware set | 0.9760; med 0.9760; SD 0.0078; [0.9640, 0.9880] | 0.8616; med 0.8620; SD 0.0026; [0.8576, 0.8661] | 20 x 250 |
| 6 | 0.10 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 6 | 0.10 | Rule-aware set | 0.9594; med 0.9620; SD 0.0110; [0.9419, 0.9741] | 0.8597; med 0.8601; SD 0.0030; [0.8547, 0.8643] | 20 x 250 |
| 6 | 0.20 | Simplex-only set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 20 x 250 |
| 6 | 0.20 | Rule-aware set | 0.9164; med 0.9160; SD 0.0153; [0.8939, 0.9520] | 0.8536; med 0.8540; SD 0.0039; [0.8476, 0.8614] | 20 x 250 |

[[FIGURE 6]]

The leave-one-out ablation localizes this tradeoff within the registered simulator. Removing the elimination constraint in positive-noise cells changes coverage by +0.050289 and width by +0.163131 on average; coverage increases in 180/180 paired cells. Under zero outcome noise, removing elimination changes coverage in 0/60 cells. This is a paired synthetic mechanism localization, not a causal estimate for an observed institution. It supports a conditional rule: retain elimination constraints when the recorded elimination rule is treated as reliable; relax them when the analysis explicitly allows rule violation, accepting the wider feasible set.

### 9.2 External rule structure and component effects

Table 5 and Figure 7 report the external multi-seed distributions. Rule-aware and rule-agnostic ordinal sets have coverage 1.000 across the three registered structures, while direct-rule misspecification has lower coverage and nonzero false certainty. The result is conditional on the external simulator.

**Table 5. Multi-seed external coverage, width, and false certainty.** Values are seed-level mean, median, sample standard deviation, and empirical 2.5%-97.5% interval.

| Candidates | Rounds | Method | Coverage: mean; median; SD; empirical 2.5%-97.5% | Width: mean; median; SD; empirical 2.5%-97.5% | False certainty: mean; median; SD; empirical 2.5%-97.5% | Seeds x replications |
|---|---|---|---|---|---|---|
| 6 | 3 | Direct-rule misspecification | 0.2175; med 0.2125; SD 0.0473; [0.1496, 0.3008] | 0.9060; med 0.9067; SD 0.0056; [0.8944, 0.9161] | 0.7825; med 0.7875; SD 0.0473; [0.6992, 0.8504] | 20 x 120 |
| 6 | 3 | Rule-agnostic ordinal set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 0.0000; med 0.0000; SD 0.0000; [0.0000, 0.0000] | 20 x 120 |
| 6 | 3 | Rule-aware discretion set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 0.9542; med 0.9540; SD 0.0036; [0.9491, 0.9609] | 0.0000; med 0.0000; SD 0.0000; [0.0000, 0.0000] | 20 x 120 |
| 7 | 3 | Direct-rule misspecification | 0.2150; med 0.2167; SD 0.0348; [0.1583, 0.2710] | 0.9280; med 0.9277; SD 0.0044; [0.9206, 0.9365] | 0.7850; med 0.7833; SD 0.0348; [0.7290, 0.8417] | 20 x 120 |
| 7 | 3 | Rule-agnostic ordinal set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 0.0000; med 0.0000; SD 0.0000; [0.0000, 0.0000] | 20 x 120 |
| 7 | 3 | Rule-aware discretion set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 0.9619; med 0.9622; SD 0.0026; [0.9576, 0.9667] | 0.0000; med 0.0000; SD 0.0000; [0.0000, 0.0000] | 20 x 120 |
| 7 | 4 | Direct-rule misspecification | 0.0433; med 0.0417; SD 0.0166; [0.0250, 0.0794] | 0.8791; med 0.8795; SD 0.0056; [0.8707, 0.8880] | 0.9567; med 0.9583; SD 0.0166; [0.9206, 0.9750] | 20 x 120 |
| 7 | 4 | Rule-agnostic ordinal set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 0.0000; med 0.0000; SD 0.0000; [0.0000, 0.0000] | 20 x 120 |
| 7 | 4 | Rule-aware discretion set | 1.0000; med 1.0000; SD 0.0000; [1.0000, 1.0000] | 0.9591; med 0.9592; SD 0.0024; [0.9551, 0.9640] | 0.0000; med 0.0000; SD 0.0000; [0.0000, 0.0000] | 20 x 120 |

[[FIGURE 7]]

### 9.3 Same-information baselines and method-selection boundary

Table 6 compares rule-aware and Bayesian intervals in the 120 clean paired seed-cells for which Pareto direction was registered. Rule-aware intervals Pareto-dominate Bayesian intervals in 0/120 cells. Bayesian intervals dominate in 14/120 cells, all in the external seven-candidate, three-round region. The remaining cells have no strict Pareto direction. The maximum-entropy center has zero point width by definition and is excluded from this interval Pareto comparison; its point metrics remain separately reported.

**Table 6. Clean same-information coverage-width Pareto comparison.** Pareto direction requires coverage no lower and width no higher, with at least one strict inequality.

| Parameter region | Paired seed-cells | Rule-aware Pareto dominance | Bayesian Pareto dominance |
|---|---|---|---|
| internal n=4, noise=0.00 | 20 | 0 | 0 |
| internal n=5, noise=0.00 | 20 | 0 | 0 |
| internal n=6, noise=0.00 | 20 | 0 | 0 |
| external candidates=6, rounds=3 | 20 | 0 | 0 |
| external candidates=7, rounds=3 | 20 | 0 | 14 |
| external candidates=7, rounds=4 | 20 | 0 | 0 |
| Total clean comparison | 120 | 0 | 14 |

The fixed internal Bayesian draw bank produces 94 replication rows below the registered posterior-draw threshold, including 10 under zero outcome noise. All rows remain in the raw evidence; no bank was enlarged and no row was deleted. Coverage, width, posterior-center error, and top-choice means use rows with defined posterior intervals, while complete-denominator feasibility is reported separately. Excluding undefined intervals can change the Bayesian summaries, but the direction and magnitude cannot be determined without changing the registered draw design.

Across internal and external set comparisons, rule-aware width is below the rule-agnostic comparator in 300/300 paired seed-parameter cells. Proposition 2 supplies the direction of this result. The registered experiments quantify the widths, coverage costs, and method-selection boundary rather than establish a general ordering among inference methods.

### 9.4 Registered component effects

Table 7 reports leave-one-out effects. Removing save or tie handling lowers external coverage in 60/60 cells. Save removal also narrows the set on average, so it is not a one-dimensional loss; tie-handling removal widens it on average. Removing external disclosure or elimination leaves coverage unchanged while widening the set. No component interactions can be estimated because no joint removals were registered.

**Table 7. Registered component-removal effects.** Changes are component removed minus full configuration within paired seed-parameter cells.

| Synthetic setting | Removed component | Paired cells | Mean coverage change | Mean width change | Observed direction |
|---|---|---|---|---|---|
| Internal, zero outcome noise | Elimination | 60 | 0 in 60/60 | Not pooled here | Coverage unchanged |
| Internal, positive outcome noise | Elimination | 180 | +0.050289 | +0.163131 | Coverage recovered; set widened in 180/180 cells |
| External, all registered regions | Disclosure | 60 | 0.000000 | +0.129121 | Coverage unchanged; set widened |
| External, all registered regions | Elimination | 60 | 0.000000 | +0.078111 | Coverage unchanged; set widened |
| External, all registered regions | Save | 60 | -0.841389 | -0.059959 | Coverage fell in 60/60 cells while the set narrowed |
| External, all registered regions | Tie handling | 60 | -0.072917 | +0.004666 | Coverage fell in 60/60 cells and the set widened on average |

### 9.5 Longitudinal empirical application

The P regime has nonempty feasible regions in 247 of 248 eligible weeks and mean normalized coordinate-wise width 0.843. R and R-plus have mean normalized rank widths 0.891 and 0.924. These values are descriptive within regime and are not pooled as a causal cross-regime comparison. Within 73 R-plus weeks, the weak/direct feasible-set ratio averages 2.666, has median 1.572, is strictly greater than one in 56 weeks, equal in 17, and never smaller. These results instantiate Proposition 3 under the specified tie-inclusive bottom-$(k+1)$ interpretation.

The empirical record does not contain ground-truth public preferences. The results illustrate rule-assumption-conditioned feasible sets and identifiability loss consistent with observed outcomes, not recovered public preferences. The 11 missing typed proxies remain logged and are not imputed.

### 9.6 Reproducibility scope

Figure 8 summarizes deterministic evidence-completeness checks for traceability, robustness recording, output existence, and implementation reproducibility. These checks concern the research artifact. They are not scores of user effectiveness, adoption, trust, or organizational performance, and this study does not add a user experiment.

[[FIGURE 8]]

## 10. Method-Selection Implications

The results distinguish rule reliability from set-width preference. When elimination outcomes are generated consistently with the encoded rule, removing elimination does not change coverage in the 60 registered clean cells and widens the set. Under positive outcome noise, retaining elimination excludes generated truth in every registered cell; removing it recovers a mean 0.050289 coverage at a mean width cost of 0.163131. This conditional statement applies to the registered simulator and does not prescribe an institutional policy.

The Bayesian comparison supplies a second boundary. In the external seven-candidate, three-round region, Bayesian intervals have 14 strict Pareto dominances over rule-aware intervals and no reverse dominance is observed anywhere in the 120 clean comparison cells. In that region the registered evidence supports using the Bayesian comparator when its prior and likelihood are accepted. Outside that region, the registered Pareto test does not establish a strict direction, so method choice depends on whether prior-based posterior interpretation or assumption-transparent feasible-set interpretation is required.

Table 8 retains the conditional design matrix as an application aid, not an empirical welfare ranking.

[[TABLE 8]]

Table 9 aligns claims with evidence types and mandatory boundaries.

[[TABLE 9]]

## 11. Discussion

The framework's contribution is a conditional account of method use under hidden public preference. Proposition 2 explains why valid rule constraints cannot expand a nested feasible set. The multi-seed experiments add information that the proposition does not provide: the coverage cost under rule violation, the component associated with that cost in a leave-one-out design, and the parameter region in which the registered Bayesian interval has a strict coverage-width ordering.

The central practical question is not why rule-aware inference should replace Bayesian inference. The registered evidence does not support that replacement. The contribution is to state when their assumptions and outputs differ: rule-aware feasible sets expose consequences of the encoded institutional rule without a probability model; Bayesian intervals provide a posterior summary under the registered prior and likelihood and have a strict Pareto direction in part of the external grid. The appropriate method follows from the accepted assumptions and inferential target.

The empirical application remains an illustration of feasible states under documented mechanisms. It supplies no ground-truth public vote and cannot validate the synthetic method ordering. The synthetic component results likewise locate behavior inside the registered generators rather than estimate causal institutional effects.

## 12. Limitations and Boundary Conditions

First, the method does not recover exact hidden votes. The empirical application is an institutional testbed without a ground-truth public ballot, so its feasible sets cannot be scored for empirical recovery. Cardinal P widths and ordinal R/R-plus widths have different meanings and are not a common uncertainty scale.

Second, the synthetic findings are conditional on 20 preregistered seeds, the registered parameter grid, and two generators. The 300/300 width ordering follows the nesting condition in Proposition 2. The 180/180 positive-noise coverage loss and the elimination leave-one-out effect are stable within this grid but do not establish behavior under other misspecification processes or observed institutions.

Third, the component analysis removes one registered component at a time. It cannot identify two-way or higher-order interactions. External save removal lowers coverage while narrowing the set on average; therefore component effects cannot be reduced to a single benefit/loss scale.

Fourth, the Bayesian interval depends on the registered Dirichlet(1) or uniform-ranking prior and zero-one constraint likelihood. Other priors and likelihoods were not tested. The 94 insufficient-posterior replication rows, including 10 clean rows, have undefined interval metrics. Retaining them preserves the registered draw bank, but excluding undefined intervals from interval means can affect the Bayesian summary in a direction that cannot be determined from the current outputs.

Finally, no user, deployment, welfare, adoption, or organizational-effect claim is evaluated. This omission is handled by the method-focused positioning rather than by treating artifact checks as human evidence. Privacy, legal, ethical, and strategic consequences of disclosure remain outside the reported calculations.

## 13. Conclusion

Rule-conditioned partial identification represents latent public preference as a feasible set rather than an observed vote. The formal framework separates cardinal percentage aggregation from ordinal ranking and judge-save mechanisms and states the nesting conditions that generate width ordering.

The multi-seed evidence localizes a coverage-width tradeoff: under positive outcome noise, removing elimination recovers coverage in every registered cell while widening the set, whereas clean-cell coverage does not change. The same-information comparison does not show a general rule-aware ordering: Bayesian intervals dominate in 14/120 clean cells and the reverse occurs in 0/120. The resulting contribution is a method-selection account that links rule reliability, parameter region, and inferential assumptions to the choice between feasible-set and posterior summaries.

## Data and Code Availability

The empirical source is the official COMAP 2026 MCM Problem C data file [13], anonymously downloadable from the official problem page and byte-matched to SHA-256 `EA99CAEC6EA243BDB450A1971A95BA8A95701A93BE7FF29F0BA3C57D72DDFF52`. COMAP states that its material may be reproduced for academic/research purposes; the source is attributed and is not relicensed by this study. The code, fixed seed list, configurations, source-data copy, and audit artifacts are prepared at https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation. At this audit stage the repository remains private; public availability may be claimed only after the author-controlled release and an anonymous URL, raw-file, and clone verification.

## References

[1] K.J. Arrow, A difficulty in the concept of social welfare, Journal of Political Economy 58 (4) (1950) 328-346. https://doi.org/10.1086/256963.

[2] H.P. Young, Condorcet's theory of voting, American Political Science Review 82 (4) (1988) 1231-1244. https://doi.org/10.2307/1961757.

[3] C. Dwork, R. Kumar, M. Naor, D. Sivakumar, Rank aggregation methods for the Web, in: Proceedings of the 10th International Conference on World Wide Web, 2001, pp. 613-622. https://doi.org/10.1145/371920.372165.

[4] A. Liang, Inference of preference heterogeneity from choice data, Journal of Economic Theory 179 (2019) 275-311. https://doi.org/10.1016/j.jet.2018.09.010.

[5] J. Lorenz, H. Rauhut, F. Schweitzer, D. Helbing, How social influence can undermine the wisdom of crowd effect, Proceedings of the National Academy of Sciences 108 (22) (2011) 9020-9025. https://doi.org/10.1073/pnas.1008636108.

[6] C.F. Manski, Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice, Journal of Econometrics 95 (2) (2000) 415-442. https://doi.org/10.1016/S0304-4076(99)00045-7.

[7] G.W. Imbens, C.F. Manski, Confidence intervals for partially identified parameters, Econometrica 72 (6) (2004) 1845-1857. https://doi.org/10.1111/j.1468-0262.2004.00555.x.

[8] C.F. Manski, Minimax-regret treatment choice with missing outcome data, Journal of Econometrics 139 (1) (2007) 105-115. https://doi.org/10.1016/j.jeconom.2006.06.006.

[9] G. Shmueli, To explain or to predict?, Statistical Science 25 (3) (2010) 289-310. https://doi.org/10.1214/10-STS330.

[10] M. Ananny, K. Crawford, Seeing without knowing: Limitations of the transparency ideal and its application to algorithmic accountability, New Media & Society 20 (3) (2018) 973-989. https://doi.org/10.1177/1461444816676645.

[11] F. Bannister, R. Connolly, The trouble with transparency: A critical review of openness in e-government, Policy & Internet 3 (1) (2011) 1-30. https://doi.org/10.2202/1944-2866.1076.

[12] B. Steunenberg, Agent discretion, regulatory policymaking, and different institutional arrangements, Public Choice 86 (3-4) (1996) 309-339. https://doi.org/10.1007/BF00136524.

[13] COMAP, 2026 MCM Problem C: Data With The Stars, The Consortium for Mathematics and Its Applications, 2026. https://contest.comap.com/undergraduate/contests/mcm/contests/2026/problems/index.html (accessed 2026-08-08).

[14] E. Tamer, Partial Identification in Econometrics, Annual Review of Economics 2 (1) (2010) 167-195. https://doi.org/10.1146/annurev.economics.050708.143401.

[15] B. Kline, E. Tamer, Recent Developments in Partial Identification, Annual Review of Economics 15 (1) (2023) 125-150. https://doi.org/10.1146/annurev-economics-051520-021124.

[16] H. Kaido, F. Molinari, J. Stoye, Confidence Intervals for Projections of Partially Identified Parameters, Econometrica 87 (4) (2019) 1397-1432. https://doi.org/10.3982/ecta14075.

[17] F.A. Bugni, I.A. Canay, X. Shi, Inference for subvectors and other functions of partially identified parameters in moment inequality models, Quantitative Economics 8 (1) (2017) 1-38. https://doi.org/10.3982/qe490.

[18] F. Brandt, V. Conitzer, U. Endriss, J. Lang, A.D. Procaccia, Introduction to Computational Social Choice, in: Handbook of Computational Social Choice, Cambridge University Press, 2016, pp. 1-20. https://doi.org/10.1017/CBO9781107446984.002.

[19] C. List, P. Pettit, Aggregating Sets of Judgments: An Impossibility Result, Economics and Philosophy 18 (1) (2002) 89-110. https://doi.org/10.1017/S0266267102001098.

[20] D.V. Budescu, E. Chen, Identifying Expertise to Extract the Wisdom of Crowds, Management Science 61 (2) (2015) 267-280. https://doi.org/10.1287/mnsc.2014.1909.

[21] A.E. Mannes, J.B. Soll, R.P. Larrick, The wisdom of select crowds, Journal of Personality and Social Psychology 107 (2) (2014) 276-299. https://doi.org/10.1037/a0036677.

[22] G. Madirolas, G.G. de Polavieja, Improving Collective Estimations Using Resistance to Social Influence, PLOS Computational Biology 11 (11) (2015) e1004594. https://doi.org/10.1371/journal.pcbi.1004594.

[23] J. Becker, D. Brackbill, D. Centola, Network dynamics of social influence in the wisdom of crowds, Proceedings of the National Academy of Sciences 114 (26) (2017). https://doi.org/10.1073/pnas.1615978114.

[24] J.L. Fiechter, N. Kornell, How the wisdom of crowds, and of the crowd within, are affected by expertise, Cognitive Research: Principles and Implications 6 (1) (2021) 5. https://doi.org/10.1186/s41235-021-00273-6.

[25] T. Kameda, W. Toyokawa, R.S. Tindale, Information aggregation and collective intelligence beyond the wisdom of crowds, Nature Reviews Psychology 1 (6) (2022) 345-357. https://doi.org/10.1038/s44159-022-00054-y.

[26] A. Burton, D.G. Altman, P. Royston, R.L. Holder, The design of simulation studies in medical statistics, Statistics in Medicine 25 (24) (2006) 4279-4292. https://doi.org/10.1002/sim.2673.

[27] T.P. Morris, I.R. White, M.J. Crowther, Using simulation studies to evaluate statistical methods, Statistics in Medicine 38 (11) (2019) 2074-2102. https://doi.org/10.1002/sim.8086.

[28] J.P.C. Kleijnen, Verification and validation of simulation models, European Journal of Operational Research 82 (1) (1995) 145-162. https://doi.org/10.1016/0377-2217(94)00016-6.

[29] J.P.C. Kleijnen, An overview of the design and analysis of simulation experiments for sensitivity analysis, European Journal of Operational Research 164 (2) (2005) 287-300. https://doi.org/10.1016/j.ejor.2004.02.005.

[30] T. Monks, C.S.M. Currie, B.S. Onggo, S. Robinson, M. Kunc, S.J.E. Taylor, Strengthening the reporting of empirical simulation studies: Introducing the STRESS guidelines, Journal of Simulation 13 (1) (2019) 55-67. https://doi.org/10.1080/17477778.2018.1442155.
## Figure Captions
**Figure 1. Rule-conditioned inference architecture under latent public preferences.** Institutional evidence is converted into rule-assumption-conditioned feasible sets and uncertainty diagnostics. The figure does not represent hidden preferences as observed.

**Figure 2. Reproducible inference workflow.** The sequence separates configuration, inference, comparison, robustness checks, and evidence export. It is not a deployed or user-validated workflow.

**Figure 3. Discretion-identifiability frontier.** Evidence type: deterministic synthetic nested-rule scenario. The positions are modeled rule relaxations, not a historical intervention-strength estimate.

**Figure 4. Value of compatible institutional disclosure.** Evidence type: synthetic compatible-disclosure scenario. Width changes follow truthful constraint addition within one state space; design scores are not measured trust, privacy, cost, or accountability outcomes.

**Figure 5. Rule Robustness Index across predeclared conclusions.** RRI is the bounded share of applicable evaluated configurations supporting a conclusion, not a method or welfare ranking.

**Figure 6. Multi-seed internal sensitivity.** Coverage and normalized width are summarized across 20 seeds; bands are empirical 2.5%-97.5% intervals of seed-level estimates. Outcome noise is a synthetic misspecification stress test.

**Figure 7. Multi-seed external sensitivity.** Coverage and normalized feasible-rank width are summarized across 20 seeds and three registered candidate-round structures; bands are empirical 2.5%-97.5% intervals.

**Figure 8. Artifact evidence-completeness checks.** The checks concern implementation completeness, traceability, and reproducibility, not user effectiveness, adoption, trust, or organizational impact.

## Table Notes

**Table 1. Institutional alternatives and use boundaries.** Retained as a design-context inventory; welfare, privacy, cost, legal fit, and implementation authority require local evidence.

**Table 2. Assumption inventory and claim boundaries.** Assumptions define the conditional identified object and the consequence of violation.

**Table 3. Baseline definitions and aligned information sets.** Point and interval outputs are evaluated by output-appropriate metrics; oracle access is synthetic-only.

**Table 4. Multi-seed internal coverage and width.** Outcome-noise rows are synthetic misspecification stress tests, not empirical error rates.

**Table 5. Multi-seed external coverage, width, and false certainty.** No real grant preference or organizational outcome is observed.

**Table 6. Clean same-information Pareto comparison.** Maximum-entropy point outputs are excluded because zero point width is not interval evidence.

**Table 7. Component-removal effects.** Effects are paired synthetic leave-one-out differences; interactions are not identified.

**Table 8. Conditional design matrix.** The matrix is not an empirical welfare ranking or automatic policy choice.

**Table 9. Claim-evidence alignment.** Each claim is bounded by its evidence type and stated limitation.
