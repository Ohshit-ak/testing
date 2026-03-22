import pytest

from moneypoly.config import JAIL_FINE
from moneypoly.game import Game


@pytest.fixture
def game():
    # Provides a two-player game fixture for deterministic branch testing.
    return Game(["A", "B"])


def test_buy_property_allows_exact_balance(game):
    # Tests affordability boundary branch where balance equals property price.
    buyer = game.players[0]
    prop = game.board.get_property_at(1)
    buyer.balance = prop.price

    assert game.buy_property(buyer, prop) is True
    assert buyer.balance == 0
    assert prop.owner == buyer


def test_buy_property_rejects_insufficient_balance(game):
    # Tests insufficient-funds branch to keep ownership unchanged.
    buyer = game.players[0]
    prop = game.board.get_property_at(1)
    buyer.balance = prop.price - 1

    assert game.buy_property(buyer, prop) is False
    assert prop.owner is None


def test_pay_rent_transfers_funds_to_owner(game):
    # Tests rent-payment path to ensure payer loses and owner gains the same amount.
    tenant = game.players[0]
    owner = game.players[1]
    prop = game.board.get_property_at(1)
    prop.owner = owner
    owner.add_property(prop)

    tenant.balance = 100
    owner.balance = 100
    rent = prop.get_rent()

    game.pay_rent(tenant, prop)

    assert tenant.balance == 100 - rent
    assert owner.balance == 100 + rent


def test_pay_rent_noop_when_mortgaged(game):
    # Tests mortgaged-property branch where rent should not be collected.
    tenant = game.players[0]
    owner = game.players[1]
    prop = game.board.get_property_at(1)
    prop.owner = owner
    owner.add_property(prop)
    prop.is_mortgaged = True

    tenant_before = tenant.balance
    owner_before = owner.balance

    game.pay_rent(tenant, prop)

    assert tenant.balance == tenant_before
    assert owner.balance == owner_before


def test_mortgage_and_unmortgage_state_paths(game):
    # Tests ownership, mortgage, and redemption decision branches.
    player = game.players[0]
    prop = game.board.get_property_at(1)
    prop.owner = player
    player.add_property(prop)

    assert game.mortgage_property(player, prop) is True
    assert game.mortgage_property(player, prop) is False
    assert game.unmortgage_property(player, prop) is True


def test_trade_rejects_when_buyer_cannot_pay(game):
    # Tests trade validation branch for unaffordable offers.
    seller = game.players[0]
    buyer = game.players[1]
    prop = game.board.get_property_at(1)
    prop.owner = seller
    seller.add_property(prop)
    buyer.balance = 0

    assert game.trade(seller, buyer, prop, 10) is False
    assert prop.owner == seller


def test_jail_turn_voluntary_fine_deducts_player_and_releases(game, monkeypatch):
    # Tests jail branch where paying fine should reduce balance and release player.
    player = game.players[0]
    player.in_jail = True
    player.jail_turns = 1
    player.balance = 500

    answers = iter([True])
    monkeypatch.setattr("moneypoly.game.ui.confirm", lambda _prompt: next(answers))
    monkeypatch.setattr(game.dice, "roll", lambda: 2)
    monkeypatch.setattr(game, "_move_and_resolve", lambda *_args, **_kwargs: None)

    game._handle_jail_turn(player)

    assert player.in_jail is False
    assert player.jail_turns == 0
    assert player.balance == 500 - JAIL_FINE


def test_jail_turn_mandatory_release_after_three_turns(game, monkeypatch):
    # Tests forced-release branch after max jail turns without voluntary action.
    player = game.players[0]
    player.in_jail = True
    player.jail_turns = 2
    player.balance = 500

    monkeypatch.setattr("moneypoly.game.ui.confirm", lambda _prompt: False)
    monkeypatch.setattr(game.dice, "roll", lambda: 4)
    monkeypatch.setattr(game, "_move_and_resolve", lambda *_args, **_kwargs: None)

    game._handle_jail_turn(player)

    assert player.in_jail is False
    assert player.jail_turns == 0
    assert player.balance == 500 - JAIL_FINE


def test_find_winner_returns_highest_net_worth(game):
    # Tests winner-selection branch to ensure richest player is selected.
    game.players[0].balance = 50
    game.players[1].balance = 500

    winner = game.find_winner()
    assert winner == game.players[1]


def test_check_bankruptcy_removes_player_and_resets_properties(game):
    # Tests bankruptcy branch that eliminates player and releases owned assets.
    doomed = game.players[0]
    prop = game.board.get_property_at(1)
    prop.owner = doomed
    prop.is_mortgaged = True
    doomed.add_property(prop)
    doomed.balance = 0

    game._check_bankruptcy(doomed)

    assert doomed not in game.players
    assert prop.owner is None
    assert prop.is_mortgaged is False


def test_apply_card_move_to_past_go_collects_salary(game):
    # Tests move-to card branch where crossing Go should credit salary.
    player = game.players[0]
    player.position = 39
    start = player.balance

    card = {"description": "Advance to Go", "action": "move_to", "value": 0}
    game._apply_card(player, card)

    assert player.position == 0
    assert player.balance == start + 200


def test_apply_card_birthday_only_collects_from_solvent_players(game):
    # Tests loop/conditional branch that skips players unable to pay birthday fee.
    player = game.players[0]
    other = game.players[1]
    other.balance = 5

    card = {"description": "Birthday", "action": "birthday", "value": 10}
    before = player.balance
    game._apply_card(player, card)

    assert player.balance == before
    assert other.balance == 5
