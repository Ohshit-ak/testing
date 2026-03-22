from moneypoly.board import Board
from moneypoly.player import Player


class TestBoard:
    def test_get_property_at_returns_property(self, board):
        # Verifies lookup branch returns property at known position.
        assert board.get_property_at(1).name == "Mediterranean Avenue"

    def test_get_property_at_returns_none_for_missing(self, board):
        # Verifies lookup fall-through branch for non-property tiles.
        assert board.get_property_at(12) is None

    def test_get_tile_type_returns_special_tile(self, board):
        # Verifies special-tile branch in tile-type resolution.
        assert board.get_tile_type(0) == "go"

    def test_get_tile_type_returns_property_tile(self, board):
        # Verifies property tile branch when position has property.
        assert board.get_tile_type(1) == "property"

    def test_get_tile_type_returns_blank(self, board):
        # Verifies blank branch when no special or property tile exists.
        assert board.get_tile_type(12) == "blank"

    def test_is_purchasable_false_for_none(self, board):
        # Verifies purchasable branch when no property exists.
        assert board.is_purchasable(12) is False

    def test_is_purchasable_false_for_mortgaged(self, board):
        # Verifies purchasable branch for mortgaged properties.
        prop = board.get_property_at(1)
        prop.is_mortgaged = True
        assert board.is_purchasable(1) is False

    def test_is_purchasable_false_for_owned(self, board):
        # Verifies purchasable branch for already-owned property.
        prop = board.get_property_at(1)
        prop.owner = Player("O")
        assert board.is_purchasable(1) is False

    def test_is_purchasable_true_for_unowned(self, board):
        # Verifies purchasable success branch for free property.
        assert board.is_purchasable(1) is True

    def test_is_special_tile_true(self, board):
        # Verifies special-tile predicate true path.
        assert board.is_special_tile(7) is True

    def test_is_special_tile_false(self, board):
        # Verifies special-tile predicate false path.
        assert board.is_special_tile(1) is False

    def test_properties_owned_by_filters_owner(self, board):
        # Verifies ownership filter branch returns only matching owner properties.
        owner = Player("O")
        board.get_property_at(1).owner = owner
        assert len(board.properties_owned_by(owner)) == 1

    def test_unowned_properties_excludes_owned(self, board):
        # Verifies unowned filter branch excludes owned properties.
        board.get_property_at(1).owner = Player("O")
        assert len(board.unowned_properties()) == len(board.properties) - 1

    def test_repr_contains_board_marker(self, board):
        # Verifies repr branch includes board class marker.
        assert "Board(" in repr(board)
