"""
Simple, flat test script for 100% coverage.
"""
import pytest
from unittest.mock import patch, MagicMock
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.config import INCOME_TAX_AMOUNT, LUXURY_TAX_AMOUNT, GO_SALARY, STARTING_BALANCE

@pytest.fixture
def g():
    return Game(["Alice", "Bob", "Charlie"])

def test_init(g):
    assert len(g.players) == 3

def test_turn_mgmt(g):
    g.advance_turn()
    assert g.current_index == 1
    g.players[2].is_eliminated = True
    g.players.remove(g.players[2])
    g.advance_turn()
    assert g.current_index == 0

def test_logic_bugs(g):
    g.players[0].balance = 5000
    g.players[1].balance = 50
    assert g.find_winner() == g.players[1] # BUG

def test_resolution_tiles(g):
    p = g.players[0]
    # luxury
    p.position = 37
    g._move_and_resolve(p, 1)
    assert p.balance == STARTING_BALANCE - LUXURY_TAX_AMOUNT
    # chance
    p.position = 6
    with patch.object(g.chance_deck, "draw", return_value={"action":"pay","value":0,"description":"X"}):
        g._move_and_resolve(p, 1)
    # free parking
    p.position = 19
    g._move_and_resolve(p, 1)

def test_property_ops_unaff(g):
    p = g.players[0]
    prop = g.board.get_property_at(1)
    p.balance = 10
    assert not g.buy_property(p, prop)
    prop.owner = p
    assert g.mortgage_property(p, prop)
    assert not g.mortgage_property(p, prop) # already mortgaged
    p.balance = 5
    assert not g.unmortgage_property(p, prop)

def test_trade_unaff(g):
    p1 = g.players[0]
    p2 = g.players[1]
    prop = g.board.get_property_at(1)
    prop.owner = p1
    p1.add_property(prop)
    p2.balance = 5
    assert not g.trade(p1, p2, prop, 100)

def test_apply_card_edge(g):
    p = g.players[0]
    # birthday alone
    g.players = [p]
    init = p.balance
    g._apply_card(p, {"action":"birthday","value":10,"description":"X"})
    assert p.balance == init

def test_bankruptcy_wrap(g):
    g.current_index = 2
    g.players[2].balance = -1
    g.players[2].is_bankrupt = lambda: True
    g._check_bankruptcy(g.players[2])
    assert g.current_index == 0

def test_run_quit(g, capsys):
    g.players = [g.players[0]]
    with patch("builtins.input", return_value="s"):
        g.run()
    assert "GAME OVER" in capsys.readouterr().out

def test_menu_full(g, capsys):
    p = g.players[0]
    prop = g.board.get_property_at(1)
    prop.owner = p
    p.add_property(prop)
    with patch("builtins.input", side_effect=["1", "2", "3", "1", "4", "1", "5", "1", "1", "50", "6", "100", "0"]):
        g.interactive_menu(p)
    assert "Alice" in capsys.readouterr().out
