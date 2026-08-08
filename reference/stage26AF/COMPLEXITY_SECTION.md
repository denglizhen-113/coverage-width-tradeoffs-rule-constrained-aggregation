# Complexity and Scalability Boundary

## Insertion location

Insert as Section 6.1 after the reproducible workflow and before Section 7.

## Manuscript text

### 6.1 Computational complexity and observed execution boundary

For a percentage-regime week with $n$ active candidates, the implemented polytope has $n$ public-support variables, one simplex equality, $n$ box bounds $0 \le p_i \le 1$, and one inequality per documented eliminated-survivor comparison. A non-final elimination record contributes $|E|(n-|E|-|W|)$ comparisons when the eliminated and withdrawn sets are disjoint; a complete final order contributes at most $n(n-1)/2$ pairwise order inequalities. The implementation first checks feasibility and then solves a minimum and maximum program for each coordinate, for $2n+1$ linear-program calls. These counts describe the implemented formulation; they are not an empirical runtime law.

For the ordinal regimes, the strict-ranking state space contains $n!$ permutations. The registered implementation enumerates exactly only when $n \le 9$ and uses fixed-seed uniform Monte Carlo above that threshold. In the empirical record, the one sampled R week uses 50,000 draws and each of 37 sampled R-plus weeks uses 10,000; 13 R weeks and 36 R-plus weeks are exact. These are the evaluated settings, not evidence for untested candidate counts.

The internal Bayesian comparator rejection-filters a fixed bank of 8,192 Dirichlet draws for each seed-parameter cell and requires at least 100 compatible draws. The 94 below-threshold replication rows show the operational consequence of low acceptance under that fixed bank; the registered design forbids adaptive enlargement. The external ordinal posterior is exact over compatible permutations in the registered small fields.

The clean-room record reports 69.01 minutes for the documented end-to-end reconstruction, including data preparation, the registered experiment archives, figures, tables, tests, and verification. Stage 26X-2 logs contain cell-level elapsed-time fields, but there is no separately instrumented timing record for an individual LP, empirical week, Stage 26X-1 cell, or isolated method phase. Accordingly, the study reports the observed full-pipeline duration and analytic state-space growth only; it does not claim efficiency or scalability beyond the evaluated configurations.

## Number-to-source trace

| Statement | Source |
|---|---|
| $n$ variables, one equality, bounded domains, eliminated-survivor and finale comparisons | `src/constraints.py::build_percentage_constraints` |
| Feasibility plus $2n$ coordinate-bound LPs | `src/constraints.py::check_feasibility` and `solve_preference_bounds` |
| $n!$ strict rankings and exact threshold $n \le 9$ | `src/ranking_identification.py::identify_week`; `scripts/05_ranking_identification.py --exact-threshold` |
| R: 13 exact, 1 sampled at 50,000; R-plus: 36 exact, 37 sampled at 10,000 | `outputs/tables/ranking_identification_summary_r.csv`; `outputs/tables/ranking_identification_summary_rplus.csv` |
| Fixed bank 8,192 and minimum 100 accepted draws | `outputs/stage26X-2/PREREGISTERED_DESIGN.md`; `scripts/26x2_baselines_ablation.py` |
| 94 below-threshold rows | `outputs/stage26X-2/raw/bayesian/*.csv`; claim audit C22 |
| Full pipeline 69.01 minutes | `outputs/stage26AA/REPRODUCIBILITY_VERIFICATION.md` |
| Cell timing exists only for Stage 26X-2 | `outputs/stage26X-2/logs/*_run_log.csv`, column `elapsed_seconds` |

`NO_TIMING_INSTRUMENTATION_EXISTS` for individual LPs, individual empirical weeks, Stage 26X-1 cells, and isolated method phases. The Stage 26X-2 cell timings are retained as logs but are not aggregated or extrapolated here, avoiding new timing results.
