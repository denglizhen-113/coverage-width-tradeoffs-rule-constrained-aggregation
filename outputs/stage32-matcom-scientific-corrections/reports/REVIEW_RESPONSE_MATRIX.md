# Review Response Matrix

| review issue | resolution | evidence |
| --- | --- | --- |
| Coverage was marginal-box rather than polytope membership | FIXED | src/dss_common.py; src/synthetic_benchmark.py; tables/joint_set_coverage_*.csv |
| Sampled ordinal extrema lacked endpoint guarantees | FIXED | src/ranking_identification.py; tables/ordinal_exact_*.csv; focused enumeration-equivalence tests |
| B_k, ties, save, multiple elimination underformalized | FIXED | Manuscript Sections 3 and 5; exact MILP constraint tests |
| Complexity heading overclaimed | FIXED | Manuscript Section 5.1 reports workload and explicitly disclaims polynomial complexity |
| Possible-winner and robust-winner literature missing | FIXED | Manuscript Section 2 and references 6-10 |
| Bayesian interval level/type and semantics unclear | FIXED | Manuscript Section 6 defines 95% equal-tail rectangles and conditional-prior semantics |
| Undefined Bayesian rows not reported by region | FIXED | tables/bayesian_undefined_by_region.csv; Manuscript Table 5 |
| Key performance MCSE and paired uncertainty missing | FIXED | tables/performance_mcse.csv; paired_elimination_effect_mcse.csv |
| Preregistered wording lacked immutable registration | FIXED | Replaced by predeclared and hash-locked throughout revised package |
| Season-28 rule provenance treated as fact | FIXED | tables/rule_provenance_sensitivity.csv; Manuscript Sections 3 and 8.3 |
| Missing proxy incorrectly described as cause of skipped P week | FIXED | Manuscript Section 3 identifies missing active judge total as cause |
| Unmeasured Figure 3b/4b and governance material diluted evidence | FIXED | Removed from revised main package; four evidence-bearing figures retained |
| Public repository did not contain latest stages | FIXED | The corrected Stage 32 package is available at the versioned public release URL |
| AMS MSC/PDF/highlights requirements | NOT APPLICABLE | Report confused Mathematics of Computation with Elsevier Mathematics and Computers in Simulation |
