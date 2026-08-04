#!/usr/bin/env python3
"""Build rule-aware season-week constraint representations."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.constraints import (  # noqa: E402
    build_judge_save_constraints,
    build_percentage_constraints,
    build_ranking_constraints,
    check_feasibility,
    save_constraint_set,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Construct percentage-regime linear constraints and register "
            "ranking/judge-save framework status for every season-week."
        )
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--panel", type=Path, default=Path("data/processed/panel_long.csv")
    )
    parser.add_argument(
        "--week-level", type=Path, default=Path("data/processed/week_level.csv")
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("outputs/tables/constraint_summary.csv"),
    )
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=Path("outputs/models/constraints"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("outputs/logs/constraint_report.md"),
    )
    return parser.parse_args()


def resolve(path: Path, root: Path) -> Path:
    return path if path.is_absolute() else root / path


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().casefold() in {"true", "1", "yes"}


def markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    def clean(value: Any) -> str:
        if pd.isna(value):
            return ""
        return str(value).replace("|", "\\|").replace("\n", " ")

    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    output.extend("| " + " | ".join(clean(value) for value in row) + " |" for row in rows)
    return "\n".join(output)


def build_report(summary: pd.DataFrame, models_dir: Path) -> str:
    p_rows = summary.loc[summary["regime"].eq("P")]
    p_built = p_rows.loc[~p_rows["skipped"]]
    p_skipped = p_rows.loc[p_rows["skipped"]]
    infeasible = p_built.loc[p_built["feasible"].eq(False)]  # noqa: E712
    skip_counts = p_skipped["skip_reason"].value_counts()
    event_counts = p_rows["constraint_type"].value_counts()
    lines = [
        "# Constraint Construction Report",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Coverage",
        "",
        markdown_table(
            ["Metric", "Count"],
            [
                ("All season-weeks processed", len(summary)),
                ("R ordinal-specification weeks", int(summary["regime"].eq("R").sum())),
                ("P weeks", len(p_rows)),
                ("R_plus weak-specification weeks", int(summary["regime"].eq("R_plus").sum())),
                ("P weeks with matrices built", len(p_built)),
                ("P weeks skipped", len(p_skipped)),
                ("P infeasible weeks", len(infeasible)),
                ("Saved P matrix files", int(p_built["model_path"].ne("").sum())),
                ("Total P outcome inequalities", int(p_built["n_inequalities"].sum())),
            ],
        ),
        "",
        f"Matrices are stored under `{models_dir}`. Every file contains the explicit "
        "variable order, contestant names, normalized judge shares, inequality and "
        "equality matrices, and variable bounds.",
        "",
        "## P-regime event handling",
        "",
        markdown_table(
            ["Constraint type", "Weeks"],
            ((event, int(count)) for event, count in event_counts.items()),
        ),
        "",
        "For a directly eliminated contestant e and each non-withdrawn survivor i, the implementation adds",
        "",
        "`F_e - F_i <= J_i / sum(J) - J_e / sum(J)`.",
        "",
        "A multiple-elimination week uses the conservative Cartesian set of eliminated-versus-survivor comparisons and imposes no ordering within the eliminated group. A finale with unique active-finalist placements uses every pairwise placement order as a strong combined-score inequality. If a finale placement mapping were missing or non-unique, the implementation would retain only the simplex and record that decision rather than invent an order.",
        "",
        "A withdrawal is excluded from both the eliminated set and the survivor comparison set because leaving the process does not reveal that contestant's combined-score rank. No-elimination and withdrawal-only weeks therefore add no outcome inequality; their feasible set is the full simplex.",
        "",
        "## Feasibility and skips",
        "",
    ]
    if p_skipped.empty:
        lines.extend(["No P-regime week was skipped.", ""])
    else:
        lines.extend(
            [
                markdown_table(
                    ["Skip reason", "Weeks"],
                    ((reason, int(count)) for reason, count in skip_counts.items()),
                ),
                "",
            ]
        )
    if infeasible.empty:
        lines.extend(["No constructed P-regime week was infeasible.", ""])
    else:
        lines.extend(
            [
                "Infeasible P weeks:",
                "",
                markdown_table(
                    ["Season", "Week", "LP message"],
                    infeasible[["season", "week", "lp_message"]].itertuples(
                        index=False, name=None
                    ),
                ),
                "",
            ]
        )
    lines.extend(
        [
            "A P week is skipped if it has fewer than two active contestants, a missing active `judge_total`, a nonpositive weekly judge-total denominator, or an observed eliminated contestant who is outside the active scoring set and therefore lacks a usable preference variable and judge total. These conditions are checked before optimization.",
            "",
            "## Why the P feasible set is a convex polytope",
            "",
            "Public preference shares lie in the bounded simplex `F >= 0` and `sum(F)=1`. Every observed percentage-aggregation outcome contributes finitely many affine half-space inequalities. The intersection of the simplex with those closed half-spaces is therefore a bounded convex polyhedron, hence a convex polytope whenever nonempty. Feasibility is checked numerically with `scipy.optimize.linprog(method='highs')`.",
            "",
            "## Ordinal regime interfaces",
            "",
            "R weeks are validated as direct ordinal ranking specifications, and R_plus weeks are validated under the conservative tie-inclusive bottom-(k+1) judge-save rule. This stage does not assign fabricated cardinal inequalities to either ordinal regime. Exact enumeration, fixed-seed sampling, and ranking-uncertainty calculations are performed by `scripts/05_ranking_identification.py`.",
            "",
            "## Generated artifacts",
            "",
            "- `outputs/tables/constraint_summary.csv`",
            "- `outputs/models/constraints/*.npz`",
            "- `outputs/logs/constraint_report.md`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = args.project_root.resolve()
    panel_path = resolve(args.panel, root)
    week_path = resolve(args.week_level, root)
    summary_path = resolve(args.summary, root)
    models_dir = resolve(args.models_dir, root)
    report_path = resolve(args.report, root)
    missing = [str(path) for path in (panel_path, week_path) if not path.is_file()]
    if missing:
        print(f"ERROR: Missing processed input(s): {', '.join(missing)}", file=sys.stderr)
        print("Run scripts/02_preprocess.py first.", file=sys.stderr)
        return 2

    try:
        panel = pd.read_csv(panel_path)
        week_level = pd.read_csv(week_path)
        if panel.duplicated(["season", "week", "contestant_id"]).any():
            raise ValueError("panel_long has duplicate season-week-contestant keys.")
        if week_level.duplicated(["season", "week"]).any():
            raise ValueError("week_level has duplicate season-week keys.")
        panel_keys = set(map(tuple, panel[["season", "week"]].drop_duplicates().to_numpy()))
        week_keys = set(map(tuple, week_level[["season", "week"]].to_numpy()))
        if panel_keys != week_keys:
            raise ValueError("panel_long and week_level season-week keys do not match.")

        models_dir.mkdir(parents=True, exist_ok=True)
        for existing_model in models_dir.glob("season_*_week_*.npz"):
            existing_model.unlink()

        summary_rows: list[dict[str, Any]] = []
        for week_row in week_level.sort_values(["season", "week"]).itertuples(index=False):
            season = int(week_row.season)
            week = int(week_row.week)
            regime = str(week_row.aggregation_regime)
            week_df = panel.loc[
                panel["season"].eq(season) & panel["week"].eq(week)
            ].copy()
            active = week_df.loc[week_df["active_status"].map(as_bool)]
            base = {
                "season": season,
                "week": week,
                "regime": regime,
                "n_active": len(active),
                "n_eliminated": int(
                    week_df["eliminated_this_week"].map(as_bool).sum()
                ),
                "no_elimination_week": as_bool(week_row.no_elimination_week),
                "double_elimination_week": as_bool(week_row.double_elimination_week),
                "withdrew_count": int(
                    week_df["withdrew_this_week"].map(as_bool).sum()
                ),
                "finale_week": as_bool(week_row.finale_week),
                "judge_total_sum": float(active["judge_total"].sum()),
            }
            if regime == "P":
                constraints = build_percentage_constraints(week_df)
                if constraints.skipped:
                    summary_rows.append(
                        {
                            **base,
                            "n_variables": constraints.n_variables,
                            "n_inequalities": constraints.n_inequalities,
                            "n_equalities": constraints.n_equalities,
                            "constraint_type": constraints.event_type,
                            "construction_status": "skipped",
                            "feasible": pd.NA,
                            "skipped": True,
                            "skip_reason": constraints.skip_reason,
                            "lp_status": pd.NA,
                            "lp_message": "",
                            "model_path": "",
                            "constraint_note": constraints.constraint_note,
                        }
                    )
                    continue
                feasibility = check_feasibility(
                    constraints.A_ub,
                    constraints.b_ub,
                    constraints.A_eq,
                    constraints.b_eq,
                    constraints.bounds,
                )
                model_path = models_dir / f"season_{season:02d}_week_{week:02d}.npz"
                save_constraint_set(constraints, model_path)
                try:
                    model_reference = model_path.relative_to(root).as_posix()
                except ValueError:
                    model_reference = str(model_path)
                summary_rows.append(
                    {
                        **base,
                        "n_variables": constraints.n_variables,
                        "n_inequalities": constraints.n_inequalities,
                        "n_equalities": constraints.n_equalities,
                        "constraint_type": constraints.event_type,
                        "construction_status": (
                            "built_feasible" if feasibility.feasible else "built_infeasible"
                        ),
                        "feasible": feasibility.feasible,
                        "skipped": False,
                        "skip_reason": "",
                        "lp_status": feasibility.status,
                        "lp_message": feasibility.message,
                        "model_path": model_reference,
                        "constraint_note": constraints.constraint_note,
                    }
                )
            else:
                framework = (
                    build_ranking_constraints(week_df)
                    if regime == "R"
                    else build_judge_save_constraints(week_df)
                )
                summary_rows.append(
                    {
                        **base,
                        "n_variables": len(active),
                        "n_inequalities": 0,
                        "n_equalities": 0,
                        "constraint_type": framework["constraint"],
                        "construction_status": framework["status"],
                        "feasible": pd.NA,
                        "skipped": False,
                        "skip_reason": "",
                        "lp_status": pd.NA,
                        "lp_message": "",
                        "model_path": "",
                        "constraint_note": (
                            "Validated ordinal week specification; no cardinal constraint fabricated."
                        ),
                    }
                )

        summary = pd.DataFrame(summary_rows)
        if len(summary) != len(week_level):
            raise ValueError("Constraint summary row count does not match week_level.")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        summary.to_csv(
            summary_path,
            index=False,
            encoding="utf-8",
            na_rep="",
            lineterminator="\n",
            float_format="%.12g",
        )
        report_path.write_text(
            build_report(summary, models_dir), encoding="utf-8", newline="\n"
        )
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    p_rows = summary.loc[summary["regime"].eq("P")]
    print(f"constraint_summary.csv: {len(summary)} season-weeks")
    print(
        f"P regime: {len(p_rows)} weeks, "
        f"{int((~p_rows['skipped']).sum())} built, "
        f"{int(p_rows['skipped'].sum())} skipped, "
        f"{int(p_rows['feasible'].eq(False).sum())} infeasible"
    )
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
