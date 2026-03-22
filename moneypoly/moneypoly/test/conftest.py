import pytest

from moneypoly.bank import Bank
from moneypoly.board import Board
from moneypoly.game import Game
from moneypoly.player import Player


@pytest.fixture
def player_a():
    return Player("A")


@pytest.fixture
def player_b():
    return Player("B")


@pytest.fixture
def bank():
    return Bank()


@pytest.fixture
def board():
    return Board()


@pytest.fixture
def game_two_players():
    return Game(["A", "B"])
