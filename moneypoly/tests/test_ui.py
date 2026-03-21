"""
Tests for ui.py — covers all ui module leaf nodes from the call graph:
  ui.print_banner, ui.print_standings, ui.print_board_ownership,
  ui.print_player_card, ui.safe_int_input, ui.confirm, ui.format_currency
"""

import pytest
from unittest.mock import patch
from moneypoly import ui
from moneypoly.player import Player
from moneypoly.board import Board


# ─── print_banner ─────────────────────────────────────────────────────────────

class TestPrintBanner:
    def test_prints_title(self, capsys):
        ui.print_banner("Hello World")
        captured = capsys.readouterr()
        assert "Hello World" in captured.out

    def test_prints_separator_lines(self, capsys):
        ui.print_banner("Test")
        captured = capsys.readouterr()
        assert "=" in captured.out


# ─── print_standings ──────────────────────────────────────────────────────────

class TestPrintStandings:
    def test_prints_player_name(self, capsys, player):
        ui.print_standings([player])
        captured = capsys.readouterr()
        assert "Alice" in captured.out

    def test_prints_jailed_tag(self, capsys, player):
        player.go_to_jail()
        ui.print_standings([player])
        captured = capsys.readouterr()
        assert "JAILED" in captured.out

    def test_prints_multiple_players(self, capsys, player, player2):
        ui.print_standings([player, player2])
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "Bob" in captured.out

    def test_prints_standings_header(self, capsys, player):
        ui.print_standings([player])
        captured = capsys.readouterr()
        assert "Standings" in captured.out


# ─── print_board_ownership ────────────────────────────────────────────────────

class TestPrintBoardOwnership:
    def test_prints_property_name(self, capsys, board):
        ui.print_board_ownership(board)
        captured = capsys.readouterr()
        assert "Mediterranean" in captured.out

    def test_prints_owner_name_when_owned(self, capsys, board):
        prop = board.get_property_at(1)
        player = Player("Alice")
        prop.owner = player
        ui.print_board_ownership(board)
        captured = capsys.readouterr()
        assert "Alice" in captured.out

    def test_prints_mortgaged_marker(self, capsys, board):
        prop = board.get_property_at(1)
        prop.is_mortgaged = True
        ui.print_board_ownership(board)
        captured = capsys.readouterr()
        assert "*" in captured.out


# ─── print_player_card (dead code per call graph, but still executable) ───────

class TestPrintPlayerCard:
    def test_prints_player_name(self, capsys, player):
        ui.print_player_card(player)
        captured = capsys.readouterr()
        assert "Alice" in captured.out

    def test_prints_jailed_status(self, capsys, player):
        player.go_to_jail()
        ui.print_player_card(player)
        captured = capsys.readouterr()
        assert "JAIL" in captured.out

    def test_prints_jail_free_cards(self, capsys, player):
        player.get_out_of_jail_cards = 1
        ui.print_player_card(player)
        captured = capsys.readouterr()
        assert "Jail" in captured.out or "jail" in captured.out

    def test_prints_no_properties(self, capsys, player):
        ui.print_player_card(player)
        captured = capsys.readouterr()
        assert "none" in captured.out

    def test_prints_properties_if_owned(self, capsys, player, prop, board):
        prop.owner = player
        player.add_property(prop)
        ui.print_player_card(player)
        captured = capsys.readouterr()
        assert "Test Street" in captured.out


# ─── safe_int_input ───────────────────────────────────────────────────────────

class TestSafeIntInput:
    def test_valid_integer(self):
        with patch("builtins.input", return_value="42"):
            result = ui.safe_int_input("Enter: ", default=0)
        assert result == 42

    def test_invalid_input_returns_default(self):
        with patch("builtins.input", return_value="abc"):
            result = ui.safe_int_input("Enter: ", default=99)
        assert result == 99

    def test_empty_input_returns_default(self):
        with patch("builtins.input", return_value=""):
            result = ui.safe_int_input("Enter: ", default=5)
        assert result == 5


# ─── confirm ──────────────────────────────────────────────────────────────────

class TestConfirm:
    def test_confirm_yes_lowercase(self):
        with patch("builtins.input", return_value="y"):
            assert ui.confirm("?") is True

    def test_confirm_no(self):
        with patch("builtins.input", return_value="n"):
            assert ui.confirm("?") is False

    def test_confirm_uppercase_y_is_true(self):
        with patch("builtins.input", return_value="Y"):
            # "Y".strip().lower() == "y" → True
            assert ui.confirm("?") is True

    def test_confirm_empty(self):
        with patch("builtins.input", return_value=""):
            assert ui.confirm("?") is False


# ─── format_currency ──────────────────────────────────────────────────────────

class TestFormatCurrency:
    def test_formats_with_dollar_sign(self):
        result = ui.format_currency(1500)
        assert result == "$1,500"

    def test_formats_zero(self):
        result = ui.format_currency(0)
        assert result == "$0"

    def test_formats_large_number(self):
        result = ui.format_currency(20000)
        assert "$20,000" in result
