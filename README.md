# Library Circulation and Demand Dashboard

## Objective
Analyse anonymised library borrowing records to summarise demand by category and book, monthly borrowing patterns, overdue loans and data-quality issues. The included dataset is synthetic.

## Requirements
Python 3.9+ and pandas, numpy, matplotlib.

Install packages:
```bash
python -m pip install pandas numpy matplotlib
```

Run from this folder:
```bash
python library_dashboard.py
```
The program reads `data/library_records.csv` and generates CSV/JSON summaries and PNG plots in `output/`.

## Project files
- `library_dashboard.py`: main program and `LoanRecord` class
- `data/library_records.csv`: synthetic sample data
- `tests/test_logic.py`: small logic tests
- `output/`: generated reports and charts (created on run)

## Analysis
Category totals, top borrowed titles, monthly loan totals, current overdue list, data quality checks and comparison of alert thresholds (>7 versus >14 days late).
