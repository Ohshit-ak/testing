from moneypoly import ui
from moneypoly.player import Player
from moneypoly.property import Property


class TestUI:
    def test_print_banner_outputs_title(self, capsys):
        # Verifies banner branch prints section heading.
        ui.print_banner("Hello")
        assert "Hello" in capsys.readouterr().out

    def test_print_player_card_with_no_properties(self, capsys):
        # Verifies player-card branch for empty property list.
        ui.print_player_card(Player("A"))
        assert "Properties: none" in capsys.readouterr().out

    def test_print_player_card_with_properties(self, capsys):
        # Verifies player-card branch for listed properties.
        p = Player("A")
        p.add_property(Property("P", 1, 100, 10))
        ui.print_player_card(p)
        assert "Properties:" in capsys.readouterr().out

    def test_print_player_card_with_jail_and_card(self, capsys):
        # Verifies jail/card branch lines in player-card output.
        p = Player("A")
        p.in_jail = True
        p.get_out_of_jail_cards = 1
        ui.print_player_card(p)
        assert "Jail cards:" in capsys.readouterr().out

    def test_print_standings_outputs_header(self, capsys):
        # Verifies standings branch emits leaderboard header.
        ui.print_standings([Player("A")])
        assert "[ Standings ]" in capsys.readouterr().out

    def test_print_board_ownership_outputs_table(self, capsys):
        # Verifies board ownership branch prints table label.
        from moneypoly.board import Board

        ui.print_board_ownership(Board())
        assert "Property Register" in capsys.readouterr().out

    def test_format_currency_formats_commas(self):
        # Verifies currency formatting branch with separators.
        assert ui.format_currency(1500) == "$1,500"

    def test_safe_int_input_returns_int(self, monkeypatch):
        # Verifies numeric-input branch returns parsed integer.
        monkeypatch.setattr("builtins.input", lambda _p: "7")
        assert ui.safe_int_input("> ") == 7

    def test_safe_int_input_returns_default_on_value_error(self, monkeypatch):
        # Verifies error-handling branch returns default value.
        monkeypatch.setattr("builtins.input", lambda _p: "x")
        assert ui.safe_int_input("> ", default=9) == 9

    def test_confirm_true_for_y(self, monkeypatch):
        # Verifies confirm branch for yes input.
        monkeypatch.setattr("builtins.input", lambda _p: "y")
        assert ui.confirm("?") is True

    def test_confirm_false_for_other(self, monkeypatch):
        # Verifies confirm branch for non-yes input.
        monkeypatch.setattr("builtins.input", lambda _p: "n")
        assert ui.confirm("?") is False
