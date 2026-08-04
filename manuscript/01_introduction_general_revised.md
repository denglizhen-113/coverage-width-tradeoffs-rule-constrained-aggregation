# Introduction: General Submission Line

Expert-crowd aggregation systems combine professional judgments with participation from members, users, audiences, or other publics. Their rules can mix expert scores, rankings, eliminations, and interventions, creating hybrid decisions in which visible expert assessments coexist with partly hidden collective input.

This information structure creates an identification problem when public preferences are hidden and only coarse outcome feedback is released. An elimination constrains the latent states compatible with a documented rule, but usually does not identify one state. Point estimation is consequently too strong without additional information; the appropriate object is a feasible preference set.

Research on prediction, retrospective explanation, and ranking analytics can describe outcome patterns or validate engineered features. Those tasks do not by themselves establish what is identified from elimination-only outcomes. In particular, a good predictive score cannot turn hidden input into observed data, and a ranking explanation can obscure the difference between cardinal and ordinal latent objects.

We develop a rule-aware partial-identification framework for cardinal and ordinal aggregation rules. Percentage aggregation induces linear inequalities on a simplex and coordinate-wise linear-program bounds. Rank aggregation induces feasible ordinal public rankings. A judge-save intervention weakens a direct elimination implication to tie-inclusive bottom-set membership, changing the compatible set by construction.

The empirical testbed is a longitudinal competition setting with documented rule changes, observed eliminations, and three aggregation regimes. Its role is methodological: it provides repeated instances of coarse feedback under changing rules. It is not the substantive center of the paper and is not used to make claims about a public-service system.

The paper contributes: (1) a rule-aware partial-identification framework for hidden public preferences; (2) a comparison of cardinal and ordinal aggregation regimes; (3) a judge-save analysis of mechanism-induced identifiability loss; and (4) validation and scenario-analysis extensions that carry uncertainty forward without converting it into point recovery.

The remainder of the paper documents the data and institutional rules, defines the identification sets, reports the core evidence, then presents secondary validation and scenario analyses before discussing design implications and limits.
