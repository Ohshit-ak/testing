"""
Tests for main.py — covers the entry-point nodes:
  get_player_names(), main()
"""

import pytest
from unittest.mock import patch, MagicMock
import moneypoly.main as main_module


# ─── get_player_names ─────────────────────────────────────────────────────────

class TestGetPlayerNames:
    def test_splits_by_comma(self):
        with patch("builtins.input", return_value="Alice, Bob"):
            names = main_module.get_player_names()
        assert names == ["Alice", "Bob"]

    def test_trims_whitespace(self):
        with patch("builtins.input", return_value="  Alice , Bob  "):
            names = main_module.get_player_names()
        assert "Alice" in names and "Bob" in names

    def test_filters_empty_entries(self):
        with patch("builtins.input", return_value="Alice,,Bob"):
            names = main_module.get_player_names()
        assert "" not in names
        assert len(names) == 2

    def test_single_name(self):
        with patch("builtins.input", return_value="Solo"):
            names = main_module.get_player_names()
        assert names == ["Solo"]


# ─── main() ───────────────────────────────────────────────────────────────────

class TestMain:
    def test_main_creates_and_runs_game(self):
        """main() should create a Game and call run()."""
        with patch("builtins.input", return_value="Alice, Bob"):
            with patch("moneypoly.main.Game") as MockGame:
                mock_game_instance = MagicMock()
                MockGame.return_value = mock_game_instance
                main_module.main()
                MockGame.assert_called_once_with(["Alice", "Bob"])
                mock_game_instance.run.assert_called_once()

    def test_main_handles_keyboard_interrupt(self, capsys):
        """main() should print a goodbye message on KeyboardInterrupt."""
        with patch("builtins.input", return_value="Alice, Bob"):
            with patch("moneypoly.main.Game") as MockGame:
                MockGame.return_value.run.side_effect = KeyboardInterrupt
                main_module.main()
                captured = capsys.readouterr()
                assert "interrupted" in captured.out.lower() or "goodbye" in captured.out.lower()

    def test_main_handles_value_error(self, capsys):
        """main() should print an error message on ValueError from Game setup."""
        with patch("builtins.input", return_value=""):
            with patch("moneypoly.main.Game") as MockGame:
                MockGame.side_effect = ValueError("not enough players")
                main_module.main()
                captured = capsys.readouterr()
                assert "error" in captured.out.lower() or "setup" in captured.out.lower()


# ─── Script Entry Point ───────────────────────────────────────────────────────

def test_script_entry_point():
    """Cover the 'if __name__ == "__main__": main()' block."""
    import runpy
    with patch("builtins.input", return_value="Alice, Bob"):
        # Patch the source of the Game class to ensure it's caught regardless of import method
        with patch("moneypoly.game.Game") as MockGame:
            # Trigger the __name__ == "__main__" block
            runpy.run_module("moneypoly.main", run_name="__main__")
            MockGame.assert_called()


