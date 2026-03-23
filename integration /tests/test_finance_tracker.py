"""
tests/test_finance_tracker.py
Unit tests for FinanceTrackerModule.
"""

import unittest
from helpers import make_modules


class TestFinanceTracker(unittest.TestCase):

    def setUp(self):
        *_, self.inv, _, _, _, _, self.fin = make_modules(starting_cash=5_000.0)
        # Unpack properly
        mods = make_modules(starting_cash=5_000.0)
        self.inv = mods[2]
        self.fin = mods[7]

    # ── Income recording ──────────────────────────────────────────────────────

    def test_record_income_increases_balance(self):
        before = self.inv.cash_balance
        self.fin.record_income(1_000.0, "race_prize", "Night race win")
        self.assertAlmostEqual(self.inv.cash_balance, before + 1_000.0, places=2)

    def test_record_income_creates_transaction(self):
        tx = self.fin.record_income(500.0, "sponsorship", "Brand deal")
        self.assertEqual(tx.tx_type, "income")
        self.assertAlmostEqual(tx.amount, 500.0, places=2)
        self.assertEqual(tx.category, "sponsorship")

    def test_record_income_balance_after_correct(self):
        tx = self.fin.record_income(200.0, "misc", "Extra cash")
        self.assertAlmostEqual(tx.balance_after, self.inv.cash_balance, places=2)

    # ── Expense recording ─────────────────────────────────────────────────────

    def test_record_expense_decreases_balance(self):
        before = self.inv.cash_balance
        self.fin.record_expense(400.0, "equipment", "Turbocharger")
        self.assertAlmostEqual(self.inv.cash_balance, before - 400.0, places=2)

    def test_record_expense_creates_transaction(self):
        tx = self.fin.record_expense(300.0, "repair", "Engine rebuild")
        self.assertEqual(tx.tx_type, "expense")
        self.assertAlmostEqual(tx.amount, 300.0, places=2)
        self.assertEqual(tx.category, "repair")

    def test_record_expense_balance_after_correct(self):
        tx = self.fin.record_expense(100.0, "fuel", "Tank up")
        self.assertAlmostEqual(tx.balance_after, self.inv.cash_balance, places=2)

    # ── Ledger ────────────────────────────────────────────────────────────────

    def test_ledger_empty_initially(self):
        self.assertEqual(len(self.fin._ledger), 0)

    def test_ledger_entry_created_for_income(self):
        self.fin.record_income(100.0, "cat", "desc")
        self.assertEqual(len(self.fin._ledger), 1)

    def test_ledger_entry_created_for_expense(self):
        self.fin.record_expense(100.0, "cat", "desc")
        self.assertEqual(len(self.fin._ledger), 1)

    def test_ledger_two_entries_after_one_each(self):
        self.fin.record_income(100.0, "in", "Income")
        self.fin.record_expense(50.0, "out", "Expense")
        self.assertEqual(len(self.fin._ledger), 2)

    def test_ledger_preserves_order(self):
        self.fin.record_income(100.0, "a", "First")
        self.fin.record_expense(50.0, "b", "Second")
        self.assertEqual(self.fin._ledger[0].tx_type, "income")
        self.assertEqual(self.fin._ledger[1].tx_type, "expense")

    # ── Category summaries ────────────────────────────────────────────────────

    def test_income_by_category_sums_correctly(self):
        self.fin.record_income(1_000.0, "race_prize", "Race 1")
        self.fin.record_income(2_000.0, "race_prize", "Race 2")
        self.fin.record_income(500.0,   "sponsorship", "Sponsor")
        cats = self.fin.income_by_category()
        self.assertAlmostEqual(cats["race_prize"],   3_000.0, places=2)
        self.assertAlmostEqual(cats["sponsorship"],    500.0, places=2)

    def test_expense_by_category_sums_correctly(self):
        self.fin.record_expense(300.0, "repair", "Fix car")
        self.fin.record_expense(200.0, "repair", "Fix again")
        self.fin.record_expense(100.0, "fuel",   "Tank up")
        cats = self.fin.expense_by_category()
        self.assertAlmostEqual(cats["repair"], 500.0, places=2)
        self.assertAlmostEqual(cats["fuel"],   100.0, places=2)

    def test_income_by_category_empty_initially(self):
        self.assertEqual(self.fin.income_by_category(), {})

    def test_expense_by_category_empty_initially(self):
        self.assertEqual(self.fin.expense_by_category(), {})

    # ── Net P/L ───────────────────────────────────────────────────────────────

    def test_net_profit_positive(self):
        self.fin.record_income(2_000.0, "race_prize", "Won")
        self.fin.record_expense(500.0, "repair", "Fixed")
        income  = sum(t.amount for t in self.fin._ledger if t.tx_type == "income")
        expense = sum(t.amount for t in self.fin._ledger if t.tx_type == "expense")
        self.assertAlmostEqual(income - expense, 1_500.0, places=2)

    def test_net_loss_when_expenses_exceed_income(self):
        self.fin.record_income(100.0,   "misc", "Small win")
        self.fin.record_expense(1_000.0, "equipment", "Big spend")
        income  = sum(t.amount for t in self.fin._ledger if t.tx_type == "income")
        expense = sum(t.amount for t in self.fin._ledger if t.tx_type == "expense")
        self.assertLess(income - expense, 0)

    # ── Error cases ───────────────────────────────────────────────────────────

    def test_record_expense_insufficient_funds_raises(self):
        with self.assertRaises(ValueError):
            self.fin.record_expense(999_999.0, "crazy", "Way too much")

    def test_record_income_negative_raises(self):
        with self.assertRaises(ValueError):
            self.fin.record_income(-100.0, "cat", "Negative income")

    def test_record_expense_negative_raises(self):
        with self.assertRaises(ValueError):
            self.fin.record_expense(-50.0, "cat", "Negative expense")


if __name__ == "__main__":
    unittest.main()
