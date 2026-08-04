# Non-Anonymized Manuscript: Author Metadata Required

# Title Page

## Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences

**Authors:** [AUTHOR NAMES TO COMPLETE]

**Affiliations:** [AUTHOR AFFILIATIONS TO COMPLETE]

**Corresponding author:** [NAME, POSTAL ADDRESS, AND EMAIL TO COMPLETE]

This title page is a completion template. It is not evidence that author metadata, declarations, or journal portal requirements have been finalized.


# Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences

## Abstract

Institutional designers often combine expert judgment with public input while retaining only coarse outcomes. When public preferences are hidden, the same observed elimination can be consistent with multiple collective states, expert intervention, and rule-specific artifacts. We develop a rule-aware decision-support framework that represents this uncertainty through feasible preference sets rather than a point estimate of hidden votes. Documented percentage rules yield cardinal feasible intervals, ranking rules yield ordinal feasible rankings, and a weak judge-save condition exposes a discretion-identifiability tradeoff. The framework evaluates rule, tie-handling, and disclosure assumptions through a discretion frontier, synthetic disclosure scenarios, and a Rule Robustness Index. A JSON-configurable DSS prototype maps documented outcomes and institutional objectives to conditional uncertainty classes, design warnings, disclosure recommendations, and accountability records. Fixed-seed synthetic benchmarks assess coverage and false certainty when truth is known only inside the simulator; a structurally different synthetic community-grant testbed examines portability. A longitudinal empirical application demonstrates mechanism-specific feasible sets under hidden truth. The study provides design-oriented decision support under incomplete observability. It does not recover exact public preferences, demonstrate organizational impact, or report a completed human-subject evaluation.

**Keywords:** Decision support systems; expert-crowd aggregation; hidden preferences; partial identification; institutional disclosure; rule robustness.

## 1. Introduction

Organizations often need to evaluate an aggregation rule after only coarse outcomes, while the collective component remains hidden. The resulting decision problem is not to impute a public vote but to assess what a documented rule permits later observers to learn and how alternative rules or disclosures alter that uncertainty. Figure 1 presents this rule-aware decision-support framing, and Figure 2 locates it in an institutional workflow.

This paper makes four contributions. First, it formalizes rule-aware partial identification for hidden public preferences. Second, it compares rule, discretion, tie, and disclosure assumptions. Third, it implements a design-oriented DSS prototype. Fourth, it supplies a reproducible evaluation package with synthetic calibration, an external synthetic testbed, baselines, and robustness checks. **Decision-support implication.** Institutional designers can use the framework to compare information consequences without presenting a hidden preference point as observed.

## 2. Decision-Support Problem

The supported user is an institutional organizer or platform governance analyst deciding whether to retain an aggregation mechanism, document or narrow expert discretion, alter a tie protocol, or disclose additional aggregate information. Table 1 lists the decision alternatives and criteria. The system accepts documented outcomes, a rule type, a judge-save assumption, a tie-handling assumption, a disclosure regime, and a decision objective. It reports compatible-state uncertainty, a bounded recommendation, and the records needed for later audit.

The system does not choose objectives, perform legal or privacy review, measure stakeholder trust, or replace implementation authority. **Decision-support implication.** The appropriate output is a conditional design recommendation with an uncertainty warning, not an automated institutional decision.

## 3. Related Work

Decision-support research emphasizes the disciplined design and evaluation of systems that help decision makers reason with models, information, and uncertainty (Arnott & Pervan, 2005, 2008). In expert-crowd settings, observed collective outcomes can be shaped by social influence and institutional aggregation, so observed results should not be equated with a directly observed public preference (Lorenz et al., 2011). Partial-identification methods instead retain the set of latent states compatible with incomplete observations and make the consequences for decisions explicit (Manski, 2000; Imbens & Manski, 2004). Transparency and accountability research also cautions that disclosure has limits and tradeoffs; this study therefore models compatible information additions without treating its scenario scores as measured trust, privacy, or accountability outcomes (Ananny & Crawford, 2018; Bannister & Connolly, 2011).

Existing research has not sufficiently addressed how institutional designers can evaluate aggregation mechanisms when public preferences are hidden, expert intervention is rule-dependent, and disclosure policies determine the identifiability of collective preferences.
## 4. Rule-Aware Partial-Identification Framework

For a percentage week, let p be the latent public-support vector in the unit simplex and q the observed normalized expert component. A documented elimination creates affine comparisons between eliminated and surviving candidates. The identified feasible set is the intersection of these constraints with the simplex; coordinate-wise linear programs obtain sharp conditional bounds. Table 2 records the assumption inventory. No-elimination and withdrawal weeks add no comparative outcome constraint; multiple eliminations and final-order information are handled only when their rule inputs are documented.

For ranking and judge-save regimes, the hidden object is a strict public ranking. Feasible rankings are those consistent with expert ranks, the named tie policy, and a direct or weak bottom-set implication. Cardinal and ordinal summaries remain mechanism-specific and are not pooled into a common public-support scale. **Decision-support implication.** A decision maker can see whether a rule changes the identifiable object before comparing policy alternatives.

## 5. DSS Artifact and Workflow

The prototype operationalizes the model as a JSON-configurable decision-support artifact. Figure 2 shows the organizer workflow from coarse outcomes through compatible states and warnings to a documented disclosure or rule choice. Its input/output contract and decision trace are reported in the artifact audit. The demonstration uses illustrative synthetic inputs and reports a broad conditional width; it is not an empirical replay or deployed system.

**Decision-support implication.** The artifact translates rule-aware uncertainty into an auditable recommendation while retaining objective setting and governance review outside the system.

## 6. Mechanism Evaluation Modules

### 6.1 Discretion-Identifiability Frontier

Figure 3 is a deterministic synthetic rule scenario that relaxes a direct bottom-set implication. The separate empirical R-plus comparison evaluates only the documented direct-versus-weak condition. The synthetic continuum is not a historical scale of intervention strength. **Decision-support implication.** Discretion can be evaluated as a governance tradeoff between flexibility and later identifiability, conditional on disclosed eligibility rules.

### 6.2 Value of Institutional Disclosure

Figure 4 compares synthetic compatible disclosure additions. The formal weak-shrinkage statement applies only when added information is truthful and compatible with the baseline constraints; privacy, cost, interpretability, and accountability values are scenario descriptors rather than measured outcomes. **Decision-support implication.** The artifact can select the least intrusive modeled disclosure that reduces compatible-state uncertainty while recording unresolved governance tradeoffs.

### 6.3 Rule Robustness Index

Figure 5 reports the share of predeclared applicable configurations supporting each conclusion. RRI is bounded in [0,1] and does not establish welfare optimality. **Decision-support implication.** A reported recommendation can distinguish robust conclusion predicates from assumption-sensitive ones instead of hiding rule dependence.

## 7. Synthetic Benchmark

Table 3 defines the baseline information sets, and Table 4 reports known-truth synthetic coverage results. Under correctly specified, no-noise simulated outcomes, the rule-aware feasible set covers the synthetic latent preference with rate 1.000. Under the explicitly labeled noisy-outcome stress test, coverage is 0.948. Figure 6 displays coverage and false-certainty diagnostics. The full-disclosure oracle is synthetic only, and prediction baselines do not become hidden-preference recovery tools.

**Decision-support implication.** Calibration evidence supports retaining feasible-set uncertainty under a stated simulator, rather than selecting a point estimate that can create false certainty.

## 8. External Testbed

The structurally different community-grant simulator starts with seven candidates, runs four elimination rounds, includes two synthetic intervention rounds, uses pairwise disclosure, and applies dense-rank tie handling with sensitivity checks. Figure 7 and Table 5 show that the correct rule-aware representation has synthetic coverage 1.000 and mean normalized feasible-rank width 0.960. This is structural portability evidence, not universal empirical validity.

**Decision-support implication.** Designers can assess whether a rule-aware workflow remains coherent under a different institutional mechanism before treating it as a general-purpose recommendation.

## 9. Empirical Application

The longitudinal application supplies repeated documented rule regimes with hidden public truth. Percentage weeks have mean normalized coordinate-wise feasible width 0.843; R-plus weeks have mechanism-specific normalized rank width 0.924. These quantities are not direct measurements on a common latent scale. The application illustrates feasible sets consistent with observed outcomes and conditioned on rule assumptions.

 **Decision-support implication.** Empirical users should interpret reported intervals and ranking supports as limits of inference from coarse records; they do not recover public preferences.

## 10. DSS Artifact-Level Evaluation

Figure 8 and the artifact evaluation matrix inspect decision relevance, uncertainty transparency, recommendation interpretability, robustness awareness, disclosure-cost awareness, rule-design usefulness, reproducibility, and implementation feasibility. The future user evaluation remains a scenario-based protocol with no participants or human-subject results.

**Decision-support implication.** The prototype demonstrates inspectable decision-support properties and a future validation pathway, but does not claim measured usability, adoption, or organizational performance.

## 11. Decision-Support Recommendations

 Table 6 maps stated objectives to conditional rule and disclosure designs. The recommendations do not choose an optimal policy: they help an institution record why it selected a disclosure or discretion policy and what uncertainty remains. Table 7 maps each main claim to its evidence and boundary.

**Decision-support implication.** Recommendation quality depends on documented objectives, rule fidelity, and local privacy or reporting constraints that remain outside the model.

## 12. Discussion

The framework shifts attention from estimating a hidden public quantity to evaluating the institutional observation rule that makes that quantity only partially identified. It preserves the distinction between cardinal and ordinal objects, exposes discretion as information-relevant, and makes disclosure an explicit design choice. The evidence hierarchy separates formal results, synthetic calibration, structural simulation, empirical illustration, artifact checks, and a future user-evaluation protocol.

**Decision-support implication.** A DSS can enhance institutional reasoning by exposing what the record supports and what additional disclosure or rule documentation would be needed for a stronger conclusion.

## 13. Limitations

The method does not recover exact hidden votes. The empirical application is an institutional testbed rather than universal proof. Synthetic benchmarks assess logical calibration rather than real-world truth. Artifact-level evaluation is not deployed organizational impact, and no completed human-subject study is claimed. Rule specification quality affects all compatible-state conclusions. Disclosure recommendations involve unmeasured privacy and reporting-cost tradeoffs. Expert discretion is modeled as a governance tradeoff rather than inherently harmful.

**Decision-support implication.** Users must preserve the rule, tie, disclosure, and objective assumptions alongside every recommendation.

## 14. Conclusion

Rule-aware partial identification provides a decision-support response to hidden public preferences and coarse institutional feedback. The contribution is a reproducible prototype that links documented rule assumptions to compatible-state uncertainty, conditional disclosure guidance, and audit records. Its claims are deliberately bounded by the evidence hierarchy and require author-side completion of citations, declarations, and live journal compliance checks before submission.

**Decision-support implication.** The manuscript supports author-side completion as a DSS submission draft, not an upload-ready claim of deployed or universally validated decision support.

## Figure Captions

**Figure 1. DSS conceptual framework.** Evidence type: theoretical decision-support framework. Documented rules and coarse outcomes lead to rule-specific feasible sets, not observed public votes.

**Figure 2. Decision-support workflow.** Evidence type: design-oriented DSS artifact workflow. The workflow separates supported configuration and recommendation tasks from external governance responsibilities; it is not a deployed or user-validated workflow.

**Figure 3. Discretion-identifiability frontier.** Evidence type: deterministic synthetic rule scenario. It illustrates nested weak-rule relaxation and is not a historical scale of expert intervention.

**Figure 4. Synthetic disclosure uncertainty curve.** Evidence type: synthetic compatible-disclosure scenario. Scenario descriptors are not measured trust, privacy, or cost outcomes.

**Figure 5. Rule Robustness Index.** Evidence type: formal/empirical configuration summary. RRI is a bounded share of applicable configurations, not a measure of institutional optimality.

**Figure 6. Synthetic benchmark coverage.** Evidence type: fixed-seed known-truth synthetic simulation. Coverage applies only to latent preferences generated inside the simulator.

**Figure 7. External synthetic testbed comparison.** Evidence type: structurally different synthetic community-grant setting. It demonstrates portability under stated conditions, not universal empirical validity.

**Figure 8. Artifact evidence-completeness checks.** Evidence type: artifact-level evaluation. The graphic is not a user-effectiveness, trust, adoption, or organizational-impact score.

## Table Notes

**Table 1. Decision alternatives and criteria.** Evidence type: design template; cost, privacy, and trust require local stakeholder evidence.

**Table 2. Assumption inventory.** Evidence type: formal model audit; assumptions define the conditional identified object.

**Table 3. Baseline definitions.** Evidence type: benchmark protocol; oracle access is synthetic-only.

**Table 4. Synthetic coverage results.** Evidence type: fixed-seed known-truth simulation; noise rows are stress tests.

**Table 5. External testbed results.** Evidence type: external synthetic testbed; no real grant preference is observed.

**Table 6. Design recommendation matrix.** Evidence type: conditional institutional design template; not an empirical welfare ranking.

**Table 7. Claim-evidence alignment.** Evidence type: manuscript integrity audit; every main claim is bounded by its evidence source.

## References

Arnott, David; Pervan, Graham (2005). A Critical Analysis of Decision Support Systems Research. Journal of Information Technology, 20(2), 67-87. https://doi.org/10.1057/palgrave.jit.2000035

Arnott, David; Pervan, Graham (2008). Eight key issues for the decision support systems discipline. Decision Support Systems, 44(3), 657-672. https://doi.org/10.1016/j.dss.2007.09.003

Lorenz, Jan; Rauhut, Heiko; Schweitzer, Frank; Helbing, Dirk (2011). How social influence can undermine the wisdom of crowd effect. Proceedings of the National Academy of Sciences, 108(22), 9020-9025. https://doi.org/10.1073/pnas.1008636108

Manski, Charles F. (2000). Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice. Journal of Econometrics, 95(2), 415-442. https://doi.org/10.1016/s0304-4076(99)00045-7

Imbens, Guido W.; Manski, Charles F. (2004). Confidence Intervals for Partially Identified Parameters. Econometrica, 72(6), 1845-1857. https://doi.org/10.1111/j.1468-0262.2004.00555.x

Ananny, Mike; Crawford, Kate (2018). Seeing without knowing: Limitations of the transparency ideal and its application to algorithmic accountability. New Media & Society, 20(3), 973-989. https://doi.org/10.1177/1461444816676645

Bannister, Frank; Connolly, Regina (2011). The Trouble with Transparency: A Critical Review of Openness in e-Government. Policy & Internet, 3(1), 1-30. https://doi.org/10.2202/1944-2866.1076
