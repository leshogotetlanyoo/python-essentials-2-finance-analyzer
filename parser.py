"""
parser.py
---------
Generates the messy sample bank statement and loads it back defensively.

This is the core of the challenge: real transaction data is broken in
predictable ways (bad separators, missing fields, junk lines, non-numeric
amounts, duplicates, sign/category mismatches, stray whitespace) and
load_transactions() must survive every one of them without crashing,
while reporting exactly what it rejected and why.
"""

import os
import random
from datetime import datetime

DATA_DIR = "data"
STATEMENT_FILE = os.path.join(DATA_DIR, "statement.txt")
REPORT_FILE = os.path.join(DATA_DIR, "report.txt")
LOG_FILE = os.path.join(DATA_DIR, "activity.log")

# Personalized categories and merchants/descriptions, each tagged with
# whether it's normally an expense (negative amount) or income (positive).
CATEGORIES = {
    "GROCERIES": {"items": ["Checkers", "Woolworths", "Pick n Pay", "Spar"], "kind": "expense"},
    "TRANSPORT": {"items": ["Uber", "Bolt", "Gautrain", "Garage Fuel"], "kind": "expense"},
    "RENT": {"items": ["Rent Payment", "Res Fees"], "kind": "expense"},
    "AIRTIME": {"items": ["Vodacom", "MTN"], "kind": "expense"},
    "ENTERTAINMENT": {"items": ["Showmax", "DStv", "Cinema"], "kind": "expense"},
    "EATING_OUT": {"items": ["Mr Price Cafe", "KFC", "Steers", "Coffee Shop"], "kind": "expense"},
    "INCOME": {"items": ["Salary", "Allowance", "Freelance Payment", "Bursary"], "kind": "income"},
    "SUBSCRIPTIONS": {"items": ["Apple Music", "Netflix", "Gym Membership"], "kind": "expense"},
    "SHOPPING": {"items": ["Clicks", "Mr Price", "Takealot"], "kind": "expense"},
    "CLOTHING": {"items": ["Shein"], "kind": "expense"},
    "BANK_FEES": {"items": ["Monthly Account Fee", "ATM Withdrawal Fee"], "kind": "expense"},
}

EXPENSE_CATEGORIES = {cat for cat, info in CATEGORIES.items() if info["kind"] == "expense"}
INCOME_CATEGORIES = {cat for cat, info in CATEGORIES.items() if info["kind"] == "income"}


def _random_amount(kind):
    """Return a realistic, correctly-signed random ZAR amount for the given kind."""
    if kind == "income":
        return round(random.uniform(1500, 25000), 2)
    return -round(random.uniform(15, 3500), 2)


def generate_sample_file():
    """
    Write data/statement.txt with a mix of clean rows and every broken
    case the loader must survive: a bad date separator, missing fields,
    a junk line, a non-numeric amount, an exact duplicate, a
    sign/category mismatch, and stray whitespace.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    rows = []

    # A handful of normal, valid rows across different personalized categories
    normal_picks = [
        ("2026-08-01", "GROCERIES"),
        ("2026-08-02", "TRANSPORT"),
        ("2026-08-03", "AIRTIME"),
        ("2026-08-04", "ENTERTAINMENT"),
        ("2026-08-05", "EATING_OUT"),
        ("2026-08-06", "SUBSCRIPTIONS"),
        ("2026-08-07", "SHOPPING"),
        ("2026-08-08", "RENT"),
        ("2026-08-17", "CLOTHING"),
    ]
    for date, category in normal_picks:
        info = CATEGORIES[category]
        desc = random.choice(info["items"])
        amount = _random_amount(info["kind"])
        rows.append(f"{date},{desc},{amount:.2f},{category}")

    # An income row
    rows.append("2026-08-09,Salary,18500.00,INCOME")

    # 1. Wrong date separator - must be NORMALISED, not rejected
    rows.append("2026/08/10,Uber,-95.00,TRANSPORT")

    # 2. Missing fields (only 2 commas' worth of data instead of 4 fields)
    rows.append("2026-08-11,KFC")

    # 3. Completely junk line - reject safely, no crash
    rows.append("hello world")

    # 4. Non-numeric amount - reject with a clear reason
    rows.append("2026-08-12,Netflix,abc,SUBSCRIPTIONS")

    # 5. Exact duplicate of an earlier valid row - must be LOADED, found later by option 5
    rows.append(f"{normal_picks[0][0]},{rows[0].split(',')[1]},{rows[0].split(',')[2]},{normal_picks[0][1]}")

    # 6. Sign/category mismatch - a GROCERIES (expense) row with a positive amount
    rows.append("2026-08-13,Woolworths,320.00,GROCERIES")

    # 7. Whitespace everywhere - must be stripped during cleaning
    rows.append(" 2026-08-14 , Checkers , -210.75 , GROCERIES ")

    # A couple more clean rows for variety
    rows.append("2026-08-15,Bolt,-60.00,TRANSPORT")
    rows.append("2026-08-16,Freelance Payment,4200.00,INCOME")

    with open(STATEMENT_FILE, "w") as f:
        for row in rows:
            f.write(row + "\n")

    log_event(f"Generated sample statement with {len(rows)} rows to {STATEMENT_FILE}.")
    return STATEMENT_FILE


def _normalise_date(raw_date):
    """
    Accept 'YYYY-MM-DD' or 'YYYY/MM/DD' and return a valid 'YYYY-MM-DD'
    string. Raises ValueError if it isn't a real date either way.
    """
    cleaned = raw_date.strip().replace("/", "-")
    parsed = datetime.strptime(cleaned, "%Y-%m-%d")  # raises ValueError if invalid
    return parsed.strftime("%Y-%m-%d")


def load_transactions(path=STATEMENT_FILE):
    """
    Read a statement file and return (valid_transactions, rejections).

    valid_transactions is a list of Transaction objects (imported lazily
    to avoid a circular import). rejections is a list of human-readable
    strings like 'row 6: not enough fields'. One bad row never stops
    the rest of the file from loading.
    """
    from models import Transaction  # local import avoids a circular dependency

    valid = []
    rejections = []

    if not os.path.exists(path):
        rejections.append(f"file not found: {path}")
        return valid, rejections

    with open(path, "r") as f:
        lines = f.readlines()

    if not any(line.strip() for line in lines):
        rejections.append(f"file is empty: {path}")
        return valid, rejections

    for i, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue  # skip genuinely blank lines silently

        parts = [p.strip() for p in line.split(",")]

        if len(parts) != 4:
            rejections.append(f"row {i}: not enough fields")
            continue

        raw_date, description, raw_amount, category = parts

        try:
            date = _normalise_date(raw_date)
        except ValueError:
            rejections.append(f"row {i}: invalid date")
            continue

        try:
            amount = float(raw_amount)
        except ValueError:
            rejections.append(f"row {i}: amount is not a number")
            continue

        if not description or not category:
            rejections.append(f"row {i}: missing description or category")
            continue

        transaction = Transaction(date, description, amount, category.upper())
        valid.append(transaction)

    log_event(f"Loaded {len(valid)} valid transactions, rejected {len(rejections)} rows from {path}.")
    return valid, rejections


def log_event(message):
    """Append a timestamped line to data/activity.log (append mode - never overwritten)."""
    os.makedirs(DATA_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
