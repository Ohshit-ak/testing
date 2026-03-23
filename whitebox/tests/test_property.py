from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup


class TestProperty:
    def test_get_rent_returns_zero_when_mortgaged(self):
        # Verifies mortgaged branch suppresses rent collection.
        prop = Property("P", 1, 100, 10)
        prop.is_mortgaged = True
        assert prop.get_rent() == 0

    def test_get_rent_returns_base_without_group(self):
        # Verifies no-group branch uses base rent value.
        prop = Property("P", 1, 100, 10)
        assert prop.get_rent() == 10

    def test_get_rent_doubles_for_full_group_owner(self):
        # Verifies full-group ownership branch doubles rent.
        group = PropertyGroup("G", "c")
        owner = Player("O")
        p1 = Property("A", 1, 60, 2, group)
        p2 = Property("B", 3, 60, 4, group)
        p1.owner = owner
        p2.owner = owner
        assert p1.get_rent() == 4

    def test_mortgage_sets_state(self):
        # Verifies mortgage branch toggles mortgaged status.
        prop = Property("P", 1, 100, 10)
        prop.mortgage()
        assert prop.is_mortgaged is True

    def test_mortgage_returns_zero_if_already_mortgaged(self):
        # Verifies duplicate mortgage guard branch.
        prop = Property("P", 1, 100, 10)
        prop.is_mortgaged = True
        assert prop.mortgage() == 0

    def test_unmortgage_returns_zero_if_not_mortgaged(self):
        # Verifies unmortgage guard branch when property is free.
        prop = Property("P", 1, 100, 10)
        assert prop.unmortgage() == 0

    def test_unmortgage_clears_mortgage(self):
        # Verifies unmortgage branch restores active property state.
        prop = Property("P", 1, 100, 10)
        prop.is_mortgaged = True
        prop.unmortgage()
        assert prop.is_mortgaged is False

    def test_is_available_true_for_unowned_unmortgaged(self):
        # Verifies availability branch for purchasable property.
        prop = Property("P", 1, 100, 10)
        assert prop.is_available() is True

    def test_is_available_false_for_owned(self):
        # Verifies availability branch blocks owned property.
        prop = Property("P", 1, 100, 10)
        prop.owner = Player("O")
        assert prop.is_available() is False

    def test_repr_contains_property_marker(self):
        # Verifies repr branch includes property label.
        assert "Property(" in repr(Property("P", 1, 100, 10))


class TestPropertyGroup:
    def test_add_property_sets_group(self):
        # Verifies add-property branch back-links property to group.
        group = PropertyGroup("G", "c")
        prop = Property("P", 1, 100, 10)
        group.add_property(prop)
        assert prop.group == group

    def test_add_property_avoids_duplicates(self):
        # Verifies duplicate add branch keeps unique property list.
        group = PropertyGroup("G", "c")
        prop = Property("P", 1, 100, 10)
        group.add_property(prop)
        group.add_property(prop)
        assert len(group.properties) == 1

    def test_all_owned_by_false_for_none_player(self):
        # Verifies ownership check branch for null player input.
        group = PropertyGroup("G", "c")
        assert group.all_owned_by(None) is False

    def test_all_owned_by_false_for_partial_ownership(self):
        # Verifies ownership branch rejects partial set ownership.
        group = PropertyGroup("G", "c")
        owner = Player("O")
        other = Player("X")
        p1 = Property("A", 1, 60, 2, group)
        p2 = Property("B", 3, 60, 4, group)
        p1.owner = owner
        p2.owner = other
        assert group.all_owned_by(owner) is False

    def test_get_owner_counts_counts_only_owned(self):
        # Verifies counting branch ignores unowned properties.
        group = PropertyGroup("G", "c")
        owner = Player("O")
        p1 = Property("A", 1, 60, 2, group)
        p1.owner = owner
        Property("B", 3, 60, 4, group)
        assert group.get_owner_counts()[owner] == 1

    def test_size_returns_group_length(self):
        # Verifies size branch returns total properties in group.
        group = PropertyGroup("G", "c")
        Property("A", 1, 60, 2, group)
        assert group.size() == 1

    def test_repr_contains_group_marker(self):
        # Verifies repr branch includes group class marker.
        assert "PropertyGroup(" in repr(PropertyGroup("G", "c"))
