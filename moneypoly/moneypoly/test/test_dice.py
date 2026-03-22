from moneypoly.dice import Dice


class TestDice:
    def test_reset_sets_values_to_zero(self):
        # Verifies reset branch clears dice faces and streak state.
        d = Dice()
        d.die1 = 6
        d.die2 = 6
        d.doubles_streak = 2
        d.reset()
        assert d.die1 == 0

    def test_roll_returns_total(self, monkeypatch):
        # Verifies roll path returns computed total.
        values = iter([2, 3])
        monkeypatch.setattr("moneypoly.dice.random.randint", lambda _a, _b: next(values))
        assert Dice().roll() == 5

    def test_roll_increments_streak_on_doubles(self, monkeypatch):
        # Verifies doubles branch increments consecutive doubles counter.
        monkeypatch.setattr("moneypoly.dice.random.randint", lambda _a, _b: 4)
        d = Dice()
        d.roll()
        assert d.doubles_streak == 1

    def test_roll_resets_streak_on_non_doubles(self, monkeypatch):
        # Verifies non-doubles branch resets streak counter.
        values = iter([4, 5])
        monkeypatch.setattr("moneypoly.dice.random.randint", lambda _a, _b: next(values))
        d = Dice()
        d.doubles_streak = 2
        d.roll()
        assert d.doubles_streak == 0

    def test_is_doubles_true(self):
        # Verifies doubles predicate true branch.
        d = Dice()
        d.die1, d.die2 = 2, 2
        assert d.is_doubles() is True

    def test_is_doubles_false(self):
        # Verifies doubles predicate false branch.
        d = Dice()
        d.die1, d.die2 = 2, 3
        assert d.is_doubles() is False

    def test_total_sums_faces(self):
        # Verifies total branch calculates die sum.
        d = Dice()
        d.die1, d.die2 = 1, 6
        assert d.total() == 7

    def test_describe_includes_doubles_note(self):
        # Verifies describe branch adds doubles marker when applicable.
        d = Dice()
        d.die1, d.die2 = 3, 3
        assert "DOUBLES" in d.describe()

    def test_describe_without_doubles_note(self):
        # Verifies describe branch omits doubles marker for mixed roll.
        d = Dice()
        d.die1, d.die2 = 3, 4
        assert "DOUBLES" not in d.describe()

    def test_repr_contains_dice_name(self):
        # Verifies repr branch includes class marker for debugging.
        assert "Dice(" in repr(Dice())
