from moneypoly import config


class TestConfigConstants:
    def test_board_size_constant(self):
        # Verifies board-size constant used by movement wrap logic.
        assert config.BOARD_SIZE == 40

    def test_starting_balance_positive(self):
        # Verifies game starts players with positive balance.
        assert config.STARTING_BALANCE > 0

    def test_max_turns_positive(self):
        # Verifies run-loop turn cap is a valid positive number.
        assert config.MAX_TURNS > 0
