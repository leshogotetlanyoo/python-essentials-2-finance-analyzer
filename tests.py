"""
tests.py
--------
Self-tests proving the analyzer survives the messy/broken cases it's
meant to handle. Run directly: python3 tests.py
Every assertion has a message so a failure says exactly what broke.
"""

import os

from models import Transaction
from parser import load_transactions, DATA_DIR
from analytics import running_balance, make_flagger, find_duplicates

TEST_FILE = os.path.join(DATA_DIR, "test_statement.txt")


def write_test_file():
    """Write a small, deliberately tricky statement file just for testing."""
    os.makedirs(DATA_DIR, exist_ok=True)
    lines = [
        "2026-08-01,Checkers,-450.50,GROCERIES",        # row 1: valid
        "2026/08/02,Uber,-95.00,TRANSPORT",              # row 2: wrong date separator, should normalise
        "2026-08-03,KFC",                                # row 3: missing fields, should reject
        "hello world",                                   # row 4: junk line, should reject
        "2026-08-04,Netflix,abc,SUBSCRIPTIONS",          # row 5: non-numeric amount, should reject
        "2026-08-01,Checkers,-450.50,GROCERIES",         # row 6: exact duplicate of row 1
    ]
    with open(TEST_FILE, "w") as f:
        for line in lines:
            f.write(line + "\n")


def cleanup_test_file():
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


# --- Set up a known, tricky test file ---
write_test_file()
valid, rejections = load_transactions(TEST_FILE)

# 1. A valid row parses into a Transaction with the right date, amount, category
assert valid[0].date == "2026-08-01", "row 1 date did not parse correctly"
assert valid[0].amount == -450.50, "row 1 amount did not parse correctly"
assert valid[0].category == "GROCERIES", "row 1 category did not parse correctly"
assert isinstance(valid[0].amount, float), "amount should be parsed as a float"

# 2. A row with the wrong date separator is normalised, not rejected
assert valid[1].date == "2026-08-02", "wrong date separator was not normalised"

# 3. A junk line and a row with missing fields are REJECTED
assert len(valid) == 3, "expected exactly 3 valid rows (2 clean + 1 duplicate), got " + str(len(valid))
assert len(rejections) == 3, "expected exactly 3 rejected rows, got " + str(len(rejections))
assert any("not enough fields" in r for r in rejections), "missing-fields row should be rejected with a clear reason"

# 4. A non-numeric amount is rejected
assert any("not a number" in r for r in rejections), "non-numeric amount row should be rejected with a clear reason"

cleanup_test_file()

# 5. running_balance yields the correct sequence for a known small list
sample = [
    Transaction("2026-08-01", "Salary", 1000.0, "INCOME"),
    Transaction("2026-08-02", "Checkers", -200.0, "GROCERIES"),
    Transaction("2026-08-03", "Uber", -50.0, "TRANSPORT"),
]
balances = list(running_balance(sample, start=0.0))
assert balances == [1000.0, 800.0, 750.0], f"running_balance gave wrong sequence: {balances}"

# 6. make_flagger(1000) flags a 5000 transaction and does NOT flag a 50 one
flagger = make_flagger(1000)
big = Transaction("2026-08-04", "Big Purchase", 5000.0, "SHOPPING")
small = Transaction("2026-08-05", "Coffee Shop", -50.0, "EATING_OUT")
assert flagger(big) is True, "make_flagger should flag a transaction above its threshold"
assert flagger(small) is False, "make_flagger should NOT flag a transaction below its threshold"

# 7. find_duplicates finds a known planted duplicate and finds none in a clean list
dup_a = Transaction("2026-08-01", "Checkers", -450.50, "GROCERIES")
dup_b = Transaction("2026-08-01", "Checkers", -450.50, "GROCERIES")
duplicates = find_duplicates([dup_a, dup_b])
assert len(duplicates) == 1, "find_duplicates should find exactly one duplicate in this planted pair"

clean_list = [
    Transaction("2026-08-01", "Checkers", -450.50, "GROCERIES"),
    Transaction("2026-08-02", "Uber", -95.00, "TRANSPORT"),
]
assert find_duplicates(clean_list) == [], "find_duplicates should find nothing in a clean list"

# 8. is_income() returns True for a positive amount and False for a negative one
income_t = Transaction("2026-08-01", "Salary", 5000.0, "INCOME")
expense_t = Transaction("2026-08-01", "Checkers", -450.50, "GROCERIES")
assert income_t.is_income() is True, "is_income should be True for a positive amount"
assert expense_t.is_income() is False, "is_income should be False for a negative amount"

# 9. Missing file is handled gracefully, not a crash
missing_valid, missing_rejections = load_transactions("data/this_file_does_not_exist.txt")
assert missing_valid == [], "loading a missing file should return no valid transactions"
assert len(missing_rejections) == 1, "loading a missing file should report exactly one rejection reason"

# 10. Empty file is handled gracefully, not a crash
empty_path = os.path.join(DATA_DIR, "empty_test.txt")
open(empty_path, "w").close()
empty_valid, empty_rejections = load_transactions(empty_path)
assert empty_valid == [], "loading an empty file should return no valid transactions"
assert len(empty_rejections) == 1, "loading an empty file should report exactly one rejection reason"
os.remove(empty_path)

print("All tests passed!")
