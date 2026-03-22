import pytest

from moneypoly.player import Player


class TestBank:
    def test_get_balance_returns_starting_funds(self, bank):
        # Verifies initial reserve state for all bank transactions.
        assert bank.get_balance() > 0

    def test_collect_increases_balance(self, bank):
        # Verifies positive collection path updates reserves.
        before = bank.get_balance()
        bank.collect(10)
        assert bank.get_balance() == before + 10

    def test_collect_negative_decreases_balance(self, bank):
        # Verifies negative collection path changes reserves as implemented.
        before = bank.get_balance()
        bank.collect(-10)
        assert bank.get_balance() == before - 10

    def test_pay_out_zero_returns_zero(self, bank):
        # Verifies non-positive payout guard branch for zero input.
        assert bank.pay_out(0) == 0

    def test_pay_out_negative_returns_zero(self, bank):
        # Verifies non-positive payout guard branch for negative input.
        assert bank.pay_out(-1) == 0

    def test_pay_out_reduces_balance(self, bank):
        # Verifies successful payout branch debits bank funds.
        before = bank.get_balance()
        bank.pay_out(5)
        assert bank.get_balance() == before - 5

    def test_pay_out_raises_on_insufficient_funds(self, bank):
        # Verifies overdraw branch prevents impossible bank payouts.
        with pytest.raises(ValueError):
            bank.pay_out(bank.get_balance() + 1)

    def test_give_loan_ignores_non_positive_amount(self, bank):
        # Verifies loan guard branch for non-positive requested amount.
        p = Player("P")
        bank.give_loan(p, 0)
        assert bank.loan_count() == 0

    def test_give_loan_records_loan(self, bank):
        # Verifies successful loan path records issued loan metadata.
        p = Player("P")
        bank.give_loan(p, 10)
        assert bank.loan_count() == 1

    def test_total_loans_issued_returns_sum(self, bank):
        # Verifies loan aggregation logic over issued loan entries.
        p = Player("P")
        bank.give_loan(p, 10)
        bank.give_loan(p, 5)
        assert bank.total_loans_issued() == 15

    def test_summary_executes(self, bank, capsys):
        # Verifies summary branch prints formatted bank report.
        bank.summary()
        assert "Bank reserves" in capsys.readouterr().out

    def test_repr_contains_bank_name(self, bank):
        # Verifies representation branch for debug-friendly display.
        assert "Bank(" in repr(bank)
