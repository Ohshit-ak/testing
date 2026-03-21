"""
Tests for dice.py — covers the `cards/dice` module nodes from the call graph:
  dice.roll, dice.is_doubles

BUG documented in call graph:
  - dice.roll() uses randint(1,5) — should be randint(1,6), so max total is 10 not 12
"""

import pytest
from unittest.mock import patch
from moneypoly.dice import Dice


# ─── __init__ / reset ─────────────────────────────────────────────────────────

class TestDiceInit:
    def test_initial_values(self, dice):
        assert dice.die1 == 0
        assert dice.die2 == 0
        assert dice.doubles_streak == 0

    def test_reset_clears_values(self, dice):
        dice.die1 = 3
        dice.die2 = 5
        dice.doubles_streak = 2
        dice.reset()
        assert dice.die1 == 0
        assert dice.die2 == 0
        assert dice.doubles_streak == 0


# ─── roll — BUG: uses randint(1,5) not randint(1,6) ──────────────────────────

class TestRoll:
    def test_roll_returns_sum(self, dice):
        with patch("moneypoly.dice.random.randint", side_effect=[3, 4]):
            result = dice.roll()
        assert result == 7

    def test_roll_bug_max_is_10_not_12(self, dice):
        """
        BUG (call graph): randint(1,5) means each die max is 5, so
        the maximum possible total is 10 — a standard d6 game needs 12.
        This test verifies the range of actual calls to confirm the bug.
        """
        with patch("moneypoly.dice.random.randint", return_value=5) as mock_randint:
            total = dice.roll()
        mock_randint.assert_called_with(1, 5)   # BUG: should be (1, 6)
        assert total == 10                       # BUG: should be able to be 12

    def test_roll_sets_die_values(self, dice):
        with patch("moneypoly.dice.random.randint", side_effect=[2, 5]):
            dice.roll()
        assert dice.die1 == 2
        assert dice.die2 == 5

    def test_roll_increments_doubles_streak_on_doubles(self, dice):
        with patch("moneypoly.dice.random.randint", side_effect=[3, 3]):
            dice.roll()
        assert dice.doubles_streak == 1

    def test_roll_resets_doubles_streak_on_non_doubles(self, dice):
        dice.doubles_streak = 2
        with patch("moneypoly.dice.random.randint", side_effect=[2, 4]):
            dice.roll()
        assert dice.doubles_streak == 0

    def test_roll_accumulates_doubles_streak(self, dice):
        with patch("moneypoly.dice.random.randint", side_effect=[3, 3, 2, 2]):
            dice.roll()
            dice.roll()
        assert dice.doubles_streak == 2


# ─── is_doubles ───────────────────────────────────────────────────────────────

class TestIsDoubles:
    def test_is_doubles_true(self, dice):
        dice.die1 = 3
        dice.die2 = 3
        assert dice.is_doubles() is True

    def test_is_doubles_false(self, dice):
        dice.die1 = 2
        dice.die2 = 4
        assert dice.is_doubles() is False

    def test_is_doubles_after_roll(self, dice):
        with patch("moneypoly.dice.random.randint", side_effect=[5, 5]):
            dice.roll()
        assert dice.is_doubles() is True


# ─── total / describe ─────────────────────────────────────────────────────────

class TestDiceHelpers:
    def test_total(self, dice):
        dice.die1 = 3
        dice.die2 = 4
        assert dice.total() == 7

    def test_describe_includes_doubles(self, dice):
        dice.die1 = 4
        dice.die2 = 4
        assert "DOUBLES" in dice.describe()

    def test_describe_no_doubles(self, dice):
        dice.die1 = 2
        dice.die2 = 5
        assert "DOUBLES" not in dice.describe()

    def test_repr(self, dice):
        assert "Dice" in repr(dice)
