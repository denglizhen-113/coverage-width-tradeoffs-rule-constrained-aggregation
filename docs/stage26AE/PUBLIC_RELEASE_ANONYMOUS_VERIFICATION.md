# Stage 26AF-1 Public Release Verification

Checked at: $time.

All requests below were performed without authenticated GitHub credentials. Clone disabled Git credential helpers, interactive prompting, and askpass.

| Check | URL or command | Status | Evidence |
|---|---|---:|---|
| Repository page | `https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation` | HTTP 200 | Public repository page resolved without authentication. |
| Raw COMAP CSV | `https://raw.githubusercontent.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation/main/data/raw/2026_MCM_Problem_C_Data.csv` | HTTP 200 | 89,580 bytes retrieved. |
| Clean clone | `git -c credential.helper= -c core.askPass= -c credential.interactive=never clone https://github.com/denglizhen-113/coverage-width-tradeoffs-rule-constrained-aggregation.git` | exit 0 | Cloned `main` at `97de71f0c525d16001c3f4f7812e53830210bbea`; CSV SHA-256 matched `EA99CAEC6EA243BDB450A1971A95BA8A95701A93BE7FF29F0BA3C57D72DDFF52`. |

Conclusion: `PUBLIC_RELEASE_ANONYMOUS_VERIFICATION_PASS`.

No privacy rollback was required.
