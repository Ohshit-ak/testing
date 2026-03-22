from moneypoly.config import JAIL_FINE
from moneypoly.game import Game
from moneypoly.player import Player


class TestGameCore:
    def test_current_player_returns_indexed_player(self, game_two_players):
        # Verifies current-player branch returns player at active index.
        assert game_two_players.current_player().name == "A"

    def test_advance_turn_updates_index(self, game_two_players):
        # Verifies advance-turn branch increments circular player index.
        game_two_players.advance_turn()
        assert game_two_players.current_index == 1

    def test_advance_turn_updates_turn_number(self, game_two_players):
        # Verifies advance-turn branch increments turn counter.
        game_two_players.advance_turn()
        assert game_two_players.turn_number == 1

    def test_play_turn_jailed_path_advances_turn(self, game_two_players, monkeypatch):
        # Verifies jailed-player branch processes jail flow then advances turn.
        p = game_two_players.players[0]
        p.in_jail = True
        monkeypatch.setattr(game_two_players, "_handle_jail_turn", lambda _p: None)
        game_two_players.play_turn()
        assert game_two_players.current_index == 1

    def test_play_turn_three_doubles_sends_to_jail(self, game_two_players, monkeypatch):
        # Verifies three-doubles branch sends player to jail.
        monkeypatch.setattr(game_two_players.dice, "roll", lambda: 4)
        monkeypatch.setattr(game_two_players.dice, "describe", lambda: "desc")
        game_two_players.dice.doubles_streak = 3
        game_two_players.play_turn()
        assert game_two_players.players[0].in_jail is True

    def test_play_turn_doubles_keeps_same_player(self, game_two_players, monkeypatch):
        # Verifies doubles branch grants extra turn without advancing index.
        monkeypatch.setattr(game_two_players.dice, "roll", lambda: 4)
        monkeypatch.setattr(game_two_players.dice, "describe", lambda: "desc")
        game_two_players.dice.doubles_streak = 0
        monkeypatch.setattr(game_two_players.dice, "is_doubles", lambda: True)
        monkeypatch.setattr(game_two_players, "_move_and_resolve", lambda *_: None)
        game_two_players.play_turn()
        assert game_two_players.current_index == 0

    def test_play_turn_non_doubles_advances(self, game_two_players, monkeypatch):
        # Verifies normal non-doubles branch advances to next player.
        monkeypatch.setattr(game_two_players.dice, "roll", lambda: 4)
        monkeypatch.setattr(game_two_players.dice, "describe", lambda: "desc")
        game_two_players.dice.doubles_streak = 0
        monkeypatch.setattr(game_two_players.dice, "is_doubles", lambda: False)
        monkeypatch.setattr(game_two_players, "_move_and_resolve", lambda *_: None)
        game_two_players.play_turn()
        assert game_two_players.current_index == 1


class TestGameMoveResolve:
    def test_move_resolve_blank_tile_still_checks_bankruptcy(self, game_two_players, monkeypatch):
        # Verifies fall-through tile branch still executes bankruptcy check.
        p = game_two_players.players[0]
        monkeypatch.setattr(p, "move", lambda _s: None)
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "blank")
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_check_bankruptcy", lambda _pl: called.__setitem__("value", True))
        game_two_players._move_and_resolve(p, 1)
        assert called["value"] is True

    def test_move_resolve_go_to_jail_tile(self, game_two_players, monkeypatch):
        # Verifies go-to-jail tile branch flags player as jailed.
        p = game_two_players.players[0]
        monkeypatch.setattr(p, "move", lambda _s: None)
        p.position = 30
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "go_to_jail")
        game_two_players._move_and_resolve(p, 1)
        assert p.in_jail is True

    def test_move_resolve_income_tax_collects_bank(self, game_two_players, monkeypatch):
        # Verifies income-tax branch collects money into bank.
        p = game_two_players.players[0]
        monkeypatch.setattr(p, "move", lambda _s: None)
        p.position = 4
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "income_tax")
        before = game_two_players.bank.get_balance()
        game_two_players._move_and_resolve(p, 1)
        assert game_two_players.bank.get_balance() == before + 200

    def test_move_resolve_luxury_tax_collects_bank(self, game_two_players, monkeypatch):
        # Verifies luxury-tax branch collects money into bank.
        p = game_two_players.players[0]
        monkeypatch.setattr(p, "move", lambda _s: None)
        p.position = 38
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "luxury_tax")
        before = game_two_players.bank.get_balance()
        game_two_players._move_and_resolve(p, 1)
        assert game_two_players.bank.get_balance() == before + 75

    def test_move_resolve_free_parking_no_balance_change(self, game_two_players, monkeypatch):
        # Verifies free-parking branch performs no monetary side effects.
        p = game_two_players.players[0]
        before = p.balance
        monkeypatch.setattr(p, "move", lambda _s: None)
        p.position = 20
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "free_parking")
        game_two_players._move_and_resolve(p, 1)
        assert p.balance == before

    def test_move_resolve_chance_draws_card(self, game_two_players, monkeypatch):
        # Verifies chance tile branch passes drawn card to card handler.
        p = game_two_players.players[0]
        monkeypatch.setattr(p, "move", lambda _s: None)
        p.position = 7
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "chance")
        monkeypatch.setattr(game_two_players.chance_deck, "draw", lambda: {"action": "collect", "value": 1, "description": "d"})
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_apply_card", lambda *_: called.__setitem__("value", True))
        game_two_players._move_and_resolve(p, 1)
        assert called["value"] is True

    def test_move_resolve_community_draws_card(self, game_two_players, monkeypatch):
        # Verifies community-chest tile branch passes drawn card to card handler.
        p = game_two_players.players[0]
        monkeypatch.setattr(p, "move", lambda _s: None)
        p.position = 2
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "community_chest")
        monkeypatch.setattr(game_two_players.community_deck, "draw", lambda: {"action": "collect", "value": 1, "description": "d"})
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_apply_card", lambda *_: called.__setitem__("value", True))
        game_two_players._move_and_resolve(p, 1)
        assert called["value"] is True

    def test_move_resolve_railroad_with_property_calls_handler(self, game_two_players, monkeypatch):
        # Verifies railroad branch handles property interaction when present.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        monkeypatch.setattr(p, "move", lambda _s: None)
        p.position = 5
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "railroad")
        monkeypatch.setattr(game_two_players.board, "get_property_at", lambda _p: prop)
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_handle_property_tile", lambda *_: called.__setitem__("value", True))
        game_two_players._move_and_resolve(p, 1)
        assert called["value"] is True

    def test_move_resolve_railroad_without_property_skips_handler(self, game_two_players, monkeypatch):
        # Verifies railroad branch no-op when property lookup returns None.
        p = game_two_players.players[0]
        monkeypatch.setattr(p, "move", lambda _s: None)
        p.position = 5
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "railroad")
        monkeypatch.setattr(game_two_players.board, "get_property_at", lambda _p: None)
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_handle_property_tile", lambda *_: called.__setitem__("value", True))
        game_two_players._move_and_resolve(p, 1)
        assert called["value"] is False

    def test_move_resolve_property_with_property_calls_handler(self, game_two_players, monkeypatch):
        # Verifies property tile branch handles property interaction when present.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        monkeypatch.setattr(p, "move", lambda _s: None)
        p.position = 1
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "property")
        monkeypatch.setattr(game_two_players.board, "get_property_at", lambda _p: prop)
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_handle_property_tile", lambda *_: called.__setitem__("value", True))
        game_two_players._move_and_resolve(p, 1)
        assert called["value"] is True

    def test_move_resolve_property_without_property_skips_handler(self, game_two_players, monkeypatch):
        # Verifies property tile branch no-op when lookup misses.
        p = game_two_players.players[0]
        monkeypatch.setattr(p, "move", lambda _s: None)
        p.position = 1
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _p: "property")
        monkeypatch.setattr(game_two_players.board, "get_property_at", lambda _p: None)
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_handle_property_tile", lambda *_: called.__setitem__("value", True))
        game_two_players._move_and_resolve(p, 1)
        assert called["value"] is False


class TestGamePropertyOps:
    def test_handle_property_tile_buy_choice(self, game_two_players, monkeypatch):
        # Verifies unowned-property buy branch calls buy operation.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = None
        monkeypatch.setattr("builtins.input", lambda _p: "b")
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "buy_property", lambda *_: called.__setitem__("value", True))
        game_two_players._handle_property_tile(p, prop)
        assert called["value"] is True

    def test_handle_property_tile_auction_choice(self, game_two_players, monkeypatch):
        # Verifies unowned-property auction branch calls auction operation.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = None
        monkeypatch.setattr("builtins.input", lambda _p: "a")
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "auction_property", lambda *_: called.__setitem__("value", True))
        game_two_players._handle_property_tile(p, prop)
        assert called["value"] is True

    def test_handle_property_tile_skip_choice(self, game_two_players, monkeypatch, capsys):
        # Verifies unowned-property skip branch prints pass message.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = None
        monkeypatch.setattr("builtins.input", lambda _p: "s")
        game_two_players._handle_property_tile(p, prop)
        assert "passes on" in capsys.readouterr().out

    def test_handle_property_tile_owned_by_self(self, game_two_players, capsys):
        # Verifies owned-by-self branch prints no-rent message.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        game_two_players._handle_property_tile(p, prop)
        assert "No rent due" in capsys.readouterr().out

    def test_handle_property_tile_owned_by_other_calls_rent(self, game_two_players, monkeypatch):
        # Verifies owned-by-other branch invokes rent payment flow.
        p = game_two_players.players[0]
        o = game_two_players.players[1]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = o
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "pay_rent", lambda *_: called.__setitem__("value", True))
        game_two_players._handle_property_tile(p, prop)
        assert called["value"] is True

    def test_buy_property_returns_false_when_insufficient(self, game_two_players):
        # Verifies buy-property insufficient-funds branch returns failure.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        p.balance = prop.price - 1
        assert game_two_players.buy_property(p, prop) is False

    def test_buy_property_assigns_owner_on_success(self, game_two_players):
        # Verifies buy-property success branch assigns property owner.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        p.balance = prop.price
        game_two_players.buy_property(p, prop)
        assert prop.owner == p

    def test_pay_rent_returns_when_mortgaged(self, game_two_players):
        # Verifies rent branch exits early for mortgaged properties.
        p = game_two_players.players[0]
        o = game_two_players.players[1]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = o
        prop.is_mortgaged = True
        before = p.balance
        game_two_players.pay_rent(p, prop)
        assert p.balance == before

    def test_pay_rent_returns_when_no_owner(self, game_two_players):
        # Verifies rent branch exits early when property has no owner.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = None
        before = p.balance
        game_two_players.pay_rent(p, prop)
        assert p.balance == before

    def test_pay_rent_transfers_to_owner_when_active(self, game_two_players):
        # Verifies active-rent branch transfers funds from tenant to owner.
        p = game_two_players.players[0]
        o = game_two_players.players[1]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = o
        o.add_property(prop)
        before = o.balance
        game_two_players.pay_rent(p, prop)
        assert o.balance > before

    def test_mortgage_property_false_for_non_owner(self, game_two_players):
        # Verifies mortgage branch rejects non-owner requests.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = game_two_players.players[1]
        assert game_two_players.mortgage_property(p, prop) is False

    def test_mortgage_property_false_when_already_mortgaged(self, game_two_players):
        # Verifies mortgage branch rejects duplicate mortgage action.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        p.add_property(prop)
        prop.is_mortgaged = True
        assert game_two_players.mortgage_property(p, prop) is False

    def test_mortgage_property_true_on_success(self, game_two_players):
        # Verifies mortgage success branch returns true.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        p.add_property(prop)
        assert game_two_players.mortgage_property(p, prop) is True

    def test_unmortgage_false_for_non_owner(self, game_two_players):
        # Verifies unmortgage branch rejects non-owner requests.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = game_two_players.players[1]
        assert game_two_players.unmortgage_property(p, prop) is False

    def test_unmortgage_false_when_not_mortgaged(self, game_two_players):
        # Verifies unmortgage branch rejects active properties.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        p.add_property(prop)
        assert game_two_players.unmortgage_property(p, prop) is False

    def test_unmortgage_false_when_cannot_afford(self, game_two_players):
        # Verifies unmortgage affordability branch for low balance.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        p.add_property(prop)
        prop.is_mortgaged = True
        p.balance = 0
        assert game_two_players.unmortgage_property(p, prop) is False

    def test_unmortgage_true_on_success(self, game_two_players):
        # Verifies unmortgage success branch returns true.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        p.add_property(prop)
        prop.is_mortgaged = True
        p.balance = 1000
        assert game_two_players.unmortgage_property(p, prop) is True

    def test_trade_false_when_seller_not_owner(self, game_two_players):
        # Verifies trade branch rejects seller without ownership.
        s = game_two_players.players[0]
        b = game_two_players.players[1]
        prop = game_two_players.board.get_property_at(1)
        assert game_two_players.trade(s, b, prop, 10) is False

    def test_trade_false_when_buyer_cannot_afford(self, game_two_players):
        # Verifies trade branch rejects unaffordable cash amount.
        s = game_two_players.players[0]
        b = game_two_players.players[1]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = s
        s.add_property(prop)
        b.balance = 0
        assert game_two_players.trade(s, b, prop, 10) is False

    def test_trade_true_on_success(self, game_two_players):
        # Verifies trade success branch transfers ownership.
        s = game_two_players.players[0]
        b = game_two_players.players[1]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = s
        s.add_property(prop)
        b.balance = 100
        assert game_two_players.trade(s, b, prop, 10) is True


class TestGameAuctionJailCards:
    def test_auction_rejects_bid_below_min_increment(self, game_two_players, monkeypatch):
        # Verifies auction low-bid branch enforces minimum increment.
        prop = game_two_players.board.get_property_at(1)
        bids = iter([20, 25])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(bids))
        game_two_players.auction_property(prop)
        assert prop.owner == game_two_players.players[0]

    def test_auction_rejects_unaffordable_bid(self, game_two_players, monkeypatch):
        # Verifies auction affordability branch ignores bids over balance.
        prop = game_two_players.board.get_property_at(1)
        game_two_players.players[1].balance = 5
        bids = iter([10, 50])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(bids))
        game_two_players.auction_property(prop)
        assert prop.owner == game_two_players.players[0]

    def test_auction_no_bids_keeps_unowned(self, game_two_players, monkeypatch):
        # Verifies auction no-bids branch leaves property unowned.
        prop = game_two_players.board.get_property_at(1)
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: 0)
        game_two_players.auction_property(prop)
        assert prop.owner is None

    def test_auction_assigns_winner(self, game_two_players, monkeypatch):
        # Verifies auction success branch assigns property to highest bidder.
        prop = game_two_players.board.get_property_at(1)
        bids = iter([10, 30])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(bids))
        game_two_players.auction_property(prop)
        assert prop.owner == game_two_players.players[1]

    def test_handle_jail_turn_uses_card(self, game_two_players, monkeypatch):
        # Verifies jail-card branch consumes card and releases player.
        p = game_two_players.players[0]
        p.in_jail = True
        p.get_out_of_jail_cards = 1
        monkeypatch.setattr("moneypoly.game.ui.confirm", lambda _p: True)
        monkeypatch.setattr(game_two_players.dice, "roll", lambda: 2)
        monkeypatch.setattr(game_two_players, "_move_and_resolve", lambda *_: None)
        game_two_players._handle_jail_turn(p)
        assert p.get_out_of_jail_cards == 0

    def test_handle_jail_turn_voluntary_fine_releases(self, game_two_players, monkeypatch):
        # Verifies voluntary-fine branch clears jail status.
        p = game_two_players.players[0]
        p.in_jail = True
        monkeypatch.setattr("moneypoly.game.ui.confirm", lambda _p: True)
        monkeypatch.setattr(game_two_players.dice, "roll", lambda: 2)
        monkeypatch.setattr(game_two_players, "_move_and_resolve", lambda *_: None)
        game_two_players._handle_jail_turn(p)
        assert p.in_jail is False

    def test_handle_jail_turn_mandatory_release_after_three(self, game_two_players, monkeypatch):
        # Verifies mandatory-release branch triggers on third skipped jail turn.
        p = game_two_players.players[0]
        p.in_jail = True
        p.jail_turns = 2
        monkeypatch.setattr("moneypoly.game.ui.confirm", lambda _p: False)
        monkeypatch.setattr(game_two_players.dice, "roll", lambda: 2)
        monkeypatch.setattr(game_two_players, "_move_and_resolve", lambda *_: None)
        game_two_players._handle_jail_turn(p)
        assert p.in_jail is False

    def test_handle_jail_turn_declines_card_then_pays_fine(self, game_two_players, monkeypatch):
        # Verifies branch where card exists but user declines, then pays fine.
        p = game_two_players.players[0]
        p.in_jail = True
        p.get_out_of_jail_cards = 1
        answers = iter([False, True])
        monkeypatch.setattr("moneypoly.game.ui.confirm", lambda _p: next(answers))
        monkeypatch.setattr(game_two_players.dice, "roll", lambda: 2)
        monkeypatch.setattr(game_two_players, "_move_and_resolve", lambda *_: None)
        game_two_players._handle_jail_turn(p)
        assert p.in_jail is False

    def test_handle_jail_turn_waits_when_not_third_turn(self, game_two_players, monkeypatch):
        # Verifies jail wait branch keeps player jailed before mandatory turn.
        p = game_two_players.players[0]
        p.in_jail = True
        p.jail_turns = 0
        monkeypatch.setattr("moneypoly.game.ui.confirm", lambda _p: False)
        game_two_players._handle_jail_turn(p)
        assert p.in_jail is True

    def test_apply_card_none_no_change(self, game_two_players):
        # Verifies card handler early-return branch for empty draw.
        p = game_two_players.players[0]
        before = p.balance
        game_two_players._apply_card(p, None)
        assert p.balance == before

    def test_apply_card_collect_increases_balance(self, game_two_players):
        # Verifies collect-card branch credits player via bank payout.
        p = game_two_players.players[0]
        before = p.balance
        game_two_players._apply_card(p, {"description": "d", "action": "collect", "value": 10})
        assert p.balance == before + 10

    def test_apply_card_pay_decreases_balance(self, game_two_players):
        # Verifies pay-card branch debits player balance.
        p = game_two_players.players[0]
        before = p.balance
        game_two_players._apply_card(p, {"description": "d", "action": "pay", "value": 10})
        assert p.balance == before - 10

    def test_apply_card_jail_sets_flag(self, game_two_players):
        # Verifies jail-card branch sends player to jail.
        p = game_two_players.players[0]
        game_two_players._apply_card(p, {"description": "d", "action": "jail", "value": 0})
        assert p.in_jail is True

    def test_apply_card_jail_free_increments_card_count(self, game_two_players):
        # Verifies jail-free card branch increments stored card count.
        p = game_two_players.players[0]
        game_two_players._apply_card(p, {"description": "d", "action": "jail_free", "value": 0})
        assert p.get_out_of_jail_cards == 1

    def test_apply_card_move_to_passes_go(self, game_two_players):
        # Verifies move-to branch credits salary when destination wraps past Go.
        p = game_two_players.players[0]
        p.position = 39
        before = p.balance
        game_two_players._apply_card(p, {"description": "d", "action": "move_to", "value": 0})
        assert p.balance == before + 200

    def test_apply_card_move_to_property_triggers_handler(self, game_two_players, monkeypatch):
        # Verifies move-to property branch invokes property tile handler.
        p = game_two_players.players[0]
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _v: "property")
        monkeypatch.setattr(game_two_players.board, "get_property_at", lambda _v: game_two_players.board.properties[0])
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_handle_property_tile", lambda *_: called.__setitem__("value", True))
        game_two_players._apply_card(p, {"description": "d", "action": "move_to", "value": 1})
        assert called["value"] is True

    def test_apply_card_move_to_property_without_property_no_handler(self, game_two_players, monkeypatch):
        # Verifies move-to property branch no-ops when property lookup fails.
        p = game_two_players.players[0]
        monkeypatch.setattr(game_two_players.board, "get_tile_type", lambda _v: "property")
        monkeypatch.setattr(game_two_players.board, "get_property_at", lambda _v: None)
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_handle_property_tile", lambda *_: called.__setitem__("value", True))
        game_two_players._apply_card(p, {"description": "d", "action": "move_to", "value": 1})
        assert called["value"] is False

    def test_apply_card_birthday_skips_insolvent_players(self, game_two_players):
        # Verifies birthday loop branch skips players below payment threshold.
        p = game_two_players.players[0]
        other = game_two_players.players[1]
        other.balance = 5
        before = p.balance
        game_two_players._apply_card(p, {"description": "d", "action": "birthday", "value": 10})
        assert p.balance == before

    def test_apply_card_birthday_collects_from_solvent_players(self, game_two_players):
        # Verifies birthday loop branch transfers money from solvent players.
        p = game_two_players.players[0]
        other = game_two_players.players[1]
        other.balance = 100
        before = p.balance
        game_two_players._apply_card(p, {"description": "d", "action": "birthday", "value": 10})
        assert p.balance == before + 10

    def test_apply_card_collect_from_all_skips_insolvent_players(self, game_two_players):
        # Verifies collect-from-all branch skips players below threshold.
        p = game_two_players.players[0]
        other = game_two_players.players[1]
        other.balance = 5
        before = p.balance
        game_two_players._apply_card(p, {"description": "d", "action": "collect_from_all", "value": 10})
        assert p.balance == before

    def test_apply_card_collect_from_all_collects_when_solvent(self, game_two_players):
        # Verifies collect-from-all branch transfers funds from solvent players.
        p = game_two_players.players[0]
        other = game_two_players.players[1]
        other.balance = 100
        before = p.balance
        game_two_players._apply_card(p, {"description": "d", "action": "collect_from_all", "value": 10})
        assert p.balance == before + 10

    def test_apply_card_unknown_action_is_noop(self, game_two_players):
        # Verifies fall-through branch for unsupported card actions.
        p = game_two_players.players[0]
        before = p.balance
        game_two_players._apply_card(p, {"description": "d", "action": "unknown", "value": 10})
        assert p.balance == before


class TestGameLifecycleMenus:
    def test_check_bankruptcy_removes_player(self, game_two_players):
        # Verifies bankruptcy branch removes bankrupt player from game list.
        p = game_two_players.players[0]
        p.balance = 0
        game_two_players._check_bankruptcy(p)
        assert p not in game_two_players.players

    def test_check_bankruptcy_resets_property_state(self, game_two_players):
        # Verifies bankruptcy branch clears owner and mortgage flags for assets.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        prop.is_mortgaged = True
        p.add_property(prop)
        p.balance = 0
        game_two_players._check_bankruptcy(p)
        assert prop.owner is None

    def test_check_bankruptcy_resets_current_index_when_out_of_range(self, game_two_players):
        # Verifies bankruptcy branch normalizes current index after removal.
        p = game_two_players.players[1]
        game_two_players.current_index = 1
        p.balance = 0
        game_two_players._check_bankruptcy(p)
        assert game_two_players.current_index == 0

    def test_check_bankruptcy_ignores_player_not_in_list(self, game_two_players):
        # Verifies bankruptcy branch where target player is already absent.
        ghost = Player("Ghost")
        ghost.balance = 0
        game_two_players._check_bankruptcy(ghost)
        assert len(game_two_players.players) == 2

    def test_check_bankruptcy_keeps_solvent_player(self, game_two_players):
        # Verifies non-bankrupt branch leaves player in game list.
        p = game_two_players.players[0]
        p.balance = 1
        game_two_players._check_bankruptcy(p)
        assert p in game_two_players.players

    def test_find_winner_none_for_empty_players(self, game_two_players):
        # Verifies find-winner branch returns None when no players remain.
        game_two_players.players = []
        assert game_two_players.find_winner() is None

    def test_find_winner_highest_net_worth(self, game_two_players):
        # Verifies find-winner branch selects highest net worth player.
        game_two_players.players[0].balance = 10
        game_two_players.players[1].balance = 20
        assert game_two_players.find_winner() == game_two_players.players[1]

    def test_run_prints_game_over_with_winner(self, game_two_players, monkeypatch, capsys):
        # Verifies run-loop winner branch prints game-over summary.
        monkeypatch.setattr(game_two_players, "play_turn", lambda: setattr(game_two_players, "running", False))
        game_two_players.run()
        assert "GAME OVER" in capsys.readouterr().out

    def test_run_prints_no_players_message(self, game_two_players, monkeypatch, capsys):
        # Verifies run-loop no-player branch prints terminal message.
        game_two_players.players = []
        game_two_players.run()
        assert "no players remaining" in capsys.readouterr().out.lower()

    def test_interactive_menu_choice_zero_exits(self, game_two_players, monkeypatch):
        # Verifies menu loop exit branch on zero choice.
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: 0)
        game_two_players.interactive_menu(game_two_players.players[0])
        assert True

    def test_interactive_menu_choice_one_calls_standings(self, game_two_players, monkeypatch):
        # Verifies menu branch dispatch for standings view.
        choices = iter([1, 0])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(choices))
        called = {"value": False}
        monkeypatch.setattr("moneypoly.game.ui.print_standings", lambda _p: called.__setitem__("value", True))
        game_two_players.interactive_menu(game_two_players.players[0])
        assert called["value"] is True

    def test_interactive_menu_choice_two_calls_board_ownership(self, game_two_players, monkeypatch):
        # Verifies menu branch dispatch for board ownership view.
        choices = iter([2, 0])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(choices))
        called = {"value": False}
        monkeypatch.setattr("moneypoly.game.ui.print_board_ownership", lambda _b: called.__setitem__("value", True))
        game_two_players.interactive_menu(game_two_players.players[0])
        assert called["value"] is True

    def test_interactive_menu_choice_three_calls_menu_mortgage(self, game_two_players, monkeypatch):
        # Verifies menu branch dispatch for mortgage sub-menu.
        choices = iter([3, 0])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(choices))
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_menu_mortgage", lambda _p: called.__setitem__("value", True))
        game_two_players.interactive_menu(game_two_players.players[0])
        assert called["value"] is True

    def test_interactive_menu_choice_four_calls_menu_unmortgage(self, game_two_players, monkeypatch):
        # Verifies menu branch dispatch for unmortgage sub-menu.
        choices = iter([4, 0])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(choices))
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_menu_unmortgage", lambda _p: called.__setitem__("value", True))
        game_two_players.interactive_menu(game_two_players.players[0])
        assert called["value"] is True

    def test_interactive_menu_choice_five_calls_menu_trade(self, game_two_players, monkeypatch):
        # Verifies menu branch dispatch for trade sub-menu.
        choices = iter([5, 0])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(choices))
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "_menu_trade", lambda _p: called.__setitem__("value", True))
        game_two_players.interactive_menu(game_two_players.players[0])
        assert called["value"] is True

    def test_interactive_menu_choice_six_positive_loan(self, game_two_players, monkeypatch):
        # Verifies emergency-loan branch issues loan for positive request.
        choices = iter([6, 20, 0])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(choices))
        called = {"value": False}
        monkeypatch.setattr(game_two_players.bank, "give_loan", lambda *_: called.__setitem__("value", True))
        game_two_players.interactive_menu(game_two_players.players[0])
        assert called["value"] is True

    def test_interactive_menu_choice_six_non_positive_loan(self, game_two_players, monkeypatch):
        # Verifies emergency-loan branch skips loan for non-positive amount.
        choices = iter([6, 0, 0])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(choices))
        called = {"value": False}
        monkeypatch.setattr(game_two_players.bank, "give_loan", lambda *_: called.__setitem__("value", True))
        game_two_players.interactive_menu(game_two_players.players[0])
        assert called["value"] is False

    def test_interactive_menu_unknown_choice_loops(self, game_two_players, monkeypatch):
        # Verifies menu fall-through branch for unsupported option values.
        choices = iter([99, 0])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(choices))
        game_two_players.interactive_menu(game_two_players.players[0])
        assert True

    def test_menu_mortgage_no_properties(self, game_two_players, capsys):
        # Verifies mortgage menu branch for empty mortgageable list.
        game_two_players._menu_mortgage(game_two_players.players[0])
        assert "No properties available" in capsys.readouterr().out

    def test_menu_mortgage_valid_selection_calls_mortgage(self, game_two_players, monkeypatch):
        # Verifies mortgage menu valid index branch invokes mortgage operation.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        p.add_property(prop)
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: 1)
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "mortgage_property", lambda *_: called.__setitem__("value", True))
        game_two_players._menu_mortgage(p)
        assert called["value"] is True

    def test_menu_mortgage_invalid_selection_skips_call(self, game_two_players, monkeypatch):
        # Verifies mortgage menu invalid index branch performs no action.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        p.add_property(prop)
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: 9)
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "mortgage_property", lambda *_: called.__setitem__("value", True))
        game_two_players._menu_mortgage(p)
        assert called["value"] is False

    def test_menu_unmortgage_no_properties(self, game_two_players, capsys):
        # Verifies unmortgage menu branch for no mortgaged properties.
        game_two_players._menu_unmortgage(game_two_players.players[0])
        assert "No mortgaged properties" in capsys.readouterr().out

    def test_menu_unmortgage_valid_selection_calls_unmortgage(self, game_two_players, monkeypatch):
        # Verifies unmortgage menu valid index branch invokes unmortgage operation.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        prop.is_mortgaged = True
        p.add_property(prop)
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: 1)
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "unmortgage_property", lambda *_: called.__setitem__("value", True))
        game_two_players._menu_unmortgage(p)
        assert called["value"] is True

    def test_menu_unmortgage_invalid_selection_skips_call(self, game_two_players, monkeypatch):
        # Verifies unmortgage menu invalid index branch performs no action.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        prop.is_mortgaged = True
        p.add_property(prop)
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: 9)
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "unmortgage_property", lambda *_: called.__setitem__("value", True))
        game_two_players._menu_unmortgage(p)
        assert called["value"] is False

    def test_menu_trade_no_other_players(self, monkeypatch):
        # Verifies trade menu branch for single-player game.
        g = Game(["Solo"])
        g._menu_trade(g.players[0])
        assert len(g.players) == 1

    def test_menu_trade_invalid_partner_index_returns(self, game_two_players, monkeypatch):
        # Verifies trade menu branch early-returns on invalid partner index.
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: 99)
        game_two_players._menu_trade(game_two_players.players[0])
        assert True

    def test_menu_trade_no_player_properties(self, game_two_players, monkeypatch, capsys):
        # Verifies trade menu branch when current player has no tradable properties.
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: 1)
        game_two_players._menu_trade(game_two_players.players[0])
        assert "has no properties" in capsys.readouterr().out

    def test_menu_trade_invalid_property_index_returns(self, game_two_players, monkeypatch):
        # Verifies trade menu branch early-returns on invalid property index.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        p.add_property(prop)
        values = iter([1, 99])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(values))
        game_two_players._menu_trade(p)
        assert prop.owner == p

    def test_menu_trade_success_calls_trade(self, game_two_players, monkeypatch):
        # Verifies trade menu happy path invokes trade operation.
        p = game_two_players.players[0]
        prop = game_two_players.board.get_property_at(1)
        prop.owner = p
        p.add_property(prop)
        values = iter([1, 1, 10])
        monkeypatch.setattr("moneypoly.game.ui.safe_int_input", lambda *_a, **_k: next(values))
        called = {"value": False}
        monkeypatch.setattr(game_two_players, "trade", lambda *_: called.__setitem__("value", True))
        game_two_players._menu_trade(p)
        assert called["value"] is True
