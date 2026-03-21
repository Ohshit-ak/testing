"""
Tests for player.py — covers the `player` module nodes from the call graph:
  player.add_money, player.deduct_money, player.is_bankrupt, player.net_worth,
  player.move, player.go_to_jail, player.add_property, player.remove_property

BUG documented in call graph:
  - player.net_worth() returns balance only — ignores property values entirely
"""

import pytest
from moneypoly.player import Player
from moneypoly.config import (
    STARTING_BALANCE, BOARD_SIZE, GO_SALARY, JAIL_POSITION
)


# ─── __init__ / initial state ─────────────────────────────────────────────────

class TestPlayerInit:
    def test_default_balance(self):
        p = Player("Alice")
        assert p.balance == STARTING_BALANCE

    def test_custom_balance(self):
        p = Player("Alice", balance=500)
        assert p.balance == 500

    def test_initial_position_zero(self):
        p = Player("Alice")
        assert p.position == 0

    def test_initial_properties_empty(self):
        p = Player("Alice")
        assert p.properties == []

    def test_not_in_jail_initially(self):
        p = Player("Alice")
        assert p.in_jail is False
        assert p.jail_turns == 0

    def test_not_eliminated_initially(self):
        p = Player("Alice")
        assert p.is_eliminated is False

    def test_no_jail_cards_initially(self):
        p = Player("Alice")
        assert p.get_out_of_jail_cards == 0


# ─── add_money ────────────────────────────────────────────────────────────────

class TestAddMoney:
    def test_add_positive(self, player):
        player.add_money(200)
        assert player.balance == STARTING_BALANCE + 200

    def test_add_zero(self, player):
        player.add_money(0)
        assert player.balance == STARTING_BALANCE

    def test_add_negative_raises(self, player):
        with pytest.raises(ValueError):
            player.add_money(-50)

    def test_add_does_not_affect_position(self, player):
        player.add_money(100)
        assert player.position == 0


# ─── deduct_money ─────────────────────────────────────────────────────────────

class TestDeductMoney:
    def test_deduct_positive(self, player):
        player.deduct_money(200)
        assert player.balance == STARTING_BALANCE - 200

    def test_deduct_zero(self, player):
        player.deduct_money(0)
        assert player.balance == STARTING_BALANCE

    def test_deduct_negative_raises(self, player):
        with pytest.raises(ValueError):
            player.deduct_money(-10)

    def test_deduct_allows_negative_balance(self, player):
        """deduct_money does NOT guard against going negative — by design."""
        player.deduct_money(STARTING_BALANCE + 100)
        assert player.balance == -100


# ─── is_bankrupt ──────────────────────────────────────────────────────────────

class TestIsBankrupt:
    def test_not_bankrupt_with_full_balance(self, player):
        assert player.is_bankrupt() is False

    def test_bankrupt_at_zero(self, player):
        player.balance = 0
        assert player.is_bankrupt() is True

    def test_bankrupt_below_zero(self, player):
        player.balance = -1
        assert player.is_bankrupt() is True

    def test_not_bankrupt_with_one_dollar(self, player):
        player.balance = 1
        assert player.is_bankrupt() is False


# ─── net_worth — BUG: ignores property values ─────────────────────────────────

class TestNetWorth:
    def test_net_worth_equals_balance_only(self, player):
        """
        BUG (call graph): net_worth() returns balance only — property
        values are completely ignored.
        This test documents the CURRENT (buggy) behaviour.
        """
        assert player.net_worth() == player.balance

    def test_net_worth_unchanged_after_acquiring_property(self, player, prop):
        """
        BUG: adding a property should increase net_worth but it does not,
        because net_worth() ignores properties.
        """
        player.add_property(prop)
        # Current (buggy) behaviour: still equals balance only
        assert player.net_worth() == player.balance

    def test_net_worth_bug_does_not_include_property_value(self, player, prop):
        """
        Explicitly show that prop.price is NOT reflected in net_worth.
        If the bug were fixed, net_worth() would be balance + prop.price.
        """
        player.balance = 1000
        player.add_property(prop)          # prop.price == 100
        # Should be 1100 if fixed, but is 1000 due to bug
        assert player.net_worth() == 1000


# ─── move ─────────────────────────────────────────────────────────────────────

class TestMove:
    def test_move_forward(self, player):
        player.move(5)
        assert player.position == 5

    def test_move_wraps_around(self, player):
        player.position = 38
        player.move(5)
        assert player.position == (38 + 5) % BOARD_SIZE

    def test_lands_on_go_awards_salary(self, player):
        player.position = 38
        player.move(2)    # 38+2 = 40 → 0 (Go)
        assert player.position == 0
        assert player.balance == STARTING_BALANCE + GO_SALARY

    def test_move_returns_new_position(self, player):
        pos = player.move(7)
        assert pos == 7

    def test_not_passing_go_no_salary(self, player):
        player.move(1)    # position 1 — did not pass Go
        assert player.balance == STARTING_BALANCE


# ─── go_to_jail ───────────────────────────────────────────────────────────────

class TestGoToJail:
    def test_position_set_to_jail(self, player):
        player.go_to_jail()
        assert player.position == JAIL_POSITION

    def test_in_jail_flag_set(self, player):
        player.go_to_jail()
        assert player.in_jail is True

    def test_jail_turns_reset(self, player):
        player.jail_turns = 2
        player.go_to_jail()
        assert player.jail_turns == 0


# ─── add_property / remove_property ──────────────────────────────────────────

class TestPropertyHoldings:
    def test_add_property(self, player, prop):
        player.add_property(prop)
        assert prop in player.properties

    def test_add_property_no_duplicate(self, player, prop):
        player.add_property(prop)
        player.add_property(prop)
        assert player.properties.count(prop) == 1

    def test_remove_property(self, player, prop):
        player.add_property(prop)
        player.remove_property(prop)
        assert prop not in player.properties

    def test_remove_property_not_owned(self, player, prop):
        """Removing a property the player doesn't own is a no-op."""
        player.remove_property(prop)  # should not raise
        assert prop not in player.properties

    def test_count_properties(self, player, prop):
        player.add_property(prop)
        assert player.count_properties() == 1

    def test_count_properties_empty(self, player):
        assert player.count_properties() == 0


# ─── helpers ──────────────────────────────────────────────────────────────────

class TestPlayerHelpers:
    def test_status_line_contains_name(self, player):
        assert "Alice" in player.status_line()

    def test_status_line_jail_tag(self, player):
        player.go_to_jail()
        assert "[JAILED]" in player.status_line()

    def test_repr(self, player):
        assert "Alice" in repr(player)
