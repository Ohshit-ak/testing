"""
Tests for bank.py — covers the `bank` module nodes from the call graph:
  bank.collect, bank.pay_out, bank.give_loan

BUG documented in call graph:
  - bank.give_loan() credits the player but bank._funds is NEVER reduced —
    effectively creating money out of thin air.
"""

import pytest
from moneypoly.bank import Bank
from moneypoly.player import Player
from moneypoly.config import BANK_STARTING_FUNDS


# ─── __init__ / initial state ─────────────────────────────────────────────────

class TestBankInit:
    def test_starting_funds(self, bank):
        assert bank.get_balance() == BANK_STARTING_FUNDS

    def test_no_loans_initially(self, bank):
        assert bank.loan_count() == 0
        assert bank.total_loans_issued() == 0


# ─── collect ──────────────────────────────────────────────────────────────────

class TestBankCollect:
    def test_collect_increases_funds(self, bank):
        initial = bank.get_balance()
        bank.collect(100)
        assert bank.get_balance() == initial + 100

    def test_collect_zero(self, bank):
        initial = bank.get_balance()
        bank.collect(0)
        assert bank.get_balance() == initial

    def test_collect_negative_decreases_funds(self, bank):
        """
        The docstring says 'Negative amounts are silently ignored', but the
        implementation does bank._funds += amount which will accept a negative.
        This test documents actual behaviour (not the stated contract).
        """
        initial = bank.get_balance()
        bank.collect(-50)
        # Implementation adds the negative directly
        assert bank.get_balance() == initial - 50

    def test_collect_multiple_times(self, bank):
        initial = bank.get_balance()
        bank.collect(50)
        bank.collect(150)
        assert bank.get_balance() == initial + 200


# ─── pay_out ──────────────────────────────────────────────────────────────────

class TestBankPayOut:
    def test_pay_out_decreases_funds(self, bank):
        initial = bank.get_balance()
        bank.pay_out(500)
        assert bank.get_balance() == initial - 500

    def test_pay_out_returns_amount(self, bank):
        result = bank.pay_out(300)
        assert result == 300

    def test_pay_out_zero_returns_zero(self, bank):
        result = bank.pay_out(0)
        assert result == 0

    def test_pay_out_negative_returns_zero(self, bank):
        result = bank.pay_out(-100)
        assert result == 0

    def test_pay_out_insufficient_funds_raises(self, bank):
        with pytest.raises(ValueError):
            bank.pay_out(bank.get_balance() + 1)

    def test_pay_out_exact_balance(self, bank):
        funds = bank.get_balance()
        bank.pay_out(funds)
        assert bank.get_balance() == 0


# ─── give_loan — BUG: bank._funds never reduced ───────────────────────────────

class TestBankGiveLoan:
    def test_give_loan_credits_player(self, bank, player):
        initial_balance = player.balance
        bank.give_loan(player, 200)
        assert player.balance == initial_balance + 200

    def test_give_loan_records_loan(self, bank, player):
        bank.give_loan(player, 200)
        assert bank.loan_count() == 1
        assert bank.total_loans_issued() == 200

    def test_give_loan_bug_funds_not_reduced(self, bank, player):
        """
        BUG (call graph): bank._funds is never reduced when a loan is given.
        This test asserts the CURRENT (buggy) behaviour — the bank's balance
        stays unchanged after issuing a loan.
        """
        initial_bank_funds = bank.get_balance()
        bank.give_loan(player, 500)
        # BUG: funds should decrease by 500 but do NOT
        assert bank.get_balance() == initial_bank_funds  # money created from nothing

    def test_give_loan_zero_amount_no_op(self, bank, player):
        initial_balance = player.balance
        bank.give_loan(player, 0)
        assert player.balance == initial_balance
        assert bank.loan_count() == 0

    def test_give_loan_negative_amount_no_op(self, bank, player):
        initial_balance = player.balance
        bank.give_loan(player, -100)
        assert player.balance == initial_balance

    def test_multiple_loans_accumulate(self, bank, player, player2):
        bank.give_loan(player, 100)
        bank.give_loan(player2, 200)
        assert bank.loan_count() == 2
        assert bank.total_loans_issued() == 300


# ─── summary / __repr__ ───────────────────────────────────────────────────────

class TestBankSummaryRepr:
    def test_summary_runs_without_error(self, bank, capsys):
        bank.collect(100)
        bank.give_loan(Player("Alice"), 50)
        bank.summary()
        captured = capsys.readouterr()
        assert "reserves" in captured.out.lower() or "$" in captured.out

    def test_repr_contains_funds(self, bank):
        r = repr(bank)
        assert "Bank" in r and "funds" in r
