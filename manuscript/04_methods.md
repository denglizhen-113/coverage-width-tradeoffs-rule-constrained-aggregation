# Methods

## 4.1 Problem Setup

For contestant i in week t, let e_it denote the observed expert contribution and let the public component be hidden. The observed outcome is an elimination set together with the institutional aggregation rule. We seek the set of public-preference states consistent with that rule and outcome, not a point estimate of an unobserved ballot.

## 4.2 Percentage Aggregation and Convex Preference Regions

For P, public support p_t lies on the unit simplex. The observed elimination relation implies linear inequalities comparing the eliminated contestant's combined score with the surviving contestants' scores. Together with non-negativity and the simplex constraint, these inequalities define a convex feasible region. Linear programs minimize and maximize each coordinate of p_t, producing lower and upper feasible-support bounds. The normalized interval width is an identification-width summary, not a sampling confidence interval. No-elimination weeks retain only justified simplex restrictions; multiple-elimination weeks use conservative set restrictions; complete final rankings add their recorded pairwise order information.

## 4.3 Ranking Aggregation and Feasible Ordinal Rankings

For R, the hidden public object is a permutation of fan ranks. A candidate ranking is feasible when its combination with observed judge ranks is consistent with the observed elimination under the direct rule. Exact enumeration is used where possible and fixed-seed Monte Carlo sampling otherwise. The resulting feasible ranking set yields contestant-level rank support, entropy, and normalized rank-width summaries. These are ordinal quantities and are never converted into cardinal support shares.

## 4.4 Judge-Save Intervention as Weak Identification

For R_plus, the direct criterion is weakened: the eliminated contestant must be contained in a tie-inclusive bottom set prior to a judge save. Every direct-feasible ranking is therefore feasible under the weak condition. We summarize the corresponding loss of identification with the within-week ratio of weak-set to direct-set size, retaining the recorded tie policy. This comparison is made within the same week rather than from cross-regime averages.

## 4.5 Dynamic Public-Appeal Proxy

For descriptive extensions, P uses the midpoint of its coordinate-wise feasible interval, while R and R_plus use a normalized feasible mean fan rank. Each proxy carries an uncertainty measure and a type label. Exponential and uncertainty-weighted smoothing create dynamic inferred public-appeal trajectories. These trajectories are not public ballots; analyses either include regime indicators or remain mechanism-specific.

## 4.6 Validation and Counterfactual Design

Prediction is a validation exercise. Historical public, dynamic, uncertainty, and expert features are lagged by one contestant observation; current-week expert scores occur only in explicitly labeled same-week baselines. Counterfactual analyses propagate interval or feasible-ranking scenarios and condition on observed active trajectories. They are scenario analyses, not causal reconstructions of an alternative season.
