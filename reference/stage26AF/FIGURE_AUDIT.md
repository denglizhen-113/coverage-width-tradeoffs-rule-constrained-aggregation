# Stage 26AF Figure Audit

## Verdict

Figures 1 and 2 materially conflict with the current manuscript positioning because their rendered titles and layers retain Decision Support language. Historical Figure 4 overlays a computed width and an unmeasured design descriptor on one axis; Stage 26AF separates them into two panels without changing either series. Figures 5 and 8 are not plotting failures, but both are constant at 1.0 and therefore carry `NO_INFORMATION_BEYOND_TABLE`. Figure 8 is an engineering completeness check and is removed from the main manuscript. Figure 5 remains in the Stage 26AF manuscript pending the author's decision.

## Eight-figure inventory before Stage 26AF

| Figure | Original title | Values carried | Tracked source | Current format | Pixels | DPI | Decision Support framing | Information assessment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Rule-Aware Decision Support under Partially Observed Public Preferences | Conceptual; no numeric values | None (conceptual architecture) | PNG | 2375x1551 | 250x250 | YES | CONCEPTUAL_INFORMATION |
| 2 | Decision-support workflow for aggregation-mechanism evaluation | Conceptual; no numeric values | None (conceptual workflow) | PNG | 2181x666 | 250x250 | YES | CONCEPTUAL_INFORMATION |
| 3 | Synthetic discretion-identifiability frontier | Modeled discretion strength, normalized rank width, flexibility index | outputs/tables/discretion_identifiability_summary.csv | PNG | 1844x1230 | 250x250 | NO | GRAPHICAL_PATTERN_AND_INTERVAL_INFORMATION |
| 4 | Synthetic value-of-disclosure scenarios | Mean feasible-set width and predeclared accountability design score | outputs/tables/value_of_disclosure.csv | PNG | 2329x1339 | 250x250 | NO | GRAPHICAL_PATTERN_WITH_INCOMMENSURATE_OVERLAY_RISK |
| 5 | Rule Robustness Index by predeclared conclusion | RRI = supporting/applicable configurations for C1-C4 | outputs/tables/rule_robustness_index.csv | PNG | 2049x879 | 250x250 | NO | NO_INFORMATION_BEYOND_TABLE |
| 6 | Internal synthetic sensitivity across 20 seeds | Coverage and normalized width with seed-level 2.5%-97.5% intervals | outputs/stage26X-1/tables/Table4_multiseed.csv | PNG | 3491x2053 | 300x300 | NO | GRAPHICAL_PATTERN_AND_INTERVAL_INFORMATION |
| 7 | External synthetic sensitivity across 20 seeds | Coverage and normalized feasible-rank width with seed-level 2.5%-97.5% intervals | outputs/stage26X-1/tables/Table5_multiseed.csv | PNG | 3129x1524 | 300x300 | NO | GRAPHICAL_PATTERN_AND_INTERVAL_INFORMATION |
| 8 | Artifact Evidence-Completeness Checks | Artifact evidence-completeness for eight engineering criteria | outputs/tables/dss_evaluation_metrics.csv | PNG | 2075x1984 | 300x300 | YES | NO_INFORMATION_BEYOND_TABLE |

## Figure 5 diagnosis

Figure 5 reports the Rule Robustness Index, defined as supporting configurations divided by applicable configurations for predeclared conclusions C1-C4. The all-1.0 display is correct: every row in `outputs/tables/rule_robustness_index.csv` has equal supporting and applicable counts. It is not a plotting-logic error.

| Conclusion | Applicable | Supporting | RRI | Table row |
| --- | --- | --- | --- | --- |
| C1 | 1 | 1 | 1.000 | 2 |
| C2 | 4 | 4 | 1.000 | 3 |
| C3 | 4 | 4 | 1.000 | 4 |
| C4 | 1 | 1 | 1.000 | 5 |

The four displayed values correspond to all four data rows in the CSV (physical CSV lines 2-5), not a single scientific effect. They do not currently correspond to a row of any main-manuscript Table 1-9; the RRI source is a standalone diagnostic table. The figure adds no pattern, interval, contrast, or ordering beyond those four cells.

## Figure 5 alternatives

| Option | Treatment | Tradeoff |
|---|---|---|
| Retain | Keep the high-resolution heatmap in the main text. | Preserves continuity but spends a figure on four constant values and risks making a configuration check look like a result. |
| Convert to a table row | Add `4/4 predeclared conclusions have RRI 1.000` as a new compact Table 9 row (or equivalent prose) and remove the figure. | Most compact faithful representation; loses no quantitative information. This is the audit recommendation. |
| Move out of main text | Retain the CSV and vector diagnostic in the repository/supplement only. | Keeps audit transparency while freeing main-text space; readers must consult the supplement for row detail. |

`AUTHOR_DECISION_REQUIRED`: Stage 26AF does not remove Figure 5. The author should choose between conversion to a compact table/prose statement and repository/supplement placement before the next manuscript assembly.
