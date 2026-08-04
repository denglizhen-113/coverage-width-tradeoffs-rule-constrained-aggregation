# Rule Robustness Index

RRI is the share of applicable, predeclared configurations that support a conclusion predicate. It classifies conclusions as robust at 0.95 or above, assumption-sensitive from 0.60 to below 0.95, and non-identifiable below 0.60. The index avoids pooling cardinal and ordinal widths.

| conclusion_id | conclusion | configuration_family | applicable_configurations | supporting_configurations | rule_robustness_index | classification | evidence_type | boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | Correct rule-aware P constraints are no less informative than the simplex-only rule-agnostic representation. | rule-aware versus rule-agnostic cardinal P | 1 | 1 | 1.0 | robust | empirical P summary plus analytical simplex baseline | This compares nested P constraints only; it does not compare P width to ordinal width. |
| C2 | The weak judge-save feasible ranking set contains the direct-feasible ranking set within evaluated R_plus weeks. | strict/relaxed tie handling and judge-save interpretations | 4 | 4 | 1.0 | robust | empirical R_plus tie-policy sensitivity | Containment is a within-week ordinal relation, not a cross-regime comparison. |
| C3 | Ordinal feasible-ranking uncertainty remains broad across documented tie policies. | strict/relaxed tie handling | 4 | 4 | 1.0 | robust | empirical R_plus tie-policy sensitivity | The 0.70 threshold is a predeclared descriptive predicate, not a welfare cutoff. |
| C4 | Cardinal and ordinal uncertainty summaries require a common functional before direct numerical comparison. | cardinal versus ordinal representation | 1 | 1 | 1.0 | robust | formal representation boundary | This is a comparability condition, not a numerical finding about which regime is more uncertain. |

A high RRI does not prove institutional optimality. It indicates that a stated conclusion persists across the evaluated configuration family.
