"""
models.py
---------
Defines the data model for the Personal Finance Transaction Analyzer.

PE2 concepts demonstrated:
- A class with __init__, instance variables, and a class variable
- A class-level counter that increments on every instantiation
- Instance methods (is_income, formatted)
- The __str__ dunder method for clean, human-readable output
- Inheritance: RecurringTransaction extends Transaction, calls
  super().__init__, and overrides __str__ while still reusing the
  parent's formatted() logic

This file only DEFINES objects. It does not read files, print menus,
or run any analysis - that all happens elsewhere.
"""


class Transaction:
    """A single financial transaction: date, description, amount, category."""

    # Class variable: counts every Transaction (and subclass) ever created
    total_transactions = 0

    def __init__(self, date, description, amount, category):
        self.date = date
        self.description = description
        self.amount = amount
        self.category = category

        Transaction.total_transactions += 1

    def is_income(self):
        """Return True if this transaction is money coming in (positive amount)."""
        return self.amount > 0

    def formatted(self):
        """
        Return a signed, fixed-format string, e.g.:
        '2026-08-01 Checkers -450.50 GROCERIES'
        """
        return f"{self.date} {self.description} {self.amount:.2f} {self.category.upper()}"

    def __str__(self):
        kind = "Income" if self.is_income() else "Expense"
        return f"{self.date} | {self.description} | R{self.amount:.2f} | {self.category} | {kind}"


class RecurringTransaction(Transaction):
    """
    A transaction that repeats on a fixed interval, like rent or a
    subscription. Demonstrates inheritance: reuses everything from
    Transaction via super().__init__, adds one new attribute
    (interval), and overrides __str__ to include it - while still
    building on the same signed formatting logic as the parent.
    """

    def __init__(self, date, description, amount, category, interval="monthly"):
        super().__init__(date, description, amount, category)
        self.interval = interval

    def __str__(self):
        base = super().__str__()
        return f"{base} | Recurring: {self.interval}"
