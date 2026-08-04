# Supplementary Code README

Run from the project root after installing `requirements.txt` dependencies:

```text
python scripts/21_dss_full_attack.py --synthetic-replications 250 --disclosure-cases 100 --seed 20260716
python scripts/22_dss_submission_candidate.py --external-replications 120 --seed 20260716 --tests-passed <verified_count>
python scripts/23_dss_submission_integrity.py
python -m pytest tests -q
```

Stage 23 itself performs an isolated copy-based reproduction of Stages 21 and 22 by default. It does not overwrite their project-root outputs. The raw file remains under `data/raw/`; its checksum and access conditions must be reviewed before any public release. Artifact demonstration inputs are explicitly synthetic and live in `outputs/artifact_demo/demo_input_config.json`.
