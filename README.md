# Coverage-Width Tradeoffs in Rule-Constrained Expert-Crowd Aggregation

This repository is the reproducibility package for a methods study of latent
public preference under expert-crowd aggregation rules. It contains the
audited empirical testbed pipeline, preregistered synthetic experiments,
same-information baselines, component ablations, manuscript-facing tables and
figures, and verification checks.

The study does not claim to observe or recover true audience votes. Empirical
outputs are feasible support intervals, feasible ranking sets, and partially
identified public appeal under stated rule assumptions. Known truth exists
only inside the synthetic simulators.

## Licenses

- Code: MIT; see `LICENSE`. The MIT license covers only the code in this
  repository and does not extend to the data.
- Source data: COMAP MCM 2026 competition problem materials, reproduced under
  COMAP's permission for academic/research purposes only. The data are not
  released under the MIT license and are not otherwise re-licensed by this
  repository. See `DATA_TERMS.md` for the exact source, the verbatim COMAP
  permission, checksum, and scope of use, and
  `DATA_REDISTRIBUTION_ASSESSMENT.md` for the provenance ruling.
- Manuscript text and third-party material are not relicensed by the MIT code
  license.

## Data

`data/raw/2026_MCM_Problem_C_Data.csv` is the official COMAP 2026 MCM Problem C
file, byte-matched to the official download:

- 421 contestant-season rows, 53 columns, 90,002 bytes.
- SHA-256:
  `EA99CAEC6EA243BDB450A1971A95BA8A95701A93BE7FF29F0BA3C57D72DDFF52`.
- Immediate distributor: COMAP.
- Program represented: *Dancing with the Stars*, seasons 1-34.

The repository does not assert an undocumented upstream collection method.
The source contains no observed public-vote label.

## Experiment Scale

- Stage 26X-1: 20 preregistered seeds, 12 internal and 3 external parameter
  regions, 67,200 simulated cases, 300 raw cell files, and 261,600 retained
  method-level replication rows.
- Stage 26X-2: maximum-entropy, Bayesian, and registered component-ablation
  classes; 300 raw files per class and 290,400 retained rows in total.
- Combined local regeneration: 1,200 raw files and 552,000 rows.

The generated raw archives are intentionally not preloaded. No individual
file approaches GitHub's 100 MiB limit, but the archives contain many
reproducible files. `reproduce.md` gives the exact regeneration commands,
expected outputs, paper mappings, and resource observations.

## Layout

| Path | Purpose |
|---|---|
| `scripts/`, `src/` | Canonical runnable pipeline and shared modules |
| `code/` | Deposit-facing mirror of the 26X-1/26X-2 experiment scripts and source modules |
| `data/raw/` | Checksum-verified COMAP source data |
| `manuscript/` | Inputs used by the Stage 1-23 manuscript pipeline |
| `outputs/stage26W/` | Locked manuscript input required by 26X hash gates |
| `outputs/stage26X-1/`, `outputs/stage26X-2/` | Locked preregistration inputs; generated results appear here |
| `reference/` | Expected tables, figures, and manuscript used only by `verify_reproduction.py` |
| `tests/` | The 69-test pre-Stage-23 contract set plus focused 26X contracts |
| `conda-lock-win-64.txt` | Exact Windows binary builds required by historical 26X hashes |

## Start

On Windows PowerShell with Conda installed:

```powershell
$env:CONDA_PKGS_DIRS = Join-Path (Get-Location) '.conda-pkgs'
conda create --yes --prefix .conda-env --file conda-lock-win-64.txt
$env:PYTHONNOUSERSITE = '1'
$env:MPLCONFIGDIR = Join-Path (Get-Location) '.mplconfig'
$py = Resolve-Path '.conda-env\python.exe'
& $py -m pip install --no-cache-dir -r requirements.txt -r requirements-docs.txt
Get-Content reproduce.md
```

Run the commands in `reproduce.md` in order. The final verifier exits nonzero
on a missing output, count mismatch, table difference, figure-pixel
difference, or manuscript mismatch.

## History and Frozen Exception

Git was first enabled at Stage 26AA; earlier commit history does not exist and
was not reconstructed. See `REPOSITORY_HISTORY_NOTE.md`. The one known Stage 24
manifest-order discrepancy is documented in `KNOWN_FROZEN_EXCEPTIONS.md` and
does not alter the frozen package.
