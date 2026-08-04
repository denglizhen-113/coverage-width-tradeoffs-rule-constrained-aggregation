# Data and Code Availability

All analysis code is organized under `src/` and `scripts/`, with focused tests under `tests/`. The reproducible entry point is:

```text
python run_all.py --skip-preprocess --manuscript
```

The repository records raw-data provenance and checksum information in `outputs/tables/data_audit_summary.csv`. If the original data source can be redistributed, the final submission should replace this sentence with its verified public source and access date. Otherwise, processed data and scripts can be shared subject to data-source terms.
