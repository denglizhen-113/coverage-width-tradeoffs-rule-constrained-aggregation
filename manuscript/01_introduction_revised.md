# Introduction

Expert-crowd decision systems combine professional assessments with public, member, user, or stakeholder input. They arise wherever institutions seek both specialized evaluation and broader participation, yet the public component is often hidden after an aggregate decision is released.

This information structure creates a basic inferential constraint. When the observable feedback is only an elimination or another coarse selection, many hidden-preference states can be compatible with the same outcome. The appropriate estimand is therefore a feasible preference set conditional on an aggregation rule, rather than a point prediction of an unobserved public score.

Existing empirical work often emphasizes point prediction, ranking prediction, or retrospective explanation. Those tasks can be useful, but they do not establish what is identified from coarse outcomes when the public signal is absent. In particular, they can obscure the fact that different aggregation rules constrain different latent objects.

We develop a rule-aware partial-identification framework for percentage and ranking aggregation. Percentage rules yield linear inequality systems over a simplex and coordinate-wise linear-program bounds. Ranking rules yield feasible ordinal public rankings. A judge-save rule weakens the direct-elimination implication by replacing it with a tie-inclusive bottom-set condition.

The empirical testbed is a longitudinal competition dataset with repeated eliminations, recorded expert scores, documented rule changes, and multiple aggregation regimes. Its value is methodological: it supplies a transparent setting in which cardinal, ordinal, and weak-intervention identification statements can be compared. It is not itself a public-service evaluation.

The paper contributes: (1) a rule-aware partial-identification framework for hidden public preferences; (2) a comparison of cardinal and ordinal aggregation mechanisms; (3) a within-week judge-save analysis that quantifies identification loss; and (4) an uncertainty-aware validation and mechanism-design extension that remains secondary to the identified-set results.

The remainder of the paper describes the data and rules, develops the identification framework, reports the core findings, then presents validation and scenario analyses with explicit limitations.
