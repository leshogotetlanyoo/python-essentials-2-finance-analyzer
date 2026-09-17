"""
reporting.py
------------
Monthly summary report and environment/date reporting.
"""

import os
import platform
from datetime import datetime

from analytics import category_totals
from parser import REPORT_FILE, DATA_DIR, log_event


def monthly_summary(transactions, rejections, duplicates, outliers, mismatches):
    """
    Build and write a full summary report to data/report.txt: totals,
    category breakdown, and counts of everything flagged along the way.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    totals = category_totals(transactions)
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expense = sum(t.amount for t in transactions if t.amount < 0)
    net = total_income + total_expense

    lines = ["===== MONTHLY SUMMARY REPORT =====", ""]
    lines.append(f"Total income : R{total_income:.2f}")
    lines.append(f"Total expense: R{total_expense:.2f}")
    lines.append(f"Net          : R{net:.2f}")
    lines.append("")
    lines.append("Category breakdown:")
    for category, amount in sorted(totals.items()):
        lines.append(f"  {category:15s} R{amount:.2f}")
    lines.append("")
    lines.append(f"Rejected rows   : {len(rejections)}")
    for reason in rejections:
        lines.append(f"  - {reason}")
    lines.append(f"Duplicates found: {len(duplicates)}")
    lines.append(f"Outliers found  : {len(outliers)}")
    lines.append(f"Sign mismatches : {len(mismatches)}")

    report_text = "\n".join(lines)
    with open(REPORT_FILE, "w") as f:
        f.write(report_text)

    log_event(f"Wrote monthly summary report to {REPORT_FILE}.")
    return report_text


def environment_report():
    """Return a string with OS, Python version, and working directory."""
    lines = [
        f"Operating System : {platform.system()} {platform.release()}",
        f"Python Version   : {platform.python_version()}",
        f"Working Directory: {os.getcwd()}",
    ]
    return "\n".join(lines)


def date_report():
    """Return a string with today's date and a timestamp."""
    now = datetime.now()
    return f"Today's Date: {now.strftime('%A, %d %B %Y')}\nTimestamp   : {now.strftime('%Y-%m-%d %H:%M:%S')}"
