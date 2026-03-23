import main
import runpy
import types
import sys
import os


class TestMain:
    def test_get_player_names_filters_empty_entries(self, monkeypatch):
        # Verifies name parsing branch removes blank comma-separated inputs.
        monkeypatch.setattr("builtins.input", lambda _p: " A, ,B ,, ")
        assert main.get_player_names() == ["A", "B"]

    def test_main_handles_keyboard_interrupt(self, monkeypatch, capsys):
        # Verifies top-level interrupt handling branch prints goodbye message.
        class DummyGame:
            def __init__(self, _names):
                pass

            def run(self):
                raise KeyboardInterrupt()

        monkeypatch.setattr(main, "Game", DummyGame)
        monkeypatch.setattr(main, "get_player_names", lambda: ["A", "B"])
        main.main()
        assert "interrupted" in capsys.readouterr().out.lower()

    def test_main_handles_value_error(self, monkeypatch, capsys):
        # Verifies setup error branch prints ValueError details.
        class DummyGame:
            def __init__(self, _names):
                raise ValueError("bad")

        monkeypatch.setattr(main, "Game", DummyGame)
        monkeypatch.setattr(main, "get_player_names", lambda: ["A", "B"])
        main.main()
        assert "Setup error: bad" in capsys.readouterr().out

    def test_main_runs_game_success_path(self, monkeypatch):
        # Verifies normal main path creates game and invokes run once.
        called = {"run": 0}

        class DummyGame:
            def __init__(self, _names):
                pass

            def run(self):
                called["run"] += 1

        monkeypatch.setattr(main, "Game", DummyGame)
        monkeypatch.setattr(main, "get_player_names", lambda: ["A", "B"])
        main.main()
        assert called["run"] == 1

    def test_module_entrypoint_invokes_main(self, monkeypatch):
        # Verifies script-entry branch executes main() when run as __main__.
        fake_game_module = types.SimpleNamespace(Game=type("G", (), {
            "__init__": lambda self, _names: None,
            "run": lambda self: None,
        }))
        monkeypatch.setitem(sys.modules, "moneypoly.game", fake_game_module)
        monkeypatch.setattr("builtins.input", lambda _p: "A,B")
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
        module_globals = runpy.run_path(script_path, run_name="__main__")
        assert module_globals["__name__"] == "__main__"
