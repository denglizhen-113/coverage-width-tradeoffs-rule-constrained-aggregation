"""Auditable preprocessing for the wide DWTS-style source table.

The module keeps source score values intact while separating their analytical
meaning. Inactive all-zero score rows remain visible in the long panel, but
their derived totals and percentages are missing so they cannot enter weekly
normalization denominators.
"""

from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


SCORE_COLUMN_RE = re.compile(
    r"^week(?P<week>\d+)_judge(?P<judge>\d+)_score$", re.IGNORECASE
)
ELIMINATION_WEEK_RE = re.compile(
    r"\beliminat(?:ed|ion)\s*(?:in\s*)?week\s*(?P<week>\d+)\b",
    re.IGNORECASE,
)
PARENTHETICAL_RE = re.compile(r"^(?P<outside>.*?)\s*\((?P<inside>[^)]*)\)\s*$")
WEEK_RE = re.compile(r"\bweek\s*(?P<week>\d+)\b", re.IGNORECASE)

REQUIRED_COLUMNS = (
    "celebrity_name",
    "ballroom_partner",
    "celebrity_industry",
    "celebrity_homestate",
    "celebrity_homecountry/region",
    "celebrity_age_during_season",
    "season",
    "results",
    "placement",
)

SPECIAL_MISSING_TOKENS = {
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


def sha256(path: Path) -> str:
    """Return an uppercase SHA-256 digest for provenance checks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def detect_csv_settings(path: Path) -> tuple[str, str, str]:
    """Detect a conservative text encoding and delimiter."""
    payload = path.read_bytes()
    decoded = ""
    encoding = ""
    for candidate in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            decoded = payload.decode(candidate)
            encoding = candidate
            break
        except UnicodeDecodeError:
            continue
    if not encoding:
        raise UnicodeError(f"Unable to decode source file: {path}")
    try:
        delimiter = csv.Sniffer().sniff(decoded[:65536], delimiters=",;\t|").delimiter
        delimiter_note = "detected by csv.Sniffer"
    except csv.Error:
        delimiter = ","
        delimiter_note = "comma fallback after delimiter detection failed"
    return encoding, delimiter, delimiter_note


def load_source_csv(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]:
    """Read parsed values and lossless raw strings using the same schema."""
    encoding, delimiter, delimiter_note = detect_csv_settings(path)
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
        raise ValueError("Parsed and raw-string source reads disagree on schema.")
    return parsed, raw, {
        "encoding": encoding,
        "delimiter": repr(delimiter),
        "delimiter_note": delimiter_note,
    }


def normalize_person_name(value: str) -> str:
    """Normalize a person name for stable identifiers, not display."""
    decomposed = unicodedata.normalize("NFKD", str(value))
    ascii_text = decomposed.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_text.casefold())


def stable_contestant_id(name: str) -> str:
    """Create a deterministic person identifier from the normalized source name."""
    normalized = normalize_person_name(name)
    if not normalized:
        raise ValueError("Cannot construct contestant_id from an empty name.")
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    return f"c_{digest}"


def aggregation_regime(season: int) -> str:
    """Apply the documented fallback rule because no regime field is supplied."""
    if 1 <= season <= 2:
        return "R"
    if 3 <= season <= 27:
        return "P"
    if 28 <= season <= 34:
        return "R_plus"
    raise ValueError(f"No documented aggregation regime for season {season}.")


def parse_elimination_week(result: str) -> int | None:
    match = ELIMINATION_WEEK_RE.search(str(result))
    return int(match.group("week")) if match else None


def score_value_state(raw_value: str, numeric_value: Any, active: bool) -> str:
    """Classify score-cell provenance without collapsing zero and missingness."""
    stripped = str(raw_value).strip()
    if stripped == "":
        return "empty_string"
    if stripped.casefold() in SPECIAL_MISSING_TOKENS:
        return "explicit_missing_token"
    if pd.isna(numeric_value):
        return "other_non_numeric"
    if float(numeric_value) == 0.0:
        return "observed_zero_active" if active else "structural_zero_inactive"
    return "observed_score"


def _base_partner_names(raw_partner: str) -> list[str]:
    match = PARENTHETICAL_RE.match(str(raw_partner).strip())
    outside = match.group("outside") if match else str(raw_partner).strip()
    return [part.strip() for part in outside.split("/") if part.strip()]


def build_partner_alias_map(
    raw_partners: Iterable[str], special_cases: pd.DataFrame
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """Resolve only variant pairs explicitly surfaced by the audit.

    The more frequent observed form becomes canonical. Ties use a deterministic
    lexical rule. No unaudited fuzzy merge is introduced here.
    """
    counts: Counter[str] = Counter()
    for raw_partner in raw_partners:
        counts.update(_base_partner_names(raw_partner))

    aliases: dict[str, str] = {}
    decisions: list[dict[str, Any]] = []
    variants = special_cases.loc[
        special_cases["case_type"].eq("partner_possible_spelling_variant")
    ]
    for raw_pair in variants["raw_value"]:
        pair = [part.strip() for part in str(raw_pair).split("|") if part.strip()]
        if len(pair) != 2:
            raise ValueError(f"Unparseable audited partner variant pair: {raw_pair}")
        left, right = pair
        canonical = sorted(pair, key=lambda name: (counts[name], name), reverse=True)[0]
        alias = right if canonical == left else left
        aliases[alias] = canonical
        decisions.append(
            {
                "alias": alias,
                "canonical": canonical,
                "alias_count": counts[alias],
                "canonical_count": counts[canonical],
                "source": "data_audit_similarity_candidate",
            }
        )
    return aliases, decisions


def canonicalize_partner(name: str, alias_map: dict[str, str]) -> str:
    cleaned = re.sub(r"\s+", " ", str(name)).strip()
    return alias_map.get(cleaned, cleaned)


def parse_partner_assignment(
    raw_partner: str, week: int, alias_map: dict[str, str]
) -> dict[str, str]:
    """Return the week-specific partner while retaining the supplied raw text."""
    text = str(raw_partner).strip()
    match = PARENTHETICAL_RE.match(text)
    outside = match.group("outside").strip() if match else text
    inside = match.group("inside").strip() if match else ""
    outside_parts = [part.strip() for part in outside.split("/") if part.strip()]
    primary = outside_parts[0] if outside_parts else outside

    event_week: int | None = None
    replacement = ""
    week_match = WEEK_RE.search(inside)
    if week_match:
        event_week = int(week_match.group("week"))
        inside_name = WEEK_RE.sub("", inside).strip(" ,-;/")
        if inside_name:
            replacement = inside_name
        elif len(outside_parts) > 1:
            replacement = outside_parts[-1]

    use_replacement = bool(replacement and event_week == int(week))
    selected = replacement if use_replacement else primary
    role = "replacement" if use_replacement else "primary"
    if event_week and replacement:
        note = (
            f"week {event_week}: {canonicalize_partner(replacement, alias_map)} "
            f"replaces {canonicalize_partner(primary, alias_map)}"
        )
    elif text != primary:
        note = "complex raw partner text retained; primary name selected"
    else:
        note = "direct"
    return {
        "partner_clean": canonicalize_partner(selected, alias_map),
        "partner_clean_primary": canonicalize_partner(primary, alias_map),
        "partner_assignment_role": role,
        "partner_normalization_note": note,
    }


def _parse_bool(value: Any) -> bool:
    return str(value).strip().casefold() in {"true", "1", "yes"}


def audit_week_table(audit_summary: pd.DataFrame) -> pd.DataFrame:
    rows = audit_summary.loc[audit_summary["section"].eq("season_week")]
    if rows.empty:
        raise ValueError("Audit summary has no season_week records.")
    table = (
        rows.pivot(index=["season", "week"], columns="metric", values="value")
        .reset_index()
        .rename_axis(columns=None)
    )
    table["season"] = pd.to_numeric(table["season"], errors="raise").astype(int)
    table["week"] = pd.to_numeric(table["week"], errors="raise").astype(int)
    for column in ("active_contestants", "eliminated_count", "withdrew_count"):
        table[column] = pd.to_numeric(table[column], errors="raise").astype(int)
    for column in (
        "no_elimination_week",
        "double_elimination_week",
        "finale_week",
    ):
        table[column] = table[column].map(_parse_bool)
    return table.sort_values(["season", "week"]).reset_index(drop=True)


def validate_audit_provenance(source: Path, audit_summary: pd.DataFrame) -> str:
    matches = audit_summary.loc[
        audit_summary["section"].eq("dataset")
        & audit_summary["metric"].eq("source_sha256"),
        "value",
    ]
    if len(matches) != 1:
        raise ValueError("Audit summary must contain exactly one source_sha256 value.")
    audited_hash = str(matches.iloc[0]).upper()
    actual_hash = sha256(source)
    if audited_hash != actual_hash:
        raise ValueError(
            "Audit outputs are stale: source SHA-256 does not match. "
            "Rerun scripts/01_data_audit.py before preprocessing."
        )
    return actual_hash


def _score_metadata(columns: Iterable[str]) -> list[dict[str, Any]]:
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


def _names(values: pd.Series) -> str:
    return "; ".join(str(value) for value in values if str(value).strip())


def _optional_int(values: pd.Series) -> int | pd.NA:
    selected = values.dropna()
    return int(selected.iloc[0]) if not selected.empty else pd.NA


def build_preprocessed_tables(
    source: Path,
    parsed: pd.DataFrame,
    raw: pd.DataFrame,
    audit_summary: pd.DataFrame,
    special_cases: pd.DataFrame,
    csv_settings: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    """Construct long, week-level, and contestant-season analysis tables."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in parsed]
    if missing_columns:
        raise ValueError(f"Required observed columns are missing: {missing_columns}")
    if parsed.shape != raw.shape:
        raise ValueError("Parsed and raw source frames have different dimensions.")

    source_hash = validate_audit_provenance(source, audit_summary)
    scores = _score_metadata(parsed.columns)
    if not scores:
        raise ValueError("No weekN_judgeM_score columns were found.")
    judge_ids = sorted({item["judge"] for item in scores})
    if judge_ids != [1, 2, 3, 4]:
        raise ValueError(f"Expected audited judge positions 1-4, found {judge_ids}.")
    score_lookup = {
        week: {item["judge"]: item["column"] for item in scores if item["week"] == week}
        for week in sorted({item["week"] for item in scores})
    }

    audited_weeks = audit_week_table(audit_summary)
    week_flags = {
        (int(row.season), int(row.week)): row
        for row in audited_weeks.itertuples(index=False)
    }
    weeks_by_season = {
        int(season): sorted(group["week"].astype(int).tolist())
        for season, group in audited_weeks.groupby("season", sort=True)
    }
    source_seasons = sorted(parsed["season"].astype(int).unique().tolist())
    if source_seasons != sorted(weeks_by_season):
        raise ValueError("Audit season-week coverage does not match source seasons.")

    alias_map, alias_decisions = build_partner_alias_map(
        raw["ballroom_partner"], special_cases
    )
    withdrawal_rows = special_cases.loc[special_cases["case_type"].eq("withdrawal")]
    withdrawal_keys = {
        (int(row.season), int(row.week), str(row.contestant_name))
        for row in withdrawal_rows.itertuples(index=False)
    }

    normalized_names = parsed["celebrity_name"].map(normalize_person_name)
    if normalized_names.eq("").any():
        raise ValueError("At least one contestant name normalizes to an empty identifier.")
    name_id_pairs = pd.DataFrame(
        {"normalized": normalized_names, "name": parsed["celebrity_name"]}
    ).drop_duplicates()
    collisions = name_id_pairs.groupby("normalized")["name"].nunique()
    if collisions.gt(1).any():
        problem = collisions[collisions.gt(1)].index.tolist()
        raise ValueError(f"Contestant identifier normalization collision: {problem}")
    first_season = (
        pd.DataFrame({"normalized": normalized_names, "season": parsed["season"]})
        .groupby("normalized")["season"]
        .min()
        .to_dict()
    )

    records: list[dict[str, Any]] = []
    for row_index, row in parsed.iterrows():
        season = int(row["season"])
        contestant_name = str(row["celebrity_name"])
        normalized_name = normalized_names.at[row_index]
        contestant_id = stable_contestant_id(contestant_name)
        elimination_week = parse_elimination_week(str(row["results"]))

        for week in weeks_by_season[season]:
            columns = score_lookup.get(week, {})
            numeric_values = {
                judge: row[columns[judge]] if judge in columns else pd.NA
                for judge in judge_ids
            }
            raw_values = {
                judge: raw.at[row_index, columns[judge]] if judge in columns else ""
                for judge in judge_ids
            }
            active = any(
                not pd.isna(value) and float(value) > 0 for value in numeric_values.values()
            )
            nonmissing_values = [
                float(value) for value in numeric_values.values() if not pd.isna(value)
            ]
            if active:
                judge_count = len(nonmissing_values)
                judge_total = sum(nonmissing_values)
                judge_mean = judge_total / judge_count
                score_record_status = "observed_active"
            else:
                judge_count = 0
                judge_total = pd.NA
                judge_mean = pd.NA
                score_record_status = (
                    "structural_zero_inactive"
                    if any(value == 0 for value in nonmissing_values)
                    else "all_missing_inactive"
                )

            partner = parse_partner_assignment(
                str(raw.at[row_index, "ballroom_partner"]), week, alias_map
            )
            flags = week_flags[(season, week)]
            record: dict[str, Any] = {
                "season": season,
                "week": week,
                "contestant_id": contestant_id,
                "contestant_season_id": f"s{season:02d}_{contestant_id}",
                "contestant_name": contestant_name,
                "partner_raw": str(raw.at[row_index, "ballroom_partner"]),
                **partner,
                "age": int(row["celebrity_age_during_season"]),
                "gender": pd.NA,
                "industry_profession": str(row["celebrity_industry"]),
                "home_state": (
                    str(raw.at[row_index, "celebrity_homestate"]).strip() or pd.NA
                ),
                "country_nationality": str(row["celebrity_homecountry/region"]),
                "returning_contestant": season > int(first_season[normalized_name]),
                "judge_count": judge_count,
                "judge_total": judge_total,
                "judge_mean": judge_mean,
                "score_record_status": score_record_status,
                "score_above_10_count": sum(
                    not pd.isna(value) and float(value) > 10
                    for value in numeric_values.values()
                ),
                "active_status": active,
                "eliminated_this_week": elimination_week == week,
                "withdrew_this_week": (season, week, contestant_name)
                in withdrawal_keys,
                "no_elimination_week": bool(flags.no_elimination_week),
                "double_elimination_week": bool(flags.double_elimination_week),
                "finale_week": bool(flags.finale_week),
                "placement": int(row["placement"]),
                "result": str(row["results"]),
                "aggregation_regime": aggregation_regime(season),
                "aggregation_regime_source": "fallback_season_range",
            }
            for judge in judge_ids:
                record[f"judge{judge}_score"] = numeric_values[judge]
                record[f"judge{judge}_state"] = score_value_state(
                    raw_values[judge], numeric_values[judge], active
                )
            records.append(record)

    panel = pd.DataFrame(records)
    denominators = panel.groupby(["season", "week"])["judge_total"].transform("sum")
    panel["judge_pct"] = panel["judge_total"].astype("Float64") / denominators.astype(
        "Float64"
    )

    panel_columns = [
        "season",
        "week",
        "contestant_id",
        "contestant_season_id",
        "contestant_name",
        "partner_raw",
        "partner_clean",
        "partner_clean_primary",
        "partner_assignment_role",
        "partner_normalization_note",
        "age",
        "gender",
        "industry_profession",
        "home_state",
        "country_nationality",
        "returning_contestant",
        "judge1_score",
        "judge2_score",
        "judge3_score",
        "judge4_score",
        "judge1_state",
        "judge2_state",
        "judge3_state",
        "judge4_state",
        "judge_count",
        "judge_total",
        "judge_mean",
        "judge_pct",
        "score_record_status",
        "score_above_10_count",
        "active_status",
        "eliminated_this_week",
        "withdrew_this_week",
        "no_elimination_week",
        "double_elimination_week",
        "finale_week",
        "placement",
        "result",
        "aggregation_regime",
        "aggregation_regime_source",
    ]
    panel = panel[panel_columns].sort_values(
        ["season", "week", "contestant_name"], kind="stable"
    ).reset_index(drop=True)

    week_records: list[dict[str, Any]] = []
    for (season, week), group in panel.groupby(["season", "week"], sort=True):
        active = group.loc[group["active_status"]]
        eliminated = group.loc[group["eliminated_this_week"]]
        withdrawn = group.loc[group["withdrew_this_week"]]
        finale = bool(group["finale_week"].iloc[0])
        if finale:
            event_type = "finale_ranking"
        elif len(eliminated) > 1:
            event_type = "joint_elimination"
        elif len(eliminated) == 1:
            event_type = "single_elimination"
        elif len(withdrawn) > 0:
            event_type = "withdrawal_without_elimination"
        else:
            event_type = "no_elimination"
        final_order = ""
        if finale:
            ordered = group.sort_values(["placement", "contestant_name"])
            final_order = "; ".join(
                f"{int(row.placement)}:{row.contestant_name}"
                for row in ordered.itertuples(index=False)
            )
        week_records.append(
            {
                "season": int(season),
                "week": int(week),
                "aggregation_regime": group["aggregation_regime"].iloc[0],
                "aggregation_regime_source": group[
                    "aggregation_regime_source"
                ].iloc[0],
                "contestants_in_season": len(group),
                "active_contestants": len(active),
                "inactive_structural_zero_rows": int(
                    group["score_record_status"].eq("structural_zero_inactive").sum()
                ),
                "eliminated_count": len(eliminated),
                "withdrawn_count": len(withdrawn),
                "no_elimination_week": bool(group["no_elimination_week"].iloc[0]),
                "double_elimination_week": bool(
                    group["double_elimination_week"].iloc[0]
                ),
                "finale_week": finale,
                "observed_event_type": event_type,
                "judge_count_min_active": int(active["judge_count"].min()),
                "judge_count_max_active": int(active["judge_count"].max()),
                "judge_total_sum_active": float(active["judge_total"].sum()),
                "judge_total_mean_active": float(active["judge_total"].mean()),
                "judge_total_min_active": float(active["judge_total"].min()),
                "judge_total_max_active": float(active["judge_total"].max()),
                "judge_pct_sum_active": float(active["judge_pct"].sum()),
                "score_above_10_cells": int(active["score_above_10_count"].sum()),
                "active_contestant_ids": _names(active["contestant_id"]),
                "active_contestant_names": _names(active["contestant_name"]),
                "eliminated_contestant_ids": _names(eliminated["contestant_id"]),
                "eliminated_contestant_names": _names(eliminated["contestant_name"]),
                "withdrawn_contestant_ids": _names(withdrawn["contestant_id"]),
                "withdrawn_contestant_names": _names(withdrawn["contestant_name"]),
                "final_placement_order": final_order,
            }
        )
    week_level = pd.DataFrame(week_records).sort_values(["season", "week"])

    contestant_records: list[dict[str, Any]] = []
    for (season, contestant_id), group in panel.groupby(
        ["season", "contestant_id"], sort=True
    ):
        group = group.sort_values("week")
        active = group.loc[group["active_status"]]
        partner_sequence = list(dict.fromkeys(group["partner_clean"].tolist()))
        replacement_weeks = group.loc[
            group["partner_assignment_role"].eq("replacement"), "week"
        ].tolist()
        contestant_records.append(
            {
                "season": int(season),
                "contestant_id": contestant_id,
                "contestant_season_id": group["contestant_season_id"].iloc[0],
                "contestant_name": group["contestant_name"].iloc[0],
                "partner_raw": group["partner_raw"].iloc[0],
                "partner_clean_primary": group["partner_clean_primary"].iloc[0],
                "partner_clean_sequence": "; ".join(partner_sequence),
                "partner_replacement_weeks": "; ".join(map(str, replacement_weeks)),
                "age": int(group["age"].iloc[0]),
                "gender": pd.NA,
                "industry_profession": group["industry_profession"].iloc[0],
                "home_state": group["home_state"].iloc[0],
                "country_nationality": group["country_nationality"].iloc[0],
                "returning_contestant": bool(group["returning_contestant"].iloc[0]),
                "placement": int(group["placement"].iloc[0]),
                "result": group["result"].iloc[0],
                "aggregation_regime": group["aggregation_regime"].iloc[0],
                "weeks_in_season": len(group),
                "active_weeks": len(active),
                "inactive_structural_zero_weeks": int(
                    group["score_record_status"].eq("structural_zero_inactive").sum()
                ),
                "first_active_week": _optional_int(active["week"]),
                "last_active_week": (
                    int(active["week"].iloc[-1]) if not active.empty else pd.NA
                ),
                "eliminated_week": _optional_int(
                    group.loc[group["eliminated_this_week"], "week"]
                ),
                "withdrew_week": _optional_int(
                    group.loc[group["withdrew_this_week"], "week"]
                ),
                "reached_finale": bool(
                    (group["active_status"] & group["finale_week"]).any()
                ),
                "judge_score_observations": int(active["judge_count"].sum()),
                "cumulative_judge_total": float(active["judge_total"].sum()),
                "mean_weekly_judge_total": float(active["judge_total"].mean()),
                "mean_judge_score": float(active["judge_mean"].mean()),
                "mean_judge_pct": float(active["judge_pct"].mean()),
                "max_judge_pct": float(active["judge_pct"].max()),
                "score_above_10_cells": int(active["score_above_10_count"].sum()),
            }
        )
    contestant_level = pd.DataFrame(contestant_records).sort_values(
        ["season", "placement", "contestant_name"], kind="stable"
    )

    report = build_preprocess_report(
        source=source,
        source_hash=source_hash,
        csv_settings=csv_settings,
        parsed=parsed,
        panel=panel,
        week_level=week_level,
        contestant_level=contestant_level,
        special_cases=special_cases,
        alias_decisions=alias_decisions,
    )
    validate_outputs(
        parsed,
        panel,
        week_level,
        contestant_level,
        audit_summary,
        special_cases,
    )
    return panel, week_level, contestant_level, report


def validate_outputs(
    parsed: pd.DataFrame,
    panel: pd.DataFrame,
    week_level: pd.DataFrame,
    contestant_level: pd.DataFrame,
    audit_summary: pd.DataFrame,
    special_cases: pd.DataFrame,
) -> None:
    """Raise on boundary violations before any processed file is written."""
    expected_rows = sum(
        int((parsed["season"] == season).sum()) * int(group["week"].nunique())
        for season, group in audit_week_table(audit_summary).groupby("season")
    )
    if len(panel) != expected_rows:
        raise ValueError(f"Panel row count mismatch: {len(panel)} != {expected_rows}")
    if panel.duplicated(["season", "week", "contestant_id"]).any():
        raise ValueError("panel_long contains duplicate season-week-contestant keys.")
    if week_level.duplicated(["season", "week"]).any():
        raise ValueError("week_level contains duplicate season-week keys.")
    if contestant_level.duplicated(["season", "contestant_id"]).any():
        raise ValueError("contestant_level contains duplicate season-contestant keys.")
    if len(contestant_level) != len(parsed):
        raise ValueError("contestant_level does not have one row per source record.")
    if panel.loc[~panel["active_status"], "judge_total"].notna().any():
        raise ValueError("Inactive structural-zero rows have non-missing judge_total.")
    if panel.loc[panel["active_status"], "judge_total"].isna().any():
        raise ValueError("Active rows have missing judge_total.")
    pct_sums = panel.groupby(["season", "week"])["judge_pct"].sum()
    if not ((pct_sums - 1.0).abs() < 1e-10).all():
        raise ValueError("Active judge_pct values do not sum to one in every week.")
    if (panel["eliminated_this_week"] & panel["withdrew_this_week"]).any():
        raise ValueError("A withdrawal was incorrectly marked as an elimination.")

    audit_counts = special_cases["case_type"].value_counts()
    output_counts = {
        "elimination": int(panel["eliminated_this_week"].sum()),
        "withdrawal": int(panel["withdrew_this_week"].sum()),
        "score_above_10": int(panel["score_above_10_count"].sum()),
        "no_elimination_week": int(week_level["no_elimination_week"].sum()),
        "double_elimination_week": int(week_level["double_elimination_week"].sum()),
        "finale_week": int(week_level["finale_week"].sum()),
    }
    for case_type, output_count in output_counts.items():
        audit_count = int(audit_counts.get(case_type, 0))
        if output_count != audit_count:
            raise ValueError(
                f"Audit reconciliation failed for {case_type}: "
                f"{output_count} != {audit_count}"
            )
    if not week_level.loc[
        week_level["double_elimination_week"], "eliminated_count"
    ].gt(1).all():
        raise ValueError("A double-elimination week has fewer than two eliminations.")
    if not week_level.loc[
        week_level["no_elimination_week"], "eliminated_count"
    ].eq(0).all():
        raise ValueError("A no-elimination week contains an elimination.")


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


def build_preprocess_report(
    *,
    source: Path,
    source_hash: str,
    csv_settings: dict[str, str],
    parsed: pd.DataFrame,
    panel: pd.DataFrame,
    week_level: pd.DataFrame,
    contestant_level: pd.DataFrame,
    special_cases: pd.DataFrame,
    alias_decisions: list[dict[str, Any]],
) -> str:
    state_columns = [f"judge{judge}_state" for judge in range(1, 5)]
    state_counts = pd.concat([panel[column] for column in state_columns]).value_counts()
    audit_counts = special_cases["case_type"].value_counts()
    regime_rows = []
    for regime, group in panel.groupby("aggregation_regime", sort=False):
        regime_rows.append(
            (
                regime,
                f"{group['season'].min()}-{group['season'].max()}",
                group["season"].nunique(),
                group[["season", "week"]].drop_duplicates().shape[0],
                len(group),
                int(group["active_status"].sum()),
            )
        )
    reconciliation_rows = [
        (
            "Eliminations",
            int(audit_counts.get("elimination", 0)),
            int(panel["eliminated_this_week"].sum()),
        ),
        (
            "Withdrawals",
            int(audit_counts.get("withdrawal", 0)),
            int(panel["withdrew_this_week"].sum()),
        ),
        (
            "Scores above 10",
            int(audit_counts.get("score_above_10", 0)),
            int(panel["score_above_10_count"].sum()),
        ),
        (
            "No-elimination weeks",
            int(audit_counts.get("no_elimination_week", 0)),
            int(week_level["no_elimination_week"].sum()),
        ),
        (
            "Multiple-elimination weeks",
            int(audit_counts.get("double_elimination_week", 0)),
            int(week_level["double_elimination_week"].sum()),
        ),
        (
            "Finale weeks",
            int(audit_counts.get("finale_week", 0)),
            int(week_level["finale_week"].sum()),
        ),
    ]

    replacement_rows = panel.loc[
        panel["partner_assignment_role"].eq("replacement"),
        [
            "season",
            "week",
            "contestant_name",
            "partner_raw",
            "partner_clean",
            "partner_clean_primary",
        ],
    ].drop_duplicates()
    alias_rows = [
        (
            decision["alias"],
            decision["canonical"],
            decision["alias_count"],
            decision["canonical_count"],
            decision["source"],
        )
        for decision in alias_decisions
    ]

    lines = [
        "# Preprocessing Report",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Provenance",
        "",
        f"- Source: `{source}`",
        f"- Source SHA-256: `{source_hash}`",
        f"- Encoding: `{csv_settings['encoding']}`",
        f"- Delimiter: `{csv_settings['delimiter']}` ({csv_settings['delimiter_note']})",
        "- Audit dependency: `outputs/tables/data_audit_summary.csv` and `special_cases.csv`.",
        "- The audit SHA-256 was checked against the source before transformation.",
        "- No stochastic operation is used in this stage.",
        "",
        "## Source-to-analysis field mapping",
        "",
        markdown_table(
            ["Analysis field", "Source field or rule"],
            [
                ("season", "season"),
                ("week", "parsed from weekN_judgeM_score column names"),
                ("contestant_name", "celebrity_name"),
                ("partner_raw", "ballroom_partner, unchanged"),
                ("partner_clean", "week-specific conservative entity normalization"),
                ("age", "celebrity_age_during_season"),
                ("gender", "not supplied; retained as missing"),
                ("industry_profession", "celebrity_industry"),
                ("home_state", "celebrity_homestate; empty remains missing"),
                ("country_nationality", "celebrity_homecountry/region"),
                ("placement", "placement"),
                ("result", "results"),
                ("aggregation_regime", "fallback season ranges; no source rule field"),
            ],
        ),
        "",
        "## Output dimensions",
        "",
        markdown_table(
            ["Artifact", "Rows", "Columns", "Key"],
            [
                (
                    "panel_long.csv",
                    len(panel),
                    len(panel.columns),
                    "season + week + contestant_id",
                ),
                (
                    "week_level.csv",
                    len(week_level),
                    len(week_level.columns),
                    "season + week",
                ),
                (
                    "contestant_level.csv",
                    len(contestant_level),
                    len(contestant_level.columns),
                    "season + contestant_id",
                ),
            ],
        ),
        "",
        (
            f"The long panel includes every source contestant in every audited week of "
            f"that season: {len(panel):,} rows, of which "
            f"{int(panel['active_status'].sum()):,} are active and "
            f"{int(panel['score_record_status'].eq('structural_zero_inactive').sum()):,} "
            "are retained structural-zero inactive rows. Weeks beyond each season's "
            "audited duration are not materialized."
        ),
        "",
        "## Cleaning and derivation rules",
        "",
        "1. Original judge-score values are preserved, including all values above 10.",
        "2. Raw score tokens are classified per judge. `N/A` is an explicit missing token; it is not converted to zero.",
        "3. A row is active when at least one judge score is positive. The data contain no active row with a mixture of positive and zero scores.",
        "4. All-zero inactive rows remain in the panel, but `judge_count`, `judge_total`, `judge_mean`, and `judge_pct` do not treat those zeros as performance scores.",
        "5. `judge_total` and `judge_mean` use only non-missing judges actually recorded for an active contestant-week. Within every observed season-week, all active contestants have the same judge count.",
        "6. `judge_pct` divides an active contestant's `judge_total` by the sum over active contestants in the same season-week. Inactive rows have missing `judge_pct`.",
        "7. Exact-name repeat appearances share a stable `contestant_id`; only appearances after the first season are marked `returning_contestant=True`.",
        "8. Elimination comes only from explicit `Eliminated Week N` result text. Withdrawals use audit-inferred last-positive-score weeks and are never labeled as eliminations.",
        "9. No-elimination, multiple-elimination, and finale flags are copied from the audited season-week table and reconciled after construction.",
        "10. Finale rows retain the supplied complete season placement; `week_level.final_placement_order` serializes that ranking for later strong constraints.",
        "",
        "### Score-cell states within audited season weeks",
        "",
        markdown_table(
            ["State", "Cells"],
            ((state, int(count)) for state, count in state_counts.items()),
        ),
        "",
        "## Aggregation regimes",
        "",
        (
            "No explicit rule field exists in the source. The documented fallback is "
            "therefore applied and recorded in every row."
        ),
        "",
        markdown_table(
            ["Regime", "Season range", "Seasons", "Season-weeks", "Panel rows", "Active rows"],
            regime_rows,
        ),
        "",
        "## Special-case reconciliation",
        "",
        markdown_table(["Case", "Audit", "Processed"], reconciliation_rows),
        "",
        "Withdrawals do not create elimination likelihoods. Multiple eliminations remain joint events, and no-elimination weeks contain zero eliminated contestants.",
        "",
        "## Partner normalization",
        "",
        "`partner_raw` is unchanged. Only audit-supported variants are canonicalized, and parenthetical/slash replacements are activated only in their stated week.",
        "",
    ]
    if alias_rows:
        lines.extend(
            [
                markdown_table(
                    ["Alias", "Canonical", "Alias count", "Canonical count", "Basis"],
                    alias_rows,
                ),
                "",
            ]
        )
    if not replacement_rows.empty:
        lines.extend(
            [
                markdown_table(
                    ["Season", "Week", "Contestant", "Raw", "Week partner", "Primary"],
                    replacement_rows.itertuples(index=False, name=None),
                ),
                "",
            ]
        )

    lines.extend(
        [
            "## Validation checks",
            "",
            "- Unique `season-week-contestant_id` keys in the long panel: passed.",
            "- Unique `season-week` keys in the week table: passed.",
            "- One contestant-level row per source contestant-season: passed.",
            "- Weekly active `judge_pct` sum equals 1 within numerical tolerance: passed.",
            "- Inactive structural-zero rows have missing derived score totals and shares: passed.",
            "- Audit event and score-above-10 counts reconcile exactly: passed.",
            "- No withdrawal row is marked as an elimination: passed.",
            "",
            "## Limitations and explicit assumptions",
            "",
            "- Gender is absent from the supplied data and is not inferred from names.",
            "- Aggregation regimes are season-range assumptions because the source has no explicit rule field.",
            "- Withdrawal, no-elimination, multiple-elimination, and finale timing inherit the documented audit inference rules.",
            "- Partner canonicalization is deliberately conservative. Unaudited spelling changes, marriage-name changes, and possible typographical errors remain unresolved rather than silently merged.",
            "- The data contain no observed audience vote. These outputs do not estimate or claim a true fan vote.",
            "",
            "## Generated artifacts",
            "",
            "- `data/processed/panel_long.csv`",
            "- `data/processed/week_level.csv`",
            "- `data/processed/contestant_level.csv`",
            "- `outputs/logs/preprocess_report.md`",
            "",
        ]
    )
    return "\n".join(lines)

