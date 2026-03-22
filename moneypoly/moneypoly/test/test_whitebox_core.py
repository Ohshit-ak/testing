import pytest

from moneypoly.bank import Bank
from moneypoly.board import Board
from moneypoly.cards import CardDeck
from moneypoly.config import GO_SALARY
from moneypoly.dice import Dice
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup


def test_bank_pay_out_rejects_overdraw():
    # Tests overdraw branch to ensure bank cannot pay more than reserves.
    bank = Bank()
    with pytest.raises(ValueError):
        bank.pay_out(bank.get_balance() + 1)


def test_bank_pay_out_non_positive_returns_zero():
    # Tests zero/negative payout boundary branch for safe no-op behavior.
    bank = Bank()
    assert bank.pay_out(0) == 0
    assert bank.pay_out(-50) == 0


def test_board_tile_type_and_special_checks():
    # Tests decision paths for special tile, property tile, and blank tile detection.
    board = Board()
    assert board.get_tile_type(0) == "go"
    assert board.get_tile_type(1) == "property"
    assert board.get_tile_type(12) == "blank"
    assert board.is_special_tile(7) is True
    assert board.is_special_tile(1) is False


def test_carddeck_empty_paths():
    # Tests empty deck edge cases for draw/peek branches.
    deck = CardDeck([])
    assert deck.draw() is None
    assert deck.peek() is None


def test_carddeck_cycles_after_exhaustion():
    # Tests wraparound branch when deck index exceeds card count.
    cards = [{"id": 1}, {"id": 2}]
    deck = CardDeck(cards)
    assert deck.draw()["id"] == 1
    assert deck.draw()["id"] == 2
    assert deck.draw()["id"] == 1


def test_dice_roll_requests_six_sided_range(monkeypatch):
    # Tests dice roll bounds branch and verifies proper 1..6 random call contract.
    calls = []

    def fake_randint(a, b):
        calls.append((a, b))
        return 1

    monkeypatch.setattr("moneypoly.dice.random.randint", fake_randint)
    d = Dice()
    d.roll()

    assert calls, "random.randint should be called during roll"
    assert all(a == 1 and b == 6 for a, b in calls)


def test_player_move_passing_go_collects_salary():
    # Tests pass-Go branch where salary must be awarded on wrap-around movement.
    p = Player("A")
    p.position = 39
    starting_balance = p.balance

    assert p.move(2) == 1
    assert p.balance == starting_balance + GO_SALARY


def test_player_add_money_rejects_negative():
    # Tests negative-input guard branch for balance increment validation.
    p = Player("A")
    with pytest.raises(ValueError):
        p.add_money(-1)


def test_property_group_requires_full_set_for_bonus_rent():
    # Tests ownership-completeness branch to prevent bonus rent from partial ownership.
    group = PropertyGroup("Brown", "brown")
    p1 = Player("Owner")
    p2 = Player("Other")

    prop_a = Property("A", 1, 60, 2, group)
    prop_b = Property("B", 3, 60, 4, group)
    prop_a.owner = p1
    prop_b.owner = p2

    assert group.all_owned_by(p1) is False


def test_property_mortgage_and_unmortgage_branches():
    # Tests mortgage state transitions and duplicate operation branches.
    prop = Property("A", 1, 100, 10)
    assert prop.mortgage() == 50
    assert prop.mortgage() == 0
    assert prop.unmortgage() == 55
    assert prop.unmortgage() == 0
