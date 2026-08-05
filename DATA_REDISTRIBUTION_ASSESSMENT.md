# Stage 26AA Data Redistribution Assessment

Assessment date: 2026-08-01

## Decision

`REDISTRIBUTABLE`

This is a limited decision: the exact COMAP-supplied CSV may be reproduced for
academic or research purposes, with COMAP attribution and the official source
link preserved. It is not a Creative Commons or general commercial-use
license, and this assessment does not grant rights beyond COMAP's published
permission.

## Identified Source

- Dataset: `2026_MCM_Problem_C_Data.csv`.
- Local immutable copy: `data/raw/2026_MCM_Problem_C_Data.csv`.
- Local shape: 421 contestant-season rows and 53 columns.
- Local size: 90,002 bytes.
- SHA-256: `EA99CAEC6EA243BDB450A1971A95BA8A95701A93BE7FF29F0BA3C57D72DDFF52`.
- Program: *Dancing with the Stars*.
- Coverage: contestant information, outcomes, and weekly judges' scores for
  seasons 1 through 34.
- Distribution channel: COMAP's official 2026 MCM/ICM Problem C download page,
  "Data With The Stars."
- Official problem page:
  https://contest.comap.com/undergraduate/contests/mcm/contests/2026/problems/index.html
- Official CSV:
  https://contest.comap.com/undergraduate/contests/mcm/contests/2026/problems/2026_MCM_Problem_C_Data.csv
- Official problem statement:
  https://contest.comap.com/undergraduate/contests/mcm/contests/2026/problems/2026_MCM_Problem_C.pdf

The official CSV downloaded on 2026-08-01 was 90,002 bytes and had SHA-256
`EA99CAEC6EA243BDB450A1971A95BA8A95701A93BE7FF29F0BA3C57D72DDFF52`.
It is therefore byte-identical to the immutable local copy.

## Project-Internal Provenance

The repository contains audit and transformation scripts but no acquisition or
scraping script. Before Stage 26AA it also contained no source URL, download
log, upstream collection description, or data-license file. The retained local
provenance began with a supplied project-root CSV and its checksum-verified
copy under `data/raw/`:

- `scripts/01_data_audit.py` audits the supplied file without modifying it.
- `scripts/02_preprocess.py` and `src/preprocessing.py` transform the immutable
  copy into analysis tables.
- `outputs/logs/data_audit.md` records the local file's shape and checksum.
- `outputs/logs/preprocess_report.md` records source-to-analysis mappings and
  the 4,199-row contestant-week panel.

Stage 26AA established the external COMAP source link by matching the official
download byte-for-byte to the local checksum. It did not recreate an earlier
download history.

## Permission and Copyright Record

The official 2026 problems page identifies COMAP as copyright holder and says:

> "May be reproduced for academic/research purposes"

Source:
https://contest.comap.com/undergraduate/contests/mcm/contests/2026/problems/index.html
(accessed 2026-08-01).

The same page directly links the Problem C CSV, and the linked file is
byte-identical to the local raw file. This is explicit permission to reproduce
that COMAP file for this repository's academic/research purpose. The repository
must preserve the attribution, source URL, and use limitation in
`DATA_TERMS.md`; it must not relabel the data as CC0, CC BY, MIT, or unrestricted
open data.

## Nature of the Compilation

The observations describe publicly reported program participants, placements,
elimination results, and judges' scores. COMAP packages those observations as
the supplied competition dataset. Neither the project nor the official problem
statement identifies COMAP's upstream collection method or states whether all
fields were transcribed directly from broadcasts, supplied by the program, or
assembled from a third-party database. Accordingly:

- the repository can identify COMAP as the immediate data distributor;
- it can describe the fields as a compilation of publicly reported program
  results;
- it cannot claim that this is the television program's original database;
- it cannot identify or endorse an undocumented third-party upstream source.

The published reproduction permission supports the limited redistribution
decision above despite this unresolved upstream-method detail. This is a
provenance and permission assessment, not legal advice.

## Derived Panel

`data/processed/panel_long.csv` has 4,199 contestant-week rows: 2,777 active
rows and 1,422 retained structural-zero inactive rows. It preserves row-level
identities, outcomes, and transformed score information from the source rather
than being only a non-identifying aggregate. It is therefore a derived data
product, not an independently sourced dataset.

The same academic/research-use limitation must follow any redistributed
row-level derivative. Releasing only summaries would reduce duplication of
source fields but would not create a broader license. The staged repository
includes the immutable raw file and reproducible code; the high-volume derived
tables remain locally regenerated and are excluded from Git history.

## Repository and Manuscript Consequence

The repository may include the checksum-verified raw CSV under
`data/raw/`, accompanied by `DATA_TERMS.md`. Code is separately licensed under
MIT. Generated results and row-level derivatives must not be described as
unrestricted data.

A truthful availability statement, after the repository is actually pushed
and verified, is:

> The code and reproducibility materials are available at [verified repository
> URL]. The source dataset is the COMAP 2026 MCM Problem C data file, reproduced
> under COMAP's permission for academic/research purposes; the official source,
> checksum, and applicable notice are recorded in the repository. No observed
> public-vote labels are contained in the dataset.

Until a nonempty remote repository has actually been verified, the manuscript
must not state that these materials are publicly available.

## Stage 26AA-1 Note

On 2026-08-04, Stage 26AA-1 removed the standalone `LICENSE-DATA` file and
replaced it with `DATA_TERMS.md`, which records the source, checksum,
verbatim COMAP permission, and the academic/research scope of use. The two
`LICENSE-DATA` file-name references above were updated to `DATA_TERMS.md`
accordingly. The assessment's substance (limited academic/research
redistribution, no CC/re-licensing, byte-identity of the raw CSV) is
unchanged.
