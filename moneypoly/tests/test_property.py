"""
Tests for property.py — covers the `property` module nodes from the call graph:
  prop.get_rent, prop.mortgage, prop.unmortgage, group.all_owned_by

BUGs documented in call graph:
  - prop.get_rent(): group.all_owned_by uses any() not all() — doubles rent too early
  - group.all_owned_by(): any() means 1 property triggers full-group rent
"""

import pytest
from moneypoly.property import Property, PropertyGroup
from moneypoly.player import Player


# ─── PropertyGroup.all_owned_by — BUG: uses any() instead of all() ──────────

class TestAllOwnedBy:
    def setup_method(self):
        self.grp = PropertyGroup("Brown", "brown")
        self.p1 = Property("Mediterranean", 1, 60, 2, self.grp)
        self.p2 = Property("Baltic", 3, 60, 4, self.grp)
        self.owner = Player("Alice")
        self.other = Player("Bob")

    def test_all_owned_by_returns_true_when_only_one_owned(self):
        """
        BUG (call graph): all_owned_by() uses any() so it returns True even
        when only ONE property in the group is owned by `player`.
        This test documents the CURRENT (buggy) behaviour.
        """
        self.p1.owner = self.owner  # owns 1 of 2 in the group
        # With any(): True (BUG) — should be False until all are owned
        assert self.grp.all_owned_by(self.owner) is True  # documents bug

    def test_all_owned_by_false_when_none_owned(self):
        assert self.grp.all_owned_by(self.owner) is False

    def test_all_owned_by_false_for_none_player(self):
        self.p1.owner = self.owner
        assert self.grp.all_owned_by(None) is False

    def test_all_owned_by_correct_owner_vs_wrong_owner(self):
        self.p1.owner = self.owner
        self.p2.owner = self.owner
        # any() → True for other if other has at least one; here other has none → False
        assert self.grp.all_owned_by(self.other) is False

    def test_all_owned_by_with_two_owners(self):
        """
        When properties are split between two players, any() still returns True
        for BOTH because each one owns at least one property.
        This is another manifestation of the bug.
        """
        self.p1.owner = self.owner
        self.p2.owner = self.other
        # any() for self.owner: p1 is owned by owner → True (BUG)
        assert self.grp.all_owned_by(self.owner) is True  # documents bug

    def test_group_size(self):
        assert self.grp.size() == 2

    def test_get_owner_counts_empty(self):
        assert self.grp.get_owner_counts() == {}

    def test_get_owner_counts_single(self):
        self.p1.owner = self.owner
        counts = self.grp.get_owner_counts()
        assert counts[self.owner] == 1


# ─── Property.get_rent ────────────────────────────────────────────────────────

class TestGetRent:
    def setup_method(self):
        self.grp = PropertyGroup("Brown", "brown")
        self.p1 = Property("Med", 1, 60, 2, self.grp)
        self.p2 = Property("Bal", 3, 60, 4, self.grp)
        self.owner = Player("Alice")

    def test_base_rent(self):
        self.p1.owner = self.owner
        # only owns p1 — but with bug any() returns True → doubled rent
        # (Test below explicitly documents that the doubling fires with 1/2 owned)
        assert self.p1.get_rent() == self.p1.base_rent * 2  # BUG visible here

    def test_rent_zero_if_mortgaged(self):
        self.p1.owner = self.owner
        self.p1.is_mortgaged = True
        assert self.p1.get_rent() == 0

    def test_rent_without_group(self):
        solo_prop = Property("Solo", 5, 100, 10, None)
        solo_prop.owner = self.owner
        assert solo_prop.get_rent() == 10

    def test_rent_doubled_when_all_owned_correctly(self):
        """
        Due to the bug, doubled rent fires even with 1 property owned.
        This test is for documentation / future fix: once fixed,
        rent should be doubled ONLY when all group props are owned.
        """
        self.p1.owner = self.owner
        self.p2.owner = self.owner
        # After fix: should be doubled because group actually fully owned
        # With bug: same result but for wrong reason
        assert self.p1.get_rent() == self.p1.base_rent * 2


# ─── Property.mortgage ────────────────────────────────────────────────────────

class TestMortgage:
    def test_mortgage_returns_half_price(self, prop):
        payout = prop.mortgage()
        assert payout == prop.price // 2

    def test_mortgage_sets_flag(self, prop):
        prop.mortgage()
        assert prop.is_mortgaged is True

    def test_mortgage_already_mortgaged_returns_zero(self, prop):
        prop.mortgage()
        result = prop.mortgage()
        assert result == 0

    def test_is_available_after_mortgage(self, prop):
        prop.mortgage()
        assert prop.is_available() is False

    def test_is_available_unowned_unmortgaged(self, prop):
        assert prop.is_available() is True


# ─── Property.unmortgage ──────────────────────────────────────────────────────

class TestUnmortgage:
    def test_unmortgage_returns_110_percent(self, prop):
        prop.mortgage()
        cost = prop.unmortgage()
        expected = int(prop.mortgage_value * 1.1)
        assert cost == expected

    def test_unmortgage_clears_flag(self, prop):
        prop.mortgage()
        prop.unmortgage()
        assert prop.is_mortgaged is False

    def test_unmortgage_not_mortgaged_returns_zero(self, prop):
        result = prop.unmortgage()
        assert result == 0

    def test_mortgage_value_is_half_price(self, prop):
        assert prop.mortgage_value == prop.price // 2


# ─── PropertyGroup helpers ────────────────────────────────────────────────────

class TestPropertyGroupHelpers:
    def test_add_property_sets_group_back_link(self, group):
        prop = Property("A", 1, 100, 10, None)
        group.add_property(prop)
        assert prop in group.properties
        assert prop.group == group

    def test_add_property_no_duplicate(self, group):
        p = Property("A", 1, 100, 10, group)
        group.add_property(p)  # attempt to add again
        assert group.properties.count(p) == 1

    def test_repr_contains_name(self, group):
        assert "Test" in repr(group)


# ─── Property.__repr__ ────────────────────────────────────────────────────────

class TestPropertyRepr:
    def test_repr_unowned(self, prop):
        r = repr(prop)
        assert "unowned" in r

    def test_repr_owned(self, prop, player):
        prop.owner = player
        r = repr(prop)
        assert player.name in r

    def test_is_available_when_owned(self, prop, player):
        prop.owner = player
        assert prop.is_available() is False
