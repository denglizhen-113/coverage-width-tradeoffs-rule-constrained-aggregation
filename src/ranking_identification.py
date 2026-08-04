"""Ordinal preference identification for ranking and judge-save regimes.

The public signal is represented only through strict fan-rank permutations.
The module supports exact enumeration in small active fields and fixed-seed
uniform or Plackett-Luce proposal sampling in larger fields.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Iterator, Sequence

import numpy as np
import pandas as pd


TIE_POLICIES = (
    "average_rank",
    "min_rank",
    "dense_rank",
    "competition_rank",
)
DEFAULT_TIE_POLICY = "average_rank"

REQUIRED_COLUMNS = {
    "season",
    "week",
    "contestant_id",
    "contestant_name",
    "judge_total",
    "active_status",
    "eliminated_this_week",
    "withdrew_this_week",
    "no_elimination_week",
    "double_elimination_week",
    "finale_week",
    "placement",
    "aggregation_regime",
}


class RankingInputError(ValueError):
    """Raised when an observed week cannot support ordinal identification."""


@dataclass(frozen=True)
class RankingWeekSpec:
    season: int
    week: int
    regime: str
    contestant_ids: tuple[str, ...]
    contestant_names: tuple[str, ...]
    judge_totals: np.ndarray
    judge_ranks: np.ndarray
    eliminated_indices: tuple[int, ...]
    withdrawn_indices: tuple[int, ...]
    no_elimination_week: bool
    double_elimination_week: bool
    finale_week: bool
    finale_order_available: bool
    placements: np.ndarray
    tie_policy: str
    skip_reason: str = ""

    @property
    def n_active(self) -> int:
        return len(self.contestant_ids)


@dataclass
class RankDistributionAccumulator:
    """Sufficient statistics for feasible fan-rank distributions."""

    n_active: int
    accepted: int = 0

    def __post_init__(self) -> None:
        self.rank_counts = np.zeros((self.n_active, self.n_active), dtype=np.int64)

    def add(self, fan_ranks: np.ndarray, feasible_mask: np.ndarray) -> None:
        accepted = fan_ranks[np.asarray(feasible_mask, dtype=bool)]
        if accepted.size == 0:
            return
        self.accepted += int(len(accepted))
        for contestant in range(self.n_active):
            self.rank_counts[contestant] += np.bincount(
                accepted[:, contestant] - 1, minlength=self.n_active
            )

    def statistics(self, eliminated_indices: Sequence[int]) -> dict[str, float]:
        if self.accepted == 0:
            return {
                "ranking_entropy": np.nan,
                "normalized_ranking_entropy": np.nan,
                "mean_fan_rank_width": np.nan,
                "max_fan_rank_width": np.nan,
                "normalized_rank_width": np.nan,
                "eliminated_fan_rank_mean": np.nan,
                "eliminated_fan_rank_min": np.nan,
                "eliminated_fan_rank_max": np.nan,
            }

        probabilities = self.rank_counts / self.accepted
        entropy_by_contestant = np.zeros(self.n_active, dtype=float)
        widths = np.zeros(self.n_active, dtype=float)
        for contestant in range(self.n_active):
            positive = probabilities[contestant] > 0
            entropy_by_contestant[contestant] = -np.sum(
                probabilities[contestant, positive]
                * np.log(probabilities[contestant, positive])
            )
            supported = np.flatnonzero(self.rank_counts[contestant] > 0) + 1
            widths[contestant] = float(supported.max() - supported.min())

        mean_entropy = float(entropy_by_contestant.mean())
        normalized_entropy = (
            mean_entropy / math.log(self.n_active) if self.n_active > 1 else 0.0
        )
        mean_width = float(widths.mean())
        normalized_width = (
            mean_width / (self.n_active - 1) if self.n_active > 1 else 0.0
        )

        eliminated_counts = np.zeros(self.n_active, dtype=np.int64)
        for index in eliminated_indices:
            eliminated_counts += self.rank_counts[index]
        if eliminated_counts.sum() == 0:
            eliminated_mean = eliminated_min = eliminated_max = np.nan
        else:
            ranks = np.arange(1, self.n_active + 1)
            eliminated_mean = float(
                np.sum(ranks * eliminated_counts) / eliminated_counts.sum()
            )
            support = ranks[eliminated_counts > 0]
            eliminated_min = float(support.min())
            eliminated_max = float(support.max())

        return {
            "ranking_entropy": mean_entropy,
            "normalized_ranking_entropy": float(
                np.clip(normalized_entropy, 0.0, 1.0)
            ),
            "mean_fan_rank_width": mean_width,
            "max_fan_rank_width": float(widths.max()),
            "normalized_rank_width": float(np.clip(normalized_width, 0.0, 1.0)),
            "eliminated_fan_rank_mean": eliminated_mean,
            "eliminated_fan_rank_min": eliminated_min,
            "eliminated_fan_rank_max": eliminated_max,
        }

    def contestant_statistics(self) -> list[dict[str, float | int]]:
        """Return contestant-specific summaries from the full feasible set."""
        rows: list[dict[str, float | int]] = []
        ranks = np.arange(1, self.n_active + 1, dtype=float)
        for contestant in range(self.n_active):
            counts = self.rank_counts[contestant]
            if self.accepted == 0 or counts.sum() == 0:
                rows.append(
                    {
                        "contestant_index": contestant,
                        "fan_rank_mean": np.nan,
                        "fan_rank_min": np.nan,
                        "fan_rank_max": np.nan,
                        "fan_rank_width": np.nan,
                        "fan_rank_entropy": np.nan,
                    }
                )
                continue
            probabilities = counts / counts.sum()
            support = ranks[counts > 0]
            positive = probabilities > 0
            rows.append(
                {
                    "contestant_index": contestant,
                    "fan_rank_mean": float(np.sum(ranks * probabilities)),
                    "fan_rank_min": float(support.min()),
                    "fan_rank_max": float(support.max()),
                    "fan_rank_width": float(support.max() - support.min()),
                    "fan_rank_entropy": float(
                        -np.sum(probabilities[positive] * np.log(probabilities[positive]))
                    ),
                }
            )
        return rows


@dataclass(frozen=True)
class RankingIdentificationResult:
    """One week of ordinal identification and retained feasible details."""

    spec: RankingWeekSpec
    summary: dict[str, float | int | str | bool]
    detail: pd.DataFrame
    rank_counts: np.ndarray


def as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype(bool)
    return series.astype(str).str.strip().str.casefold().isin({"true", "1", "yes"})


def compute_judge_ranks(judge_totals: Sequence[float], tie_policy: str) -> np.ndarray:
    """Rank higher expert scores better (rank 1) under a named tie policy."""
    if tie_policy not in TIE_POLICIES:
        raise ValueError(f"Unsupported tie policy: {tie_policy}")
    values = pd.Series(np.asarray(judge_totals, dtype=float))
    if values.isna().any():
        raise RankingInputError("active_judge_total_missing")
    method = {
        "average_rank": "average",
        "min_rank": "min",
        "dense_rank": "dense",
        "competition_rank": "min",
    }[tie_policy]
    return values.rank(ascending=False, method=method).to_numpy(dtype=float)


def build_week_spec(week_df: pd.DataFrame, tie_policy: str) -> RankingWeekSpec:
    missing = sorted(REQUIRED_COLUMNS.difference(week_df.columns))
    if missing:
        raise RankingInputError(f"missing_required_columns: {missing}")
    keys = week_df[["season", "week"]].drop_duplicates()
    if len(keys) != 1:
        raise RankingInputError("week_df_must_contain_one_season_week")
    season = int(keys.iloc[0]["season"])
    week = int(keys.iloc[0]["week"])
    regimes = set(week_df["aggregation_regime"].dropna().astype(str))
    if len(regimes) != 1 or next(iter(regimes)) not in {"R", "R_plus"}:
        raise RankingInputError(f"unsupported_regime: {regimes}")
    regime = next(iter(regimes))

    active_mask = as_bool(week_df["active_status"])
    eliminated_all = as_bool(week_df["eliminated_this_week"])
    if (eliminated_all & ~active_mask).any():
        names = week_df.loc[eliminated_all & ~active_mask, "contestant_name"].astype(str)
        raise RankingInputError(
            "eliminated_contestant_outside_active_set: " + "; ".join(names)
        )
    active = week_df.loc[active_mask].sort_values("contestant_id", kind="stable")
    if len(active) < 2:
        raise RankingInputError("fewer_than_two_active_contestants")
    judge_totals = pd.to_numeric(active["judge_total"], errors="coerce").to_numpy()
    if np.isnan(judge_totals).any():
        raise RankingInputError("active_judge_total_missing")

    placements = pd.to_numeric(active["placement"], errors="coerce").to_numpy()
    finale = bool(as_bool(active["finale_week"]).iloc[0])
    finale_order_available = bool(
        finale
        and not np.isnan(placements).any()
        and len(np.unique(placements)) == len(active)
    )
    skip_reason = (
        "finale_placement_missing_or_nonunique"
        if finale and not finale_order_available
        else ""
    )

    eliminated = tuple(
        np.flatnonzero(as_bool(active["eliminated_this_week"]).to_numpy()).tolist()
    )
    withdrawn = tuple(
        np.flatnonzero(as_bool(active["withdrew_this_week"]).to_numpy()).tolist()
    )
    if set(eliminated).intersection(withdrawn):
        raise RankingInputError("contestant_marked_eliminated_and_withdrawn")
    return RankingWeekSpec(
        season=season,
        week=week,
        regime=regime,
        contestant_ids=tuple(active["contestant_id"].astype(str)),
        contestant_names=tuple(active["contestant_name"].astype(str)),
        judge_totals=judge_totals.astype(float),
        judge_ranks=compute_judge_ranks(judge_totals, tie_policy),
        eliminated_indices=eliminated,
        withdrawn_indices=withdrawn,
        no_elimination_week=bool(as_bool(active["no_elimination_week"]).iloc[0]),
        double_elimination_week=bool(
            as_bool(active["double_elimination_week"]).iloc[0]
        ),
        finale_week=finale,
        finale_order_available=finale_order_available,
        placements=placements.astype(float),
        tie_policy=tie_policy,
        skip_reason=skip_reason,
    )


def orders_to_fan_ranks(orders: np.ndarray) -> np.ndarray:
    """Convert best-to-worst contestant orders into per-contestant ranks."""
    orders = np.asarray(orders, dtype=np.int16)
    if orders.ndim != 2:
        raise ValueError("orders must be a two-dimensional array")
    n_rows, n_active = orders.shape
    ranks = np.empty_like(orders, dtype=np.int16)
    ranks[np.arange(n_rows)[:, None], orders] = np.arange(1, n_active + 1)
    return ranks


def _bottom_consistency(
    combined: np.ndarray,
    eliminated: Sequence[int],
    eligible: np.ndarray,
    bottom_size: int,
) -> np.ndarray:
    if not eliminated:
        return np.ones(len(combined), dtype=bool)
    if any(index not in set(eligible.tolist()) for index in eliminated):
        return np.zeros(len(combined), dtype=bool)
    size = min(int(bottom_size), len(eligible))
    if size <= 0:
        return np.zeros(len(combined), dtype=bool)
    eligible_scores = combined[:, eligible]
    threshold_index = len(eligible) - size
    threshold = np.partition(eligible_scores, threshold_index, axis=1)[
        :, threshold_index
    ]
    return np.all(combined[:, list(eliminated)] >= threshold[:, None] - 1e-12, axis=1)


def consistency_masks(
    spec: RankingWeekSpec, fan_ranks: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return direct-R-like and R_plus weak consistency masks."""
    fan_ranks = np.asarray(fan_ranks, dtype=float)
    if fan_ranks.ndim != 2 or fan_ranks.shape[1] != spec.n_active:
        raise ValueError("fan_ranks shape does not match the week specification")
    combined = fan_ranks + spec.judge_ranks[None, :]

    if spec.finale_week and spec.finale_order_available:
        placement_order = np.argsort(spec.placements, kind="stable")
        ordered_combined = combined[:, placement_order]
        valid = np.all(np.diff(ordered_combined, axis=1) >= -1e-12, axis=1)
        return valid, valid.copy()
    if spec.finale_week:
        valid = np.ones(len(fan_ranks), dtype=bool)
        return valid, valid.copy()
    if spec.no_elimination_week or not spec.eliminated_indices:
        valid = np.ones(len(fan_ranks), dtype=bool)
        return valid, valid.copy()

    withdrawn = set(spec.withdrawn_indices)
    eligible = np.asarray(
        [index for index in range(spec.n_active) if index not in withdrawn], dtype=int
    )
    k = len(spec.eliminated_indices)
    direct = _bottom_consistency(
        combined, spec.eliminated_indices, eligible, bottom_size=k
    )
    weak = _bottom_consistency(
        combined, spec.eliminated_indices, eligible, bottom_size=k + 1
    )
    return direct, weak


def exact_permutation_batches(
    n_active: int, batch_size: int = 50_000
) -> Iterator[tuple[int, np.ndarray]]:
    """Yield every permutation in deterministic lexicographic batches."""
    iterator = itertools.permutations(range(n_active))
    start = 0
    while True:
        batch = list(itertools.islice(iterator, batch_size))
        if not batch:
            break
        yield start, np.asarray(batch, dtype=np.int16)
        start += len(batch)


def uniform_permutation_batches(
    n_active: int,
    n_samples: int,
    rng: np.random.Generator,
    batch_size: int = 50_000,
) -> Iterator[tuple[int, np.ndarray]]:
    """Yield independent uniform random permutations using random-key sorting."""
    start = 0
    while start < n_samples:
        size = min(batch_size, n_samples - start)
        orders = np.argsort(rng.random((size, n_active)), axis=1).astype(np.int16)
        yield start, orders
        start += size


def plackett_luce_permutation_batches(
    worths: Sequence[float],
    n_samples: int,
    rng: np.random.Generator,
    batch_size: int = 50_000,
) -> Iterator[tuple[int, np.ndarray]]:
    """Yield Plackett-Luce rankings via the Gumbel top-k representation."""
    worths = np.asarray(worths, dtype=float)
    if np.any(~np.isfinite(worths)) or np.any(worths <= 0):
        raise ValueError("Plackett-Luce worths must be finite and positive")
    log_worths = np.log(worths)
    start = 0
    while start < n_samples:
        size = min(batch_size, n_samples - start)
        utilities = log_worths[None, :] + rng.gumbel(size=(size, len(worths)))
        orders = np.argsort(-utilities, axis=1).astype(np.int16)
        yield start, orders
        start += size


def proposal_worths(spec: RankingWeekSpec, mechanism: str) -> np.ndarray:
    """Construct outcome-guided PL proposal weights for diagnostic sampling."""
    worths = np.ones(spec.n_active, dtype=float)
    if spec.finale_week and spec.finale_order_available:
        centered = spec.placements - np.nanmin(spec.placements)
        worths *= np.exp(-0.25 * centered)
    elif spec.eliminated_indices:
        penalty = 0.65 if mechanism == "R_plus" else 0.45
        worths[list(spec.eliminated_indices)] *= penalty
    return worths


def seeded_rng(base_seed: int, season: int, week: int, stream: int) -> np.random.Generator:
    return np.random.default_rng(
        np.random.SeedSequence([int(base_seed), int(season), int(week), int(stream)])
    )


def monte_carlo_standard_error(accepted: int, evaluated: int) -> float:
    if evaluated <= 0:
        return np.nan
    probability = accepted / evaluated
    return float(math.sqrt(probability * (1.0 - probability) / evaluated))


def evaluate_acceptance_rate(
    spec: RankingWeekSpec,
    mechanism: str,
    batches: Iterator[tuple[int, np.ndarray]],
) -> tuple[int, int]:
    accepted = 0
    evaluated = 0
    for _, orders in batches:
        fan_ranks = orders_to_fan_ranks(orders)
        direct, weak = consistency_masks(spec, fan_ranks)
        mask = weak if mechanism == "R_plus" else direct
        accepted += int(mask.sum())
        evaluated += len(mask)
    return accepted, evaluated


def repeated_acceptance_sd(
    spec: RankingWeekSpec,
    mechanism: str,
    sampling_method: str,
    base_seed: int,
    n_samples: int = 2_000,
    n_repeats: int = 3,
) -> float:
    rates: list[float] = []
    for repeat in range(n_repeats):
        rng = seeded_rng(base_seed, spec.season, spec.week, 100 + repeat)
        if sampling_method == "uniform":
            batches = uniform_permutation_batches(spec.n_active, n_samples, rng)
        elif sampling_method == "plackett_luce_guided":
            batches = plackett_luce_permutation_batches(
                proposal_worths(spec, mechanism), n_samples, rng
            )
        else:
            raise ValueError(f"Unknown sampling method: {sampling_method}")
        accepted, evaluated = evaluate_acceptance_rate(spec, mechanism, batches)
        rates.append(accepted / evaluated)
    return float(np.std(rates, ddof=1)) if len(rates) > 1 else 0.0


def summarize_accumulator(
    spec: RankingWeekSpec,
    accumulator: RankDistributionAccumulator,
    *,
    n_total_permutations: int,
    n_evaluated_permutations: int,
    direct_feasible_count: int,
    enumeration_method: str,
    sampling_method: str,
) -> dict[str, float | int | str | bool]:
    stats = accumulator.statistics(spec.eliminated_indices)
    feasible_fraction = (
        accumulator.accepted / n_evaluated_permutations
        if n_evaluated_permutations
        else np.nan
    )
    direct_fraction = (
        direct_feasible_count / n_evaluated_permutations
        if n_evaluated_permutations
        else np.nan
    )
    loss_ratio = (
        accumulator.accepted / direct_feasible_count
        if spec.regime == "R_plus" and direct_feasible_count > 0
        else (1.0 if spec.regime == "R" and direct_feasible_count > 0 else np.nan)
    )
    return {
        "season": spec.season,
        "week": spec.week,
        "regime": spec.regime,
        "n_active": spec.n_active,
        "n_total_permutations": n_total_permutations,
        "n_evaluated_permutations": n_evaluated_permutations,
        "n_feasible_permutations": accumulator.accepted,
        "feasible_fraction": feasible_fraction,
        **stats,
        "n_feasible_direct_R_like": direct_feasible_count,
        "feasible_fraction_direct_R_like": direct_fraction,
        "identifiability_loss_ratio": loss_ratio,
        "tie_policy": spec.tie_policy,
        "finale_week": spec.finale_week,
        "double_elimination_week": spec.double_elimination_week,
        "enumeration_method": enumeration_method,
        "sampling_method": sampling_method,
        "finale_order_available": spec.finale_order_available,
        "skip_reason": spec.skip_reason,
        "mc_standard_error": (
            monte_carlo_standard_error(
                accumulator.accepted, n_evaluated_permutations
            )
            if enumeration_method == "monte_carlo"
            else 0.0
        ),
    }


def identify_week(
    spec: RankingWeekSpec,
    *,
    exact_threshold: int = 9,
    n_samples: int = 10_000,
    base_seed: int = 20260714,
    detail_limit: int | None = 1_000,
    batch_size: int = 50_000,
) -> RankingIdentificationResult:
    """Enumerate or sample one week's feasible public ranking set.

    Exact counts and distributional summaries always use every enumerated
    permutation. ``detail_limit`` only caps the retained long-form ranking
    records written for audit and inspection.
    """
    if exact_threshold < 1:
        raise ValueError("exact_threshold must be positive")
    if n_samples < 1:
        raise ValueError("n_samples must be positive")
    if detail_limit is not None and detail_limit < 0:
        raise ValueError("detail_limit must be nonnegative or None")
    if spec.regime not in {"R", "R_plus"}:
        raise ValueError(f"Unsupported mechanism: {spec.regime}")

    exact = spec.n_active <= exact_threshold
    enumeration_method = "exact" if exact else "monte_carlo"
    sampling_method = "none" if exact else "uniform"
    total_permutations = math.factorial(spec.n_active)
    if exact:
        batches = exact_permutation_batches(spec.n_active, batch_size=batch_size)
    else:
        rng = seeded_rng(base_seed, spec.season, spec.week, 0)
        batches = uniform_permutation_batches(
            spec.n_active, n_samples, rng, batch_size=batch_size
        )

    accumulator = RankDistributionAccumulator(spec.n_active)
    direct_feasible_count = 0
    evaluated = 0
    retained: list[tuple[int, np.ndarray, bool, bool]] = []
    feasible_seen = 0
    detail_rng = seeded_rng(base_seed, spec.season, spec.week, 999)
    for start, orders in batches:
        fan_ranks = orders_to_fan_ranks(orders)
        direct, weak = consistency_masks(spec, fan_ranks)
        feasible = weak if spec.regime == "R_plus" else direct
        accumulator.add(fan_ranks, feasible)
        direct_feasible_count += int(direct.sum())
        evaluated += len(fan_ranks)

        for position in np.flatnonzero(feasible):
            feasible_seen += 1
            record = (
                start + int(position),
                fan_ranks[position].copy(),
                bool(direct[position]),
                bool(weak[position]),
            )
            if detail_limit is None:
                retained.append(record)
            elif detail_limit > 0 and len(retained) < detail_limit:
                retained.append(record)
            elif detail_limit > 0:
                replacement = int(detail_rng.integers(0, feasible_seen))
                if replacement < detail_limit:
                    retained[replacement] = record

    summary = summarize_accumulator(
        spec,
        accumulator,
        n_total_permutations=total_permutations,
        n_evaluated_permutations=evaluated,
        direct_feasible_count=direct_feasible_count,
        enumeration_method=enumeration_method,
        sampling_method=sampling_method,
    )
    summary["feasible_count_type"] = (
        "exact_count" if exact else "accepted_sample_draws"
    )
    summary["estimated_n_feasible_permutations"] = (
        float(summary["feasible_fraction"]) * total_permutations
        if np.isfinite(float(summary["feasible_fraction"]))
        else np.nan
    )
    retained.sort(key=lambda item: item[0])
    retained_count = len(retained)
    summary["detail_retained_permutations"] = retained_count
    summary["detail_truncated"] = retained_count < accumulator.accepted
    summary["detail_retention_method"] = (
        "none"
        if detail_limit == 0
        else (
            "fixed_seed_reservoir"
            if retained_count < accumulator.accepted
            else "all_feasible"
        )
    )

    detail_rows: list[dict[str, float | int | str | bool]] = []
    for permutation_id, fan_ranks, direct_ok, weak_ok in retained:
        combined = spec.judge_ranks + fan_ranks
        for contestant in range(spec.n_active):
            detail_rows.append(
                {
                    "season": spec.season,
                    "week": spec.week,
                    "permutation_id": permutation_id,
                    "contestant_id": spec.contestant_ids[contestant],
                    "contestant_name": spec.contestant_names[contestant],
                    "judge_rank": spec.judge_ranks[contestant],
                    "fan_rank": int(fan_ranks[contestant]),
                    "combined_rank_score": combined[contestant],
                    "eliminated_this_week": contestant
                    in spec.eliminated_indices,
                    "is_feasible": True,
                    "bottom_two_consistent": weak_ok,
                    "direct_elimination_consistent": direct_ok,
                    "identifiability_loss_ratio": summary[
                        "identifiability_loss_ratio"
                    ],
                    "tie_policy": spec.tie_policy,
                    "enumeration_method": enumeration_method,
                }
            )
    detail_columns = [
        "season",
        "week",
        "permutation_id",
        "contestant_id",
        "contestant_name",
        "judge_rank",
        "fan_rank",
        "combined_rank_score",
        "eliminated_this_week",
        "is_feasible",
        "bottom_two_consistent",
        "direct_elimination_consistent",
        "identifiability_loss_ratio",
        "tie_policy",
        "enumeration_method",
    ]
    return RankingIdentificationResult(
        spec=spec,
        summary=summary,
        detail=pd.DataFrame(detail_rows, columns=detail_columns),
        rank_counts=accumulator.rank_counts.copy(),
    )
