"""Library Circulation and Demand Dashboard. Run: python library_dashboard.py"""
from pathlib import Path
import json
from datetime import date
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "library_records.csv"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

class LoanRecord:
    """Represent one loan. len(obj) gives its duration in days."""
    def __init__(self, record_id, book_id, book_title, category, borrower_id, loan_date, due_date, return_date=""):
        self.record_id = record_id
        self.book_id = book_id
        self.book_title = book_title
        self.category = category
        self.borrower_id = borrower_id
        self.loan_date = pd.to_datetime(loan_date)
        self.due_date = pd.to_datetime(due_date)
        self.return_date = pd.to_datetime(return_date) if str(return_date).strip() else None

    def __len__(self):
        end = self.return_date if self.return_date is not None else pd.Timestamp(date.today())
        return max(0, int((end - self.loan_date).days))

    def __repr__(self):
        return f"LoanRecord({self.record_id}, {self.book_title})"


def load_and_clean(path=DATA_FILE):
    df = pd.read_csv(path)
    before = len(df)
    duplicates = int(df.duplicated(subset=["record_id"]).sum())
    df = df.drop_duplicates(subset=["record_id"], keep="first").copy()
    missing_category = int((df["category"].isna() | (df["category"].astype(str).str.strip()=="")).sum())
    missing_borrower = int((df["borrower_id"].isna() | (df["borrower_id"].astype(str).str.strip()=="")).sum())
    df["category"] = df["category"].fillna("").replace("", "Unknown")
    df["borrower_id"] = df["borrower_id"].fillna("").replace("", "Unknown")
    for col in ["loan_date", "due_date", "return_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df = df.dropna(subset=["record_id", "loan_date", "due_date"]).copy()
    quality = {"rows_before_cleaning": before, "duplicate_record_ids_removed": duplicates,
               "missing_categories_filled": missing_category,
               "missing_borrower_ids_filled": missing_borrower,
               "rows_after_cleaning": int(len(df))}
    return df, quality


def analyse(df):
    today = pd.Timestamp(date.today())
    df["month"] = df["loan_date"].dt.to_period("M").astype(str)
    df["is_open"] = df["return_date"].isna()
    df["days_past_due"] = np.where(df["is_open"] & (df["due_date"] < today),
                                  (today-df["due_date"]).dt.days, 0)
    df["is_overdue"] = df["days_past_due"] > 0
    category_counts = df.groupby("category").size().sort_values(ascending=False)
    popular_books = df.groupby("book_title").size().sort_values(ascending=False).head(10)
    monthly = df.groupby("month").size().sort_index()
    overdue = df[df["is_overdue"]].copy()
    alert_7 = int((df["days_past_due"] > 7).sum())
    alert_14 = int((df["days_past_due"] > 14).sum())
    return category_counts, popular_books, monthly, overdue, alert_7, alert_14


def save_plots(category_counts, popular_books, monthly, df):
    category_counts.plot(kind="bar", figsize=(9,5), title="Borrowing Records by Category")
    plt.xlabel("Category"); plt.ylabel("Number of loans"); plt.tight_layout()
    plt.savefig(OUTPUT_DIR/"category_demand.png"); plt.close()
    popular_books.sort_values().plot(kind="barh", figsize=(9,5), title="Top 10 Borrowed Books")
    plt.xlabel("Number of loans"); plt.tight_layout()
    plt.savefig(OUTPUT_DIR/"popular_books.png"); plt.close()
    monthly.plot(kind="line", marker="o", figsize=(10,5), title="Monthly Borrowing Trend")
    plt.xlabel("Month"); plt.ylabel("Number of loans"); plt.xticks(rotation=45); plt.tight_layout()
    plt.savefig(OUTPUT_DIR/"monthly_trend.png"); plt.close()
    df["days_past_due"].clip(upper=60).plot(kind="hist", bins=12, figsize=(8,5), title="Days Past Due (capped at 60)")
    plt.xlabel("Days past due"); plt.ylabel("Record count"); plt.tight_layout()
    plt.savefig(OUTPUT_DIR/"late_days_histogram.png"); plt.close()


def export_results(df, category_counts, popular_books, monthly, overdue, quality, alert_7, alert_14):
    df.to_csv(OUTPUT_DIR/"cleaned_records.csv", index=False)
    category_counts.rename("loan_count").to_csv(OUTPUT_DIR/"category_summary.csv")
    popular_books.rename("loan_count").to_csv(OUTPUT_DIR/"popular_books.csv")
    monthly.rename("loan_count").to_csv(OUTPUT_DIR/"monthly_summary.csv")
    overdue.to_csv(OUTPUT_DIR/"overdue_records.csv", index=False)
    summary = {"total_valid_records": int(len(df)), "unique_books_borrowed": int(df["book_title"].nunique()),
               "open_loans": int(df["is_open"].sum()), "currently_overdue_loans": int(df["is_overdue"].sum()),
               "alerts_more_than_7_days_late": alert_7, "alerts_more_than_14_days_late": alert_14,
               "data_quality": quality}
    with open(OUTPUT_DIR/"summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, default=str)
    return summary


def main():
    print("=== Library Circulation and Demand Dashboard ===")
    df, quality = load_and_clean()
    category_counts, popular_books, monthly, overdue, alert_7, alert_14 = analyse(df)
    records = [LoanRecord(*row) for row in df[["record_id","book_id","book_title","category","borrower_id","loan_date","due_date","return_date"]].fillna("").itertuples(index=False, name=None)]
    print(f"Valid records: {len(records)}")
    print("\nCategory demand:\n", category_counts)
    print("\nTop borrowed books:\n", popular_books)
    print(f"\nCurrently overdue loans: {len(overdue)}")
    print(f"Alert threshold >7 days: {alert_7}; >14 days: {alert_14}")
    print("\nData quality checks:", quality)
    save_plots(category_counts, popular_books, monthly, df)
    export_results(df, category_counts, popular_books, monthly, overdue, quality, alert_7, alert_14)
    print("\nSaved output CSVs, summary.json and four plots in output/.")
    if records: print(f"Example: {records[0]} | duration: {len(records[0])} days")

if __name__ == "__main__":
    main()
