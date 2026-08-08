# Cover-Letter Reproducibility Paragraph

The reproducibility package is designated for `https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation`. Following
`reproduce.md` in its documented order, the clean-room run regenerated 1,200
raw experiment files containing 552,000 retained method-level rows and matched
16/16 manuscript tables and 8/8 figures. The package does not claim that a
fresh clone is bare-`pytest` green before generation: a direct pre-generation
staged-package run passed 98/100 tests, and the two failures were assertions for
generated artifacts that the release intentionally omits. After those artifacts
were generated in the documented sequence, the complete verification run
passed. The fixed Bayesian draw bank retained and disclosed all 94
insufficient-posterior rows; none was replaced or deleted.

This paragraph may be inserted into the eventual SIMPAT cover letter only
after the repository is public and the designated URL, raw CSV URL, and clone
path pass anonymous verification. Before that gate it is approved wording, not
a public-availability claim.
