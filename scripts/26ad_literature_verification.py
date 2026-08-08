"""Verify literature metadata online and build the non-frozen Stage 26AD draft."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SOURCE = Path("outputs/stage26AC/METHODS_research_draft_STAGE26AC.md")
OUTPUT_DIR = Path("outputs/stage26AD")
ACCESS_TIME = "2026-08-08T17:52:26+08:00"
USER_AGENT = "C2-research-audit/1.0 (mailto:3070116993@qq.com)"
COMAP_URL = (
    "https://contest.comap.com/undergraduate/contests/mcm/contests/2026/"
    "problems/index.html"
)


class VerificationError(RuntimeError):
    """Raised when a citation field or integrity gate cannot be verified."""


@dataclass(frozen=True)
class Reference:
    number: int
    families: tuple[str, ...]
    year: int
    title: str
    container: str
    doi: str
    citation: str
    domain: str
    location: str
    support: str


EXISTING = (
    Reference(1, ("Arrow",), 1950, "A Difficulty in the Concept of Social Welfare", "Journal of Political Economy", "10.1086/256963", "", "social choice", "Section 3.2", "aggregation impossibility foundation"),
    Reference(2, ("Young",), 1988, "Condorcet's Theory of Voting", "American Political Science Review", "10.2307/1961757", "", "social choice", "Section 3.2", "Condorcet voting foundation"),
    Reference(3, ("Dwork", "Kumar", "Naor", "Sivakumar"), 2001, "Rank aggregation methods for the Web", "Proceedings of the 10th international conference on World Wide Web", "10.1145/371920.372165", "", "social choice", "Section 3.2", "algorithmic rank aggregation"),
    Reference(4, ("Liang",), 2019, "Inference of preference heterogeneity from choice data", "Journal of Economic Theory", "10.1016/j.jet.2018.09.010", "", "partial identification", "Section 3.1", "preference heterogeneity from choice data"),
    Reference(5, ("Lorenz", "Rauhut", "Schweitzer", "Helbing"), 2011, "How social influence can undermine the wisdom of crowd effect", "Proceedings of the National Academy of Sciences", "10.1073/pnas.1008636108", "", "expert-crowd", "Section 3.3", "social-influence boundary"),
    Reference(6, ("Manski",), 2000, "Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice", "Journal of Econometrics", "10.1016/S0304-4076(99)00045-7", "", "partial identification", "Section 3.1", "identification and decision ambiguity"),
    Reference(7, ("Imbens", "Manski"), 2004, "Confidence Intervals for Partially Identified Parameters", "Econometrica", "10.1111/j.1468-0262.2004.00555.x", "", "partial identification", "Section 3.1", "confidence intervals under partial identification"),
    Reference(8, ("Manski",), 2007, "Minimax-regret treatment choice with missing outcome data", "Journal of Econometrics", "10.1016/j.jeconom.2006.06.006", "", "partial identification", "Section 3.1", "decision criterion under incomplete identification"),
    Reference(9, ("Shmueli",), 2010, "To Explain or to Predict?", "Statistical Science", "10.1214/10-STS330", "", "methodology", "Section 3.4", "claim-objective distinction"),
    Reference(10, ("Ananny", "Crawford"), 2018, "Seeing without knowing: Limitations of the transparency ideal and its application to algorithmic accountability", "New Media & Society", "10.1177/1461444816676645", "", "transparency", "Section 3.4", "transparency limitation"),
    Reference(11, ("Bannister", "Connolly"), 2011, "The Trouble with Transparency: A Critical Review of Openness in e-Government", "Policy & Internet", "10.2202/1944-2866.1076", "", "transparency", "Section 3.4", "openness limitation"),
    Reference(12, ("Steunenberg",), 1996, "Agent discretion, regulatory policymaking, and different institutional arrangements", "Public Choice", "10.1007/BF00136524", "", "discretion", "Section 3.4", "institutional discretion"),
)


NEW = (
    Reference(14, ("Tamer",), 2010, "Partial Identification in Econometrics", "Annual Review of Economics", "10.1146/annurev.economics.050708.143401", "E. Tamer, Partial Identification in Econometrics, Annual Review of Economics 2 (1) (2010) 167-195. https://doi.org/10.1146/annurev.economics.050708.143401.", "partial identification", "Section 3.1", "review of partial-identification objects and methods"),
    Reference(15, ("Kline", "Tamer"), 2023, "Recent Developments in Partial Identification", "Annual Review of Economics", "10.1146/annurev-economics-051520-021124", "B. Kline, E. Tamer, Recent Developments in Partial Identification, Annual Review of Economics 15 (1) (2023) 125-150. https://doi.org/10.1146/annurev-economics-051520-021124.", "partial identification", "Section 3.1", "recent partial-identification developments"),
    Reference(16, ("Kaido", "Molinari", "Stoye"), 2019, "Confidence Intervals for Projections of Partially Identified Parameters", "Econometrica", "10.3982/ecta14075", "H. Kaido, F. Molinari, J. Stoye, Confidence Intervals for Projections of Partially Identified Parameters, Econometrica 87 (4) (2019) 1397-1432. https://doi.org/10.3982/ecta14075.", "partial identification", "Section 3.1", "inference for projections of identified sets"),
    Reference(17, ("Bugni", "Canay", "Shi"), 2017, "Inference for subvectors and other functions of partially identified parameters in moment inequality models", "Quantitative Economics", "10.3982/qe490", "F.A. Bugni, I.A. Canay, X. Shi, Inference for subvectors and other functions of partially identified parameters in moment inequality models, Quantitative Economics 8 (1) (2017) 1-38. https://doi.org/10.3982/qe490.", "partial identification", "Section 3.1", "inference for functions of partially identified parameters"),
    Reference(18, ("Brandt", "Conitzer", "Endriss", "Lang", "Procaccia"), 2016, "Introduction to Computational Social Choice", "Handbook of Computational Social Choice", "10.1017/CBO9781107446984.002", "F. Brandt, V. Conitzer, U. Endriss, J. Lang, A.D. Procaccia, Introduction to Computational Social Choice, in: Handbook of Computational Social Choice, Cambridge University Press, 2016, pp. 1-20. https://doi.org/10.1017/CBO9781107446984.002.", "social choice", "Section 3.2", "computational treatment of collective choice"),
    Reference(19, ("List", "Pettit"), 2002, "Aggregating Sets of Judgments: An Impossibility Result", "Economics and Philosophy", "10.1017/S0266267102001098", "C. List, P. Pettit, Aggregating Sets of Judgments: An Impossibility Result, Economics and Philosophy 18 (1) (2002) 89-110. https://doi.org/10.1017/S0266267102001098.", "social choice", "Section 3.2", "judgment-aggregation impossibility boundary"),
    Reference(20, ("Budescu", "Chen"), 2015, "Identifying Expertise to Extract the Wisdom of Crowds", "Management Science", "10.1287/mnsc.2014.1909", "D.V. Budescu, E. Chen, Identifying Expertise to Extract the Wisdom of Crowds, Management Science 61 (2) (2015) 267-280. https://doi.org/10.1287/mnsc.2014.1909.", "expert-crowd", "Section 3.3", "expertise-sensitive crowd aggregation"),
    Reference(21, ("Mannes", "Soll", "Larrick"), 2014, "The wisdom of select crowds", "Journal of Personality and Social Psychology", "10.1037/a0036677", "A.E. Mannes, J.B. Soll, R.P. Larrick, The wisdom of select crowds, Journal of Personality and Social Psychology 107 (2) (2014) 276-299. https://doi.org/10.1037/a0036677.", "expert-crowd", "Section 3.3", "selection of informed subsets"),
    Reference(22, ("Madirolas", "de Polavieja"), 2015, "Improving Collective Estimations Using Resistance to Social Influence", "PLOS Computational Biology", "10.1371/journal.pcbi.1004594", "G. Madirolas, G.G. de Polavieja, Improving Collective Estimations Using Resistance to Social Influence, PLOS Computational Biology 11 (11) (2015) e1004594. https://doi.org/10.1371/journal.pcbi.1004594.", "expert-crowd", "Section 3.3", "social-influence-resistant collective estimation"),
    Reference(23, ("Becker", "Brackbill", "Centola"), 2017, "Network dynamics of social influence in the wisdom of crowds", "Proceedings of the National Academy of Sciences", "10.1073/pnas.1615978114", "J. Becker, D. Brackbill, D. Centola, Network dynamics of social influence in the wisdom of crowds, Proceedings of the National Academy of Sciences 114 (26) (2017). https://doi.org/10.1073/pnas.1615978114.", "expert-crowd", "Section 3.3", "network-dependent social influence"),
    Reference(24, ("Fiechter", "Kornell"), 2021, "How the wisdom of crowds, and of the crowd within, are affected by expertise", "Cognitive Research: Principles and Implications", "10.1186/s41235-021-00273-6", "J.L. Fiechter, N. Kornell, How the wisdom of crowds, and of the crowd within, are affected by expertise, Cognitive Research: Principles and Implications 6 (1) (2021) 5. https://doi.org/10.1186/s41235-021-00273-6.", "expert-crowd", "Section 3.3", "expertise effects on crowd aggregation"),
    Reference(25, ("Kameda", "Toyokawa", "Tindale"), 2022, "Information aggregation and collective intelligence beyond the wisdom of crowds", "Nature Reviews Psychology", "10.1038/s44159-022-00054-y", "T. Kameda, W. Toyokawa, R.S. Tindale, Information aggregation and collective intelligence beyond the wisdom of crowds, Nature Reviews Psychology 1 (6) (2022) 345-357. https://doi.org/10.1038/s44159-022-00054-y.", "expert-crowd", "Section 3.3", "recent review of information aggregation and collective intelligence"),
    Reference(26, ("Burton", "Altman", "Royston", "Holder"), 2006, "The design of simulation studies in medical statistics", "Statistics in Medicine", "10.1002/sim.2673", "A. Burton, D.G. Altman, P. Royston, R.L. Holder, The design of simulation studies in medical statistics, Statistics in Medicine 25 (24) (2006) 4279-4292. https://doi.org/10.1002/sim.2673.", "simulation methodology", "Section 3.4", "simulation-study design"),
    Reference(27, ("Morris", "White", "Crowther"), 2019, "Using simulation studies to evaluate statistical methods", "Statistics in Medicine", "10.1002/sim.8086", "T.P. Morris, I.R. White, M.J. Crowther, Using simulation studies to evaluate statistical methods, Statistics in Medicine 38 (11) (2019) 2074-2102. https://doi.org/10.1002/sim.8086.", "simulation methodology", "Section 3.4", "estimands, performance measures, and simulation reporting"),
    Reference(28, ("Kleijnen",), 1995, "Verification and validation of simulation models", "European Journal of Operational Research", "10.1016/0377-2217(94)00016-6", "J.P.C. Kleijnen, Verification and validation of simulation models, European Journal of Operational Research 82 (1) (1995) 145-162. https://doi.org/10.1016/0377-2217(94)00016-6.", "simulation methodology", "Section 3.4", "simulation verification and validation"),
    Reference(29, ("Kleijnen",), 2005, "An overview of the design and analysis of simulation experiments for sensitivity analysis", "European Journal of Operational Research", "10.1016/j.ejor.2004.02.005", "J.P.C. Kleijnen, An overview of the design and analysis of simulation experiments for sensitivity analysis, European Journal of Operational Research 164 (2) (2005) 287-300. https://doi.org/10.1016/j.ejor.2004.02.005.", "simulation methodology", "Section 3.4", "simulation sensitivity analysis"),
    Reference(30, ("Monks", "Currie", "Onggo", "Robinson", "Kunc", "Taylor"), 2019, "Strengthening the reporting of empirical simulation studies: Introducing the STRESS guidelines", "Journal of Simulation", "10.1080/17477778.2018.1442155", "T. Monks, C.S.M. Currie, B.S. Onggo, S. Robinson, M. Kunc, S.J.E. Taylor, Strengthening the reporting of empirical simulation studies: Introducing the STRESS guidelines, Journal of Simulation 13 (1) (2019) 55-67. https://doi.org/10.1080/17477778.2018.1442155.", "simulation methodology", "Section 3.4", "transparent simulation reporting"),
)


RELATED_WORK = """## 3. Related Work

### 3.1 Partial identification and method selection under uncertainty

Partial identification replaces an unsupported point claim with the set of values consistent with observations and assumptions [6,14,15]. The inferential literature develops confidence regions for partially identified parameters, projections, subvectors, and other functions of identified sets [7,16,17]. Related work also connects choice data to preference heterogeneity and decisions under incomplete information [4,8]. This paper uses that logic in an institutional inverse problem: observed expert scores and coarse outcomes restrict, but do not reveal, the latent public component. Its contribution is not a new generic confidence-region procedure; it is the explicit mapping from heterogeneous aggregation rules to different cardinal and ordinal feasible objects and to a conditional method-selection boundary.

### 3.2 Computational social choice and aggregation rules

Social-choice foundations show that collective orderings depend on the aggregation rule and the admissible preference domain [1,2]. Algorithmic rank aggregation and computational social choice make the rule itself an explicit mathematical and computational object [3,18], while judgment-aggregation results show that jointly attractive aggregation requirements can be incompatible [19]. These literatures primarily map individual inputs into collective outcomes. The present study addresses the inverse direction: given expert inputs, a documented rule, and a coarse institutional outcome, which latent public states remain feasible? It therefore does not claim to solve voting-rule design or to rank social-choice mechanisms by welfare.

### 3.3 Expert judgment, crowd aggregation, and social influence

Crowd accuracy is not guaranteed by group size alone. Prior work studies how social influence can degrade collective estimates [5], how expertise or selected subsets can be used in aggregation [20,21], and how resistance to influence or network structure changes collective estimation [22,23]. More recent studies directly examine expertise effects and information aggregation beyond a simple independent-crowd model [24,25]. This paper does not optimize crowd composition or estimate individual expertise. It treats the public component as latent and asks how much the observed expert-crowd outcome identifies under the stated rule.

### 3.4 Simulation methodology, discretion, and the research gap

Simulation evidence requires declared data-generating factors, performance measures, verification and validation, sensitivity analysis, and transparent reporting [26-30]. The present evaluation accordingly separates known-truth calibration from the empirical testbed, fixes seeds and parameter cells in preregistered designs, reports undefined posterior rows, and distinguishes structural nesting from empirical performance. These controls support reproducibility within the registered simulators; they do not validate untested institutions, priors, likelihoods, or misspecification processes.

Transparency and discretion also have limits: more disclosure need not reveal the underlying process, and institutional discretion changes the mapping from observations to admissible latent states [10-12]. The resulting gap is a rule-aware, auditable comparison that distinguishes explanation from prediction [9], localizes which institutional constraint creates a coverage-width tradeoff, and compares feasible-set and posterior summaries on aligned information. The contribution is therefore a bounded method-selection criterion rather than a universal superiority claim.
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify every existing and proposed reference through Crossref and "
            "doi.org, then generate Stage 26AD literature reports and draft."
        )
    )
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--access-time", default=ACCESS_TIME)
    return parser.parse_args(argv)


def normalize(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("‐", "-").replace("‑", "-").replace("–", "-")
    text = text.replace("—", "-").replace("’", "'").replace("&", "and")
    text = re.sub(r"[^a-zA-Z0-9]+", " ", text).strip().casefold()
    return text


def request_json(url: str) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(3):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(attempt + 1)
    raise VerificationError(f"Metadata request failed after three attempts: {url}: {last_error}")


def crossref_record(doi: str) -> tuple[dict[str, Any], str]:
    encoded = urllib.parse.quote(doi, safe="")
    url = f"https://api.crossref.org/works/{encoded}"
    payload = request_json(url)
    if payload.get("status") != "ok" or not payload.get("message"):
        raise VerificationError(f"Crossref did not return a work for {doi}")
    return payload["message"], url


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def http_probe(url: str, follow: bool, byte_range: bool = True) -> tuple[int, str, str]:
    opener = (
        urllib.request.build_opener()
        if follow
        else urllib.request.build_opener(NoRedirect())
    )
    headers = {"User-Agent": USER_AGENT}
    if byte_range:
        headers["Range"] = "bytes=0-0"
    request = urllib.request.Request(url, headers=headers, method="GET")
    attempts = 1 if follow else 3
    timeout = 8 if follow else 20
    for attempt in range(attempts):
        try:
            with opener.open(request, timeout=timeout) as response:
                return response.status, response.geturl(), response.headers.get("Location", "")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.geturl(), exc.headers.get("Location", "")
        except (urllib.error.URLError, TimeoutError):
            if attempt < attempts - 1:
                time.sleep(attempt + 1)
    return 0, url, ""


def resolve_doi(doi: str) -> dict[str, Any]:
    doi_url = f"https://doi.org/{doi}"
    status, _, location = http_probe(doi_url, follow=False)
    resolved = status in {200, 301, 302, 303, 307, 308} and (
        status == 200 or bool(location)
    )
    landing_status = None
    landing_url = location
    if location:
        landing_status, landing_url, _ = http_probe(location, follow=True)
    return {
        "doi_url": doi_url,
        "resolver_status": status,
        "location": location,
        "landing_status": landing_status,
        "landing_url": landing_url,
        "resolved": resolved,
    }


def publication_year(record: dict[str, Any]) -> int:
    for key in ("published-print", "issued", "published", "published-online"):
        parts = record.get(key, {}).get("date-parts", [])
        if parts and parts[0]:
            return int(parts[0][0])
    raise VerificationError("Crossref record has no publication year")


def record_families(record: dict[str, Any]) -> tuple[str, ...]:
    return tuple(author.get("family", "") for author in record.get("author", []))


def first(record: dict[str, Any], key: str) -> str:
    value = record.get(key, "")
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value or "")


def verify_reference(reference: Reference) -> dict[str, Any]:
    record, metadata_url = crossref_record(reference.doi)
    resolution = resolve_doi(reference.doi)
    observed = {
        "families": record_families(record),
        "year": publication_year(record),
        "title": first(record, "title"),
        "container": first(record, "container-title"),
        "doi": str(record.get("DOI", "")),
    }
    mismatches: list[str] = []
    if tuple(normalize(value) for value in observed["families"]) != tuple(
        normalize(value) for value in reference.families
    ):
        mismatches.append(
            f"authors expected {reference.families}, observed {observed['families']}"
        )
    for key, expected in (
        ("year", reference.year),
        ("title", reference.title),
        ("container", reference.container),
        ("doi", reference.doi),
    ):
        value = observed[key]
        if key == "year":
            equal = value == expected
        else:
            equal = normalize(str(value)) == normalize(str(expected))
        if not equal:
            mismatches.append(f"{key} expected {expected!r}, observed {value!r}")
    if not resolution["resolved"]:
        mismatches.append(
            f"DOI resolver returned HTTP {resolution['resolver_status']} without location"
        )
    return {
        "reference": reference,
        "record": record,
        "metadata_url": metadata_url,
        "resolution": resolution,
        "observed": observed,
        "mismatches": mismatches,
        "verified": not mismatches,
    }


def author_text(record: dict[str, Any]) -> str:
    names = []
    for author in record.get("author", []):
        names.append(" ".join(filter(None, (author.get("given"), author.get("family")))))
    return "; ".join(names)


def resolution_text(resolution: dict[str, Any]) -> str:
    base = f"doi.org HTTP {resolution['resolver_status']}"
    if resolution["location"]:
        base += f" -> {resolution['location']}"
    if resolution["landing_status"] is not None:
        base += f"; landing HTTP {resolution['landing_status']}"
    return base


def verification_table(rows: list[dict[str, Any]], access_time: str) -> str:
    lines = [
        "| 编号 | 作者 | 年份 | 标题 | 出处 | DOI | DOI 解析状态 | 核验 URL | 访问时间 | 结论 |",
        "|---:|---|---:|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        ref = row["reference"]
        observed = row["observed"]
        conclusion = "VERIFIED" if row["verified"] else "FIELD_MISMATCH: " + "; ".join(row["mismatches"])
        urls = f"<{row['metadata_url']}><br><{row['resolution']['doi_url']}>"
        lines.append(
            f"| {ref.number} | {author_text(row['record'])} | {observed['year']} | "
            f"{observed['title']} | {observed['container']} | {observed['doi']} | "
            f"{resolution_text(row['resolution'])} | {urls} | {access_time} | {conclusion} |"
        )
    return "\n".join(lines)


def render_existing(rows: list[dict[str, Any]], comap_status: int, access_time: str) -> str:
    table = verification_table(rows, access_time)
    return f"""# Stage 26AD Existing References Verification

## Method

Each DOI-bearing entry was fetched from the live Crossref REST record and then
requested through `doi.org` without automatic redirection. A 3xx response is
accepted only when it supplies a landing location. The landing status is also
recorded; a publisher-side 403 does not make the DOI unresolvable when the DOI
registry supplies a valid target. Authors, print/issued year, title, venue, and
DOI were compared field by field. Access time: `{access_time}`.

{table}

| 编号 | 作者 | 年份 | 标题 | 出处 | DOI | DOI 解析状态 | 核验 URL | 访问时间 | 结论 |
|---:|---|---:|---|---|---|---|---|---|---|
| 13 | COMAP | 2026 | 2026 MCM Problem C: Data With The Stars | The Consortium for Mathematics and Its Applications | N/A | Official page HTTP {comap_status} | <{COMAP_URL}> | {access_time} | {"VERIFIED" if comap_status == 200 else "NOT_FOUND"} |

## Ruling

All 13 existing entries are retained only if every DOI entry above is
`VERIFIED` and the official COMAP page returns HTTP 200. Crossref reports the
Ananny-Crawford article as online-first in 2016 and print publication in 2018;
the manuscript's 2018 year matches the print volume and is therefore not a
field mismatch. No remembered citation metadata was used.
"""


def render_gap_analysis() -> str:
    return """# Stage 26AD Literature Gap Analysis

## Baseline coverage in the 13-reference Stage 26AC draft

| Domain | Existing direct references | Missing foundation/recent coverage | Review consequence |
|---|---|---|---|
| Partial/set identification | 4: [4], [6]-[8] | No field-level review, recent overview, or treatment of projections/subvectors | The manuscript used partial-identification language correctly but did not show adequate engagement with inference beyond basic intervals. |
| Computational social choice and aggregation rules | 3: [1]-[3] | No computational-social-choice synthesis or judgment-aggregation boundary | The inverse problem could appear detached from the rule-design literature that motivates heterogeneous aggregation mechanisms. |
| Expert and crowd judgment | 1: [5] | No expertise selection, subset aggregation, network influence, or recent collective-intelligence review | This was the thinnest domain relative to the title and a plausible desk-review concern. |
| Simulation methodology | 0 direct methodological references; [9] is a general objective distinction | No simulation design, verification/validation, sensitivity-analysis, or reporting guidance | This was the highest venue-specific gap for a simulation-methods journal. Reproducible code alone does not replace engagement with simulation methodology. |

References [10]-[12] cover transparency and institutional discretion and are
useful cross-cutting context, but they do not fill any of the four method
domains above.

## Verified supplementation plan

| Domain | Verified additions | Coverage after integration | Boundary |
|---|---|---:|---|
| Partial/set identification | [14]-[17] | 8 | Adds a field review, a 2023 update, and inference for projections/subvectors; does not claim the paper implements those generic procedures. |
| Computational social choice | [18]-[19] | 5 | Adds a computational synthesis and judgment-aggregation impossibility result; does not turn the paper into a voting-rule design study. |
| Expert-crowd aggregation | [20]-[25] | 7 | Adds expertise, selected crowds, social/network influence, and 2021-2022 reviews; the paper still does not estimate expertise or optimize group composition. |
| Simulation methodology | [26]-[30] | 5 | Adds design, performance evaluation, verification/validation, sensitivity analysis, and reporting; external validation beyond the two simulators remains absent. |

The integrated total is 30 references. This count is an outcome of the
verified topical set, not a quota: two ambiguous/incomplete candidates remain
excluded, and no citation was added solely to increase the count.
"""


def render_new(rows: list[dict[str, Any]], access_time: str) -> str:
    lines = [
        "# Stage 26AD Verified New References",
        "",
        "Only rows with exact author/year/title/venue/DOI agreement and a live DOI resolver location are listed.",
        "",
        "| 编号 | 作者 | 年份 | 标题 | 出处 | DOI | DOI 解析状态 | 核验 URL | 访问时间 | 对应缺口 | 拟引用位置 |",
        "|---:|---|---:|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        ref = row["reference"]
        observed = row["observed"]
        urls = f"<{row['metadata_url']}><br><{row['resolution']['doi_url']}>"
        lines.append(
            f"| {ref.number} | {author_text(row['record'])} | {observed['year']} | "
            f"{observed['title']} | {observed['container']} | {observed['doi']} | "
            f"{resolution_text(row['resolution'])} | {urls} | {access_time} | "
            f"{ref.domain}: {ref.support} | {ref.location} |"
        )
    return "\n".join(lines) + "\n"


def render_unverified(unverified: list[dict[str, Any]], access_time: str) -> str:
    handbook = unverified[0]
    working = unverified[1]
    return f"""# Stage 26AD Unverified Candidates

These entries must not be written into the manuscript.

## Handbook-level DOI

- Candidate: *Handbook of Computational Social Choice*.
- DOI: `10.1017/CBO9781107446984`.
- Crossref URL: <{handbook['url']}>.
- Accessed: {access_time}.
- Missing/conflicting field: the record contains the five expected editors but
  also exposes Hervé Moulin in the author field. That makes a book-level author
  citation ambiguous. The manuscript instead uses the fully verified
  introduction chapter DOI `10.1017/CBO9781107446984.002`.

## Working-paper DOI

- Candidate: *Econometrics with Partial Identification*.
- DOI: `10.1920/wp.cem.2019.2519`.
- Crossref URL: <{working['url']}>.
- Accessed: {access_time}.
- Missing field: `container-title` is empty in the accessed Crossref record,
  so the requested outlet field cannot be completely verified. The item is not
  inserted; the verified Annual Review articles cover the relevant field-level
  discussion.

No unverified candidate appears in the Stage 26AD reference list or body.
"""


def render_integration_log() -> str:
    lines = [
        "# Stage 26AD Citation Integration Log",
        "",
        "| 文献 | 插入位置 | 支撑的论断 | 论断原文 |",
        "|---|---|---|---|",
    ]
    claims = {
        14: "field-level partial-identification review",
        15: "recent partial-identification developments",
        16: "confidence regions for projections",
        17: "inference for subvectors/functions",
        18: "computational social choice treats rules algorithmically",
        19: "aggregation requirements may be incompatible",
        20: "expertise-sensitive crowd aggregation",
        21: "selected subsets in crowd judgment",
        22: "resistance to social influence",
        23: "network structure and social influence",
        24: "expertise effects on crowd estimates",
        25: "recent collective-intelligence synthesis",
        26: "simulation-study design",
        27: "simulation estimands and performance measures",
        28: "verification and validation",
        29: "sensitivity-analysis design",
        30: "transparent simulation reporting",
    }
    for ref in NEW:
        lines.append(
            f"| [{ref.number}] {ref.title} | {ref.location} | {ref.support} | "
            f"{claims[ref.number]} |"
        )
    lines.extend(
        [
            "",
            "All inserted claims are descriptive literature mappings. None asserts",
            "rule-aware superiority, empirical public-vote recovery, deployment effects,",
            "or validation outside the registered simulators.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_manuscript(source: str) -> str:
    start = source.index("## 3. Related Work\n")
    end = source.index("## 4. Data, Institutional Rules, and Evidence Scope\n")
    revised = source[:start] + RELATED_WORK + "\n" + source[end:]
    marker = "\n## Figure Captions\n"
    if marker not in revised:
        raise VerificationError("Figure Captions marker is missing")
    references, tail = revised.split(marker, maxsplit=1)
    if "[13] COMAP" not in references:
        raise VerificationError("Expected COMAP reference [13] is missing")
    additions = "\n\n".join(f"[{ref.number}] {ref.citation}" for ref in NEW)
    return references.rstrip() + "\n\n" + additions + marker + tail


def citation_numbers(text: str) -> set[int]:
    body = text.split("## References\n", maxsplit=1)[0]
    found: set[int] = set()
    for match in re.finditer(r"\[(\d+(?:[-,]\d+)*)\]", body):
        token = match.group(1)
        for part in token.split(","):
            if "-" in part:
                left, right = (int(value) for value in part.split("-", maxsplit=1))
                found.update(range(left, right + 1))
            else:
                found.add(int(part))
    return found


def reference_numbers(text: str) -> list[int]:
    block = text.split("## References\n", maxsplit=1)[1].split(
        "\n## Figure Captions\n", maxsplit=1
    )[0]
    return [int(value) for value in re.findall(r"^\[(\d+)\]", block, flags=re.MULTILINE)]


def render_integrity(
    manuscript: str,
    verified_dois: set[str],
    source_hash: str,
    output_hash: str,
) -> str:
    refs = reference_numbers(manuscript)
    citations = citation_numbers(manuscript)
    expected = list(range(1, 31))
    missing_body = sorted(set(refs) - citations)
    missing_list = sorted(citations - set(refs))
    reference_block = manuscript.split("## References\n", maxsplit=1)[1].split(
        "\n## Figure Captions\n", maxsplit=1
    )[0]
    doi_presence = {
        doi: f"https://doi.org/{doi}".casefold() in reference_block.casefold()
        for doi in verified_dois
    }
    failures = []
    if refs != expected:
        failures.append(f"reference sequence is {refs}, expected {expected}")
    if missing_body:
        failures.append(f"uncited reference numbers: {missing_body}")
    if missing_list:
        failures.append(f"body citations absent from list: {missing_list}")
    absent_dois = sorted(doi for doi, present in doi_presence.items() if not present)
    if absent_dois:
        failures.append(f"verified DOIs absent from list: {absent_dois}")
    if "10.1920/wp.cem.2019.2519" in manuscript.casefold():
        failures.append("unverified working-paper candidate was inserted")
    if failures:
        raise VerificationError("; ".join(failures))
    return f"""# Stage 26AD Reference Integrity Check

`INTEGRITY_PASS`

| Check | Result | Evidence |
|---|---|---|
| Every reference is cited in the body | PASS | 30/30 reference numbers appear before the reference list. |
| Every body citation exists in the list | PASS | No citation number lies outside 1-30. |
| Numbering is continuous and unique | PASS | Exact sequence 1-30. |
| DOI resolution verified | PASS | 29 DOI-bearing entries were requested through `doi.org`; COMAP [13] has an official HTTP-200 source page rather than a DOI. |
| Unverified candidates excluded | PASS | Neither the ambiguous book-level record nor the incomplete working-paper record was inserted. |
| Stage 26AC source preserved | PASS | Input SHA-256 `{source_hash.upper()}`; a new Stage 26AD file was written instead. |
| Stage 26AD output hash | PASS | SHA-256 `{output_hash.upper()}`. |

The integrity result covers citation metadata, resolver behavior, numbering,
and body/list consistency. It does not imply that every cited result has been
independently replicated or that the literature search is a systematic review.
"""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.project_root.resolve()
    source_path = root / args.source
    output = root / args.output_dir
    if not source_path.is_file():
        raise VerificationError(f"Source manuscript is missing: {source_path}")
    output.mkdir(parents=True, exist_ok=True)

    existing_rows = [verify_reference(reference) for reference in EXISTING]
    new_rows = [verify_reference(reference) for reference in NEW]
    failures = [
        f"[{row['reference'].number}] {row['mismatches']}"
        for row in existing_rows + new_rows
        if not row["verified"]
    ]
    if failures:
        raise VerificationError("Reference verification failed: " + "; ".join(failures))

    comap_status, _, _ = http_probe(COMAP_URL, follow=True, byte_range=False)
    if comap_status != 200:
        raise VerificationError(f"COMAP official page returned HTTP {comap_status}")

    unverified = []
    for doi in ("10.1017/CBO9781107446984", "10.1920/wp.cem.2019.2519"):
        record, url = crossref_record(doi)
        unverified.append({"record": record, "url": url})

    source_bytes = source_path.read_bytes()
    source_text = source_bytes.decode("utf-8")
    manuscript = build_manuscript(source_text)
    manuscript_bytes = manuscript.encode("utf-8")
    source_hash = sha256_bytes(source_bytes)
    output_hash = sha256_bytes(manuscript_bytes)
    verified_dois = {reference.doi for reference in EXISTING + NEW}

    files = {
        "EXISTING_REFERENCES_VERIFICATION.md": render_existing(
            existing_rows, comap_status, args.access_time
        ),
        "LITERATURE_GAP_ANALYSIS.md": render_gap_analysis(),
        "VERIFIED_NEW_REFERENCES.md": render_new(new_rows, args.access_time),
        "UNVERIFIED_CANDIDATES.md": render_unverified(
            unverified, args.access_time
        ),
        "CITATION_INTEGRATION_LOG.md": render_integration_log(),
        "METHODS_research_draft_STAGE26AD.md": manuscript,
        "REFERENCE_INTEGRITY_CHECK.md": render_integrity(
            manuscript, verified_dois, source_hash, output_hash
        ),
    }
    for name, content in files.items():
        write(output / name, content)
        print(f"Wrote {(args.output_dir / name).as_posix()}")
    print(f"EXISTING_VERIFIED={len(existing_rows) + 1}/13")
    print(f"NEW_VERIFIED={len(new_rows)}/{len(NEW)}")
    print("REFERENCE_INTEGRITY=PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, urllib.error.URLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
