# Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences

## Abstract

Institutional designers must choose aggregation, discretion, tie-handling, and disclosure rules even when only coarse outcomes are observable and public preferences remain hidden. We develop a model-driven decision-support framework that represents this information gap through rule-assumption-conditioned feasible sets rather than point estimates of hidden votes. Percentage rules yield cardinal feasible intervals through linear programming; ranking and judge-save rules yield ordinal feasible-ranking sets under explicit tie and discretion assumptions. A decision cockpit translates feasible-set uncertainty, rule robustness, and compatible disclosure scenarios into conditional design recommendations, residual-uncertainty warnings, and an auditable decision record. Fixed-seed synthetic calibration evaluates coverage and false-certainty diagnostics when latent truth is available only inside the simulator. A second synthetic community-grant simulator checks the workflow under one different rule structure, while a longitudinal empirical application illustrates mechanism-specific feasible sets consistent with observed outcomes. In 250 replications at fixed seed 20260716, the no-noise rule-aware set has coverage 1.000 and mean normalized width 0.845, versus simplex-only coverage 1.000 and width 1.000. Under the stated 10% outcome-noise stress test, rule-aware coverage is 0.948 and width is 0.836, versus simplex-only coverage 1.000 and width 1.000. Artifact-level evaluation checks decision relevance, transparency, traceability, and reproducibility, but does not establish deployment, user validation, or organizational impact. The contribution is a model-driven prototype for representing uncertainty in institutional aggregation design under incomplete observability.

**Keywords:** Decision support systems; expert-crowd aggregation; hidden preferences; partial identification; institutional disclosure; rule robustness.

## 1. Introduction

Institutions and platforms often combine expert judgement with public input while disclosing only expert scores, rankings, eliminations, or final outcomes. Designers must nevertheless decide how much discretion to allow, which aggregation and tie rules to retain, and whether additional aggregate information should be disclosed. The practical problem is not simply predictive. When the public component is hidden, the same observed outcome can be compatible with multiple latent preference states, and an apparently decisive point estimate can conceal that ambiguity.

Decision Support Systems (DSS) research emphasizes foundations, functionality, implementation, interfaces, and evaluation that improve decision making rather than only automate a calculation [1,2]. This paper therefore treats hidden-preference aggregation as a design decision under incomplete observability. The supported user is an institutional organizer or platform governance analyst. The supported alternatives include retaining or revising an aggregation rule, narrowing or documenting expert discretion, pre-specifying a tie protocol, and releasing additional aggregate information. The system's job is to show what the observed record and stated rule jointly imply, how sensitive that implication is to assumptions, and which conditional recommendation follows from a declared design objective.

The central inferential object is a feasible set of latent public preferences consistent with the record, not a recovered ballot. Percentage aggregation induces a convex polytope of cardinal public-support vectors. Rank aggregation induces a set of feasible strict public rankings. A judge-save intervention weakens a direct elimination implication to tie-inclusive bottom-set membership. Because these mechanisms identify different mathematical objects, their uncertainty summaries are reported within regime and are not pooled into an unsupported common scale.

Figure 1 summarizes the architecture. Institutional evidence and decision context enter the rule-aware inference core; the decision cockpit returns bounded recommendations and preserves a governance feedback loop. The red boundary in the figure is substantive: outputs remain conditioned on observed records and stated rules, and hidden public preferences are not represented as observed.

[[FIGURE 1]]

The study makes four contributions. First, it supplies a **DSS foundation**: a rule-aware partial-identification model that converts documented institutional mechanisms and coarse outcomes into auditable feasible sets. Second, it supplies **DSS functionality**: a mechanism-evaluation framework for aggregation rules, expert-discretion assumptions, tie handling, disclosure regimes, and conclusion stability. Third, it supplies a **DSS artifact**: a JSON-configurable decision cockpit that converts feasible-set uncertainty into a conditional recommendation, warning, and decision trace. Fourth, it supplies **evaluation evidence**: a known-truth synthetic benchmark, a second synthetic rule structure, rule-agnostic set, point-proxy, and synthetic-oracle comparisons, robustness checks, an empirical illustration, and artifact-level evaluation.

The remainder of the paper defines the decision problem and evidence hierarchy, positions the contribution, documents the empirical testbed, formalizes the identified sets and metrics, presents the DSS artifact and mechanism-evaluation modules, reports synthetic and empirical evidence, and closes with design implications and limitations.

## 2. Decision-Support Problem and Research Questions

The decision maker supplies an institutional objective and a documented mechanism. Inputs include the active candidate set, observed expert scores or ranks, outcome type, eliminated or withdrawn units, regime, tie policy, judge-save interpretation, disclosure state, privacy/reporting constraints, and the decision objective. Outputs include the identified object, feasible-set width or rank support, an uncertainty class, a Rule Robustness Index (RRI) label when applicable, a disclosure recommendation, an accountability warning, and an audit trace. Table 1 makes the alternatives and limits explicit.

[[TABLE 1]]

The analysis addresses four research questions. **RQ1:** What cardinal or ordinal public-preference states remain feasible under each documented aggregation regime? **RQ2:** How does a weak judge-save implication change identifiability relative to direct elimination within the same rule environment? **RQ3:** How do truthful, compatible disclosures and tie assumptions change residual uncertainty and conclusion stability? **RQ4:** Can an auditable DSS artifact translate these conditional results into institution-design guidance without manufacturing certainty?

The artifact does not choose an institution's normative objective, perform legal or privacy review, measure stakeholder trust, or replace implementation authority. Recommendation quality is therefore conditional on locally supplied objectives and constraints.

**Decision-support implication.** The framework supports comparison of information consequences and governance tradeoffs while keeping normative choice and institutional authority with the decision maker.

## 3. Related Work

### 3.1 Model-driven DSS under uncertainty

DSS scholarship has long distinguished the theoretical foundations, decision tasks, artifacts, and evaluation practices needed to enhance decision making [1,2]. The present contribution belongs to the model-driven branch: a formal representation of institutional rules produces inspectable decision information, and the artifact exposes assumptions rather than hiding them behind a prediction score. Decisions under incomplete identification are naturally ambiguity-sensitive because multiple latent states remain compatible with the same observations [8-10]. The framework operationalizes that ambiguity as a decision input.

### 3.2 Aggregation mechanisms and hidden preferences

Aggregation rules are not interchangeable computational details. Foundational social-choice work establishes that collective outcomes depend on the aggregation relation [3,4], while rank-aggregation research formalizes the computational treatment of multiple orderings [5]. Preference inference likewise depends on the observed choice process [6]. These literatures motivate the separation between percentage-regime cardinal feasible regions and ranking-regime ordinal feasible sets. Evidence that social influence can alter collective judgements further cautions against equating an observed aggregate outcome with a directly observed public preference [7].

### 3.3 Partial identification, discretion, and disclosure

Partial identification retains all latent states compatible with incomplete observations rather than selecting one unsupported state [8,9]. Decision criteria such as minimax regret illustrate why unresolved states may remain decision-relevant [10]. Institutional discretion changes what an outcome reveals, so it must enter the observation rule rather than be treated as an after-the-fact correction [14]. Transparency research also cautions that disclosure is not synonymous with accountability or measured organizational benefit [12,13]. Accordingly, this paper evaluates disclosure as compatible constraint addition and reports privacy, cost, and accountability terms only as design considerations unless empirical evidence exists.

### 3.4 Evaluation and research gap

Prediction and identification answer different questions [11]. A prediction model may classify observed outcomes without identifying a hidden public input. Computational competitions can provide useful reproducible testbeds [15], but testbed performance is not automatic evidence of real organizational impact. Existing work has not sufficiently addressed how institutional designers can evaluate aggregation mechanisms when public preferences are hidden, expert intervention is rule-dependent, and disclosure policies determine the identifiability of collective preferences. The gap is therefore both inferential and operational: a DSS must preserve rule-conditioned uncertainty and translate it into an auditable design decision.

## 4. Data, Institutional Rules, and Evidence Scope

### 4.1 Longitudinal empirical testbed

The processed longitudinal panel contains 4,199 contestant-week records before identification-specific availability restrictions. The unified identification feature file contains 2,777 active contestant-week records, of which 2,766 have a typed public-appeal proxy. Its regime coverage is 248 P season-weeks (1,997 active contestant-weeks across 25 seasons), 14 R season-weeks (78 active contestant-weeks across 2 seasons), and 73 R-plus season-weeks (702 active contestant-weeks across 7 seasons). Of the 248 P weeks, 247 yield identification results. The remaining P week contains 11 records with missing typed proxies because its documented constraint construction was skipped; those records remain logged and are not imputed.

The data pipeline preserves zeros, parsed missing values, empty strings, and explicit missing tokens as distinct audit states until their meanings are documented. It also distinguishes withdrawals, no-elimination weeks, multiple eliminations, final rounds, scores above 10, and partner-name normalization. These cases are not silently coerced into ordinary elimination weeks. The empirical application is a repeated institutional testbed with documented regime changes; it is not a direct observation of public ballots and is not claimed to represent all expert-crowd systems.

### 4.2 Three regime-specific observation rules

In regime P, the combined decision uses a normalized expert component and a hidden cardinal public-support vector. In regime R, expert and public ranks are aggregated and the lowest combined standing is eliminated under a named tie policy. In regime R-plus, a judge-save intervention means that the observed eliminated contestant need only belong to an enlarged tie-inclusive bottom set before the save decision. Table 2 records the assumptions, violation consequences, and claim boundaries.

[[TABLE 2]]

No-elimination weeks add no comparative constraint. Withdrawals are non-comparative unless the record documents otherwise. Multiple eliminations constrain eliminated units relative to non-withdrawn survivors but do not impose an order among eliminated units. Final-order constraints are added only when documented placements support them. Hence P, R, and R-plus are three information environments with different identified objects, not interchangeable measures of one latent vote share.

### 4.3 Evidence hierarchy

The paper separates six evidence types: formal propositions; fixed-seed known-truth synthetic calibration; a structurally different external synthetic testbed; a real empirical application with hidden truth; artifact-level evaluation; and a scenario-based future user-evaluation protocol. Formal claims establish conditional set relations. Synthetic evidence evaluates logical calibration under a known simulator. The empirical application illustrates feasible sets consistent with observed outcomes. Artifact checks evaluate traceability and completeness, not human usefulness, adoption, or organizational impact.

**Decision-support implication.** Every reported quantity is interpreted within its rule and evidence type, which prevents a designer from treating incomparable or synthetic quantities as observed institutional outcomes.

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

Small fields are enumerated exactly. Larger fields use 10,000 fixed-seed uniform permutations. In the empirical runs, R has 13 exact and 1 sampled week; R-plus has 36 exact and 37 sampled weeks. The maximum reported Monte Carlo standard error for feasible fractions is approximately 0.005. This is numerical approximation error, not uncertainty about public behaviour.

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

**Decision-support implication.** The formal model tells the decision maker which assumptions create information and which conclusions disappear when those assumptions are relaxed.

## 6. DSS Artifact and Workflow

The model-driven DSS artifact has a documented JSON input contract and a structured output contract. Inputs record observed outcomes, active candidates, expert components, aggregation regime, tie policy, judge-save assumption, disclosure state, objective, and any locally supplied privacy or reporting constraints. The inference layer selects the mechanism-specific state space, encodes only documented constraints, checks feasibility, computes bounds or feasible rankings, and returns uncertainty and sensitivity diagnostics.

The decision cockpit compares predeclared alternatives rather than selecting an unconstrained optimum. Under an uncertainty-reduction objective, a broad compatible set triggers the least intrusive modeled disclosure that materially narrows uncertainty, accompanied by a privacy/reporting warning. Under a discretion-preservation objective, the artifact recommends documented eligibility and rationale rather than silently interpreting an intervention as direct elimination. Every output records the rule, tie, disclosure, objective, evidence type, residual uncertainty, and conditions under which the recommendation should be revisited.

Figure 2 shows the auditable sequence: frame the objective, encode the record, identify compatible states, compare designs, challenge robustness, and either revise assumptions/disclosure or issue a conditional decision record. Objective setting, legal/privacy review, stakeholder engagement, and implementation authority remain outside the artifact.

[[FIGURE 2]]

The prototype is a reproducible demonstration, not a deployed system. It has not been adopted by an organization, evaluated with human participants, or linked to measured organizational outcomes.

**Decision-support implication.** The cockpit makes rule assumptions, evidence boundaries, and residual uncertainty visible when an institutional design choice is recorded.

## 7. Mechanism-Evaluation Modules

### 7.1 Discretion-identifiability frontier

Figure 3 is a deterministic synthetic nested-rule scenario. The horizontal positions represent direct, weak-save, and broader-save assumptions; they are not a historical estimate of intervention strength. Relaxing a bottom-set implication increases the modeled flexibility index and may increase feasible-rank width. The empirical R-plus record supports only the direct-versus-weak comparison defined by the documented mechanism.

[[FIGURE 3]]

**Decision-support implication.** Expert discretion is treated as a governance tradeoff between exceptional-case flexibility, identifiability, and auditability, not as inherently beneficial or harmful.

### 7.2 Value of compatible institutional disclosure

Figure 4 compares truthful, compatible synthetic disclosure additions to the same latent state space. Outcome-only and judge-rank records leave mean normalized width 0.844 in the scenario; top-$k$ disclosure reduces it to 0.739, while vote bins, pairwise relations, and margin intervals produce progressively different reductions. The reported accountability design score is a scenario descriptor, not a measured trust, privacy, cost, or organizational outcome. The nesting claim applies only to compatible constraint addition.

[[FIGURE 4]]

The synthetic reductions relative to the outcome-only width are 12.5% for top-$k$ ranks, 88.3% for vote bins, and 92.7% for margin intervals. These values compare modeled information states; a real institution must assess privacy exposure, reporting cost, interpretability, and strategic response before choosing a disclosure channel.

**Decision-support implication.** The artifact can identify the least intrusive modeled disclosure that reaches a stated uncertainty objective while retaining an explicit governance warning.

### 7.3 Rule Robustness Index

Figure 5 reports the predeclared conclusion predicates, their supporting and applicable configurations, and RRI. All four evaluated conclusions have RRI 1.000 within their applicable configuration families. This establishes stability only across those predeclared checks; it neither exhausts institutional rule space nor establishes welfare optimality.

[[FIGURE 5]]

**Decision-support implication.** A recommendation can distinguish a conclusion that persists across evaluated assumptions from one that is sensitive or non-identifiable.

## 8. Evaluation Design and Baselines

### 8.1 Declared information-set comparison

Baselines are defined by the information they are permitted to use, not as a simple accuracy tournament. Table 3 specifies the naive expert-share point proxy, rule-agnostic ordinal representation, simplex-only partial-identification baseline, and synthetic full-disclosure oracle. Only the oracle sees latent synthetic truth, and only inside the simulator. The rule-aware and simplex-only sets share the same synthetic state space, with documented outcome-rule constraints added only to the rule-aware set. Proposition 2 therefore determines the weak set-inclusion relation when those added constraints are valid.

[[TABLE 3]]

### 8.2 Fixed-seed synthetic benchmark

The cardinal benchmark uses 250 replications with five active candidates and fixed seed 20260716. It generates latent public shares and expert shares, applies a percentage aggregation rule, records only coarse elimination outcomes, and hides latent truth from every inference method except the synthetic oracle. A separate 10% outcome-noise condition intentionally violates the generating rule as a stress test.

The evaluation reports known-truth coverage, mechanism-specific width, false certainty for zero-width proxies, outcome consistency, and feasibility. Coverage assesses whether a set contains synthetic truth; it is not a general prediction metric.

### 8.3 Structurally different external synthetic testbed

The external community-grant simulator starts with seven proposals, runs four elimination rounds, applies synthetic expert intervention in two rounds, adds one pairwise public-priority disclosure, and uses dense-rank tie handling with four-policy sensitivity. It differs from the main benchmark in state space, candidate count, repeated eliminations, intervention frequency, disclosure, and tie protocol. Its purpose is structural portability under stated conditions, not universal empirical validity.

## 9. Results

### 9.1 Synthetic calibration and baseline comparison

Table 4 and Figure 6 report the known-truth benchmark. In 250 replications at fixed seed 20260716 under correctly specified no-noise outcomes, the rule-aware feasible set has coverage 1.000 and mean normalized width 0.845, while the simplex-only rule-agnostic set has coverage 1.000 and width 1.000. Proposition 2 guarantees that valid added rule constraints cannot enlarge the set; the observed widths quantify the strict shrinkage in this simulator rather than establish its direction independently. Under the 10% outcome-noise stress condition, the rule-aware set has coverage 0.948 and mean width 0.836, while the simplex-only set has coverage 1.000 and width 1.000. Thus, under outcome noise, rule-aware coverage is lower than simplex-only coverage. This difference records a tradeoff between narrowing the set with rule constraints and retaining coverage of the generated truth, and it limits use when rules may be misspecified or outcomes contain noise. The stress-test values are not real-data error rates.

[[TABLE 4]]

The naive point proxy has synthetic false-certainty rate 1.000 under exact latent-vector matching. This diagnostic says that its zero-width assertion fails to equal the generated truth; it does not imply that point prediction is never useful for an observable outcome.

[[FIGURE 6]]

**Decision-support implication.** Proposition 2 determines set non-expansion only when added rule constraints are valid. The reported widths quantify that structural relation in this simulator; under outcome noise, the narrower rule-aware set has lower coverage than the simplex-only set.

### 9.2 External synthetic testbed

Table 5 and Figure 7 report the external ordinal benchmark. The rule-aware discretion model and rule-agnostic ordinal representation both cover the complete known synthetic ranking in every replication, while direct-rule misspecification has coverage 0.042 and false-certainty rate 0.958. Mean normalized feasible-rank width is 0.960 for the rule-aware discretion model and 1.000 for the rule-agnostic representation. In this second simulator, the encoded weak-discretion rule retains the generated ranking, while interpreting intervention as direct elimination can exclude it.

[[TABLE 5]]

[[FIGURE 7]]

**Decision-support implication.** Before transferring a mechanism-analysis workflow, designers can test whether the observation rule remains correctly encoded under the target institution's intervention and tie structure.

### 9.3 Longitudinal empirical application

The P regime has nonempty feasible regions in 247 of 248 eligible weeks and mean normalized coordinate-wise width 0.843. R and R-plus have mean normalized rank widths 0.891 and 0.924. These values are descriptive within regime and are not pooled as a causal cross-regime comparison. Within 73 R-plus weeks, the weak/direct feasible-set ratio averages 2.666, has median 1.572, is strictly greater than one in 56 weeks, equal in 17, and never smaller. These results instantiate Proposition 3 under the specified tie-inclusive bottom-$(k+1)$ interpretation.

The empirical record does not contain ground-truth public preferences. The results therefore illustrate rule-assumption-conditioned feasible sets and identifiability loss consistent with observed outcomes, not recovered public preferences. The 11 missing typed proxies remain logged and are not imputed.

**Decision-support implication.** Empirical intervals and rank supports should be read as limits of inference from the recorded mechanism, not as estimates with an unobserved error benchmark.

### 9.4 Artifact-level DSS evaluation

Figure 8 summarizes deterministic evidence-completeness checks for decision relevance, uncertainty transparency, recommendation interpretability, robustness awareness, disclosure-cost awareness, rule-design usefulness, reproducibility, and implementation feasibility. The prototype passes the predeclared artifact checks, including 69 reproducibility tests in the recorded artifact evaluation and a deterministic demonstration runtime of 0.027 seconds. These are artifact-level checks, not user-effectiveness or organizational-performance scores.

[[FIGURE 8]]

The scenario-based future user evaluation remains a protocol with no participants or human-subject results. It is designed to test decision trace completeness, comprehension of uncertainty warnings, recommendation consistency, and perceived usefulness only after ethics and study-design decisions are completed.

**Decision-support implication.** The artifact demonstrates inspectable decision-support properties and a reproducible evaluation path while leaving human usefulness and institutional impact for future evaluation.

## 10. Decision-Support Recommendations

Table 6 maps stated objectives to conditional rule and disclosure designs. The matrix does not produce an empirically optimal policy. It records which design follows under a declared objective, what information is required, and which governance risk remains outside the model.

[[TABLE 6]]

For transparency objectives, the artifact compares top-$k$, binned, pairwise, and interval disclosures only after checking compatibility and reporting privacy/reporting costs. For discretion objectives, it distinguishes narrowed eligibility from retained discretion with a disclosed trigger and rationale. For stability objectives, it recommends pre-specifying the tie and override protocol rather than interpreting rule changes after observing an outcome. For external auditability, it prioritizes versioned rules, checksums, seeds, and scenario configuration.

Table 7 aligns each main claim with its evidence type and mandatory boundary. This alignment is part of the artifact's accountability logic: a recommendation inherits the assumptions and evidence limitations of the calculation that supports it.

[[TABLE 7]]

**Decision-support implication.** Recommendation quality depends on documented objectives, rule fidelity, privacy constraints, reporting costs, and implementation authority that must be assessed locally.

## 11. Discussion

The framework recasts hidden-preference analysis as institutional decision analytics. The observation rule determines both the compatible state space and the scope of a defensible recommendation. A wide feasible set is not a failed estimate; it is evidence that the recorded mechanism does not support a narrower conclusion. This distinction is especially important in settings where institutional interfaces encourage a single score even though the underlying public signal is not observed.

The discretion-identifiability result is a governance tradeoff rather than a welfare ranking. A judge-save rule may preserve exceptional-case flexibility while weakening what a final elimination reveals about the public component. Disclosure can restore information only when it is compatible with the state space and must still be evaluated against privacy, reporting burden, gaming risk, and interpretability. RRI then indicates whether a conclusion persists across the configuration family that was actually evaluated, not across every conceivable institution.

The paper integrates four DSS layers. The formal layer represents incomplete observability through rule-aware feasible sets. The functional layer compares mechanisms, discretion, ties, and disclosure without pooling incompatible latent objects. The artifact layer translates uncertainty into a conditional recommendation and audit trace. The evaluation layer combines known-truth calibration, a second synthetic rule structure, empirical illustration, robustness checks, and artifact-level evidence. These layers do not establish organizational impact or user-level decision effects; they define and implement a model-driven prototype for institutional design under hidden inputs.

## 12. Limitations and Boundary Conditions

First, the method does not recover exact hidden votes. The empirical application is an institutional testbed, not universal proof, and no ground-truth public ballot is available for empirical validation. Second, the synthetic benchmarks validate logical calibration under their simulators, not real-world truth, stakeholder behaviour, or causal institutional effects. In the 10% outcome-noise stress test, the rule-aware set has coverage 0.948 and width 0.836, while the simplex-only set has coverage 1.000 and width 1.000. This is a coverage-width tradeoff: constraints that narrow the set can exclude generated truth when the rule is misspecified or outcomes contain noise. The benchmark uses one fixed seed and reports no interval or cross-seed distribution, so it cannot determine the stability of this tradeoff across random realizations.

Third, rule specification quality affects every feasible set. Alternative tie policies, undocumented interventions, outcome coding, withdrawal handling, or incompatible disclosures may change the result. Cardinal P widths and ordinal R/R-plus widths have different meanings and are not a common latent uncertainty measure. Sample composition and active-field size further limit descriptive cross-regime comparisons.

Fourth, artifact-level evaluation is not equivalent to deployment, adoption, user validation, trust, or organizational impact. No completed human-subject study is claimed. The cockpit does not conduct privacy, legal, ethical, or stakeholder review. Fifth, disclosure recommendations involve privacy exposure, strategic response, interpretability, and reporting cost that are not estimated by the current data. Finally, expert discretion is treated as a governance tradeoff, not as inherently harmful; institutions may value flexibility even when it weakens identifiability.

## 13. Conclusion

Rule-aware partial identification represents feasible public-preference uncertainty for expert-crowd aggregation when the public component is hidden. Percentage rules generate cardinal feasible polytopes, while ranking and judge-save rules generate ordinal feasible-ranking sets under explicit tie and discretion assumptions. Within the evaluated configurations and two simulators, the implemented disclosure, RRI, and calibration checks expose modeled information consequences. Proposition 2 supplies the conditional set-non-expansion result; the synthetic benchmark reports the shrinkage magnitude and coverage under its stated simulator.

The decision cockpit translates these quantities into conditional recommendations, residual-uncertainty warnings, and an auditable record. Its contribution is not recovery of an unobserved public will or proof of organizational impact. It is a reproducible prototype that records feasible conclusions, modeled disclosure effects, and the governance assumptions attached to each output.

## Data and Code Availability for Anonymized Review

The data and code supporting the findings of this study are available in a public repository. Repository details are supplied in the title page/submission metadata and will be fully disclosed after peer review according to journal requirements.

## References

[1] D. Arnott, G. Pervan, Eight key issues for the decision support systems discipline, Decision Support Systems 44 (3) (2008) 657-672. https://doi.org/10.1016/j.dss.2007.09.003.

[2] D. Arnott, G. Pervan, A critical analysis of decision support systems research, Journal of Information Technology 20 (2) (2005) 67-87. https://doi.org/10.1057/palgrave.jit.2000035.

[3] K.J. Arrow, A difficulty in the concept of social welfare, Journal of Political Economy 58 (4) (1950) 328-346. https://doi.org/10.1086/256963.

[4] H.P. Young, Condorcet's theory of voting, American Political Science Review 82 (4) (1988) 1231-1244. https://doi.org/10.2307/1961757.

[5] C. Dwork, R. Kumar, M. Naor, D. Sivakumar, Rank aggregation methods for the Web, in: Proceedings of the 10th International Conference on World Wide Web, 2001, pp. 613-622. https://doi.org/10.1145/371920.372165.

[6] A. Liang, Inference of preference heterogeneity from choice data, Journal of Economic Theory 179 (2019) 275-311. https://doi.org/10.1016/j.jet.2018.09.010.

[7] J. Lorenz, H. Rauhut, F. Schweitzer, D. Helbing, How social influence can undermine the wisdom of crowd effect, Proceedings of the National Academy of Sciences 108 (22) (2011) 9020-9025. https://doi.org/10.1073/pnas.1008636108.

[8] C.F. Manski, Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice, Journal of Econometrics 95 (2) (2000) 415-442. https://doi.org/10.1016/S0304-4076(99)00045-7.

[9] G.W. Imbens, C.F. Manski, Confidence intervals for partially identified parameters, Econometrica 72 (6) (2004) 1845-1857. https://doi.org/10.1111/j.1468-0262.2004.00555.x.

[10] C.F. Manski, Minimax-regret treatment choice with missing outcome data, Journal of Econometrics 139 (1) (2007) 105-115. https://doi.org/10.1016/j.jeconom.2006.06.006.

[11] G. Shmueli, To explain or to predict?, Statistical Science 25 (3) (2010) 289-310. https://doi.org/10.1214/10-STS330.

[12] M. Ananny, K. Crawford, Seeing without knowing: Limitations of the transparency ideal and its application to algorithmic accountability, New Media & Society 20 (3) (2018) 973-989. https://doi.org/10.1177/1461444816676645.

[13] F. Bannister, R. Connolly, The trouble with transparency: A critical review of openness in e-government, Policy & Internet 3 (1) (2011) 1-30. https://doi.org/10.2202/1944-2866.1076.

[14] B. Steunenberg, Agent discretion, regulatory policymaking, and different institutional arrangements, Public Choice 86 (3-4) (1996) 309-339. https://doi.org/10.1007/BF00136524.

[15] R.M. Bell, Y. Koren, Lessons from the Netflix Prize challenge, ACM SIGKDD Explorations Newsletter 9 (2) (2007) 75-79. https://doi.org/10.1145/1345448.1345465.

## Figure Captions

**Figure 1. Rule-aware DSS architecture under hidden public preferences.** Evidence type: theoretical decision-support framework. Institutional evidence and design context are converted into rule-assumption-conditioned feasible sets, uncertainty diagnostics, and bounded recommendations. The figure does not represent hidden preferences as observed.

**Figure 2. Decision-support workflow.** Evidence type: implementation-artifact workflow. The sequence separates supported configuration, inference, comparison, and recommendation tasks from objective setting, privacy/legal review, stakeholder engagement, and implementation authority. It is not a deployed or user-validated workflow.

**Figure 3. Discretion-identifiability frontier.** Evidence type: deterministic synthetic nested-rule scenario. The positions are modeled rule relaxations, not a historical intervention-strength estimate.

**Figure 4. Value of compatible institutional disclosure.** Evidence type: synthetic compatible-disclosure scenario. Width changes follow truthful constraint addition within one state space; design scores are not measured trust, privacy, cost, or accountability outcomes.

**Figure 5. Rule Robustness Index across predeclared conclusions.** Evidence type: formal and empirical configuration summary. RRI is the bounded share of applicable evaluated configurations supporting a conclusion, not institutional optimality.

**Figure 6. Synthetic benchmark calibration.** Evidence type: fixed-seed known-truth synthetic benchmark. Coverage applies only to latent preferences generated inside the simulator, and the noise condition is a misspecification stress test.

**Figure 7. External synthetic testbed.** Evidence type: structurally different synthetic community-grant setting. The result supports portability under the stated simulator, not universal empirical validity.

**Figure 8. DSS artifact evidence-completeness checks.** Evidence type: artifact-level evaluation. The checks concern implementation completeness, traceability, and reproducibility, not user effectiveness, adoption, trust, or organizational impact.

## Table Notes

**Table 1. Decision alternatives, institutional choices, and use boundaries.** Evidence type: decision-design template. Trust, privacy, cost, legal fit, and implementation authority require local evidence.

**Table 2. Assumption inventory and claim boundaries.** Evidence type: formal model audit. Assumptions define the conditional identified object and the consequence of violation.

**Table 3. Baseline definitions and information sets.** Evidence type: synthetic benchmark protocol. Oracle access is synthetic-only; the comparison is not a generic accuracy tournament.

**Table 4. Fixed-seed synthetic coverage and uncertainty results.** Evidence type: known-truth synthetic benchmark. Outcome-noise rows are misspecification stress tests, not empirical error rates.

**Table 5. External synthetic testbed results.** Evidence type: structurally different synthetic testbed. No real grant preference or organizational outcome is observed.

**Table 6. Conditional design recommendation matrix.** Evidence type: decision-design template. The matrix is not an empirical welfare ranking or automatic policy choice.

**Table 7. Claim-evidence alignment.** Evidence type: manuscript-integrity audit. Every main claim is bounded by its evidence type and mandatory limitation.
