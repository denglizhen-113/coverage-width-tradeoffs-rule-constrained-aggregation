# Figure Contract Update

## Historical contract

The Stage 26AA historical clean-room assertion remains 8/8 PNGs and is unchanged. Its files, hashes, and `outputs/stage26AA/REPRODUCIBILITY_VERIFICATION.md` were not modified.

## Assertion update

**Before (Stage 26AF):** Stage 26AF creates a separate presentation contract: seven numbered main figures plus one unnumbered repository artifact check, each with a vector PDF and 600 dpi PNG.

**After (Stage 26AF-1):** Stage 26AF-1 creates a separate presentation contract: six numbered main figures plus two unnumbered repository diagnostics, each with a vector PDF and 600 dpi PNG.

The six retained scientific figures and both diagnostics are byte-identical to their Stage 26AF PDF/PNG sources. Only disposition paths and the old Figures 6/7 numbering changed. No retained canvas was regenerated or altered.

## Stage 26AF-1 6+2 contract

| Contract item | Disposition | PNG | PDF | DPI | Embedded fonts | PNG SHA-256 | PDF SHA-256 | Tracked source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| main_figure_1 | Figure 1 | outputs/stage26AF-1/figures/main/Figure_01_rule_conditioned_inference_architecture.png | outputs/stage26AF-1/figures/main/Figure_01_rule_conditioned_inference_architecture.pdf | 600.0x600.0 | PASS: /BMQQDV+DejaVuSans; /EVICAO+DejaVuSans-Bold | 19bb0e5a51ffd074c6c54007325c85d6e247ab9096757c8ce662d398f63da33a | 2e3d522da9e9bf6a87d2845da10eeb9652e13a582c728a279cc957465371a43e | conceptual architecture |
| main_figure_2 | Figure 2 | outputs/stage26AF-1/figures/main/Figure_02_reproducible_comparison_workflow.png | outputs/stage26AF-1/figures/main/Figure_02_reproducible_comparison_workflow.pdf | 600.0x600.0 | PASS: /BMQQDV+DejaVuSans; /EVICAO+DejaVuSans-Bold | 647f10740d30d679219412235dbf0e47b5ed0bfc543f2a6f73d8dd68e5b77447 | 089e141c112dc2565cbe4317817f19e1968db1841f7ad83bd580e3c8423bb1fe | conceptual workflow |
| main_figure_3 | Figure 3 | outputs/stage26AF-1/figures/main/Figure_03_discretion_identifiability_frontier.png | outputs/stage26AF-1/figures/main/Figure_03_discretion_identifiability_frontier.pdf | 600.0x600.0 | PASS: /BMQQDV+DejaVuSans | 07509dcc9ce08e20e2c687caa0bb1dd07d841a392b74a481e645adfce96905db | 75c54fee325cc45e4ce5d1de21a0500498fb761afdcdc86491fb4c7fc6185685 | outputs/tables/discretion_identifiability_summary.csv |
| main_figure_4 | Figure 4 | outputs/stage26AF-1/figures/main/Figure_04_compatible_disclosure_scenarios.png | outputs/stage26AF-1/figures/main/Figure_04_compatible_disclosure_scenarios.pdf | 600.0x600.0 | PASS: /BMQQDV+DejaVuSans; /EVICAO+DejaVuSans-Bold | 837adbf53fa3a0f58310e029b1c924fe2bc49b634cf8c5f69175663b6821166b | 1ece22d79b2532b746a7c02c1aa5d7b0066787c3fffbdcf453f239c36703e074 | outputs/tables/value_of_disclosure.csv |
| main_figure_5 | Figure 5 | outputs/stage26AF-1/figures/main/Figure_05_multiseed_internal_sensitivity.png | outputs/stage26AF-1/figures/main/Figure_05_multiseed_internal_sensitivity.pdf | 600.0x600.0 | PASS: /FHXFSG+TimesNewRomanPS-BoldMT; /FHXFSG+TimesNewRomanPSMT | 1fe106a7022aa4e6f78d68b1c69e3e54cbcfcded306247b603427aebf96637fd | 8175dd7b6b6cf7a2d63adc0e994e4b8f31487898b6218f41ff7e08cefe880e6a | outputs/stage26X-1/tables/Table4_multiseed.csv |
| main_figure_6 | Figure 6 | outputs/stage26AF-1/figures/main/Figure_06_multiseed_external_sensitivity.png | outputs/stage26AF-1/figures/main/Figure_06_multiseed_external_sensitivity.pdf | 600.0x600.0 | PASS: /FHXFSG+TimesNewRomanPS-BoldMT; /FHXFSG+TimesNewRomanPSMT | 3c5558b8bdd1b07e7f48d7a9ae05b2a6c4953ff933bb936ef6b0908f1ca2e6e9 | d6acaac65f1eeda4a212cf90d9c51ccd65f514873e76778d21b4d49dc2bb8a2b | outputs/stage26X-1/tables/Table5_multiseed.csv |
| RRI_Record_predeclared_conclusions | former Figure 5: predeclared-conclusion RRI record | outputs/stage26AF-1/figures/repository_diagnostic/RRI_Record_predeclared_conclusions.png | outputs/stage26AF-1/figures/repository_diagnostic/RRI_Record_predeclared_conclusions.pdf | 600.0x600.0 | PASS: /BMQQDV+DejaVuSans; /EVICAO+DejaVuSans-Bold | c2b7efb4253c9577b5db938e163888017c94d838a9218b83fea5df3fe82a0093 | e8f79d016b868d96a68d89b59368e975c5f83ece5d863f837b4400dc0149aae8 | outputs/tables/rule_robustness_index.csv |
| Artifact_Check_evidence_completeness | former Figure 8: artifact evidence-completeness check | outputs/stage26AF-1/figures/repository_diagnostic/Artifact_Check_evidence_completeness.png | outputs/stage26AF-1/figures/repository_diagnostic/Artifact_Check_evidence_completeness.pdf | 600.0x600.0 | PASS: /BMQQDV+DejaVuSans | 2a7e30e69aaa4238b8868fbabe9b0a53f72bd081b873aacaa0e98c84707b88de | 9aa2de9b43ddb6ace1699261783d9e3cefb99518ee18d47b500ca4aa193d20a7 | outputs/tables/dss_evaluation_metrics.csv |

Result: `PASS_6_MAIN_PLUS_2_REPOSITORY_DIAGNOSTICS`; `PASS_HISTORICAL_8_OF_8_UNCHANGED`; `PASS_RETAINED_FIGURE_HASHES_UNCHANGED`.
