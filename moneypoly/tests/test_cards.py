"""
Tests for cards.py — covers the `cards/dice` module nodes from the call graph:
  deck.draw
"""

import pytest
from moneypoly.cards import CardDeck, CHANCE_CARDS, COMMUNITY_CHEST_CARDS


# ─── CardDeck.draw ────────────────────────────────────────────────────────────

class TestCardDeckDraw:
    def test_draw_returns_card(self, chance_deck):
        card = chance_deck.draw()
        assert card is not None
        assert "action" in card
        assert "value" in card

    def test_draw_cycles_sequentially(self):
        cards = [{"action": "collect", "value": 100},
                 {"action": "pay", "value": 50}]
        deck = CardDeck(cards)
        first = deck.draw()
        second = deck.draw()
        assert first["value"] == 100
        assert second["value"] == 50

    def test_draw_wraps_around(self):
        cards = [{"action": "collect", "value": 1}]
        deck = CardDeck(cards)
        deck.draw()         # index = 1, wraps to 0
        card = deck.draw()  # should return the same card again
        assert card["value"] == 1

    def test_draw_empty_deck_returns_none(self):
        deck = CardDeck([])
        assert deck.draw() is None

    def test_draw_increments_index(self, chance_deck):
        initial_index = chance_deck.index
        chance_deck.draw()
        assert chance_deck.index == initial_index + 1

    def test_draw_all_chance_cards(self):
        deck = CardDeck(list(CHANCE_CARDS))
        for _ in CHANCE_CARDS:
            card = deck.draw()
            assert card is not None

    def test_draw_all_community_chest_cards(self):
        deck = CardDeck(list(COMMUNITY_CHEST_CARDS))
        for _ in COMMUNITY_CHEST_CARDS:
            card = deck.draw()
            assert card is not None


# ─── peek / reshuffle / cards_remaining ───────────────────────────────────────

class TestCardDeckHelpers:
    def test_peek_does_not_advance_index(self, chance_deck):
        idx = chance_deck.index
        chance_deck.peek()
        assert chance_deck.index == idx

    def test_peek_returns_same_as_next_draw(self, chance_deck):
        peeked = chance_deck.peek()
        drawn = chance_deck.draw()
        assert peeked == drawn

    def test_peek_empty_deck_returns_none(self):
        assert CardDeck([]).peek() is None

    def test_cards_remaining_full_deck(self, chance_deck):
        assert chance_deck.cards_remaining() == len(CHANCE_CARDS)

    def test_cards_remaining_after_draw(self, chance_deck):
        total = len(CHANCE_CARDS)
        chance_deck.draw()
        assert chance_deck.cards_remaining() == total - 1

    def test_reshuffle_resets_index(self, chance_deck):
        chance_deck.draw()
        chance_deck.draw()
        chance_deck.reshuffle()
        assert chance_deck.index == 0

    def test_len_returns_card_count(self, chance_deck):
        assert len(chance_deck) == len(CHANCE_CARDS)

    def test_repr_contains_count(self, chance_deck):
        assert str(len(CHANCE_CARDS)) in repr(chance_deck)
