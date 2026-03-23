from moneypoly.cards import CardDeck


class TestCardDeck:
    def test_draw_returns_none_for_empty_deck(self):
        # Verifies empty-deck draw branch returns sentinel None.
        assert CardDeck([]).draw() is None

    def test_peek_returns_none_for_empty_deck(self):
        # Verifies empty-deck peek branch returns sentinel None.
        assert CardDeck([]).peek() is None

    def test_draw_advances_index(self):
        # Verifies draw branch mutates index state.
        deck = CardDeck([{"id": 1}])
        deck.draw()
        assert deck.index == 1

    def test_draw_cycles_cards(self):
        # Verifies modulo branch cycles card order after exhaustion.
        deck = CardDeck([{"id": 1}, {"id": 2}])
        deck.draw()
        deck.draw()
        assert deck.draw()["id"] == 1

    def test_peek_does_not_advance_index(self):
        # Verifies peek path leaves deck state unchanged.
        deck = CardDeck([{"id": 1}])
        deck.peek()
        assert deck.index == 0

    def test_reshuffle_resets_index(self, monkeypatch):
        # Verifies reshuffle branch resets index to zero.
        deck = CardDeck([{"id": 1}, {"id": 2}])
        deck.index = 5
        monkeypatch.setattr("moneypoly.cards.random.shuffle", lambda _: None)
        deck.reshuffle()
        assert deck.index == 0

    def test_reshuffle_empty_deck_keeps_index(self):
        # Verifies empty deck guard branch in reshuffle.
        deck = CardDeck([])
        deck.index = 3
        deck.reshuffle()
        assert deck.index == 3

    def test_cards_remaining_uses_modulo(self):
        # Verifies remaining-card branch with wrapped index value.
        deck = CardDeck([{"id": 1}, {"id": 2}, {"id": 3}])
        deck.index = 4
        assert deck.cards_remaining() == 2

    def test_len_returns_card_count(self):
        # Verifies len branch reports full deck size.
        assert len(CardDeck([1, 2, 3])) == 3

    def test_repr_contains_carddeck(self):
        # Verifies repr branch emits class name for diagnostics.
        assert "CardDeck(" in repr(CardDeck([1]))
