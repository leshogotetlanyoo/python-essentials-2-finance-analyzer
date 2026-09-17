"""
main.py
-------
The Finance Transaction Analyzer menu. Imports from every other module
and wires them together. Holds almost no logic of its own - each menu
option calls a function that already exists elsewhere.
"""

import subprocess
import sys

from parser import generate_sample_file, load_transactions, log_event
from analytics import (
    running_balance,
    make_flagger,
    find_duplicates,
    find_outliers,
    find_sign_mismatches,
    category_totals,
)
from reporting import monthly_summary, environment_report, date_report

# Holds the current in-memory state, populated by option 2
transactions = []
rejections = []


def print_menu():
    print("\n===== FINANCE TRANSACTION ANALYZER =====")
    print("1. Generate a messy sample statement file")
    print("2. Load & validate transactions (reject bad rows)")
    print("3. Show running balance (ledger)")
    print("4. Category breakdown (income vs expense by tag)")
    print("5. Detect duplicate transactions")
    print("6. Flag unusual transactions (statistical outliers)")
    print("7. Monthly summary report -> file")
    print("8. Run self-tests (tests.py)")
    print("9. Exit")


def prompt_float(prompt_text):
    while True:
        raw = input(prompt_text)
        try:
            return float(raw)
        except ValueError:
            print("That's not a valid number - please try again.")


def require_loaded():
    if not transactions:
        print("No transactions loaded yet. Use option 2 first.")
        return False
    return True


def handle_generate():
    path = generate_sample_file()
    print(f"Sample statement written to {path}")


def handle_load():
    global transactions, rejections
    transactions, rejections = load_transactions()
    print(f"Loaded {len(transactions)} valid transactions.")
    print(f"Rejected {len(rejections)} rows:")
    for reason in rejections:
        print(f"  - {reason}")


def handle_balance():
    if not require_loaded():
        return
    balance = 0.0
    for t, balance in zip(transactions, running_balance(transactions)):
        print(f"{t.date} | {t.description:20s} R{t.amount:>10.2f} | Balance: R{balance:.2f}")


def handle_category_breakdown():
    if not require_loaded():
        return
    totals = category_totals(transactions)
    for category, amount in sorted(totals.items()):
        kind = "Income" if amount > 0 else "Expense"
        print(f"  {category:15s} R{amount:>10.2f}  ({kind})")


def handle_duplicates():
    if not require_loaded():
        return
    duplicates = find_duplicates(transactions)
    if not duplicates:
        print("No duplicate transactions found.")
        return
    print(f"Found {len(duplicates)} duplicate transaction(s):")
    for t in duplicates:
        print(f"  {t}")


def handle_outliers():
    if not require_loaded():
        return
    threshold = prompt_float("Flag transactions with amount magnitude above (e.g. 1000): ")
    flagger = make_flagger(threshold)
    flagged = [t for t in transactions if flagger(t)]

    outliers = find_outliers(transactions)

    print(f"Transactions above your R{threshold:.2f} threshold: {len(flagged)}")
    for t in flagged:
        print(f"  {t}")

    print(f"\nStatistical outliers (more than 2 std devs from mean): {len(outliers)}")
    for t in outliers:
        print(f"  {t}")


def handle_report():
    if not require_loaded():
        return
    duplicates = find_duplicates(transactions)
    outliers = find_outliers(transactions)
    mismatches = find_sign_mismatches(transactions)
    monthly_summary(transactions, rejections, duplicates, outliers, mismatches)
    print("Report written to data/report.txt")
    print()
    print(environment_report())
    print()
    print(date_report())


def handle_tests():
    print("Running tests.py ...\n")
    result = subprocess.run([sys.executable, "tests.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode == 0:
        print("Self-tests: PASSED")
    else:
        print("Self-tests: FAILED")
        print(result.stderr)


MENU_ACTIONS = {
    "1": handle_generate,
    "2": handle_load,
    "3": handle_balance,
    "4": handle_category_breakdown,
    "5": handle_duplicates,
    "6": handle_outliers,
    "7": handle_report,
    "8": handle_tests,
}


def main():
    print("Welcome to the Finance Transaction Analyzer!")
    while True:
        print_menu()
        choice = input("Choose an option (1-9): ").strip()

        if choice == "9":
            print("Goodbye!")
            log_event("Program exited normally.")
            break

        action = MENU_ACTIONS.get(choice)
        if action is None:
            print("Invalid option. Please choose a number from 1 to 9.")
            continue

        try:
            action()
        except Exception as exc:
            print(f"Something went wrong with that option: {exc}")


if __name__ == "__main__":
    main()
