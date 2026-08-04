from __future__ import annotations

import numpy as np
import pandas as pd

from src.dynamic_preference import (
    build_dynamic_public_appeal,
    exponential_smooth,
    uncertainty_weighted_smooth,
)


def test_exponential_smoothing_and_missing_carry_forward() -> None:
    smoothed, used = exponential_smooth([0.2, 0.8, np.nan, 0.4], 0.5)
    assert np.allclose(smoothed, [0.2, 0.5, 0.5, 0.45], equal_nan=True)
    assert used.tolist() == [True, True, False, True]


def test_uncertainty_reduces_update_weight() -> None:
    values = [0.2, 0.8, 0.8]
    result, _, effective = uncertainty_weighted_smooth(values, [0.0, 0.0, 1.0], 0.5)
    assert effective[1] > effective[2]
    assert result[2] < 0.8


def test_dynamic_output_is_bounded_and_reproducible() -> None:
    features = pd.DataFrame(
        {
            "season": [1, 1, 1],
            "week": [1, 2, 3],
            "contestant_id": ["a", "a", "a"],
            "contestant_season_id": ["s1-a"] * 3,
            "contestant_name": ["A"] * 3,
            "aggregation_regime": ["R"] * 3,
            "public_appeal_proxy": [0.1, 0.9, 0.2],
            "public_appeal_uncertainty": [0.2, 0.8, 0.4],
        }
    )
    first = build_dynamic_public_appeal(features)
    second = build_dynamic_public_appeal(features)
    assert first["dynamic_public_appeal"].between(0, 1).all()
    assert np.allclose(first["dynamic_public_appeal"], second["dynamic_public_appeal"])
