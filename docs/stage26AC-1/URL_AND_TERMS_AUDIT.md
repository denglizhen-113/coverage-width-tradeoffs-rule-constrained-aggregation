# Stage 26AC-1 URL and Terms Audit

## Ruling

Active files are internally prepared for `https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation`. The six Stage 25
license generators no longer assign CC BY 4.0, CC0, or a repository data
license to the COMAP file. COMAP attribution, its formal reference entry, and
the test-order boundary are present.

The author reports that the GitHub rename is complete and local `origin` equals `https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation.git`. Configuration status: `PASS`. Remote network reachability remains a separate pre-push check because github.com was temporarily unreachable during this audit. The repository must remain private until the private push and later anonymous public checks complete.

## Active public-facing surfaces

- `README.md`
- `outputs/stage26AA/repo_staging/README.md`
- `outputs/stage26AA/repo_staging/reproduce.md`
- `outputs/stage26AA/repo_staging/DATA_TERMS.md`
- `outputs/stage26AC/METHODS_research_draft_STAGE26AC.md`
- `outputs/stage26AD/METHODS_research_draft_STAGE26AD.md`
- `outputs/stage26AA/repo_staging/manuscript/METHODS_research_draft_STAGE26AC.md`
- `outputs/stage26AA/repo_staging/manuscript/METHODS_research_draft_STAGE26AD.md`

Each surface contains the approved URL. The Stage 26AC/26AD manuscripts retain
private tense and therefore do not yet claim successful public access.

## Generator synchronization

| Script | SHA-256 | Result |
|---|---|---|
| `25ha_apply_author_provided_information.py` | `2881420383298098EB42CFD109D6BE32CB411013941F05CA086DA0B25F177FD0` | MATCH root/staged |
| `25hb_apply_final_author_confirmations.py` | `62274C79C817C02040AE88A4947AE34C49FC849A9DCD48708F2F7A9333517787` | MATCH root/staged |
| `25hc_apply_repository_address_and_approval_closure.py` | `0A6E94C4A04E5E326EAEDEED741198A0CBDBA63A0399FB8BA3234C0D6FE5D509` | MATCH root/staged |
| `25hd_reconstruct_dss_submission_docx.py` | `1876D67235AFF93795CC1ABF5E83BBDD8111C3EF07FA7B8D0144D0ABAD5BBC62` | MATCH root/staged |
| `25he_finalize_dss_submission_package.py` | `B25105BD2355E6F851195B771DF4E883CB801402289E48926D6F9BE521A375CC` | MATCH root/staged |
| `25hf_resolve_dss_upload_gate.py` | `C9533F0F7817610519C9083E2439C2831AAF98CDF9F2415F6AD9AE0A7C7C3F86` | MATCH root/staged |
| `26y_ejor_submission_migration.py` | `64A600B47E15B582C013829233692D8C0C11441DDB3ADC15E45FA71F574EA8BE` | MATCH root/staged |
| `26ac_research_audit_optimization.py` | `B2CE5CA24FE8345FF9A8954459F29FF7DF5DF5E0FB92BAEABF22D9FFF6D9997E` | MATCH root/staged |
| `26ac1_repository_publication_readiness.py` | `5253EBDE5E8B82F62ACAF2EFAF58C7CE69C512674E7DA4C83FB718282DD47ECB` | MATCH root/staged |
| `26ad_literature_verification.py` | `B58C0EE88FDD32D187D9C0CC5B0CF8556E25E81C53B57575056FA29E8039E9C8` | MATCH root/staged |

## Terms and provenance

- `DATA_TERMS.md` preserves the COMAP copyright notice and the verbatim
  academic/research-purpose permission.
- MIT remains code-only; no active generator emits a separate data license.
- Historical Stage 25 logs and frozen outputs were not silently rewritten.
- The author selected a normal corrective commit; history rewrite is neither
  required nor authorized.

## Remaining external sequence

1. Review and normally commit the staged changes.
2. Recheck authenticated remote reachability and push while private.
3. Confirm the pushed commit and repository file inventory.
4. Make public under the author's conditional approval.
5. Verify the repository page, raw COMAP CSV, and clone URL anonymously.
6. If any check fails, return the repository to private.
