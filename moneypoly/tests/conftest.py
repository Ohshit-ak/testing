"""
Shared pytest fixtures for MoneyPoly tests.
Adds the project root to sys.path so that the package can be imported
regardless of the directory from which pytest is invoked.
"""
import sys
import os

# Allow imports like:  from moneypoly.moneypoly.moneypoly.xxx import Xxx
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "moneypoly"))

import pytest
from moneypoly.player import Player
from moneypoly.bank import Bank
from moneypoly.board import Board
from moneypoly.property import Property, PropertyGroup
from moneypoly.cards import CardDeck, CHANCE_CARDS, COMMUNITY_CHEST_CARDS
from moneypoly.dice import Dice
from moneypoly.game import Game


@pytest.fixture
def player():
    return Player("Alice")


@pytest.fixture
def player2():
    return Player("Bob")


@pytest.fixture
def bank():
    return Bank()


@pytest.fixture
def board():
    return Board()


@pytest.fixture
def dice():
    return Dice()


@pytest.fixture
def group():
    return PropertyGroup("Test", "test_color")


@pytest.fixture
def prop(group):
    return Property("Test Street", 1, 100, 10, group)


@pytest.fixture
def chance_deck():
    return CardDeck(list(CHANCE_CARDS))


@pytest.fixture
def community_deck():
    return CardDeck(list(COMMUNITY_CHEST_CARDS))


@pytest.fixture
def game():
    return Game(["Alice", "Bob"])
