# Data and Institutional Rules

## Empirical testbed

The processed longitudinal panel contains 4,199 contestant-week records before identification-specific availability restrictions. The unified identification feature file contains 2,777 active contestant-week records, of which 2,766 have a typed public-appeal proxy. The remaining 11 observations correspond to a logged P-regime constraint skip and are not imputed.

| Regime | Seasons | Season-weeks | Active contestant-weeks |
| --- | ---: | ---: | ---: |
| P | 25 | 247 | 1997 |
| R | 2 | 14 | 78 |
| R_plus | 7 | 73 | 702 |

## Institutional rules

In P, the combined decision uses normalized expert performance and a hidden cardinal public-support component. In R, expert and public ranks are combined and the lowest combined standing is eliminated. In R_plus, a judge-save intervention means that the observed eliminated contestant need only belong to a tie-inclusive bottom set before the save decision. The encoded rules also distinguish no-elimination weeks, multiple eliminations, withdrawals, and final rounds; these conditions are recorded in the preprocessing and constraint reports.

The raw public component is not observed. Thus P, R, and R_plus are not three interchangeable measurements of one latent vote share. They are three information environments with different feasible objects.

Traceable sources: `data/processed/panel_long.csv`, `data/processed/identification_features_long.csv`, and `outputs/tables/constraint_summary.csv`.
