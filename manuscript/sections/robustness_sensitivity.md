# Robustness and Sensitivity

| sensitivity_dimension | scenario_or_comparison | relative_change_or_gap | evidence_type | classification | interpretation_boundary |
| --- | --- | --- | --- | --- | --- |
| missingness | synthetic removal of outcome information | 1.0 | synthetic scenario | highly sensitive | Removing constraints widens a feasible set by construction; this is an information boundary. |
| tie handling | average/min/dense/competition rank policies | 0.027396664604045676 | empirical R_plus tie-policy sensitivity | stable | Ordinal result only; no cardinal comparison is made. |
| alternative rule interpretation | direct versus weak judge-save implication | -0.009235207097690101 | synthetic stress test | moderately sensitive | Noise/misspecification is not an empirical intervention estimate. |
| alternative proxy construction | proxy changes with fixed identification constraints | 0.0 | analytical boundary | stable | The dynamic proxy is downstream and does not alter the feasible-set constraints. |
| ordinal/cardinal mapping | attempted cross-regime width mapping |  | formal comparability boundary | highly sensitive | No common functional is defined; raw widths are not compared. |
| active contestant trajectory selection | P width split by active-field size | 0.18465115616652084 | empirical descriptive diagnostic | moderately sensitive | Descriptive split only; active trajectories are historically selected. |
| judge-save assumptions | tie-policy range in weak/direct ordinal model | 0.027396664604045676 | empirical R_plus tie-policy sensitivity | stable | Containment remains separately audited. |
| disclosure granularity | top-k versus full synthetic disclosure | 1.0 | synthetic disclosure scenario | highly sensitive | Information gain is modeled, not historically observed. |
| noise in observed outcomes | clean versus noisy synthetic observed elimination | 0.052000000000000046 | synthetic stress test | moderately sensitive | Tests logical calibration under intentionally inconsistent coarse outcomes. |

Each row is labeled by evidence type. Synthetic stress tests diagnose behavior under known assumptions; empirical rows describe existing rule/tie sensitivity; formal boundaries are not converted to artificial numerical comparisons.
