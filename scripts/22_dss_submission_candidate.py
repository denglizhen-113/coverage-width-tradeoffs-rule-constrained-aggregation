#!/usr/bin/env python3
"""Build a reproducible DSS submission-candidate package over frozen evidence.

The stage adds an operational artifact, synthetic structural-portability test,
artifact-level evaluation, protocol-only future user evaluation, and DSS-facing
submission materials. It never overwrites raw data, frozen analytical outputs,
or the frozen pipeline entry point.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dss_decision_cockpit import (  # noqa: E402
    config_json,
    default_demo_payload,
    evaluate_payload,
    markdown_report,
)
from src.dss_evaluation_metrics import (  # noqa: E402
    build_dss_evaluation_metrics,
    dss_evaluation_markdown,
)
from src.external_testbed import external_testbed_audit, run_external_testbed  # noqa: E402


FIGURE_DPI = 300
SEED = 20260716


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a DSS artifact demonstration, structurally different "
            "synthetic testbed, artifact-level evaluation, protocol-only user "
            "evaluation, manuscript sections, and readiness audit."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root containing src/, outputs/, and manuscript/ (default: repository root).",
    )
    parser.add_argument(
        "--external-replications",
        type=int,
        default=120,
        help="Fixed-seed replications for the external synthetic testbed (default: 120).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help="Fixed random seed for the external synthetic testbed (default: 20260716).",
    )
    parser.add_argument(
        "--tests-passed",
        type=int,
        default=0,
        help="Number of tests passed in a separately completed verification run (default: 0; records no test claim).",
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


def require(root: Path, relative_paths: list[str]) -> None:
    missing = [relative for relative in relative_paths if not (root / relative).is_file()]
    if missing:
        raise FileNotFoundError("Required Stage 22 inputs are missing: " + "; ".join(missing))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frozen_hash_mismatches(root: Path) -> pd.DataFrame:
    manifest = pd.read_csv(root / "outputs/tables/frozen_outputs_hashes.csv")
    rows: list[dict[str, str]] = []
    for row in manifest.itertuples(index=False):
        path = root / str(row.relative_path)
        actual = sha256(path) if path.is_file() else ""
        rows.append(
            {
                "relative_path": str(row.relative_path),
                "status": "match" if actual == str(row.sha256) else "mismatch",
            }
        )
    return pd.DataFrame(rows)


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for _, row in frame.loc[:, columns].fillna("").iterrows():
        values = [str(row[column]).replace("|", "\\|").replace("\n", " ") for column in columns]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, divider, *rows])


def apply_plot_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    with Image.open(path) as image:
        image.verify()


def plot_demo_dashboard(round_results: pd.DataFrame, summary: dict[str, object], path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2), constrained_layout=True, gridspec_kw={"width_ratios": [1.15, 0.85]})
    data = round_results.copy()
    widths = pd.to_numeric(data["feasible_set_width"], errors="coerce")
    colors = ["#2F6B4F" if bool(value) else "#B84B4B" for value in data["feasible"]]
    axes[0].barh(np.arange(len(data)), widths, color=colors)
    display_labels = data["round_id"].str.replace("illustrative_", "", regex=False).str.replace("_", " ", regex=False)
    axes[0].set_yticks(np.arange(len(data)), display_labels)
    axes[0].set_xlim(0, 1.0)
    axes[0].set_xlabel("Conditional feasible-set width")
    axes[0].set_title("Round-level uncertainty")
    axes[0].invert_yaxis()
    for index, (width, count) in enumerate(zip(widths, data["eliminated_count"])):
        if np.isfinite(width):
            axes[0].text(min(float(width) + 0.025, 0.94), index, f"{float(width):.2f}; {int(count)} eliminated", va="center", fontsize=8)

    axes[1].set_axis_off()
    labels = [
        ("Rule", str(summary["aggregation_rule_type"])),
        ("Width", f"{float(summary['feasible_set_width']):.3f}"),
        ("Class", str(summary["uncertainty_class"]).replace("_", " ")),
        ("Robustness", str(summary["rule_robustness_label"])),
        ("Disclosure", str(summary["disclosure_regime"]).replace("_", " ")),
    ]
    y = 0.90
    for heading, value in labels:
        axes[1].text(0.02, y, heading, weight="bold", transform=axes[1].transAxes)
        axes[1].text(0.34, y, value, transform=axes[1].transAxes, wrap=True)
        y -= 0.15
    axes[1].text(
        0.02,
        0.08,
        "Illustrative synthetic inputs.\nNot an empirical public-vote estimate.",
        transform=axes[1].transAxes,
        fontsize=8,
    )
    fig.suptitle("DSS Artifact Demonstration: Conditional Uncertainty Dashboard", y=1.02, fontsize=12, weight="bold")
    save_figure(fig, path)


def _box(ax: plt.Axes, xy: tuple[float, float], label: str, color: str) -> None:
    patch = FancyBboxPatch(
        xy,
        0.205,
        0.22,
        boxstyle="round,pad=0.012,rounding_size=0.016",
        facecolor=color,
        edgecolor="#444444",
        linewidth=0.8,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + 0.1025, xy[1] + 0.11, label, ha="center", va="center", fontsize=8, wrap=True)


def plot_decision_maker_flow(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12.0, 4.5))
    ax.set_axis_off()
    boxes = [
        ("Coarse outcomes\nand documented rules", (0.02, 0.58), "#DCEAF7"),
        ("Configure rule,\ndisclosure, objective", (0.27, 0.58), "#DDF1E3"),
        ("Compute compatible\nstates and warnings", (0.52, 0.58), "#FCE8C6"),
        ("Compare robust and\nassumption-sensitive findings", (0.77, 0.58), "#E9DFF4"),
        ("Choose disclosure\nand rule adjustment", (0.39, 0.17), "#F6D7D7"),
    ]
    for label, xy, color in boxes:
        _box(ax, xy, label, color)
    for start, end in [((0.23, 0.69), (0.27, 0.69)), ((0.48, 0.69), (0.52, 0.69)), ((0.73, 0.69), (0.77, 0.69))]:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.1, "color": "#444444"})
    ax.annotate("", xy=(0.50, 0.39), xytext=(0.87, 0.58), arrowprops={"arrowstyle": "->", "lw": 1.1, "color": "#444444"})
    ax.text(0.50, 0.05, "Outside the system: objective setting, legal/privacy review, stakeholder engagement, and implementation authority.", ha="center", fontsize=8.5)
    ax.text(0.50, 0.94, "Decision-Maker Use Scenario: Rule and Disclosure Evaluation", ha="center", fontsize=12, weight="bold")
    save_figure(fig, path)


def plot_external_testbed(results: pd.DataFrame, path: Path) -> None:
    data = results.copy()
    labels = data["method"].str.replace("_", " ")
    x = np.arange(len(data))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5), constrained_layout=True)
    axes[0].bar(x - 0.18, data["coverage_rate"], width=0.36, color="#2F6B4F", label="Known-truth coverage")
    axes[0].bar(x + 0.18, data["false_certainty_rate"], width=0.36, color="#B84B4B", label="False-certainty diagnostic")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_xticks(x, labels, rotation=25, ha="right")
    axes[0].set_ylabel("Synthetic rate")
    axes[0].set_title("Calibration under structural variation")
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    axes[1].bar(x - 0.18, data["average_feasible_set_width"], width=0.36, color="#1F5A7A", label="Feasible-rank width")
    axes[1].bar(x + 0.18, data["disclosure_uncertainty_reduction"], width=0.36, color="#D28A2D", label="Pairwise disclosure reduction")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_xticks(x, labels, rotation=25, ha="right")
    axes[1].set_ylabel("Normalized rank-width quantity")
    axes[1].set_title("Conditional uncertainty and disclosure")
    axes[1].legend(frameon=False, fontsize=8, loc="upper left")
    fig.suptitle("External Synthetic Testbed: Community-Grant Prioritization", y=1.02, fontsize=12, weight="bold")
    save_figure(fig, path)


def plot_evaluation_radar(metrics: pd.DataFrame, path: Path) -> None:
    labels = metrics["criterion"].tolist()
    values = metrics["artifact_evidence_completeness"].to_numpy(dtype=float)
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    closed_angles = np.concatenate([angles, [angles[0]]])
    closed_values = np.concatenate([values, [values[0]]])
    fig, ax = plt.subplots(figsize=(7.2, 6.5), subplot_kw={"projection": "polar"}, constrained_layout=True)
    ax.plot(closed_angles, closed_values, color="#1F5A7A", linewidth=1.8, marker="o")
    ax.fill(closed_angles, closed_values, color="#1F5A7A", alpha=0.18)
    ax.set_xticks(angles, labels, fontsize=8)
    ax.set_yticks([0.25, 0.50, 0.75, 1.0], ["0.25", "0.50", "0.75", "1.00"], fontsize=7)
    ax.set_ylim(0, 1.0)
    ax.set_title(
        "Artifact Evidence-Completeness Checks\nNot a user-effectiveness, trust, adoption, or organizational-impact score.",
        y=1.14,
        fontsize=11,
        weight="bold",
    )
    save_figure(fig, path)


def artifact_description() -> str:
    return """
# Operational DSS Artifact

The decision-support artifact is a lightweight, JSON-configurable cockpit for an institutional organizer or platform governance analyst. It records observed elimination outcomes, aggregation rule type, judge-save assumption, tie-handling assumption, disclosure regime, and decision objective. It then calculates the rule-specific compatible-state width, classifies conditional uncertainty, retrieves an applicable predeclared rule-robustness label, and returns a disclosure recommendation, a design warning, and an accountability implication.

For percentage aggregation, each supplied elimination generates affine comparisons between the eliminated and non-eliminated active candidates. The cockpit intersects those comparisons with the unit simplex and uses coordinate-wise linear programs to report a mean feasible-share interval width. No-elimination and withdrawal rounds deliberately add no outcome constraint; multiple eliminations are compared with all non-eliminated active candidates; a finale order is used only when the user supplies a complete documented order. For ranking rules, the cockpit enumerates strict public rankings in small fields and uses fixed-seed uniform draws above the declared enumeration cap. A weak judge-save condition expands bottom-set eligibility by one position rather than being treated as a direct elimination.

The artifact is a decision-support workflow rather than a point-estimation tool. Its report records the assumptions that make a conclusion conditional and states when coarse outcomes do not support a unique hidden-preference claim. The cockpit supports institutional judgment; it does not set objectives, infer stakeholder values, perform legal or privacy review, or replace a decision maker.
"""


def use_scenario() -> str:
    return """
# Decision-Maker Use Scenario

An institutional organizer oversees a recurring expert-crowd selection process. The organizer observes expert scores and final eliminations, but the public-preference signal is released only coarsely. A discretionary save can preserve a candidate despite a weak combined standing. The organizer must decide whether to retain the current aggregation rule, disclose more preference information, or tighten the judge-save protocol.

First, the organizer enters the documented active set, outcomes, expert inputs, aggregation rule, intervention assumption, tie protocol, disclosure regime, and objective. The cockpit does not convert this record into a claimed public vote. It produces a compatible-state width and marks whether the conclusion is broad, moderate, or narrow only under the selected rule. If the judge-save condition is modeled as weak bottom-set membership, the report distinguishes this from a direct-elimination reading and makes the extra ambiguity visible.

Second, the organizer compares rule and disclosure scenarios. A broad compatible set paired with a transparency objective leads to a conditional recommendation for the least intrusive additional public-rank or pairwise disclosure. A flexibility objective leads instead to an intervention record with eligibility and rationale. The rule-robustness label identifies whether the relevant predeclared conclusion survives the available configuration checks; it does not declare an institutional optimum.

Third, the organizer documents the selected disclosure policy and any rule adjustment with the cockpit configuration and report. The system supports a traceable design decision about information release and rule clarity. Objective setting, privacy and legal assessment, stakeholder consultation, implementation authority, and monitoring of real organizational consequences remain outside the system.
"""


def external_testbed_section(results: pd.DataFrame) -> str:
    display = results.loc[:, [
        "method",
        "coverage_rate",
        "average_feasible_set_width",
        "false_certainty_rate",
        "rule_robustness_index",
        "disclosure_uncertainty_reduction",
        "recommendation_stability",
    ]].copy()
    for column in display.columns[1:]:
        display[column] = display[column].map(lambda value: f"{float(value):.3f}")
    return "\n".join(
        [
            "# Structurally Different External Testbed",
            "",
            "To examine structural portability without claiming a second empirical validation, we construct a fixed-seed synthetic community-grant prioritization panel. The setting begins with seven proposals, runs four elimination rounds, uses a synthetic expert intervention in two rounds, adopts dense-rank tie handling, and releases one synthetic pairwise public-priority relation. These ingredients differ from the single-week percentage simulator and from the longitudinal empirical testbed.",
            "",
            markdown_table(display, list(display.columns)),
            "",
            "The rule-aware discretion representation retains the known synthetic ranking whenever the simulation follows its stated direct or weak intervention rule. Treating every intervention as direct is deliberately a misspecification comparator, not a plausible empirical estimate. The testbed demonstrates structural portability of the conditional DSS logic under this institutional mechanism; it neither proves universal applicability nor supplies evidence about real grant decisions, users, or organizations.",
        ]
    ) + "\n"


def scenario_evaluation_table() -> pd.DataFrame:
    rows = [
        ("institutional organizer", "classify a conclusion as robust or assumption-sensitive", "classification accuracy", "select robust / assumption-sensitive / unresolved", "protocol only"),
        ("platform governance researcher", "choose among disclosure regimes under a stated privacy objective", "task completion accuracy; perceived reporting burden", "scenario choice plus rationale", "protocol only"),
        ("decision-support researcher", "explain the effect of a judge-save rule", "interpretability; trust calibration", "short structured explanation", "protocol only"),
        ("competition rule designer", "compare two aggregation mechanisms", "decision confidence; mechanism-comparison accuracy", "choice, confidence scale, rationale", "protocol only"),
        ("public accountability reviewer", "decide whether additional information should be disclosed", "perceived usefulness; reporting burden", "recommendation with uncertainty explanation", "protocol only"),
    ]
    return pd.DataFrame(rows, columns=["future_participant_role", "evaluation_task", "planned_measure", "response_format", "evidence_status"]).assign(
        evaluation_type="future scenario-based user evaluation design",
        interpretation_boundary="No participant has been recruited and no human-subject, trust, usability, or organizational-impact data are reported.",
    )


def user_evaluation_design(table: pd.DataFrame) -> str:
    return "\n".join(
        [
            "# Future Scenario-Based User Evaluation Design",
            "",
            "## Status",
            "",
            "This is a proposed future protocol. No participants were recruited, no participant data were collected, and no claims about usefulness, trust, workload, decision quality, privacy outcomes, or organizational impact are made.",
            "",
            "## Recruitment Roles",
            "",
            "Future recruitment would seek an institutional organizer, platform governance researcher, decision-support researcher, competition rule designer, and public accountability reviewer. Eligibility, sample size, compensation, consent, data handling, and any required ethics review must be determined before implementation; none is inferred here.",
            "",
            "## Scenario Tasks and Measures",
            "",
            markdown_table(table, ["future_participant_role", "evaluation_task", "planned_measure", "response_format", "evidence_status"]),
            "",
            "## Analysis Plan",
            "",
            "A future study should pre-register scenario versions, scoring keys for accuracy tasks, exclusion rules, and the distinction between calibrated confidence and raw confidence. It should report role-specific results, missingness, and limitations rather than pooling diverse stakeholder roles into an unqualified effectiveness claim. The protocol should compare the artifact against a documented information-only control only after a locally appropriate evaluation design and approvals are established.",
        ]
    ) + "\n"


def scenario_evaluation_section() -> str:
    return """
# Scenario-Based Evaluation Plan

No user or organizational evaluation has been conducted. We therefore provide a future scenario-based evaluation protocol rather than simulated participant results. The protocol asks potential institutional organizers, governance researchers, DSS researchers, rule designers, and accountability reviewers to identify robust versus assumption-sensitive conclusions, choose among disclosure regimes, explain judge-save effects, compare aggregation mechanisms, and decide whether further information should be disclosed.

Planned measures include task completion accuracy, perceived usefulness, perceived interpretability, decision confidence, trust calibration, and perceived reporting burden. These measures are prospective: they require a future recruitment, approved data-management plan, and locally appropriate ethics determination. They must not be presented as current evidence of usability, trust, adoption, or organizational impact.
"""


def related_work_final() -> str:
    return """
# DSS-Positioned Related Work

## Decision Support for Uncertain Institutional Decisions

The manuscript frames institutional rule and disclosure selection as a decision-support problem under incomplete observability. The existing verified reference map does not contain a completed DSS-specific source set for this stream. This is a citation gap requiring manual source identification, full-text reading, and claim-level verification before submission; no unverified DSS citation is added here.

## Model-Driven DSS and Decision Analytics

The cockpit is model-driven in the narrow sense that documented rules and outcomes generate compatible-state calculations and warnings. The current verified reference map lacks a venue-specific model-driven DSS source that can support broader effectiveness claims. The artifact is therefore described by its implemented behavior, not by an unverified literature claim.

## Rule-Based and Explainable DSS

Rule, tie, intervention, disclosure, and objective assumptions are carried into an auditable recommendation. The available verified sources do not yet establish a dedicated explainable-DSS literature bridge. This stream remains a manual-review gap rather than a fabricated citation list.

## Human-in-the-Loop and Expert-Crowd Decision Systems

The expert-crowd setting is motivated cautiously by the verified source map (Lorenz et al., 2011). The contribution does not claim that the empirical testbed records true collective preferences or demonstrates human-AI collaboration outcomes. A future user evaluation is protocol-only.

## Transparency, Accountability, and Disclosure

The disclosure component is a formal scenario analysis: it represents how additional signals could reduce compatible-state uncertainty under stated rules. The project does not contain measured trust, privacy, cost, or accountability outcomes. Dedicated DSS transparency and accountability sources remain a manual-review need.

## Partial Identification and Uncertainty-Aware Decision Support

Manski (2000, 2007) and Imbens and Manski (2004), all present in the verified source map, motivate retaining identified sets and decision uncertainty rather than collapsing incomplete information to a point. In this work, that logic is operationalized through rule-specific feasible preference intervals and rankings. Cardinal and ordinal uncertainty are retained as different objects rather than being pooled into one unsupported scale.

## Precise Gap

Existing work has not sufficiently addressed how institutional designers can compare aggregation mechanisms when public preferences are hidden, expert intervention is rule-dependent, and disclosure policies determine the identifiability of collective preferences. The present contribution is a reproducible, rule-aware decision-support artifact that makes those conditional information consequences inspectable. Its empirical application is a testbed, its additional setting is synthetic, and its proposed user evaluation remains future work.
"""


def literature_gap_audit(reference_plan: pd.DataFrame) -> str:
    verified = reference_plan.loc[reference_plan["verified"].astype(str).str.casefold().eq("yes")]
    return "\n".join(
        [
            "# DSS Literature Gap Audit",
            "",
            f"- Existing reference-plan rows with verified metadata: `{len(verified)}`.",
            "- New external citations added in this stage: `0`.",
            "- Citation policy: use only project-verified citations; any DSS-specific gap remains visible for manual source review.",
            "",
            "| Required DSS stream | Current verified support | Status before submission |",
            "| --- | --- | --- |",
            "| Uncertain institutional DSS | No dedicated DSS source in the verified map | manual review required |",
            "| Model-driven DSS / analytics | No dedicated DSS source in the verified map | manual review required |",
            "| Rule-based / explainable DSS | No dedicated DSS source in the verified map | manual review required |",
            "| Human-in-the-loop / expert-crowd systems | Lorenz et al. (2011) provides cautious motivation only | partial; claim-level review required |",
            "| Transparency, accountability, disclosure | Formal scenario module only; no stakeholder measurement source in verified map | manual review required |",
            "| Partial identification under uncertainty | Manski (2000, 2007); Imbens and Manski (2004) | available for identified-set logic; not a DSS-effectiveness claim |",
            "",
            "The related-work section deliberately does not claim a completed DSS literature review. Before upload, authors must select and read additional DSS sources, verify bibliographic metadata and exact claims, and format a final bibliography in the live journal style.",
        ]
    ) + "\n"


def title_options() -> str:
    return """
# DSS Title Options

## Recommended

Rule-Aware Decision Support for Expert-Crowd Aggregation under Hidden Public Preferences

## Alternatives

1. A Rule-Aware Decision Support Framework for Institutional Aggregation under Hidden Preferences
2. Decision Support for Accountable Expert-Crowd Aggregation with Partial Preference Disclosure
3. Evaluating Aggregation Rules under Hidden Public Preferences: A Decision-Support Framework

All options describe hidden preferences as partially observed inputs. None implies recovery of true public votes, a universal optimal rule, or measured organizational impact.
"""


def final_abstract() -> str:
    return """
# DSS Abstract

Institutional and platform designers often combine expert judgments with public input while releasing only coarse outcomes. When public preferences are hidden, an observed elimination may be compatible with multiple collective states, expert intervention, or a rule artifact. We develop a rule-aware decision-support framework that translates documented aggregation rules, active sets, expert inputs, outcomes, tie handling, judge-save assumptions, and disclosure regimes into feasible preference representations rather than a recovered public vote. Percentage rules yield cardinal feasible intervals; ranking rules yield feasible ordinal rankings; and a weak judge-save condition makes the discretion-identifiability trade-off explicit. The framework combines a discretion-identifiability frontier, modeled value-of-disclosure scenarios, and a rule robustness index with a fixed-seed known-truth synthetic benchmark. We implement these components in a JSON-configurable DSS artifact that produces conditional uncertainty classes, design warnings, disclosure recommendations, and accountability records for institutional designers. A structurally different synthetic community-grant testbed evaluates calibration, feasible-set width, false-certainty diagnostics, disclosure uncertainty reduction, and recommendation stability. The longitudinal empirical setting remains a testbed, and the external setting is synthetic. Results support conditional institutional design analysis under incomplete observability; they do not recover exact public preferences, measure stakeholder trust or privacy outcomes, demonstrate organizational impact, or identify a universally optimal aggregation rule.
"""


def contribution_statement() -> str:
    return """
# DSS Contribution Statement

1. **Rule-aware partial identification for institutional aggregation.** The framework maps documented percentage, ranking, and judge-save mechanisms into mechanism-specific compatible-state representations instead of an unsupported hidden-preference point estimate.
2. **Operational decision-support artifact.** A JSON-configurable cockpit converts six decision inputs into a feasible-set width, uncertainty class, robustness label, disclosure recommendation, design warning, and accountability implication.
3. **Explicit information-design evaluation.** Discretion, tie handling, and disclosure are modeled as conditions that alter what later observers can identify; the associated recommendations remain conditional rather than welfare-optimal claims.
4. **Calibrated portability evidence with preserved boundaries.** A known-truth synthetic benchmark and a structurally different synthetic institutional testbed evaluate feasible-set coverage, false-certainty diagnostics, robustness, and disclosure reduction. Neither substitutes for empirical public preferences or a user study.
5. **Future validation discipline.** A scenario-based user-evaluation protocol separates artifact-level checks from future evidence about interpretability, trust calibration, burden, and organizational use.
"""


def compliance_rows() -> pd.DataFrame:
    rows = [
        ("title page", "needs author input", "Author identities, affiliations, corresponding author, and institutional metadata are not inferred."),
        ("author list", "needs author input", "No author list is generated from project files."),
        ("highlights", "needs formatting", "Draft highlights exist but require integration and live-guide confirmation."),
        ("abstract", "needs formatting", "DSS abstract draft exists; live word limit and format remain unverified."),
        ("keywords", "needs formatting", "Keywords must be finalized against the live submission form."),
        ("graphical abstract if needed", "unresolved", "Official DSS requirement could not be browser-verified in this runtime."),
        ("editable tables", "needs formatting", "Generated CSV evidence is editable, but final manuscript tables are not assembled."),
        ("figure resolution", "needs formatting", "New figures are generated at 300 DPI; official production specification remains unverified."),
        ("data availability statement", "needs author input", "Data source terms, access route, and redistribution permission require author confirmation."),
        ("code availability statement", "needs author input", "Repository/archive location, licence, and persistent release must be selected by authors."),
        ("declaration of competing interests", "needs author input", "No conflict declaration may be inferred."),
        ("funding statement", "needs author input", "Funding sources and funder roles may not be inferred."),
        ("generative AI declaration", "needs author input", "A draft exists, but final wording and live policy placement require confirmation."),
        ("ethics statement if needed", "needs author input", "Authors must determine whether any review or consent statement applies; no approval is invented."),
        ("CRediT author contributions", "needs author input", "Named roles must be completed by authors."),
        ("supplementary material", "needs formatting", "Existing outputs need selection, labeling, and a reproducibility release plan."),
        ("anonymous version if required", "unresolved", "Double-anonymous requirement could not be browser-verified in this runtime."),
        ("reference style", "needs formatting", "A final DSS-formatted bibliography and claim-level source review are incomplete."),
        ("word count", "needs formatting", "A complete manuscript has not yet been typeset or counted against a verified live limit."),
        ("file naming", "unresolved", "Live portal naming and upload requirements could not be browser-verified in this runtime."),
    ]
    return pd.DataFrame(rows, columns=["submission_item", "status", "basis"]).assign(
        official_reference="Decision Support Systems / Elsevier official guide intended reference point",
        official_verification_status="unresolved: official page could not be inspected in this runtime on 2026-07-16",
    )


def compliance_markdown(checklist: pd.DataFrame) -> str:
    return "\n".join(
        [
            "# DSS Submission Compliance Checklist",
            "",
            "## Official-Source Boundary",
            "",
            "The official Decision Support Systems / Elsevier page was selected as the reference point, but it could not be inspected from the available browser runtime on 2026-07-16. The checklist therefore does not assert current official requirements. Items depending on live instructions are marked `unresolved`; other statuses only describe the present project materials.",
            "",
            markdown_table(checklist, ["submission_item", "status", "basis"]),
            "",
            "Before upload, authors must inspect the live official guide and submission portal, resolve every `unresolved` item, complete all author-specific declarations, and reconcile the final compiled files with the then-current requirements.",
        ]
    ) + "\n"


def readiness_report(root: Path, hash_mismatches: int, checklist: pd.DataFrame) -> str:
    required = [
        "src/dss_artifact.py",
        "src/dss_decision_cockpit.py",
        "outputs/artifact_demo/demo_input_config.json",
        "outputs/artifact_demo/demo_decision_report.md",
        "outputs/artifact_demo/demo_recommendation_table.csv",
        "outputs/artifact_demo/demo_uncertainty_dashboard.png",
        "manuscript/sections/dss_artifact_description.md",
        "manuscript/sections/dss_use_scenario.md",
        "outputs/figures/decision_maker_use_case_flow.png",
        "src/external_testbed.py",
        "outputs/tables/external_testbed_results.csv",
        "outputs/figures/external_testbed_comparison.png",
        "outputs/logs/external_testbed_audit.md",
        "manuscript/sections/external_testbed.md",
        "src/dss_evaluation_metrics.py",
        "outputs/tables/dss_evaluation_metrics.csv",
        "outputs/figures/dss_evaluation_radar.png",
        "manuscript/sections/dss_evaluation.md",
        "outputs/tables/scenario_based_evaluation.csv",
        "outputs/logs/user_evaluation_design.md",
        "manuscript/sections/scenario_based_evaluation.md",
        "manuscript/related_work_DSS_final.md",
        "outputs/logs/dss_literature_gap_audit.md",
        "manuscript/title_options_DSS_final.md",
        "manuscript/abstract_DSS_final.md",
        "manuscript/contribution_DSS_final.md",
        "outputs/logs/dss_submission_compliance_checklist.md",
    ]
    missing = [path for path in required if not (root / path).is_file()]
    unresolved = int(checklist["status"].eq("unresolved").sum())
    author_input = int(checklist["status"].eq("needs author input").sum())
    label = "DSS-submission-candidate" if not missing and hash_mismatches == 0 else "DSS-needs-minor-integration"
    return "\n".join(
        [
            "# DSS Submission Candidate Report",
            "",
            f"## Final label: {label}",
            "",
            "This label means that the previously identified artifact, decision-maker scenario, structural-portability, artifact-evaluation, protocol, and checklist gaps now have explicit deliverables. It does not mean upload-ready or officially compliant.",
            "",
            "## What Changed from DSS-Conditionally-Ready",
            "",
            "- A configuration-driven DSS cockpit translates documented inputs into conditional recommendations and audit records.",
            "- A full institutional decision-maker scenario and use-case flow make the supported decision concrete.",
            "- A structurally different synthetic community-grant testbed evaluates portability under a different candidate count, round count, intervention frequency, disclosure setting, and tie protocol.",
            "- Artifact-level metrics distinguish implemented evidence completeness from user or organizational impact.",
            "- A future-only scenario-based user-evaluation protocol prevents simulated stakeholders from being presented as evidence.",
            "",
            "## Required DSS Elements",
            "",
            f"- DSS artifact present: `{'yes' if (root / 'src/dss_artifact.py').is_file() else 'no'}`.",
            f"- Decision-maker use scenario present: `{'yes' if (root / 'manuscript/sections/dss_use_scenario.md').is_file() else 'no'}`.",
            f"- External synthetic testbed present: `{'yes' if (root / 'outputs/tables/external_testbed_results.csv').is_file() else 'no'}`.",
            f"- DSS artifact-level evaluation present: `{'yes' if (root / 'outputs/tables/dss_evaluation_metrics.csv').is_file() else 'no'}`.",
            f"- Compliance checklist present: `{'yes' if (root / 'outputs/logs/dss_submission_compliance_checklist.md').is_file() else 'no'}`.",
            f"- Frozen-artifact hash mismatches: `{hash_mismatches}`.",
            f"- Required new deliverables missing: `{len(missing)}`.",
            "",
            "## What Remains Unproven",
            "",
            "- No empirical hidden public preferences are recovered.",
            "- No real users, organizations, or decision makers evaluated the cockpit.",
            "- No trust, privacy, reporting-cost, adoption, or organizational-impact outcome was measured.",
            "- The external setting is synthetic and demonstrates structural portability only.",
            "- DSS-specific literature gaps and final claim-level reading remain manual work.",
            "",
            "## What Must Not Be Claimed",
            "",
            "Do not claim true public-vote recovery, a universally optimal rule, demonstrated usability, stakeholder trust, privacy protection, organizational benefit, completed ethics review, or verified current Elsevier/DSS compliance.",
            "",
            "## Upload Blockers",
            "",
            f"- Checklist items unresolved because the official guide could not be inspected: `{unresolved}`.",
            f"- Checklist items requiring author input: `{author_input}`.",
            "- A complete manuscript, verified DSS-specific bibliography, declarations, source-term decision, release/archival plan, and final PDF/portal check remain necessary before upload.",
        ]
    ) + "\n"


def validate_generated_outputs(root: Path, expected: list[str]) -> None:
    missing = [relative for relative in expected if not (root / relative).is_file()]
    if missing:
        raise ValueError("Expected Stage 22 outputs are missing: " + "; ".join(missing))
    for relative in [path for path in expected if path.endswith(".png")]:
        with Image.open(root / relative) as image:
            if image.width < 200 or image.height < 150:
                raise ValueError(f"Generated figure appears too small: {relative}.")
            image.verify()


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    required = [
        "outputs/tables/frozen_outputs_hashes.csv",
        "outputs/tables/rule_robustness_index.csv",
        "outputs/tables/reference_insertion_plan.csv",
        "outputs/logs/dss_full_attack_readiness_report.md",
        "src/constraints.py",
        "src/ranking_identification.py",
    ]
    try:
        require(root, required)
        mismatch_table = frozen_hash_mismatches(root)
        hash_mismatches = int(mismatch_table["status"].eq("mismatch").sum())
        if hash_mismatches:
            details = mismatch_table.loc[mismatch_table["status"].eq("mismatch"), "relative_path"].tolist()
            raise ValueError("Frozen artifacts changed: " + "; ".join(details))

        apply_plot_style()
        tables = root / "outputs/tables"
        figures = root / "outputs/figures"
        logs = root / "outputs/logs"
        artifact_dir = root / "outputs/artifact_demo"
        sections = root / "manuscript/sections"
        manuscript = root / "manuscript"

        rule_robustness = pd.read_csv(tables / "rule_robustness_index.csv")
        demo_started = time.perf_counter()
        config, artifact = evaluate_payload(default_demo_payload(), rule_robustness=rule_robustness)
        demo_runtime = time.perf_counter() - demo_started
        write_text(artifact_dir / "demo_input_config.json", config_json(config))
        write_text(artifact_dir / "demo_decision_report.md", markdown_report(config, artifact))
        write_csv(artifact.recommendation_table, artifact_dir / "demo_recommendation_table.csv")
        plot_demo_dashboard(artifact.round_results, artifact.summary, artifact_dir / "demo_uncertainty_dashboard.png")
        write_text(sections / "dss_artifact_description.md", artifact_description())

        write_text(sections / "dss_use_scenario.md", use_scenario())
        plot_decision_maker_flow(figures / "decision_maker_use_case_flow.png")

        external = run_external_testbed(n_replications=args.external_replications, seed=args.seed)
        write_csv(external, tables / "external_testbed_results.csv")
        plot_external_testbed(external, figures / "external_testbed_comparison.png")
        write_text(logs / "external_testbed_audit.md", external_testbed_audit(external, seed=args.seed))
        write_text(sections / "external_testbed.md", external_testbed_section(external))

        metrics = build_dss_evaluation_metrics(
            artifact,
            external_results=external,
            tests_passed=args.tests_passed,
            artifact_runtime_seconds=demo_runtime,
        )
        write_csv(metrics, tables / "dss_evaluation_metrics.csv")
        plot_evaluation_radar(metrics, figures / "dss_evaluation_radar.png")
        write_text(sections / "dss_evaluation.md", dss_evaluation_markdown(metrics))

        scenario_table = scenario_evaluation_table()
        write_csv(scenario_table, tables / "scenario_based_evaluation.csv")
        write_text(logs / "user_evaluation_design.md", user_evaluation_design(scenario_table))
        write_text(sections / "scenario_based_evaluation.md", scenario_evaluation_section())

        reference_plan = pd.read_csv(tables / "reference_insertion_plan.csv")
        write_text(manuscript / "related_work_DSS_final.md", related_work_final())
        write_text(logs / "dss_literature_gap_audit.md", literature_gap_audit(reference_plan))
        write_text(manuscript / "title_options_DSS_final.md", title_options())
        write_text(manuscript / "abstract_DSS_final.md", final_abstract())
        write_text(manuscript / "contribution_DSS_final.md", contribution_statement())

        checklist = compliance_rows()
        write_text(logs / "dss_submission_compliance_checklist.md", compliance_markdown(checklist))

        expected = [
            "src/dss_artifact.py",
            "src/dss_decision_cockpit.py",
            "outputs/artifact_demo/demo_input_config.json",
            "outputs/artifact_demo/demo_decision_report.md",
            "outputs/artifact_demo/demo_recommendation_table.csv",
            "outputs/artifact_demo/demo_uncertainty_dashboard.png",
            "manuscript/sections/dss_artifact_description.md",
            "manuscript/sections/dss_use_scenario.md",
            "outputs/figures/decision_maker_use_case_flow.png",
            "src/external_testbed.py",
            "outputs/tables/external_testbed_results.csv",
            "outputs/figures/external_testbed_comparison.png",
            "outputs/logs/external_testbed_audit.md",
            "manuscript/sections/external_testbed.md",
            "src/dss_evaluation_metrics.py",
            "outputs/tables/dss_evaluation_metrics.csv",
            "outputs/figures/dss_evaluation_radar.png",
            "manuscript/sections/dss_evaluation.md",
            "outputs/tables/scenario_based_evaluation.csv",
            "outputs/logs/user_evaluation_design.md",
            "manuscript/sections/scenario_based_evaluation.md",
            "manuscript/related_work_DSS_final.md",
            "outputs/logs/dss_literature_gap_audit.md",
            "manuscript/title_options_DSS_final.md",
            "manuscript/abstract_DSS_final.md",
            "manuscript/contribution_DSS_final.md",
            "outputs/logs/dss_submission_compliance_checklist.md",
        ]
        validate_generated_outputs(root, expected)
        write_text(logs / "dss_submission_candidate_report.md", readiness_report(root, hash_mismatches, checklist))
        if not (logs / "dss_submission_candidate_report.md").is_file():
            raise ValueError("DSS readiness report was not created.")
    except (OSError, ValueError, KeyError, IndexError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("DSS submission-candidate package completed.")
    print(f"Artifact demo rounds: {len(artifact.round_results)}")
    print(f"External synthetic replications: {args.external_replications}")
    print(f"External testbed methods: {len(external)}")
    print(f"Artifact demo runtime seconds: {demo_runtime:.3f}")
    print(f"Frozen-artifact hash mismatches: {hash_mismatches}")
    print("Readiness: DSS-submission-candidate (not upload-ready; see compliance checklist).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
