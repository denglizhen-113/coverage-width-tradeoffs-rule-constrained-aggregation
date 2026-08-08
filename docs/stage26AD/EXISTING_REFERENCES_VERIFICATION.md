# Stage 26AD Existing References Verification

## Method

Each DOI-bearing entry was fetched from the live Crossref REST record and then
requested through `doi.org` without automatic redirection. A 3xx response is
accepted only when it supplies a landing location. The landing status is also
recorded; a publisher-side 403 does not make the DOI unresolvable when the DOI
registry supplies a valid target. Authors, print/issued year, title, venue, and
DOI were compared field by field. Access time: `2026-08-08T17:52:26+08:00`.

| 编号 | 作者 | 年份 | 标题 | 出处 | DOI | DOI 解析状态 | 核验 URL | 访问时间 | 结论 |
|---:|---|---:|---|---|---|---|---|---|---|
| 1 | Kenneth J. Arrow | 1950 | A Difficulty in the Concept of Social Welfare | Journal of Political Economy | 10.1086/256963 | doi.org HTTP 302 -> https://www.journals.uchicago.edu/doi/10.1086/256963; landing HTTP 403 | <https://api.crossref.org/works/10.1086%2F256963><br><https://doi.org/10.1086/256963> | 2026-08-08T17:52:26+08:00 | VERIFIED |
| 2 | H. P. Young | 1988 | Condorcet's Theory of Voting | American Political Science Review | 10.2307/1961757 | doi.org HTTP 302 -> https://www.cambridge.org/core/product/identifier/S0003055400196406/type/journal_article; landing HTTP 200 | <https://api.crossref.org/works/10.2307%2F1961757><br><https://doi.org/10.2307/1961757> | 2026-08-08T17:52:26+08:00 | VERIFIED |
| 3 | Cynthia Dwork; Ravi Kumar; Moni Naor; D. Sivakumar | 2001 | Rank aggregation methods for the Web | Proceedings of the 10th international conference on World Wide Web | 10.1145/371920.372165 | doi.org HTTP 302 -> https://dl.acm.org/doi/10.1145/371920.372165; landing HTTP 403 | <https://api.crossref.org/works/10.1145%2F371920.372165><br><https://doi.org/10.1145/371920.372165> | 2026-08-08T17:52:26+08:00 | VERIFIED |
| 4 | Annie Liang | 2019 | Inference of preference heterogeneity from choice data | Journal of Economic Theory | 10.1016/j.jet.2018.09.010 | doi.org HTTP 302 -> https://linkinghub.elsevier.com/retrieve/pii/S0022053118306112; landing HTTP 200 | <https://api.crossref.org/works/10.1016%2Fj.jet.2018.09.010><br><https://doi.org/10.1016/j.jet.2018.09.010> | 2026-08-08T17:52:26+08:00 | VERIFIED |
| 5 | Jan Lorenz; Heiko Rauhut; Frank Schweitzer; Dirk Helbing | 2011 | How social influence can undermine the wisdom of crowd effect | Proceedings of the National Academy of Sciences | 10.1073/pnas.1008636108 | doi.org HTTP 302 -> https://pnas.org/doi/full/10.1073/pnas.1008636108; landing HTTP 403 | <https://api.crossref.org/works/10.1073%2Fpnas.1008636108><br><https://doi.org/10.1073/pnas.1008636108> | 2026-08-08T17:52:26+08:00 | VERIFIED |
| 6 | Charles F. Manski | 2000 | Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice | Journal of Econometrics | 10.1016/s0304-4076(99)00045-7 | doi.org HTTP 302 -> https://linkinghub.elsevier.com/retrieve/pii/S0304407699000457; landing HTTP 200 | <https://api.crossref.org/works/10.1016%2FS0304-4076%2899%2900045-7><br><https://doi.org/10.1016/S0304-4076(99)00045-7> | 2026-08-08T17:52:26+08:00 | VERIFIED |
| 7 | Guido W. Imbens; Charles F. Manski | 2004 | Confidence Intervals for Partially Identified Parameters | Econometrica | 10.1111/j.1468-0262.2004.00555.x | doi.org HTTP 302 -> http://doi.wiley.com/10.1111/j.1468-0262.2004.00555.x; landing HTTP 403 | <https://api.crossref.org/works/10.1111%2Fj.1468-0262.2004.00555.x><br><https://doi.org/10.1111/j.1468-0262.2004.00555.x> | 2026-08-08T17:52:26+08:00 | VERIFIED |
| 8 | Charles F. Manski | 2007 | Minimax-regret treatment choice with missing outcome data | Journal of Econometrics | 10.1016/j.jeconom.2006.06.006 | doi.org HTTP 302 -> https://linkinghub.elsevier.com/retrieve/pii/S0304407606001047; landing HTTP 200 | <https://api.crossref.org/works/10.1016%2Fj.jeconom.2006.06.006><br><https://doi.org/10.1016/j.jeconom.2006.06.006> | 2026-08-08T17:52:26+08:00 | VERIFIED |
| 9 | Galit Shmueli | 2010 | To Explain or to Predict? | Statistical Science | 10.1214/10-sts330 | doi.org HTTP 302 -> https://projecteuclid.org/journals/statistical-science/volume-25/issue-3/To-Explain-or-to-Predict/10.1214/10-STS330.full; landing HTTP 200 | <https://api.crossref.org/works/10.1214%2F10-STS330><br><https://doi.org/10.1214/10-STS330> | 2026-08-08T17:52:26+08:00 | VERIFIED |
| 10 | Mike Ananny; Kate Crawford | 2018 | Seeing without knowing: Limitations of the transparency ideal and its application to algorithmic accountability | New Media &amp; Society | 10.1177/1461444816676645 | doi.org HTTP 302 -> https://journals.sagepub.com/doi/10.1177/1461444816676645; landing HTTP 403 | <https://api.crossref.org/works/10.1177%2F1461444816676645><br><https://doi.org/10.1177/1461444816676645> | 2026-08-08T17:52:26+08:00 | VERIFIED |
| 11 | Frank Bannister; Regina Connolly | 2011 | The Trouble with Transparency: A Critical Review of Openness in e‐Government | Policy &amp; Internet | 10.2202/1944-2866.1076 | doi.org HTTP 302 -> https://onlinelibrary.wiley.com/doi/10.2202/1944-2866.1076; landing HTTP 403 | <https://api.crossref.org/works/10.2202%2F1944-2866.1076><br><https://doi.org/10.2202/1944-2866.1076> | 2026-08-08T17:52:26+08:00 | VERIFIED |
| 12 | Bernard Steunenberg | 1996 | Agent discretion, regulatory policymaking, and different institutional arrangements | Public Choice | 10.1007/bf00136524 | doi.org HTTP 302 -> http://link.springer.com/10.1007/BF00136524; landing HTTP 200 | <https://api.crossref.org/works/10.1007%2FBF00136524><br><https://doi.org/10.1007/BF00136524> | 2026-08-08T17:52:26+08:00 | VERIFIED |

| 编号 | 作者 | 年份 | 标题 | 出处 | DOI | DOI 解析状态 | 核验 URL | 访问时间 | 结论 |
|---:|---|---:|---|---|---|---|---|---|---|
| 13 | COMAP | 2026 | 2026 MCM Problem C: Data With The Stars | The Consortium for Mathematics and Its Applications | N/A | Official page HTTP 200 | <https://contest.comap.com/undergraduate/contests/mcm/contests/2026/problems/index.html> | 2026-08-08T17:52:26+08:00 | VERIFIED |

## Ruling

All 13 existing entries are retained only if every DOI entry above is
`VERIFIED` and the official COMAP page returns HTTP 200. Crossref reports the
Ananny-Crawford article as online-first in 2016 and print publication in 2018;
the manuscript's 2018 year matches the print volume and is therefore not a
field mismatch. No remembered citation metadata was used.
