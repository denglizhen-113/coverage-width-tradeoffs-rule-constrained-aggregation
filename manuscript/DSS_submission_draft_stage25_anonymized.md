# Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences

## Abstract

Institutional designers must sometimes choose aggregation, discretion, and disclosure rules after observing only coarse outcomes while public preferences remain hidden. We develop a model-driven decision-support framework that represents this information gap through rule-assumption-conditioned feasible sets rather than a point estimate of hidden votes. Percentage rules yield cardinal feasible intervals; ranking and judge-save rules yield ordinal feasible-ranking sets under explicit tie and discretion assumptions. The decision cockpit translates feasible-set width, rule robustness, and disclosure scenarios into conditional design recommendations and accountability warnings. Fixed-seed synthetic calibration evaluates coverage and false-certainty diagnostics when ground truth is available only inside the simulator. A structurally different external synthetic testbed examines portability, while the empirical application illustrates feasible sets consistent with observed outcomes. The artifact-level evaluation checks decision relevance, transparency, traceability, and reproducibility; it is not a deployment, user-validation, or organizational-impact study. The contribution is uncertainty-aware decision support for institutional aggregation design under incomplete observability.

**Keywords:** Decision support systems; partial identification; preference aggregation; expert discretion; institutional disclosure; rule robustness.

## 1. Introduction

Institutions that combine expert judgement with public input still need to decide how much discretion to allow, what aggregation rule to retain, and what information to disclose after only coarse outcomes are recorded. The decision problem is therefore not to impute a public vote. It is to determine which latent preference states remain feasible under documented rules, then use that uncertainty to compare institutional design alternatives. Figure 1 presents this DSS problem; Figure 2 maps the workflow from observed outcomes to an accountable design recommendation.

This study makes four linked contributions. First, it supplies a **DSS foundation**: rule-aware partial identification produces a feasible set conditioned on observed outcomes and stated institutional rules. Second, it supplies **DSS functionality**: a mechanism-evaluation framework compares aggregation rules, expert-discretion assumptions, tie handling, and disclosure regimes. Third, it supplies an **implementation artifact**: a JSON-configurable decision cockpit translates uncertainty into a recommendation, warning, and audit trail. Fourth, it supplies **evaluation evidence**: synthetic calibration, an external synthetic testbed, baseline comparison, robustness analysis, and artifact-level checks. These contributions support enhanced decision making without representing hidden preferences as observed.

**Decision-support implication.** Institutional designers can compare information consequences and governance tradeoffs without converting a hidden preference into a false point estimate.

## 2. Decision-Support Problem and Institutional Setting

The supported user is an institutional organizer or platform governance analyst. The supported decisions are whether to retain an aggregation mechanism, narrow or document expert discretion, pre-specify a tie protocol, or disclose additional aggregate information. Inputs are observed outcomes, a rule type, a judge-save assumption, a tie-handling assumption, a disclosure regime, and a stated decision objective. Outputs are a rule-assumption-conditioned feasible-set summary, uncertainty class, robustness label, disclosure recommendation, and accountability warning. Table 1 lists decision alternatives and criteria.

The artifact does not choose an institution's objective, perform legal or privacy review, measure stakeholder trust, or replace implementation authority. **Decision-support implication.** Its value is disciplined uncertainty-to-recommendation translation, not automated institutional choice.

## 3. Related Work

Decision-support research concerns models and artifacts that improve decision making through foundations, functionality, interfaces, implementation, and evaluation (Arnott & Pervan, 2005, 2008). Expert-crowd settings can be shaped by social influence and institutional aggregation, so an observed outcome is not equivalent to an observed public preference (Lorenz et al., 2011). Partial-identification methods retain the set of latent states compatible with incomplete observations and make the decision consequences of ambiguity explicit (Manski, 2000; Imbens & Manski, 2004). Transparency and accountability scholarship cautions that disclosure is not synonymous with accountability, motivating the study's explicit boundary between information scenarios and measured stakeholder outcomes (Ananny & Crawford, 2018; Bannister & Connolly, 2011).

The gap is a decision-support workflow for institutional designers who must compare aggregation mechanisms when public preferences are hidden, expert intervention is rule-dependent, and disclosure policy changes what can be identified.

## 4. Rule-Aware Partial-Identification Framework

For a percentage week, let $p$ denote the latent public-support vector in the unit simplex and let $q$ denote the observed normalized expert component. A documented elimination adds affine comparisons between an eliminated candidate and surviving candidates. The rule-aware feasible set is the intersection of the simplex with those valid outcome constraints; coordinate-wise linear programs produce sharp conditional bounds. No-elimination and withdrawal weeks add no comparative outcome constraint unless documented information supports one. Multiple eliminations and final-order information are encoded only when the corresponding rule input is documented.

For ranking and judge-save regimes, the latent object is a strict public ranking. A feasible ranking is consistent with expert ranks, the named tie policy, and either a direct or weak bottom-set implication. Cardinal shares and ordinal rank supports are not pooled into a common scale without a justified mapping. Table 2 records the assumptions and Supplementary Appendix S1 gives the propositions and proof sketches.

**Decision-support implication.** A designer can see whether changing a rule changes the identified object before comparing alternatives.

## 5. DSS Artifact and Workflow

The model-driven DSS artifact records the rule inputs and decision objective, computes the compatible-state uncertainty, retrieves a predeclared robustness label, and returns a disclosure recommendation, design warning, and accountability implication. The demonstration uses illustrative synthetic configuration inputs; it is neither an empirical replay nor an institutionally operating implementation. Its input/output contract and decision trace are auditable in the artifact materials.

**Decision-support implication.** The cockpit makes rule assumptions and residual uncertainty visible at the point of institutional design choice.

## 6. Mechanism Evaluation Modules

### 6.1 Discretion-Identifiability Frontier

Figure 3 is a deterministic synthetic rule scenario that relaxes a direct bottom-set implication. The empirical R-plus record supports only the documented direct-versus-weak comparison. The displayed continuum is not a historical scale of expert intervention.

**Decision-support implication.** Expert discretion can be evaluated as a conditional governance tradeoff between flexibility and later identifiability.

### 6.2 Value of Institutional Disclosure

Figure 4 compares truthful, compatible synthetic disclosure additions. Additional disclosure weakly shrinks a feasible set only when it adds compatible constraints to the same state space. Privacy, cost, interpretability, and accountability quantities in this module are scenario descriptors, not measured stakeholder outcomes.

**Decision-support implication.** The artifact can compare the smallest modeled disclosure option that reduces uncertainty while retaining an explicit governance warning.

### 6.3 Rule Robustness Index

Figure 5 reports the share of applicable predeclared configurations supporting each conclusion. The Rule Robustness Index (RRI) lies in [0,1] and summarizes conditional conclusion stability; it is not an institutional-welfare optimum.

**Decision-support implication.** A recommendation can distinguish robust conclusion predicates from rule-sensitive ones.

## 7. Synthetic Benchmark and Baselines

Table 3 defines the information available to each baseline, and Table 4 reports fixed-seed known-truth synthetic results. Under correctly specified, no-noise simulated outcomes, rule-aware feasible-set coverage is 1.000. Under the explicitly labeled outcome-noise stress test, coverage is 0.948. The rule-aware mean normalized width is 0.845 versus 1.000 for the simplex-only rule-agnostic representation; point or prediction proxies have a synthetic false-certainty rate of 1.000. These are calibration diagnostics under synthetic ground truth, not empirical error rates. Figure 6 displays coverage and false-certainty diagnostics.

**Decision-support implication.** Rule constraints can improve calibration under stated simulation assumptions while preserving uncertainty instead of presenting a decisive-looking proxy.

## 8. External Synthetic Testbed

The external synthetic community-grant simulator uses seven candidates, four elimination rounds, two synthetic intervention rounds, pairwise disclosure, and dense-rank primary tie handling. The correct rule-aware representation has synthetic coverage 1.000 and mean normalized feasible-rank width 0.960; treating intervention as direct elimination yields a synthetic false-certainty diagnostic of 0.958. Figure 7 and Table 5 provide structural-portability evidence, not universal empirical validation.

**Decision-support implication.** Designers can test whether a mechanism-evaluation workflow remains coherent under a structurally different institutional rule before generalizing its use.

## 9. Empirical Application

The longitudinal application supplies repeated documented regimes with hidden public truth. Percentage weeks have mean normalized coordinate-wise feasible width 0.843; R-plus weeks have mechanism-specific normalized rank width 0.924. These quantities are not on a common latent scale. They illustrate rule-assumption-conditioned feasible sets consistent with observed outcomes, not recovered public preferences.

**Decision-support implication.** Users should interpret intervals and rank supports as limits of inference from coarse records.

## 10. Artifact-Level DSS Evaluation

Figure 8 and the evaluation matrix examine decision relevance, uncertainty transparency, recommendation interpretability, robustness awareness, disclosure-cost awareness, rule-design usefulness, reproducibility, and implementation feasibility. The scenario-based future user evaluation remains a protocol with no participants or human-subject results.

**Decision-support implication.** The artifact demonstrates inspectable decision-support properties and a validation path, not measured usability, adoption, or organizational performance.

## 11. Decision-Support Recommendations

Table 6 maps stated objectives to conditional rule and disclosure designs, and Table 7 maps each main claim to its evidence boundary. The matrix does not select an optimal policy. It documents which recommendation follows under a stated objective, rule, and disclosure condition, and which tradeoffs remain outside the model.

**Decision-support implication.** Recommendation quality depends on documented objectives, rule fidelity, privacy constraints, and reporting costs that must be assessed locally.

## 12. Discussion and Limitations

The framework recasts hidden-preference analysis as institutional decision analytics: the observation rule determines both the compatible state space and the scope of a defensible recommendation. The paper contributes a DSS foundation, functionality, an operational artifact, and layered evaluation evidence, while retaining strict distinctions among formal propositions, synthetic calibration, external synthetic testing, empirical illustration, artifact-level evaluation, and a future user-evaluation protocol.

The method does not recover exact hidden votes. The empirical application is an institutional testbed rather than universal proof. Synthetic benchmarks validate logical calibration under their simulators, not real-world truth. Artifact-level evaluation is not organizational deployment or impact. Rule quality, tie policy, disclosure compatibility, privacy, and reporting costs remain substantive governance assumptions.

**Decision-support implication.** Every recommendation should travel with its rule, tie, disclosure, objective, and evidence-type assumptions.

## 13. Conclusion

Rule-aware partial identification provides uncertainty-aware decision support for expert-crowd aggregation when the public component is hidden. The resulting feasible sets, mechanism comparisons, decision cockpit, and reproducible evidence package help institutional designers reason about aggregation, discretion, and disclosure without claiming knowledge the record does not contain.

**Decision-support implication.** The package is a final-author-review candidate, not a claim of real deployment or verified organizational impact.

## Figure Captions

**Figure 1. DSS conceptual framework.** Evidence type: theoretical decision-support framework. Documented rules and coarse outcomes lead to rule-assumption-conditioned feasible sets, not observed public votes.

**Figure 2. Decision-support workflow.** Evidence type: implementation artifact workflow. It separates supported configuration and recommendation tasks from governance responsibilities and is not a deployed or user-validated workflow.

**Figure 3. Discretion-identifiability frontier.** Evidence type: deterministic synthetic rule scenario. It is not a historical scale of intervention strength.

**Figure 4. Synthetic disclosure uncertainty curve.** Evidence type: synthetic compatible-disclosure scenario. Scenario descriptors are not measured trust, privacy, or cost outcomes.

**Figure 5. Rule Robustness Index.** Evidence type: formal/empirical configuration summary. RRI is bounded conditional stability, not institutional optimality.

**Figure 6. Synthetic benchmark coverage.** Evidence type: fixed-seed known-truth synthetic calibration. Coverage applies only to latent preferences generated inside the simulator.

**Figure 7. External synthetic testbed comparison.** Evidence type: external synthetic community-grant setting. It demonstrates structural portability under stated conditions, not universal empirical validity.

**Figure 8. Artifact evidence-completeness checks.** Evidence type: artifact-level evaluation. It is not a user-effectiveness, adoption, or organizational-impact score.

## Table Notes

**Table 1. Decision alternatives and criteria.** Evidence type: design template; trust, privacy, and cost require local evidence.

**Table 2. Assumption inventory.** Evidence type: formal model audit; assumptions define the conditional identified object.

**Table 3. Baseline definitions.** Evidence type: benchmark protocol; oracle access is synthetic-only.

**Table 4. Synthetic coverage results.** Evidence type: fixed-seed synthetic benchmark; noise rows are stress tests.

**Table 5. External testbed results.** Evidence type: external synthetic testbed; no real grant preference is observed.

**Table 6. Design recommendation matrix.** Evidence type: conditional design template; not an empirical welfare ranking.

**Table 7. Claim-evidence alignment.** Evidence type: manuscript integrity audit; every main claim is bounded by evidence type.

## References

Arnott, David; Pervan, Graham (2005). A Critical Analysis of Decision Support Systems Research. Journal of Information Technology, 20(2), 67-87. https://doi.org/10.1057/palgrave.jit.2000035

Arnott, David; Pervan, Graham (2008). Eight key issues for the decision support systems discipline. Decision Support Systems, 44(3), 657-672. https://doi.org/10.1016/j.dss.2007.09.003

Lorenz, Jan; Rauhut, Heiko; Schweitzer, Frank; Helbing, Dirk (2011). How social influence can undermine the wisdom of crowd effect. Proceedings of the National Academy of Sciences, 108(22), 9020-9025. https://doi.org/10.1073/pnas.1008636108

Manski, Charles F. (2000). Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice. Journal of Econometrics, 95(2), 415-442. https://doi.org/10.1016/s0304-4076(99)00045-7

Imbens, Guido W.; Manski, Charles F. (2004). Confidence Intervals for Partially Identified Parameters. Econometrica, 72(6), 1845-1857. https://doi.org/10.1111/j.1468-0262.2004.00555.x

Ananny, Mike; Crawford, Kate (2018). Seeing without knowing: Limitations of the transparency ideal and its application to algorithmic accountability. New Media & Society, 20(3), 973-989. https://doi.org/10.1177/1461444816676645

Bannister, Frank; Connolly, Regina (2011). The Trouble with Transparency: A Critical Review of Openness in e-Government. Policy & Internet, 3(1), 1-30. https://doi.org/10.2202/1944-2866.1076
