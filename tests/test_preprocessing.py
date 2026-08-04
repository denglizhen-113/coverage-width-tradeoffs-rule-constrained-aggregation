"""Focused tests for rule boundaries and special-case parsing."""

from __future__ import annotations

import unittest

import pandas as pd

from src.preprocessing import (
    aggregation_regime,
    parse_elimination_week,
    parse_partner_assignment,
    score_value_state,
    stable_contestant_id,
)


class PreprocessingRuleTests(unittest.TestCase):
    def test_aggregation_regime_boundaries(self) -> None:
        self.assertEqual(aggregation_regime(1), "R")
        self.assertEqual(aggregation_regime(2), "R")
        self.assertEqual(aggregation_regime(3), "P")
        self.assertEqual(aggregation_regime(27), "P")
        self.assertEqual(aggregation_regime(28), "R_plus")
        self.assertEqual(aggregation_regime(34), "R_plus")
        with self.assertRaises(ValueError):
            aggregation_regime(35)

    def test_parenthetical_partner_replacement_is_week_specific(self) -> None:
        aliases = {"Val Chmerkovskiy": "Valentin Chmerkovskiy"}
        raw = "Val Chmerkovskiy (Joey Graziadei week 9)"
        week_8 = parse_partner_assignment(raw, 8, aliases)
        week_9 = parse_partner_assignment(raw, 9, aliases)
        self.assertEqual(week_8["partner_clean"], "Valentin Chmerkovskiy")
        self.assertEqual(week_8["partner_assignment_role"], "primary")
        self.assertEqual(week_9["partner_clean"], "Joey Graziadei")
        self.assertEqual(week_9["partner_assignment_role"], "replacement")

    def test_slash_partner_replacement_is_week_specific(self) -> None:
        raw = "Emma Slater/Kaitlyn Bristowe (week 9)"
        week_8 = parse_partner_assignment(raw, 8, {})
        week_9 = parse_partner_assignment(raw, 9, {})
        self.assertEqual(week_8["partner_clean"], "Emma Slater")
        self.assertEqual(week_9["partner_clean"], "Kaitlyn Bristowe")

    def test_score_states_keep_zero_and_missing_distinct(self) -> None:
        self.assertEqual(
            score_value_state("0", 0.0, False), "structural_zero_inactive"
        )
        self.assertEqual(score_value_state("0", 0.0, True), "observed_zero_active")
        self.assertEqual(
            score_value_state("N/A", pd.NA, True), "explicit_missing_token"
        )
        self.assertEqual(score_value_state("", pd.NA, False), "empty_string")
        self.assertEqual(score_value_state("11.5", 11.5, True), "observed_score")

    def test_identifiers_and_elimination_parsing_are_deterministic(self) -> None:
        self.assertEqual(stable_contestant_id("Kelly Monaco"), stable_contestant_id("Kelly Monaco"))
        self.assertEqual(parse_elimination_week("Eliminated Week 7"), 7)
        self.assertIsNone(parse_elimination_week("Withdrew"))


if __name__ == "__main__":
    unittest.main()

