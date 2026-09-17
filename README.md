# Personal Finance Transaction Analyzer

A menu-driven Python program that reads a messy bank-statement file,
validates and cleans every transaction, tracks a running balance,
categorises spending, flags duplicates and unusual transactions, and
writes summary reports — built to survive genuinely broken input, not
just clean happy-path data.

## About this submission

- **Name:** Tetlanyo Leshogo
- **Cohort:** 2026 DS Jan Cohort

## Features

- Generates a realistic, deliberately messy sample statement (bad date
  separators, missing fields, junk lines, non-numeric amounts, a
  duplicate, a sign/category mismatch, and stray whitespace)
- Loads and validates transactions defensively — one bad row never
  stops the rest of the file from loading, and every rejection is
  reported with a clear reason
- Models transactions as objects, including a `RecurringTransaction`
  subclass
- Tracks a running balance with a generator
- Flags transactions above a custom threshold using a closure
- Detects exact duplicate transactions
- Flags statistical outliers using the `statistics` module
- Flags sign/category mismatches (e.g. an expense category with a
  positive amount)
- Exports a full monthly summary report to a file
- Ships with its own test suite (`tests.py`) proving all of the above
  actually works against the tricky inputs, not just clean data

## How to run

```bash
git clone https://github.com/<your-username>/python-essentials-2-finance-analyzer.git
cd python-essentials-2-finance-analyzer
python3 main.py
```

To run the test suite on its own:

```bash
python3 tests.py
```

Start with option 1 (generate the sample statement), then option 2
(load & validate) — most other options need transactions loaded first.

## Project structure

```
python-essentials-2-finance-analyzer/
├── main.py           # The menu loop — imports and wires everything else together
├── models.py          # Transaction and RecurringTransaction classes
├── parser.py           # Generates the messy sample file and loads it defensively
├── analytics.py         # Running-balance generator, closure, dedup, outliers
├── reporting.py          # Monthly summary report and environment/date info
├── tests.py                # Self-tests proving the edge cases are handled
├── requirements.txt          # Dependency list (empty — stdlib only)
├── .gitignore                  # Keeps generated data files and __pycache__ out of git
└── data/                         # Created/filled at runtime
```

## Why this is hard (and how it's handled)

Real transaction data breaks in predictable ways. This project's
`parser.py` is built defensively so that no single bad row ever
crashes the loader:

| Broken input | How it's handled |
|---|---|
| Wrong date separator (`2026/08/03`) | Normalised to `2026-08-03`, not rejected |
| Missing fields | Rejected, counted, loading continues |
| Junk line (`hello world`) | Rejected safely, no crash |
| Non-numeric amount | Rejected with a clear reason |
| Exact duplicate | Loaded, then found by the duplicate detector |
| Sign/category mismatch | Loaded, then flagged as inconsistent in the report |
| Missing or empty file | Reported gracefully, no crash |
| Stray whitespace | Stripped during cleaning |

## Testing

`tests.py` runs 10+ assertions against known tricky inputs — a valid
row, a normalised date, rejected junk/missing-field rows, a rejected
non-numeric amount, an exact `running_balance` sequence, a closure
correctly flagging above/below its threshold, duplicate detection on
a planted pair, `is_income()` on both signs, and missing/empty file
handling. It prints `All tests passed!` when everything's green, and
fails loudly on the first broken assertion otherwise.
