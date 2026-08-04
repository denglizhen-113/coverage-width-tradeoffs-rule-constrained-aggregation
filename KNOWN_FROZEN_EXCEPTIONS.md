# Known Frozen Exceptions

This register documents known discrepancies in frozen historical artifacts.
It does not authorize editing or regenerating those artifacts in place.

## Stage 24 Submission Package Manifest

Affected file: `submission_package_stage24/SUBMISSION_NOTES_AND_NO_GO.md`

| Field | Manifest record | Current frozen file |
|---|---|---|
| Bytes | 1,688 | 1,677 |
| SHA-256 | `345b4879bb67b6b341e6c31d38202066d0d4f060e762e749c7ff341aa0c0483b` | `8f246e3a371b806f7c055e53ff517e9d54375fbc4fc1cfeb6d204b8069e705d0` |

The manifest is `outputs/tables/stage24_submission_package_manifest.csv`.
There are 28 manifest entries and 28 actual package files; this is the only
size or hash mismatch. Entry ordering already passes. The current package note
is byte-identical to `outputs/logs/stage24_final_no_go_check.md`.

### Cause

The historical Stage 24 generator computed and wrote the package manifest at
former line 865, then generated and overwrote the final package note at former
line 887. The manifest therefore captured the note's pre-overwrite state. The
frozen note itself is the valid final no-go content; the manifest entry is
stale.

### Ruling

- Do not modify the Stage 24 package or its manifest in place.
- Do not regenerate the historical Stage 24 outputs.
- Treat the current note as valid and this register as the exception record.
- Retain downstream hashes as historical evidence rather than cascading a
  replacement through later packages.

Regenerating the frozen package would change the Stage 24 manifest and every
downstream record that references its bytes, creating more provenance risk than
this isolated, explained exception.

### Future-Only Generator Repair

`scripts/24_dss_author_submission_completion.py` now:

1. assigns `SUBMISSION_NOTES_AND_NO_GO.md` the explicit manifest role
   `final submission no-go note`;
2. computes and writes the final no-go report before calling
   `package_manifest(...)`;
3. inventories the final bytes rather than a pre-existing version.

Before Stage 26AA, the relevant order was manifest first at lines 865-866 and
final-note write second at lines 885-887. After Stage 26AA, the final-note
writes are at lines 866-868 and the manifest call follows at lines 871-872
(line numbers may shift with later edits). No Stage 24 command was rerun.

