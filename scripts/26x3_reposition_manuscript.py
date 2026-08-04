"""Generate the Stage 26X-3 repositioned manuscript and evidence reports."""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
from collections import defaultdict
from pathlib import Path


SOURCE_SHA256 = "6f1fc33fcd93e099b0ecf85f3f129e94b4aa00be80a42e8dd162bc3d2db45b76"
OUTPUT_NAMES = {
    "CONTRIBUTION_REPOSITIONING.md",
    "NEGATIVE_RESULTS_DISCLOSURE.md",
    "MANUSCRIPT_REPOSITIONING_LOG.md",
    "FROZEN_ARTIFACT_TEST_FAILURE.md",
    "TARGET_JOURNAL_ANALYSIS.md",
    "SUBMISSION_VERDICT_V2.md",
    "METHODS_submission_draft_STAGE26X3_source.md",
    "Figure_06_multiseed_internal_sensitivity.png",
    "Figure_06_multiseed_internal_sensitivity.pdf",
    "Figure_07_multiseed_external_sensitivity.png",
    "Figure_07_multiseed_external_sensitivity.pdf",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Stage 26X-3 from locked Stage 26W, 26X-1, and 26X-2 evidence."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root containing outputs/stage26W and outputs/stage26X-1/2.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Destination directory. Defaults to outputs/stage26X-3 under the project root.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def fmt(value: str, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}"


def distribution(row: dict[str, str], prefix: str) -> str:
    return (
        f"{fmt(row[prefix + '_mean'])}; med {fmt(row[prefix + '_median'])}; "
        f"SD {fmt(row[prefix + '_std'])}; "
        f"[{fmt(row[prefix + '_q025'])}, {fmt(row[prefix + '_q975'])}]"
    )


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def table4(root: Path) -> str:
    rows = read_csv(root / "outputs/stage26X-1/tables/Table4_multiseed.csv")
    methods = {
        "rule_aware_partial_identification": "Rule-aware set",
        "rule_agnostic_partial_identification": "Simplex-only set",
    }
    selected = [row for row in rows if row["method"] in methods]
    selected.sort(
        key=lambda row: (
            int(float(row["n_active"])),
            float(row["outcome_noise_probability"]),
            row["method"],
        )
    )
    display = []
    for row in selected:
        display.append(
            [
                str(int(float(row["n_active"]))),
                fmt(row["outcome_noise_probability"], 2),
                methods[row["method"]],
                distribution(row, "coverage_rate"),
                distribution(row, "average_feasible_set_width"),
                f"{row['n_seeds']} x {row['replications_per_seed']}",
            ]
        )
    return md_table(
        [
            "Active candidates",
            "Outcome noise",
            "Method",
            "Coverage: mean; median; SD; empirical 2.5%-97.5%",
            "Width: mean; median; SD; empirical 2.5%-97.5%",
            "Seeds x replications",
        ],
        display,
    )


def table5(root: Path) -> str:
    rows = read_csv(root / "outputs/stage26X-1/tables/Table5_multiseed.csv")
    labels = {
        "direct_rule_misspecification": "Direct-rule misspecification",
        "rule_agnostic_ordinal": "Rule-agnostic ordinal set",
        "rule_aware_discretion": "Rule-aware discretion set",
    }
    rows.sort(
        key=lambda row: (
            int(float(row["n_candidates"])),
            int(float(row["n_rounds"])),
            row["method"],
        )
    )
    display = []
    for row in rows:
        display.append(
            [
                str(int(float(row["n_candidates"]))),
                str(int(float(row["n_rounds"]))),
                labels[row["method"]],
                distribution(row, "coverage_rate"),
                distribution(row, "average_feasible_set_width"),
                distribution(row, "false_certainty_rate"),
                f"{row['n_seeds']} x {row['replications_per_seed']}",
            ]
        )
    return md_table(
        [
            "Candidates",
            "Rounds",
            "Method",
            "Coverage: mean; median; SD; empirical 2.5%-97.5%",
            "Width: mean; median; SD; empirical 2.5%-97.5%",
            "False certainty: mean; median; SD; empirical 2.5%-97.5%",
            "Seeds x replications",
        ],
        display,
    )


def table6(root: Path) -> str:
    rows = read_csv(root / "outputs/stage26X-2/tables/attribution_pairwise_cells.csv")
    clean = [row for row in rows if row["clean_cell"] == "True"]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clean:
        grouped[row["parameter_region"]].append(row)
    order = [
        "internal n=4, noise=0.00",
        "internal n=5, noise=0.00",
        "internal n=6, noise=0.00",
        "external candidates=6, rounds=3",
        "external candidates=7, rounds=3",
        "external candidates=7, rounds=4",
    ]
    display = []
    aware_total = 0
    bayesian_total = 0
    for region in order:
        group = grouped[region]
        aware = sum(row["aware_pareto_dominates"] == "True" for row in group)
        bayesian = sum(row["bayesian_pareto_dominates"] == "True" for row in group)
        aware_total += aware
        bayesian_total += bayesian
        display.append([region, str(len(group)), str(aware), str(bayesian)])
    display.append(["Total clean comparison", str(len(clean)), str(aware_total), str(bayesian_total)])
    assert len(clean) == 120 and aware_total == 0 and bayesian_total == 14
    return md_table(
        [
            "Parameter region",
            "Paired seed-cells",
            "Rule-aware Pareto dominance",
            "Bayesian Pareto dominance",
        ],
        display,
    )


def table7(root: Path) -> str:
    robustness = (root / "outputs/stage26X-1/ROBUSTNESS_ASSESSMENT.md").read_text(encoding="utf-8")
    ablation = (root / "outputs/stage26X-2/ABLATION_RESULTS.md").read_text(encoding="utf-8")
    paired = read_csv(root / "outputs/stage26X-2/tables/ablation_paired_effects.csv")
    positive_noise = [
        row
        for row in paired
        if row["configuration"] == "internal_without_elimination"
        and float(row["outcome_noise_probability"]) > 0
    ]
    coverage_mean = sum(float(row["coverage_change"]) for row in positive_noise) / len(positive_noise)
    width_mean = sum(float(row["width_change"]) for row in positive_noise) / len(positive_noise)
    assert len(positive_noise) == 180
    assert f"{coverage_mean:.6f}" == "0.050289"
    assert f"{width_mean:.6f}" == "0.163131"
    for value, source in (
        ("0.050289", robustness),
        ("180/180", robustness),
        ("-0.841389", ablation),
        ("-0.059959", ablation),
        ("-0.072917", ablation),
        ("0.004666", ablation),
        ("0.129121", ablation),
        ("0.078111", ablation),
    ):
        assert value in source
    return md_table(
        [
            "Synthetic setting",
            "Removed component",
            "Paired cells",
            "Mean coverage change",
            "Mean width change",
            "Observed direction",
        ],
        [
            ["Internal, zero outcome noise", "Elimination", "60", "0 in 60/60", "Not pooled here", "Coverage unchanged"],
            ["Internal, positive outcome noise", "Elimination", "180", "+0.050289", "+0.163131", "Coverage recovered; set widened in 180/180 cells"],
            ["External, all registered regions", "Disclosure", "60", "0.000000", "+0.129121", "Coverage unchanged; set widened"],
            ["External, all registered regions", "Elimination", "60", "0.000000", "+0.078111", "Coverage unchanged; set widened"],
            ["External, all registered regions", "Save", "60", "-0.841389", "-0.059959", "Coverage fell in 60/60 cells while the set narrowed"],
            ["External, all registered regions", "Tie handling", "60", "-0.072917", "+0.004666", "Coverage fell in 60/60 cells and the set widened on average"],
        ],
    )


def replace_section(
    text: str,
    start: str,
    end: str | None,
    replacement: str,
    location: str,
    evidence: str,
    log: list[dict[str, str]],
) -> str:
    start_index = text.index(start)
    end_index = len(text) if end is None else text.index(end, start_index)
    before = text[start_index:end_index].rstrip()
    replacement = replacement.strip()
    log.append(
        {
            "location": location,
            "before": before,
            "after": replacement,
            "evidence": evidence,
        }
    )
    suffix = "" if end is None else "\n\n"
    return text[:start_index] + replacement + suffix + text[end_index:]


def build_manuscript(root: Path) -> tuple[str, list[dict[str, str]]]:
    source_path = root / "outputs/stage26W/DSS_submission_draft_STAGE26W_source.md"
    if sha256(source_path) != SOURCE_SHA256:
        raise RuntimeError("Stage 26W source hash differs from the Stage 26X-2 locked input.")
    text = source_path.read_text(encoding="utf-8")
    log: list[dict[str, str]] = []
    t4 = table4(root)
    t5 = table5(root)
    t6 = table6(root)
    t7 = table7(root)

    abstract = """
## Abstract

Institutional aggregation often reveals expert scores, ranks, eliminations, or final outcomes while leaving public preferences latent. We formulate rule-conditioned feasible sets for this incomplete-observation problem: percentage rules produce cardinal support intervals through linear programming, whereas ranking and judge-save rules produce ordinal feasible-ranking sets under explicit tie and discretion assumptions. Twenty preregistered seeds span 12 internal parameter regions and three external rule structures. Rule-aware width is below the rule-agnostic comparator in 300/300 paired seed-parameter cells, as anticipated by the set nesting in Proposition 2. The empirical content is the cost of imposing those constraints and the conditions under which that cost appears. Positive outcome noise lowers rule-aware coverage in 180/180 internal cells by a mean 0.050289; removing the elimination constraint restores 0.050289 coverage while increasing width by 0.163131, whereas clean-cell coverage does not change when elimination is removed. In clean same-information comparisons, rule-aware intervals Pareto-dominate the Bayesian baseline in 0/120 cells, while Bayesian intervals dominate in 14/120 cells, all in the external seven-candidate, three-round region. The framework therefore characterizes feasible latent public preference, localizes a coverage-width tradeoff, and identifies parameter regions relevant to method selection; it does not assert that one inference method is uniformly preferred or that synthetic results establish user or organizational effects.

**Keywords:** Expert-crowd aggregation; latent public preference; partial identification; feasible support interval; coverage-width tradeoff; method selection.
"""
    text = replace_section(text, "## Abstract", "## 1. Introduction", abstract, "Abstract and keywords", "Stage 26X-1 robustness and Stage 26X-2 attribution", log)

    introduction = """
## 1. Introduction

Institutions and platforms often combine expert judgement with public input while disclosing only expert scores, rankings, eliminations, or final outcomes. When the public component is hidden, the same observed outcome can be compatible with multiple latent preference states, and a point estimate can conceal that ambiguity. The inferential problem is to characterize what the record and stated rule identify without treating latent public preference as an observed vote.

The central object is a feasible set of latent public preferences consistent with the observation process. Percentage aggregation induces a convex polytope of cardinal public-support vectors. Rank aggregation induces a set of feasible strict public rankings. A judge-save intervention weakens a direct elimination implication to tie-inclusive bottom-set membership. Because these mechanisms identify different mathematical objects, their uncertainty summaries are reported within regime and are not pooled into a common scale.

Figure 1 summarizes the inference architecture. Institutional evidence enters a rule-conditioned constraint layer; the output is a feasible set, sensitivity record, and explicit assumption boundary. The red boundary is substantive: hidden public preferences remain latent.

[[FIGURE 1]]

The study makes three contributions. First, it localizes a coverage-width tradeoff to the elimination constraint in the registered internal simulator: removing that constraint under positive outcome noise restores a mean 0.050289 coverage while increasing mean width by 0.163131, with no clean-cell coverage change. Second, it identifies a method-selection boundary: Bayesian intervals Pareto-dominate rule-aware intervals in 14/120 clean paired cells, all in the external seven-candidate, three-round region, while the reverse comparison occurs in 0/120 cells. Third, it supplies a formal partial-identification framework for rule-conditioned cardinal and ordinal feasible sets; the 300/300 width ordering is interpreted as the empirical realization of Proposition 2, not as an independently discovered performance gain.

The remainder of the paper positions the partial-identification problem, documents the empirical and synthetic evidence, defines the rule-conditioned feasible sets, reports the multi-seed baseline and ablation results, and states the conditions under which each method is informative.
"""
    text = replace_section(text, "## 1. Introduction", "## 2. Decision-Support Problem and Research Questions", introduction, "Section 1", "outputs/stage26X-1/ROBUSTNESS_ASSESSMENT.md; outputs/stage26X-2/ATTRIBUTION_RULING.md", log)

    problem = """
## 2. Inferential Problem and Research Questions

The observed record supplies the active candidate set, expert scores or ranks, outcome type, eliminated or withdrawn units, aggregation regime, tie policy, judge-save interpretation, and disclosure state. The analysis returns the identified object, feasible-set width or rank support, robustness diagnostics, and the conditions under which the result changes. Table 1 records the institutional alternatives and claim boundaries retained from the original design framing.

[[TABLE 1]]

The analysis addresses four research questions. **RQ1:** What cardinal or ordinal latent public-preference states remain feasible under each documented aggregation regime? **RQ2:** How does a weak judge-save implication change identifiability relative to direct elimination within the same rule environment? **RQ3:** Which registered constraint removals change coverage and width under clean and noisy synthetic outcomes? **RQ4:** How do rule-aware, rule-agnostic, maximum-entropy, and Bayesian methods compare when their observed information is aligned?

The framework does not choose an institution's normative objective, measure stakeholder welfare, or infer a true public vote from the empirical application. Its scope is the identified set and the method-selection boundary supported by the registered synthetic designs.

**Method-selection implication.** A method choice is conditioned on the observation rule, rule reliability, and the coverage-width objective rather than on a claim that one method applies uniformly.
"""
    text = replace_section(text, "## 2. Decision-Support Problem and Research Questions", "## 3. Related Work", problem, "Section 2", "Stage 26X-2 same-information comparison and attribution ruling", log)

    related31 = """
### 3.1 Partial identification and method selection under uncertainty

Partial identification represents all latent states consistent with observed information instead of selecting one unsupported state [8,9]. Decisions under incomplete identification can remain ambiguity-sensitive because unresolved states affect admissible actions [10]. The present framework uses this logic to compare rule-conditioned feasible sets, point centers, and posterior intervals while keeping their information sets and inferential meanings explicit.
"""
    text = replace_section(text, "### 3.1 Model-driven DSS under uncertainty", "### 3.2 Aggregation mechanisms and hidden preferences", related31, "Section 3.1", "References [8-10] and Stage 26X-2 information-set audit", log)

    related34 = """
### 3.4 Evaluation and research gap

Prediction, posterior inference, and partial identification answer different questions [11]. Existing aggregation studies do not by themselves establish how rule-conditioned set width, synthetic-truth coverage, and posterior intervals trade off when the recorded outcome rule may be violated. The gap addressed here is therefore comparative and conditional: align the observed information, report the structural nesting separately from empirical coverage, and identify the parameter regions in which the registered methods yield different coverage-width orderings.
"""
    text = replace_section(text, "### 3.4 Evaluation and research gap", "## 4. Data, Institutional Rules, and Evidence Scope", related34, "Section 3.4", "Stage 26X-2 ATTRIBUTION_RULING.md", log)

    evidence = """
### 4.3 Evidence hierarchy

The paper separates five evidence types: formal propositions; multi-seed known-truth synthetic calibration; a structurally different external synthetic testbed; a real empirical application with hidden truth; and artifact-level reproducibility checks. Formal claims establish conditional set relations. Synthetic evidence evaluates the registered methods under known simulators. The empirical application illustrates feasible sets consistent with observed outcomes. Artifact checks concern traceability and execution, not human usefulness, adoption, or organizational impact.

**Method-selection implication.** Every reported quantity is interpreted within its rule, simulator, and inferential object, preventing a synthetic or posterior quantity from being presented as an observed institutional outcome.
"""
    text = replace_section(text, "### 4.3 Evidence hierarchy", "## 5. Rule-Aware Partial-Identification Framework", evidence, "Section 4.3", "Stage 26X-1 and Stage 26X-2 registered evidence hierarchy", log)

    old_implication = "**Decision-support implication.** The formal model tells the decision maker which assumptions create information and which conclusions disappear when those assumptions are relaxed."
    new_implication = "**Method-selection implication.** The formal model identifies which assumptions remove states and which conclusions disappear when those assumptions are relaxed."
    if old_implication not in text:
        raise RuntimeError("Expected Section 5 implication was not found.")
    text = text.replace(old_implication, new_implication, 1)
    log.append({"location": "Section 5.5 implication", "before": old_implication, "after": new_implication, "evidence": "Propositions 1-4"})

    artifact = """
## 6. Reproducible Inference Artifact and Workflow

The implementation has a documented JSON input contract and structured output contract. Inputs record observed outcomes, active candidates, expert components, aggregation regime, tie policy, judge-save assumption, and disclosure state. The inference layer selects the mechanism-specific state space, encodes the registered constraints, checks feasibility, and computes bounds, feasible rankings, or comparator outputs.

Every run records the rule, tie treatment, disclosure state, evidence type, residual uncertainty, seed, and configuration. Figure 2 shows the auditable sequence from record encoding through feasible-state construction, baseline comparison, robustness analysis, and evidence export. The artifact is a reproducible research implementation; no user-effectiveness or organizational-outcome claim is attached to it.

[[FIGURE 2]]

**Method-selection implication.** The artifact makes the information set and assumption changes inspectable for each comparator.
"""
    text = replace_section(text, "## 6. DSS Artifact and Workflow", "## 7. Mechanism-Evaluation Modules", artifact, "Section 6", "outputs/stage26X-2/BASELINE_IMPLEMENTATION.md", log)

    mechanisms = """
## 7. Mechanism-Evaluation Modules

### 7.1 Discretion-identifiability frontier

Figure 3 is a deterministic synthetic nested-rule scenario. The horizontal positions represent direct, weak-save, and broader-save assumptions; they are not a historical estimate of intervention strength. Relaxing a bottom-set implication increases modeled flexibility and may increase feasible-rank width. The empirical R-plus record supports only the direct-versus-weak comparison defined by the documented mechanism.

[[FIGURE 3]]

**Method-selection implication.** Expert discretion changes the observation rule and therefore the identified set; the model does not assign welfare value to that change.

### 7.2 Compatible disclosure constraints

Figure 4 compares truthful, compatible synthetic disclosure additions to the same latent state space. Outcome-only and judge-rank records leave mean normalized width 0.844 in the scenario; top-$k$ disclosure reduces it to 0.739, while vote bins, pairwise relations, and margin intervals produce different reductions. The nesting claim applies only to compatible constraint addition.

[[FIGURE 4]]

The synthetic reductions relative to the outcome-only width are 12.5% for top-$k$ ranks, 88.3% for vote bins, and 92.7% for margin intervals. These are modeled information changes, not measured privacy, cost, trust, or organizational outcomes.

**Method-selection implication.** Disclosure constraints can be compared by the feasible states they remove, subject to compatibility with the baseline state space.

### 7.3 Rule Robustness Index

Figure 5 reports predeclared conclusion predicates, their supporting and applicable configurations, and RRI. All four evaluated conclusions have RRI 1.000 within their applicable configuration families. This statement is bounded by the registered configurations and does not establish welfare or method ranking.

[[FIGURE 5]]

**Method-selection implication.** RRI distinguishes persistence across the evaluated configuration family from claims about untested institutions.
"""
    text = replace_section(text, "## 7. Mechanism-Evaluation Modules", "## 8. Evaluation Design and Baselines", mechanisms, "Section 7", "Existing generated Figures 3-5 and Proposition 1", log)

    evaluation = f"""
## 8. Evaluation Design and Baselines

### 8.1 Declared information-set comparison

The comparison distinguishes set estimators from point estimators. Rule-aware and rule-agnostic sets share each generated case; rule constraints are added only to the rule-aware set. The maximum-entropy center is a zero-width point summary of the rule-aware polytope and is evaluated by point recovery and error, not interval coverage. The Bayesian baseline uses the same observed record with a registered prior and zero-one constraint likelihood. The synthetic oracle sees latent truth only for calibration.

{md_table(
        ["Method", "Observed information", "Output", "Permitted comparison"],
        [
            ["Rule-aware partial identification", "Expert component, coarse outcome, registered rule", "Feasible set", "Coverage and width within simulator"],
            ["Rule-agnostic partial identification", "Active state space without outcome-rule constraints", "Feasible set", "Structural nesting comparator"],
            ["Maximum-entropy center", "Same rule-aware feasible polytope", "Point", "Point error and top-choice accuracy only"],
            ["Bayesian latent-preference baseline", "Same observed record plus registered prior and zero-one likelihood", "Posterior interval", "Coverage-width comparison under the registered prior"],
            ["Full-disclosure oracle", "Synthetic latent truth", "Point", "Calibration boundary; synthetic only"],
        ],
    )}

### 8.2 Multi-seed internal benchmark

The internal percentage benchmark uses 20 preregistered seeds, active-set sizes 4, 5, and 6, outcome-noise probabilities 0, 0.05, 0.10, and 0.20, and 250 replications per seed-parameter cell. Outcome noise intentionally violates the generating rule. Seed-level means are summarized by the mean, median, sample standard deviation, and empirical 2.5%-97.5% interval; replications are not treated as independent seed-level observations.

### 8.3 Multi-seed external benchmark

The external ordinal simulator uses the same 20 seeds and three registered structures: six candidates with three rounds, seven candidates with three rounds, and seven candidates with four rounds. Each seed-structure cell has 120 replications. It varies candidate count, repeated eliminations, intervention, disclosure, and tie handling. Its purpose is to identify behavior within these structures, not to establish validity outside the simulators.
"""
    text = replace_section(text, "## 8. Evaluation Design and Baselines", "## 9. Results", evaluation, "Section 8 and Table 3", "outputs/stage26X-1/PREREGISTERED_DESIGN.md; outputs/stage26X-2/PREREGISTERED_DESIGN.md", log)

    results = f"""
## 9. Results

### 9.1 Internal coverage-width tradeoff

Table 4 and Figure 6 report the internal multi-seed distributions. Rule-aware width is below simplex-only width in 240/240 internal seed-parameter cells. This direction is the realized set nesting in Proposition 2; the table quantifies its magnitude and does not treat it as independent evidence of method ranking. In the 60 clean cells, rule-aware coverage is not below simplex-only coverage. In all 180 positive-noise cells, rule-aware coverage is lower; the mean decline is 0.050289, with median 0.044000 and empirical 2.5%-97.5% interval [0.012000, 0.108000].

**Table 4. Multi-seed internal coverage and width.** Values are seed-level mean, median, sample standard deviation, and empirical 2.5%-97.5% interval. Outcome-noise rows are synthetic misspecification stress tests.

{t4}

[[FIGURE 6]]

The leave-one-out ablation localizes this tradeoff within the registered simulator. Removing the elimination constraint in positive-noise cells changes coverage by +0.050289 and width by +0.163131 on average; coverage increases in 180/180 paired cells. Under zero outcome noise, removing elimination changes coverage in 0/60 cells. This is a paired synthetic mechanism localization, not a causal estimate for an observed institution. It supports a conditional rule: retain elimination constraints when the recorded elimination rule is treated as reliable; relax them when the analysis explicitly allows rule violation, accepting the wider feasible set.

### 9.2 External rule structure and component effects

Table 5 and Figure 7 report the external multi-seed distributions. Rule-aware and rule-agnostic ordinal sets have coverage 1.000 across the three registered structures, while direct-rule misspecification has lower coverage and nonzero false certainty. The result is conditional on the external simulator.

**Table 5. Multi-seed external coverage, width, and false certainty.** Values are seed-level mean, median, sample standard deviation, and empirical 2.5%-97.5% interval.

{t5}

[[FIGURE 7]]

### 9.3 Same-information baselines and method-selection boundary

Table 6 compares rule-aware and Bayesian intervals in the 120 clean paired seed-cells for which Pareto direction was registered. Rule-aware intervals Pareto-dominate Bayesian intervals in 0/120 cells. Bayesian intervals dominate in 14/120 cells, all in the external seven-candidate, three-round region. The remaining cells have no strict Pareto direction. The maximum-entropy center has zero point width by definition and is excluded from this interval Pareto comparison; its point metrics remain separately reported.

**Table 6. Clean same-information coverage-width Pareto comparison.** Pareto direction requires coverage no lower and width no higher, with at least one strict inequality.

{t6}

The fixed internal Bayesian draw bank produces 94 replication rows below the registered posterior-draw threshold, including 10 under zero outcome noise. All rows remain in the raw evidence; no bank was enlarged and no row was deleted. Coverage, width, posterior-center error, and top-choice means use rows with defined posterior intervals, while complete-denominator feasibility is reported separately. Excluding undefined intervals can change the Bayesian summaries, but the direction and magnitude cannot be determined without changing the registered draw design.

Across internal and external set comparisons, rule-aware width is below the rule-agnostic comparator in 300/300 paired seed-parameter cells. Proposition 2 supplies the direction of this result. The registered experiments quantify the widths, coverage costs, and method-selection boundary rather than establish a general ordering among inference methods.

### 9.4 Registered component effects

Table 7 reports leave-one-out effects. Removing save or tie handling lowers external coverage in 60/60 cells. Save removal also narrows the set on average, so it is not a one-dimensional loss; tie-handling removal widens it on average. Removing external disclosure or elimination leaves coverage unchanged while widening the set. No component interactions can be estimated because no joint removals were registered.

**Table 7. Registered component-removal effects.** Changes are component removed minus full configuration within paired seed-parameter cells.

{t7}

### 9.5 Longitudinal empirical application

The P regime has nonempty feasible regions in 247 of 248 eligible weeks and mean normalized coordinate-wise width 0.843. R and R-plus have mean normalized rank widths 0.891 and 0.924. These values are descriptive within regime and are not pooled as a causal cross-regime comparison. Within 73 R-plus weeks, the weak/direct feasible-set ratio averages 2.666, has median 1.572, is strictly greater than one in 56 weeks, equal in 17, and never smaller. These results instantiate Proposition 3 under the specified tie-inclusive bottom-$(k+1)$ interpretation.

The empirical record does not contain ground-truth public preferences. The results illustrate rule-assumption-conditioned feasible sets and identifiability loss consistent with observed outcomes, not recovered public preferences. The 11 missing typed proxies remain logged and are not imputed.

### 9.6 Reproducibility scope

Figure 8 summarizes deterministic evidence-completeness checks for traceability, robustness recording, output existence, and implementation reproducibility. These checks concern the research artifact. They are not scores of user effectiveness, adoption, trust, or organizational performance, and this study does not add a user experiment.

[[FIGURE 8]]
"""
    text = replace_section(text, "## 9. Results", "## 10. Decision-Support Recommendations", results, "Section 9 and Tables 4-7", "Stage 26X-1 tables and Stage 26X-2 baseline/ablation/attribution tables", log)

    implications = """
## 10. Method-Selection Implications

The results distinguish rule reliability from set-width preference. When elimination outcomes are generated consistently with the encoded rule, removing elimination does not change coverage in the 60 registered clean cells and widens the set. Under positive outcome noise, retaining elimination excludes generated truth in every registered cell; removing it recovers a mean 0.050289 coverage at a mean width cost of 0.163131. This conditional statement applies to the registered simulator and does not prescribe an institutional policy.

The Bayesian comparison supplies a second boundary. In the external seven-candidate, three-round region, Bayesian intervals have 14 strict Pareto dominances over rule-aware intervals and no reverse dominance is observed anywhere in the 120 clean comparison cells. In that region the registered evidence supports using the Bayesian comparator when its prior and likelihood are accepted. Outside that region, the registered Pareto test does not establish a strict direction, so method choice depends on whether prior-based posterior interpretation or assumption-transparent feasible-set interpretation is required.

Table 8 retains the conditional design matrix as an application aid, not an empirical welfare ranking.

[[TABLE 8]]

Table 9 aligns claims with evidence types and mandatory boundaries.

[[TABLE 9]]
"""
    text = replace_section(text, "## 10. Decision-Support Recommendations", "## 11. Discussion", implications, "Section 10 and table renumbering", "outputs/stage26X-2/ATTRIBUTION_RULING.md; outputs/stage26X-2/ABLATION_RESULTS.md", log)

    discussion = """
## 11. Discussion

The framework's contribution is a conditional account of method use under hidden public preference. Proposition 2 explains why valid rule constraints cannot expand a nested feasible set. The multi-seed experiments add information that the proposition does not provide: the coverage cost under rule violation, the component associated with that cost in a leave-one-out design, and the parameter region in which the registered Bayesian interval has a strict coverage-width ordering.

The central practical question is not why rule-aware inference should replace Bayesian inference. The registered evidence does not support that replacement. The contribution is to state when their assumptions and outputs differ: rule-aware feasible sets expose consequences of the encoded institutional rule without a probability model; Bayesian intervals provide a posterior summary under the registered prior and likelihood and have a strict Pareto direction in part of the external grid. The appropriate method follows from the accepted assumptions and inferential target.

The empirical application remains an illustration of feasible states under documented mechanisms. It supplies no ground-truth public vote and cannot validate the synthetic method ordering. The synthetic component results likewise locate behavior inside the registered generators rather than estimate causal institutional effects.
"""
    text = replace_section(text, "## 11. Discussion", "## 12. Limitations and Boundary Conditions", discussion, "Section 11", "Stage 26X-2 attribution ruling", log)

    limitations = """
## 12. Limitations and Boundary Conditions

First, the method does not recover exact hidden votes. The empirical application is an institutional testbed without a ground-truth public ballot, so its feasible sets cannot be scored for empirical recovery. Cardinal P widths and ordinal R/R-plus widths have different meanings and are not a common uncertainty scale.

Second, the synthetic findings are conditional on 20 preregistered seeds, the registered parameter grid, and two generators. The 300/300 width ordering follows the nesting condition in Proposition 2. The 180/180 positive-noise coverage loss and the elimination leave-one-out effect are stable within this grid but do not establish behavior under other misspecification processes or observed institutions.

Third, the component analysis removes one registered component at a time. It cannot identify two-way or higher-order interactions. External save removal lowers coverage while narrowing the set on average; therefore component effects cannot be reduced to a single benefit/loss scale.

Fourth, the Bayesian interval depends on the registered Dirichlet(1) or uniform-ranking prior and zero-one constraint likelihood. Other priors and likelihoods were not tested. The 94 insufficient-posterior replication rows, including 10 clean rows, have undefined interval metrics. Retaining them preserves the registered draw bank, but excluding undefined intervals from interval means can affect the Bayesian summary in a direction that cannot be determined from the current outputs.

Finally, no user, deployment, welfare, adoption, or organizational-effect claim is evaluated. This omission is handled by the method-focused positioning rather than by treating artifact checks as human evidence. Privacy, legal, ethical, and strategic consequences of disclosure remain outside the reported calculations.
"""
    text = replace_section(text, "## 12. Limitations and Boundary Conditions", "## 13. Conclusion", limitations, "Section 12", "Stage 26X-1 robustness; Stage 26X-2 baseline and ablation limitations", log)

    conclusion = """
## 13. Conclusion

Rule-conditioned partial identification represents latent public preference as a feasible set rather than an observed vote. The formal framework separates cardinal percentage aggregation from ordinal ranking and judge-save mechanisms and states the nesting conditions that generate width ordering.

The multi-seed evidence localizes a coverage-width tradeoff: under positive outcome noise, removing elimination recovers coverage in every registered cell while widening the set, whereas clean-cell coverage does not change. The same-information comparison does not show a general rule-aware ordering: Bayesian intervals dominate in 14/120 clean cells and the reverse occurs in 0/120. The resulting contribution is a method-selection account that links rule reliability, parameter region, and inferential assumptions to the choice between feasible-set and posterior summaries.
"""
    text = replace_section(text, "## 13. Conclusion", "## Data and Code Availability for Anonymized Review", conclusion, "Section 13", "Stage 26X-2 ATTRIBUTION_RULING.md", log)

    captions = """
## Figure Captions

**Figure 1. Rule-conditioned inference architecture under latent public preferences.** Institutional evidence is converted into rule-assumption-conditioned feasible sets and uncertainty diagnostics. The figure does not represent hidden preferences as observed.

**Figure 2. Reproducible inference workflow.** The sequence separates configuration, inference, comparison, robustness checks, and evidence export. It is not a deployed or user-validated workflow.

**Figure 3. Discretion-identifiability frontier.** Evidence type: deterministic synthetic nested-rule scenario. The positions are modeled rule relaxations, not a historical intervention-strength estimate.

**Figure 4. Value of compatible institutional disclosure.** Evidence type: synthetic compatible-disclosure scenario. Width changes follow truthful constraint addition within one state space; design scores are not measured trust, privacy, cost, or accountability outcomes.

**Figure 5. Rule Robustness Index across predeclared conclusions.** RRI is the bounded share of applicable evaluated configurations supporting a conclusion, not a method or welfare ranking.

**Figure 6. Multi-seed internal sensitivity.** Coverage and normalized width are summarized across 20 seeds; bands are empirical 2.5%-97.5% intervals of seed-level estimates. Outcome noise is a synthetic misspecification stress test.

**Figure 7. Multi-seed external sensitivity.** Coverage and normalized feasible-rank width are summarized across 20 seeds and three registered candidate-round structures; bands are empirical 2.5%-97.5% intervals.

**Figure 8. Artifact evidence-completeness checks.** The checks concern implementation completeness, traceability, and reproducibility, not user effectiveness, adoption, trust, or organizational impact.

## Table Notes

**Table 1. Institutional alternatives and use boundaries.** Retained as a design-context inventory; welfare, privacy, cost, legal fit, and implementation authority require local evidence.

**Table 2. Assumption inventory and claim boundaries.** Assumptions define the conditional identified object and the consequence of violation.

**Table 3. Baseline definitions and aligned information sets.** Point and interval outputs are evaluated by output-appropriate metrics; oracle access is synthetic-only.

**Table 4. Multi-seed internal coverage and width.** Outcome-noise rows are synthetic misspecification stress tests, not empirical error rates.

**Table 5. Multi-seed external coverage, width, and false certainty.** No real grant preference or organizational outcome is observed.

**Table 6. Clean same-information Pareto comparison.** Maximum-entropy point outputs are excluded because zero point width is not interval evidence.

**Table 7. Component-removal effects.** Effects are paired synthetic leave-one-out differences; interactions are not identified.

**Table 8. Conditional design matrix.** The matrix is not an empirical welfare ranking or automatic policy choice.

**Table 9. Claim-evidence alignment.** Each claim is bounded by its evidence type and stated limitation.
"""
    text = replace_section(text, "## Figure Captions", None, captions, "Figure captions and Table notes", "Stage 26X-1 Figures 6-7 and Stage 26X-2 attribution", log)
    return text.rstrip() + "\n", log


def report_contribution(root: Path) -> str:
    source = root / "outputs/stage26W/DSS_submission_draft_STAGE26W_source.md"
    claims = [
        (
            "Abstract (source line 5)",
            "In 250 replications at fixed seed 20260716, the no-noise rule-aware set has coverage 1.000 and mean normalized width 0.845, versus simplex-only coverage 1.000 and width 1.000.",
            "需改写为结构性与条件性表述",
            "Across 20 preregistered seeds, the 300/300 width ordering is reported as the realization of Proposition 2; the empirical result emphasized is the coverage cost under noise.",
        ),
        (
            "Section 9.1 (source line 209)",
            "Proposition 2 guarantees that valid added rule constraints cannot enlarge the set; the observed widths quantify the strict shrinkage in this simulator rather than establish its direction independently.",
            "需改写为结构性表述",
            "Rule-aware width is below the comparator in 300/300 cells, and this direction is attributed to Proposition 2 rather than to a performance ordering.",
        ),
        (
            "Section 9.1 implication (source line 217)",
            "The reported widths quantify that structural relation in this simulator; under outcome noise, the narrower rule-aware set has lower coverage than the simplex-only set.",
            "需改写为条件性表述",
            "Positive outcome noise lowers coverage in 180/180 cells; elimination removal recovers coverage while widening the set.",
        ),
        (
            "Conclusion (source line 279)",
            "Proposition 2 supplies the conditional set-non-expansion result; the synthetic benchmark reports the shrinkage magnitude and coverage under its stated simulator.",
            "需改写为结构性与方法选择表述",
            "The conclusion separates formal nesting from the empirical coverage-width cost and the Bayesian method-selection boundary.",
        ),
    ]
    rows = []
    for location, before, action, after in claims:
        rows.append([location, before, action, after])
    return f"""# Stage 26X-3 Contribution Repositioning

## Evidence lock

- Stage 26W source: `{source.as_posix()}`
- SHA256: `{sha256(source)}`
- Stage 26X-2 ruling: `RULE_AWARE_ADVANTAGE_STRUCTURAL_ONLY`
- No new experiment or numeric result is introduced by this stage.

## Repositioned contributions

1. **Coverage-width mechanism localization.** In the registered positive-noise grid, coverage is lower in `180/180` cells by mean `0.050289`. Removing elimination changes coverage by `+0.050289` and width by `+0.163131`; clean-cell coverage is unchanged in `60/60` cells. The operational statement is conditional on rule reliability and is not a real-world causal claim.
2. **Method-selection boundary.** Rule-aware intervals have Pareto dominance in `0/120` clean paired cells; Bayesian intervals dominate in `14/120`, all in the external `(7 candidates, 3 rounds)` region.
3. **Formal feasible-set framework.** Proposition 2 and the `300/300` width ordering are reported as a structural nesting result, not as an empirical method-ranking result.

## Audit of comparative formulations in the Stage 26W manuscript

The source contains no literal claim that rule-aware inference is uniformly preferred. The following comparative formulations could nevertheless be read as an ordering if detached from their boundaries, so each is rewritten.

{md_table(["位置", "修改前原文", "处置", "修改后表述"], rows)}

## Replacement titles

`AUTHOR_DECISION_REQUIRED`

1. Partial Identification of Latent Public Preferences under Institutional Aggregation Rules
2. Coverage-Width Tradeoffs in Rule-Constrained Expert-Crowd Aggregation
3. Choosing between Rule Constraints and Posterior Intervals under Hidden Preferences

The current title is retained in the Stage 26X-3 manuscript until the author selects one title.
"""


def report_negative_results() -> str:
    return """# Stage 26X-3 Negative Results Disclosure

## Disclosed results

| 位置 | 正文新增表述 | 依据 |
|---|---|---|
| Abstract; Sections 1 and 9.3; Conclusion | Rule-aware intervals Pareto-dominate Bayesian intervals in `0/120` clean paired cells. Bayesian intervals dominate in `14/120`, all in the external seven-candidate, three-round region. | `outputs/stage26X-2/ATTRIBUTION_RULING.md`; `outputs/stage26X-2/tables/attribution_pairwise_cells.csv` |
| Section 9.3; Section 12 | The fixed Bayesian draw bank has `94` insufficient-posterior replication rows, including `10` under zero outcome noise. All are retained; no resampling or deletion occurred. | `outputs/stage26X-2/BASELINE_IMPLEMENTATION.md` |
| Section 9.3; Section 12 | Interval metrics are undefined for those rows. Defined-posterior rows enter interval means and complete-denominator feasibility is reported separately. The impact direction and magnitude cannot be determined without changing the registered draw design. | `outputs/stage26X-2/BASELINE_IMPLEMENTATION.md`; `outputs/stage26X-2/ATTRIBUTION_RULING.md` |
| Abstract; Sections 1, 9.1, 9.3, 11, and 12 | Width is lower in `300/300` paired cells, with the direction attributed to Proposition 2 rather than an independent performance result. | `outputs/stage26X-1/ROBUSTNESS_ASSESSMENT.md`; Proposition 2 |

## Non-selective interpretation

- The `0/120` result is not attributed to the experimental grid or sample size.
- The `14/120` reverse direction is reported with its complete registered region.
- The maximum-entropy point baseline is not placed in an interval Pareto comparison because its zero width is a point-output definition.
- External save removal is not described as a one-dimensional loss: coverage falls in `60/60` cells while mean width also falls.
- Leave-one-out component results are described as synthetic mechanism localization; no real-world causal effect or component interaction is claimed.
"""


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def report_log(log: list[dict[str, str]]) -> str:
    rows = [
        [
            escape_cell(entry["location"]),
            escape_cell(entry["before"]),
            escape_cell(entry["after"]),
            escape_cell(entry["evidence"]),
        ]
        for entry in log
    ]
    return "# Stage 26X-3 Manuscript Repositioning Log\n\n" + md_table(
        ["位置", "修改前原文", "修改后原文", "依据文件"], rows
    )


def report_frozen_failure() -> str:
    return """# Stage 26X-3 Frozen Artifact Test Failure

## Test and reproduced mismatch

- Test: `tests/test_stage25he_finalization.py::test_docx_tables_match_condensed_source_matrices`
- Frozen DOCX: `submission_package_stage25/02_submission_files/DSS_anonymized_manuscript_STAGE25H_E_final.docx`
- Dynamic expectation: `scripts/25he_finalize_dss_submission_package.py::_docx_runtime()` -> `scripts/25he_repair_submission_assets.py::compact_tables()`
- Assertion: each of the seven DOCX tables must equal the table matrix produced by the current `compact_tables()` implementation.

| Table | Frozen DOCX | Current expectation | First differing cell |
|---|---|---|---|
| 3 | 6 rows x 4 columns, including `prediction only classifier` | 5 rows x 4 columns; `prediction_only_classifier` is filtered | Row 3, column 0: actual `prediction only classifier`; expected `Rule-agnostic set` |
| 4 | 7 rows x 6 columns, including `Prediction proxy` | 7 rows x 6 columns with the proxy omitted from the selected method list | Row 3, column 1: actual `Prediction proxy`; expected `Rule-agnostic set` |

Tables 1, 2, 5, 6, and 7 match.

## Cause ruling

The failure is caused by comparing a frozen Stage 25H-E DOCX against expectation logic that now reflects removal of the unsupported prediction-only baseline. The Table 3 filter and Table 4 selected-method list in `scripts/25he_repair_submission_assets.py` omit the two rows still present in the frozen DOCX. This is semantically consistent with the Stage 26W baseline removal. Because this workspace has no readable Git history, the exact process that changed the helper cannot be attributed from repository metadata.

Figure 6 is not read by this assertion and cannot cause the table-cell mismatch. The failure does not show corruption of the frozen DOCX; it shows that the test mixes a frozen artifact with a mutable expectation generator.

The default system Python currently stops at collection because `python-docx` is absent. The cell mismatch above was reproduced with the bundled document runtime used for DOCX inspection. This environment detail is separate from the stale expectation.

## Handling

`AUTHOR_DECISION_REQUIRED`

Update the test in a later maintenance stage so the frozen Stage 25H-E DOCX is compared with a frozen Stage 25H-E expectation snapshot, or explicitly version the expectation by stage. Do not modify the frozen DOCX and do not restore the unsupported baseline to the current manuscript.
"""


def report_journals() -> str:
    return """# Stage 26X-3 Target Journal Analysis

Retrieval date for all web sources: `2026-07-29`.

## 1. Group Decision and Negotiation

**Official scope.** “Approaches include (1) computer group decision and negotiation support systems (GDNSS), (2) artificial intelligence and management science, (3) applied game theory, experiment and social choice, and (4) cognitive/behavioral sciences in group decision and negotiation. ... The journal provides a publication vehicle for theoretical and empirical research, and real-world applications and case studies.” Source: https://link.springer.com/journal/10726/aims-and-scope

**Contribution mapping.** The coverage-width localization fits group-decision mechanism analysis; the Bayesian boundary fits method selection under incomplete information; the formal feasible-set result fits social choice and management-science theory.

**Recent-content evidence.** The official article list includes “Preference-Approval Structures and Opportunity Sets” (https://link.springer.com/article/10.1007/s10726-026-10002-3), a formal preference-structure paper, and “Evaluating Decision-Making in Large Language Models Under Risk and Uncertainty: Expected Utility Violations in ChatGPT, Claude and DeepSeek” (https://link.springer.com/article/10.1007/s10726-026-10006-z), whose title centers violations rather than a one-sided performance claim. These examples support theoretical work and adverse/boundary findings, but the journal does not state a blanket policy for negative-result papers.

**Remaining objections.** The empirical testbed is entertainment-platform data rather than negotiation behavior; the manuscript must make the group aggregation mechanism, not the platform, the object of study. The current title and Figures 1-2 retain DSS language pending author/title migration.

**Metrics and classification.** `AUTHOR_MUST_VERIFY`: verify the submission-year JCR category/quartile and the current Chinese Academy of Sciences partition; no metric value is asserted here.

## 2. Annals of Operations Research

**Official scope.** “The Annals of Operations Research publishes peer-reviewed original articles dealing with some aspects of operations research, including theory, practice, and computation. Submissions may include full-length research articles, short notes, expositions and surveys, reports on computational studies, and case studies of new or innovative practical applications.” Source: https://link.springer.com/journal/10479/aims-and-scope

**Contribution mapping.** The formal identified-set construction maps to theory; the registered multi-seed and leave-one-out analyses map to computational studies; the method boundary maps to practice-oriented method choice.

**Recent-content evidence.** The official article list includes “Risk-aware trading portfolio optimization” (https://link.springer.com/article/10.1007/s10479-026-07323-6) and “Integrated super-efficiency models for network systems: from slack-based measure to unified analysis framework” (https://link.springer.com/article/10.1007/s10479-026-07330-7). These show current publication of risk-conditioned optimization and framework papers. Neither example establishes a general negative-results policy.

**Remaining objections.** The formal results may be viewed as direct set-inclusion consequences unless the coverage mechanism localization and Bayesian boundary are foregrounded. The empirical application has no observed latent truth.

**Metrics and classification.** `AUTHOR_MUST_VERIFY`: verify the submission-year JCR category/quartile and Chinese Academy of Sciences partition.

## 3. European Journal of Operational Research

**Official scope.** “The European Journal of Operational Research (EJOR) publishes high quality, original papers that contribute to the methodology of operational research (OR) and to the practice of decision making.” It lists “Theory and Methodology Papers” and includes “Decision Support” and “Interfaces with Other Disciplines.” Source: https://www.sciencedirect.com/journal/european-journal-of-operational-research/about/aims-and-scope

**Contribution mapping.** Feasible-set characterization maps to theory and methodology; coverage-width localization maps to stochastics/statistics and decision support; the expert-crowd mechanism maps to interfaces with social choice.

**Recent-content evidence.** The official article records include “Decomposition algorithms for computational stochastic mixed-integer programming: A survey” (https://www.sciencedirect.com/science/article/pii/S0377221726005072) and “The parallel stack loading problem: Polynomial solvability in the unlimited-capacity case and exact approaches for the finite-capacity case” (https://www.sciencedirect.com/science/article/pii/S0377221726002328). These examples indicate a high formal and computational threshold; they do not demonstrate acceptance of negative-result-led manuscripts as a category.

**Remaining objections.** Proposition 2 is structurally direct, no independent implementation comparison is reported, and Bayesian reverse dominance can prompt a request for a broader prior/likelihood sensitivity study. This is the highest editorial-fit risk among the top three.

**Metrics and classification.** `AUTHOR_MUST_VERIFY`: verify the submission-year JCR category/quartile and Chinese Academy of Sciences partition.

## 4. Computers & Operations Research

**Official scope.** The journal covers “Decision-Making under Uncertainty and Data Analytics” and publishes work in “theories, modeling, algorithms, and applications of Operations Research.” It also states: “All full-length research papers published in the journal must demonstrate constructive algorithmic complexity and extensive numerical experiments. Numerical illustrations (examples) are not sufficient: the numerical experiments must have a scientific value of their own, particularly with comparisons to other approaches.” Source: https://www.sciencedirect.com/journal/computers-and-operations-research/about/aims-and-scope

**Contribution mapping.** The framework maps to modeling under uncertainty; the 20-seed grid and Bayesian comparison map to numerical comparison; the constraint implementation maps to computation.

**Recent-content evidence.** The official article record includes “Instance scaling and metamodel-based sensitivity analysis for rolling horizon optimization with application to postal letter delivery services” (https://www.sciencedirect.com/science/article/pii/S0305054826002303), showing sensitivity analysis as part of a computational optimization contribution. The official scope does not say that negative-result-led papers are accepted as a category.

**Remaining objections.** The current paper does not claim a new optimization algorithm or constructive complexity result, and the registered grid may be judged narrower than the journal's “extensive numerical experiments” requirement. The structural-only ruling weakens this match.

**Metrics and classification.** `AUTHOR_MUST_VERIFY`: verify the submission-year JCR category/quartile and Chinese Academy of Sciences partition.

## 5. Socio-Economic Planning Sciences

**Official scope.** The journal “strongly encourages contributions dealing with applications of quantitative models and techniques to important decision problems in the service and public sectors.” It requires importance or uniqueness in methodology, application, or problem context. Source: https://www.sciencedirect.com/journal/socio-economic-planning-sciences/about/aims-and-scope

**Contribution mapping.** The formal framework maps to quantitative methodology, and institutional aggregation could map to public-sector allocation only if the application is actually public/service sector. The current empirical testbed does not establish that context.

**Recent-content evidence.** The official article records include “Life expectancy and its determinants: A machine learning analysis with implications for policy interventions” (https://www.sciencedirect.com/science/article/pii/S0038012126000996) and “Optimizing facility locations and shuttle routes for senior welfare centers in aging societies: A priority-based approach” (https://www.sciencedirect.com/science/article/pii/S0038012126001023). These examples reinforce the public/service-sector application emphasis rather than a negative-results genre.

**Remaining objections.** The current application lacks a public-policy or service-delivery decision problem, so the scope fit depends on a context the evidence does not supply. No such context should be inferred.

**Metrics and classification.** `AUTHOR_MUST_VERIFY`: verify the submission-year JCR category/quartile and Chinese Academy of Sciences partition.

## Recommended order

1. **Group Decision and Negotiation**: direct subject match for group aggregation, preference structures, social choice, and theoretical/empirical work.
2. **Annals of Operations Research**: broad acceptance of theory and computational studies, with less dependence on a new algorithmic-complexity claim.
3. **European Journal of Operational Research**: formal scope match but a higher threshold for methodological contribution and robustness.
4. **Computers & Operations Research**: uncertainty/computation fit, offset by the explicit algorithmic-complexity and extensive-experiment requirement.
5. **Socio-Economic Planning Sciences**: quantitative-method fit, but current evidence lacks its public/service-sector problem context.

最终选择由作者决定。期刊指标、JCR 分区与中科院分区均须由作者按投稿年度核实。
"""


def report_verdict() -> str:
    return """# Stage 26X-3 Submission Verdict V2

## Verdict

`READY_WITH_REPOSITIONED_CONTRIBUTION`

This verdict means the evidence package can enter target-journal selection and format migration. It does not mean acceptance is predicted, and it does not assert any journal metric or quartile.

## Comparison with Stage 26S

| Stage 26S issue | Current status | Evidence |
|---|---|---|
| Single seed; no interval or distribution | Resolved for the registered synthetic designs | 20 preregistered seeds; 300 paired seed-parameter cells; Tables 4-5 and Figures 6-7 report seed-level distributions and empirical intervals |
| Unsupported prediction-only alias | Resolved by removal; not restored | Stage 26W removal logs; Stage 26X-1 confirms absence |
| No same-information competitive baseline | Resolved for registered maximum-entropy and Bayesian baselines | Independent implementations, raw outputs, and logs in Stage 26X-2 |
| No component ablation | Resolved as registered leave-one-out localization; interactions remain unidentified | Stage 26X-2 Table 7 and ablation report |
| Structural width result presented as method gain | Resolved by repositioning | `RULE_AWARE_ADVANTAGE_STRUCTURAL_ONLY`; 0/120 reverse comparison disclosed |
| No user/deployment validation for decision-effect claims | No experiment added; the unsupported effect claim and DSS target are abandoned | Manuscript states no user, deployment, welfare, adoption, or organizational-effect claim |

## Core contribution in three sentences

The paper formalizes rule-conditioned feasible sets for latent public preference under cardinal and ordinal expert-crowd aggregation. It localizes a registered synthetic coverage-width tradeoff to elimination constraints and quantifies the effect across 20 seeds. It identifies a parameter region in which the registered Bayesian interval has a strict Pareto direction, making the contribution about method selection rather than general method ranking.

## Journal-tier assessment

The evidence is coherent enough for editorial review at a scope-matched methods journal: the formal object, multi-seed distributions, independent baselines, adverse comparisons, raw evidence, and limitation boundaries are all present. Whether this supports a JCR Q1 venue cannot be determined from internal evidence alone; `AUTHOR_MUST_VERIFY` applies to the current JCR and Chinese Academy of Sciences classifications, and editorial contribution thresholds remain journal-specific. Group Decision and Negotiation has the closest documented scope; Annals of Operations Research is the second match.

## Remaining risks

1. A paper centered on an adverse comparison and a conditional tradeoff may be judged less substantial than a new method-ranking result.
2. The 94 insufficient-posterior replication rows, including 10 clean rows, can prompt questions about Bayesian summary sensitivity. The impact direction is not identified under the locked draw bank.
3. Reviewers may ask why Bayesian inference is not used directly. The response is: the paper characterizes when the registered posterior interval or assumption-transparent feasible set is informative; it does not claim one is uniformly preferred. Bayesian intervals have the recorded strict direction in the external seven-candidate, three-round region, while rule-aware sets expose consequences of institutional rule assumptions without a probability model.
4. The leave-one-out design does not identify component interactions or real-world causal effects.
5. The empirical application has no observed latent public preference and remains illustrative.
6. The current title and Figures 1-2 retain DSS-oriented language. Title selection and visual migration require author action after the target journal is chosen.

## Author decisions before format migration

- Select one target journal after verifying current metrics and classifications.
- Select the manuscript title; three alternatives are recorded in `CONTRIBUTION_REPOSITIONING.md`.
"""


def generate(root: Path, output_dir: Path) -> None:
    root = root.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    unexpected = [path for path in output_dir.iterdir() if path.name not in OUTPUT_NAMES]
    if unexpected:
        raise RuntimeError(
            "Output directory contains files outside the Stage 26X-3 contract: "
            + ", ".join(path.name for path in unexpected)
        )

    manuscript, log = build_manuscript(root)
    write_text(output_dir / "METHODS_submission_draft_STAGE26X3_source.md", manuscript)
    write_text(output_dir / "CONTRIBUTION_REPOSITIONING.md", report_contribution(root))
    write_text(output_dir / "NEGATIVE_RESULTS_DISCLOSURE.md", report_negative_results())
    write_text(output_dir / "MANUSCRIPT_REPOSITIONING_LOG.md", report_log(log))
    write_text(output_dir / "FROZEN_ARTIFACT_TEST_FAILURE.md", report_frozen_failure())
    write_text(output_dir / "TARGET_JOURNAL_ANALYSIS.md", report_journals())
    write_text(output_dir / "SUBMISSION_VERDICT_V2.md", report_verdict())

    for number, stem in ((6, "internal"), (7, "external")):
        for suffix in ("png", "pdf"):
            source = root / "outputs/stage26X-1" / f"Figure_{number:02d}_multiseed_{stem}_sensitivity.{suffix}"
            target = output_dir / source.name
            shutil.copyfile(source, target)
            if sha256(source) != sha256(target):
                raise RuntimeError(f"Figure copy hash mismatch: {target}")

    observed = {path.name for path in output_dir.iterdir()}
    if observed != OUTPUT_NAMES:
        raise RuntimeError(f"Stage 26X-3 output contract mismatch: {sorted(observed)}")


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    output_dir = args.output_dir or root / "outputs/stage26X-3"
    generate(root, output_dir)
    print(f"STAGE26X3_OUTPUT_DIR = {output_dir}")


if __name__ == "__main__":
    main()
