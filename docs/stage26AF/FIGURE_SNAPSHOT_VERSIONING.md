# Figure Snapshot Contract Versioning

## Historical contract retained

The Stage 26AA clean-room record remains an immutable historical assertion: its eight reference PNGs matched the Stage 21/22 and Stage 26X-1 regenerated outputs pixel-for-pixel. Neither those files nor `outputs/stage26AA/REPRODUCIBILITY_VERIFICATION.md` was modified. The historical contract applies only to the old eight-PNG manuscript presentation and remains evidence for that stage.

## Stage 26AF contract added

Stage 26AF creates a separate presentation contract: seven numbered main figures plus one unnumbered repository artifact check, each with a vector PDF and 600 dpi PNG. It validates file hashes, numbering, source-table identity, PNG dpi, and PDF font embedding. It does not assert pixel equality with the historical figures because titles, layout, resolution, and scope changed deliberately.

## Coexistence rule

The contracts are parallel and stage-scoped. A historical clean-room failure may not be repaired by reverting Stage 26AF figures, and a Stage 26AF failure may not be hidden by overwriting historical reference files. Exact paths, hashes, and scopes are recorded in `figure_snapshot_manifest.csv`.

| Contract | Figure | Path | SHA-256 | Scope |
| --- | --- | --- | --- | --- |
| historical_cleanroom_8_png | historical_figure_1 | outputs/figures/dss_conceptual_framework.png | 776f9f516289769a2f2a84f86c30aa6d8a2bb98521418a1b577ded5e79380702 | Stage 26AA clean-room 8/8 pixel contract; immutable historical evidence |
| historical_cleanroom_8_png | historical_figure_2 | outputs/figures/decision_support_workflow.png | 9d567b010ab84dd6612124523755393f1439fb6528c46699031ba6e2517b0069 | Stage 26AA clean-room 8/8 pixel contract; immutable historical evidence |
| historical_cleanroom_8_png | historical_figure_3 | outputs/figures/discretion_identifiability_frontier.png | fdae348706360722afe3fc8724ded7bfc31d5b4374d8363d6ed27b4e3ca884c9 | Stage 26AA clean-room 8/8 pixel contract; immutable historical evidence |
| historical_cleanroom_8_png | historical_figure_4 | outputs/figures/disclosure_uncertainty_curve.png | 20b17808b9306e1750e6e7dfbe691b72e5390741c2b3a20d6ef59e7e209b878e | Stage 26AA clean-room 8/8 pixel contract; immutable historical evidence |
| historical_cleanroom_8_png | historical_figure_5 | outputs/figures/rule_robustness_heatmap.png | 83d6b0264277ba65ad9e7e6954cc60abc35b09f6ac846db6086e4b4d6b4858f1 | Stage 26AA clean-room 8/8 pixel contract; immutable historical evidence |
| historical_cleanroom_8_png | historical_figure_6 | outputs/stage26X-1/Figure_06_multiseed_internal_sensitivity.png | f813b6d088b19b29429ed9d3569c542a508b656d6166f5ebe756aa11cf705edd | Stage 26AA clean-room 8/8 pixel contract; immutable historical evidence |
| historical_cleanroom_8_png | historical_figure_7 | outputs/stage26X-1/Figure_07_multiseed_external_sensitivity.png | 4b61a557d9739992a892eba14c2dce8da0871cc7b5cc01ff4ab3b3045170e7d8 | Stage 26AA clean-room 8/8 pixel contract; immutable historical evidence |
| historical_cleanroom_8_png | historical_figure_8 | outputs/figures/dss_evaluation_radar.png | c25276696b4b72e5a8ecaf6c749decd6f48741d254e9c9a06bf0dd55b2c536a2 | Stage 26AA clean-room 8/8 pixel contract; immutable historical evidence |
| stage26AF_vector_600dpi | 1 | outputs/stage26AF/figures/main/Figure_01_rule_conditioned_inference_architecture.png | 19bb0e5a51ffd074c6c54007325c85d6e247ab9096757c8ce662d398f63da33a | Stage 26AF presentation contract; PDF companion separately hashed in delivery manifest |
| stage26AF_vector_600dpi | 2 | outputs/stage26AF/figures/main/Figure_02_reproducible_comparison_workflow.png | 647f10740d30d679219412235dbf0e47b5ed0bfc543f2a6f73d8dd68e5b77447 | Stage 26AF presentation contract; PDF companion separately hashed in delivery manifest |
| stage26AF_vector_600dpi | 3 | outputs/stage26AF/figures/main/Figure_03_discretion_identifiability_frontier.png | 07509dcc9ce08e20e2c687caa0bb1dd07d841a392b74a481e645adfce96905db | Stage 26AF presentation contract; PDF companion separately hashed in delivery manifest |
| stage26AF_vector_600dpi | 4 | outputs/stage26AF/figures/main/Figure_04_compatible_disclosure_scenarios.png | 837adbf53fa3a0f58310e029b1c924fe2bc49b634cf8c5f69175663b6821166b | Stage 26AF presentation contract; PDF companion separately hashed in delivery manifest |
| stage26AF_vector_600dpi | 5 | outputs/stage26AF/figures/main/Figure_05_rule_robustness_index.png | c2b7efb4253c9577b5db938e163888017c94d838a9218b83fea5df3fe82a0093 | Stage 26AF presentation contract; PDF companion separately hashed in delivery manifest |
| stage26AF_vector_600dpi | 6 | outputs/stage26AF/figures/main/Figure_06_multiseed_internal_sensitivity.png | 1fe106a7022aa4e6f78d68b1c69e3e54cbcfcded306247b603427aebf96637fd | Stage 26AF presentation contract; PDF companion separately hashed in delivery manifest |
| stage26AF_vector_600dpi | 7 | outputs/stage26AF/figures/main/Figure_07_multiseed_external_sensitivity.png | 3c5558b8bdd1b07e7f48d7a9ae05b2a6c4953ff933bb936ef6b0908f1ca2e6e9 | Stage 26AF presentation contract; PDF companion separately hashed in delivery manifest |
| stage26AF_vector_600dpi | repository artifact check (former Figure 8) | outputs/stage26AF/figures/repository_diagnostic/Artifact_Check_evidence_completeness.png | 2a7e30e69aaa4238b8868fbabe9b0a53f72bd081b873aacaa0e98c84707b88de | Stage 26AF presentation contract; PDF companion separately hashed in delivery manifest |
