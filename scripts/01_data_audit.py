#!/usr/bin/env python3
"""Audit the supplied expert-crowd competition data without modifying it.

The source is read twice: once with pandas' missing-value parsing and once as
raw strings. This preserves the distinction between numeric zero, parsed NaN,
empty fields, and explicit tokens such as ``N/A``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import unicodedata
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover - depends on runtime setup
    raise SystemExit(
        "pandas is required. Install pandas>=2.0 and rerun this command."
    ) from exc


SCORE_COLUMN_RE = re.compile(
    r"^week(?P<week>\d+)_judge(?P<judge>\d+)_score$", re.IGNORECASE
)
ELIMINATION_WEEK_RE = re.compile(
    r"\beliminat(?:ed|ion)\s*(?:in\s*)?week\s*(?P<week>\d+)\b",
    re.IGNORECASE,
)
EXPLICIT_WEEK_RE = re.compile(r"\bweek\s*(?P<week>\d+)\b", re.IGNORECASE)
WITHDRAWAL_RE = re.compile(r"\bwithdrew\b|\bwithdrawn\b", re.IGNORECASE)
PARTNER_REPLACEMENT_RE = re.compile(
    r"\bweek\s*\d+\b|\breplac(?:ed|ement)\b|\bsubstitut(?:e|ed|ion)\b",
    re.IGNORECASE,
)

FIELD_ALIASES = {
    "season": ("season", "season_number"),
    "week": ("week", "week_number"),
    "contestant": (
        "contestant",
        "contestant_name",
        "celebrity_name",
        "celebrity",
        "name",
    ),
    "placement": ("placement", "final_placement", "rank", "final_rank"),
    "results": ("results", "result", "outcome", "decision_outcome"),
    "partner": ("ballroom_partner", "partner", "partner_name"),
}

# Raw tokens are counted independently of pandas' parsed NaN values.
SPECIAL_TOKENS = {
    "n/a",
    "na",
    "nan",
    "null",
    "none",
    "missing",
    "not available",
    "-",
    "--",
    ".",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit source data and generate column, season-week, event, score, "
            "partner, and repeated-contestant diagnostics."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root (default: parent of the scripts directory).",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="CSV input. Relative paths are resolved from --project-root.",
    )
    parser.add_argument(
        "--tables-dir",
        type=Path,
        default=Path("outputs/tables"),
        help="Output table directory, relative to the project root by default.",
    )
    parser.add_argument(
        "--logs-dir",
        type=Path,
        default=Path("outputs/logs"),
        help="Output log directory, relative to the project root by default.",
    )
    return parser.parse_args()


def resolve_from_root(path: Path, root: Path) -> Path:
    return path if path.is_absolute() else root / path


def discover_input(project_root: Path, requested: Path | None) -> Path:
    if requested is not None:
        candidate = resolve_from_root(requested, project_root).resolve()
        if not candidate.is_file():
            raise FileNotFoundError(f"Input file not found: {candidate}")
        return candidate

    raw_dir = project_root / "data" / "raw"
    candidates = sorted(
        path
        for path in raw_dir.glob("*.csv")
        if path.is_file() and "template" not in path.name.casefold()
    )
    if len(candidates) == 1:
        return candidates[0].resolve()
    if not candidates:
        raise FileNotFoundError(
            f"No CSV source found under {raw_dir}. Supply --input explicitly."
        )
    names = ", ".join(path.name for path in candidates)
    raise RuntimeError(
        f"Multiple CSV sources found under {raw_dir}: {names}. "
        "Select one with --input."
    )


def detect_text_settings(path: Path) -> tuple[str, str, str]:
    raw = path.read_bytes()
    encoding = ""
    decoded = ""
    for candidate in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            decoded = raw.decode(candidate)
            encoding = candidate
            break
        except UnicodeDecodeError:
            continue
    if not encoding:
        raise UnicodeError(f"Unable to decode {path} with supported encodings.")

    sample = decoded[:65536]
    try:
        delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        delimiter_note = "detected by csv.Sniffer"
    except csv.Error:
        delimiter = ","
        delimiter_note = "fallback to comma after delimiter detection failed"
    return encoding, delimiter, delimiter_note


def load_csv(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]:
    encoding, delimiter, delimiter_note = detect_text_settings(path)
    parsed = pd.read_csv(path, encoding=encoding, sep=delimiter)
    raw = pd.read_csv(
        path,
        encoding=encoding,
        sep=delimiter,
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )
    if parsed.shape != raw.shape or list(parsed.columns) != list(raw.columns):
        raise ValueError("Parsed and raw-string reads produced different schemas.")
    settings = {
        "encoding": encoding,
        "delimiter": repr(delimiter),
        "delimiter_note": delimiter_note,
    }
    return parsed, raw, settings


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def normalized_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def resolve_fields(columns: Iterable[str]) -> dict[str, str | None]:
    normalized_columns = {normalized_label(column): column for column in columns}
    resolved: dict[str, str | None] = {}
    for field, aliases in FIELD_ALIASES.items():
        resolved[field] = next(
            (
                normalized_columns[normalized_label(alias)]
                for alias in aliases
                if normalized_label(alias) in normalized_columns
            ),
            None,
        )
    return resolved


def score_metadata(columns: Iterable[str]) -> list[dict[str, Any]]:
    metadata: list[dict[str, Any]] = []
    for column in columns:
        match = SCORE_COLUMN_RE.fullmatch(column)
        if match:
            metadata.append(
                {
                    "column": column,
                    "week": int(match.group("week")),
                    "judge": int(match.group("judge")),
                }
            )
    return sorted(metadata, key=lambda item: (item["week"], item["judge"]))


def scalar(value: Any) -> Any:
    if pd.isna(value):
        return ""
    if hasattr(value, "item"):
        return value.item()
    return value


def markdown_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    def clean(value: Any) -> str:
        return str(scalar(value)).replace("|", "\\|").replace("\n", " ")

    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    output.extend("| " + " | ".join(clean(value) for value in row) + " |" for row in rows)
    return "\n".join(output)


def audit(
    parsed: pd.DataFrame,
    raw: pd.DataFrame,
    source: Path,
    settings: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    summary_rows: list[dict[str, Any]] = []
    special_rows: list[dict[str, Any]] = []

    def add_summary(
        section: str,
        metric: str,
        value: Any,
        *,
        column: str = "",
        season: Any = "",
        week: Any = "",
        details: str = "",
    ) -> None:
        summary_rows.append(
            {
                "section": section,
                "metric": metric,
                "column": column,
                "season": season,
                "week": week,
                "value": scalar(value),
                "details": details,
            }
        )

    def add_special(
        case_type: str,
        *,
        season: Any = "",
        week: Any = "",
        contestant_name: Any = "",
        column: str = "",
        raw_value: Any = "",
        details: str = "",
    ) -> None:
        special_rows.append(
            {
                "case_type": case_type,
                "season": scalar(season),
                "week": scalar(week),
                "contestant_name": scalar(contestant_name),
                "column": column,
                "raw_value": scalar(raw_value),
                "details": details,
            }
        )

    fields = resolve_fields(parsed.columns)
    scores = score_metadata(parsed.columns)
    score_columns = [item["column"] for item in scores]
    score_weeks = sorted({item["week"] for item in scores})
    judge_ids = sorted({item["judge"] for item in scores})
    score_lookup = {
        week: [item["column"] for item in scores if item["week"] == week]
        for week in score_weeks
    }

    add_summary("dataset", "source_file", source.name)
    add_summary("dataset", "source_bytes", source.stat().st_size)
    add_summary("dataset", "source_sha256", sha256(source))
    add_summary("dataset", "row_count", len(parsed))
    add_summary("dataset", "column_count", len(parsed.columns))
    add_summary("dataset", "encoding", settings["encoding"])
    add_summary("dataset", "delimiter", settings["delimiter"], details=settings["delimiter_note"])
    add_summary(
        "dataset",
        "layout",
        "wide contestant-season",
        details="Week and judge identifiers are encoded in score column names.",
    )

    for column in parsed.columns:
        raw_stripped = raw[column].str.strip()
        raw_folded = raw_stripped.str.casefold()
        zero_count = int(
            pd.to_numeric(raw_stripped, errors="coerce").eq(0).sum()
        )
        empty_count = int(raw_stripped.eq("").sum())
        special_count = int(raw_folded.isin(SPECIAL_TOKENS).sum())
        missing_count = int(parsed[column].isna().sum())
        metrics = {
            "dtype": str(parsed[column].dtype),
            "missing_count": missing_count,
            "missing_rate": missing_count / len(parsed) if len(parsed) else 0.0,
            "zero_count": zero_count,
            "raw_empty_string_count": empty_count,
            "raw_special_string_count": special_count,
            "distinct_count_including_missing": int(parsed[column].nunique(dropna=False)),
        }
        for metric, value in metrics.items():
            add_summary("column_profile", metric, value, column=column)

    for field in ("season", "week", "contestant", "placement", "results"):
        actual = fields[field]
        if field == "week" and actual is None and score_weeks:
            add_summary(
                "core_fields",
                "presence",
                "encoded_in_score_columns",
                column="weekN_judgeM_score",
                details=(
                    f"Logical field: week; detected weeks "
                    f"{min(score_weeks)}-{max(score_weeks)}."
                ),
            )
        else:
            add_summary(
                "core_fields",
                "presence",
                bool(actual),
                column=actual or "",
                details=f"Logical field: {field}",
            )

    add_summary("judge_scores", "score_column_count", len(score_columns))
    add_summary("judge_scores", "distinct_judge_positions", len(judge_ids))
    add_summary("judge_scores", "judge_ids", ",".join(map(str, judge_ids)))
    add_summary("judge_scores", "encoded_week_count", len(score_weeks))

    numeric_scores = (
        parsed[score_columns].apply(pd.to_numeric, errors="coerce")
        if score_columns
        else pd.DataFrame(index=parsed.index)
    )
    if score_columns:
        max_score = numeric_scores.max().max()
        above_ten_mask = numeric_scores.gt(10)
        add_summary("judge_scores", "maximum_score", max_score)
        add_summary("judge_scores", "score_above_10_count", int(above_ten_mask.sum().sum()))

        for row_position, column_position in zip(*above_ten_mask.to_numpy().nonzero()):
            row_index = numeric_scores.index[row_position]
            column = score_columns[column_position]
            metadata = SCORE_COLUMN_RE.fullmatch(column)
            source_row = parsed.loc[row_index]
            add_special(
                "score_above_10",
                season=source_row.get(fields["season"], "") if fields["season"] else "",
                week=int(metadata.group("week")) if metadata else "",
                contestant_name=(
                    source_row.get(fields["contestant"], "") if fields["contestant"] else ""
                ),
                column=column,
                raw_value=raw.iloc[row_index][column],
                details="Preserved exactly; no clipping applied.",
            )

    season_week_records: list[dict[str, Any]] = []
    if fields["season"] and score_columns:
        season_col = fields["season"]
        result_col = fields["results"]
        contestant_col = fields["contestant"]
        season_values = sorted(parsed[season_col].dropna().unique().tolist())

        for season in season_values:
            season_mask = parsed[season_col].eq(season)
            season_frame = parsed.loc[season_mask]
            valid_weeks = [
                week
                for week in score_weeks
                if numeric_scores.loc[season_mask, score_lookup[week]].notna().any().any()
            ]
            if not valid_weeks:
                add_summary("season_profile", "weeks_in_season", 0, season=season)
                continue

            finale_week = max(valid_weeks)
            add_summary("season_profile", "weeks_in_season", len(valid_weeks), season=season)
            add_summary("season_profile", "first_week", min(valid_weeks), season=season)
            add_summary("season_profile", "finale_week", finale_week, season=season)

            eliminated_by_week: dict[int, list[int]] = {week: [] for week in valid_weeks}
            withdrawn_by_week: dict[int, list[int]] = {week: [] for week in valid_weeks}

            if result_col:
                for row_index in season_frame.index:
                    result = str(raw.at[row_index, result_col]).strip()
                    elimination = ELIMINATION_WEEK_RE.search(result)
                    if elimination:
                        event_week = int(elimination.group("week"))
                        eliminated_by_week.setdefault(event_week, []).append(row_index)
                        add_special(
                            "elimination",
                            season=season,
                            week=event_week,
                            contestant_name=(
                                parsed.at[row_index, contestant_col] if contestant_col else ""
                            ),
                            column=result_col,
                            raw_value=result,
                            details="Parsed from the results field.",
                        )
                    if WITHDRAWAL_RE.search(result):
                        explicit = EXPLICIT_WEEK_RE.search(result)
                        if explicit:
                            event_week = int(explicit.group("week"))
                            inference = "parsed from the results field"
                        else:
                            positive_weeks = [
                                week
                                for week in valid_weeks
                                if numeric_scores.loc[row_index, score_lookup[week]].gt(0).any()
                            ]
                            event_week = max(positive_weeks) if positive_weeks else min(valid_weeks)
                            inference = "inferred as the last week with a positive judge score"
                        withdrawn_by_week.setdefault(event_week, []).append(row_index)
                        add_special(
                            "withdrawal",
                            season=season,
                            week=event_week,
                            contestant_name=(
                                parsed.at[row_index, contestant_col] if contestant_col else ""
                            ),
                            column=result_col,
                            raw_value=result,
                            details=inference,
                        )

            for week in valid_weeks:
                week_scores = numeric_scores.loc[season_mask, score_lookup[week]]
                active_mask = week_scores.gt(0).any(axis=1)
                active_count = int(active_mask.sum())
                eliminated_count = len(eliminated_by_week.get(week, []))
                withdrew_count = len(withdrawn_by_week.get(week, []))
                no_elimination = week != finale_week and eliminated_count == 0
                double_elimination = eliminated_count > 1
                finale = week == finale_week
                record = {
                    "season": season,
                    "week": week,
                    "active_contestants": active_count,
                    "eliminated_count": eliminated_count,
                    "withdrew_count": withdrew_count,
                    "no_elimination_week": no_elimination,
                    "double_elimination_week": double_elimination,
                    "finale_week": finale,
                }
                season_week_records.append(record)
                for metric, value in record.items():
                    if metric not in {"season", "week"}:
                        add_summary(
                            "season_week",
                            metric,
                            value,
                            season=season,
                            week=week,
                        )

                if no_elimination:
                    add_special(
                        "no_elimination_week",
                        season=season,
                        week=week,
                        details=(
                            "Inferred: no contestant result states elimination in this "
                            "non-finale week."
                        ),
                    )
                if double_elimination:
                    names = [
                        str(parsed.at[index, contestant_col])
                        for index in eliminated_by_week[week]
                    ] if contestant_col else []
                    add_special(
                        "double_elimination_week",
                        season=season,
                        week=week,
                        raw_value="; ".join(names),
                        details=f"{eliminated_count} eliminations parsed from results.",
                    )
                if finale:
                    add_special(
                        "finale_week",
                        season=season,
                        week=week,
                        details="Inferred as the final week with any recorded judge score.",
                    )

    partner_flags: list[dict[str, Any]] = []
    spelling_candidate_count = 0
    partner_col = fields["partner"]
    if partner_col:
        season_col = fields["season"]
        contestant_col = fields["contestant"]
        for row_index, value in raw[partner_col].items():
            partner = value.strip()
            flags: list[str] = []
            if "(" in partner or ")" in partner:
                flags.append("parenthetical_information")
            if "/" in partner:
                flags.append("slash_information")
            if PARTNER_REPLACEMENT_RE.search(partner):
                flags.append("possible_replacement_or_substitution")
            for flag in flags:
                entry = {
                    "flag": flag,
                    "partner": partner,
                    "season": parsed.at[row_index, season_col] if season_col else "",
                    "contestant": (
                        parsed.at[row_index, contestant_col] if contestant_col else ""
                    ),
                }
                partner_flags.append(entry)
                add_special(
                    f"partner_{flag}",
                    season=entry["season"],
                    contestant_name=entry["contestant"],
                    column=partner_col,
                    raw_value=partner,
                    details="Flagged for later entity normalization; raw text retained.",
                )

        unique_bases = sorted(
            {
                re.sub(r"\s*\([^)]*\)\s*", " ", value).strip()
                for value in raw[partner_col]
                if value.strip()
            }
        )
        for left_index, left in enumerate(unique_bases):
            left_key = normalize_person_name(left)
            for right in unique_bases[left_index + 1 :]:
                right_key = normalize_person_name(right)
                if not left_key or not right_key or left_key == right_key:
                    continue
                if left_key[0] != right_key[0]:
                    continue
                ratio = SequenceMatcher(None, left_key, right_key).ratio()
                if ratio >= 0.84:
                    spelling_candidate_count += 1
                    add_special(
                        "partner_possible_spelling_variant",
                        column=partner_col,
                        raw_value=f"{left} | {right}",
                        details=f"String-similarity candidate only (ratio={ratio:.3f}); not merged.",
                    )
        add_summary(
            "partner_fields",
            "unique_raw_partner_strings",
            int(raw[partner_col].nunique(dropna=False)),
            column=partner_col,
        )
        add_summary(
            "partner_fields",
            "row_level_structure_flags",
            len(partner_flags),
            column=partner_col,
            details="Parenthetical, slash, and replacement/substitution flags.",
        )
        add_summary(
            "partner_fields",
            "possible_spelling_variant_pairs",
            spelling_candidate_count,
            column=partner_col,
            details="Similarity candidates only; no automatic merge.",
        )

    repeated_contestants: list[dict[str, Any]] = []
    contestant_col = fields["contestant"]
    if contestant_col:
        season_col = fields["season"]
        counts = parsed.groupby(contestant_col, dropna=False).size().sort_values(ascending=False)
        for contestant, count in counts[counts > 1].items():
            appearances = parsed.loc[parsed[contestant_col].eq(contestant)]
            seasons = (
                sorted(appearances[season_col].dropna().tolist()) if season_col else []
            )
            repeated_contestants.append(
                {"contestant": contestant, "appearances": int(count), "seasons": seasons}
            )
            add_special(
                "repeated_contestant",
                contestant_name=contestant,
                raw_value=", ".join(map(str, seasons)),
                details=f"{int(count)} contestant-season rows with exact same name.",
            )
        add_summary(
            "contestants",
            "unique_contestant_names",
            int(parsed[contestant_col].nunique(dropna=True)),
        )
        add_summary(
            "contestants",
            "repeated_contestant_names",
            len(repeated_contestants),
        )

    summary = pd.DataFrame(summary_rows)
    special = pd.DataFrame(
        special_rows,
        columns=[
            "case_type",
            "season",
            "week",
            "contestant_name",
            "column",
            "raw_value",
            "details",
        ],
    )
    if not special.empty:
        special = (
            special.assign(
                _season_sort=pd.to_numeric(special["season"], errors="coerce").fillna(
                    float("inf")
                ),
                _week_sort=pd.to_numeric(special["week"], errors="coerce").fillna(
                    float("inf")
                ),
            )
            .sort_values(
                ["case_type", "_season_sort", "_week_sort", "contestant_name"],
                kind="stable",
                na_position="last",
            )
            .drop(columns=["_season_sort", "_week_sort"])
            .reset_index(drop=True)
        )

    column_rows = []
    for column in parsed.columns:
        raw_stripped = raw[column].str.strip()
        column_rows.append(
            (
                column,
                str(parsed[column].dtype),
                int(parsed[column].isna().sum()),
                f"{parsed[column].isna().mean():.2%}",
                int(pd.to_numeric(raw_stripped, errors="coerce").eq(0).sum()),
                int(raw_stripped.eq("").sum()),
                int(raw_stripped.str.casefold().isin(SPECIAL_TOKENS).sum()),
            )
        )

    core_rows = []
    for field in ("season", "week", "contestant", "placement", "results"):
        actual = fields[field]
        if field == "week" and actual is None and score_weeks:
            core_rows.append((field, "encoded", "weekN_judgeM_score columns"))
        else:
            core_rows.append((field, "yes" if actual else "no", actual or ""))

    event_counts = special["case_type"].value_counts() if not special.empty else pd.Series(dtype=int)
    above_ten_examples = special.loc[special["case_type"].eq("score_above_10")].head(20)
    season_week_frame = pd.DataFrame(season_week_records)

    lines = [
        "# Data Audit Report",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Source and integrity",
        "",
        f"- File: `{source}`",
        f"- SHA-256: `{sha256(source)}`",
        f"- Size: {source.stat().st_size:,} bytes",
        f"- Parsed dimensions: {len(parsed):,} rows x {len(parsed.columns):,} columns",
        f"- Encoding: `{settings['encoding']}`",
        f"- Delimiter: `{settings['delimiter']}` ({settings['delimiter_note']})",
        "- Source mutation: none; the audit is read-only.",
        "",
        "## Observed structure",
        "",
        (
            "The source is a wide contestant-season table. There is no standalone "
            "week column; week and judge identifiers are encoded in score-column names."
        ),
        "",
        markdown_table(["Logical field", "Present", "Observed column"], core_rows),
        "",
        f"Detected {len(score_columns)} judge-score columns across "
        f"{len(score_weeks)} encoded weeks and {len(judge_ids)} judge positions.",
        "",
        "## Missingness and raw-token semantics",
        "",
        (
            "Parsed NaN counts and raw tokens are reported separately. A raw `N/A` "
            "is an explicit token, whereas an empty CSV field is counted as an empty "
            "string. Numeric zero is retained as a value. These states are not pooled."
        ),
        "",
        markdown_table(
            [
                "Column",
                "dtype",
                "NaN",
                "missing rate",
                "zero",
                "raw empty",
                "raw special token",
            ],
            column_rows,
        ),
        "",
        "## Season and week diagnostics",
        "",
    ]

    if not season_week_frame.empty:
        season_overview = []
        for season, frame in season_week_frame.groupby("season", sort=True):
            double_weeks = frame.loc[frame["double_elimination_week"], "week"].tolist()
            no_elim_weeks = frame.loc[frame["no_elimination_week"], "week"].tolist()
            season_overview.append(
                (
                    season,
                    frame["week"].nunique(),
                    int(frame["active_contestants"].max()),
                    int(frame["active_contestants"].min()),
                    ", ".join(map(str, no_elim_weeks)),
                    ", ".join(map(str, double_weeks)),
                    int(frame.loc[frame["finale_week"], "week"].max()),
                )
            )
        lines.extend(
            [
                markdown_table(
                    [
                        "Season",
                        "weeks",
                        "max active",
                        "min active",
                        "inferred no-elim weeks",
                        "double-elim weeks",
                        "finale week",
                    ],
                    season_overview,
                ),
                "",
                (
                    "Active means at least one positive judge score in that contestant-week. "
                    "Elimination counts are parsed from the `results` field. Detailed "
                    "season-week counts are in `data_audit_summary.csv`."
                ),
                "",
            ]
        )
    else:
        lines.extend(["Season-week diagnostics could not be constructed.", ""])

    lines.extend(["## Special cases", ""])
    if not event_counts.empty:
        lines.extend(
            [
                markdown_table(
                    ["Case type", "Rows"],
                    ((case_type, count) for case_type, count in event_counts.items()),
                ),
                "",
            ]
        )
    else:
        lines.extend(["No special cases were detected.", ""])

    if not above_ten_examples.empty:
        lines.extend(
            [
                "### Scores above 10 (first 20 cells)",
                "",
                markdown_table(
                    ["Season", "Week", "Contestant", "Column", "Value"],
                    above_ten_examples[
                        ["season", "week", "contestant_name", "column", "raw_value"]
                    ].itertuples(index=False, name=None),
                ),
                "",
                "These scores are preserved exactly and are not clipped to 10.",
                "",
            ]
        )

    spelling_candidates = special.loc[
        special["case_type"].eq("partner_possible_spelling_variant")
    ]
    lines.extend(["### Partner-field audit", ""])
    lines.append(
        f"Detected {len(partner_flags)} row-level parenthetical, slash, or replacement "
        "flags. Raw partner strings remain unchanged."
    )
    lines.append("")
    lines.append(
        f"Detected {len(spelling_candidates)} possible spelling/name-variant pair(s) "
        "using a conservative similarity screen."
    )
    lines.append("")
    if not spelling_candidates.empty:
        lines.extend(
            [
                "Possible spelling variants are similarity candidates only; the audit "
                "does not merge them:",
                "",
                markdown_table(
                    ["Candidate pair", "Details"],
                    spelling_candidates[["raw_value", "details"]].itertuples(
                        index=False, name=None
                    ),
                ),
                "",
            ]
        )

    lines.extend(["### Repeated contestants", ""])
    if repeated_contestants:
        lines.extend(
            [
                markdown_table(
                    ["Contestant", "Appearances", "Seasons"],
                    (
                        (
                            item["contestant"],
                            item["appearances"],
                            ", ".join(map(str, item["seasons"])),
                        )
                        for item in repeated_contestants
                    ),
                ),
                "",
            ]
        )
    else:
        lines.extend(["No exact-name repeated contestants were detected.", ""])

    lines.extend(
        [
            "## Audit assumptions and limitations",
            "",
            "1. A season week exists when at least one score cell in that season-week is non-missing.",
            "2. A contestant is active in a week when at least one judge score is positive. All-zero rows are retained but excluded from the active count.",
            "3. An elimination week is parsed only from explicit `Eliminated Week N`-style result text.",
            "4. A non-finale week with no explicit eliminated contestant is flagged as a possible no-elimination week. This is an inference, not an explicit rule field.",
            "5. More than one parsed elimination in the same season-week is treated as a joint/double-elimination event.",
            "6. The finale is inferred as the final week containing any recorded judge score for the season.",
            "7. When a withdrawal has no explicit week, its week is inferred as the contestant's last week with a positive judge score. Withdrawals are not counted as eliminations.",
            "8. Parentheses, slashes, and replacement keywords in partner strings are only flagged. No partner entity is normalized at the audit stage.",
            "9. Similar partner names are reported as fuzzy candidates and are never merged automatically.",
            "10. The source has no observed fan-vote column; this audit makes no fan-vote estimate or truth claim.",
            "",
            "## Generated artifacts",
            "",
            "- `outputs/tables/data_audit_summary.csv`",
            "- `outputs/tables/special_cases.csv`",
            "- `outputs/logs/data_audit.md`",
            "",
        ]
    )
    return summary, special, "\n".join(lines)


def normalize_person_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_text = decomposed.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_text.casefold())


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    tables_dir = resolve_from_root(args.tables_dir, project_root)
    logs_dir = resolve_from_root(args.logs_dir, project_root)

    try:
        source = discover_input(project_root, args.input)
        parsed, raw, settings = load_csv(source)
        summary, special, report = audit(parsed, raw, source, settings)
    except (FileNotFoundError, RuntimeError, UnicodeError, ValueError, pd.errors.ParserError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    tables_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    summary_path = tables_dir / "data_audit_summary.csv"
    special_path = tables_dir / "special_cases.csv"
    report_path = logs_dir / "data_audit.md"

    summary.to_csv(summary_path, index=False, encoding="utf-8")
    special.to_csv(special_path, index=False, encoding="utf-8")
    report_path.write_text(report, encoding="utf-8", newline="\n")

    print(f"Audited: {source}")
    print(f"Rows x columns: {len(parsed)} x {len(parsed.columns)}")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {special_path}")
    print(f"Wrote: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
