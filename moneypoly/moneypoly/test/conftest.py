import os
import sys

import pytest

# Make imports stable whether pytest is launched from project root or test/.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
