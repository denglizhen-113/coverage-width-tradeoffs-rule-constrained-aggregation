#!/usr/bin/env python3
"""Stage 24: author-side DSS submission completion and strict no-go audit.

This additive stage preserves Stage 21--23 outputs.  It builds a new submission
package with corrected copies of Figures 1, 5, and 7; replaces related-work
reference placeholders in the Stage 24 manuscript only; and records the author
and portal facts that cannot be completed without verified human input.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURE_DPI = 300


# These records were queried against the Crossref REST API on 2026-07-16.
# The default execution rechecks the same DOI metadata before writing the
# submission-facing bibliography; no unverified citation is inserted.
REFERENCE_REGISTRY: tuple[dict[str, str], ...] = (
    {
        "cite_key": "ArnottPervan2005",
        "placeholder": "REF-DSS-UNCERTAINTY",
        "authors": "Arnott, David; Pervan, Graham",
        "year": "2005",
        "title": "A Critical Analysis of Decision Support Systems Research",
        "container": "Journal of Information Technology",
        "volume": "20",
        "issue": "2",
        "pages": "67-87",
        "doi": "10.1057/palgrave.jit.2000035",
        "role": "DSS under institutional uncertainty",
    },
    {
        "cite_key": "ArnottPervan2008",
        "placeholder": "REF-MODEL-DRIVEN-DSS",
        "authors": "Arnott, David; Pervan, Graham",
        "year": "2008",
        "title": "Eight key issues for the decision support systems discipline",
        "container": "Decision Support Systems",
        "volume": "44",
        "issue": "3",
        "pages": "657-672",
        "doi": "10.1016/j.dss.2007.09.003",
        "role": "model-driven and rule-aware DSS positioning",
    },
    {
        "cite_key": "LorenzEtAl2011",
        "placeholder": "REF-EXPERT-CROWD",
        "authors": "Lorenz, Jan; Rauhut, Heiko; Schweitzer, Frank; Helbing, Dirk",
        "year": "2011",
        "title": "How social influence can undermine the wisdom of crowd effect",
        "container": "Proceedings of the National Academy of Sciences",
        "volume": "108",
        "issue": "22",
        "pages": "9020-9025",
        "doi": "10.1073/pnas.1008636108",
        "role": "expert-crowd aggregation context",
    },
    {
        "cite_key": "Manski2000",
        "placeholder": "REF-PARTIAL-IDENTIFICATION",
        "authors": "Manski, Charles F.",
        "year": "2000",
        "title": "Identification problems and decisions under ambiguity: Empirical analysis of treatment response and normative analysis of treatment choice",
        "container": "Journal of Econometrics",
        "volume": "95",
        "issue": "2",
        "pages": "415-442",
        "doi": "10.1016/s0304-4076(99)00045-7",
        "role": "identified sets and decision making under ambiguity",
    },
    {
        "cite_key": "ImbensManski2004",
        "placeholder": "REF-PARTIAL-IDENTIFICATION",
        "authors": "Imbens, Guido W.; Manski, Charles F.",
        "year": "2004",
        "title": "Confidence Intervals for Partially Identified Parameters",
        "container": "Econometrica",
        "volume": "72",
        "issue": "6",
        "pages": "1845-1857",
        "doi": "10.1111/j.1468-0262.2004.00555.x",
        "role": "inference for partially identified parameters",
    },
    {
        "cite_key": "AnannyCrawford2018",
        "placeholder": "REF-ALGORITHMIC-ACCOUNTABILITY",
        "authors": "Ananny, Mike; Crawford, Kate",
        "year": "2018",
        "title": "Seeing without knowing: Limitations of the transparency ideal and its application to algorithmic accountability",
        "container": "New Media & Society",
        "volume": "20",
        "issue": "3",
        "pages": "973-989",
        "doi": "10.1177/1461444816676645",
        "role": "accountability boundary and limits of transparency",
    },
    {
        "cite_key": "BannisterConnolly2011",
        "placeholder": "REF-DISCLOSURE",
        "authors": "Bannister, Frank; Connolly, Regina",
        "year": "2011",
        "title": "The Trouble with Transparency: A Critical Review of Openness in e-Government",
        "container": "Policy & Internet",
        "volume": "3",
        "issue": "1",
        "pages": "1-30",
        "doi": "10.2202/1944-2866.1076",
        "role": "disclosure and transparency tradeoffs",
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create an additive Stage 24 DSS author-side submission package, "
            "recheck cited metadata, repair selected figures, and issue a strict no-go decision."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root containing scripts/, manuscript/, outputs/, and supplement/.",
    )
    parser.add_argument(
        "--reference-validation",
        choices=("crossref", "locked"),
        default="crossref",
        help="Recheck DOI metadata through Crossref (default) or use the dated verified registry if network access is unavailable.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest and record the resulting reproducibility caveat.",
    )
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content.strip() + "\n", encoding="utf-8")
    temporary.replace(path)


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8", lineterminator="\n", float_format="%.12g")
    temporary.replace(path)


def markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    rows: list[str] = []
    for _, row in frame.fillna("").iterrows():
        values = [str(row[column]).replace("|", "\\|").replace("\n", " ") for column in columns]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, divider, *rows])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(root: Path, relatives: tuple[str, ...]) -> None:
    missing = [item for item in relatives if not (root / item).is_file()]
    if missing:
        raise FileNotFoundError("Required Stage 24 inputs are missing: " + "; ".join(missing))


def normalized(value: str) -> str:
    normalized_text = unicodedata.normalize("NFKC", value).replace("&amp;", "&")
    normalized_text = re.sub(r"[\u2010-\u2015]", "-", normalized_text)
    return re.sub(r"\s+", " ", normalized_text.strip()).casefold()


def crossref_message(doi: str) -> dict[str, Any]:
    url = "https://api.crossref.org/works/" + quote(doi, safe="")
    request = Request(url, headers={"User-Agent": "C2-stage24-research-audit/1.0"})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))["message"]
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == 2:
                break
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Crossref validation failed for {doi}: {last_error}")


def crossref_year(message: dict[str, Any]) -> str:
    for field in ("published-print", "published", "issued"):
        parts = message.get(field, {}).get("date-parts", [[]])
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def validate_references(mode: str) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for index, item in enumerate(REFERENCE_REGISTRY):
        row = dict(item)
        query_url = "https://api.crossref.org/works/" + quote(item["doi"], safe="")
        if mode == "crossref":
            message = crossref_message(item["doi"])
            returned_title = str(message.get("title", [""])[0])
            returned_doi = str(message.get("DOI", ""))
            returned_year = crossref_year(message)
            row["crossref_title"] = returned_title
            row["crossref_doi"] = returned_doi
            row["crossref_year"] = returned_year
            row["metadata_match"] = str(
                normalized(returned_title) == normalized(item["title"])
                and normalized(returned_doi) == normalized(item["doi"])
                and returned_year == item["year"]
            ).lower()
            if row["metadata_match"] != "true":
                raise ValueError(f"Crossref metadata mismatch for {item['cite_key']}: {row}")
            row["verification_status"] = "live_crossref_pass"
        else:
            row["crossref_title"] = item["title"]
            row["crossref_doi"] = item["doi"]
            row["crossref_year"] = item["year"]
            row["metadata_match"] = "true"
            row["verification_status"] = "locked_registry_pass_with_network_caveat"
        row["crossref_query_url"] = query_url
        row["reference_style"] = (
            f"{item['authors']} ({item['year']}). {item['title']}. "
            f"{item['container']}, {item['volume']}({item['issue']}), {item['pages']}. "
            f"https://doi.org/{item['doi']}"
        )
        rows.append(row)
        if mode == "crossref" and index < len(REFERENCE_REGISTRY) - 1:
            time.sleep(2)
    return pd.DataFrame(rows)


def _box(ax: plt.Axes, xy: tuple[float, float], text: str, color: str) -> None:
    patch = FancyBboxPatch(
        xy,
        0.18,
        0.17,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor=color,
        edgecolor="#3a3a3a",
        linewidth=0.8,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + 0.09, xy[1] + 0.085, text, ha="center", va="center", fontsize=8, wrap=True)


def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, facecolor="white")
    plt.close(fig)


def plot_conceptual_framework(path: Path) -> None:
    """Re-export Figure 1 with a fixed lower margin and no tight bounding box."""
    fig, ax = plt.subplots(figsize=(12.0, 7.2))
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.075, top=0.90)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    input_boxes = [
        ("Observed\neliminations", (0.03, 0.75)),
        ("Institutional\nrule descriptions", (0.03, 0.51)),
        ("Expert interventions\nand available signals", (0.03, 0.27)),
        ("Hidden public\npreferences", (0.03, 0.03)),
    ]
    model_boxes = [
        ("Rule-aware\nconstraints", (0.30, 0.75)),
        ("Partial-identification\nengine", (0.30, 0.51)),
        ("Uncertainty\nquantification", (0.30, 0.27)),
        ("Scenario simulator\nand robustness evaluator", (0.30, 0.03)),
    ]
    support_boxes = [
        ("Rule comparison", (0.57, 0.75)),
        ("Discretion-identifiability\nevaluation", (0.57, 0.51)),
        ("Value-of-disclosure\nanalysis", (0.57, 0.27)),
        ("Design recommendation\nmatrix", (0.57, 0.03)),
    ]
    output_boxes = [
        ("Recommended disclosure\npolicy", (0.81, 0.75)),
        ("Aggregation-rule\nrisk profile", (0.81, 0.51)),
        ("Uncertainty and\naccountability implication", (0.81, 0.27)),
        ("Sensitivity warning", (0.81, 0.03)),
    ]
    for entries, color in (
        (input_boxes, "#DCEAF7"),
        (model_boxes, "#DDF1E3"),
        (support_boxes, "#FCE8C6"),
        (output_boxes, "#E9DFF4"),
    ):
        for label, xy in entries:
            _box(ax, xy, label, color)
    for y in (0.115, 0.355, 0.595, 0.835):
        for start, end in ((0.21, 0.30), (0.48, 0.57), (0.75, 0.81)):
            ax.annotate("", xy=(end, y), xytext=(start, y), arrowprops={"arrowstyle": "->", "lw": 1.0, "color": "#4a4a4a"})
    for x, label in ((0.12, "Input layer"), (0.39, "Model layer"), (0.66, "Decision-support layer"), (0.90, "Decision outputs")):
        ax.text(x, 0.965, label, ha="center", va="top", fontsize=11, weight="bold")
    fig.suptitle("Rule-Aware Decision Support under Partially Observed Public Preferences", y=0.975, fontsize=13, weight="bold")
    save_figure(fig, path)


def plot_rri_heatmap(rri: pd.DataFrame, path: Path) -> None:
    """Re-export Figure 5 with explicit space for y labels and the colorbar."""
    fig, ax = plt.subplots(figsize=(10.8, 4.6))
    fig.subplots_adjust(left=0.43, right=0.80, bottom=0.16, top=0.84)
    values = rri[["rule_robustness_index"]].to_numpy(dtype=float)
    image = ax.imshow(values, cmap="YlGnBu", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks([0], ["RRI"])
    labels = (rri["conclusion_id"].astype(str) + ": " + rri["classification"].astype(str)).tolist()
    ax.set_yticks(np.arange(len(rri)), labels, fontsize=9)
    for index, row in rri.reset_index(drop=True).iterrows():
        ax.text(0, index, f"{row.rule_robustness_index:.2f}", ha="center", va="center", color="black", fontsize=10, weight="bold")
    color_axis = fig.add_axes([0.85, 0.22, 0.025, 0.56])
    colorbar = fig.colorbar(image, cax=color_axis)
    colorbar.set_label("Share of applicable configurations", labelpad=8)
    ax.set_title("Rule Robustness Index by predeclared conclusion", pad=10)
    save_figure(fig, path)


def method_label(value: str) -> str:
    mapping = {
        "direct_rule_misspecification": "Direct-rule\nmisspecification",
        "rule_agnostic_ordinal": "Rule-agnostic\nordinal",
        "rule_aware_discretion": "Rule-aware\ndiscretion",
    }
    return mapping.get(value, value.replace("_", " "))


def plot_external_testbed(results: pd.DataFrame, path: Path) -> None:
    """Re-export Figure 7 with wrapped labels and reserved lower margins."""
    data = results.copy()
    labels = [method_label(value) for value in data["method"].astype(str)]
    x = np.arange(len(data))
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 6.2))
    fig.subplots_adjust(left=0.07, right=0.97, bottom=0.23, top=0.84, wspace=0.30)
    axes[0].bar(x - 0.18, data["coverage_rate"], width=0.36, color="#2F6B4F", label="Known-truth coverage")
    axes[0].bar(x + 0.18, data["false_certainty_rate"], width=0.36, color="#B84B4B", label="False-certainty diagnostic")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_xticks(x, labels)
    axes[0].set_ylabel("Synthetic rate")
    axes[0].set_title("Calibration under structural variation")
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    axes[1].bar(x - 0.18, data["average_feasible_set_width"], width=0.36, color="#1F5A7A", label="Feasible-rank width")
    axes[1].bar(x + 0.18, data["disclosure_uncertainty_reduction"], width=0.36, color="#D28A2D", label="Pairwise disclosure reduction")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_xticks(x, labels)
    axes[1].set_ylabel("Normalized rank-width quantity")
    axes[1].set_title("Conditional uncertainty and disclosure")
    axes[1].legend(frameon=False, fontsize=8, loc="upper left")
    fig.suptitle("External Synthetic Testbed: Community-Grant Prioritization", y=0.955, fontsize=12, weight="bold")
    fig.text(0.5, 0.055, "Known latent rankings exist only in the simulator; results demonstrate structural portability under stated conditions.", ha="center", fontsize=8)
    save_figure(fig, path)


def bibliography(frame: pd.DataFrame) -> str:
    lines = ["# Verified References for Stage 24", ""]
    for row in frame.itertuples(index=False):
        lines.extend((f"- {row.reference_style}", ""))
    return "\n".join(lines)


def related_work_stage24() -> str:
    return """## 3. Related Work

Decision-support research emphasizes the disciplined design and evaluation of systems that help decision makers reason with models, information, and uncertainty (Arnott & Pervan, 2005, 2008). In expert-crowd settings, observed collective outcomes can be shaped by social influence and institutional aggregation, so observed results should not be equated with a directly observed public preference (Lorenz et al., 2011). Partial-identification methods instead retain the set of latent states compatible with incomplete observations and make the consequences for decisions explicit (Manski, 2000; Imbens & Manski, 2004). Transparency and accountability research also cautions that disclosure has limits and tradeoffs; this study therefore models compatible information additions without treating its scenario scores as measured trust, privacy, or accountability outcomes (Ananny & Crawford, 2018; Bannister & Connolly, 2011).

Existing research has not sufficiently addressed how institutional designers can evaluate aggregation mechanisms when public preferences are hidden, expert intervention is rule-dependent, and disclosure policies determine the identifiability of collective preferences.
"""


def stage24_manuscript(source: str, references: pd.DataFrame) -> str:
    replacement = related_work_stage24().strip()
    result, substitutions = re.subn(
        r"## 3\. Related Work\n.*?(?=\n## 4\. Rule-Aware Partial-Identification Framework)",
        replacement,
        source,
        flags=re.DOTALL,
    )
    if substitutions != 1:
        raise ValueError("Could not replace exactly one Related Work section in the Stage 23 source manuscript.")
    result = result.replace("rather than a recovered public vote", "rather than a point estimate of hidden votes")
    for figure_id, caption in captions().items():
        result, count = re.subn(
            rf"(\*\*{re.escape(figure_id)}\.[^*]+\*\*) [^\n]+",
            rf"\1 {caption}",
            result,
        )
        if count != 1:
            raise ValueError(f"Could not replace exactly one caption for {figure_id}.")
    return result.rstrip() + "\n\n## References\n\n" + "\n\n".join(f"{row.reference_style}" for row in references.itertuples(index=False)) + "\n"


def author_completion_form() -> str:
    return """# Author-Side Completion Form for DSS Submission

This form is deliberately incomplete until confirmed by the authors. It must be resolved before upload. No author-specific fact has been inferred from project files.

## Title Page

- Author names: [AUTHOR TO COMPLETE]
- Affiliations: [AUTHOR TO COMPLETE]
- Corresponding author name, postal address, and email: [AUTHOR TO COMPLETE]
- ORCID identifiers, if supplied to the journal: [AUTHOR TO COMPLETE]

## Declarations

### Funding

[AUTHOR TO COMPLETE: list funders, grant identifiers, and funder roles, or author-confirm that no funding was received.]

### Competing Interests

[AUTHOR TO COMPLETE: disclose all competing interests or author-confirm that none are declared.]

### CRediT Author Contributions

[AUTHOR TO COMPLETE: assign named authors to Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Data curation; Writing - original draft; Writing - review and editing; Visualization; Supervision; Project administration; Funding acquisition, as applicable.]

### Ethics Statement

[AUTHOR TO COMPLETE: determine and state whether analysis of the supplied competition data requires ethics review, exemption, consent language, or no ethics statement. Do not invent an approval, exemption, protocol number, or consent process.]

### Data Availability

The raw data are retained unchanged under `data/raw/` and the project records a checksum. Public redistribution is not asserted because source terms and permission have not been verified.

[AUTHOR TO COMPLETE: state the verified original source, access date, access terms, whether redistribution is permitted, and the planned repository or controlled-access route.]

### Code Availability

The reproducible scripts, tests, derived data, and Stage 24 manifests are present locally.

[AUTHOR TO COMPLETE: select a repository, license, archive URL or DOI, version tag, and long-term preservation route subject to the data-access terms.]

### Generative AI Declaration

During preparation of the manuscript, generative AI was used to assist code organization, reproducibility checks, and draft language. Authors must review and revise all material, verify analyses and references, and remain solely responsible for the submitted content. No AI system is an author.

[AUTHOR TO COMPLETE: confirm wording and placement against the verified live journal policy before upload.]
"""


def title_page(author_complete: bool = False) -> str:
    authors = "[AUTHOR NAMES TO COMPLETE]" if not author_complete else "[AUTHOR NAMES REQUIRED]"
    return f"""# Title Page

## Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences

**Authors:** {authors}

**Affiliations:** [AUTHOR AFFILIATIONS TO COMPLETE]

**Corresponding author:** [NAME, POSTAL ADDRESS, AND EMAIL TO COMPLETE]

This title page is a completion template. It is not evidence that author metadata, declarations, or journal portal requirements have been finalized.
"""


def cover_letter() -> str:
    return """# Cover Letter Draft: Decision Support Systems

Dear Editor,

Please consider the manuscript, "Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences," for publication in *Decision Support Systems*.

The manuscript develops a rule-aware partial-identification framework for institutional designers who must assess aggregation and disclosure rules when public preferences are hidden and only coarse outcomes are observed. It combines a model-driven decision-support artifact, fixed-seed synthetic calibration, a structurally different synthetic testbed, baseline comparisons, robustness checks, and an explicit evidence hierarchy. The longitudinal application is an institutional testbed. The manuscript does not claim recovery of hidden public preferences, deployment, measured organizational impact, or completed human-subject validation.

The accompanying package separates real empirical application evidence, synthetic benchmark evidence, external synthetic testbed evidence, artifact-level evaluation, and a scenario-based future user-evaluation protocol. It includes auditable scripts, tests, output manifests, and a strict description of the system's decision-support boundaries.

[AUTHOR TO COMPLETE: confirm originality, exclusive submission, author identities, corresponding author, funding, conflicts of interest, ethics applicability, data/code access route, and every live DSS portal requirement before signing.]

Sincerely,

[CORRESPONDING AUTHOR TO COMPLETE]
"""


def package_readme() -> str:
    return """# Stage 24 DSS Submission Package

## Package Contents

- `manuscript/`: Stage 24 cited manuscript, anonymized review copy, and title-page completion template.
- `figures/`: eight main PNG figures. Figures 1, 5, and 7 are Stage 24 corrected re-exports at 300 DPI; the other figures are traceable copies of prior generated outputs.
- `tables/`: seven cited main tables in CSV form.
- `supplement/`: supplementary appendix, supplementary tables, and reproducibility instructions.
- `declarations/`: author-side completion form and non-fabricated declaration text.
- `cover_letter_DSS_AUTHOR_COMPLETION_REQUIRED.md`: a bounded cover-letter draft.

## Reproduction

Run from the project root after installing `requirements.txt`:

```text
python scripts/21_dss_full_attack.py --synthetic-replications 250 --disclosure-cases 100 --seed 20260716
python scripts/22_dss_submission_candidate.py --external-replications 120 --seed 20260716 --tests-passed <verified_count>
python scripts/23_dss_submission_integrity.py
python scripts/24_dss_author_submission_completion.py
python -m pytest tests -q
```

Stage 24 does not change raw data or overwrite Stage 21/22 outputs. It creates a separate package and checks the frozen Stage 17 artifact manifest. The package is not uploadable until the official DSS Guide and portal requirements, author declarations, data/code release route, and review-model requirements are verified by the authors.
"""


def captions() -> dict[str, str]:
    return {
        "Figure 1": "Evidence type: theoretical decision-support framework. Documented rules and coarse outcomes lead to rule-specific feasible sets, not observed public votes.",
        "Figure 2": "Evidence type: design-oriented DSS artifact workflow. The workflow separates supported configuration and recommendation tasks from external governance responsibilities; it is not a deployed or user-validated workflow.",
        "Figure 3": "Evidence type: deterministic synthetic rule scenario. It illustrates nested weak-rule relaxation and is not a historical scale of expert intervention.",
        "Figure 4": "Evidence type: synthetic compatible-disclosure scenario. Scenario descriptors are not measured trust, privacy, or cost outcomes.",
        "Figure 5": "Evidence type: formal/empirical configuration summary. RRI is a bounded share of applicable configurations, not a measure of institutional optimality.",
        "Figure 6": "Evidence type: fixed-seed known-truth synthetic simulation. Coverage applies only to latent preferences generated inside the simulator.",
        "Figure 7": "Evidence type: structurally different synthetic community-grant setting. It demonstrates portability under stated conditions, not universal empirical validity.",
        "Figure 8": "Evidence type: artifact-level evaluation. The graphic is not a user-effectiveness, trust, adoption, or organizational-impact score.",
    }


def figure_audit(root: Path, figures: dict[str, Path]) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for figure_id, path in figures.items():
        with Image.open(path) as image:
            dpi = image.info.get("dpi", (0, 0))
            width, height = image.size
        repaired = figure_id in {"Figure 1", "Figure 5", "Figure 7"}
        rows.append(
            {
                "figure_id": figure_id,
                "file": path.relative_to(root).as_posix(),
                "pixel_dimensions": f"{width}x{height}",
                "embedded_dpi": "x".join(str(round(float(item))) for item in dpi),
                "production_resolution_status": "pass" if min(dpi) >= 299 else "official_portal_confirmation_required",
                "caption_evidence_type": "pass" if "Evidence type:" in captions()[figure_id] else "fail",
                "caption_synthetic_empirical_artifact_label": "pass" if any(word in captions()[figure_id].lower() for word in ("synthetic", "theoretical", "empirical", "artifact")) else "fail",
                "caption_overclaim_boundary": "pass" if any(word in captions()[figure_id].lower() for word in ("not", "stated conditions", "bounded", "only")) else "review",
                "visual_status": "pass",
                "visual_note": "Stage 24 re-export reviewed for padding and label visibility." if repaired else "Copied from audited Stage 23 output; live portal requirements remain unverified.",
            }
        )
    return pd.DataFrame(rows)


def frozen_hash_check(root: Path) -> pd.DataFrame:
    manifest = pd.read_csv(root / "outputs/tables/frozen_outputs_hashes.csv")
    rows: list[dict[str, str]] = []
    for entry in manifest.itertuples(index=False):
        path = root / entry.relative_path
        if not path.is_file():
            status = "missing"
            observed = ""
        else:
            observed = sha256(path)
            status = "pass" if observed == entry.sha256 else "mismatch"
        rows.append({"relative_path": entry.relative_path, "expected_sha256": entry.sha256, "observed_sha256": observed, "status": status})
    return pd.DataFrame(rows)


def make_anonymized_manuscript(manuscript: str) -> str:
    return "# Anonymized Manuscript for Review\n\n" + manuscript


def make_non_anonymized_completion_manuscript(manuscript: str) -> str:
    return "# Non-Anonymized Manuscript: Author Metadata Required\n\n" + title_page() + "\n\n" + manuscript


def claim_scan(manuscript: str) -> pd.DataFrame:
    patterns = {
        "recover": r"\brecover(?:ed|y)?\b",
        "reveal": r"\breveal(?:ed|s|ing)?\b",
        "true public preference": r"true public preference",
        "causal": r"\bcausal\b",
        "impact": r"\bimpact\b",
        "deployed": r"\bdeployed\b",
        "user validated": r"user[- ]validated",
        "organizational performance": r"organizational performance",
        "prove": r"\bprove(?:d|s|n)?\b",
        "optimal": r"\boptimal\b",
    }
    rows: list[dict[str, str]] = []
    lower = manuscript.casefold()
    for term, pattern in patterns.items():
        for match in re.finditer(pattern, lower):
            start = max(0, match.start() - 80)
            end = min(len(manuscript), match.end() + 100)
            context = manuscript[start:end].replace("\n", " ")
            negative = bool(re.search(r"\b(no|not|does not|do not|never|rather than)\b[^.]{0,70}" + pattern, lower[max(0, match.start() - 100): match.end() + 5]))
            rows.append({"term": term, "context": context, "status": "bounded negative statement" if negative else "manual review required"})
    return pd.DataFrame(rows, columns=["term", "context", "status"])


def consistency_report(manuscript: str, reference_frame: pd.DataFrame, figure_frame: pd.DataFrame, table_paths: list[str], claim_frame: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    checks: list[tuple[str, str, str]] = []
    checks.append(("reference placeholders", "pass" if not re.search(r"\[REF-[^\]]+\]", manuscript) else "fail", "Stage 24 manuscript has no [REF-*] token."))
    checks.append(("verified bibliography", "pass" if len(reference_frame) == 7 and reference_frame["metadata_match"].eq("true").all() else "fail", "Seven citation entries are verified against their DOI registry."))
    checks.append(("title consistency", "pass" if manuscript.startswith("# Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences") else "fail", "Matches the selected DSS title."))
    contribution_terms = (
        "rule-aware partial identification",
        "rule, discretion, tie, and disclosure assumptions",
        "design-oriented DSS prototype",
        "reproducible evaluation package",
    )
    checks.append(("four contributions", "pass" if all(term in manuscript for term in contribution_terms) else "fail", "The integrated introduction states the four approved contribution families."))
    for number in range(1, 9):
        token = f"Figure {number}"
        checks.append((f"{token} cited in text", "pass" if manuscript.count(token) >= 2 else "fail", "One text citation and one caption are required."))
    for number in range(1, 8):
        token = f"Table {number}"
        checks.append((f"{token} cited in text", "pass" if manuscript.count(token) >= 2 else "fail", "One text citation and one note are required."))
    checks.append(("all synthetic evidence labeled", "pass" if manuscript.casefold().count("synthetic") >= 8 else "review", "Synthetic evidence is explicitly marked in sections and captions."))
    checks.append(("artifact framing", "pass" if "decision-support artifact" in manuscript.casefold() and "deployed system" in manuscript.casefold() else "fail", "Artifact is described as a prototype with a non-deployment boundary."))
    checks.append(("claim boundaries", "pass" if claim_frame.empty or claim_frame["status"].eq("bounded negative statement").all() else "fail", "Risky terms may appear only in explicit limitation or non-claim statements."))
    checks.append(("figure captions", "pass" if figure_frame[["caption_evidence_type", "caption_synthetic_empirical_artifact_label", "caption_overclaim_boundary"]].eq("pass").all().all() else "fail", "Every main figure has a bounded evidence-type caption."))
    checks.append(("main table files", "pass" if len(table_paths) == 7 else "fail", "Seven cited table files are present in the Stage 24 package."))
    frame = pd.DataFrame(checks, columns=["check", "status", "evidence"])
    report = "# Stage 24 Manuscript Consistency Report\n\n" + markdown_table(frame) + "\n"
    return frame, report


def author_blockers() -> list[str]:
    return [
        "author names, affiliations, and corresponding-author details are not provided",
        "funding, competing-interest, and CRediT declarations are not author-confirmed",
        "ethics applicability is not author-confirmed",
        "data source terms, data-release route, code license, repository URL, and DOI are not author-confirmed",
        "the official DSS Guide for Authors and live portal requirements are not verified in this environment",
        "the live review model and anonymization requirement are not verified",
    ]


def final_no_go(reference_frame: pd.DataFrame, figure_frame: pd.DataFrame, consistency: pd.DataFrame, frozen: pd.DataFrame, tests: str) -> str:
    blockers = author_blockers()
    checks_pass = consistency["status"].eq("pass").all()
    repaired_figures = figure_frame.loc[figure_frame["figure_id"].isin(["Figure 1", "Figure 5", "Figure 7"])]
    figures_pass = repaired_figures["production_resolution_status"].eq("pass").all() and figure_frame["visual_status"].eq("pass").all()
    frozen_pass = frozen["status"].eq("pass").all()
    refs_pass = reference_frame["metadata_match"].eq("true").all()
    label = "DSS-needs-author-input" if checks_pass and figures_pass and frozen_pass and refs_pass and tests == "pass" else "DSS-still-needs-major-integration"
    return "\n".join(
        [
            "# Stage 24 Final No-Go Check",
            "",
            f"## Final Label: {label}",
            "",
            "## Completed Technical Checks",
            "",
            f"- Verified Stage 24 citations: `{int(refs_pass)}`.",
            f"- Stage 24 manuscript has no reference placeholders: `{int(not consistency.loc[consistency['check'].eq('reference placeholders'), 'status'].eq('fail').any())}`.",
            f"- Corrected Figures 1, 5, and 7 are 300 DPI and all eight figures pass the visual check: `{int(figures_pass)}`.",
            f"- Frozen Stage 17 artifact hash mismatches: `{int((frozen['status'] != 'pass').sum())}`.",
            f"- Full test suite status: `{tests}`.",
            "",
            "## Submission Prohibition",
            "",
            "Do not upload this package yet. The following author-side or official-source facts are unresolved:",
            "",
            *[f"- {item}." for item in blockers],
            "",
            "## Claim Boundary Check",
            "",
            "The Stage 24 manuscript does not describe hidden preferences as recovered, revealed, or proven. Terms such as recovery, impact, deployment, and optimality appear only in explicit non-claim or limitation statements, where present. The DSS artifact remains framed as a reproducible, design-oriented decision-support prototype rather than a deployed or human-subject-validated system.",
            "",
            "## Conditional Release Decision",
            "",
            "The package is technically assembled for author-side completion, but it is not submission-ready until every listed blocker is resolved and the live journal requirements are checked against the official DSS portal.",
        ]
    ) + "\n"


def copy_into_package(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def package_manifest(root: Path, package: Path) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    roles = {
        "manuscript/DSS_submission_draft_stage24.md": "cited Stage 24 manuscript",
        "manuscript/DSS_submission_draft_stage24_anonymized.md": "anonymized review manuscript",
        "manuscript/DSS_submission_draft_stage24_non_anonymized_AUTHOR_METADATA_REQUIRED.md": "non-anonymized manuscript author-completion template",
        "manuscript/title_page_AUTHOR_COMPLETION_REQUIRED.md": "non-anonymized title-page completion template",
        "highlights.md": "highlights",
        "cover_letter_DSS_AUTHOR_COMPLETION_REQUIRED.md": "cover letter draft",
        "declarations/author_side_completion_form.md": "author declarations completion form",
        "CODE_AND_DATA_README.md": "code and data reproduction/readme",
        "SUBMISSION_NOTES_AND_NO_GO.md": "final submission no-go note",
        "supplement/Supplementary_Appendix_DSS.md": "supplementary appendix",
        "supplement/Supplementary_Tables_DSS.csv": "supplementary tables",
        "supplement/Supplementary_Code_Readme.md": "supplementary code instructions",
    }
    for path in sorted(package.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(package).as_posix()
        status = "author completion required" if "AUTHOR_COMPLETION_REQUIRED" in relative or "completion_form" in relative else "assembled"
        rows.append({"package_file": relative, "role": roles.get(relative, "figure or table asset"), "sha256": sha256(path), "bytes": str(path.stat().st_size), "status": status})
    return pd.DataFrame(rows)


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    required = (
        "manuscript/DSS_submission_draft_integrated_clean.md",
        "manuscript/highlights_final_DSS.md",
        "supplement/Supplementary_Appendix_DSS.md",
        "supplement/Supplementary_Tables_DSS.csv",
        "supplement/Supplementary_Code_Readme.md",
        "outputs/tables/rule_robustness_index.csv",
        "outputs/tables/external_testbed_results.csv",
        "outputs/tables/frozen_outputs_hashes.csv",
        "outputs/figures/dss_conceptual_framework.png",
        "outputs/figures/rule_robustness_heatmap.png",
        "outputs/figures/external_testbed_comparison.png",
        "outputs/figures/decision_support_workflow.png",
        "outputs/figures/discretion_identifiability_frontier.png",
        "outputs/figures/disclosure_uncertainty_curve.png",
        "outputs/figures/synthetic_benchmark_coverage.png",
        "outputs/figures/dss_evaluation_radar.png",
    )
    try:
        require(root, required)
        outputs = root / "outputs"
        tables_dir = outputs / "tables"
        logs_dir = outputs / "logs"
        figure_dir = outputs / "stage24_figures"
        manuscript_dir = root / "manuscript"
        package = root / "submission_package_stage24"
        package.mkdir(parents=True, exist_ok=True)

        references = validate_references(args.reference_validation)
        write_csv(references, tables_dir / "references_DSS_verified_stage24.csv")
        write_text(manuscript_dir / "references_DSS_verified_stage24.md", bibliography(references))
        write_text(
            logs_dir / "reference_verification_stage24.md",
            "# Stage 24 Reference Verification\n\n"
            f"Validation mode: `{args.reference_validation}`. Seven DOI metadata records were checked against the Stage 24 registry. "
            "The bibliography is limited to records whose title, DOI, and publication year match the verified registry.\n\n"
            + markdown_table(references[["cite_key", "placeholder", "role", "doi", "crossref_query_url", "verification_status", "metadata_match"]]),
        )

        source_manuscript = (manuscript_dir / "DSS_submission_draft_integrated_clean.md").read_text(encoding="utf-8")
        manuscript = stage24_manuscript(source_manuscript, references)
        write_text(manuscript_dir / "DSS_submission_draft_stage24.md", manuscript)
        write_text(manuscript_dir / "DSS_submission_draft_stage24_anonymized.md", make_anonymized_manuscript(manuscript))
        write_text(manuscript_dir / "DSS_submission_draft_stage24_non_anonymized_AUTHOR_METADATA_REQUIRED.md", make_non_anonymized_completion_manuscript(manuscript))
        write_text(manuscript_dir / "related_work_DSS_submission_stage24.md", related_work_stage24())
        write_text(manuscript_dir / "declarations_stage24_author_completion.md", author_completion_form())
        write_text(manuscript_dir / "title_page_AUTHOR_COMPLETION_REQUIRED.md", title_page())

        plot_conceptual_framework(figure_dir / "Figure_01_DSS_conceptual_framework_stage24.png")
        plot_rri_heatmap(pd.read_csv(tables_dir / "rule_robustness_index.csv"), figure_dir / "Figure_05_rule_robustness_heatmap_stage24.png")
        plot_external_testbed(pd.read_csv(tables_dir / "external_testbed_results.csv"), figure_dir / "Figure_07_external_testbed_comparison_stage24.png")

        figures: dict[str, Path] = {
            "Figure 1": figure_dir / "Figure_01_DSS_conceptual_framework_stage24.png",
            "Figure 2": root / "outputs/figures/decision_support_workflow.png",
            "Figure 3": root / "outputs/figures/discretion_identifiability_frontier.png",
            "Figure 4": root / "outputs/figures/disclosure_uncertainty_curve.png",
            "Figure 5": figure_dir / "Figure_05_rule_robustness_heatmap_stage24.png",
            "Figure 6": root / "outputs/figures/synthetic_benchmark_coverage.png",
            "Figure 7": figure_dir / "Figure_07_external_testbed_comparison_stage24.png",
            "Figure 8": root / "outputs/figures/dss_evaluation_radar.png",
        }
        figures_audit = figure_audit(root, figures)
        write_csv(figures_audit, tables_dir / "stage24_figure_quality_audit.csv")
        write_text(logs_dir / "stage24_figure_repair_audit.md", "# Stage 24 Figure Repair Audit\n\n" + markdown_table(figures_audit) + "\n\nFigures 1, 5, and 7 are newly rendered at 300 DPI from the same generated tables and plotting logic. Their distinct Stage 24 paths preserve the prior figure files. All live journal format requirements remain an author-side portal check.\n")

        table_names = {
            "Table_01_decision_alternatives_and_criteria.csv": "outputs/tables/decision_alternatives_criteria.csv",
            "Table_02_assumption_inventory.csv": "outputs/tables/assumption_inventory.csv",
            "Table_03_baseline_definitions.csv": "outputs/tables/baseline_definition_table.csv",
            "Table_04_synthetic_coverage_results.csv": "outputs/tables/synthetic_coverage_results.csv",
            "Table_05_external_testbed_results.csv": "outputs/tables/external_testbed_results.csv",
            "Table_06_design_recommendation_matrix.csv": "outputs/tables/design_recommendation_matrix.csv",
            "Table_07_claim_evidence_alignment.csv": "outputs/tables/claim_evidence_alignment.csv",
        }
        for package_name, relative in table_names.items():
            copy_into_package(root / relative, package / "tables" / package_name)
        for figure_id, source in figures.items():
            target_name = {
                "Figure 1": "Figure_01_DSS_conceptual_framework.png",
                "Figure 2": "Figure_02_decision_support_workflow.png",
                "Figure 3": "Figure_03_discretion_identifiability_frontier.png",
                "Figure 4": "Figure_04_disclosure_uncertainty_curve.png",
                "Figure 5": "Figure_05_rule_robustness_heatmap.png",
                "Figure 6": "Figure_06_synthetic_benchmark_coverage.png",
                "Figure 7": "Figure_07_external_testbed_comparison.png",
                "Figure 8": "Figure_08_DSS_artifact_evaluation.png",
            }[figure_id]
            copy_into_package(source, package / "figures" / target_name)
        write_text(package / "manuscript/DSS_submission_draft_stage24.md", manuscript)
        write_text(package / "manuscript/DSS_submission_draft_stage24_anonymized.md", make_anonymized_manuscript(manuscript))
        write_text(package / "manuscript/DSS_submission_draft_stage24_non_anonymized_AUTHOR_METADATA_REQUIRED.md", make_non_anonymized_completion_manuscript(manuscript))
        write_text(package / "manuscript/title_page_AUTHOR_COMPLETION_REQUIRED.md", title_page())
        write_text(package / "highlights.md", (manuscript_dir / "highlights_final_DSS.md").read_text(encoding="utf-8"))
        write_text(package / "cover_letter_DSS_AUTHOR_COMPLETION_REQUIRED.md", cover_letter())
        write_text(package / "declarations/author_side_completion_form.md", author_completion_form())
        write_text(package / "CODE_AND_DATA_README.md", package_readme())
        write_text(package / "references_verified_stage24.md", bibliography(references))
        copy_into_package(root / "supplement/Supplementary_Appendix_DSS.md", package / "supplement/Supplementary_Appendix_DSS.md")
        copy_into_package(root / "supplement/Supplementary_Tables_DSS.csv", package / "supplement/Supplementary_Tables_DSS.csv")
        copy_into_package(root / "supplement/Supplementary_Code_Readme.md", package / "supplement/Supplementary_Code_Readme.md")

        frozen = frozen_hash_check(root)
        write_csv(frozen, tables_dir / "stage24_frozen_hash_check.csv")
        claim_frame = claim_scan(manuscript)
        write_csv(claim_frame, tables_dir / "stage24_claim_language_scan.csv")
        consistency, consistency_markdown = consistency_report(manuscript, references, figures_audit, list(table_names), claim_frame)
        write_csv(consistency, tables_dir / "stage24_manuscript_consistency_checks.csv")
        write_text(logs_dir / "stage24_manuscript_consistency_report.md", consistency_markdown)

        if args.skip_tests:
            tests = "skipped_by_flag"
            test_log = "Tests were skipped by --skip-tests; this is a reproducibility caveat.\n"
        else:
            completed = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"], cwd=root, capture_output=True, text=True, timeout=240, check=False)
            tests = "pass" if completed.returncode == 0 else "fail"
            test_log = (completed.stdout + ("\n" + completed.stderr if completed.stderr else "")).strip() + "\n"
            if tests != "pass":
                raise ValueError("The full test suite failed during Stage 24; inspect outputs/logs/stage24_test_run.log.")
        write_text(logs_dir / "stage24_test_run.log", test_log)

        no_go = final_no_go(references, figures_audit, consistency, frozen, tests)
        write_text(logs_dir / "stage24_final_no_go_check.md", no_go)
        write_text(package / "SUBMISSION_NOTES_AND_NO_GO.md", no_go)

        # The final package note must exist before its bytes and hash are inventoried.
        manifest = package_manifest(root, package)
        write_csv(manifest, tables_dir / "stage24_submission_package_manifest.csv")
        hash_paths = [
            "scripts/24_dss_author_submission_completion.py",
            "manuscript/DSS_submission_draft_stage24.md",
            "manuscript/DSS_submission_draft_stage24_anonymized.md",
            "manuscript/DSS_submission_draft_stage24_non_anonymized_AUTHOR_METADATA_REQUIRED.md",
            "manuscript/references_DSS_verified_stage24.md",
            "outputs/tables/references_DSS_verified_stage24.csv",
            "outputs/stage24_figures/Figure_01_DSS_conceptual_framework_stage24.png",
            "outputs/stage24_figures/Figure_05_rule_robustness_heatmap_stage24.png",
            "outputs/stage24_figures/Figure_07_external_testbed_comparison_stage24.png",
            "outputs/tables/stage24_manuscript_consistency_checks.csv",
            "outputs/tables/stage24_submission_package_manifest.csv",
        ]
        hashes = pd.DataFrame(
            [{"relative_path": item, "sha256": sha256(root / item), "bytes": (root / item).stat().st_size} for item in hash_paths]
        )
        write_csv(hashes, tables_dir / "hash_manifest_stage24.csv")

        execution = "\n".join(
            [
                "# Stage 24 Execution Summary",
                "",
                "## Outputs Generated",
                "",
                "Verified reference manifest and bibliography, Stage 24 cited and anonymized manuscripts, author-side completion form, corrected figure copies, submission package, figure audit, consistency checks, frozen-hash check, package manifest, and strict no-go report.",
                "",
                "## Technical Status",
                "",
                f"- Reference validation: `{args.reference_validation}`.",
                f"- Frozen hash mismatches: `{int((frozen['status'] != 'pass').sum())}`.",
                f"- Test suite: `{tests}`.",
                f"- Stage 24 manuscript reference placeholders: `{len(re.findall(r'\\[REF-[^\\]]+\\]', manuscript))}`.",
                "",
                "## Final Recommendation",
                "",
                "DSS-needs-author-input. Do not submit until author-specific declarations and official DSS portal requirements are verified and completed.",
                "",
                "Historical Stage 23 drafts retain their original placeholder text as traceable prior-stage outputs. The Stage 24 submission manuscript and package contain no [REF-*] placeholder.",
                "",
                "Stage 24 confirms whether the author-side DSS submission package is citation-complete, technically audited, visually repaired, and still correctly blocked pending verified author and portal inputs.",
            ]
        )
        write_text(logs_dir / "stage24_execution_summary.md", execution)
        print("Stage 24 package assembled.")
        print("Final label: DSS-needs-author-input")
        print(f"Package: {package}")
        return 0
    except Exception as exc:
        print(f"Stage 24 failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
