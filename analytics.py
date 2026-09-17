"""
analytics.py
------------
Generator, closure, and statistical analysis over loaded transactions.
"""

import statistics


def running_balance(transactions, start=0.0):
    """
    Generator that yields the running balance after each transaction,
    in the order given. Stateful - order matters, since each yield
    depends on everything that came before it.
    """
    balance = start
    for transaction in transactions:
        balance += transaction.amount
        yield balance


def make_flagger(threshold):
    """
    Closure factory: returns a flagger(transaction) function that
    remembers the threshold it was created with, and flags any
    transaction whose amount magnitude exceeds it.
    """
    def flagger(transaction):
        return abs(transaction.amount) > threshold

    return flagger


def find_duplicates(transactions):
    """
    Detect exact duplicates using a set of (date, description, amount,
    category) signatures. Returns the list of transactions that are
    duplicates of an earlier one (the second+ occurrence).
    """
    seen = set()
    duplicates = []
    for transaction in transactions:
        signature = (transaction.date, transaction.description, transaction.amount, transaction.category)
        if signature in seen:
            duplicates.append(transaction)
        else:
            seen.add(signature)
    return duplicates


def find_outliers(transactions):
    """
    Flag transactions whose amount is more than 2 standard deviations
    from the mean, using the statistics module. Needs at least 2
    transactions to compute a standard deviation.
    """
    if len(transactions) < 2:
        return []

    amounts = [t.amount for t in transactions]
    mean = statistics.mean(amounts)
    stdev = statistics.stdev(amounts)

    if stdev == 0:
        return []

    return [t for t in transactions if abs(t.amount - mean) > 2 * stdev]


def find_sign_mismatches(transactions):
    """
    Flag transactions where the sign of the amount doesn't match what
    the category implies - e.g. a GROCERIES (expense) row with a
    positive amount, or an INCOME row with a negative amount.
    """
    from parser import EXPENSE_CATEGORIES, INCOME_CATEGORIES

    mismatches = []
    for t in transactions:
        if t.category in EXPENSE_CATEGORIES and t.amount > 0:
            mismatches.append(t)
        elif t.category in INCOME_CATEGORIES and t.amount < 0:
            mismatches.append(t)
    return mismatches


def category_totals(transactions):
    """Return a dict of category -> summed amount across all transactions."""
    totals = {}
    for t in transactions:
        totals[t.category] = totals.get(t.category, 0.0) + t.amount
    return totals
