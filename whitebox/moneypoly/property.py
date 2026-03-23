"""Defines property and property-group models used on the MoneyPoly board."""

from dataclasses import dataclass


@dataclass
class _PropertyFinance:
    """Immutable financial terms for a property."""

    price: int
    base_rent: int
    mortgage_value: int


@dataclass
class _PropertyState:
    """Mutable status for mortgage and building progress."""

    is_mortgaged: bool = False
    houses: int = 0


class Property:
    """Represents a single purchasable property tile on the MoneyPoly board."""

    FULL_GROUP_MULTIPLIER = 2

    def __init__(self, name, position, *args):
        """
        Build a property from positional board data.

        Accepted forms:
        - Property(name, position, price, base_rent)
        - Property(name, position, price, base_rent, group)
        """
        price, base_rent, group = self._parse_constructor_args(args)
        self.name = name
        self.position = position
        self._finance = _PropertyFinance(
            price=price,
            base_rent=base_rent,
            mortgage_value=price // 2,
        )
        self.owner = None
        self._state = _PropertyState()

        # Register with the group immediately on creation
        self.group = group
        if group is not None and self not in group.properties:
            group.properties.append(self)

    @staticmethod
    def _parse_constructor_args(args):
        """Parse legacy positional constructor arguments safely."""
        if len(args) == 2:
            price, base_rent = args
            return price, base_rent, None
        if len(args) == 3:
            price, base_rent, group = args
            return price, base_rent, group
        raise TypeError("Property expects price, base_rent, optional group")

    @property
    def price(self):
        """Purchase price."""
        return self._finance.price

    @property
    def base_rent(self):
        """Base rent before any multiplier."""
        return self._finance.base_rent

    @property
    def mortgage_value(self):
        """Mortgage payout for this property."""
        return self._finance.mortgage_value

    @property
    def is_mortgaged(self):
        """Whether the property is currently mortgaged."""
        return self._state.is_mortgaged

    @is_mortgaged.setter
    def is_mortgaged(self, value):
        self._state.is_mortgaged = bool(value)

    @property
    def houses(self):
        """Number of houses built on this property."""
        return self._state.houses

    @houses.setter
    def houses(self, value):
        self._state.houses = value

    def get_rent(self):
        """
        Return the rent owed for landing on this property.
        Rent is doubled if the owner holds the entire colour group.
        Returns 0 if the property is mortgaged.
        """
        if self.is_mortgaged:
            return 0
        if self.group is not None and self.group.all_owned_by(self.owner):
            return self.base_rent * self.FULL_GROUP_MULTIPLIER
        return self.base_rent

    def mortgage(self):
        """
        Mortgage this property and return the payout to the owner.
        Returns 0 if already mortgaged.
        """
        if self.is_mortgaged:
            return 0
        self.is_mortgaged = True
        return self.mortgage_value

    def unmortgage(self):
        """
        Lift the mortgage on this property.
        Returns the cost (110 % of mortgage value), or 0 if not mortgaged.
        """
        if not self.is_mortgaged:
            return 0
        cost = int(self.mortgage_value * 1.1)
        self.is_mortgaged = False
        return cost

    def is_available(self):
        """Return True if this property can be purchased (unowned, not mortgaged)."""
        return self.owner is None and not self.is_mortgaged

    def __repr__(self):
        owner_name = self.owner.name if self.owner else "unowned"
        return f"Property({self.name!r}, pos={self.position}, owner={owner_name!r})"


class PropertyGroup:
    """Represents a group of properties that share a colour and have special rules."""

    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.properties = []

    def add_property(self, prop):
        """Add a Property to this group and back-link it."""
        if prop not in self.properties:
            self.properties.append(prop)
            prop.group = self

    def all_owned_by(self, player):
        """Return True if every property in this group is owned by `player`."""
        if player is None:
            return False
        return bool(self.properties) and all(p.owner == player for p in self.properties)

    def get_owner_counts(self):
        """Return a dict mapping each owner to how many properties they hold in this group."""
        counts = {}
        for prop in self.properties:
            if prop.owner is not None:
                counts[prop.owner] = counts.get(prop.owner, 0) + 1
        return counts

    def size(self):
        """Return the number of properties in this group."""
        return len(self.properties)

    def __repr__(self):
        return f"PropertyGroup({self.name!r}, {len(self.properties)} properties)"
