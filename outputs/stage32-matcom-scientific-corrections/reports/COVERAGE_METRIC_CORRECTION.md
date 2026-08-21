# Coverage Metric Correction

The legacy internal `coverage` field tested whether every truth coordinate lay between separately optimized marginal bounds. That Cartesian projection box is an outer approximation to the joint polytope. Stage 32 evaluates all original equalities, inequalities, and variable bounds.

Across positive-noise paired replications, removing elimination changes joint-set coverage by 0.117600 (MCSE 0.001519), not the legacy projection-box value 0.050289. Existing frozen Stage 26X files are retained as provenance and are not overwritten.
