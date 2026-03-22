"""
Module: Finance Tracker (Extra Module 2)
Responsibility: Maintain a full ledger of all financial transactions,
                generate summaries, flag losses, and track net profit/loss.
Depends on: InventoryModule (wraps its credit/debit to intercept transactions).

Design rationale: The Inventory module handles raw cash balance, but has no
concept of transaction history, budgeting, or profit/loss analysis.
FinanceTracker wraps Inventory's credit/debit calls and records every
transaction in a ledger — giving crew management a financial dashboard
without breaking the Inventory module's single responsibility.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid

from inventory import InventoryModule


TRANSACTION_TYPES = ("income", "expense")


@dataclass
class Transaction:
    tx_id: str
    tx_type: str          # "income" | "expense"
    amount: float
    category: str         # e.g. "race_prize", "mission_reward", "repair", "mission_cost"
    description: str
    balance_after: float
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __str__(self):
        sign = "+" if self.tx_type == "income" else "-"
        return (
            f"[{self.timestamp}] {sign}${self.amount:>10,.2f}  "
            f"[{self.category:<15}] {self.description:<35} | "
            f"Balance: ${self.balance_after:,.2f}"
        )


class FinanceTrackerModule:
    """
    Intercepts all cash movements via record_income() and record_expense(),
    and provides financial reporting on top of InventoryModule's balance.

    Usage: call record_income / record_expense INSTEAD of inventory.credit/debit
    directly — this module delegates to InventoryModule and also logs the entry.
    """

    def __init__(self, inventory: InventoryModule):
        self._inv = inventory
        self._ledger: List[Transaction] = []

    # ------------------------------------------------------------------ #
    #  Transaction recording                                               #
    # ------------------------------------------------------------------ #

    def record_income(self, amount: float, category: str, description: str) -> Transaction:
        """Credit inventory and log the income transaction."""
        self._inv.credit(amount, reason=description)
        tx = Transaction(
            tx_id=str(uuid.uuid4()),
            tx_type="income",
            amount=amount,
            category=category,
            description=description,
            balance_after=self._inv.cash_balance,
        )
        self._ledger.append(tx)
        return tx

    def record_expense(self, amount: float, category: str, description: str) -> Transaction:
        """Debit inventory and log the expense transaction."""
        self._inv.debit(amount, reason=description)
        tx = Transaction(
            tx_id=str(uuid.uuid4()),
            tx_type="expense",
            amount=amount,
            category=category,
            description=description,
            balance_after=self._inv.cash_balance,
        )
        self._ledger.append(tx)
        return tx

    # ------------------------------------------------------------------ #
    #  Reporting                                                           #
    # ------------------------------------------------------------------ #

    def show_ledger(self, limit: Optional[int] = None) -> None:
        print("\n=== FINANCIAL LEDGER ===")
        entries = self._ledger if limit is None else self._ledger[-limit:]
        if not entries:
            print("  (no transactions recorded)")
        for tx in entries:
            print(f"  {tx}")
        print()

    def show_summary(self) -> None:
        total_income = sum(t.amount for t in self._ledger if t.tx_type == "income")
        total_expense = sum(t.amount for t in self._ledger if t.tx_type == "expense")
        net = total_income - total_expense
        print("\n=== FINANCIAL SUMMARY ===")
        print(f"  Total income:   ${total_income:>12,.2f}")
        print(f"  Total expenses: ${total_expense:>12,.2f}")
        print(f"  Net P/L:        ${net:>12,.2f}  {'✅ PROFIT' if net >= 0 else '⚠ LOSS'}")
        print(f"  Current balance:${self._inv.cash_balance:>12,.2f}")
        print()

    def income_by_category(self) -> dict:
        summary: dict = {}
        for tx in self._ledger:
            if tx.tx_type == "income":
                summary[tx.category] = summary.get(tx.category, 0.0) + tx.amount
        return summary

    def expense_by_category(self) -> dict:
        summary: dict = {}
        for tx in self._ledger:
            if tx.tx_type == "expense":
                summary[tx.category] = summary.get(tx.category, 0.0) + tx.amount
        return summary

    def show_category_breakdown(self) -> None:
        print("\n=== CATEGORY BREAKDOWN ===")
        print("  INCOME:")
        for cat, total in sorted(self.income_by_category().items(), key=lambda x: -x[1]):
            print(f"    {cat:<20} ${total:,.2f}")
        print("  EXPENSES:")
        for cat, total in sorted(self.expense_by_category().items(), key=lambda x: -x[1]):
            print(f"    {cat:<20} ${total:,.2f}")
        print()
