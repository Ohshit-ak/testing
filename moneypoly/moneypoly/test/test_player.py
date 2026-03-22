import pytest

from moneypoly.config import GO_SALARY, JAIL_POSITION
from moneypoly.player import Player
from moneypoly.property import Property


class TestPlayer:
    def test_add_money_increases_balance(self, player_a):
        # Verifies positive add-money path updates balance.
        before = player_a.balance
        player_a.add_money(10)
        assert player_a.balance == before + 10

    def test_add_money_raises_for_negative(self, player_a):
        # Verifies add-money guard branch rejects negative values.
        with pytest.raises(ValueError):
            player_a.add_money(-1)

    def test_deduct_money_decreases_balance(self, player_a):
        # Verifies deduct-money path updates balance correctly.
        before = player_a.balance
        player_a.deduct_money(10)
        assert player_a.balance == before - 10

    def test_deduct_money_raises_for_negative(self, player_a):
        # Verifies deduct-money guard branch rejects negative values.
        with pytest.raises(ValueError):
            player_a.deduct_money(-1)

    def test_is_bankrupt_true_on_zero(self, player_a):
        # Verifies bankrupt predicate true branch at boundary zero.
        player_a.balance = 0
        assert player_a.is_bankrupt() is True

    def test_is_bankrupt_false_positive_balance(self, player_a):
        # Verifies bankrupt predicate false branch for solvent player.
        player_a.balance = 1
        assert player_a.is_bankrupt() is False

    def test_net_worth_returns_balance(self, player_a):
        # Verifies net-worth branch returns current balance value.
        player_a.balance = 42
        assert player_a.net_worth() == 42

    def test_move_wraps_position(self, player_a):
        # Verifies movement branch wraps around board boundaries.
        player_a.position = 39
        assert player_a.move(2) == 1

    def test_move_awards_go_salary_when_passing_go(self, player_a):
        # Verifies pass-go branch awards salary on wrap-around.
        player_a.position = 39
        before = player_a.balance
        player_a.move(2)
        assert player_a.balance == before + GO_SALARY

    def test_move_no_salary_for_zero_steps(self, player_a):
        # Verifies zero-step branch does not award salary.
        before = player_a.balance
        player_a.move(0)
        assert player_a.balance == before

    def test_go_to_jail_sets_position(self, player_a):
        # Verifies jail transition sets player to jail location.
        player_a.go_to_jail()
        assert player_a.position == JAIL_POSITION

    def test_go_to_jail_sets_flag(self, player_a):
        # Verifies jail transition marks player as jailed.
        player_a.go_to_jail()
        assert player_a.in_jail is True

    def test_add_property_adds_once(self, player_a):
        # Verifies add-property path avoids duplicate entries.
        prop = Property("P", 1, 10, 1)
        player_a.add_property(prop)
        player_a.add_property(prop)
        assert len(player_a.properties) == 1

    def test_remove_property_removes_existing(self, player_a):
        # Verifies remove-property path removes owned property.
        prop = Property("P", 1, 10, 1)
        player_a.add_property(prop)
        player_a.remove_property(prop)
        assert prop not in player_a.properties

    def test_remove_property_ignores_missing(self, player_a):
        # Verifies remove-property branch handles absent property safely.
        prop = Property("P", 1, 10, 1)
        player_a.remove_property(prop)
        assert len(player_a.properties) == 0

    def test_count_properties_returns_length(self, player_a):
        # Verifies property-count branch reflects owned properties.
        player_a.add_property(Property("P", 1, 10, 1))
        assert player_a.count_properties() == 1

    def test_status_line_includes_jail_tag_when_jailed(self, player_a):
        # Verifies status formatting branch includes jailed marker.
        player_a.in_jail = True
        assert "[JAILED]" in player_a.status_line()

    def test_status_line_excludes_jail_tag_when_free(self, player_a):
        # Verifies status formatting branch excludes jailed marker.
        player_a.in_jail = False
        assert "[JAILED]" not in player_a.status_line()

    def test_repr_contains_player_name(self, player_a):
        # Verifies repr branch includes class marker for debugging.
        assert "Player(" in repr(player_a)
