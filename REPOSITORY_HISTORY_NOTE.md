# Repository History Note

Version control was first enabled during Stage 26AA on 2026-08-01. The empty
`.git` directory present before this stage did not contain a Git repository or
recoverable commits.

The project history for Stages 1 through 26Z therefore cannot be reconstructed
as a sequence of commits. The Stage output directories, execution logs, and
hash manifests are the only retained evidence of earlier changes. This initial
commit is a truthful snapshot of the files present when version control was
enabled; it is not a reconstruction of earlier development history.

The principal frozen-artifact records are:

- `outputs/tables/frozen_outputs_hashes.csv`
- `outputs/tables/hash_manifest_stage24.csv`
- `outputs/tables/stage24_frozen_hash_check.csv`
- `outputs/tables/stage24_submission_package_manifest.csv`
- `submission_package_stage25/11_reproducibility/frozen_artifact_hash_manifest_stage25.csv`
- `submission_package_stage25/13_audit_tables/stage25_submission_file_manifest.csv`

Known exceptions to those records are documented in
`KNOWN_FROZEN_EXCEPTIONS.md`. No commit was backdated and no missing author,
timestamp, or intermediate history was invented.

